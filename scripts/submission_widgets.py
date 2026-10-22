"""Explicit submission shared by computed answers and review controls."""


def submission_code(cell_id: str, prepare: str = "", fields: tuple = ()) -> str:
    return '''# Run once to display Submit. Running this cell does not submit an attempt.
try:
    import ipywidgets as widgets
except ImportError:
    import piplite
    await piplite.install("ipywidgets==8.1.7")
    import ipywidgets as widgets
from IPython.display import display, clear_output
from comm import create_comm
from html import escape

def _show_course_submission():
    prepare = ''' + repr(prepare) + '''
    fields = ''' + repr(fields) + '''
    controls_for_task = dict(globals().get("controls", {}))
    submit = widgets.Button(description="Submit", button_style="info", disabled=True)
    feedback = widgets.HTML(value="Connecting to your learning record...")
    artifact_output = widgets.Output(layout=widgets.Layout(width="100%"))
    channel = create_comm(target_name="al.submit", data={"cell": ''' + repr(cell_id) + '''})
    def status(text):
        feedback.value = '<div role="status" aria-live="polite">' + text + '</div>'
    def receive(message):
        data = message["content"]["data"]
        if data.get("ready"):
            status("When your answer is ready, select Submit for feedback.")
        elif data.get("outcome") == "Incomplete":
            status("<b>Not complete yet.</b> Answer every part, then submit again. This attempt was recorded.")
        elif data.get("outcome") == "Correct":
            status("<b>Correct.</b> Your submitted answer follows the stated data and rules. This attempt was recorded.")
        elif data.get("outcome") == "Incorrect":
            status("<b>Not yet correct.</b> Compare your submitted answer with the displayed data and rules. Revise and submit again. This attempt was recorded.")
        else:
            status(escape(data.get("error", "Could not record this attempt. Please submit again.")))
        for control in controls_for_task.values():
            control.disabled = False
        submit.disabled = False
    channel.on_msg(receive)
    def send(_):
        if submit.disabled:
            return
        submit.disabled = True
        for control in controls_for_task.values():
            control.disabled = True
        status("Checking and recording your submitted answer...")
        try:
            with artifact_output:
                clear_output(wait=True)
                exec(prepare, globals())
                if fields:
                    rows = ''.join('<tr><th style="text-align:left">' + escape(name) + '</th><td>' +
                                   escape(str(globals().get(name))) + '</td></tr>' for name in fields)
                    display(widgets.HTML('<b>Submitted answer</b><table>' + rows + '</table>'))
            channel.send({"submit": True})
        except Exception as error:
            status("Could not prepare your answer: " + escape(str(error)) + ". Run the required cells and try again. No attempt was submitted.")
            for control in controls_for_task.values():
                control.disabled = False
            submit.disabled = False
    def edited(_):
        if not submit.disabled:
            status("Changes not submitted. Select Submit for feedback.")
    for control in controls_for_task.values():
        control.observe(edited, names="value")
    submit.on_click(send)
    display(submit, artifact_output, feedback)

_show_course_submission()
'''
