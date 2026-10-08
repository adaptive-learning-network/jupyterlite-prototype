import json as _al_json
def _al_check():
    g = globals()
    required = ("priority_district", "increase", "recommended_step")
    if any(g.get(name) is None for name in required):
        return "incomplete"
    try:
        if g["priority_district"] != 'Kambia' or type(g["increase"]) not in (int, float) or g["increase"] != 5:
            return "incorrect"
        if g["recommended_step"] != "verify_reports_and_investigate":
            return "incorrect"
    except (KeyError, TypeError, ValueError):
        return "incorrect"
    return "correct"
print("AL_OBSERVATION " + _al_json.dumps({"outcome": _al_check()}))
del _al_check
