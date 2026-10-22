#!/usr/bin/env python3
"""Verify Python checks for correct, incorrect, and unanswered inputs."""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_exercises import EXERCISES, placeholder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def literal(language: str, value) -> str:
    if isinstance(value, list):
        inner = ", ".join(json.dumps(v) for v in value)
        return f"[{inner}]" if language == "python" else f"c({inner})"
    if isinstance(value, str):
        return json.dumps(value)
    return repr(value)


WRONG = {"choice": "z", "set": ["a"], "date": "1999-01-01"}


def answers(language: str, variables: dict, mode: str) -> str:
    if mode == "placeholder":
        return placeholder(language, variables)
    op = "=" if language == "python" else "<-"
    lines = []
    for name, (kind, expected) in variables.items():
        if mode == "correct":
            value = expected
        elif kind in WRONG:
            value = WRONG[kind]
        else:
            value = expected + 1  # count and rate
        lines.append(f"{name} {op} {literal(language, value)}")
    return "\n".join(lines) + "\n"


def outcome(output: str) -> str:
    line = next(l for l in output.splitlines() if l.startswith("AL_OBSERVATION "))
    return json.loads(line[len("AL_OBSERVATION "):])["outcome"]


def run_python(code: str) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(code, {})
    return outcome(buffer.getvalue())



def main() -> int:
    failures = 0
    expected = {"correct": "correct", "incorrect": "incorrect", "placeholder": "incomplete"}
    for ex in EXERCISES:
        for mode, want in expected.items():
            got = {}
            for language, ext, runner in (("python", "py", run_python),):
                check = (ROOT / "app-assets/adaptive-learning/checks" / f"{ex['check']}.{ext}").read_text(encoding="utf-8")
                got[language] = runner(ex["setup"][language] + "\n" + answers(language, ex["variables"], mode) + check)
            ok = got["python"] == want
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'}  {ex['check']:<22} {mode:<12} python={got['python']:<10}")
    from make_unit01_pilot import REPORTS, expected as unit01_expected
    district, increase = unit01_expected()
    check = (ROOT / "app-assets/adaptive-learning/checks/u01-data-to-decision.py").read_text(encoding="utf-8")
    cases = {
        "placeholder": ("priority_district = None\nincrease = None\nrecommended_step = None\n", "incomplete"),
        "wrong_district": (f"priority_district = 'Bombali'\nincrease = {increase}\nrecommended_step = 'verify_reports_and_investigate'\n", "incorrect"),
        "wrong_action": (f"priority_district = {district!r}\nincrease = {increase}\nrecommended_step = 'declare_confirmed_outbreak'\n", "incorrect"),
        "correct": (f"priority_district = {district!r}\nincrease = {increase}\nrecommended_step = 'verify_reports_and_investigate'\n", "correct"),
    }
    for mode, (answer, want) in cases.items():
        got = run_python(f"reports = {REPORTS!r}\n" + answer + check)
        ok = got == want
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  u01-data-to-decision {mode:<15} python={got}")
    from make_unit02_pilot import CASE_ROUTE, LAB_ROUTE
    check = (ROOT / "app-assets/adaptive-learning/checks/u02-system-map.py").read_text(encoding="utf-8")
    system_cases = {
        "untouched": (None, "incomplete"),
        "partial": ({"case": list(CASE_ROUTE), "lab": list(LAB_ROUTE), "case_moves": 1, "lab_moves": 0}, "incomplete"),
        "wrong_route": ({"case": list(reversed(CASE_ROUTE)), "lab": list(LAB_ROUTE), "case_moves": 2, "lab_moves": 2}, "incorrect"),
        "corrected": ({"case": list(CASE_ROUTE), "lab": list(LAB_ROUTE), "case_moves": 3, "lab_moves": 3}, "correct"),
    }
    for mode, (answer, want) in system_cases.items():
        got = run_python(f"reporting_pathways = {answer!r}\n" + check)
        ok = got == want
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  u02-system-map      {mode:<15} python={got}")
    print("PASSED" if not failures else f"FAILED ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
