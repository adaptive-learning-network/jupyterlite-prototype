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

INTRO = """# Explore case events through a DHIS2-shaped adapter

This is a **local course simulation**, not a DHIS2 server. It uses synthetic measles case events. The adapter answers three read-only requests in the Python Jupyter kernel; it makes no network requests or changes to a real health information system.

*Unit 3: Using Informatics to Get Information Faster.* Learning objective: **Use software to explore a dataset.**

The [UCSF course book's Unit 2.1 Assignment 2](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_2.ipynb) asks: “How big is this dataset?”, “What timeframe does the dataset span?”, and “What locations does the dataset include?” [Assignment 3](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_3.ipynb) adds: “Describe the variables in your dataset.” Those are the questions this exercise preserves.

In the course assignment, the network is down and the district data manager supplies an Excel backup and DHIS2 data dictionary. This pilot provides a synthetic, local API-shaped copy of case events and dictionary entries so you can practice the same inspection questions inside JupyterLite. It does not simulate an online DHIS2 connection.

## Your task

1. Use `api.get` to find the ID of **Kambia District** in `/api/organisationUnits`.
2. Query `/api/tracker/events` with `program="P_MEASLES"` and that `orgUnit` ID. Store the returned list in `events`.
3. Use `/api/dataElements` to find the ID for **Date of rash onset**. Store it in `onset_element`.
4. From the returned events, compute `n_cases`, `n_missing_onset`, `first_onset`, and `last_onset`. For the date range, use nonblank onset dates, as `YYYY-MM-DD` strings.

Run the setup cell, then edit and run the exercise cell. The **Learning** panel checks your result. The one missing onset date is a data-quality signal; do not silently replace it with the event date.
"""

REFERENCES = """## References

- [UCSF FETP JupyterBook: Unit 2.1 case study, Assignment 2](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_2.ipynb): dataset size, timeframe, locations, and population.
- [UCSF FETP JupyterBook: Unit 2.1 case study, Assignment 3](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_3.ipynb): use the data dictionary to understand variables.
- [FETP Unit 3 instructor guide](https://docs.google.com/document/d/1B6qrW7QBcL4uCO85QPIN8pJ--37S8N6j3xkT87qBACA).
- [FETP Unit 3 slides](https://docs.google.com/presentation/d/1EXkFCxffubjhpM94373WiJ0a9_V0Tsfn): dataset exploration, slides 56–57.
- [FETP Unit 3 knowledge check](https://forms.gle/Y4yG5gMbFznczrBd9).
- [DHIS2 Tracker API reference](https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-241/tracker.html): event query shape. This pilot implements only the documented subset stated above.

*The case events and IDs in this notebook are synthetic.*
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
    setup = "import json\nFIXTURE = json.loads(" + repr(json.dumps(FIXTURE, separators=(",", ":"))) + ")\n" + ADAPTER
    exercise = """# Use the adapter and its data dictionary. Replace each None.
org_unit = None
events = None
onset_element = None
n_cases = None
n_missing_onset = None
first_onset = None
last_onset = None
"""
    metadata = {"al": {"activity": EX + "act-dhis2-query", "object": EX + "act-dhis2-query-exercise", "check": "checks/dhis2-query", "hints": ["Read the two metadata lists first; use displayName to select their IDs.", "The event query needs both program and orgUnit. Each event's dataValues list holds dataElement/value pairs.", "Build a list of onset values from the matching data element; count blanks separately, then use min and max on the nonblank dates."]}, "tags": ["al-exercise"]}
    notebook = {
        "cells": [cell("markdown", INTRO, "0"), cell("code", setup, "1"), cell("code", exercise, "2", metadata), cell("markdown", REFERENCES, "3")],
        "metadata": {"kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"}, "language_info": {"name": "python"}, "al": {"activity": EX + "act-dhis2-query", "language": "python", "generatedBy": "scripts/make_dhis2_pilot.py"}, "title": "Explore case events through a DHIS2-shaped adapter (Python)"},
        "nbformat": 4, "nbformat_minor": 5,
    }
    path = OUT / "exercises/python/07-dhis2-query.ipynb"
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
    (OUT / "checks/dhis2-query.py").write_text(check, encoding="utf-8")
    print("wrote Python DHIS2 adapter pilot and check")


if __name__ == "__main__":
    main()
