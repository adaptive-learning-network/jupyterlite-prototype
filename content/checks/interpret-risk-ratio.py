import json as _al_json
def _al_check():
    g = globals()
    if g.get('answer') is None:
        return 'incomplete'
    try:
        if not (str(g['answer']).strip().lower() == 'b'):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
