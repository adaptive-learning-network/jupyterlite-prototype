import json as _al_json
def _al_check():
    g = globals()
    if g.get('risk_ratio') is None:
        return 'incomplete'
    try:
        if not (abs(float(g['risk_ratio']) - 3.0) < 1e-6):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
