import json as _al_json
def _al_check():
    g = globals()
    if g.get('coverage_x') is None:
        return 'incomplete'
    try:
        if not (abs(float(g['coverage_x']) - 0.92) < 1e-6):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
