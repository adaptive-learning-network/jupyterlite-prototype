"""Generate the U03 N06 practice and different-case assessment pilot."""
import json
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[1] / 'catalog/case-aggregate-v1.json'

def check_code():
    policy = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    return '''import json as _json
_policy = ''' + repr(policy) + '''
_response = globals().get('classification_response')
if isinstance(_response, dict):
    _task_id = _response.get('taskId')
    _task = next((task for task in _policy['tasks'] if task['id'] == _task_id), None)
    if _task is None:
        raise ValueError('Unknown classification task')
    _answers = _response.get('answers', {})
    _criteria = [{'id': table['id'], 'selection': _answers.get(table['id']) if _answers.get(table['id']) in {'case', 'aggregate'} else None, 'outcome': ('incomplete' if _answers.get(table['id']) not in {'case', 'aggregate'} else
        'correct' if _answers[table['id']] == ('case' if table['rowUnit'] == 'case' else 'aggregate') else 'incorrect')}
        for table in _task['tables']]
    _outcome = 'incomplete' if any(r['outcome'] == 'incomplete' for r in _criteria) else 'correct' if all(r['outcome'] == 'correct' for r in _criteria) else 'incorrect'
    print('AL_OBSERVATION ' + _json.dumps({'outcome': _outcome, 'taskId': _task_id, 'criteria': _criteria}))
else:
    # Native legacy check contract; the new browser protocol requires criteria.
    _answer = globals().get('aggregate_tables')
    _expected = {table['id'] for table in _policy['tasks'][0]['tables'] if table['rowUnit'] == 'group'}
    _outcome = 'incomplete' if _answer is None else 'correct' if set(_answer) == _expected else 'incorrect'
    print('AL_OBSERVATION ' + _json.dumps({'outcome': _outcome}))
'''


def setup_code(tables=None, aggregate_letters=None, hints=None):
    policy = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    return '''# Run once to display practice and new-case controls. Re-running preserves attempt history.
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
    policy = ''' + repr(policy) + '''
    hints = ''' + repr(hints or []) + '''
    state = {}
    controls = {}
    stage = widgets.HTML()
    cards = widgets.VBox(layout=widgets.Layout(width="100%"))
    submit = widgets.Button(description="Submit", button_style="info", disabled=True)
    hint = widgets.Button(description="Show a hint", disabled=True)
    another = widgets.Button(description="Try another case", disabled=True)
    practice = widgets.Button(description="Return to practice", disabled=True)
    feedback = widgets.HTML(value="Connecting to your learning record...")
    feedback.add_class('al-classification-feedback')
    help_text = widgets.HTML()
    progress_text = widgets.HTML()
    buttons = widgets.VBox([submit, hint, another, practice], layout=widgets.Layout(width="100%"))
    display(stage, cards, buttons, feedback, help_text, progress_text)
    channel = create_comm(target_name='al.practice', data={'cell': '1', 'version': policy['version']})

    def lock():
        for button in (submit, hint, another, practice): button.disabled = True
        for control in controls.values(): control.disabled = True

    def render(attempt):
        task = next(task for task in policy['tasks'] if task['id'] == attempt['taskId'])
        state['task'] = task
        controls.clear()
        new_cards = []
        stage.value = '<h2>' + ('Practice' if attempt['mode'] == 'practice' else 'New case') + '</h2><p>' + escape(task['title']) + '</p><p>Classify each table using what one row represents.</p>'
        for table in task['tables']:
            head = ''.join('<th scope="col">' + escape(name) + '</th>' for name in table['columns'])
            body = ''.join('<tr>' + ''.join('<td>' + escape(str(value)) + '</td>' for value in row) + '</tr>' for row in table['rows'])
            preview = '<div style="overflow-x:auto"><table><caption>Invented example rows</caption><thead><tr>' + head + '</tr></thead><tbody>' + body + '</tbody></table></div>'
            choice = widgets.RadioButtons(options=[('Case-based', 'case'), ('Aggregate', 'aggregate')], index=None,
                layout=widgets.Layout(width='100%', height='auto'))
            controls[table['id']] = choice
            card = widgets.VBox([widgets.HTML('<b>Table ' + table['id'].upper() + ': ' + escape(table['title']) + '</b>'), widgets.HTML(preview), choice],
                layout=widgets.Layout(width='100%', padding='0.5rem', margin='0 0 0.75rem 0'))
            card.add_class('al-dataset-' + table['id'])
            new_cards.append(card)
        cards.children = tuple(new_cards)
        feedback.value = ('Select answers, then Submit. Hints and feedback are available in practice.' if attempt['mode'] == 'practice' else
            'This is a different case. Submit all classifications before seeing feedback. Only your first complete submission can demonstrate performance on this new case. No hints are provided during this check.')
        if attempt['submissions']:
            feedback.value += '<p>Earlier submissions for this task are retained. Re-running does not make this an unseen case.</p>'

    def receive(message):
        data = message['content']['data']
        if data.get('connected'):
            channel.send({'action': 'resume'})
            return
        if data.get('error'):
            feedback.value = '<b>Could not complete that request.</b> ' + escape(data['error'])
        else:
            attempt = data['attempt']
            if state.get('attempt', {}).get('id') != attempt['id']:
                render(attempt)
                for result in data.get('lastCriteria', []):
                    if result['id'] in controls:
                        controls[result['id']].value = result.get('selection')
            state['attempt'] = attempt
            progress = data['progress']
            progress_text.value = '<p><b>' + escape(progress['label']) + '</b></p><p>This describes your performance on these tasks, not a certification of workplace proficiency.</p>'
            if data.get('outcome') == 'incomplete':
                missing = ', '.join(r['id'].upper() for r in data['criteria'] if r['outcome'] == 'incomplete')
                feedback.value = '<b>Not complete yet.</b> Choose a classification for table(s) ' + missing + '. This submission was recorded. No answer feedback is shown yet.'
            elif data.get('outcome') in {'correct', 'incorrect'}:
                rows = []
                for result in data['criteria']:
                    table = next(t for t in state['task']['tables'] if t['id'] == result['id'])
                    explanation = ('Each row describes one case. A number or age-group label can still describe an individual case.' if table['rowUnit'] == 'case' else
                        'Each row summarizes a group of cases. A summary or report ID identifies the group report, not an individual case.')
                    rows.append('<p><b>Table ' + result['id'].upper() + ': ' + ('Correct' if result['outcome'] == 'correct' else 'Incorrect') + '.</b> ' + explanation + '</p>')
                feedback.value = ('<b>All classifications are correct.</b>' if data['outcome'] == 'correct' else '<b>Some classifications need another look.</b>') + ''.join(rows) + '<p>Submission recorded. You can revise these choices for practice, or try another case.</p>'
            suggestions = ''.join('<p><b>Suggested help:</b> ' + escape(text) + '</p>' for text in progress['suggestions'])
            shown = ''.join('<p><b>Hint ' + str(i+1) + ':</b> ' + escape(text) + '</p>' for i, text in enumerate(hints[:attempt['guidanceLevel']])) if attempt['mode'] == 'practice' else ''
            help_text.value = shown + suggestions
        attempt = state.get('attempt')
        submit.disabled = attempt is None
        hint.disabled = attempt is None or attempt['mode'] != 'practice' or attempt['guidanceLevel'] >= len(hints)
        another.disabled = attempt is None or (attempt['mode'] == 'practice' and attempt['submissions'] == 0)
        practice.disabled = attempt is None or attempt['mode'] == 'practice'
        for control in controls.values(): control.disabled = False

    def send(action, **values):
        lock()
        channel.send({'action': action, **values})
    def submit_choices(_):
        global classification_response
        classification_response = {'taskId': state['attempt']['taskId'], 'answers': {key: control.value for key, control in controls.items()}}
        feedback.value = 'Checking and recording your classifications...'
        send('submit')
    submit.on_click(submit_choices)
    hint.on_click(lambda _: send('hint'))
    another.on_click(lambda _: send('begin', mode='reassessment'))
    practice.on_click(lambda _: send('begin', mode='practice'))
    channel.on_msg(receive)

_show_dataset_classification()
'''
