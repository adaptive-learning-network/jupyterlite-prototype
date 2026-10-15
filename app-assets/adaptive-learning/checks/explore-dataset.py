import json as _al_json
def _al_check():
    g = globals()
    if g.get('n_records') is None:
        return 'incomplete'
    try:
        if not (int(g['n_records']) == 139):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    if g.get('first_date') is None:
        return 'incomplete'
    try:
        if not (str(g['first_date'])[:10] == '2025-01-06'):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    if g.get('last_date') is None:
        return 'incomplete'
    try:
        if not (str(g['last_date'])[:10] == '2025-06-23'):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    if g.get('n_locations') is None:
        return 'incomplete'
    try:
        if not (int(g['n_locations']) == 3):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    if g.get('age_min') is None:
        return 'incomplete'
    try:
        if not (int(g['age_min']) == 0):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    if g.get('age_max') is None:
        return 'incomplete'
    try:
        if not (int(g['age_max']) == 9):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
