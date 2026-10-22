#!/usr/bin/env python3
"""Generate the unscored learner-record inspection notebook."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "content/exercises/python/u03-n08-my-learning-record.ipynb"


def cell(kind, source, cell_id):
    result = {"cell_type": kind, "id": cell_id, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update({"execution_count": None, "outputs": []})
    return result


def main():
    intro = """**Course outline:** Unit 03 | Notebook 08 | Python

# My learning record

Review your attempts, progress, suggested next activities, and recorded reflections below.

This view is **unscored** and does not change your learning record. No code needs to run.
Your record stays in this browser. In the Learning panel, **Download reflections** keeps a readable copy of explicitly recorded writing. **Export evidence** downloads scored attempts and progress as RDF; it excludes reflection text and notebook edits. Download edited notebooks separately from the File menu. Unrecorded text is not included. These downloads do not restore browser storage automatically. Keep your browser storage while using the course.
"""
    # A saved MIME output is rendered directly by the browser extension. Its
    # payload has no learner data: the renderer reads the current local store.
    record = cell("code", '''from IPython.display import display
display({"application/vnd.al.learner-record+json": {"version": 1},
         "text/plain": "Open this notebook in the course JupyterLite site to view your learning record."}, raw=True)
''', "record-view")
    record["metadata"] = {"jupyter": {"source_hidden": True}, "editable": False,
                          "al": {"view": "learner-record"}}
    record["outputs"] = [{"output_type": "display_data", "metadata": {}, "data": {
        "application/vnd.al.learner-record+json": {"version": 1},
        "text/plain": ["Open this notebook in the course JupyterLite site to view your learning record."]
    }}]
    notebook = {
        "cells": [cell("markdown", intro, "0"), record],
        "metadata": {
            "kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
            "language_info": {"name": "python"},
            "title": "My learning record (Python)",
            "al": {"language": "python", "generatedBy": "scripts/make_learning_record_notebook.py"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote unscored learner-record notebook")


if __name__ == "__main__":
    main()
