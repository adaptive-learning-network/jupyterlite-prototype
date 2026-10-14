#!/usr/bin/env python3
"""Build the optional, unscored local course question library."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "course-materials/version3-form-library.md"
FEEDBACK = ROOT / "course-materials/version3-quiz-feedback.json"
OUTPUT = ROOT / "content/readings/ucsf/u00-n02-version3-form-library.ipynb"
REVIEW = ROOT / "docs/review/provisional-quiz-feedback.md"
QUESTION = re.compile(r"(?m)^\d+\. \*\*(.+?)\*\*(?:[^\n]*)\n((?:[ \t]+- [^\n]+\n?)+)")
MODES = {
    "Unit 1": ["one", "many", "one", "one"],
    "Unit 2": ["one", "many", "one", "one", "one", "one"],
    "Unit 4": ["many", "one", "many", "many"],
    "Unit 5": ["many", "one", "many", "many", "many"],
    "Unit 7": ["one", "one", "one", "many", "one", "one", "many", "one", "many"],
}


def cell(kind: str, source: str, cell_id: str, *, hidden: bool = False) -> dict:
    result = {
        "cell_type": kind, "id": cell_id,
        "metadata": {"jupyter": {"source_hidden": True}} if hidden else {},
        "source": source.strip().splitlines(keepends=True),
    }
    if kind == "code":
        result.update({"execution_count": None, "outputs": []})
    return result


def questions(source: str, unit: str, feedback: list[dict]) -> list[dict]:
    found = [{"prompt": prompt, "choices": [line.strip()[2:] for line in options.splitlines()]}
             for prompt, options in QUESTION.findall(source)]
    modes = MODES[unit]
    if len(found) != len(modes) or len(feedback) != len(found) or any(len(item["choices"]) < 2 for item in found):
        raise ValueError(f"review quiz parsing for {unit}: {len(found)} questions")
    for item in found:
        if any(choice.strip().rstrip(".").casefold() in {"choose one", "select one", "select all that apply"}
               for choice in item["choices"]):
            raise ValueError(f"instruction parsed as a choice for {unit}: {item['prompt']}")
    for item, mode, answer in zip(found, modes, feedback):
        item["mode"] = mode
        correct = answer["correct"]
        if (not correct or len(set(correct)) != len(correct) or
                any(not isinstance(index, int) or index < 1 or index > len(item["choices"]) for index in correct) or
                (mode == "one" and len(correct) != 1) or not answer["feedback"].strip()):
            raise ValueError(f"review provisional feedback for {unit}: {item['prompt']}")
        item["correct"] = correct
        item["feedback"] = answer["feedback"]
    return found


def written_prompts(case: str, unit: str) -> list[str]:
    if unit == "Unit 1":
        first = re.search(r"(?m)^1\. (.+)$", case)
        second = re.search(r"(?m)^2\. (.+)$", case)
        parts = re.findall(r"(?m)^   - (.+)$", case)
        if not first or not second or len(parts) != 3:
            raise ValueError("review Unit 1 written prompts")
        return [first.group(1), *(f"{second.group(1)} {part}" for part in parts)]
    prompts = re.findall(r"(?m)^- (?:[a-d]|\d+)\. (.+)$", case)
    if len(prompts) != 10:
        raise ValueError(f"review {unit} written prompts: {len(prompts)}")
    return prompts


def response_code(unit: str, prompts: list[str]) -> str:
    data = json.dumps(prompts, ensure_ascii=False)
    return f'''# Run this cell to write responses for {unit}. The code is setup only.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from html import escape
from IPython.display import display

prompts = {data}
response_fields = []
cards = []
for number, prompt in enumerate(prompts, 1):
    field = widgets.Textarea(
        placeholder='Write your response here',
        layout=widgets.Layout(width='100%', height='100px'),
    )
    response_fields.append(field)
    cards.append(widgets.VBox([
        widgets.HTML(value=f"<strong>{{number}}. {{escape(prompt)}}</strong>"), field,
    ], layout=widgets.Layout(border='1px solid #d6dee5', padding='0.75rem', margin='0 0 0.75rem 0')))
display(widgets.VBox(cards))
'''


def quiz_code(unit: str, items: list[dict]) -> str:
    # These wheels are in the local JupyterLite index. Feedback is explicitly
    # provisional and does not create an adaptive observation.
    data = json.dumps(items, ensure_ascii=False)
    return f'''# Run this cell to choose answers for {unit}. The code is setup only.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from html import escape
from IPython.display import HTML, display

display(HTML("""<style>
.course-quiz-card .widget-radio,
.course-quiz-card .widget-checkbox {{ height: auto !important; }}
.course-quiz-card .widget-radio-box {{ width: 100% !important; }}
.course-quiz-card .widget-radio-box label,
.course-quiz-card .widget-checkbox .widget-label-basic {{
    display: block !important;
    position: relative;
    box-sizing: border-box;
    height: auto !important;
    min-height: 1.6em;
    padding: 0.15em 0 0.15em 1.65em;
    margin: 0.15em 0;
    line-height: 1.4;
    white-space: normal !important;
    overflow-wrap: anywhere;
}}
.course-quiz-card .widget-radio-box label input[type=radio],
.course-quiz-card .widget-checkbox .widget-label-basic input[type=checkbox] {{
    position: absolute;
    left: 0;
    top: 0.35em;
    margin: 0;
}}
</style>"""))

items = {data}
controls = []
cards = []
for number, item in enumerate(items, 1):
    title = widgets.HTML(value=f"<strong>{{number}}. {{escape(item['prompt'])}}</strong><br><small>Select {{'one' if item['mode'] == 'one' else 'all that apply'}}.</small>")
    if item['mode'] == 'one':
        control = widgets.RadioButtons(
            options=[(choice, choice) for choice in item['choices']],
            index=None, layout=widgets.Layout(width='100%'),
            style={{'description_width': 'initial'}},
        )
    else:
        control = [widgets.Checkbox(value=False, description=choice, indent=False,
                   layout=widgets.Layout(width='100%'), style={{'description_width': 'initial'}})
                   for choice in item['choices']]
    controls.append(control)
    choices = control if isinstance(control, list) else [control]
    card = widgets.VBox([title, *choices], layout=widgets.Layout(
        border='1px solid #d6dee5', padding='0.75rem', margin='0 0 0.75rem 0'))
    card.add_class('course-quiz-card')
    cards.append(card)

summary = widgets.Output()
review_button = widgets.Button(description='Submit for feedback', button_style='info')
def review(_, unit_items=items, unit_controls=controls, output=summary):
    with output:
        output.clear_output()
        print('{unit} provisional practice feedback (not the official form key):')
        correct_count = 0
        for number, (item, control) in enumerate(zip(unit_items, unit_controls), 1):
            selected = ([index for index, choice in enumerate(control, 1) if choice.value]
                        if isinstance(control, list) else
                        ([item['choices'].index(control.value) + 1] if control.value is not None else []))
            if not selected:
                print(f"{{number}}. Choose an answer, then submit again.")
                continue
            is_correct = set(selected) == set(item['correct'])
            correct_count += is_correct
            print(f"{{number}}. {{'Correct' if is_correct else 'Incorrect'}}. {{item['feedback']}}")
            if not is_correct:
                expected = '; '.join(item['choices'][index - 1] for index in item['correct'])
                print(f"   Provisional expected choice: {{expected}}")
        print(f"{{correct_count}} of {{len(unit_items)}} matched the provisional practice key. You can revise and submit again.")
review_button.on_click(review)
display(widgets.VBox([*cards, review_button, summary]))
'''


def main() -> None:
    sections = SOURCE.read_text(encoding="utf-8").split("<!-- notebook cell -->")
    if len(sections) != 4:
        raise ValueError("form library must have four reviewed sections")
    feedback_file = json.loads(FEEDBACK.read_text(encoding="utf-8"))
    feedback = feedback_file["units"]
    if set(feedback) != set(MODES) or not feedback_file["status"].startswith("provisional"):
        raise ValueError("review provisional quiz feedback coverage and status")
    unit1_quiz, unit1_case = sections[1].split("### Small group work U01-N02", 1)
    unit2_quiz, unit2_case = sections[2].split("### Case-study questions", 1)
    blocks = re.split(r"(?=^### Unit [457]\b)", sections[3], flags=re.M)
    if len(blocks) != 4:
        raise ValueError("expected Unit 4, 5, and 7 question groups")
    cells = [cell("markdown", sections[0], "intro")]
    review_groups: dict[str, list[dict]] = {}
    for unit, source, case in [
        ("Unit 1", unit1_quiz, "### Small group work" + unit1_case),
        ("Unit 2", unit2_quiz, "### Case-study questions" + unit2_case),
    ]:
        slug = unit.lower().replace(" ", "-")
        cells.append(cell("markdown", f"## {unit} · Practice quiz\n\nChoose answers below, then select **Submit for feedback**. This provisional feedback is for practice; it does not update your adaptive learning record.", f"{slug}-intro"))
        review_groups[unit] = questions(source, unit, feedback[unit])
        cells.append(cell("code", quiz_code(unit, review_groups[unit]), f"{slug}-choices", hidden=True))
        cells.append(cell("markdown", f"## {unit} · Written case study\n\nWrite a response for each prompt below. These responses are unscored. Copy anything you want to keep before restarting the kernel.", f"{slug}-case"))
        cells.append(cell("code", response_code(unit, written_prompts(case, unit)), f"{slug}-responses", hidden=True))
    for unit, block in zip(("Unit 4", "Unit 5", "Unit 7"), blocks[1:]):
        slug = unit.lower().replace(" ", "-")
        cells.append(cell("markdown", f"## {unit} · Practice quiz\n\nChoose answers below, then select **Submit for feedback**. This provisional feedback is for practice; it does not update your adaptive learning record.", f"{slug}-intro"))
        review_groups[unit] = questions(block, unit, feedback[unit])
        cells.append(cell("code", quiz_code(unit, review_groups[unit]), f"{slug}-choices", hidden=True))
    notebook = {
        "cells": cells,
        "metadata": {
            "title": "Practice questions for Laila's case",
            "generatedBy": "scripts/make_form_library.py",
            "kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Provisional quiz feedback for review", "",
             "**Status:** Provisional practice feedback, not the official Google Forms answer key.",
             "The supplied quiz PDFs list questions and point values but do not identify correct choices or explanations. "
             "These proposed choices were inferred from the supplied course slides and question wording. "
             "Do not use them as an official assessment key until a course owner reviews them.", "",
             "The learner-facing library is `content/readings/ucsf/u00-n02-version3-form-library.ipynb`. "
             "Edit `course-materials/version3-quiz-feedback.json` to correct a proposed choice or explanation, "
             "then regenerate the notebook and this review sheet.", "",
             "**Priority review:** Unit 2 question 2 says ‘select all’ although this provisional key has one choice; "
             "Unit 5 questions 1–2 depend on the course's distinction between PII, PHI, and other sensitive data; "
             "Unit 7 question 2 offers a drop-down but no explicit yes/no radio control. "
             "Please confirm those items against the form owner's key first. "
             "[CDC guidance](https://www.cdc.gov/niosh/ocas/datahandle.html) and "
             "[HHS guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html) "
             "treat biometric identifiers as identifying in relevant contexts, so Unit 5's slide category should not be generalized.", ""]
    for unit, items in review_groups.items():
        lines += [f"## {unit}", ""]
        for number, item in enumerate(items, 1):
            selected = "; ".join(f"{index}. {item['choices'][index - 1]}" for index in item["correct"])
            lines += [f"### Question {number}: {item['prompt']}", "",
                      f"**Proposed choice{'s' if len(item['correct']) > 1 else ''}:** {selected}", "",
                      f"**Feedback:** {item['feedback']}", ""]
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    REVIEW.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {sum(map(len, MODES.values()))} interactive questions")


if __name__ == "__main__":
    main()
