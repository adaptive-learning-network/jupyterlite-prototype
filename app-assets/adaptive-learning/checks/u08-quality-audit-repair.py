import json as _al_json
from collections import Counter
from datetime import date
def expected_answers(unit, data):
    """Recompute training expectations from source coverage and explicit rules."""
    if unit == 4:
        # Each selected source must add a required field; the aggregate lacks case IDs.
        required = set(data["required_fields"])
        selected = [s["id"] for s in data["sources"] if s["grain"] == "case" and required & set(s["fields"])]
        return {"sources": selected, "grain": "case"}
    if unit == 5:
        counts = Counter(row["district"] for row in data["cases"])
        return {"fields": sorted(set(data["task_fields"]) & set(data["role_fields"])),
                "suppress": sorted(k for k, v in counts.items() if v < data["release_minimum"])}
    if unit == 6:
        total = len(data["cases"])
        positive = sum(row["result"] == "positive" for row in data["lab"])
        # Claims 1 and 2 are numeric, claim 3 asserts causation without supporting evidence.
        claimed = {"all_positive": positive == total, "no_followup": all(row["result"] != "pending" for row in data["lab"])
                   and len(data["lab"]) == total, "water_caused": False}
        return {"claims": sorted(k for k, supported in claimed.items() if not supported), "review": "human_review"}
    if unit == 7:
        return {"required": data["form"]["required"], "age_max": data["form"]["age_max"],
                "district_control": "list"}
    if unit == 8:
        rows = data["dirty"]
        ids = Counter(row["case_id"] for row in rows)
        return {"missing": sum(not row["district"] for row in rows),
                "duplicates": sum(v - 1 for v in ids.values()),
                "invalid": sum(not data["form"]["age_min"] <= row["age"] <= data["form"]["age_max"] for row in rows),
                "late": sum((date.fromisoformat(row["report_date"]) - date.fromisoformat(row["onset_date"])).days > data["timely_days"] for row in rows),
                "repair": "verify_and_log"}
    raise ValueError(unit)

def evaluate_answer(unit, response, data):
    expected = expected_answers(unit, data)
    if not isinstance(response, dict) or any(response.get(k) is None or response.get(k) == [] for k in expected):
        return "incomplete"
    for key, value in expected.items():
        actual = response.get(key)
        if isinstance(value, list):
            if not isinstance(actual, (list, tuple)) or sorted(actual) != sorted(value):
                return "incorrect"
        elif actual != value:
            return "incorrect"
    return "correct"

print('AL_OBSERVATION ' + _al_json.dumps({'outcome': evaluate_answer(8, globals().get('unit08_response'), {'sources': [{'id': 'case', 'grain': 'case', 'fields': ['case_id', 'district', 'onset_date', 'age'], 'access': 'district analyst'}, {'id': 'lab', 'grain': 'case', 'fields': ['case_id', 'specimen_date', 'result'], 'access': 'authorized laboratory extract'}, {'id': 'weekly', 'grain': 'district-week', 'fields': ['district', 'week', 'count'], 'access': 'public summary'}], 'required_fields': ['case_id', 'district', 'onset_date', 'result'], 'cases': [{'case_id': 'C01', 'district': 'Kambia', 'onset_date': '2021-10-18', 'age': 8, 'contact_label': 'Training contact A'}, {'case_id': 'C02', 'district': 'Kambia', 'onset_date': '2021-10-19', 'age': 12, 'contact_label': 'Training contact B'}, {'case_id': 'C03', 'district': 'Kambia', 'onset_date': '2021-10-20', 'age': 4, 'contact_label': 'Training contact C'}, {'case_id': 'C04', 'district': 'Port Loko', 'onset_date': '2021-10-20', 'age': 17, 'contact_label': 'Training contact D'}], 'lab': [{'case_id': 'C01', 'specimen_date': '2021-10-21', 'result': 'positive'}, {'case_id': 'C02', 'specimen_date': '2021-10-22', 'result': 'pending'}], 'role_fields': ['case_id', 'district', 'onset_date', 'age'], 'task_fields': ['case_id', 'district', 'onset_date'], 'release_minimum': 3, 'form': {'required': ['case_id', 'district', 'age'], 'age_min': 0, 'age_max': 120, 'districts': ['Kambia', 'Port Loko']}, 'submissions': [{'case_id': 'T01', 'district': 'Kambia', 'age': 8}, {'case_id': '', 'district': 'Kambia', 'age': 8}, {'case_id': 'T03', 'district': 'Kambia', 'age': 180}, {'case_id': 'T04', 'district': 'Other', 'age': 8}, {'case_id': 'T05', 'district': '', 'age': 8}, {'case_id': 'T06', 'district': 'Kambia', 'age': None}], 'dirty': [{'case_id': 'Q01', 'district': 'Kambia', 'age': 8, 'onset_date': '2021-10-18', 'report_date': '2021-10-19'}, {'case_id': 'Q01', 'district': 'Kambia', 'age': 8, 'onset_date': '2021-10-18', 'report_date': '2021-10-19'}, {'case_id': 'Q02', 'district': '', 'age': 12, 'onset_date': '2021-10-19', 'report_date': '2021-10-20'}, {'case_id': 'Q03', 'district': 'Port Loko', 'age': 180, 'onset_date': '2021-10-20', 'report_date': '2021-10-21'}, {'case_id': 'Q04', 'district': 'Kambia', 'age': 4, 'onset_date': '2021-10-18', 'report_date': '2021-10-25'}], 'timely_days': 2, 'verified_corrections': [{'case_id': 'Q02', 'field': 'district', 'value': 'Port Loko', 'evidence': 'Training register review: district confirmed'}, {'case_id': 'Q03', 'field': 'age', 'value': 18, 'evidence': 'Training register review: age confirmed as 18 years'}], 'verified_duplicate': {'case_id': 'Q01', 'evidence': 'Training source review: these identical rows are the same report'}})}))
