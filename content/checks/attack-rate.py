import json as _al_json
def _al_check():
    g = globals()
    if g.get('ar_exposed') is None:
        return 'incomplete'
    try:
        if not (abs(float(g['ar_exposed']) - 0.75) < 1e-6):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    if g.get('ar_unexposed') is None:
        return 'incomplete'
    try:
        if not (abs(float(g['ar_unexposed']) - 0.25) < 1e-6):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
