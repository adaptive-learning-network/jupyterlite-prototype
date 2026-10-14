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
VERIFIED_EXTERNAL_REFERENCES: set[str] = set()
IMAGE_RE = re.compile(r'!\[[^]]*\]\(([^)]+)\)|<img\b[^>]*\bsrc=["\']([^"\']+)', re.I)
URL_RE = re.compile(r'https?://[^\s)>"`]+')


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
        slides = [1] if name.startswith("u01-") else [2]
        if name.startswith("u00-"):
            slides = [1, 2]
        if name == "08-my-learning-record":
            source = "Public Health Informatics for FETP, learner progress and adaptive practice."
            slides = []
        prefix = "../../readings/ucsf/assets/"

    lines = ["## References", "", f"- {source}"]
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
        for cell in cells:
            if cell["cell_type"] != "markdown":
                continue
            source = "".join(cell["source"])
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
