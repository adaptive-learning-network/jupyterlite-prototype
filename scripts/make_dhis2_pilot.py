#!/usr/bin/env python3
"""Generate a Python-only, browser-local DHIS2 adapter exercise.

The adapter is intentionally small. It resembles selected DHIS2 read endpoints,
but makes no network requests and does not claim compatibility with a server.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content"
EX = "https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#"

PROGRAM = "P_MEASLES"
KAMBIA = "OU_KAMBIA"
ONSET = "DE_ONSET"

FIXTURE = {
    "organisationUnits": [
        {"id": KAMBIA, "displayName": "Kambia District"},
        {"id": "OU_PORT_LOKO", "displayName": "Port Loko District"},
    ],
    "dataElements": [
        {"id": ONSET, "displayName": "Date of rash onset", "valueType": "DATE"},
        {"id": "DE_AGE", "displayName": "Age in years", "valueType": "INTEGER"},
        {"id": "DE_CLASS", "displayName": "Case classification", "valueType": "TEXT"},
    ],
    "events": [
        {"event": "EV_001", "program": PROGRAM, "orgUnit": KAMBIA, "occurredAt": "2021-10-20", "dataValues": [{"dataElement": ONSET, "value": "2021-10-18"}, {"dataElement": "DE_AGE", "value": "4"}, {"dataElement": "DE_CLASS", "value": "suspected"}]},
        {"event": "EV_002", "program": PROGRAM, "orgUnit": KAMBIA, "occurredAt": "2021-10-23", "dataValues": [{"dataElement": ONSET, "value": "2021-10-21"}, {"dataElement": "DE_AGE", "value": "8"}, {"dataElement": "DE_CLASS", "value": "suspected"}]},
        {"event": "EV_003", "program": PROGRAM, "orgUnit": KAMBIA, "occurredAt": "2021-10-27", "dataValues": [{"dataElement": ONSET, "value": ""}, {"dataElement": "DE_AGE", "value": "2"}, {"dataElement": "DE_CLASS", "value": "suspected"}]},
        {"event": "EV_004", "program": PROGRAM, "orgUnit": KAMBIA, "occurredAt": "2021-11-02", "dataValues": [{"dataElement": ONSET, "value": "2021-10-30"}, {"dataElement": "DE_AGE", "value": "13"}, {"dataElement": "DE_CLASS", "value": "probable"}]},
        {"event": "EV_005", "program": PROGRAM, "orgUnit": KAMBIA, "occurredAt": "2021-11-05", "dataValues": [{"dataElement": ONSET, "value": "2021-11-04"}, {"dataElement": "DE_AGE", "value": "6"}, {"dataElement": "DE_CLASS", "value": "confirmed"}]},
        {"event": "EV_006", "program": PROGRAM, "orgUnit": "OU_PORT_LOKO", "occurredAt": "2021-10-25", "dataValues": [{"dataElement": ONSET, "value": "2021-10-24"}, {"dataElement": "DE_AGE", "value": "5"}, {"dataElement": "DE_CLASS", "value": "suspected"}]},
        {"event": "EV_007", "program": PROGRAM, "orgUnit": "OU_PORT_LOKO", "occurredAt": "2021-11-03", "dataValues": [{"dataElement": ONSET, "value": "2021-11-01"}, {"dataElement": "DE_AGE", "value": "7"}, {"dataElement": "DE_CLASS", "value": "probable"}]},
    ],
}

ADAPTER = '''from copy import deepcopy

class CourseDhis2Adapter:
    """A read-only, in-memory subset of DHIS2-like GET responses."""

    def __init__(self, fixture):
        self._fixture = deepcopy(fixture)

    def get(self, path, params=None):
        params = dict(params or {})
        if path == "/api/organisationUnits":
            if params:
                raise ValueError("organisationUnits does not support query parameters in this pilot")
            return {"organisationUnits": deepcopy(self._fixture["organisationUnits"])}
        if path == "/api/dataElements":
            if params:
                raise ValueError("dataElements does not support query parameters in this pilot")
            return {"dataElements": deepcopy(self._fixture["dataElements"])}
        if path == "/api/tracker/events":
            if set(params) != {"program", "orgUnit"}:
                raise ValueError("events requires program and orgUnit")
            if params["program"] != "P_MEASLES":
                raise ValueError("unknown program")
            if params["orgUnit"] not in {u["id"] for u in self._fixture["organisationUnits"]}:
                raise ValueError("unknown organisation unit")
            return {"events": deepcopy([e for e in self._fixture["events"]
                                        if e["program"] == params["program"]
                                        and e["orgUnit"] == params["orgUnit"]])}
        raise ValueError("unsupported endpoint: " + str(path))

api = CourseDhis2Adapter(FIXTURE)
'''

INTRO = """**Course outline:** Unit 03 | Notebook 07 | Python

# Get a district measles summary, one step at a time

Laila needs a short briefing: **How many measles case-event records are available for Kambia District, what onset period do they cover, and how complete are the onset dates?**

**Learning objective:** **Explore** district case-event records using software.

You have already distinguished individual case records from aggregate counts. Here you will retrieve individual records and turn them into a small summary. All Python is supplied. Run each code cell with **Shift+Enter**, read its output, then continue. You do not need to invent API commands or memorize IDs.

These are invented training records in a **browser-local simulation**. No connection to a health information system is needed. In this example, each event represents one case record; the count is **not** a count of laboratory-confirmed cases.

## The route through this notebook

1. Find the district: which records belong in Laila's briefing?
2. Read the dictionary: which field means rash onset?
3. Request the records for that district and surveillance program.
4. Read an ordinary table instead of a nested computer response.
5. Count records, count missing onset dates, and describe the known onset period.
6. Select **Submit**, then reflect on the missing date.

## A few terms before you start

| Familiar idea | Term used by the simulated system | What it means here |
| --- | --- | --- |
| Ask software for data | API request | A structured request, similar to specifying a filter in a reporting tool. |
| Read, rather than change, records | `api.get(...)` | The Python instruction that asks this simulation for a response. |
| A list you want to open | Endpoint, such as `/api/organisationUnits` | The name of a collection inside the simulation. It is not a website you need to visit. |
| District | Organisation unit | A location used to select records. |
| Dictionary field | Data element | A variable, such as Date of rash onset. |
| Internal code | ID | The computer's label for a district or variable. We look it up beside its readable name. |

Run the next collapsed setup cell once. It prepares the simulation; you do not need to read or edit its infrastructure code.
"""

DISTRICT_TEXT = """## 1. Which district do we need?

Start with the **place** in Laila's question: Kambia District. The first request returns a list of districts and their internal codes.

`api.get(...)` asks for the list. The response contains a named list, `organisationUnits`; square brackets open that list. The supplied loop reads each district name and keeps the ID next to **Kambia District**. You can reuse this pattern without writing it yourself.

**Run the cell. Check:** Does the selected name say Kambia District? Its ID is just a computer label, not another geographic level.
"""
DISTRICT_CODE = 'district_name = "Kambia District"\ndistrict_response = api.get("/api/organisationUnits")\ndistricts = district_response["organisationUnits"]\nshow_table(districts, [("displayName", "District name"), ("id", "ID used in a request")])\n\norg_unit = None\nfor district in districts:\n    if district["displayName"] == district_name:\n        org_unit = district["id"]\nif org_unit is None:\n    raise ValueError("Choose a district name from the table above.")\nprint("Selected district:", district_name, "| ID:", org_unit)\n'

DICTIONARY_TEXT = """## 2. Which date answers the epidemiologic question?

Laila wants to describe **when illness began**, so use **Date of rash onset**. A data dictionary connects the readable field name, its internal ID, and its type. `DATE` means a date; the other fields here contain an age or a classification.

Run the cell to see the dictionary and select the onset field by its name. The pattern is the same as selecting the district in Step 1.

**Check:** The selected field should say Date of rash onset. A case-event date and a symptom-onset date are different concepts; we will compare them in Step 4.
"""
DICTIONARY_CODE = 'onset_label = "Date of rash onset"\ndictionary_response = api.get("/api/dataElements")\ndata_elements = dictionary_response["dataElements"]\nshow_table(data_elements, [("displayName", "Field name"), ("id", "Field ID"), ("valueType", "Type")])\n\nonset_element = None\nfor element in data_elements:\n    if element["displayName"] == onset_label:\n        onset_element = element["id"]\nif onset_element is None:\n    raise ValueError("Choose a field name from the dictionary above.")\nprint("Selected field:", onset_label, "| ID:", onset_element)\n'

EVENTS_TEXT = """## 3. Ask for the right records

Now specify **what** and **where**:

| Request setting | Meaning |
| --- | --- |
| `program: P_MEASLES` | The measles surveillance program in this simulation. This code is supplied for you. |
| `orgUnit: org_unit` | The district ID you selected in Step 1. |

Both settings are needed. A district filter alone would not say which surveillance program to use. The response has a list named `events`; the next cell opens it and tells you how many records came back. An optional preview shows one raw computer record. You do not need to decode it yourself; Step 4 turns the selected field into a readable column.

**Check:** The printed district should still be Kambia. Retrieving records does not establish that they are complete, unique, or all confirmed cases.
"""
EVENTS_CODE = 'request_settings = {"program": "P_MEASLES", "orgUnit": org_unit}\nprint("Request settings:", request_settings)\nevent_response = api.get("/api/tracker/events", request_settings)\nevents = event_response["events"]\nprint("Retrieved", len(events), "case-event records for", district_name)\nif events:\n    show_event_preview(events[0])\n'

FLATTEN_TEXT = """## 4. Turn the response into a table you can read

The response stores each event's measurements inside a list called `dataValues`. Each measurement pairs a **field ID** with a **value**. This is a computer storage layout, not a new epidemiologic concept.

The supplied code opens each event, finds the field selected in Step 2, and puts its value into an onset-date column. The resulting table has **one row per case-event record**.

- **Event ID:** the record's identifier in this example.
- **Event date:** the date attached to the surveillance event; do not assume it means symptom onset or date of entry.
- **Rash onset date:** the field we selected from the dictionary.

**Before the summary:** Look down the onset column. Is any date missing? Compare an event date with its onset date. They need not be the same. A blank onset means unknown; it does not mean the event date is a valid replacement.
"""
FLATTEN_CODE = 'onset_rows = []\nfor event in events:\n    onset_value = ""\n    for measurement in event["dataValues"]:\n        if measurement["dataElement"] == onset_element:\n            onset_value = measurement["value"]\n    onset_rows.append({\n        "event": event["event"],\n        "event_date": event["occurredAt"],\n        "onset": onset_value,\n    })\nshow_table(onset_rows, [("event", "Event ID"), ("event_date", "Event date (not onset)"), ("onset", "Rash onset date")])\n'

SUMMARY_TEXT = """## 5. Describe the records and their limitations

The summary answers three different questions:

| Measure | How the code gets it | What it tells Laila |
| --- | --- | --- |
| Case-event records | Count all retrieved records | How many records were selected, regardless of onset completeness. |
| Missing onset dates | Count blank onset values | How many records cannot be placed on an onset-based epidemic curve yet. |
| Earliest and latest known onset | Compare only nonblank onset dates | The onset period represented by known dates, not necessarily the full outbreak duration. |

`len` counts entries. `min` and `max` find the earliest and latest known dates here because these dates use the same `YYYY-MM-DD` format. We keep blank dates separate; we do not substitute the event date.

Run the cell and compare the summary with the table above. **A record with missing onset still contributes to the record count.**
"""
SUMMARY_CODE = 'n_cases = len(events)\nn_missing_onset = 0\nknown_onsets = []\nfor row in onset_rows:\n    if row["onset"] == "":\n        n_missing_onset += 1\n    else:\n        known_onsets.append(row["onset"])\n\nfirst_onset = min(known_onsets) if known_onsets else None\nlast_onset = max(known_onsets) if known_onsets else None\nshow_table([\n    {"measure": "Selected case-event records", "value": n_cases},\n    {"measure": "Missing onset dates", "value": n_missing_onset},\n    {"measure": "Earliest known onset", "value": first_onset},\n    {"measure": "Latest known onset", "value": last_onset},\n], [("measure", "Measure"), ("value", "Result")])\n'

TABLE_HELPER = '\ndef show_table(rows, columns):\n    from html import escape\n    from IPython.display import HTML, display\n    headings = "".join("<th style=\'text-align:left;padding:0.4rem\'>" + escape(label) + "</th>" for _, label in columns)\n    body = []\n    for row in rows:\n        cells = []\n        for key, _ in columns:\n            value = row.get(key)\n            text = "Missing" if value is None or value == "" else str(value)\n            cells.append("<td style=\'padding:0.4rem;border-bottom:1px solid #ddd\'>" + escape(text) + "</td>")\n        body.append("<tr>" + "".join(cells) + "</tr>")\n    display(HTML("<table><thead><tr>" + headings + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"))\n'

SUBMIT_CODE = '# Run to display Submit for your guided exploration.\ntry:\n    import ipywidgets as widgets\nexcept ImportError:\n    import piplite\n    await piplite.install("ipywidgets==8.1.7")\n    import ipywidgets as widgets\nfrom comm import create_comm\nfrom html import escape\nfrom IPython.display import display\n\ndef _show_dhis2_submit():\n    button = widgets.Button(description="Submit", button_style="info", disabled=True)\n    status = widgets.HTML(value="Connecting to your learning record...")\n    channel = create_comm(target_name="al.submit", data={"cell": "1"})\n    def receive(message):\n        data = message["content"]["data"]\n        if data.get("ready"):\n            status.value = "Run Steps 1-5, then submit this guided exploration."\n        elif data.get("outcome") == "Incomplete":\n            status.value = "<b>Not complete yet.</b> Run each code cell in Steps 1-5, in order, then submit again. This attempt was recorded."\n        elif data.get("outcome") == "Incorrect":\n            status.value = "<b>Check the district, date field, and summary.</b> Laila needs Kambia District and Date of rash onset. Rerun Steps 1-5 in order, keeping missing onset dates separate from event dates. This attempt was recorded."\n        elif data.get("outcome") == "Correct":\n            status.value = "<b>Guided exploration complete.</b> Your selected records and summary match Laila\'s question. This attempt was recorded. Now explain the missing-date limitation in the reflection below."\n        else:\n            status.value = escape(data.get("error", "Could not record. Please submit again."))\n        button.disabled = False\n    channel.on_msg(receive)\n    def submit(_):\n        button.disabled = True\n        status.value = "Checking and recording your guided exploration..."\n        channel.send({"submit": True})\n    button.on_click(submit)\n    display(button, status)\n\n_show_dhis2_submit()\n'

REFERENCES = """## Continue Laila's investigation

For another practice run, change only `district_name` in Step 1 to **Port Loko District**, then rerun Steps 1-5. What changes in the returned records? Return it to **Kambia District** and rerun the steps before submitting Laila's task.

Next, open [My learning record](u03-n08-my-learning-record.ipynb) to review what your attempts recorded.
"""


def cell(kind: str, source: str, cell_id: str, metadata: dict | None = None) -> dict:
    result = {"cell_type": kind, "id": cell_id, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update({"execution_count": None, "outputs": []})
    return result


def expected() -> dict:
    events = [e for e in FIXTURE["events"] if e["program"] == PROGRAM and e["orgUnit"] == KAMBIA]
    dates = [v["value"] for e in events for v in e["dataValues"] if v["dataElement"] == ONSET and v["value"]]
    return {"ids": [e["event"] for e in events], "n_cases": len(events), "n_missing_onset": len(events) - len(dates), "first_onset": min(dates), "last_onset": max(dates)}


def main() -> None:
    from missingness_visuals import LESSON as missingness_lesson, PLOT_CODE, RENDERER
    setup = "import json\nFIXTURE = json.loads(" + repr(json.dumps(FIXTURE, separators=(",", ":"))) + ")\n" + ADAPTER
    from reflection_widgets import reflection_code
    setup += RENDERER
    setup += TABLE_HELPER + "\ndef show_event_preview(event):\n    from html import escape\n    from IPython.display import HTML, display\n    display(HTML('<details><summary>Optional: inspect one computer record</summary><pre style=\"white-space:pre-wrap\">' + escape(json.dumps(event, indent=2)) + '</pre></details>'))\n" + "\norg_unit = events = onset_element = n_cases = n_missing_onset = first_onset = last_onset = None\nprint('Simulation ready. Continue with Step 1.')\n"
    metadata = {"al": {"activity": EX + "act-dhis2-query", "object": EX + "act-dhis2-query-exercise", "check": "checks/dhis2-query", "submission": "widget", "hints": [
        "Run each supplied cell in Steps 1-5 in order; Step 1 selects Kambia District.",
        "Step 2 selects Date of rash onset. Step 4 shows that field alongside the event date; blanks mean unknown onset.",
        "Step 5 counts every retrieved record, counts blank onset dates separately, and finds the date range from known onset dates only."
    ]}, "tags": ["al-exercise"], "jupyter": {"source_hidden": True}}
    notebook = {
        "cells": [
            cell("markdown", INTRO, "0"), cell("code", setup, "1", metadata),
            cell("markdown", DISTRICT_TEXT, "district-step"), cell("code", DISTRICT_CODE, "district-code"),
            cell("markdown", DICTIONARY_TEXT, "dictionary-step"), cell("code", DICTIONARY_CODE, "dictionary-code"),
            cell("markdown", EVENTS_TEXT, "events-step"), cell("code", EVENTS_CODE, "events-code"),
            cell("markdown", FLATTEN_TEXT, "flatten-step"), cell("code", FLATTEN_CODE, "flatten-code"),
            cell("markdown", missingness_lesson, "missingness-step"), cell("code", PLOT_CODE, "missingness-code"),
            cell("markdown", SUMMARY_TEXT, "summary-step"), cell("code", SUMMARY_CODE, "summary-code"),
            cell("markdown", "## 6. Submit and interpret\n\nRun the next cell to display **Submit**. This checks the guided run for Kambia District. You can return to a step, rerun the later steps, and submit again.", "submit-step"),
            cell("code", SUBMIT_CODE, "submit", metadata),
            cell("markdown", "## What would you tell the district team?\n\nRun the next cell for reflection fields and select **Record** to keep your notes in this browser. These reflections are unscored.", "reflection-step"),
            cell("code", reflection_code("exercise:u03-n07", ["What does the summary tell Laila, and what can it not establish about the outbreak?", "How could using an event date in place of missing rash onset affect an epidemic curve? What would you verify with the district team?"]), "reflection-fields", metadata),
            cell("markdown", REFERENCES, "continue"),
        ],
        "metadata": {"kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"}, "language_info": {"name": "python"}, "al": {"activity": EX + "act-dhis2-query", "language": "python", "generatedBy": "scripts/make_dhis2_pilot.py"}, "title": "Get a district measles summary, one step at a time (Python)"},
        "nbformat": 4, "nbformat_minor": 5,
    }
    path = OUT / "exercises/python/u03-n07-dhis2-query.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    answer = expected()
    check = f'''import json as _al_json
def _al_check():
    g = globals()
    required = ("org_unit", "events", "onset_element", "n_cases", "n_missing_onset", "first_onset", "last_onset")
    if any(g.get(name) is None for name in required):
        return "incomplete"
    try:
        if g["org_unit"] != {KAMBIA!r} or g["onset_element"] != {ONSET!r}:
            return "incorrect"
        if not isinstance(g["events"], list) or sorted(e["event"] for e in g["events"]) != {sorted(answer['ids'])!r}:
            return "incorrect"
        if int(g["n_cases"]) != {answer['n_cases']} or int(g["n_missing_onset"]) != {answer['n_missing_onset']}:
            return "incorrect"
        if str(g["first_onset"]) != {answer['first_onset']!r} or str(g["last_onset"]) != {answer['last_onset']!r}:
            return "incorrect"
    except (KeyError, TypeError, ValueError):
        return "incorrect"
    return "correct"
print("AL_OBSERVATION " + _al_json.dumps({{"outcome": _al_check()}}))
del _al_check
'''
    checks = ROOT / "app-assets/adaptive-learning/checks"
    checks.mkdir(parents=True, exist_ok=True)
    (checks / "dhis2-query.py").write_text(check, encoding="utf-8")
    print("wrote Python DHIS2 adapter pilot and check")


if __name__ == "__main__":
    main()
