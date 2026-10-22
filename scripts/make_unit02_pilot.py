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

# Trace Laila's reporting pathways

![Three-panel teaching comic: Laila reviews a clinical record, traces case and laboratory streams, and examines a district summary with a colleague seated across a shared table.](../assets/laila-unit02-notebook01-comic.png)

*Laila needs to know where a report begins and which systems carry it to the district.*

![Source HIS diagram: electronic patient and community records feed case alerts and reports; laboratory records feed laboratory reports; both reach the district health information system and then MOH.](../assets/unit2-ucsf-his-context.png)

*Follow the case and laboratory reporting branches to the district health information system and Ministry of Health (MOH). Ask who can access each system.*

**Learning objective:** **Trace** a case-report path and a laboratory-report path from source records to MOH.

## Laila's case

Kukuna Health Center calls about reports of fever and rash. Laila's team must prepare a surveillance summary. She needs to know where the data originates, which paper and electronic systems hold it, and who can use each system.

In the diagram above, build two **electronic** paths. For each path, use **Move up** and **Move down** to match the diagram: **MOH at the top, source records at the bottom**. Information travels **upward**, from the bottom of each list to the top. Select a stage first, then move it. Both lists start out of order. Select **Submit** below the lists for feedback on both reporting pathways. You can reorder and submit again; the Learning panel records each attempt. Here, a pathway means the sequence of reporting systems, rather than a geographic map.

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
from html import escape
from comm import create_comm

def _show_reporting_pathways():
    reporting_state = {"case_moves": 0, "lab_moves": 0}

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
    case_list = widgets.Select(options=case_order, rows=4, description="", layout=widgets.Layout(width="100%", min_width="0"))
    lab_list = widgets.Select(options=lab_order, rows=4, description="", layout=widgets.Layout(width="100%", min_width="0"))

    def move_stage(stage_list, direction, route_name):
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
            reporting_state["case_moves"] += 1
        else:
            reporting_state["lab_moves"] += 1
        feedback.value = "Order changed. Select Submit to check your current pathways."

    def route_controls(stage_list, route_name):
        up = widgets.Button(description="Move up", icon="arrow-up")
        down = widgets.Button(description="Move down", icon="arrow-down")
        up.on_click(lambda _: move_stage(stage_list, -1, route_name))
        down.on_click(lambda _: move_stage(stage_list, 1, route_name))
        return widgets.VBox([
            widgets.HTML("<b>Top: central level (MOH)</b>"),
            stage_list,
            widgets.HTML("<b>&uarr; Reporting flows upward from source records at the bottom.</b>"),
            widgets.HBox([up, down]),
        ], layout=widgets.Layout(width="100%", min_width="0"))

    def collect_reporting_pathways():
        return {
            "case": list(reversed(case_list.options)),
            "lab": list(reversed(lab_list.options)),
            "case_moves": reporting_state["case_moves"],
            "lab_moves": reporting_state["lab_moves"],
        }

    submit_button = widgets.Button(description="Submit", button_style="info", disabled=True)
    feedback = widgets.HTML(value="Connecting to your learning record...")
    submitted_pathways = widgets.HTML()
    submission_channel = create_comm(target_name="al.submit", data={"cell": "1"})

    def receive_submission(message):
        data = message["content"]["data"]
        if data.get("ready"):
            feedback.value = "Match the diagram: MOH at the top, source records at the bottom. Reporting flows upward. Then select Submit."
        elif data.get("outcome"):
            outcome = data["outcome"]
            if outcome == "Incomplete":
                feedback.value = "<b>Not complete yet.</b> Move stages in both pathways, then submit again. This attempt was recorded."
            else:
                messages = []
                for key, label in (("case", "Case pathway"), ("lab", "Laboratory pathway")):
                    expected = _expected_case if key == "case" else _expected_lab
                    correct = reporting_pathways[key] == expected
                    messages.append(f"<b>{label}: {'Correct' if correct else 'Incorrect'}.</b> " +
                                    ("Your layout matches the diagram; reports flow upward from source records to MOH." if correct else
                                     "Read upward: source records at the bottom, then reports, then the district system, with MOH at the top."))
                feedback.value = "<br>".join(messages) + "<br>Attempt recorded. See the Learning panel for your next suggestion."
        else:
            feedback.value = escape(data.get("error", "Could not record. Please try again."))
        submit_button.disabled = False
        for control in pathway_controls:
            control.disabled = False

    submission_channel.on_msg(receive_submission)

    def submit_reporting_pathways(_=None):
        global reporting_pathways
        reporting_pathways = collect_reporting_pathways()
        submitted_pathways.value = "<b>Submitted reporting flow</b><p>Read these arrows left to right: source records &rarr; reports &rarr; district &rarr; MOH. This is the upward flow in your lists and in the diagram.</p>" + "".join(
            "<p><b>" + label + ":</b> " + " &rarr; ".join(escape(stage) for stage in reporting_pathways[key]) + "</p>"
            for key, label in (("case", "Case pathway"), ("lab", "Laboratory pathway")))
        submit_button.disabled = True
        for control in pathway_controls:
            control.disabled = True
        feedback.value = "Checking and recording this attempt..."
        submission_channel.send({"submit": True})

    submit_button.on_click(submit_reporting_pathways)
    _expected_case = CASE_EXPECTED
    _expected_lab = LAB_EXPECTED
    case_controls = route_controls(case_list, "case")
    lab_controls = route_controls(lab_list, "lab")
    pathway_controls = [case_list, lab_list, *case_controls.children[3].children, *lab_controls.children[3].children]
    display(widgets.VBox([
        widgets.HTML("<b>1. Health facility case-report path</b>"),
        case_controls,
        widgets.HTML("<b>2. Laboratory-report path</b>"),
        lab_controls,
        submit_button, submitted_pathways, feedback,
    ]))

_show_reporting_pathways()
'''

ENDING = """## Continue the case

Use the **Learning** panel for the next activity. If a route was incorrect,
follow each arrow in the diagram and submit your revised reporting pathways.
"""

def cell(kind: str, source: str, cell_id: str, metadata: dict | None = None) -> dict:
    value = {"cell_type": kind, "id": cell_id, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        value.update({"execution_count": None, "outputs": []})
    return embed_images(value)


def main() -> None:
    from reflection_widgets import reflection_code
    meta = {"al": {"activity": EX + "act-u02-system-map", "object": EX + "act-u02-system-map-exercise",
                    "check": "checks/u02-system-map", "submission": "widget", "hints": [
                        "Start each path with its source record, then follow the arrows in the country HIS diagram.",
                        "Case alerts and laboratory reports are different branches; both feed the district health information system.",
                        "From the district health information system, the diagram points to MOH. Check the order of both branches.",
                    ]}, "tags": ["al-exercise"]}
    notebook = {
        "cells": [cell("markdown", INTRO, "0"),
                  cell("code", SETUP.replace("CASE_EXPECTED", repr(list(CASE_ROUTE))).replace("LAB_EXPECTED", repr(list(LAB_ROUTE))), "1", {**meta, "jupyter": {"source_hidden": True}}),
                  cell("markdown", "Select **Submit** above to check your current reporting pathways. Keep MOH at the top and source records at the bottom, as in the diagram. Feedback shows the upward reporting flow and whether each pathway is correct. Reorder and submit again to retry.", "2"),
                  cell("markdown", "## Reflect on system use\n\nRun the next cell to enter your reflections. Select **Record** to save them in this browser. Your responses are unscored.", "3"),
                  cell("code", reflection_code("exercise:u02-n01", ["Who needs each case or laboratory report?", "What access question would you verify with the district team?"]), "reflection-fields", {"jupyter": {"source_hidden": True}}),
                  cell("markdown", ENDING, "continue")],
        "metadata": {"kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
                     "language_info": {"name": "python"},
                     "al": {"activity": EX + "act-u02-system-map", "language": "python", "generatedBy": "scripts/make_unit02_pilot.py"},
                     "title": "Unit 02 Notebook 01: Trace Laila's reporting pathways (Python)"},
        "nbformat": 4, "nbformat_minor": 5,
    }
    path = OUT / "exercises/python/u02-n01-system-map.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    check = f'''import json as _al_json

def _al_check():
    candidate = globals().get("reporting_pathways")
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
