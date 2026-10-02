import json as _al_json
def _al_check():
    g = globals()
    if g.get('ill_exposed') is None:
        return 'incomplete'
    try:
        if not (int(g['ill_exposed']) == 30):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
