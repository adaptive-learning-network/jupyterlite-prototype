#!/usr/bin/env python3
"""Keep course references at the end of every shipped notebook.

References name the course source without making an external page necessary to
complete a reading or exercise. Linked slide decks and companion readings are
shipped inside JupyterLite.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from import_ucsf_readings import SOURCES

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
READINGS = CONTENT / "readings/ucsf"
SOURCE_LABELS = {name: label for name, _, label, _, _ in SOURCES}
# Optional references: YouTube titles/publishers verified 2026-10-15;
# Seaborn's official 0.13.2 API reference verified 2026-10-22.
VERIFIED_EXTERNAL_REFERENCES: set[str] = {
    "https://seaborn.pydata.org/generated/seaborn.barplot.html",
    "https://www.youtube.com/watch?v=fLUygA8Hpfo",
    "https://www.youtube.com/watch?v=Fzc3j8QG_Mw",
    "https://www.youtube.com/watch?v=KSEUh-wj7Y0",
}
IMAGE_RE = re.compile(r'!\[[^]]*\]\(([^)]+)\)|<img\b[^>]*\bsrc=["\']([^"\']+)', re.I)
URL_RE = re.compile(r'https?://[^\s)>"`]+')
EDITORIAL_RE = re.compile(
    r"Source media:|Original PDF link|Available course deck for context:|"
    r"Source and visual attribution|archived UCSF notebook|exact slides are unverified|"
    r"Original teaching illustration|no dialogue is taken from the slides", re.I)


def references(path: Path) -> str:
    name = path.stem
    if path.parent == READINGS:
        if name in SOURCE_LABELS:
            label = SOURCE_LABELS[name].replace(" (archived build)", "")
            source = f"UCSF-IGHS, *FETP JupyterBook*, {label}."
        elif name == "u00-n02-version3-form-library":
            source = "Public Health Informatics for FETP, Version 3 course questions and forms."
        else:
            source = "Public Health Informatics for FETP, Units 1 and 2 course readings."
        slides = []
        if name.startswith("u00-"):
            slides = [1, 2]
        elif name.startswith("u01-"):
            slides = [1]
        elif name.startswith("u02-"):
            slides = [2]
        prefix = "assets/"
    else:
        source = "Public Health Informatics for FETP, course slides and practice exercises."
        if name == "u01-n01-data-to-decision":
            source = "UCSF-IGHS, *FETP JupyterBook*, Unit 1 informatics lesson; adapted with synthetic weekly reports."
        elif name == "u02-n01-system-map":
            source = "UCSF-IGHS, *FETP JupyterBook*, Unit 2 HIS case study and group work; adapted with a local system map."
        elif name.startswith(tuple(f"u{unit:02d}-n01-" for unit in range(4, 9))):
            from make_units04_08 import UNITS
            spec = next(row for row in UNITS if name == f"u{row['unit']:02d}-n01-{row['slug']}")
            source = spec["references"]
        elif name.startswith(tuple(f"u{unit:02d}-n01-" for unit in range(9, 15))):
            from make_units09_14 import UNITS
            spec = next(row for row in UNITS if name == f"u{row['unit']:02d}-n01-{row['slug']}")
            source = spec["references"]
        slides = [1] if name.startswith(("u01-", "u06-")) else [2]
        if name.startswith("u05-"):
            slides = []
        if name.startswith("u00-"):
            slides = [1, 2]
        if name == "u03-n08-my-learning-record":
            source = "Public Health Informatics for FETP, learner progress and adaptive practice."
            slides = []
        prefix = "../../readings/ucsf/assets/"

    lines = ["## References", "", f"- {source}"]
    if name == "u13-n01-analysis-dashboard":
        lines.append("- [Seaborn barplot reference](https://seaborn.pydata.org/generated/seaborn.barplot.html) (optional).")
    for unit in slides:
        pdf = f"{prefix}unit-{unit}-version-2-slides.pdf"
        if not (path.parent / pdf).is_file():
            raise FileNotFoundError(f"missing local slide deck: {path}: {pdf}")
        lines.append(f"- [Unit {unit} course slides (local PDF)]({pdf}).")
    return "\n".join(lines) + "\n"


def update(path: Path, check: bool) -> bool:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    desired = references(path)
    cells = notebook["cells"]
    existing = next((i for i, cell in enumerate(cells)
                     if cell["cell_type"] == "markdown" and
                     "".join(cell["source"]).startswith("## References\n")), None)
    if existing is not None and existing != len(cells) - 1:
        raise ValueError(f"References must be the final cell: {path}")
    if existing is None:
        used_ids = {cell.get("id") for cell in cells}
        cell_id = "references"
        while cell_id in used_ids:
            cell_id += "-next"
        cells.append({"cell_type": "markdown", "id": cell_id, "metadata": {},
                      "source": desired.splitlines(keepends=True)})
        changed = True
    else:
        changed = "".join(cells[existing]["source"]) != desired
        if changed:
            cells[existing]["source"] = desired.splitlines(keepends=True)
    if changed and not check:
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if check:
        needs_reflection = (path.parent == READINGS and path.stem in SOURCE_LABELS) or path.stem in {
            "u01-n01-data-to-decision", "u02-n01-system-map"} or path.stem.startswith(tuple(f"u{unit:02d}-n01-" for unit in range(4, 15)))
        if needs_reflection:
            controls = [cell for cell in cells if cell["cell_type"] == "code" and
                        '_reflection_section(' in "".join(cell["source"])]
            if (not controls or any('description="Record"' not in "".join(cell["source"]) for cell in controls)
                    or notebook["metadata"].get("kernelspec", {}).get("language") != "python"):
                raise ValueError(f"reflection requires response fields and a Python Jupyter kernel: {path}")
        for cell in cells:
            if cell["cell_type"] != "markdown":
                continue
            source = "".join(cell["source"])
            if re.search(r"Write your reasoning here|Enter your response here|Replace this prompt|Double-click this cell to write", source, re.I):
                raise ValueError(f"response placeholder requires an entry field and Record control: {path}")
            editorial = EDITORIAL_RE.search(source)
            if editorial and not source.startswith("## References\n"):
                raise ValueError(f"editorial material belongs in repository docs: {path}: {editorial.group()}")
            for url in URL_RE.findall(source):
                if url not in VERIFIED_EXTERNAL_REFERENCES:
                    raise ValueError(f"unreviewed external course link: {path}: {url}")
            for match in IMAGE_RE.finditer(source):
                image = match.group(1) or match.group(2)
                if image.startswith("attachment:"):
                    if image.removeprefix("attachment:") not in cell.get("attachments", {}):
                        raise ValueError(f"missing notebook image attachment: {path}: {image}")
                elif not (path.parent / image).is_file():
                    raise FileNotFoundError(f"missing local notebook image: {path}: {image}")
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if references need regeneration")
    args = parser.parse_args()
    paths = sorted(CONTENT.rglob("*.ipynb"))
    changed = [path for path in paths if update(path, args.check)]
    print(f"checked {len(paths)} notebooks; {len(changed)} need references")
    if args.check and changed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
