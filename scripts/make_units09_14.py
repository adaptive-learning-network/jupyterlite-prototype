"""Units 9-14: one local computational narrative per topic."""
from __future__ import annotations
import inspect,json
from collections import Counter
from pathlib import Path
import make_units04_08 as shared
from make_units04_08 import ROOT,EX,comic,cell,show_table,exercise_code,evaluate_answer
from reflection_widgets import reflection_code
from local_linking_analysis import linking_cells, analysis_cells

DATA = {
 'cases': [
  {'case_id':'C01','district':'Kambia','onset_date':'2021-10-18','age':8,'sex':'F'},
  {'case_id':'C02','district':'Kambia','onset_date':'2021-10-19','age':12,'sex':'M'},
  {'case_id':'C03','district':'Kambia','onset_date':'2021-10-20','age':4,'sex':'F'},
  {'case_id':'C04','district':'Port Loko','onset_date':'2021-10-20','age':17,'sex':'M'}],
 'lab': [{'case_id':'C01','code':'P'},{'case_id':'C02','code':'PEND'},
         {'case_id':'C02','code':'NEG'},{'case_id':'C99','code':'X'}],
 'code_map': {'P':'positive','NEG':'negative','PEND':'pending'},
 'dictionary': [
  {'field':'case_id','type':'text','required':True,'meaning':'Stable case event identifier; preserve leading zeros'},
  {'field':'district','type':'controlled text','required':True,'meaning':'Reporting district: Kambia or Port Loko'},
  {'field':'onset_date','type':'ISO date','required':True,'meaning':'First symptom date; not specimen date'},
  {'field':'age','type':'integer years','required':True,'meaning':'Completed years, 0 to 120'}],
 'flows': [{'step':1,'location':'Collection','output':'Case event'},
           {'step':2,'location':'District database','output':'Stored case_id'},
           {'step':3,'location':'Authorized analyst view','output':'Scoped extract'},
           {'step':4,'location':'District summary','output':'Aggregates for the briefing'}],
 'age_cutoff':5,
 'draft_counts': {'district':'Kambia','numerator':3,'denominator':4},
 'population': None,
 'causal_comparison': None,
 'draft': [
  {'claim':'counts','text':'Three of four reported cases are from Kambia.'},
  {'claim':'risk','text':'Kambia residents have three times the disease risk of Port Loko residents.'},
  {'claim':'cause','text':'The reporting system caused the difference between districts.'},
  {'claim':'followup','text':'Resolve the conflicting laboratory records before reporting final laboratory status.'}]
}

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

def build_artifact(unit,response,data):
    """Return inspectable outputs; leave original records untouched."""
    if unit==9:
        mapped=[{'source_code':r['code'],'value':data['code_map'].get(r['code']),
                 'action':'mapped' if r['code'] in data['code_map'] else ('review required' if response['unknown']=='flag' else 'UNSAFE: discarded unknown code')}
                for r in data['lab']]
        return {'Field dictionary':data['dictionary'],'Value reconciliation':mapped}
    if unit==10:
        keys=Counter(r[response['key']] for r in data['cases'])
        return {'Key audit':[{'candidate':response['key'],'distinct':len(keys),'rows':len(data['cases']),
                              'unique':all(v==1 for v in keys.values())}],
                'Record flow':data['flows'] if response['flow']=='collect_store_view_summary' else list(reversed(data['flows']))}
    if unit==11:
        output=[]
        for row in data['cases']:
            copy=dict(row)
            copy['age_group']=age_group(row['age'])
            output.append(copy)
        before=Counter(r['case_id'] for r in data['cases']);after=Counter(r['case_id'] for r in output)
        return {'Transformed copy':output,'Reconciliation':[{'input_rows':len(data['cases']),'output_rows':len(output),
                  'same_ID_multiplicity':before==after,'under5':sum(r['age_group']=='under5' for r in output)}]}
    if unit==12:
        index={}
        for row in data['lab']: index.setdefault(row['case_id'],[]).append(row)
        linked=[];review=[]
        for row in data['cases']:
            matches=index.get(row['case_id'],[])
            if not matches and response['join']=='inner': continue
            code=matches[0]['code'] if len(matches)==1 else None
            status='conflict' if len(matches)>1 else ('unmatched' if not matches else data['code_map'].get(code,'unmapped'))
            linked.append({**row,'result':status})
        case_ids={r['case_id'] for r in data['cases']}
        for row in data['lab']:
            errors=[]
            if row['case_id'] not in case_ids: errors.append('unknown case identifier')
            if len(index[row['case_id']])>1: errors.append('conflicting results; verify source')
            if row['code'] not in data['code_map']: errors.append('unmapped result code')
            review.append({**row,'accepted':not errors,'review':'; '.join(errors)})
        # Only resolved, mapped records enter the candidate exchange table. No network POST.
        payload=[{'case_id':r['case_id'],'result':data['code_map'][r['code']],'source':'training-lab'}
                 for r in data['lab'] if len(index[r['case_id']])==1 and r['case_id'] in case_ids and r['code'] in data['code_map']]
        return {'Linked case view':linked,'Import validation':review,'Candidate exchange rows':payload}
    if unit==13:
        summary=summarize(data);total=len(data['cases'])
        table=[{'district':k,'reported_cases':v,'share_of_reports':round(v/total,3) if total else None,'population_rate':'unavailable: no population denominator'} for k,v in summary['district'].items()]
        return {'District briefing':table,'Person summary':[{'dimension':kind,'category':k,'count':v} for kind in ['age_group','sex'] for k,v in summary[kind].items()],
                'Time summary':[{'onset_date':k,'cases':v} for k,v in summary['onset'].items()]}
    if unit==14:
        total=len(data['cases']);counts=summarize(data)['district']
        return {'Draft review':[{'claim':r['text'],'your_decision':'supported' if r['claim'] in response['supported'] else 'not supported'} for r in data['draft']],
                'Evidence for the briefing':[{'measure':'Reported cases','value':total},
                     {'measure':'Kambia share of reports','value':counts.get('Kambia',0)/total if total else None},
                     {'measure':'Population denominator','value':'Not supplied'},
                     {'measure':'Causal comparison','value':'Not supplied'}]}
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

from html import escape
# Notebook runtime supplies widgets/display; native tests inject a chart sink.

UNITS=[]
def spec(unit,slug,title,objective,controls,lesson,reflection,cue,visual,reference,hints):
    UNITS.append(dict(unit=unit,slug=slug,title=title,objective=objective,controls=controls,lesson=lesson,
      reflection=reflection,cue=cue,visual=visual,references=reference,hints=hints,slide=None))
C=lambda key,label,options:(key,label,'choice',options)
N=lambda key,label:(key,label,'integer',None)

spec(9,'dictionary-value-map','Give every field and code a meaning','Select field meanings and a code-mapping policy.',[
 C('id_type','Case identifier type',[('Text (preserve leading zeros)','text'),('Whole number','integer')]),
 C('pending','Meaning of PEND',[('Pending result','pending'),('Negative result','negative')]),
 C('unknown','Action for unmapped code X',[('Flag for source review','flag'),('Discard silently','drop')])],
 '''## Two systems, one question
Laila finds `P`, `NEG`, and `PEND` in the laboratory file. A data dictionary records each field's meaning, type, allowed values, and required status. A value map connects source codes to shared meanings.

**Training contract:** `P` means positive, `NEG` negative, and `PEND` pending. `X` has no agreed meaning. A case identifier is text; `0012` must retain its leading zeros. Unknown codes require review, not a guessed result.

Inspect the dictionary and source records below. Choose field semantics and a mapping policy, then inspect the generated reconciliation table.''',
 ['How would you confirm an unfamiliar code with the laboratory?','Which dictionary change would require a version and communication to other systems?'],
 [('Laila','Does PEND mean negative?'),('Laboratory','No. The result is still pending.'),('Laila','A shared dictionary keeps a missing answer from becoming a false answer.')],
 ('../../readings/ucsf/assets/slide-previews/unit-2-056.jpg','Course dictionary example; Unit 2 Version 2 slide 56'),
 'Public Health Informatics for FETP, Version 2 Unit 2, slides 56–58 (dictionary); Unit 5 terminology sections. UCSF Unit 9 topic wrapper and Unit 2.1 variable-selection assignment.',
 ['A pending test has not produced a final result.','Identifiers are labels, even when they contain only digits.','Unmapped codes remain visible for review.'])
spec(10,'table-design-data-flow','Follow a case through linked tables','Select keys and relationships for linked tables.',[
 C('key','Case table primary key',[('case_id','case_id'),('district','district')]),
 C('relationship','Case to laboratory relationship',[('One case to many laboratory records','one_many'),('One district to one case','one_one')]),
 C('flow','Data flow',[('Collect → store → authorized view → summary','collect_store_view_summary'),('Summary → view → store → collect','reverse')])],
 '''## Storage is a design decision
A primary key identifies a row uniquely. A foreign key connects a laboratory record to its case. A district name repeats and cannot identify a case. More than one laboratory record may refer to the same case; a laboratory table needs its own record identifier as well as `case_id`.

The course asks learners to map how data move through the HIS. Trace this pathway: **collection → district database → authorized analyst view → district summary**. A summary is an output, not a replacement for the event records. The browser DHIS2 adapter fits at the authorized-view boundary; this exercise stays in local tables.

Choose a case key, relationship, and flow. The key audit reveals what happens when a repeated field is treated as unique.''',
 ['Where could a delayed report change the district summary?','Why should laboratory records have their own identifier as well as case_id?'],
 [('Laila','Can district identify each case?'),('Martha','Several cases share the same district.'),('Laila','I need a case key and a clear path from the register to my summary.')],
 ('../../readings/ucsf/assets/his_context.png','Course health information system context'),
 'Public Health Informatics for FETP, Version 2 Unit 5 storage and data-flow sections; UCSF Unit 10 topic wrapper and Unit 5 Assignment 2 (data transmission map).',
 ['Count distinct values before choosing a key.','One case may have several specimens or laboratory updates.','Collection precedes storage and access.'])
spec(11,'recode-reconcile','Transform a copy without losing cases','Evaluate a recoded table against the supplied case records.',[
 C('case_group','Age group for case C01',[('Under 5 years','under5'),('5 years or older','5plus'),('Unknown age','unknown')]),
 N('under5','Number of cases younger than 5'),N('rows','Rows after adding age groups'),
 C('missing','If a case has no recorded age',[('Retain case with unknown age group','retain_unknown'),('Drop the case','drop')])],
 '''## Group the supplied cases by age

Laila needs to separate cases younger than five years from cases aged five years
or older. The invented case records for this task are provided here:

{{case_rows}}

Age is recorded in completed years. Add an age group to each case using these rules:

- `under5`: age is less than 5.
- `5plus`: age is 5 or older.
- `unknown`: age is missing. Keep the case in the table.

The age-group definitions are fixed for this report. An eight-year-old belongs
in `5plus`. A case aged exactly five years also belongs in `5plus`.

1. Run the visible worked example below. It shows the groups for ages 4, 5, 8,
   and a missing age. These examples explain the rule; they are not additional cases.
2. Inspect the four supplied case records. Decide which group C01 belongs to,
   how many cases are younger than five, and how many rows should remain after
   adding the age groups. Also choose what should happen if an age is missing.
3. Run the controls cell after the worked example and enter your answers.
4. Select **Submit**. The notebook creates and displays a recoded copy using
   the fixed definitions above, then gives feedback on your answers.
5. Compare the recoded table with the supplied records. Check that every case
   identifier is still present and appears the same number of times. Matching
   row counts alone would not show whether one case had been replaced by another.

The supplied records stay unchanged. Your answers are predictions and review
judgments; they do not change the age-group definitions or remove cases.
''',
 ['What additional checks would detect a case replaced by another case?','How would you record a change to the age-group definition?'],
 [('Laila','My code runs. Is that enough?'),('Supervisor','Did the same cases survive?'),('Laila','I will compare identifiers, counts, and the meaning of every new group.')],
 ('../../readings/ucsf/assets/slide-previews/unit-2-056.jpg','Course dictionary example; use field meaning when recoding'),
 'Public Health Informatics for FETP, Version 2 Unit 5 transformation/preparation sections; UCSF Unit 11 topic wrapper and Unit 5 cleaning assignment.',
 ['Under five excludes the fifth birthday.','Count the case identifiers in the table supplied in this notebook.','A missing age does not mean no case.'])
spec(12,'link-exchange','Link records before an exchange','Analyze matched, unmatched, and conflicting case keys.',[
 C('join','Join for a complete case view',[('Keep every case (left join)','left'),('Keep matched cases only (inner join)','inner')]),
 N('conflicts','Number of case keys with multiple lab rows'),
 C('unknown','Import policy for invalid or conflicting rows',[('Quarantine for review','quarantine'),('Send all rows','send')])],
 '''## Link the supplied case and laboratory records

Laila has four case records and a laboratory table. Both are included in this
notebook; run the cells below to inspect and link them. The case table contains
`case_id`, district, onset date, age, and recorded sex. The laboratory table
contains `case_id` and a result code.

Linking adds laboratory information as **columns** beside the matching case.
Appending laboratory rows to the case table would not do that. Adding **rows**
is appropriate when combining separate case records with the same fields.
Before linking, check that the identifier has the same meaning and format in
both data sources, inspect missing or repeated identifiers, and check the result codes.

In these records, C02 has two different laboratory results. C99 appears only
in the laboratory table and has an undefined result code. C03 and C04 have no
laboratory row. The worked example shows why a direct match can create extra
rows, then checks the laboratory records before producing a case table and
rows ready for a possible exchange. Unresolved records stay visible for review.
**No matching laboratory record does not mean a negative test.**

Run the examples in order, then use the review controls and reflection fields.
All records stay in this browser; nothing is sent to another system.''',
 ['Which laboratory rows need follow-up, and what would you verify before assigning a final result?',
  'Which checks show that linking kept every case without adding extra copies?',
  'What would you check before sharing the accepted laboratory rows with another system?'],
 [('Laila','Two results match the same case.'),('Laboratory','They disagree. Please verify the source.'),('Laila','I will keep unmatched cases visible and block unresolved rows from exchange.')],
 ('../../readings/ucsf/assets/match_rows.png','Course matching notification and clinical rows'),
 'UCSF FETP JupyterBook, Unit 2.3 compilation/analysis and Assignment 5; Unit 12 topic wrapper. Version 2 Units 2 and 5, record matching and exchange.',
 ['A left join retains cases without a match.','Count lab rows by case identifier before joining.','Validate identifiers, cardinality, codes, and provenance before exchange.'])
spec(13,'analysis-dashboard','Build a district briefing from the records','Interpret supplied person, place, and time summaries.',[
 N('kambia','Kambia reported case count'),
 C('denominator','Denominator for share of reports',[('All reported cases in this extract','reported_cases'),('District population (not supplied)','population')]),
 C('chart','Chart for the timing of illness',[('Cases by onset date','onset'),('Cases by district','district')]),
 C('rate','Population disease rate',[('Unavailable without population and time at risk','unavailable'),('Use the share of reports as the rate','share')])],
 '''## Describe the supplied cases with tables and Seaborn charts

Laila needs a briefing describing **who is affected, where cases were reported,
and when illness began**. This notebook supplies four invented case records
from Kambia and Port Loko, with onset dates from 18 to 20 October 2021.
Run the cells below to inspect the records, calculate summaries, and draw
Seaborn charts of age group, recorded sex, district, and illness-onset day.

For this briefing, choose **reported case count** as the measure, the dates
covered by this extract as the period, and the two reporting districts as the
geographic units. Each table and chart should name its measure and scope.
A count, a share of reports, and a population disease rate answer different
questions. A share uses the total number of supplied cases as its denominator.
A population rate requires additional population and time information.

The extract has no death, vaccination, household-location, or notification-date
fields, and it does not cover twelve months. It cannot support death summaries,
vaccination percentages, household maps, notification-delay markers, or a
population incidence calculation. An outbreak assessment would also require
an appropriate baseline and threshold definition.

After running the summaries and charts, answer the review questions and record
a short briefing under **finding, evidence, limitations, and recommended action**.''',
 ['Finding: describe who, where, and when using the supplied case counts.',
  'Evidence: which table and Seaborn chart support your finding?',
  'Limitations: what information would you need before drawing conclusions about disease risk or an outbreak?',
  'Recommended action: what should the district team verify next, and who should follow up?'],
 [('Laila','Kambia has more reports.'),('Supervisor','Does that mean higher disease risk?'),('Laila','I can show counts and timing. A risk comparison needs population evidence.')],
 ('../../readings/ucsf/assets/laila_analyze.png','Course Laila analysis cue'),
 'UCSF FETP JupyterBook, Unit 6 Assignment 2 (tables/graphs/maps; Data, Period, Organization Unit), Unit 2.3 analysis, and Units 13–14 topic wrappers. Version 2 Unit 6 analysis and visualization.',
 ['Count the cases for each district.','A share uses the total number of reports as its denominator.','Onset dates answer the timing question; population rates need another denominator.'])
spec(14,'interpret-with-ai','Challenge an AI-assisted briefing','Critique a supplied interpretation against case evidence.',[
 ('supported','Claims supported by this extract','multi',[(label,row['claim']) for label,row in zip(['Claim 1: share of reports','Claim 2: population risk','Claim 3: reporting caused difference','Claim 4: laboratory follow-up'], DATA['draft'])]),
 C('risk','Evidence needed for a risk comparison',[('Population denominators and comparable ascertainment','needs_population'),('More confident wording','confidence')]),
 C('release','Decision before sharing',[('Human review with limitations and AI disclosure','human_review'),('Publish the draft unchanged','publish')])],
 '''## The draft is an aid, not the evidence
Laila has the same four-case extract and the briefing from Unit 13. Below is a supplied AI-style draft, not a live model response. Two statements describe the available evidence; two go beyond it.

A share of reports is not a relative population risk. The extract has no population denominator, comparison design, or evidence that the reporting system caused a disease difference. Laboratory conflicts still require follow-up. Reporting completeness, access to care, and selection into the extract may differ between districts.

Select every supported claim. Then choose what the risk comparison needs and who reviews the briefing before release. Keep the final message proportionate to the evidence, acknowledge uncertainty, and disclose AI assistance. Do not put identifiable health records into an unapproved AI service.''',
 ['Write a two-sentence briefing with a count, a limitation, and a follow-up action.','What would you disclose about AI assistance and human responsibility?'],
 [('Laila','The draft sounds certain about risk.'),('Supervisor','Show me its denominator and evidence.'),('Laila','I will keep supported counts, remove causal overclaims, and document the review.')],
 ('../../readings/ucsf/assets/laila_analyze.png','Course Laila interpretation context'),
 'Public Health Informatics for FETP, Version 2 Unit 7 interpretation context (not an AI deck); UCSF Unit 15 topic wrapper. Synthetic draft and computed case evidence for this practice task.',
 ['Three of four reports is a share, not a population risk ratio.','No causal comparison is supplied.','A supported follow-up action can address unresolved data rather than claim an explanation.'])

def setup_code(spec):
    preview="show_table(training_data['cases'])\n"
    if spec['unit'] in (9,12):preview+="show_table(training_data['lab'])\nprint('Code map:',training_data['code_map'])\n"
    if spec['unit']==9:preview+="show_table(training_data['dictionary'])\n"
    if spec['unit']==10:preview+="show_table(training_data['flows'])\n"
    if spec['unit']==14:preview+="show_table(training_data['draft'])\n"
    return shared.setup_code(spec, data=DATA,
        helpers=[show_table,summarize,supported_claims,age_group,expected_answers,evaluate_answer,build_artifact], preview=preview)


def age_group_example_code():
    return '# Run this worked example: apply the fixed age groups.\n' + inspect.getsource(age_group) + '''
# Boundary and missing-age examples, separate from the four case records.
example_ages = [4, 5, 8, None]
for example_age in example_ages:
    example_label = "Missing" if example_age is None else example_age
    print(f"Age {example_label}: {age_group(example_age)}")
'''


def main():
    for s in UNITS:comic(s)
    if any(not (ROOT/'content/exercises/assets'/comic(s)).exists() for s in UNITS):
        raise SystemExit('Render comic PNGs with scripts/render_course_comics.cjs, then rerun.')
    scenarios=[]
    for i,s in enumerate(UNITS):
        u=s['unit'];ident=f"u{u:02d}-{s['slug']}";filename=f"u{u:02d}-n01-{s['slug']}.ipynb"
        lesson=s['lesson']
        if u==11:
            # Use the same records as the runnable exercise; no separate file or
            # Python execution is needed to inspect the inputs.
            rows='| Case identifier | District | Onset date | Age (completed years) | Sex |\n| --- | --- | --- | --- | --- |\n'
            rows+='\n'.join(f"| {r['case_id']} | {r['district']} | {r['onset_date']} | {r['age'] if r['age'] is not None else 'Missing'} | {r['sex']} |" for r in DATA['cases'])
            lesson=lesson.replace('{{case_rows}}',rows)
        intro=f"**Unit {u:02d} · Notebook 01**\n\n# {s['title']}\n\n**Learning objective:** {s['objective']}\n\n![Laila's decision](../assets/{comic(s)})\n\nAll records in this exercise are invented.\n\n{lesson}\n\n![{s['visual'][1]}]({s['visual'][0]})\n\n*{s['visual'][1]}.*\n"
        nextfile=f"u{u+1:02d}-n01-{UNITS[i+1]['slug']}.ipynb" if i+1<len(UNITS) else 'u03-n08-my-learning-record.ipynb'
        meta={'al':{'activity':EX+'act-'+ident,'object':EX+'act-'+ident+'-exercise','check':'checks/'+ident,'hints':s['hints'],'submission':'widget'},'tags':['al-exercise'],'jupyter':{'source_hidden':True}}
        exercise=exercise_code(s)
        if u==11:
            exercise=exercise.replace('Correct: your result follows the stated evidence and training rules.',
                'Correct: your age-group review and row count match the supplied cases; cases with missing ages should be retained.')
            exercise=exercise.replace('Not yet correct: compare the artifact with the task and rules. Revise your choices and retry; the Learning panel offers hints.',
                'Not yet correct: compare your answers with the age groups and case identifiers in the displayed table. Review the missing-age rule, then try again.')
        cells=[cell('markdown',intro,'0'),cell('code',setup_code(s),'1',{'jupyter':{'source_hidden':True}}),
          cell('markdown','## Submit your decision\n\nRun the next cell to display **Submit**, then select the button for feedback. Only an explicit submission records an attempt. Revise your choices and submit again to retry.','check-instructions'),
          cell('code',exercise,'2',meta),
          cell('markdown','## Reflect on the decision\n\nRun the next cell. Write your reflections, then select **Record** to save them with your learner record in this browser. Reflections are unscored.','3'),
          cell('code',reflection_code('exercise:'+ident,s['reflection']),'reflection-fields',{'jupyter':{'source_hidden':True}}),
          cell('markdown',f"## Continue learning\n\n[{'Next notebook' if u<14 else 'Review your learning record'}]({nextfile}) · [Course start](u00-n00-start-here.ipynb)\n\nReview attempts, hints, and recommendations in the **Learning** panel.",'continue')]
        if u==12:
            cells[1:1]=linking_cells(cell,DATA)
        if u==13:
            cells[1:1]=analysis_cells(cell,DATA)
        if u==11:
            cells[1:1]=[
                cell('markdown','## Apply the fixed age groups\n\nSelect the code cell below and press **Shift+Enter**. Compare the groups for a four-year-old, a five-year-old, an eight-year-old, and a missing age. This worked example is unscored and runs without the setup cell.\n\nThen use the controls cell that follows to answer the review questions about the four supplied cases.','age-group-example-intro'),
                cell('code',age_group_example_code(),'age-group-example')]
        doc={'cells':cells,'metadata':{'title':s['title'],'generatedBy':'scripts/make_units09_14.py','kernelspec':{'name':'python','display_name':'Python (Pyodide)','language':'python'},'language_info':{'name':'python'},'al':{'activity':EX+'act-'+ident,'language':'python'}},'nbformat':4,'nbformat_minor':5}
        (ROOT/'content/exercises/python'/filename).write_text(json.dumps(doc,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
        check='import json as _al_json\nfrom collections import Counter\n'+inspect.getsource(summarize)+'\n'+inspect.getsource(supported_claims)+'\n'+inspect.getsource(age_group)+'\n'+inspect.getsource(expected_answers)+'\n'+inspect.getsource(evaluate_answer)
        check+=f"\nprint('AL_OBSERVATION '+_al_json.dumps({{'outcome':evaluate_answer({u},globals().get('unit{u:02d}_response'),{DATA!r})}}))\n"
        (ROOT/'app-assets/adaptive-learning/checks'/f'{ident}.py').write_text(check,encoding='utf-8')
        scenarios.append({'unit':u,'id':ident,'path':'notebooks/'+filename,'controls':[dict(key=k,label=l,kind=t,options=o) for k,l,t,o in s['controls']],'correct':expected_answers(u,DATA),'reflectionCount':len(s['reflection'])})
    (ROOT/'test/fixtures/units09-14-scenarios.json').write_text(json.dumps(scenarios,indent=2)+'\n',encoding='utf-8')
    print('Generated six Python narratives and adaptive checks: Units 9-14')
if __name__=='__main__':main()
