import json as _al_json
def _al_check():
    g = globals()
    if g.get('n_mmr_dose1_x') is None:
        return 'incomplete'
    try:
        if not (int(g['n_mmr_dose1_x']) == 46):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
