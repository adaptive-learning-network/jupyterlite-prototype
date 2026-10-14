#!/usr/bin/env python3
"""Build the unscored local form-reference notebook from reviewed Markdown."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "course-materials/version3-form-library.md"
OUTPUT = ROOT / "content/readings/ucsf/u00-n02-version3-form-library.ipynb"


def main() -> None:
    sections = SOURCE.read_text(encoding="utf-8").split("<!-- notebook cell -->")
    if len(sections) != 4:
        raise ValueError("form library must have four reviewed sections")
    cells = [
        {"cell_type": "markdown", "id": str(i), "metadata": {},
         "source": section.strip().splitlines(keepends=True)}
        for i, section in enumerate(sections)
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "title": "Practice questions for Laila's case",
            "generatedBy": "scripts/make_form_library.py",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
