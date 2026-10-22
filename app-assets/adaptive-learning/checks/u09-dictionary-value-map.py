import json as _al_json
from collections import Counter
def summarize(data):
    rows=data['cases']
    return {'district':dict(Counter(r['district'] for r in rows)),
            'onset':dict(sorted(Counter(r['onset_date'] for r in rows).items())),
            'age_group':dict(Counter('under5' if r['age']<data['age_cutoff'] else '5plus' for r in rows)),
            'sex':dict(Counter(r['sex'] for r in rows))}

def supported_claims(data):
    draft=data['draft_counts']
    counts=summarize(data)['district']
    lab_counts=Counter(r['case_id'] for r in data['lab'])
    supports={
        'counts': counts.get(draft['district'],0)==draft['numerator'] and len(data['cases'])==draft['denominator'],
        'risk': False,  # No population risk claim can follow from a report share alone.
        'cause': False, # No causal claim can follow from this descriptive case extract.
        'followup': any(v>1 for v in lab_counts.values())
    }
    return sorted(key for key,value in supports.items() if value)

def age_group(age):
    """Fixed categories for this report; the fifth birthday starts 5plus."""
    if age is None:
        return 'unknown'
    return 'under5' if age < 5 else '5plus'

def expected_answers(unit,data):
    if unit==9: return {'id_type':'text','pending':data['code_map']['PEND'],'unknown':'flag'}
    if unit==10: return {'key':'case_id','relationship':'one_many','flow':'collect_store_view_summary'}
    if unit==11: return {'case_group':age_group(data['cases'][0]['age']),'under5':sum(age_group(r['age'])=='under5' for r in data['cases']),'rows':len(data['cases']),'missing':'retain_unknown'}
    if unit==12:
        counts=Counter(r['case_id'] for r in data['lab'])
        return {'join':'left','conflicts':sum(v>1 for v in counts.values()),'unknown':'quarantine'}
    if unit==13:
        groups=summarize(data)['district']
        return {'kambia':groups.get('Kambia',0),'denominator':'reported_cases','chart':'onset','rate':'unavailable'}
    if unit==14:
        return {'supported':supported_claims(data),
                'risk':'needs_population','release':'human_review'}
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
        elif type(actual) is not type(value) or actual != value:
            return "incorrect"
    return "correct"

print('AL_OBSERVATION '+_al_json.dumps({'outcome':evaluate_answer(9,globals().get('unit09_response'),{'cases': [{'case_id': 'C01', 'district': 'Kambia', 'onset_date': '2021-10-18', 'age': 8, 'sex': 'F'}, {'case_id': 'C02', 'district': 'Kambia', 'onset_date': '2021-10-19', 'age': 12, 'sex': 'M'}, {'case_id': 'C03', 'district': 'Kambia', 'onset_date': '2021-10-20', 'age': 4, 'sex': 'F'}, {'case_id': 'C04', 'district': 'Port Loko', 'onset_date': '2021-10-20', 'age': 17, 'sex': 'M'}], 'lab': [{'case_id': 'C01', 'code': 'P'}, {'case_id': 'C02', 'code': 'PEND'}, {'case_id': 'C02', 'code': 'NEG'}, {'case_id': 'C99', 'code': 'X'}], 'code_map': {'P': 'positive', 'NEG': 'negative', 'PEND': 'pending'}, 'dictionary': [{'field': 'case_id', 'type': 'text', 'required': True, 'meaning': 'Stable case event identifier; preserve leading zeros'}, {'field': 'district', 'type': 'controlled text', 'required': True, 'meaning': 'Reporting district: Kambia or Port Loko'}, {'field': 'onset_date', 'type': 'ISO date', 'required': True, 'meaning': 'First symptom date; not specimen date'}, {'field': 'age', 'type': 'integer years', 'required': True, 'meaning': 'Completed years, 0 to 120'}], 'flows': [{'step': 1, 'location': 'Collection', 'output': 'Case event'}, {'step': 2, 'location': 'District database', 'output': 'Stored case_id'}, {'step': 3, 'location': 'Authorized analyst view', 'output': 'Scoped extract'}, {'step': 4, 'location': 'District summary', 'output': 'Aggregates for the briefing'}], 'age_cutoff': 5, 'draft_counts': {'district': 'Kambia', 'numerator': 3, 'denominator': 4}, 'population': None, 'causal_comparison': None, 'draft': [{'claim': 'counts', 'text': 'Three of four reported cases are from Kambia.'}, {'claim': 'risk', 'text': 'Kambia residents have three times the disease risk of Port Loko residents.'}, {'claim': 'cause', 'text': 'The reporting system caused the difference between districts.'}, {'claim': 'followup', 'text': 'Resolve the conflicting laboratory records before reporting final laboratory status.'}]})}))
