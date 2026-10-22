"""Shared reflection controls for course notebook generators."""


import hashlib
import json
from pathlib import Path


def reflection_code(section: str, prompts: list[str]) -> str:
    registry = json.loads(Path(__file__).with_name('reflection_questions.json').read_text(encoding='utf-8'))
    questions = []
    for prompt in prompts:
        question = next((q for q in registry.get(section, []) if prompt == q['prompt'] or prompt in q['legacyPrompts']), None)
        questions.append(question or {'id': 'q-' + hashlib.sha256(prompt.encode()).hexdigest()[:12], 'version': 1, 'prompt': prompt, 'legacyPrompts': [prompt]})
    return """# Run this cell to write and record your reflections.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from html import escape
from IPython.display import display
from comm import create_comm

def _reflection_section(section, questions):
    prompts = [question["prompt"] for question in questions]
    fields = []
    for number, prompt in enumerate(prompts, 1):
        field = widgets.Textarea(placeholder="Write your reflection here", rows=5,
                                 layout=widgets.Layout(width="100%"))
        fields.append(field)
        display(widgets.VBox([
            widgets.HTML(value=f"<strong>{number}. {escape(prompt)}</strong>"), field
        ], layout=widgets.Layout(width="100%", padding="0.5rem", margin="0 0 0.5rem 0")))
    button = widgets.Button(description="Record", button_style="info", disabled=True)
    status = widgets.HTML(value="Connecting to your browser learner record...")
    status.add_class("course-reflection-status")
    channel = create_comm(target_name="al.reflections", data={"section": section})
    def receive(message):
        data = message["content"]["data"]
        if "entries" in data:
            entries = data["entries"]
            restored = 0
            earlier = 0
            for question, field in zip(questions, fields):
                saved = next((entry for entry in reversed(entries) if
                    (entry.get("id") == question["id"] and entry.get("version") == question["version"]) or
                    (question["version"] == 1 and not entry.get("id") and entry["prompt"] in question["legacyPrompts"])), None)
                field.value = saved["answer"] if saved else ""
                restored += saved is not None
                earlier += any(entry.get("id") == question["id"] and entry.get("version") != question["version"] for entry in entries)
            status.value = "Recorded reflections restored." if restored else "Select Record to save in this browser."
            if earlier or any(entry.get("history") for entry in entries) or len(entries) > restored:
                status.value += " Earlier responses remain in My learning record and Download reflections. Review them before answering revised questions."
        elif data.get("saved"):
            status.value = "Recorded in this browser. Your reflections are unscored."
        else:
            status.value = escape(data.get("error", "Could not record. Please try again."))
        button.disabled = False
    channel.on_msg(receive)
    def record(_):
        button.disabled = True
        status.value = "Recording..."
        channel.send({"entries": [{**question, "answer": field.value}
                                  for question, field in zip(questions, fields)]})
    def edited(_):
        status.value = "Changes not recorded. Select Record to save."
    for field in fields:
        field.observe(edited, names="value")
    button.on_click(record)
    display(button, status)

_reflection_section(""" + repr(section) + ", " + repr(questions) + ")\n"
