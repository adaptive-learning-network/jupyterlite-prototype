#!/usr/bin/env python3
"""Import UCSF Unit 1–2 book pages as unscored JupyterLite reading notebooks.

The pinned upstream revision makes this a deliberate source update, rather than
a network dependency of the site build. Run this script only when reviewing a
new UCSF revision; generated notebooks and referenced images are committed.
"""

from __future__ import annotations

import json
import argparse
import re
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content/readings/ucsf"
ASSETS = OUT / "assets"
REVISION = "7eca2ec9d4d6082e76c7061a4746f1ac69d4ca7b"
RAW = f"https://raw.githubusercontent.com/UCSF-IGHS/FETP/{REVISION}/FETP_book/"
BROWSE = f"https://github.com/UCSF-IGHS/FETP/blob/{REVISION}/FETP_book/"

def lab_link(filename: str) -> str:
    """Let JupyterLab open a notebook in the same content directory."""
    return f"{filename}.ipynb"

# Source numbering is UCSF's. The local Version 3 unit is stated separately
# inside each notebook; these readings are not al: assessment activities.
SOURCES = [
    ("u01-n01-slides", "Unit_1.md", "UCSF Unit 1", "Local Unit 1: informatics value", "Unit slides"),
    ("u01-n02-lesson", "_build/html/_sources/FETP_Unit_1.ipynb", "UCSF Unit 1 (archived build)", "Local Unit 1: informatics value", "Introduction to informatics"),
    ("u01-n03-knowledge-check", "Unit_1_Informatics_quiz.ipynb", "UCSF Unit 1", "Local Unit 1: informatics value", "Knowledge check"),
    ("u02-n01-slides", "Unit_2.ipynb", "UCSF Unit 2", "Local Units 2–3 and later topics", "Unit slides"),
    ("u02-n02-knowledge-check", "Unit_2_Informatics_quiz.ipynb", "UCSF Unit 2", "Local Units 2–3 and later topics", "Knowledge check"),
    ("u02-n03-his-context", "Unit_2.1.ipynb", "UCSF Unit 2.1", "Local Unit 2: country HIS context", "Country and HIS context"),
    ("u02-n04-case-study", "Unit_2.1_Case_study.ipynb", "UCSF Unit 2.1", "Local Units 2–3: context and information needs", "Surveillance case study"),
    ("u02-n05-group-work", "Unit_2.1_Group_work.ipynb", "UCSF Unit 2.1", "Local Unit 2: system map", "Country HIS group work"),
    ("u02-n06-assignment-1", "_build/html/_sources/Unit_2.1_Case_study_Assignment_1.ipynb", "UCSF Unit 2.1 (archived build)", "Local Unit 2: country HIS context", "Case study assignment 1"),
    ("u02-n07-explore-datasets", "Unit_2.1_Using_Software_to_Explore_Datasets.ipynb", "UCSF Unit 2.1", "Local Unit 3: information needs", "Explore datasets"),
    ("u02-n08-assignment-2", "Unit_2.1_Case_study_Assignment_2.ipynb", "UCSF Unit 2.1", "Local Unit 3: information needs", "Case study assignment 2"),
    ("u02-n09-assignment-3", "Unit_2.1_Case_study_Assignment_3.ipynb", "UCSF Unit 2.1", "Local Unit 3: information needs", "Case study assignment 3"),
    ("u02-n10-data-quality", "Unit_2.2.ipynb", "UCSF Unit 2.2", "Local Unit 8: data quality", "Data quality"),
    ("u02-n11-assignment-4", "Unit_2.2_Case_study_Assignment_4.ipynb", "UCSF Unit 2.2", "Local Unit 8: data quality", "Case study assignment 4"),
    ("u02-n12-compile-analyze", "Unit_2.3_Compile_and_Analyze_Data.ipynb", "UCSF Unit 2.3", "Local Units 11–13: transformation, merging, analysis", "Compile and analyze data"),
    ("u02-n13-analyze-visualize", "Unit_2.3.ipynb", "UCSF Unit 2.3", "Local Unit 13: analysis and visualization", "Analyze and visualize data"),
    ("u02-n14-assignment-5", "Unit_2.3_Case_study_Assignment_5.ipynb", "UCSF Unit 2.3", "Local Unit 12: merging and exchange", "Case study assignment 5"),
    ("u02-n15-assignment-6", "Unit_2.3_Case_study_Assignment_6.ipynb", "UCSF Unit 2.3", "Local Unit 13: analysis and visualization", "Case study assignment 6"),
]

# Learner-facing framing. Source versions and crosswalks live in course docs.
LEARNING = {
    "u01-n01-slides": ("Why informatics matters", "Identify a way informatics helps Laila use surveillance data.", "Which slide best explains why more data alone does not solve Laila's problem?"),
    "u01-n02-lesson": ("From data to decisions", "Explain how Laila turns reports into a useful public health decision.", "Choose one report value and describe the context needed before Laila acts on it."),
    "u01-n03-knowledge-check": ("Check your understanding", "Apply informatics ideas to Laila's reporting problem.", "What would you ask Laila before interpreting a sudden increase in reports?"),
    "u02-n01-slides": ("Follow the surveillance pathway", "Trace how a report moves from detection toward action.", "Where could a delayed or missing report change a district summary?"),
    "u02-n02-knowledge-check": ("Check the reporting pathway", "Explain how health information systems support surveillance.", "Which handoff in the reporting pathway would you verify first?"),
    "u02-n03-his-context": ("Map the information system", "Map the people and systems that move a case report.", "Follow one case alert from a health facility to the district team."),
    "u02-n04-case-study": ("Laila's surveillance case", "Identify the information Laila needs for a surveillance summary.", "What is known from the first alert, and what must Laila still find out?"),
    "u02-n05-group-work": ("Map who needs the data", "Map the sources, systems, and users of Laila's report.", "Who creates each record, and who needs the resulting summary?"),
    "u02-n06-assignment-1": ("Start the case investigation", "Describe the reporting problem and Laila's first information needs.", "Write two questions Laila should answer before choosing a dataset."),
    "u02-n07-explore-datasets": ("Explore a surveillance dataset", "Inspect a dataset before using it for Laila's report.", "Which variables and time period would you check first?"),
    "u02-n08-assignment-2": ("Check dataset fit", "Evaluate whether a dataset fits Laila's question.", "Compare its people, places, and time period with the report request."),
    "u02-n09-assignment-3": ("Select useful variables", "Select variables needed for a working dataset.", "Which fields identify a case, a place, and an onset date?"),
    "u02-n10-data-quality": ("Find data quality problems", "Detect gaps that could distort a surveillance summary.", "Which missing or inconsistent fields would change your interpretation?"),
    "u02-n11-assignment-4": ("Plan data quality repairs", "Prioritize fixes for incomplete or inconsistent records.", "Which change would you make first, and how would you record it?"),
    "u02-n12-compile-analyze": ("Prepare data for analysis", "Organize records for a person, place, and time summary.", "What checks would you run before combining records?"),
    "u02-n13-analyze-visualize": ("Show the pattern", "Analyze patterns in cases across person, place, and time.", "Which table or visual would help Laila explain the signal?"),
    "u02-n14-assignment-5": ("Combine the case data", "Verify a merged dataset before analysis.", "How would you detect duplicated or unmatched case IDs?"),
    "u02-n15-assignment-6": ("Build the surveillance summary", "Justify a surveillance finding with tables and visuals.", "What can Laila recommend from the evidence, and what remains uncertain?"),
}

IMAGE_RE = re.compile(r"!\[([^]]*)\]\((images/[^)]+)\)")
HTML_IMAGE_RE = re.compile(r'(<img\b[^>]*?src=["\'])images/([^"\']+)', re.IGNORECASE)
EXTERNAL_IMAGE_RE = re.compile(r'<img\b[^>]*?src=["\'](https?://[^"\']+)["\'][^>]*?/?>', re.IGNORECASE)
IFRAME_RE = re.compile(r"<iframe\b[^>]*>\s*</iframe>", re.IGNORECASE | re.DOTALL)
SRC_RE = re.compile(r'''\bsrc=["']([^"']+)["']''', re.IGNORECASE)
URL_RE = re.compile(r'''https?://[^\s"']+''')
FORM_LINK_RE = re.compile(r"\[([^]]+)\]\((https://docs\.google\.com/forms/[^)]+)\)")

# These headings come from visible UCSF questions. The quiz forms could not be
# inspected, so their local prompts are adaptations of the course material.
LOCAL_RESPONSES = {
    "u01-n02-lesson": ["How can informatics help Laila turn surveillance data into useful information?",
                       "How do information, knowledge, and a decision differ in Laila's report?"],
    "u01-n03-knowledge-check": ["How can an informatics tool improve surveillance or an outbreak investigation?",
                                "Trace raw data through information and knowledge to action in Laila's case.",
                                "Name a component of your country's health information system and its surveillance role."],
    "u02-n02-knowledge-check": ["Trace case information from its source through the country health information system.",
                                "Who uses that information at facility, district, and national levels?",
                                "Where could reporting lose timeliness or completeness?"],
    "u02-n05-group-work": ["Information needed for Laila's yellow fever report", "Where the data originates",
                            "Paper and electronic systems", "Who can access and use each system"],
    "u02-n08-assignment-2": ["Dataset size", "Time span and comparison with the period of interest",
                              "Locations and comparison with the locations of interest",
                              "People included and comparison with the population of interest"],
    "u02-n09-assignment-3": ["Question 4: variables in the dataset",
                              "Question 5: use the data dictionary and Excel to create a working dataset"],
    "u02-n11-assignment-4": ["Question 6: data quality problems and examples",
                              "Question 7: repair steps, changes made, and remaining problems"],
    "u02-n14-assignment-5": ["Question 8: findings and preparation needed", "Question 9: prepare the patient dataset",
                              "Question 10: merge result and checks"],
    "u02-n15-assignment-6": ["Question 11: analyses and tools", "Question 12: tables",
                              "Question 13: household map", "Question 14: epi curve and event dates",
                              "Question 15: surveillance summary and recommendations"],
}


def localize_form(filename: str, body: str, prior_url: str | None = None) -> tuple[str, str | None, str | None]:
    matches = FORM_LINK_RE.findall(body)
    if not matches and not prior_url:
        return body, None, None
    if filename not in LOCAL_RESPONSES or (matches and len({url for _, url in matches}) != 1):
        raise ValueError(f"unmapped source form in {filename}")
    source_url = matches[0][1] if matches else prior_url
    body = FORM_LINK_RE.sub("**Use the local response section below.**", body)
    body = re.sub(r"> \*\*Please submit your answers using the form provided below\*\*",
                  "**Record your answers in the local response section below.**", body)
    is_quiz = "knowledge-check" in filename or filename == "u01-n02-lesson"
    note = ("Use these prompts to test your reasoning. "
            "For more practice, open the [question library](u00-n02-version3-form-library.ipynb). "
            "Your response here is for reflection and is not scored."
            if is_quiz else
            "Use these headings to organize your case response. Your notes stay in this browser and are not scored.")
    prompts = "\n\n".join(f"**{i}. {prompt}**\n\n_Enter your response here._"
                           for i, prompt in enumerate(LOCAL_RESPONSES[filename], 1))
    response = ("## Local response section\n\n" + note +
                "\n\nDouble-click this cell, replace each italic placeholder with your answer, "
                "then press **Shift+Enter** and save the notebook. Responses remain in this browser.\n\n" + prompts)
    return body, response, source_url
IMAGE_ALT = {
    "laila_2.png": "Laila's current data-access problems and the quality dataset she needs",
    "his_context.png": "Laila's country HIS diagram linking community, facility, district, and national systems",
    "sl_diseases.png": "Sierra Leone table of priority diseases and reporting categories",
    "laila_2.2.png": "Laila's data-quality questions about completeness, accuracy, and timeliness",
    "laila_analyze.png": "Laila's need to summarize person, place, and time before her report",
    "laila_2.3.png": "Laila's case notification data and remaining missing variables",
    "match_rows.png": "Matching case IDs across two example datasets",
}

UNIT1_SLIDES_PDF = "https://drive.google.com/file/d/1fMH_U9sGqUJfT_cA85OC_SpUKJ_hqxyV/preview"
SLIDE_PREVIEWS = {
    "u01-n01-slides": ("Unit 1", "unit-1-version-2-slides.pdf", 30),
    "u02-n01-slides": ("Unit 2", "unit-2-version-2-slides.pdf", 112),
}
UNIT1_VISUALS = {
    "1lp7jiftbj2Va-HN6QN6wfPu8GpA0QIde": (22, "Laila faces data overload"),
    "1yHoX1gRFidMnKgsGWT0yQcGLUhW7B3vB": (19, "What public health informatics does"),
    "1JH42e3y9Fjxz6YHWGvXsTRukm67fp-dM": (21, "How informaticians support a health system"),
    "1sdTujihwDDiKR0ZJaL6ryLaq1X-1Ies6": (25, "From data to wisdom"),
    "1_ksiZ0RMpLgHFnxNay_WODXDZTRU39pB": (26, "The public health surveillance cycle"),
    "1O7-oJefmWMCD5Wsra5xqi1d425NGtsov": (27, "Creating value from surveillance data"),
}
UNIT1_SLIDES_PLACEHOLDER = f"**Linked media from the source notebook**\n\n- [Open the source resource]({UNIT1_SLIDES_PDF})"
UNIT1_SLIDES_EXPLANATION = (
    "[Explore the Unit 1 slides](u01-n01-slides.ipynb) as you read. "
    "Look for the point where raw reports become information Laila can use."
)


def get_bytes(path: str) -> bytes:
    with urlopen(RAW + path, timeout=30) as response:
        return response.read()


def source_of(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def code_to_reading(source: str) -> str:
    return ""


def normalize_markdown(markdown: str, images: set[str]) -> str:
    def replace_iframe(match: re.Match) -> str:
        src = SRC_RE.search(match.group())
        if not src:
            return ""
        if "docs.google.com/forms" in src.group(1):
            return f"[Answer the questions below]({src.group(1)})"
        return ""

    markdown = IFRAME_RE.sub(replace_iframe, markdown)

    def replace_image(match: re.Match) -> str:
        path = match.group(2)
        images.add(path)
        return f"![{IMAGE_ALT.get(Path(path).name, match.group(1))}](assets/{Path(path).name})"

    markdown = IMAGE_RE.sub(replace_image, markdown)

    def replace_html_image(match: re.Match) -> str:
        images.add("images/" + match.group(2))
        return match.group(1) + "assets/" + match.group(2)

    markdown = HTML_IMAGE_RE.sub(replace_html_image, markdown)

    def replace_external_image(match: re.Match) -> str:
        url = match.group(1)
        drive_id = re.search(r"drive\.google\.com/uc\?id=([^&]+)", url)
        if drive_id and drive_id.group(1) in UNIT1_VISUALS:
            page, alt = UNIT1_VISUALS[drive_id.group(1)]
            return f"![{alt}](assets/slide-previews/unit-1-{page:03d}.jpg)"
        return ""

    return EXTERNAL_IMAGE_RE.sub(replace_external_image, markdown).strip()


def cell(source: str, cell_id: str) -> dict:
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": source.splitlines(keepends=True)}


def localize_dependencies(filename: str, body: str) -> str:
    if filename == "u01-n02-lesson":
        for drive_id, (page, alt) in UNIT1_VISUALS.items():
            body = body.replace(
                f"[Open source illustration](https://drive.google.com/file/d/{drive_id}/view)",
                f"![{alt}](assets/slide-previews/unit-1-{page:03d}.jpg)",
            )
    body = re.sub(r"^.*\[Watch the source video\]\(https?://[^\n]+\n?", "", body, flags=re.M)
    body = re.sub(r"^- \[[^\n\]]+\]\(https?://scribehow\.com/[^\n]+\n?", "", body, flags=re.M)
    body = re.sub(r"^.*\[Open the source slides or response form\]\(https?://[^\n]+\n?", "", body, flags=re.M)
    body = re.sub(r"^.*\[Presentation Template: Surveillance Summary Report\]\(https?://[^\n]+\n?",
                  "Use the headings **finding, evidence, limitations, and recommended action** for your local surveillance summary.\n", body, flags=re.M)
    body = re.sub(r"\[2021 (?:Measles )?Case Notification Data\]\(https?://[^)]+\)",
                  "[Local practice case register](assets/laila-case-register.csv)", body)
    body = re.sub(r"\[2021 Clinical Data \(Measles\)\]\(https?://[^)]+\)",
                  "[Local practice clinical records](assets/laila-clinical-records.csv)", body)
    body = re.sub(r"^- \[(?:Technical Guidelines|Situational Analysis|Community Health Information System)[^\n]+\n?", "", body, flags=re.M)
    body = re.sub(r"^- DHIS2 Data Dictionary \([^\n]+", "- [Local practice data dictionary](assets/laila-data-dictionary.md)", body, flags=re.M)
    body = re.sub(r"\*The source page used a flashcard widget here\.[^*]+\*", "", body)
    body = re.sub(r"How-To Scribes", "Local practice steps", body, flags=re.I)
    body = re.sub(r"^\*\*Lets take a minute and watch this video\*\*\s*", "", body, flags=re.M)
    body = re.sub(r"^\*\*Watch or explore\*\*\s*", "", body, flags=re.M)
    body = re.sub(r"^What are Excel Local practice steps\?.*?What Excel Local practice steps are available\?",
                  "Use the local case register below to sort, filter, count, and inspect minimum and maximum values.",
                  body, flags=re.M | re.S)
    body = re.sub(r"^\*\*Excel Local practice steps\*\*", "**Practice with the local files below**", body, flags=re.M)
    body = body.replace("#### Excel Local practice steps", "#### Practice with the browser dataset")
    body = re.sub(r"### Resources: Sierra Leone eIDSR and HIS Strategies\s*The following resources describe the current eIDSR and HIS context, strategies, and policies:",
                  "### Apply the system context\n\nWhich district responsibility would be hardest if facility and community reports arrive late? What would you verify with the district team?", body)
    if "### Dimensions of Data Quality" in body and "**Completeness:**" not in body:
        body = body.replace("### Dimensions of Data Quality\n", "### Dimensions of Data Quality\n\n"
                            "- **Completeness:** are expected records and required fields present?\n"
                            "- **Timeliness:** do reports arrive in time for action?\n"
                            "- **Accuracy:** do values match the event or source record?\n")
    body = body.replace("- Excel\n\n**Practice with the local files below**", "")
    body = body.replace("### Resources\n\nUse the headings", "### Report structure\n\nUse the headings")
    if filename == "u01-n02-lesson":
        # The archived page put this image and 39px text in nested HTML divs.
        # Markdown renders more reliably in JupyterLite's narrow reading pane.
        body = re.sub(
            r'<div style="display: flex; align-items: flex-start;">\s*'
            r'\s*!\[Creating value from surveillance data\]'
            r'\(assets/slide-previews/unit-1-027\.jpg\)\s*'
            r'<div style="flex: 1;">.*?</div>\s*</div>',
            '![Creating value from surveillance data](assets/slide-previews/unit-1-027.jpg)\n\n'
            'By applying informatics principles, systems, and tools, we use evidence '
            'to solve public health problems and improve health outcomes.',
            body,
            flags=re.S,
        )
        # --reuse-local also repairs notebooks generated before the block above.
        body = re.sub(
            r'<div style="display: flex; align-items: flex-start;">\s*'
            r'<img src="assets/slide-previews/unit-1-027\.jpg"[^>]*>\s*'
            r'<div style="flex: 1;">.*?</div>\s*</div>',
            '![Creating value from surveillance data](assets/slide-previews/unit-1-027.jpg)\n\n'
            'By applying informatics principles, systems, and tools, we use evidence '
            'to solve public health problems and improve health outcomes.',
            body,
            flags=re.S,
        )
    if filename == "u02-n07-explore-datasets" and "## Try it with a small register" not in body:
        body += ("\n\n## Try it with a small register\n\n"
                 "Open the [practice case register](assets/laila-case-register.csv) and "
                 "[data dictionary](assets/laila-data-dictionary.md). These fictional records are a small "
                 "practice set, not Laila's 8,500-row file. Count records, find the earliest and latest onset dates, "
                 "and list the districts. Which fields would you need for a district summary?\n")
    if filename == "u02-n10-data-quality" and "## Try a quality check" not in body:
        body += ("\n\n## Try a quality check\n\n"
                 "Use the [practice case register](assets/laila-case-register.csv), "
                 "[clinical records](assets/laila-clinical-records.csv), and "
                 "[data dictionary](assets/laila-data-dictionary.md). Identify a missing specimen date, "
                 "an unmatched case ID, and a value that needs clarification before reporting.\n")
    if filename == "u02-n13-analyze-visualize" and "## Try a local summary" not in body:
        body += ("\n\n## Try a local summary\n\n"
                 "Use the [practice case register](assets/laila-case-register.csv) to count cases by district "
                 "and onset week. Sketch one table or chart, then write the finding, evidence, limitations, "
                 "and recommended verification step. These fictional records are for practice.\n")
    body = re.sub(r"\n{4,}", "\n\n\n", body)
    return body


def make_notebook(row: tuple[str, str, str, str, str], images: set[str],
                  body_override: str | None = None, prior_form_url: str | None = None) -> tuple[str, dict]:
    filename, source_path, source_unit, local_topic, title = row
    if body_override is None:
        raw = get_bytes(source_path).decode("utf-8")
        if source_path.endswith(".md"):
            parts = [raw]
        else:
            original = json.loads(raw)
            parts = [source_of(c) if c["cell_type"] == "markdown" else code_to_reading(source_of(c))
                     for c in original["cells"]]
        page_images: set[str] = set()
        body = "\n\n".join(part for part in (normalize_markdown(p, page_images) for p in parts) if part)
    else:
        body = body_override
        page_images = set(re.findall(r"assets/([^\s)\"']+)", body))
    body = body.replace("Laila’s Laila’s Problem:", "Laila’s Problem:")
    body = body.replace("*The source page used a flashcard widget here. Open the source notebook in UCSF's book to use it.*", "")
    body = body.replace("**Linked media from the source notebook**", "**Watch or explore**")
    if filename == "u01-n02-lesson":
        body = body.replace(UNIT1_SLIDES_PLACEHOLDER, UNIT1_SLIDES_EXPLANATION)
        body = re.sub(r"\*\*Source media: Unit 1 slides PDF\.\*\*.*?(?=\n\n---)",
                      UNIT1_SLIDES_EXPLANATION, body, count=1, flags=re.S)
    body = localize_dependencies(filename, body)
    body = re.sub(r"^## Unit [12] (?:Version 2 )?slide preview\n.*?\n---\n\n", "", body, count=1, flags=re.S)
    if filename in SLIDE_PREVIEWS:
        unit, pdf, pages = SLIDE_PREVIEWS[filename]
        url = f"../files/readings/ucsf/assets/{pdf}"
        preview = (
            f"## {unit} slide preview\n\n"
            "Open a page range below. Each slide has a link to its full PDF page. "
            "As you browse, notice where data is collected, organized, interpreted, and used.\n\n"
            f"[Open all {pages} slide pages in the PDF]({url})\n\n---\n\n"
        )
        body = preview + body
        body = re.sub(r"\[Open the source slides or response form\]\([^)]*\)", "", body)
        body = re.sub(r"\n# Unit Slides\s*$", "", body)
    body, response, source_form_url = localize_form(filename, body, prior_form_url)
    images.update(page_images)
    unit_number = int(filename[1:3])
    notebook_number = int(filename[5:7])
    learner_title, goal, prompt = LEARNING[filename]
    outline = (
        f"**Unit {unit_number} · Notebook {notebook_number:02d}**\n\n"
        f"# {learner_title}\n\n"
        f"**Learning goal:** {goal}\n\n"
        "Follow Laila's case, inspect the examples, and use the question at the end to test your understanding."
    )
    names = [entry[0] for entry in SOURCES]
    position = names.index(filename)
    adjacent = []
    if position:
        adjacent.append(f"[Previous reading]({lab_link(names[position - 1])})")
    adjacent.append(f"[Reading index]({lab_link('u00-n01-reading-index')})")
    if position + 1 < len(names):
        adjacent.append(f"[Next reading]({lab_link(names[position + 1])})")
    reflection = ("## Try it\n\n" + prompt + "\n\n"
                  "Double-click this cell to write a short answer in your own notebook copy. "
                  "Choose **No Kernel** if asked; this reading has no code to run.\n\n"
                  "_Write your reasoning here._")
    navigation = ("## Continue learning\n\n" + " · ".join(adjacent) + "\n\n"
                  "For a scored exercise, open the **Learning** panel. Your notes in this reading are for practice.")
    slide_cells = []
    if filename in SLIDE_PREVIEWS:
        unit, pdf, pages = SLIDE_PREVIEWS[filename]
        number = int(unit[-1])
        for first in range(1, pages + 1, 10):
            last = min(first + 9, pages)
            lines = [f"<details><summary>{unit} PDF pages {first}–{last}</summary>", ""]
            for page in range(first, last + 1):
                pdf_url = f"../files/readings/ucsf/assets/{pdf}#page={page}"
                image_url = f"assets/slide-previews/unit-{number}-{page:03d}.jpg"
                lines.append(
                    f"**Page {page}** · [Open this PDF page]({pdf_url})\n\n"
                    f"![{unit} slide page {page}]({image_url})\n"
                )
            lines += ["", "</details>"]
            slide_cells.append(cell("\n".join(lines), f"slide-{first:03d}"))
    if response:
        notebook_cells = [cell(outline, "0"), cell(body, "1"), cell(response, "2"), cell(navigation, "3")]
    else:
        notebook_cells = [cell(outline, "0"), cell(body, "1"), *slide_cells,
                          cell(reflection, "2"), cell(navigation, "3")]
    notebook = {
        "cells": notebook_cells,
        "metadata": {"title": learner_title, "generatedBy": "scripts/import_ucsf_readings.py",
                     **({"sourceFormUrl": source_form_url} if source_form_url else {})},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return filename, notebook


def write_index() -> None:
    def links(unit: str) -> str:
        return "\n".join(
            f"- [Notebook {name.split('-')[1][1:]}: {LEARNING[name][0]}]({lab_link(name)})"
            for name, *_ in SOURCES if name.startswith(unit)
        )

    notebook = {
        "cells": [
            cell("**Course source library · Reading index**\n\n# Explore the fuller course readings\n\n"
                 "These readings preserve more of the course text, prompts, and diagrams. "
                 "The scored Python notebooks provide the main case path, including the "
                 "explanation and visuals needed for each computation. These readings are optional. "
                 "Your written notes stay in this browser.", "0"),
            cell("## Unit 1 ? From data to decisions\n\n" + links("u01-"), "1"),
            cell("## Unit 2 ? Follow a report through the system\n\n" + links("u02-"), "2"),
            cell("## Continue Laila's case\n\nChoose **No Kernel** if asked; these readings have no code to run. "
                 "Return to the [Unit 1 computational notebook](../../exercises/python/u01-n01-data-to-decision.ipynb) "
                 "or use the **Learning** panel for the next scored exercise. "
                 "[Optional practice questions](u00-n02-version3-form-library.ipynb) offer another way to review the ideas.", "3"),
        ],
        "metadata": {"title": "Unit 1 and 2 reading index", "generatedBy": "scripts/import_ucsf_readings.py"},
        "nbformat": 4, "nbformat_minor": 5,
    }
    (OUT / "u00-n01-reading-index.ipynb").write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse-local", action="store_true",
                        help="rebuild navigation and review notes from committed source bodies without downloading")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    images: set[str] = set()
    for row in SOURCES:
        body = None
        prior_form_url = None
        if args.reuse_local:
            existing = OUT / f"{row[0]}.ipynb"
            existing_notebook = json.loads(existing.read_text(encoding="utf-8"))
            body = source_of(existing_notebook["cells"][1])
            prior_form_url = existing_notebook["metadata"].get("sourceFormUrl")
        filename, notebook = make_notebook(row, images, body, prior_form_url)
        (OUT / f"{filename}.ipynb").write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write_index()
    if not args.reuse_local:
        for path in sorted(images):
            if not path.startswith("images/") or Path(path).name != path.removeprefix("images/"):
                raise ValueError(f"unexpected source image path: {path}")
            (ASSETS / Path(path).name).write_bytes(get_bytes(path))
    print(f"prepared {len(SOURCES)} reading notebooks and {len(images)} referenced source images from {REVISION}")


if __name__ == "__main__":
    main()
