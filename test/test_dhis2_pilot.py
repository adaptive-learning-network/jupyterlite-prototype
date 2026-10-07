"""Native checks for the generated, Python-only DHIS2 adapter pilot."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "content/exercises/python/07-dhis2-query.ipynb"
CHECK = ROOT / "content/checks/dhis2-query.py"


class PilotTests(unittest.TestCase):
    def setUp(self) -> None:
        notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        self.assertEqual([cell["id"] for cell in notebook["cells"]], ["0", "1", "2", "3"])
        self.assertEqual(notebook["cells"][2]["metadata"]["al"]["check"], "checks/dhis2-query")
        self.ns: dict = {}
        exec("".join(notebook["cells"][1]["source"]), self.ns)

    def outcome(self) -> str:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(CHECK.read_text(encoding="utf-8"), self.ns)
        line = next(line for line in buffer.getvalue().splitlines() if line.startswith("AL_OBSERVATION "))
        return json.loads(line.removeprefix("AL_OBSERVATION "))["outcome"]

    def test_query_scope_and_copy(self) -> None:
        api = self.ns["api"]
        kambia = api.get("/api/tracker/events", {"program": "P_MEASLES", "orgUnit": "OU_KAMBIA"})["events"]
        other = api.get("/api/tracker/events", {"program": "P_MEASLES", "orgUnit": "OU_PORT_LOKO"})["events"]
        self.assertTrue(kambia and other)
        self.assertTrue(all(e["orgUnit"] == "OU_KAMBIA" for e in kambia))
        self.assertTrue(all(e["orgUnit"] == "OU_PORT_LOKO" for e in other))
        kambia[0]["dataValues"].clear()
        self.assertTrue(api.get("/api/tracker/events", {"program": "P_MEASLES", "orgUnit": "OU_KAMBIA"})["events"][0]["dataValues"])
        with self.assertRaises(ValueError):
            api.get("/api/tracker/events", {"program": "P_MEASLES"})
        with self.assertRaises(ValueError):
            api.get("/api/patients")

    def test_check_outcomes(self) -> None:
        for name in ("org_unit", "events", "onset_element", "n_cases", "n_missing_onset", "first_onset", "last_onset"):
            self.ns[name] = None
        self.assertEqual(self.outcome(), "incomplete")

        api = self.ns["api"]
        self.ns["org_unit"] = next(u["id"] for u in api.get("/api/organisationUnits")["organisationUnits"] if u["displayName"] == "Kambia District")
        self.ns["onset_element"] = next(d["id"] for d in api.get("/api/dataElements")["dataElements"] if d["displayName"] == "Date of rash onset")
        events = api.get("/api/tracker/events", {"program": "P_MEASLES", "orgUnit": self.ns["org_unit"]})["events"]
        self.ns["events"] = events
        dates = [v["value"] for e in events for v in e["dataValues"] if v["dataElement"] == self.ns["onset_element"]]
        self.ns["n_cases"] = len(events)
        self.ns["n_missing_onset"] = sum(not date for date in dates)
        self.ns["first_onset"] = min(date for date in dates if date)
        self.ns["last_onset"] = max(date for date in dates if date)
        self.assertEqual(self.outcome(), "correct")
        self.ns["n_missing_onset"] = 0
        self.assertEqual(self.outcome(), "incorrect")


if __name__ == "__main__":
    unittest.main()
