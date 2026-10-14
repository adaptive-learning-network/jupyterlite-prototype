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

*Laila needs a district summary, but late and incomplete reports make it hard to see what is happening.*

Laila's case continues across course units. Start with her reported counts in Unit 1, then follow the information through reporting systems in Unit 2. Unit 3 asks which items are raw **data** and which already organize data into **information**.

<img src="../assets/unit2-v2-surveillance-cycle.png" width="420" alt="Course surveillance cycle from detection and collection to analysis, interpretation, communication, and action.">

*Start at **data to information**: organize collected values into a pattern you can interpret.*

## Try one cell

Select the next cell and press **Shift+Enter**. It is a practice cell and does not affect your learning record.
"""
    run = "print('Ready to investigate with Laila.')"
    next_steps = """## Where to go next

1. Open **`u01-n01-data-to-decision.ipynb`** for Unit 1. The notebook gives you the case context, local visual, data, calculation, and decision in one place.
2. Continue with **`u02-n01-system-map.ipynb`** for Unit 2 and **`u03-n01-data-or-information.ipynb`** for Unit 3. In Unit 3 Notebook 01, sort the cards, then run **Check my choices**. The **Learning** panel records attempts and suggests what to do next.
3. If you want fuller course source text or slide pages, use the optional library at **`readings/ucsf/u00-n01-reading-index.ipynb`**. It is for reference and does not add observations.
4. After a few attempts, export your record from the Learning panel. The unscored **`08-my-learning-record.ipynb`** notebook in this folder shows how observations, estimates, and recommendations changed.

Notebook 00 is an orientation, so it has no scored exercise. Current scored Python exercises cover **Units 1, 2, and 3**. The readings are optional source material.
"""
    references = """## Optional course source library

- [Browse fuller course readings](../../readings/ucsf/u00-n01-reading-index.ipynb).
- [View the Unit 1 slides](../../readings/ucsf/u01-n01-slides.ipynb) and [Unit 2 slides](../../readings/ucsf/u02-n01-slides.ipynb) here in the course.
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
