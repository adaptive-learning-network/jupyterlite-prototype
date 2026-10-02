#!/usr/bin/env python3
"""Generate the Python and R exercise notebooks and their checks from one spec.

Each activity in the al: catalog gets one notebook per Jupyter kernel language.
The exercise cell carries `al` metadata (activity IRI, observed-object IRI,
check path, facilitation-ladder hints). After the learner runs it, the
extension executes checks/<name>.<ext> in the same Jupyter kernel; the check
prints one line, `AL_OBSERVATION {"outcome": "correct|incorrect|incomplete"}`.

Checks contain expected values. They run in the learner's own Jupyter kernel,
so results are formative: the catalog caps this evidence at the simulation stage.

Usage: python scripts/make_exercises.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
EX = "https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#"

KERNELSPEC = {
    "python": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
    "r": {"name": "xr", "display_name": "R (xeus-r)", "language": "R"},
}
LANGUAGE_INFO = {"python": {"name": "python"}, "r": {"name": "R"}}

SETUP = {
    "python": (
        "# Synthetic picnic outbreak: 60 attendees.\n"
        "# ate_salad = 1 if the person ate potato salad; ill = 1 if they became ill.\n"
        "ate_salad = [1] * 40 + [0] * 20\n"
        "ill = [1] * 30 + [0] * 10 + [1] * 5 + [0] * 15\n"
        "print(len(ate_salad), 'attendees')"
    ),
    "r": (
        "# Synthetic picnic outbreak: 60 attendees.\n"
        "# ate_salad = 1 if the person ate potato salad; ill = 1 if they became ill.\n"
        "ate_salad <- c(rep(1, 40), rep(0, 20))\n"
        "ill <- c(rep(1, 30), rep(0, 10), rep(1, 5), rep(0, 15))\n"
        "cat(length(ate_salad), 'attendees\\n')"
    ),
}

# variables: name -> (kind, expected). kind "count" | "rate" | "choice".
EXERCISES = [
    {
        "file": "01-frequency", "check": "frequency", "activity": "act-frequency",
        "title": "Count cases by exposure",
        "task": "How many people who **ate potato salad** became **ill**? Store the count in `ill_exposed`.",
        "variables": {"ill_exposed": ("count", 30)},
        "hints": [
            "You need people for whom both `ate_salad` and `ill` equal 1.",
            "Pair the two lists element by element and count the pairs where both values are 1.",
            "Python: `sum(a == 1 and i == 1 for a, i in zip(ate_salad, ill))`; R: `sum(ate_salad == 1 & ill == 1)`.",
        ],
    },
    {
        "file": "02-attack-rate", "check": "attack-rate", "activity": "act-attack-rate",
        "title": "Calculate attack rates",
        "task": "Calculate the attack rate (proportion ill) among those who ate potato salad (`ar_exposed`) and among those who did not (`ar_unexposed`).",
        "variables": {"ar_exposed": ("rate", 0.75), "ar_unexposed": ("rate", 0.25)},
        "hints": [
            "An attack rate is: ill people in a group ÷ all people in that group.",
            "Count the ill and the total separately for `ate_salad == 1` and for `ate_salad == 0`.",
            "Exposed: 30 ill of 40; unexposed: 5 ill of 20.",
        ],
    },
    {
        "file": "03-risk-ratio", "check": "risk-ratio", "activity": "act-risk-ratio",
        "title": "Calculate a risk ratio",
        "task": "Calculate the risk ratio of illness comparing those who ate potato salad with those who did not. Store it in `risk_ratio`.",
        "variables": {"risk_ratio": ("rate", 3.0)},
        "hints": [
            "A risk ratio compares two attack rates.",
            "Divide the attack rate in the exposed group by the attack rate in the unexposed group.",
            "0.75 ÷ 0.25.",
        ],
    },
    {
        "file": "04-interpret-risk-ratio", "check": "interpret-risk-ratio", "activity": "act-interpret-rr",
        "title": "Interpret a risk ratio",
        "task": (
            "The risk ratio is 3.0. Which statement is correct? Store the letter in `answer`.\n\n"
            "- **a**: Eating potato salad caused every illness.\n"
            "- **b**: People who ate potato salad were three times as likely to become ill as people who did not.\n"
            "- **c**: The potato salad contained three times more bacteria than other foods.\n"
            "- **d**: The risk of illness was 3%."
        ),
        "variables": {"answer": ("choice", "b")},
        "hints": [
            "A risk ratio compares the risk in two groups; it is not itself a risk.",
            "An association does not show that one food caused every case.",
            "Look for the statement that compares how likely illness was between the two groups.",
        ],
    },
]


def python_check(variables: dict) -> str:
    lines = [
        "import json as _al_json",
        "def _al_check():",
        "    g = globals()",
    ]
    for name, (kind, expected) in variables.items():
        lines += [f"    if g.get({name!r}) is None:", "        return 'incomplete'"]
        if kind == "count":
            test = f"int(g[{name!r}]) == {expected}"
        elif kind == "rate":
            test = f"abs(float(g[{name!r}]) - {expected}) < 1e-6"
        else:
            test = f"str(g[{name!r}]).strip().lower() == {expected!r}"
        lines += ["    try:", f"        if not ({test}):", "            return 'incorrect'",
                  "    except (TypeError, ValueError):", "        return 'incorrect'"]
    lines += ["    return 'correct'",
              "print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))",
              "del _al_check"]
    return "\n".join(lines) + "\n"


def r_check(variables: dict) -> str:
    lines = ["local({", "  outcome <- tryCatch({", "    result <- \"correct\""]
    for name, (kind, expected) in variables.items():
        if kind == "count":
            test = f"isTRUE(as.numeric({name}) == {expected})"
        elif kind == "rate":
            test = f"isTRUE(abs(as.numeric({name}) - {expected}) < 1e-6)"
        else:
            test = f"isTRUE(tolower(trimws(as.character({name}))) == \"{expected}\")"
        lines += [
            f"    if (!exists(\"{name}\", envir = globalenv()) || is.null(get(\"{name}\", envir = globalenv()))) {{",
            "      result <- \"incomplete\"",
            f"    }} else if (result == \"correct\" && !{test}) {{",
            "      result <- \"incorrect\"",
            "    }",
        ]
    lines += ["    result", "  }, error = function(e) \"incorrect\")",
              "  cat(paste0(\"AL_OBSERVATION {\\\"outcome\\\":\\\"\", outcome, \"\\\"}\\n\"))", "})"]
    return "\n".join(lines) + "\n"


def placeholder(language: str, variables: dict) -> str:
    if language == "python":
        return "\n".join(f"{name} = None  # replace None with your answer" for name in variables) + "\n"
    return "\n".join(f"{name} <- NULL  # replace NULL with your answer" for name in variables) + "\n"


def cell(cell_type: str, source: str, cell_id: str, metadata: dict | None = None) -> dict:
    c = {"cell_type": cell_type, "id": cell_id, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        c.update({"execution_count": None, "outputs": []})
    return c


def notebook(ex: dict, language: str) -> dict:
    name = "Python" if language == "python" else "R"
    intro = (
        f"# {ex['title']}\n\n"
        f"{ex['task']}\n\n"
        "Run the setup cell, then edit and run the exercise cell. The **Learning** panel records the "
        "result and suggests what to do next. Hints are available there; using more than two lowers "
        "how much this attempt counts as evidence."
    )
    al_meta = {
        "activity": EX + ex["activity"],
        "object": f"{EX}{ex['activity']}-exercise",
        "check": f"checks/{ex['check']}",
        "hints": ex["hints"],
    }
    return {
        "cells": [
            cell("markdown", intro, "0"),
            cell("code", SETUP[language], "1"),
            cell("code", placeholder(language, ex["variables"]), "2", {"al": al_meta, "tags": ["al-exercise"]}),
        ],
        "metadata": {
            "kernelspec": KERNELSPEC[language],
            "language_info": LANGUAGE_INFO[language],
            "al": {"activity": EX + ex["activity"], "language": language, "generatedBy": "scripts/make_exercises.py"},
            "title": f"{ex['title']} ({name})",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    for language, folder in (("python", "python"), ("r", "r")):
        out = CONTENT / "exercises" / folder
        out.mkdir(parents=True, exist_ok=True)
        for ex in EXERCISES:
            (out / f"{ex['file']}.ipynb").write_text(json.dumps(notebook(ex, language), indent=1, ensure_ascii=False) + "\n")
    checks = CONTENT / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    for ex in EXERCISES:
        (checks / f"{ex['check']}.py").write_text(python_check(ex["variables"]))
        (checks / f"{ex['check']}.R").write_text(r_check(ex["variables"]))
    print(f"wrote {len(EXERCISES) * 2} notebooks and {len(EXERCISES) * 2} checks")


if __name__ == "__main__":
    main()
