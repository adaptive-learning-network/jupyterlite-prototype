"""Generate per-table classification controls for U03 N06."""


def setup_code(tables: dict[str, str], aggregate_letters: list[str]) -> str:
    return '''# Run once to display the table choices. Re-running clears selections.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from IPython.display import display
from comm import create_comm
from html import escape

def _show_dataset_classification():
    tables = ''' + repr(tables) + '''
    expected_aggregate = set(''' + repr(aggregate_letters) + ''')
    controls = {}
    submitted = {}
    examples = {
        "a": [["P01", "Training person A", 8, "F", "Kambia", "Suspected measles"]],
        "b": [["Kambia", 12, 3], ["Port Loko", 7, 2]],
        "c": [["0-4", "Measles", 3], ["5-14", "Measles", 5]],
        "d": [["TA", "2017-03-10", "Kambia", "2021-10-18"]],
        "e": [["Training county A", 12, 1, 8]],
    }
    for letter, table in tables.items():
        choice = widgets.RadioButtons(options=[("Case-based", "case"), ("Aggregate", "aggregate")],
                                      index=None, layout=widgets.Layout(width="100%", height="auto"))
        controls[letter] = choice
        headings = table.removeprefix("Table with ").split(", ")
        example_html = '<div style="overflow-x:auto"><table><caption>Invented example rows</caption><tr>' + ''.join('<th>' + escape(h) + '</th>' for h in headings) + '</tr>'
        for row in examples[letter]:
            example_html += '<tr>' + ''.join('<td>' + escape(str(value)) + '</td>' for value in row) + '</tr>'
        example_html += '</table></div>'
        card = widgets.VBox([
            widgets.HTML(f'<b>Table {letter.upper()}</b><p style="overflow-wrap:anywhere">{escape(table)}</p>'),
            widgets.HTML(example_html), choice,
        ], layout=widgets.Layout(width="100%", padding="0.5rem", margin="0 0 0.75rem 0"))
        card.add_class("al-dataset-" + letter)
        display(card)

    submit = widgets.Button(description="Submit", button_style="info", disabled=True)
    feedback = widgets.HTML(value="Connecting to your learning record...")
    channel = create_comm(target_name="al.submit", data={"cell": "1"})

    def receive(message):
        data = message["content"]["data"]
        outcome = data.get("outcome")
        if data.get("ready"):
            feedback.value = "Classify each table, then select Submit."
        elif outcome == "Incomplete":
            missing = ", ".join(letter.upper() for letter, value in submitted.items() if value is None)
            feedback.value = "<b>Not complete yet.</b> Choose a classification for table(s) " + missing + ". This attempt was recorded."
        elif outcome in {"Correct", "Incorrect"}:
            rows = []
            for letter, value in submitted.items():
                expected = "aggregate" if letter in expected_aggregate else "case"
                correct = value == expected
                explanation = ("These fields summarize counts for a district, age/disease group, or county."
                               if expected == "aggregate" else "These fields describe individual people or cases, rather than grouped counts.")
                rows.append(f"<p><b>Table {letter.upper()}: {'Correct' if correct else 'Incorrect'}.</b> " + explanation + "</p>")
            feedback.value = ("<b>All five classifications are correct.</b>" if outcome == "Correct" else
                              "<b>Some classifications need another look.</b>") + "".join(rows) + "Attempt recorded. Change a choice and submit again to retry."
        else:
            feedback.value = escape(data.get("error", "Could not record this attempt. Please submit again."))
        submit.disabled = False
        for control in controls.values():
            control.disabled = False

    channel.on_msg(receive)

    def submit_choices(_):
        global aggregate_tables
        submitted.clear()
        submitted.update({letter: control.value for letter, control in controls.items()})
        aggregate_tables = (None if any(value is None for value in submitted.values()) else
                            [letter for letter, value in submitted.items() if value == "aggregate"])
        submit.disabled = True
        for control in controls.values():
            control.disabled = True
        feedback.value = "Checking and recording your classifications..."
        channel.send({"submit": True})

    def edited(_):
        if not submit.disabled:
            feedback.value = "Choices changed. Select Submit to check them."

    for control in controls.values():
        control.observe(edited, names="value")
    submit.on_click(submit_choices)
    display(submit, feedback)

_show_dataset_classification()
'''
