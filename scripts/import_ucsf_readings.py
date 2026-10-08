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
    ("u01-n03-knowledge-check", "Unit_1_Informatics_quiz.ipynb", "UCSF Unit 1", "Local Unit 1: informatics value", "Knowledge check link"),
    ("u02-n01-slides", "Unit_2.ipynb", "UCSF Unit 2", "Local Units 2–3 and later topics", "Unit slides"),
    ("u02-n02-knowledge-check", "Unit_2_Informatics_quiz.ipynb", "UCSF Unit 2", "Local Units 2–3 and later topics", "Knowledge check link"),
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

IMAGE_RE = re.compile(r"!\[([^]]*)\]\((images/[^)]+)\)")
HTML_IMAGE_RE = re.compile(r'(<img\b[^>]*?src=["\'])images/([^"\']+)', re.IGNORECASE)
EXTERNAL_IMAGE_RE = re.compile(r'<img\b[^>]*?src=["\'](https?://[^"\']+)["\'][^>]*?/?>', re.IGNORECASE)
IFRAME_RE = re.compile(r"<iframe\b[^>]*>\s*</iframe>", re.IGNORECASE | re.DOTALL)
SRC_RE = re.compile(r'''\bsrc=["']([^"']+)["']''', re.IGNORECASE)
URL_RE = re.compile(r'''https?://[^\s"']+''')
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
UNIT1_SLIDES_PLACEHOLDER = f"**Linked media from the source notebook**\n\n- [Open the source resource]({UNIT1_SLIDES_PDF})"
UNIT1_SLIDES_EXPLANATION = (
    "**Source media: Unit 1 slides PDF.** The archived UCSF notebook embeds a Google Drive PDF here. "
    "CDC may block that viewer, and the PDF itself was not available for inspection here, so its exact slides are unverified. "
    f"[Original PDF link]({UNIT1_SLIDES_PDF}).\n\n"
    "**Available course deck for context:** The supplied *Unit 1 v2: Intro to Informatics for FETP* PowerPoint "
    "has 31 slides. Slides 1–15 introduce the module, objectives, and learning methods; "
    "16–22 cover the digital revolution, epidemiology, and public health informatics; "
    "23–25 present Laila's data overload; 26–29 show data → information → knowledge → wisdom "
    "and the surveillance value cycle; 30–31 summarize and invite reflection. "
    "This Version 2 deck is related course material, not a verified copy of the linked PDF."
)


def get_bytes(path: str) -> bytes:
    with urlopen(RAW + path, timeout=30) as response:
        return response.read()


def source_of(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def code_to_reading(source: str) -> str:
    videos = re.findall(r"YouTubeVideo\(['\"]([^'\"]+)", source)
    urls = [url.rstrip(",)") for url in URL_RE.findall(source)]
    links = [f"- [Watch the source video](https://www.youtube.com/watch?v={video})" for video in videos]
    links += [f"- [Open the source resource]({url})" for url in urls]
    if links:
        return "**Linked media from the source notebook**\n\n" + "\n".join(dict.fromkeys(links))
    return "*The source page used a flashcard widget here. Open the source notebook in UCSF's book to use it.*"


def normalize_markdown(markdown: str, images: set[str]) -> str:
    def replace_iframe(match: re.Match) -> str:
        src = SRC_RE.search(match.group())
        return f"[Open the source slides or response form]({src.group(1)})" if src else "*Embedded source resource*"

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
        # The archived Unit 1 book embeds six Google Drive images whose direct
        # image endpoint is no longer renderable in JupyterLite. Keep a source
        # link in place, rather than showing a broken image box.
        url = match.group(1)
        drive_id = re.search(r"drive\.google\.com/uc\?id=([^&]+)", url)
        if drive_id:
            url = f"https://drive.google.com/file/d/{drive_id.group(1)}/view"
        return f"[Open source illustration]({url})"

    return EXTERNAL_IMAGE_RE.sub(replace_external_image, markdown).strip()


def cell(source: str, cell_id: str) -> dict:
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": source.splitlines(keepends=True)}


def make_notebook(row: tuple[str, str, str, str, str], images: set[str],
                  body_override: str | None = None) -> tuple[str, dict]:
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
    if filename == "u01-n02-lesson":
        body = body.replace(UNIT1_SLIDES_PLACEHOLDER, UNIT1_SLIDES_EXPLANATION)
    images.update(page_images)
    number = filename.split("-")[1][1:]
    outline = (
        f"**Source reading:** {source_unit} · Notebook {number}\n\n"
        f"# {title}\n\n"
        f"**Course alignment:** {local_topic}. This preserves a UCSF JupyterBook page as reading material. "
        "It does not record an adaptive-learning observation. UCSF and the local Version 3 course use different unit numbers."
    )
    names = [entry[0] for entry in SOURCES]
    position = names.index(filename)
    adjacent = []
    if position:
        adjacent.append(f"[Previous reading]({lab_link(names[position - 1])})")
    adjacent.append(f"[Reading index]({lab_link('u00-n01-reading-index')})")
    if position + 1 < len(names):
        adjacent.append(f"[Next reading]({lab_link(names[position + 1])})")
    reading_note = (
        "## Use and review this reading\n\n"
        "If JupyterLite asks for a kernel, choose **No Kernel**; this page has no runnable cells. "
        "Read the source lesson or case questions above. In your own notebook copy, note what is clear, "
        "what needs a local example, and whether a linked slide, form, video, or illustration opens. "
        "For an assignment, answer its source questions in your own copy. These notes are unscored. "
        "For assessed practice, use the **Learning** panel when an exercise exists for this topic.\n\n"
        " · ".join(adjacent)
    )
    references = (
        "## Source and visual attribution\n\n"
        f"- [Original UCSF JupyterBook page]({BROWSE + source_path}) at revision `{REVISION}`.\n"
        + ("- Images in this reading were copied from that same revision of the UCSF course repository.\n" if page_images else "")
        + "\n"
        "The page is retained as a reading. Embedded slides, forms, and videos open through their original links."
    )
    notebook = {
        "cells": [cell(outline, "0"), cell(body, "1"), cell(reading_note, "2"), cell(references, "3")],
        "metadata": {"title": f"{source_unit} · {title}", "sourceRevision": REVISION,
                     "sourcePath": source_path, "generatedBy": "scripts/import_ucsf_readings.py"},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return filename, notebook


def write_index() -> None:
    def links(unit: str) -> str:
        return "\n".join(
            f"- [Notebook {name.split('-')[1][1:]}: {title}]({lab_link(name)}) — {local_topic}"
            for name, _, _, local_topic, title in SOURCES if name.startswith(unit)
        )

    notebook = {
        "cells": [
            cell("**Course outline:** Source readings · Index\n\n# UCSF Unit 1 and Unit 2 readings\n\n"
                 "These pages preserve the UCSF JupyterBook text, case prompts, and available visuals. "
                 "They are unscored. Their unit numbers come from UCSF; each page states its closest local Version 3 topic.", "0"),
            cell("## UCSF Unit 1\n\n" + links("u01-"), "1"),
            cell("## UCSF Unit 2\n\n" + links("u02-"), "2"),
            cell("## Using these readings\n\nOpen a page from the list or the JupyterLite file browser. "
                 "The links stay on this JupyterLite site, including a local preview. "
                 "Each reading links back here and to the adjacent page. "
                 "If asked to select a kernel, choose **No Kernel**. "
                 "For assessed practice, use the **Learning** panel when an exercise exists for the topic. "
                 f"[UCSF source repository](https://github.com/UCSF-IGHS/FETP/tree/{REVISION}/FETP_book).", "3"),
        ],
        "metadata": {"title": "UCSF Unit 1 and 2 reading index", "sourceRevision": REVISION,
                     "generatedBy": "scripts/import_ucsf_readings.py"},
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
        if args.reuse_local:
            existing = OUT / f"{row[0]}.ipynb"
            body = source_of(json.loads(existing.read_text(encoding="utf-8"))["cells"][1])
        filename, notebook = make_notebook(row, images, body)
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
