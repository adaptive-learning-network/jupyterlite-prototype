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
    viewer = (ROOT / "scripts/learning_record_view.py").read_text(encoding="utf-8")
    intro = """**Course outline:** Unit 03 | Notebook 08 | Python

# My learning record: what did the adaptive system record?

This final, **unscored** notebook shows your own learner graph. It does not submit an answer or add an observation.

1. In the **Learning** panel, choose **Export record**. Your browser downloads `learner-record.nq`.
2. In the JupyterLite file browser, open this notebook's folder (`exercises/python`) and upload that file here.
3. Run the next two cells. They use only files in this browser's JupyterLite workspace; there are no network requests.

To see changes across retries, export after each attempt, rename each download `learner-record-01.nq`, `learner-record-02.nq`, and so on, then upload those files together. The notebook reads them in filename order. The export contains an opaque learner ID and your learning history; share it only if you choose to.
"""
    run = """from IPython.display import Markdown, display

files = find_exports()
display(Markdown(render_report([(path.name, path.read_text(encoding="utf-8")) for path in files])))
"""
    references = """## Read your record

The browser-local record contains observations from your attempts. The exported graph also contains recalculated estimates and recommendations. This notebook reads the export snapshot you upload here; it does not change your record.
"""
    notebook = {
        "cells": [cell("markdown", intro, "0"), cell("code", viewer, "1"), cell("code", run, "2"), cell("markdown", references, "3")],
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
