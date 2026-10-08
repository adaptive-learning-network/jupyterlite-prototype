#!/usr/bin/env python3
"""Generate the Python and R exercise notebooks and their checks from one spec.

Content: Public Health Informatics for FETP, Unit 3 "Using Informatics to Get
Information Faster" (Version 3 course materials, used with permission). Exercise
text, examples, and help follow the unit's slides and instructor guide.

Each activity in the al: catalog gets one notebook per Jupyter kernel language.
The exercise cell carries `al` metadata (activity IRI, observed-object IRI,
check path, facilitation-ladder hints). After the learner runs it, the
extension executes checks/<name>.<ext> in the same Jupyter kernel; the check
prints one line, `AL_OBSERVATION {"outcome": "correct|incorrect|incomplete"}`.

Checks contain expected values. They run in the learner's own Jupyter kernel,
so results are formative: the catalog caps this evidence at the simulation stage.

Usage: python scripts/make_exercises.py
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
EX = "https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#"

KERNELSPEC = {
    "python": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
    "r": {"name": "xr", "display_name": "R (xeus-r)", "language": "R"},
}
LANGUAGE_INFO = {"python": {"name": "python"}, "r": {"name": "R"}}

UNIT = "Unit 3: Using Informatics to Get Information Faster"
OBJECTIVES = [
    "Define data & information (D&I) needs",
    "Communicate your data & information needs",
    "Combine variables to meet your information needs",
    "See how database organization enables automation",
]

# Original course documents. Notebooks replace them as the delivery format; each
# notebook keeps these links in a References section at the bottom.
SOURCE_DOCS = {
    "guide": ("Unit 3 instructor guide (Google Docs)", "https://docs.google.com/document/d/1B6qrW7QBcL4uCO85QPIN8pJ--37S8N6j3xkT87qBACA"),
    "slides": ("Unit 3 slides, v3 revised 2025-05-13 (Google Slides)", "https://docs.google.com/presentation/d/1EXkFCxffubjhpM94373WiJ0a9_V0Tsfn"),
    "quiz": ("Unit 3 knowledge check (Google Forms)", "https://forms.gle/Y4yG5gMbFznczrBd9"),
}

# Excel How-To Scribes from the Unit 3 slides (slides 56-57): the course's
# on-demand demonstrations. Notebooks show the same steps in Python or R.
SCRIBES = {
    "copy": ("Make a working copy of your dataset", "https://scribehow.com/shared/Create_a_copy_of_the_dataset_as_a_new_file__C7nao6DfR2OgFA63HVto9Q"),
    "sort": ("Sort data using a single variable", "https://scribehow.com/shared/A_guide_to_sorting_data_in_MS_Excel__OdSOUuArSBSRInz4qO6ijw"),
    "multisort": ("Sort data using multiple variables", "https://scribehow.com/shared/A_guide_to_multiple_sorting_in_MS_Excel__NieApI7sQLSM7fcqvGqpjA"),
    "filter": ("Filter data", "https://scribehow.com/shared/A_guide_to_filtering_data_in_MS_Excel__tz_S8tOWTiaIyII1Qu1Wng"),
    "count": ("Use the Count function", "https://scribehow.com/shared/How_big_is_your_dataset_A_guide_to_counting_rows_in_Excel__U6cLWaK9RvSmt6mz3k99Lw"),
    "maxmin": ("Use the Max-Min function", "https://scribehow.com/shared/A_guide_to_estimating_maximum_and_minimum_values_in_Excel_using_MAX_and_MIN_functions__lZiWahgvQJyEbnk45t6MJw"),
}

# ---------------------------------------------------------------------------
# Immunization register. Columns follow the machine-readable example on Unit 3
# slide 29 (Patient ID, Vaccine Type, Date Given, Dose #, Location, Age, Sex),
# with machine-friendly names. The first five rows are the slide's example rows.
# The remaining rows are synthetic, built so that the slide 7 statement holds:
# "In District X, 92% of children under age 5 received their first dose of the
# MMR vaccine."
# ---------------------------------------------------------------------------

COLUMNS = ["patient_id", "vaccine_type", "date_given", "dose", "location", "age", "sex"]
SLIDE_ROWS = [  # slide 29, with "Region" read as the district in the slide 7 statement
    ("MMR", "2025-05-10", 1, "District X", 2, "F"),
    ("MMR", "2025-05-12", 1, "District X", 4, "M"),
    ("MMR", "2025-05-13", 2, "District Y", 3, "F"),
    ("MMR", "2025-05-14", 1, "District X", 1, "F"),
    ("MMR", "2025-05-15", 1, "District Y", 2, "M"),
]
# (location, vaccine, dose, under five?, total rows including slide rows)
GROUPS = [
    ("District X", "MMR", 1, True, 46),
    ("District X", "MMR", 2, True, 10),
    ("District X", "Polio", 1, True, 12),
    ("District X", "Hepatitis B", 1, True, 8),
    ("District X", "MMR", 1, False, 4),
    ("District Y", "MMR", 1, True, 30),
    ("District Y", "MMR", 2, True, 1),
    ("District Y", "Polio", 1, True, 6),
    ("District Z", "MMR", 1, True, 18),
    ("District Z", "MMR", 2, True, 4),
]
POPULATION_UNDER_5 = {"District X": 50, "District Y": 40, "District Z": 25}


def build_register() -> list[tuple]:
    slide_counts: dict[tuple, int] = {}
    for vaccine, _, dose, location, age, _ in SLIDE_ROWS:
        key = (location, vaccine, dose, age < 5)
        slide_counts[key] = slide_counts.get(key, 0) + 1
    generated = []
    k = 0
    start = date(2025, 1, 6)
    for location, vaccine, dose, under5, total in GROUPS:
        for _ in range(total - slide_counts.get((location, vaccine, dose, under5), 0)):
            age = k % 5 if under5 else [5, 6, 7, 9][k % 4]
            given = start + timedelta(days=(k * 37) % 170)
            generated.append((vaccine, given.isoformat(), dose, location, age, "F" if k % 2 else "M"))
            k += 1
    random.Random(3).shuffle(generated)
    return [(i + 1, *row) for i, row in enumerate(SLIDE_ROWS + generated)]


REGISTER = build_register()
DATES = sorted(r[2] for r in REGISTER)
ANSWERS = {
    "n_records": len(REGISTER),
    "first_date": DATES[0],
    "last_date": DATES[-1],
    "n_locations": len({r[4] for r in REGISTER}),
    "age_min": min(r[5] for r in REGISTER),
    "age_max": max(r[5] for r in REGISTER),
    "n_mmr_dose1_x": sum(1 for r in REGISTER if r[1] == "MMR" and r[3] == 1 and r[4] == "District X" and r[5] < 5),
}
ANSWERS["coverage_x"] = ANSWERS["n_mmr_dose1_x"] / POPULATION_UNDER_5["District X"]
assert abs(ANSWERS["coverage_x"] - 0.92) < 1e-9, "register must reproduce the slide 7 statement"

REGISTER_CSV = "\n".join([",".join(COLUMNS)] + [",".join(str(v) for v in row) for row in REGISTER])
POPULATION_CSV = "\n".join(["location,population_under5"] + [f"{k},{v}" for k, v in POPULATION_UNDER_5.items()])

LOAD = {
    "python": (
        "# Immunization register (machine-readable: one row per observation,\n"
        "# one column per variable, one value per cell) and under-5 population.\n"
        "import io\nimport pandas as pd\n\n"
        f'REGISTER_CSV = """{REGISTER_CSV}"""\n\n'
        f'POPULATION_CSV = """{POPULATION_CSV}"""\n\n'
        "register = pd.read_csv(io.StringIO(REGISTER_CSV))\n"
        "population = pd.read_csv(io.StringIO(POPULATION_CSV))\n"
        "register.head()"
    ),
    "r": (
        "# Immunization register (machine-readable: one row per observation,\n"
        "# one column per variable, one value per cell) and under-5 population.\n"
        f'register <- read.csv(text = "{REGISTER_CSV}", stringsAsFactors = FALSE)\n'
        f'population <- read.csv(text = "{POPULATION_CSV}", stringsAsFactors = FALSE)\n'
        "head(register)"
    ),
}


def items_setup(language: str, title: str, items: list[str]) -> str:
    if language == "python":
        lines = [f"# {title}", "items = {"] + [f"    {chr(97 + i)!r}: {item!r}," for i, item in enumerate(items)] + ["}",
                 "for letter, item in items.items():", "    print(letter, '-', item)"]
    else:
        values = ", ".join(f'{chr(97 + i)} = "{item}"' for i, item in enumerate(items))
        lines = [f"# {title}", f"items <- c({values})", 'for (letter in names(items)) cat(letter, "-", items[[letter]], "\\n")']
    return "\n".join(lines)


DATA_OR_INFORMATION = [  # Unit 3 slide 18
    "Age",
    "Heat (choropleth) map",
    "Clinical sign or symptom",
    "Date of onset",
    "Table showing number of cases by age categories",
    "Epi curve showing number of cases by epi week",
]
MACHINE_READABLE_RULES = [  # Unit 3 slide 29
    "Each observation has its own row",
    "Each variable has its own column",
    "Each value has its own cell",
]
DATASET_TABLES = [  # Unit 3 slide 39
    "Table with ID, Name, Age, Sex, District, Diagnosis",
    "Table with District, Malaria_Cases, Typhoid_Cases",
    "Table with Age_Group, Disease, Count",
    "Table with Patient_Initials, Date_of_Birth, Location, Diagnosis_Date",
    "Table with County, Total_Cases, Deaths, Recovered",
]


def scribe_list(*keys: str) -> str:
    return "\n".join(f"- [{SCRIBES[k][0]}]({SCRIBES[k][1]})" for k in keys)


# variables: name -> (kind, expected). Kinds: count | rate | choice | set | date.
EXERCISES = [
    {
        "file": "u03-n01-data-or-information", "check": "data-or-information", "slides": "6, 18–24", "activity": "act-data-or-information",
        "title": "Data or information?",
        "objective": OBJECTIVES[0],
        "context": (
            "**Data** are raw, unorganized numbers and facts: single variables that have limited value in isolation. "
            "**Information** is organized and structured data: it combines multiple variables to uncover patterns, "
            "trends, and relationships. (Data – Information – Knowledge – Wisdom pyramid.)"
        ),
        "task": "Which of the items listed by the setup cell are **information** rather than data? "
                "Store their letters in `information_items`, for example `[\"a\", \"c\"]` in Python or `c(\"a\", \"c\")` in R.",
        "setup": {lang: items_setup(lang, "Data versus information: which is it?", DATA_OR_INFORMATION) for lang in ("python", "r")},
        "variables": {"information_items": ("set", ["b", "e", "f"])},
        "hints": [
            "Ask of each item: is it a single variable, or does it combine variables to show a pattern?",
            "Age, a clinical sign, and a date of onset are each one variable recorded about one case.",
            "A map, a table of cases by age category, and an epi curve each combine variables: those are information.",
        ],
    },
    {
        "file": "02-explore-dataset", "check": "explore-dataset", "slides": "51–57", "activity": "act-explore-dataset",
        "title": "Explore the immunization register",
        "objective": "Use software to explore a dataset",
        "context": (
            "Laila's supervisor gave her a large surveillance file, and she does not know whether it includes the data she "
            "needs. To make data more useful, ask: What timeframe does the dataset span? What locations does it include? "
            "Who is included? Five essential functions help: **sort**, **filter**, **count**, **max**, and **min**.\n\n"
            "The same steps in Excel (Excel How-To Scribes):\n" + scribe_list("copy", "sort", "count", "maxmin")
        ),
        "task": (
            "Answer these questions about `register` with code:\n\n"
            "- `n_records`: how many records (rows) it contains;\n"
            "- `first_date` and `last_date`: the earliest and latest `date_given` (as `YYYY-MM-DD`);\n"
            "- `n_locations`: how many different locations it includes;\n"
            "- `age_min` and `age_max`: the youngest and oldest ages."
        ),
        "setup": LOAD,
        "variables": {
            "n_records": ("count", ANSWERS["n_records"]),
            "first_date": ("date", ANSWERS["first_date"]),
            "last_date": ("date", ANSWERS["last_date"]),
            "n_locations": ("count", ANSWERS["n_locations"]),
            "age_min": ("count", ANSWERS["age_min"]),
            "age_max": ("count", ANSWERS["age_max"]),
        },
        "hints": [
            "Count gives the size of the dataset; Min and Max give the timeframe and the age range.",
            "Python: len(register), register['date_given'].min(), register['location'].nunique(). "
            "R: nrow(register), min(register$date_given), length(unique(register$location)).",
            "Dates are stored as YYYY-MM-DD text, so the smallest text value is the earliest date. Use max() for the latest date and the oldest age.",
        ],
    },
    {
        "file": "03-filter-records", "check": "filter-records", "slides": "56–57", "activity": "act-filter-records",
        "title": "Filter the records you need",
        "objective": OBJECTIVES[2],
        "context": (
            "Filtering shows or hides specific data in a list, which makes large datasets much easier to work with.\n\n"
            "The same steps in Excel (Excel How-To Scribes):\n" + scribe_list("filter", "multisort")
        ),
        "task": "How many records are a **first dose** (`dose` 1) of **MMR** given in **District X** to a child **under age 5**? "
                "Store the number in `n_mmr_dose1_x`.",
        "setup": LOAD,
        "variables": {"n_mmr_dose1_x": ("count", ANSWERS["n_mmr_dose1_x"])},
        "hints": [
            "Four conditions must all be true: vaccine type, dose number, location, and age.",
            "Combine the conditions with 'and': `&` in pandas and in R.",
            "Python: ((register['vaccine_type'] == 'MMR') & (register['dose'] == 1) & (register['location'] == 'District X') & (register['age'] < 5)).sum(); "
            "R: sum(register$vaccine_type == 'MMR' & register$dose == 1 & register$location == 'District X' & register$age < 5).",
        ],
    },
    {
        "file": "04-coverage", "check": "coverage", "slides": "7–17", "activity": "act-coverage",
        "title": "Turn data into information: vaccination coverage",
        "objective": OBJECTIVES[2],
        "context": (
            "Data transformed into information looks like this: *In District X, 92% of children under age 5 received their "
            "first dose of the MMR vaccine.* The variables in that sentence are: district, number of children vaccinated "
            "(numerator), total number of children in District X (denominator), age, vaccine dose, and vaccine type."
        ),
        "task": "Combine those variables to compute the proportion of children under age 5 in District X who received their first "
                "MMR dose. Use `register` for the numerator and `population` for the denominator. Store it in `coverage_x` "
                "as a proportion (for example 0.5, not 50).",
        "setup": LOAD,
        "variables": {"coverage_x": ("rate", ANSWERS["coverage_x"])},
        "hints": [
            "Coverage = number vaccinated (numerator) ÷ number of children in the population (denominator).",
            "The numerator is the filtered count from the previous exercise; the denominator is District X's population_under5.",
            "Python: n / population.loc[population['location'] == 'District X', 'population_under5'].item(); "
            "R: n / population$population_under5[population$location == 'District X'].",
        ],
    },
    {
        "file": "05-machine-readable", "check": "machine-readable", "slides": "28–32", "activity": "act-machine-readable",
        "title": "Machine-readable or human-readable?",
        "objective": OBJECTIVES[3],
        "context": (
            "Machine-readable datasets enable automation of data to information. They follow three rules (listed by the setup "
            "cell). Human-readable datasets violate these rules. Every violation means more complicated code, a higher risk "
            "of errors, and less automation."
        ),
        "task": "In a human-readable register, patient 1's record shows **\"MMR, Polio, Hepatitis B\"** in the Vaccine Type cell. "
                "Which rule does this break? Store its letter in `answer`.",
        "setup": {lang: items_setup(lang, "Rules for machine-readable datasets", MACHINE_READABLE_RULES) for lang in ("python", "r")},
        "variables": {"answer": ("choice", "c")},
        "hints": [
            "Look at what is inside that single cell.",
            "Three vaccines are packed into one cell; software cannot count or filter them separately.",
            "Each vaccine needs its own row (one observation each), so that each cell holds one value.",
        ],
    },
    {
        "file": "06-case-or-aggregate", "check": "case-or-aggregate", "slides": "38–39", "activity": "act-case-or-aggregate",
        "title": "Case-based or aggregate?",
        "objective": OBJECTIVES[3],
        "context": (
            "**Case-based** datasets hold one row per person or case. **Aggregate** datasets contain counts or averages, with "
            "no individual identifiers; they support trend analysis, resource allocation, and public reporting (for example, "
            "allocating medical supplies based on district case counts)."
        ),
        "task": "Look at the datasets listed by the setup cell. Which are **aggregate** datasets? Store their letters in "
                "`aggregate_tables`.",
        "setup": {lang: items_setup(lang, "Is this a case-based or aggregate dataset?", DATASET_TABLES) for lang in ("python", "r")},
        "variables": {"aggregate_tables": ("set", ["b", "c", "e"])},
        "hints": [
            "Does each row describe one person, or a group of people?",
            "Columns such as Count, Total_Cases, or Malaria_Cases hold counts of people.",
            "Tables with IDs, names, initials, or dates of birth describe individuals: those are case-based.",
        ],
    },
]


def python_test(name: str, kind: str, expected) -> str:
    v = f"g[{name!r}]"
    if kind == "count":
        return f"int({v}) == {expected}"
    if kind == "rate":
        return f"abs(float({v}) - {expected!r}) < 1e-6"
    if kind == "date":
        return f"str({v})[:10] == {expected!r}"
    if kind == "set":
        return f"sorted({{str(x).strip().lower() for x in {v}}}) == {sorted(expected)!r}"
    return f"str({v}).strip().lower() == {expected!r}"


def r_test(name: str, kind: str, expected) -> str:
    if kind == "count":
        return f"isTRUE(as.numeric({name}) == {expected})"
    if kind == "rate":
        return f"isTRUE(abs(as.numeric({name}) - {expected!r}) < 1e-6)"
    if kind == "date":
        return f'isTRUE(substr(as.character({name}), 1, 10) == "{expected}")'
    if kind == "set":
        values = ", ".join(f'"{x}"' for x in sorted(expected))
        return f"identical(sort(unique(tolower(trimws(as.character({name}))))), c({values}))"
    return f'isTRUE(tolower(trimws(as.character({name}))) == "{expected}")'


def python_check(variables: dict) -> str:
    lines = ["import json as _al_json", "def _al_check():", "    g = globals()"]
    for name, (kind, expected) in variables.items():
        lines += [f"    if g.get({name!r}) is None:", "        return 'incomplete'",
                  "    try:", f"        if not ({python_test(name, kind, expected)}):", "            return 'incorrect'",
                  "    except (TypeError, ValueError):", "        return 'incorrect'"]
    lines += ["    return 'correct'",
              "print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))",
              "del _al_check"]
    return "\n".join(lines) + "\n"


def r_check(variables: dict) -> str:
    lines = ["local({", "  outcome <- tryCatch({", "    result <- \"correct\""]
    for name, (kind, expected) in variables.items():
        lines += [
            f"    if (!exists(\"{name}\", envir = globalenv()) || is.null(get(\"{name}\", envir = globalenv()))) {{",
            "      result <- \"incomplete\"",
            f"    }} else if (result == \"correct\" && !{r_test(name, kind, expected)}) {{",
            "      result <- \"incorrect\"",
            "    }",
        ]
    lines += ["    result", "  }, error = function(e) \"incorrect\")",
              "  cat(paste0(\"AL_OBSERVATION {\\\"outcome\\\":\\\"\", outcome, \"\\\"}\\n\"))", "})"]
    return "\n".join(lines) + "\n"


def placeholder(language: str, variables: dict) -> str:
    if language == "python":
        return "\n".join(f"{name} = None  # replace None with your answer" for name in variables) + "\n"
    return "\n".join(f"{name} <- NULL  # replace NULL with your answer" for name in variables) + "\n"


def references(ex: dict) -> str:
    lines = ["## References", "",
             f"- [{SOURCE_DOCS['guide'][0]}]({SOURCE_DOCS['guide'][1]})",
             f"- [{SOURCE_DOCS['slides'][0]}]({SOURCE_DOCS['slides'][1]}): slides {ex['slides']}",
             f"- [{SOURCE_DOCS['quiz'][0]}]({SOURCE_DOCS['quiz'][1]})",
             "- Excel How-To Scribes:"]
    if ex["file"] == "u03-n01-data-or-information":
        lines.insert(5, "- Surveillance-cycle visual: *Unit 2, Version 2, Detection and Diagnosis*, slide 3 (course deck supplied with the project).")
    lines += [f"  - [{title}]({url})" for title, url in SCRIBES.values()]
    lines += ["", "*Public Health Informatics for FETP, Version 3 course materials, used with permission.*"]
    return "\n".join(lines)


def cell(cell_type: str, source: str, cell_id: str, metadata: dict | None = None) -> dict:
    c = {"cell_type": cell_type, "id": cell_id, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        c.update({"execution_count": None, "outputs": []})
    return c


def notebook(ex: dict, language: str) -> dict:
    name = "Python" if language == "python" else "R"
    pilot_outline = ""
    pilot_cue = ""
    if ex["file"] == "u03-n01-data-or-information":
        pilot_outline = f"**Course outline:** Unit 03 · Notebook 01 · {name}\n\n"
        pilot_cue = (
            "![Three-panel comic: Laila examines a line list, her supervisor points to the records, and she imagines a chart and map.](../assets/laila-unit03-notebook01-comic.png)\n\n"
            "*Laila has ages, symptoms, and onset dates. Her supervisor asks which items already show a pattern. "
            "Help Laila tell raw data from information. (Original teaching illustration; dialogue is not from the slides.)*\n\n"
        )
        pilot_cue += (
            '<img src="../assets/unit2-v2-surveillance-cycle.png" width="420" alt="Course surveillance cycle: detect, collect, compile and analyze, interpret, communicate, and take action.">\n\n'
            "*Slide connection: Unit 2, Version 2, slide 3. This notebook works at the **data → information** step, "
            "where collected values become a pattern that can be interpreted.*\n\n"
        )
    intro = (
        f"{pilot_outline}# {ex['title']}\n\n{pilot_cue}"
        f"*{UNIT}*. Learning objective: **{ex['objective']}**.\n\n"
        f"{ex['context']}\n\n"
        f"## Your task\n\n{ex['task']}\n\n"
        "Run the setup cell, then edit and run the exercise cell. The **Learning** panel records the result and suggests "
        "what to do next. Hints are available there; using more than two lowers how much this attempt counts as evidence."
    )
    al_meta = {
        "activity": EX + ex["activity"],
        "object": f"{EX}{ex['activity']}-exercise",
        "check": f"checks/{ex['check']}",
        "hints": ex["hints"],
    }
    return {
        "cells": [
            cell("markdown", intro, "0"),
            cell("code", ex["setup"][language], "1"),
            cell("code", placeholder(language, ex["variables"]), "2", {"al": al_meta, "tags": ["al-exercise"]}),
            cell("markdown", references(ex), "3"),
        ],
        "metadata": {
            "kernelspec": KERNELSPEC[language],
            "language_info": LANGUAGE_INFO[language],
            "al": {"activity": EX + ex["activity"], "language": language, "generatedBy": "scripts/make_exercises.py"},
            "title": f"{ex['title']} ({name})",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    for folder in ("python", "r"):
        out = CONTENT / "exercises" / folder
        out.mkdir(parents=True, exist_ok=True)
        for stale in out.glob("*.ipynb"):
            stale.unlink()
    checks = CONTENT / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    for stale in checks.glob("*"):
        stale.unlink()
    for language in ("python", "r"):
        for ex in EXERCISES:
            path = CONTENT / "exercises" / language / f"{ex['file']}.ipynb"
            path.write_text(json.dumps(notebook(ex, language), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for ex in EXERCISES:
        (checks / f"{ex['check']}.py").write_text(python_check(ex["variables"]), encoding="utf-8")
        (checks / f"{ex['check']}.R").write_text(r_check(ex["variables"]), encoding="utf-8")
    print(f"wrote {len(EXERCISES) * 2} notebooks and {len(EXERCISES) * 2} checks; register has {len(REGISTER)} records")
    # Separate Python-only pilot requested for the DHIS2 adapter. The existing
    # paired Python/R exercise spec stays unchanged until the R pilot is built.
    from make_dhis2_pilot import main as make_dhis2_pilot
    make_dhis2_pilot()
    from make_learning_record_notebook import main as make_learning_record_notebook
    make_learning_record_notebook()
    from make_course_orientation import main as make_course_orientation
    make_course_orientation()


if __name__ == "__main__":
    main()
