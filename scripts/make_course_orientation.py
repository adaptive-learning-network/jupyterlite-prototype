#!/usr/bin/env python3
"""Generate the unscored course entry notebook."""

from __future__ import annotations

import json
from pathlib import Path

from notebook_images import embed_images

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "content/exercises/python/u00-n00-start-here.ipynb"


def cell(kind: str, source: str, cell_id: str) -> dict:
    result = {"cell_type": kind, "id": cell_id, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update({"execution_count": None, "outputs": []})
    return embed_images(result)


def main() -> None:
    intro = """**Course outline:** Unit 00 · Notebook 00 · Start here

# Welcome to the FETP informatics exercises

These notebooks turn course questions into small, hands-on investigations. You will work with **synthetic data**, run code in your browser, and use the **Learning** panel to see feedback and a suggested next activity. Your work stays in this browser unless you choose to export it.

## Meet the cast

| Laila | Her supervisor | Martha | You |
| :--- | :--- | :--- | :--- |
| 👩🏽‍💻 The course case-study character. She needs useful information from surveillance data. | 🧑🏽‍⚕️ Needs a report that supports decisions. | 📋 A community health worker who collects and reports data in a later course scenario. | 🔎 The investigator: run the exercises, inspect the evidence, and decide what to report. |

<img src="../assets/unit2-v2-laila-problem.png" width="600" alt="Course slide: Laila needs a district TB summary report and faces delayed, incomplete, fragmented data.">

*Slide connection: Unit 2, Version 2, slide 2 introduces Laila's reporting problem. Martha appears in slides 65–67 of the same deck.*

Laila's case continues across course units. The first scored notebook starts with a small choice: which items are raw **data**, and which already organize data into **information**?

<img src="../assets/unit2-v2-surveillance-cycle.png" width="420" alt="Course surveillance cycle from detection and collection to analysis, interpretation, communication, and action.">

*Slide connection: Unit 2, Version 2, slide 3. Notebook 01 begins at the **data → information** part of this cycle.*

## Try one cell

Select the next cell and press **Shift+Enter**. It is a practice cell and does not affect your learning record.
"""
    run = "print('Ready to investigate with Laila.')"
    next_steps = """## Where to go next

1. Browse the UCSF Unit 1 and Unit 2 source readings in **`readings/ucsf/u00-n01-reading-index.ipynb`**. They include the course narrative, case questions, and diagrams. Reading them does not add observations.
2. Open **`u03-n01-data-or-information.ipynb`** in this folder for Unit 3 Notebook 01 in Python. The matching R notebook is in `exercises/r`. You can also try **`u01-n01-data-to-decision.ipynb`** for the Unit 1 exercise.
3. In Unit 3 Notebook 01, run the collapsed setup cell, sort the cards into Data or Information, then run **Check my choices**. The **Learning** panel records the attempt and offers hints or a next activity.
4. After a few attempts, export your record from the Learning panel. The unscored **`08-my-learning-record.ipynb`** notebook in this folder can show how observations, estimates, and recommendations changed.

Notebook 00 is an orientation, so it has no scored exercise. Current scored exercises cover **Units 1 and 3**. Unit 2 has source readings; its local scored exercises are still planned.
"""
    references = """## Course sources

- [FETP Unit 3 instructor guide](https://docs.google.com/document/d/1B6qrW7QBcL4uCO85QPIN8pJ--37S8N6j3xkT87qBACA) and [slides](https://docs.google.com/presentation/d/1EXkFCxffubjhpM94373WiJ0a9_V0Tsfn) introduce the data-to-information work used in Notebook 01.
- [FETP course JupyterBook](https://github.com/UCSF-IGHS/FETP) supplies the wider course sequence and case context.
- The embedded visuals come from *Unit 2, Version 2, Detection and Diagnosis*, slides 2–3 of the deck supplied with the project. Martha's scenario appears on slides 65–67.

Laila is the case-study character in the course materials. The dialogue and visual cues in these notebooks are teaching prompts, not quotations from the slides.
"""
    notebook = {
        "cells": [
            cell("markdown", intro, "0"),
            cell("code", run, "1"),
            cell("markdown", next_steps, "2"),
            cell("markdown", references, "3"),
        ],
        "metadata": {
            "kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
            "language_info": {"name": "python"},
            "title": "Unit 00 · Notebook 00 · Start here",
            "al": {"language": "python", "generatedBy": "scripts/make_course_orientation.py"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote unscored course orientation notebook")


if __name__ == "__main__":
    main()
