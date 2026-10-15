#!/usr/bin/env python3
"""Five Python computational narratives; source, fixtures, checks and controls.

Course mapping and known source gaps: docs/design/units04-08.md.
"""
from __future__ import annotations

import inspect
import hashlib
import json
import textwrap
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path

from notebook_images import embed_images
from reflection_widgets import reflection_code

ROOT = Path(__file__).resolve().parent.parent
EX = "https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#"

# Entirely invented records. Stable IDs carry the case across all five tasks.
DATA = {
    "sources": [
        {"id": "case", "grain": "case", "fields": ["case_id", "district", "onset_date", "age"], "access": "district analyst"},
        {"id": "lab", "grain": "case", "fields": ["case_id", "specimen_date", "result"], "access": "authorized laboratory extract"},
        {"id": "weekly", "grain": "district-week", "fields": ["district", "week", "count"], "access": "public summary"},
    ],
    "required_fields": ["case_id", "district", "onset_date", "result"],
    "cases": [
        {"case_id": "C01", "district": "Kambia", "onset_date": "2021-10-18", "age": 8, "contact_label": "Training contact A"},
        {"case_id": "C02", "district": "Kambia", "onset_date": "2021-10-19", "age": 12, "contact_label": "Training contact B"},
        {"case_id": "C03", "district": "Kambia", "onset_date": "2021-10-20", "age": 4, "contact_label": "Training contact C"},
        {"case_id": "C04", "district": "Port Loko", "onset_date": "2021-10-20", "age": 17, "contact_label": "Training contact D"},
    ],
    "lab": [{"case_id": "C01", "specimen_date": "2021-10-21", "result": "positive"},
            {"case_id": "C02", "specimen_date": "2021-10-22", "result": "pending"}],
    "role_fields": ["case_id", "district", "onset_date", "age"],
    "task_fields": ["case_id", "district", "onset_date"],
    "release_minimum": 3,
    "form": {"required": ["case_id", "district", "age"], "age_min": 0, "age_max": 120,
             "districts": ["Kambia", "Port Loko"]},
    "submissions": [
        {"case_id": "T01", "district": "Kambia", "age": 8},
        {"case_id": "", "district": "Kambia", "age": 8},
        {"case_id": "T03", "district": "Kambia", "age": 180},
        {"case_id": "T04", "district": "Other", "age": 8},
        {"case_id": "T05", "district": "", "age": 8},
        {"case_id": "T06", "district": "Kambia", "age": None},
    ],
    "dirty": [
        {"case_id": "Q01", "district": "Kambia", "age": 8, "onset_date": "2021-10-18", "report_date": "2021-10-19"},
        {"case_id": "Q01", "district": "Kambia", "age": 8, "onset_date": "2021-10-18", "report_date": "2021-10-19"},
        {"case_id": "Q02", "district": "", "age": 12, "onset_date": "2021-10-19", "report_date": "2021-10-20"},
        {"case_id": "Q03", "district": "Port Loko", "age": 180, "onset_date": "2021-10-20", "report_date": "2021-10-21"},
        {"case_id": "Q04", "district": "Kambia", "age": 4, "onset_date": "2021-10-18", "report_date": "2021-10-25"},
    ],
    "timely_days": 2,
    "verified_corrections": [
        {"case_id": "Q02", "field": "district", "value": "Port Loko", "evidence": "Training register review: district confirmed"},
        {"case_id": "Q03", "field": "age", "value": 18, "evidence": "Training register review: age confirmed as 18 years"},
    ],
    "verified_duplicate": {"case_id": "Q01", "evidence": "Training source review: these identical rows are the same report"},
}


def expected_answers(unit, data):
    """Recompute training expectations from source coverage and explicit rules."""
    if unit == 4:
        # Each selected source must add a required field; the aggregate lacks case IDs.
        required = set(data["required_fields"])
        selected = [s["id"] for s in data["sources"] if s["grain"] == "case" and required & set(s["fields"])]
        return {"sources": selected, "grain": "case"}
    if unit == 5:
        counts = Counter(row["district"] for row in data["cases"])
        return {"fields": sorted(set(data["task_fields"]) & set(data["role_fields"])),
                "suppress": sorted(k for k, v in counts.items() if v < data["release_minimum"])}
    if unit == 6:
        total = len(data["cases"])
        positive = sum(row["result"] == "positive" for row in data["lab"])
        # Claims 1 and 2 are numeric, claim 3 asserts causation without supporting evidence.
        claimed = {"all_positive": positive == total, "no_followup": all(row["result"] != "pending" for row in data["lab"])
                   and len(data["lab"]) == total, "water_caused": False}
        return {"claims": sorted(k for k, supported in claimed.items() if not supported), "review": "human_review"}
    if unit == 7:
        return {"required": data["form"]["required"], "age_max": data["form"]["age_max"],
                "district_control": "list"}
    if unit == 8:
        rows = data["dirty"]
        ids = Counter(row["case_id"] for row in rows)
        return {"missing": sum(not row["district"] for row in rows),
                "duplicates": sum(v - 1 for v in ids.values()),
                "invalid": sum(not data["form"]["age_min"] <= row["age"] <= data["form"]["age_max"] for row in rows),
                "late": sum((date.fromisoformat(row["report_date"]) - date.fromisoformat(row["onset_date"])).days > data["timely_days"] for row in rows),
                "repair": "verify_and_log"}
    raise ValueError(unit)


def evaluate_answer(unit, response, data):
    expected = expected_answers(unit, data)
    if not isinstance(response, dict) or any(response.get(k) is None or response.get(k) == [] for k in expected):
        return "incomplete"
    for key, value in expected.items():
        actual = response.get(key)
        if isinstance(value, list):
            if not isinstance(actual, (list, tuple)) or sorted(actual) != sorted(value):
                return "incorrect"
        elif actual != value:
            return "incorrect"
    return "correct"


# Compact per-notebook control specifications. Dropdown placeholders are not radio options.
UNITS = [
    dict(unit=4, slug="source-inventory", title="Find the data Laila needs",
         objective="Compare case, laboratory, and aggregate data sources.",
         capability="Compare data sources for an investigation", prerequisite="case-vs-aggregate",
         cue=[("Laila", "My case file has no laboratory result."), ("Supervisor", "Which source has the missing field?"), ("Laila", "I will check the grain and identifiers first.")],
         slide=37,
         lesson="""## A question before an extraction

Laila needs a district summary of suspected measles cases and their laboratory status.
The course describes the problem: **the variables and data she needs are stored in different databases—or not available at all**.
Existing HIS applications may collect data epidemiologists need; reuse starts with a question about fitness for purpose.

**One row represents the grain of a source.** A case register has a row per case;
a laboratory extract can connect results through `case_id`. A district-week total
cannot tell you which case has a result. A missing laboratory row means **unknown**,
not a negative result. Access permission must be checked before extraction.

Run the next cell to inspect a local source catalogue. Select the smallest set
that supplies `case_id`, `district`, `onset_date`, and `result` at case level.
Hold **Ctrl** (or **Command**) to select more than one source. Then run **Check my work**.
""",
         controls=[("sources", "Sources", "multi", [("Case register", "case"), ("Laboratory extract", "lab"), ("Weekly aggregate", "weekly")]),
                   ("grain", "Required grain", "choice", [("One case", "case"), ("One district-week", "district-week")])],
         reflection=["What permission and data-dictionary questions would you resolve before using these sources?", "How would unmatched laboratory results affect Laila's report?"],
         hints=["Start from the required fields and the meaning of one row, rather than the software name.", "A case ID can connect a case register and a laboratory extract. A weekly total cannot replace a missing individual result.", "Compare the fields of the two case-level sources with the required field list; retain the case grain."],
         references="UCSF FETP, Assessing HIS Software Applications; FETP Version 2 Unit 2, slides 29–37."),
    dict(unit=5, slug="access-and-safe-release", title="Give access without releasing too much",
         objective="Evaluate role-specific access and disclosure risks.",
         capability="Evaluate access and safe release", prerequisite="u04-source-inventory",
         cue=[("Supervisor", "The analyst needs a trend file, not contacts."), ("Laila", "I will limit the extract to the task."), ("Supervisor", "And check the small public counts.")],
         slide=None,
         lesson="""## Two audiences, two decisions

The course asks: **What features and measures will keep data secure during data
collection, storage, and analysis? How will access to the database and server be managed?**
Data security protects against unauthorized access, modification, and disclosure.
Confidentiality protects the secrecy of health data; privacy concerns individuals'
control of their personal health information. Access control is one measure, alongside
secure transmission, backups, and keeping credentials private.

Laila prepares an internal case-level trend extract for a district analyst. The
task needs only `case_id`, `district`, and `onset_date`. The analyst's training role
permits those fields and `age`, but permission alone does not make age necessary.
Select only the fields needed for this task. Contact labels must stay out.

For a **separate public summary**, this exercise's rule releases district counts
of **3 or more** and withholds smaller counts. This is a training rule, not a national disclosure standard.
Removing names alone does not remove disclosure risk; repeated releases and totals
can reveal suppressed values. Do not publish totals or complementary breakdowns here.
Run the next cell, choose the internal fields and the district to suppress, and check the resulting extracts.
""",
         controls=[("fields", "Internal extract fields", "multi", [(x, x) for x in ["case_id", "district", "onset_date", "age", "contact_label"]]),
                   ("suppress", "Withhold public counts for", "multi", [(x, x) for x in ["Kambia", "Port Loko"]])],
         reflection=["Which security features and additional working practices would you require for the internal extract?", "What would you check before releasing other tables that overlap this public summary?"],
         hints=["Separate access permission from the information needed for this specific task.", "The trend task uses an identifier, district, and onset date. Compare district counts with the stated threshold.", "Exclude both contact labels and unnecessary age. Withhold the district whose count is below three."],
         references="UCSF FETP, Unit 3 Assignment 3; FETP Version 2 Unit 3, slides 53–61 and 68."),
    dict(unit=6, slug="ai-use-and-review", title="Review an AI-assisted draft before acting",
         objective="Evaluate an AI-assisted draft against surveillance evidence.",
         capability="Evaluate an AI-assisted draft", prerequisite="u05-access-and-safe-release",
         cue=[("Laila", "This draft sounds certain."), ("Supervisor", "Do the records support its claims?"), ("Laila", "I will check each claim before sharing it.")],
         slide=26,
         lesson="""## Confidence in wording is not evidence

The course's data → information → knowledge → wisdom pathway connects a result
to context and a defensible action. A fluent draft still needs that pathway.
Use an AI-assisted tool to help draft or organize text only when the task and data
are appropriate; retain human responsibility for checking the evidence and release.

Laila receives this **practice draft**:

1. **All reported cases are laboratory-positive.**
2. **No laboratory follow-up is needed.**
3. **Contaminated water caused this cluster.**

The local records below include pending results and cases without a laboratory match.
A missing result is not a negative result, and these descriptive data do not establish
a cause. Even a numerically correct statement may need contextual review.

Run the next cell to compute the evidence summary. Mark **every unsupported claim**
and choose what should happen before the draft is shared. The supplied draft is the
object of review; you do not need an AI account or to submit any records to a service.
""",
         controls=[("claims", "Unsupported claims", "multi", [("All cases laboratory-positive", "all_positive"), ("No follow-up needed", "no_followup"), ("Water caused the cluster", "water_caused")]),
                   ("review", "Before sharing", "choice", [("Human evidence and disclosure review", "human_review"), ("Share the draft automatically", "auto_release")])],
         reflection=["Rewrite one unsupported claim using only the available evidence and its limitations.", "What data and release conditions would you check before using an AI-assisted tool for this task?"],
         hints=["Compare each sentence with a computed count or with the evidence needed to establish causation.", "Count positive results, pending results, and cases without a matching laboratory record separately.", "All three statements go beyond these records. Human review must precede release."],
         references="FETP Version 2 Unit 1, slides 26–27 (information value); Unit 7, interpretation and information bias. AI review is an authored practice scenario."),
    dict(unit=7, slug="form-design-validation", title="Design a form and test its rules",
         objective="Design a case form with validation rules.",
         capability="Design and test case-form validation", prerequisite="u06-ai-use-and-review",
         cue=[("Martha", "The old form accepted almost anything."), ("Laila", "Let's define the fields and test errors."), ("Martha", "And keep a valid report easy to submit.")],
         slide=67,
         lesson="""## Prevent an error where it enters

Martha's course scenario describes an application that **requires completion of a
core set of data fields**, uses **drop-down lists** and date controls, and alerts
her to values outside the expected range. The data dictionary defines the meaning,
format, and allowed values; a control makes those standards easier to follow.

Design a small training form. Its dictionary requires `case_id`, `district`, and
`age`; `age` is completed years from **0 to 120** and district is **Kambia** or
**Port Loko**. Those ranges and required fields are this exercise's explicit rules.
An unexpected value needs verification, not an invented replacement.

Run the next cell. Choose the required fields, maximum age, and district control.
Then run **Check my work** to test the form against a valid submission, a missing
identifier, an out-of-range age, an unrecognized district, and missing district or age. Watch which records
are accepted. A form that rejects everything is not a successful form.

This is the same design question as the course's DHIS2 modification assignment:
which fields and rules need changing, and who should authorize and test the change?
""",
         controls=[("required", "Required fields", "multi", [(x, x) for x in ["case_id", "district", "age"]]),
                   ("age_max", "Maximum age", "integer", None),
                   ("district_control", "District control", "choice", [("Controlled district list", "list"), ("Unrestricted text", "free_text")])],
         reflection=["What modifications would your investigation form need, and who would authorize them?", "Which quality problems can this form prevent, and which still need review against the source?"],
         hints=["Use the dictionary to choose constraints, then test both valid and invalid submissions.", "A blank identifier, age 180, and district Other each violate a stated rule. The valid T01 record should pass.", "Require all three fields, use a controlled district list, and use the dictionary's upper age bound."],
         references="FETP Version 2 Unit 2, slides 65–67; Unit 3, slides 44–49; UCSF FETP Unit 4 Assignment 2."),
    dict(unit=8, slug="quality-audit-repair", title="Audit quality and plan defensible repairs",
         objective="Analyze completeness, validity, duplication, and timeliness.",
         capability="Audit data quality and preserve corrections", prerequisite="u07-form-design-validation",
         cue=[("Laila", "Two rows have the same identifier."), ("Martha", "Is it a repeat report or another event?"), ("Laila", "I will verify it and preserve the original.")],
         slide=68,
         lesson="""## Quality is a question about fitness for use

The course defines data quality through accuracy and completeness and asks:
**Do the data accurately reflect reality, so that the data serve the intended purpose?**
Validation can expose a problem; a valid value is not proof of accuracy.

Audit this incoming extract using its stated dictionary:

- **Completeness:** count rows with a missing district.
- **Uniqueness:** count extra rows beyond the first occurrence of each `case_id`.
- **Validity:** count ages outside 0–120 years.
- **Timeliness:** count reports more than **2 days** after onset, using this training rule.

Run the next cell to inspect the rows and the Python audit function. You may call
`audit_quality(training_data)` in your own code cell to inspect its report. Enter
your counts, choose a repair approach, and run **Check my work**.

For this training extract, the source review confirms Q02's district as **Port Loko**,
Q03's age as **18 years**, and the two identical Q01 rows as the **same report**.
The verified repair approach applies only those confirmations to a separate copy,
logs each original and replacement, and keeps the untouched incoming extract.
The late report remains late; correcting values cannot undo a reporting delay.

Do not replace a missing district with a guess, turn an impossible age into zero,
or silently delete a repeated ID. Check the source, retain the original values,
and log the reason and evidence for a correction. A repeated ID may represent a
repeat report or a separate event; the record grain determines the right action.
""",
         controls=[("missing", "Missing district rows", "integer", None), ("duplicates", "Extra duplicate-ID rows", "integer", None),
                   ("invalid", "Invalid age rows", "integer", None), ("late", "Late report rows", "integer", None),
                   ("repair", "Repair approach", "choice", [("Verify sources; preserve originals and log decisions", "verify_and_log"), ("Guess missing values and overwrite originals", "overwrite"), ("Delete every row with a repeated ID", "delete_all")])],
         reflection=["Which source checks would you request before resolving the repeated identifier?", "What would your correction log contain, and how would unresolved errors affect the district summary?"],
         hints=["Count each quality dimension separately. A row can have more than one problem.", "For duplicate IDs, count occurrences beyond the first; for timeliness, subtract onset from report date.", "Compare missing districts, duplicate excess, age bounds, and delay with the report. Verify and log changes rather than silently overwriting."],
         references="FETP Version 2 Unit 2, slides 60–68; UCSF FETP Unit 2.2 and Case Study Assignment 4."),
]


def show_table(rows):
    if not rows:
        display(widgets.HTML("<p>No rows selected.</p>"))
        return
    names = list(rows[0])
    header = "".join("<th>" + escape(str(name)) + "</th>" for name in names)
    body = "".join("<tr>" + "".join("<td>" + escape(str(row.get(name, ""))) + "</td>" for name in names) + "</tr>" for row in rows)
    display(widgets.HTML('<div style="overflow-x:auto"><table><thead><tr>' + header + '</tr></thead><tbody>' + body + '</tbody></table></div>'))


def audit_quality(data):
    rows = data["dirty"]
    ids = Counter(row["case_id"] for row in rows)
    return {"missing": sum(not row["district"] for row in rows),
            "duplicates": sum(count - 1 for count in ids.values()),
            "invalid": sum(not data["form"]["age_min"] <= row["age"] <= data["form"]["age_max"] for row in rows),
            "late": sum((date.fromisoformat(row["report_date"]) - date.fromisoformat(row["onset_date"])).days > data["timely_days"] for row in rows)}


def build_artifact(unit, response, data):
    """The learner's choices drive a real local transformation, including bad choices."""
    if unit == 4:
        selected = response["sources"]
        fields = set().union(*(set(s["fields"]) for s in data["sources"] if s["id"] in selected))
        print("Required fields not covered:", sorted(set(data["required_fields"]) - fields))
        if "case" in selected:
            lab = {row["case_id"]: row for row in data["lab"]} if "lab" in selected else {}
            return [{"case_id": row["case_id"], "district": row["district"], "onset_date": row["onset_date"],
                     "result": lab.get(row["case_id"], {}).get("result", "unknown")} for row in data["cases"]]
        return [{"district": key, "count": value} for key, value in Counter(row["district"] for row in data["cases"]).items()] if "weekly" in selected else []
    if unit == 5:
        allowed = set(response["fields"]) & set(data["role_fields"])
        denied = set(response["fields"]) - set(data["role_fields"])
        if denied:
            print("Role access denied for:", sorted(denied))
        internal = [{key: row[key] for key in response["fields"] if key in row and key in allowed} for row in data["cases"]] if allowed else []
        public = [{"district": key, "public_count": "withheld" if key in response["suppress"] else count}
                  for key, count in Counter(row["district"] for row in data["cases"]).items()]
        return {"Internal extract (invented records)": internal, "Public summary": public}
    if unit == 6:
        positive = sum(row["result"] == "positive" for row in data["lab"])
        pending = sum(row["result"] == "pending" for row in data["lab"])
        unmatched = len({row["case_id"] for row in data["cases"]} - {row["case_id"] for row in data["lab"]})
        return [{"measure": "Reported cases", "count": len(data["cases"])},
                {"measure": "Positive laboratory results", "count": positive},
                {"measure": "Pending laboratory results", "count": pending},
                {"measure": "Cases without a laboratory match", "count": unmatched}]
    if unit == 7:
        tested = []
        for i, row in enumerate(data["submissions"], 1):
            errors = [key + " required" for key in response["required"] if row.get(key) in (None, "")]
            age = row.get("age")
            if age not in (None, "") and (type(age) is not int or not data["form"]["age_min"] <= age <= response["age_max"]):
                errors.append("age must be whole years within range")
            if response["district_control"] == "list" and row.get("district") not in (None, "") and row["district"] not in data["form"]["districts"]:
                errors.append("district not recognized")
            tested.append({"submission": i, "accepted": not errors, "errors": "; ".join(errors)})
        return tested
    if unit == 8:
        actual = audit_quality(data)
        print("Computed audit:", actual)
        if response["repair"] != "verify_and_log":
            print("No changes applied: choose source verification with originals and a correction log.")
            return [dict(row) for row in data["dirty"]]
        cleaned, ledger, seen = [], [], {}
        for source in data["dirty"]:
            row = dict(source)
            if seen.get(row["case_id"]) == source and row["case_id"] == data["verified_duplicate"]["case_id"]:
                ledger.append({"case_id": row["case_id"], "field": "duplicate row", "before": dict(row),
                               "after": "earlier identical report retained", "evidence": data["verified_duplicate"]["evidence"]})
                continue
            seen[row["case_id"]] = dict(source)
            for change in data["verified_corrections"]:
                if change["case_id"] == row["case_id"]:
                    ledger.append({"case_id": row["case_id"], "field": change["field"], "before": row[change["field"]],
                                   "after": change["value"], "evidence": change["evidence"]})
                    row[change["field"]] = change["value"]
            cleaned.append(row)
        print("Audit after verified repairs:", audit_quality({**data, "dirty": cleaned}))
        return {"Verified correction log": ledger, "Cleaned copy": cleaned}
    return []


def comic(spec):
    """Local vector teaching art: three panels and fictional dialogue."""
    panels = []
    for i, (speaker, words) in enumerate(spec["cue"]):
        x = i * 200 if i < 2 else 0
        y = 0 if i < 2 else 202
        width = 188 if i < 2 else 388
        lines = textwrap.wrap(words, 19 if i < 2 else 43)
        text = "".join(f'<tspan x="{x + 20}" dy="19">{escape(line)}</tspan>' for line in lines)
        panels.append(f'''<g transform="translate(0,{y})"><rect x="{x+4}" y="4" width="{width}" height="194" rx="10" fill="#f4f8fc" stroke="#b6cadd"/>
<path d="M{x+18} 15H{x+width-10}V115H{x+108}l-25 20 3-20H{x+18}z" fill="white" stroke="#b6cadd"/>
<text font-family="sans-serif" font-size="16" y="23">{text}</text>
<circle cx="{x+47}" cy="151" r="14" fill="#915e46"/>
<path d="M{x+33} 149q-4-26 14-20q20-2 14 22q-6-15-28-2" fill="#332a30"/>
<path d="M{x+23} 193q0-27 24-27q25 0 25 27" fill="#287d8e"/>
<text x="{x+83}" y="178" font-family="sans-serif" font-size="15" fill="#163b58">{escape(speaker)}</text></g>''')
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 404" role="img"><title>Laila: ' + escape(spec["title"]) + '</title>' + "".join(panels) + '</svg>'
    name = f"laila-unit{spec['unit']:02d}-story.svg"
    artwork = ROOT / "artwork"
    artwork.mkdir(exist_ok=True)
    (artwork / name).write_text(svg, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(svg.encode("utf-8")).hexdigest()[:12]
    return name.replace(".svg", f"-{digest}.png")


def cell(kind, source, ident, metadata=None):
    result = {"cell_type": kind, "id": ident, "metadata": metadata or {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return embed_images(result)


def setup_code(spec, *, data=None, helpers=None, preview=None):
    imports = '''# Run once to inspect the data and display the controls.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from IPython.display import display
from html import escape
from collections import Counter
from datetime import date
display(widgets.HTML("""<style>
.course-task-control { height: auto !important; margin-bottom: 0.75rem; gap: 0.25rem; }
.course-task-control > label { width: auto !important; text-align: left; white-space: normal; line-height: 1.4; }
.course-task-control > select, .course-task-control > input { width: 100% !important; min-width: 0; max-width: 100%; flex: 0 0 auto !important; }
</style>"""))
'''
    code = imports + "\ntraining_data = " + repr(DATA if data is None else data) + "\n"
    for function in (helpers or [show_table, audit_quality, expected_answers, evaluate_answer, build_artifact]):
        code += "\n" + inspect.getsource(function) + "\n"
    unit = spec["unit"]
    code += f"unit{unit:02d}_response = None\ncontrols = {{}}\n"
    if any(control[2] == "multi" for control in spec["controls"]):
        code += "display(widgets.HTML('<p>For multiple choices, hold Ctrl (Command on Mac) while selecting items.</p>'))\n"
    if any(control[2] == "integer" for control in spec["controls"]):
        code += "display(widgets.HTML('<p>In numeric fields, enter a non-negative number; -1 means unanswered.</p>'))\n"
    if unit == 4:
        code += "show_table(training_data['sources'])\n"
    elif unit == 5:
        code += "print('Role permits:', training_data['role_fields'])\nprint('Task needs:', training_data['task_fields'])\nshow_table([{'district': k, 'count': v} for k, v in Counter(row['district'] for row in training_data['cases']).items()])\n"
    elif unit == 6:
        code += "show_table(build_artifact(6, {}, training_data))\n"
    elif unit == 7:
        code += "print('Training dictionary:', training_data['form'])\nshow_table(training_data['submissions'])\n"
    elif unit == 8:
        code += "show_table(training_data['dirty'])\n"
    if preview is not None:
        code += preview
    for key, label, kind, options in spec["controls"]:
        if kind == "multi":
            code += f"controls[{key!r}] = widgets.SelectMultiple(description={label!r}, options={options!r}, value=(), rows={len(options)}, style={{'description_width': 'initial'}}, layout=widgets.Layout(width='100%', flex_flow='column', align_items='stretch'))\n"
        elif kind == "integer":
            code += f"controls[{key!r}] = widgets.BoundedIntText(description={label!r}, value=-1, min=-1, max=999, style={{'description_width': 'initial'}}, layout=widgets.Layout(width='240px', flex_flow='column', align_items='stretch'))\n"
        else:
            code += f"controls[{key!r}] = widgets.Dropdown(description={label!r}, options={[('Select an answer', None), *options]!r}, value=None, style={{'description_width': 'initial'}}, layout=widgets.Layout(width='100%', flex_flow='column', align_items='stretch'))\n"
        code += f"controls[{key!r}].add_class('course-task-control')\ndisplay(controls[{key!r}])\n"
    return code


def exercise_code(spec):
    unit = spec["unit"]
    return f'''# Check my work: run after making your choices above. Revise and run again to retry.
unit{unit:02d}_response = {{key: (list(control.value) if isinstance(control, widgets.SelectMultiple)
                       else None if isinstance(control, widgets.BoundedIntText) and control.value < 0
                       else control.value) for key, control in controls.items()}}
result = evaluate_answer({unit}, unit{unit:02d}_response, training_data)
if result == "incomplete":
    print("Incomplete: answer every field, then check again.")
else:
    artifact = build_artifact({unit}, unit{unit:02d}_response, training_data)
    if isinstance(artifact, dict):
        for title, rows in artifact.items():
            print(title)
            show_table(rows)
    else:
        show_table(artifact)
    print("Correct: your result follows the stated evidence and training rules." if result == "correct"
          else "Not yet correct: compare the artifact with the task and rules. Revise your choices and retry; the Learning panel offers hints.")
'''


def main():
    # Prepare all vector sources before checking for their rendered PNGs.
    for spec in UNITS:
        name = comic(spec)
        if not (ROOT / "content/exercises/assets" / name).exists():
            # All five SVG sources are prepared below before an author rerenders.
            for remaining in UNITS:
                comic(remaining)
            raise SystemExit("Updated comic PNGs are needed. Run node scripts/render_course_comics.cjs, then rerun this generator.")
    for spec in UNITS:
        unit, slug = spec["unit"], spec["slug"]
        ident = f"u{unit:02d}-{slug}"
        filename = f"u{unit:02d}-n01-{slug}.ipynb"
        art = comic(spec)
        intro = f"**Unit {unit:02d} · Notebook 01**\n\n# {spec['title']}\n\n**Learning objective:** {spec['objective']}\n\n"
        intro += f"![Laila's next decision: {spec['title']}](../assets/{art})\n\n"
        intro += "All records in this exercise are invented. Follow Laila's question, inspect the evidence, and check your decision.\n\n" + spec["lesson"]
        if spec["slide"]:
            deck = 1 if unit == 6 else 2
            page = spec["slide"]
            intro += f"\n\n![Course visual: {'the information value pathway' if unit == 6 else 'Laila and Martha: source and quality context'}](../../readings/ucsf/assets/slide-previews/unit-{deck}-{page:03d}.jpg)\n\n"
            intro += f"*Slide connection: Unit {deck}, Version 2, slide {page}. Use this visual as you compare the source, control, or evidence in the task.*\n"
        else:
            intro += "\n\n| Security | Confidentiality | Privacy |\n| --- | --- | --- |\n| Protection against unauthorized access, change, and disclosure | Secrecy of health data | Individual control of personal health information |\n\n*Slide connection: Version 2 Unit 3, slide 60 compares these three concepts.*\n"
        meta = {"al": {"activity": EX + "act-" + ident, "object": EX + "act-" + ident + "-exercise", "check": "checks/" + ident,
                       "hints": spec["hints"]}, "tags": ["al-exercise"]}
        next_name = f"u{unit+1:02d}-n01-{UNITS[unit-3]['slug']}.ipynb" if unit < 8 else "u09-n01-dictionary-value-map.ipynb"
        continuation = f"## Continue Laila's case\n\n[{'Next notebook'}]({next_name}) · [Course start](u00-n00-start-here.ipynb)\n\nUse the **Learning** panel to see what this attempt recorded and what it recommends. Your learning record keeps attempts and hints used."
        cells = [cell("markdown", intro, "0"), cell("code", setup_code(spec), "1", {"jupyter": {"source_hidden": True}}),
                 cell("markdown", "## Check my work\n\nRun the next cell after making your choices. Incomplete and incorrect attempts remain in your learning record. You can revise your choices and try again.", "check-instructions"),
                 cell("code", exercise_code(spec), "2", meta),
                 cell("markdown", "## Reflect on the decision\n\nRun the next cell to write your reflections. Select **Record** to save them with your learner record in this browser. Reflections are unscored.", "3"),
                 cell("code", reflection_code("exercise:" + ident, spec["reflection"]), "reflection-fields", {"jupyter": {"source_hidden": True}}),
                 cell("markdown", continuation, "continue")]
        document = {"cells": cells, "metadata": {"title": spec["title"], "generatedBy": "scripts/make_units04_08.py",
                    "kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"}, "language_info": {"name": "python"},
                    "al": {"activity": EX + "act-" + ident, "language": "python"}}, "nbformat": 4, "nbformat_minor": 5}
        (ROOT / "content/exercises/python" / filename).write_text(json.dumps(document, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        check = "import json as _al_json\nfrom collections import Counter\nfrom datetime import date\n" + inspect.getsource(expected_answers) + "\n" + inspect.getsource(evaluate_answer)
        check += f"\nprint('AL_OBSERVATION ' + _al_json.dumps({{'outcome': evaluate_answer({unit}, globals().get('unit{unit:02d}_response'), {DATA!r})}}))\n"
        (ROOT / "app-assets/adaptive-learning/checks" / (ident + ".py")).write_text(check, encoding="utf-8")
    print("generated five Python narratives and five adaptive checks (Units 4–8)")
    scenarios = [{"unit": spec["unit"], "id": f"u{spec['unit']:02d}-{spec['slug']}",
                  "path": f"notebooks/u{spec['unit']:02d}-n01-{spec['slug']}.ipynb",
                  "controls": [{"key": key, "label": label, "kind": kind, "options": options} for key, label, kind, options in spec["controls"]],
                  "correct": expected_answers(spec["unit"], DATA)} for spec in UNITS]
    fixture = ROOT / "test/fixtures/units04-08-scenarios.json"
    fixture.parent.mkdir(exist_ok=True)
    fixture.write_text(json.dumps(scenarios, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
