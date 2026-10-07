#!/usr/bin/env python3
"""Parity test: Python and R checks return the same outcome for the same answers.

Runs every check natively (CPython and Rscript) for correct, incorrect, and
untouched (placeholder) answers. Requires Rscript on PATH.

Usage: python scripts/test_checks.py
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
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


def run_r(code: str) -> str:
    result = subprocess.run(["Rscript", "-e", code], capture_output=True, text=True, check=True)
    return outcome(result.stdout)


def main() -> int:
    if not shutil.which("Rscript"):
        print("Rscript not found", file=sys.stderr)
        return 2
    failures = 0
    expected = {"correct": "correct", "incorrect": "incorrect", "placeholder": "incomplete"}
    for ex in EXERCISES:
        for mode, want in expected.items():
            got = {}
            for language, ext, runner in (("python", "py", run_python), ("r", "R", run_r)):
                check = (ROOT / "content/checks" / f"{ex['check']}.{ext}").read_text()
                got[language] = runner(ex["setup"][language] + "\n" + answers(language, ex["variables"], mode) + check)
            ok = got["python"] == got["r"] == want
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'}  {ex['check']:<22} {mode:<12} python={got['python']:<10} r={got['r']}")
    print("PASSED" if not failures else f"FAILED ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
