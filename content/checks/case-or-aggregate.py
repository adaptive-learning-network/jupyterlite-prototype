import json as _al_json
def _al_check():
    g = globals()
    if g.get('aggregate_tables') is None:
        return 'incomplete'
    try:
        if not (sorted({str(x).strip().lower() for x in g['aggregate_tables']}) == ['b', 'c', 'e']):
            return 'incorrect'
    except (TypeError, ValueError):
        return 'incorrect'
    return 'correct'
print('AL_OBSERVATION ' + _al_json.dumps({'outcome': _al_check()}))
del _al_check
