import json as _al_json
def _al_check():
    g = globals()
    required = ("org_unit", "events", "onset_element", "n_cases", "n_missing_onset", "first_onset", "last_onset")
    if any(g.get(name) is None for name in required):
        return "incomplete"
    try:
        if g["org_unit"] != 'OU_KAMBIA' or g["onset_element"] != 'DE_ONSET':
            return "incorrect"
        if not isinstance(g["events"], list) or sorted(e["event"] for e in g["events"]) != ['EV_001', 'EV_002', 'EV_003', 'EV_004', 'EV_005']:
            return "incorrect"
        if int(g["n_cases"]) != 5 or int(g["n_missing_onset"]) != 1:
            return "incorrect"
        if str(g["first_onset"]) != '2021-10-18' or str(g["last_onset"]) != '2021-11-04':
            return "incorrect"
    except (KeyError, TypeError, ValueError):
        return "incorrect"
    return "correct"
print("AL_OBSERVATION " + _al_json.dumps({"outcome": _al_check()}))
del _al_check
