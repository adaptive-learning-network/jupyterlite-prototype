"""Radio choices and recorded feedback for the Unit 3 single-value question."""


def setup_code(rules: dict[str, str]) -> str:
    return '''# Run once to display the question. Re-running clears the selection.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from IPython.display import display
from comm import create_comm
from html import escape

def _show_machine_readable_question():
    rules = ''' + repr(rules) + '''
    choices = widgets.RadioButtons(
        options=[(f"{letter.upper()}. {text}", letter) for letter, text in rules.items()],
        index=None, layout=widgets.Layout(width="100%", height="auto"))
    choices.add_class("al-machine-readable-choices")
    submit = widgets.Button(description="Submit", button_style="info", disabled=True)
    feedback = widgets.HTML(value="Connecting to your learning record...")
    channel = create_comm(target_name="al.submit", data={"cell": "1"})

    def receive(message):
        data = message["content"]["data"]
        if data.get("ready"):
            feedback.value = "Select one answer, then select Submit."
        elif data.get("outcome") == "Incomplete":
            feedback.value = "<b>Select an answer first.</b> This incomplete attempt was recorded."
        elif data.get("outcome") == "Correct":
            feedback.value = "<b>Correct.</b> Each value has its own cell. MMR, Polio, and Hepatitis B are three vaccine values packed into one cell. Use one patient-vaccine observation per row so each vaccine value has its own cell. This attempt was recorded."
        elif data.get("outcome") == "Incorrect":
            explanation = ("The question describes multiple vaccine values inside one cell, rather than observations sharing a row."
                           if answer == "a" else "Vaccine Type already has its own column. The problem is that one cell contains three vaccine values.")
            feedback.value = "<b>Not yet correct.</b> " + explanation + " Select another answer and submit again. This attempt was recorded."
        else:
            feedback.value = escape(data.get("error", "Could not record this attempt. Please submit again."))
        choices.disabled = False
        submit.disabled = False

    channel.on_msg(receive)

    def submit_answer(_):
        global answer
        answer = choices.value
        choices.disabled = True
        submit.disabled = True
        feedback.value = "Checking and recording your answer..."
        channel.send({"submit": True})

    def edited(_):
        if not choices.disabled:
            feedback.value = "Answer changed. Select Submit to check it."

    choices.observe(edited, names="value")
    submit.on_click(submit_answer)
    display(widgets.HTML("""<style>
    .al-machine-readable-choices .widget-radio-box label {
      height: auto !important; min-height: 28px; white-space: normal !important;
      display: flex; align-items: flex-start; line-height: 1.5; margin-bottom: 6px;
    }
    .al-machine-readable-choices input { flex-shrink: 0; margin-top: 4px; }
    .al-machine-readable-choices .widget-radio-box { width: 100%; min-width: 0; }
    </style><b>Which rule does this cell break?</b><p>Select one answer.</p>"""),
            choices, submit, feedback)

_show_machine_readable_question()
'''
