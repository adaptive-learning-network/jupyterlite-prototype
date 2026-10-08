#!/usr/bin/env python3
"""Generate the Python-only Unit 1 data-to-decision pilot and its check."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content"
EX = "https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#"

# Synthetic weekly *reported* counts. A rise is a signal to verify, not a
# confirmed outbreak. This small table extends the Unit 1 data-to-action idea.
REPORTS = [
    {"district": "Kambia", "week": "previous", "reported_cases": 2},
    {"district": "Kambia", "week": "current", "reported_cases": 7},
    {"district": "Port Loko", "week": "previous", "reported_cases": 3},
    {"district": "Port Loko", "week": "current", "reported_cases": 4},
    {"district": "Bombali", "week": "previous", "reported_cases": 4},
    {"district": "Bombali", "week": "current", "reported_cases": 3},
]

INTRO = """**Course outline:** Unit 01 · Notebook 01 · Python

# From data to a public health decision

![Three-panel teaching comic: Laila reads anonymous counts, compares bars, and discusses a signal with a colleague.](../assets/laila-unit01-notebook01-comic.png)

*Laila has more reports than time. She needs to find the clearest signal, then check it before drawing a conclusion. Original teaching illustration; no dialogue is taken from the slides.*

<img src="../assets/unit1-v2-data-wisdom-pyramid.png" width="360" alt="Course pyramid with data at the base, followed by information, knowledge, and wisdom.">

*Slide connection: Unit 1, Version 2, slide 26. You will turn raw reported counts (data) into a district comparison (information), interpret the change (knowledge), and select a cautious action (wisdom).*

**Learning objective:** **Justify** one public health action from a synthetic surveillance summary.

The [Unit 1 course lesson](../../readings/ucsf/u01-n02-lesson.ipynb) describes Laila's problem as **data overload**: locating, cleaning, and transforming data into usable information takes time. It defines information as data organized with context, knowledge as interpreted patterns, and wisdom as decisions and actions informed by that knowledge. This short exercise follows that sequence.

## Scenario and task

Laila receives a small table of **synthetic weekly reported case counts**. The reports have not yet been verified. Run the setup cell to see the table. In the exercise cell:

1. Calculate each district's change: current week minus previous week.
2. Set `priority_district` to the district with the largest increase and `increase` to that numeric change.
3. Set `recommended_step` to one of the two strings below. Choose the first public health step supported by the table:
   - `"verify_reports_and_investigate"`: verify the reports and investigate the signal.
   - `"declare_confirmed_outbreak"`: declare a confirmed outbreak from these counts alone.

Then run the exercise cell. The **Learning** panel records each check, offers hints, and recommends the next activity. Afterward, write one sentence in the reflection cell explaining what the counts do and do not establish. The reflection is for you; it is not automatically graded.
"""

REFERENCES = """## References

- [UCSF FETP JupyterBook, Unit 1 lesson](../../readings/ucsf/u01-n02-lesson.ipynb), sections “Laila’s Problem: Data Overload” and “Transforming Data into Wisdom” ([pinned source](https://github.com/UCSF-IGHS/FETP/blob/7eca2ec9d4d6082e76c7061a4746f1ac69d4ca7b/FETP_book/_build/html/_sources/FETP_Unit_1.ipynb)).
- [FETP Unit 1 slides](https://docs.google.com/presentation/d/12B-A7_4LhTTfWXtbj3KOmZyWkyq8GPR5xCuIifawZVQ): the local Version 2 slide 23 introduces Laila's data overload; slide 26 supplies the reproduced data–information–knowledge–wisdom pyramid; slide 28 shows the information value cycle. The online deck may use different slide numbers.
- [FETP Unit 1 instructor guide](https://docs.google.com/document/d/17vQbKSFUWlu0NzVWhe_ZmPBXQQxbj9JKkEZI-TPpHOM).
- [FETP Unit 1 knowledge check](https://docs.google.com/forms/d/e/1FAIpQLSddLw3-yw2-kDUZfewy15d8mM22h2f30Jgynua3oibIWoskqw/viewform).

*The counts are synthetic and support practice in interpreting a signal; they are not outbreak evidence. The illustration was generated for this course prototype and is not a source slide.*
"""


def cell(kind: str, source: str, cell_id: str, metadata: dict | None = None) -> dict:
    value = {"cell_type": kind, "id": cell_id, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        value.update({"execution_count": None, "outputs": []})
    return value


def expected() -> tuple[str, int]:
    by_district = defaultdict(dict)
    for row in REPORTS:
        by_district[row["district"]][row["week"]] = row["reported_cases"]
    changes = {district: weeks["current"] - weeks["previous"] for district, weeks in by_district.items()}
    district = max(changes, key=changes.get)
    assert list(changes.values()).count(changes[district]) == 1
    return district, changes[district]


def main() -> None:
    setup = "reports = " + repr(REPORTS) + "\nfor row in reports:\n    print(row)\n"
    exercise = """# Use reports to calculate the weekly change for each district.
# Replace the None values. You may add helper variables above them.
priority_district = None
increase = None
recommended_step = None
"""
    meta = {"al": {"activity": EX + "act-u01-data-to-decision", "object": EX + "act-u01-data-to-decision-exercise", "check": "checks/u01-data-to-decision", "hints": ["For each district, pair its previous and current rows before comparing counts.", "Subtract previous from current for every district; choose the largest increase, not merely the largest current count.", "A reported increase is a signal. Verify the reports and investigate before declaring a confirmed outbreak."]}, "tags": ["al-exercise"]}
    reflection = "## Your reflection\n\nReplace this prompt with one sentence: *Why is the chosen action justified, and what remains uncertain?*\n\n" + REFERENCES
    notebook = {
        "cells": [cell("markdown", INTRO, "0"), cell("code", setup, "1"), cell("code", exercise, "2", meta), cell("markdown", reflection, "3")],
        "metadata": {"kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"}, "language_info": {"name": "python"}, "al": {"activity": EX + "act-u01-data-to-decision", "language": "python", "generatedBy": "scripts/make_unit01_pilot.py"}, "title": "Unit 01 Notebook 01: From data to a public health decision (Python)"},
        "nbformat": 4, "nbformat_minor": 5,
    }
    path = OUT / "exercises/python/u01-n01-data-to-decision.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    district, increase = expected()
    check = f'''import json as _al_json
def _al_check():
    g = globals()
    required = ("priority_district", "increase", "recommended_step")
    if any(g.get(name) is None for name in required):
        return "incomplete"
    try:
        if g["priority_district"] != {district!r} or type(g["increase"]) not in (int, float) or g["increase"] != {increase}:
            return "incorrect"
        if g["recommended_step"] != "verify_reports_and_investigate":
            return "incorrect"
    except (KeyError, TypeError, ValueError):
        return "incorrect"
    return "correct"
print("AL_OBSERVATION " + _al_json.dumps({{"outcome": _al_check()}}))
del _al_check
'''
    (OUT / "checks/u01-data-to-decision.py").write_text(check, encoding="utf-8")
    print("wrote Unit 01 Notebook 01 Python pilot and check")


if __name__ == "__main__":
    main()
