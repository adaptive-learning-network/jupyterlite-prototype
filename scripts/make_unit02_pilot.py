#!/usr/bin/env python3
"""Generate the Python-only Unit 2 HIS system-map exercise and check."""

from __future__ import annotations

import json
from pathlib import Path

from notebook_images import embed_images

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content"
EX = "https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#"

CASE_ROUTE = (
    "Electronic patient records",
    "Electronic case alerts and reports",
    "District health information system",
    "Ministry of Health",
)
LAB_ROUTE = (
    "Electronic laboratory records",
    "Electronic laboratory reports",
    "District health information system",
    "Ministry of Health",
)

INTRO = """**Course outline:** Unit 02 · Notebook 01 · Python

# Map Laila's reporting systems

![Three-panel teaching comic: Laila reviews a clinical record, traces case and laboratory streams, and examines a district summary with a colleague.](../assets/laila-unit02-notebook01-comic.png)

*Laila needs to know where a report begins and which systems carry it to the district.*

![Source HIS diagram: electronic patient and community records feed case alerts and reports; laboratory records feed laboratory reports; both reach the district health information system and then MOH.](../assets/unit2-ucsf-his-context.png)

*Follow the case and laboratory reporting branches to the district health information system and Ministry of Health (MOH). Ask who can access each system.*

**Learning objective:** **Trace** a case-report path and a laboratory-report path from source records to MOH.

## Laila's case

Kukuna Health Center calls about reports of fever and rash. Laila's team must prepare a surveillance summary. She needs to know where the data originates, which paper and electronic systems hold it, and who can use each system.

In the diagram above, build two **electronic** paths. For each path, use **Move up** and **Move down** to put the four stages in the order information travels. Select a stage first, then move it. Both lists start out of order. Run **Check my map** after moving stages in both lists. You can correct a route and check again; the Learning panel records each attempt.

Trace the fever-and-rash reporting path shown in the diagram.
"""

SETUP = '''# Run once to display the route controls. Re-running resets both routes.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from IPython.display import display

case_order = [
    "District health information system",
    "Electronic patient records",
    "Ministry of Health",
    "Electronic case alerts and reports",
]
lab_order = [
    "Electronic laboratory reports",
    "Ministry of Health",
    "Electronic laboratory records",
    "District health information system",
]
case_moves = 0
lab_moves = 0
case_list = widgets.Select(options=case_order, rows=4, description="Case path", layout=widgets.Layout(width="650px"))
lab_list = widgets.Select(options=lab_order, rows=4, description="Lab path", layout=widgets.Layout(width="650px"))

def move_stage(stage_list, direction, route_name):
    global case_moves, lab_moves
    items = list(stage_list.options)
    selected = stage_list.value
    if selected not in items:
        return
    old = items.index(selected)
    new = old + direction
    if not 0 <= new < len(items):
        return
    items[old], items[new] = items[new], items[old]
    stage_list.options = items
    stage_list.value = selected
    if route_name == "case":
        case_moves += 1
    else:
        lab_moves += 1

def route_controls(stage_list, route_name):
    up = widgets.Button(description="Move up", icon="arrow-up")
    down = widgets.Button(description="Move down", icon="arrow-down")
    up.on_click(lambda _: move_stage(stage_list, -1, route_name))
    down.on_click(lambda _: move_stage(stage_list, 1, route_name))
    return widgets.VBox([stage_list, widgets.HBox([up, down])])

def collect_system_map():
    return {
        "case": list(case_list.options),
        "lab": list(lab_list.options),
        "case_moves": case_moves,
        "lab_moves": lab_moves,
    }

display(widgets.VBox([
    widgets.HTML("<b>1. Health facility case-report path</b>"),
    route_controls(case_list, "case"),
    widgets.HTML("<b>2. Laboratory-report path</b>"),
    route_controls(lab_list, "lab"),
]))
'''

EXERCISE = '''# Check my map: run this cell after moving stages in both paths.
system_map = collect_system_map()
print("Case path:", " → ".join(system_map["case"]))
print("Lab path: ", " → ".join(system_map["lab"]))
'''

ENDING = """## Continue the case

Use the **Learning** panel for the next activity. If a route was incorrect,
follow each arrow in the diagram and try the same map again.
"""

def cell(kind: str, source: str, cell_id: str, metadata: dict | None = None) -> dict:
    value = {"cell_type": kind, "id": cell_id, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        value.update({"execution_count": None, "outputs": []})
    return embed_images(value)


def main() -> None:
    from reflection_widgets import reflection_code
    meta = {"al": {"activity": EX + "act-u02-system-map", "object": EX + "act-u02-system-map-exercise",
                    "check": "checks/u02-system-map", "hints": [
                        "Start each path with its source record, then follow the arrows in the country HIS diagram.",
                        "Case alerts and laboratory reports are different branches; both feed the district health information system.",
                        "From the district health information system, the diagram points to MOH. Check the order of both branches.",
                    ]}, "tags": ["al-exercise"]}
    notebook = {
        "cells": [cell("markdown", INTRO, "0"),
                  cell("code", SETUP, "1", {"jupyter": {"source_hidden": True}}),
                  cell("code", EXERCISE, "2", meta),
                  cell("markdown", "## Reflect on system use\n\nRun the next cell to enter your reflections. Select **Record** to save them in this browser. Your responses are unscored.", "3"),
                  cell("code", reflection_code("exercise:u02-n01", ["Who needs each case or laboratory report?", "What access question would you verify with the district team?"]), "reflection-fields", {"jupyter": {"source_hidden": True}}),
                  cell("markdown", ENDING, "continue")],
        "metadata": {"kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
                     "language_info": {"name": "python"},
                     "al": {"activity": EX + "act-u02-system-map", "language": "python", "generatedBy": "scripts/make_unit02_pilot.py"},
                     "title": "Unit 02 Notebook 01: Map Laila's reporting systems (Python)"},
        "nbformat": 4, "nbformat_minor": 5,
    }
    path = OUT / "exercises/python/u02-n01-system-map.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    check = f'''import json as _al_json

def _al_check():
    candidate = globals().get("system_map")
    if not isinstance(candidate, dict) or not candidate.get("case_moves") or not candidate.get("lab_moves"):
        return "incomplete"
    if candidate.get("case") != {list(CASE_ROUTE)!r} or candidate.get("lab") != {list(LAB_ROUTE)!r}:
        return "incorrect"
    return "correct"

print("AL_OBSERVATION " + _al_json.dumps({{"outcome": _al_check()}}))
del _al_check
'''
    checks = ROOT / "app-assets/adaptive-learning/checks"
    checks.mkdir(parents=True, exist_ok=True)
    (checks / "u02-system-map.py").write_text(check, encoding="utf-8")
    print("wrote Unit 02 Notebook 01 Python pilot and check")


if __name__ == "__main__":
    main()
