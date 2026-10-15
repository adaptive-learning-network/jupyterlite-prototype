import json as _al_json

def _al_check():
    candidate = globals().get("system_map")
    if not isinstance(candidate, dict) or not candidate.get("case_moves") or not candidate.get("lab_moves"):
        return "incomplete"
    if candidate.get("case") != ['Electronic patient records', 'Electronic case alerts and reports', 'District health information system', 'Ministry of Health'] or candidate.get("lab") != ['Electronic laboratory records', 'Electronic laboratory reports', 'District health information system', 'Ministry of Health']:
        return "incorrect"
    return "correct"

print("AL_OBSERVATION " + _al_json.dumps({"outcome": _al_check()}))
del _al_check
