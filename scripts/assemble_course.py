"""Assemble one learner notebook sequence from course exercises and teaching sources.

Authoring inputs stay in content/. Only .course-content/ is published.
"""
from __future__ import annotations
import copy,json,re,shutil,textwrap
from pathlib import Path
from reflection_widgets import reflection_code
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'content'
OUTPUT=ROOT/'.course-content'
READINGS=SOURCE/'readings/ucsf'
TARGETS={
'u00-n01-reading-index':'u00-n00-start-here',
'u01-n01-slides':'u01-n01-data-to-decision',
'u01-n02-lesson':'u01-n01-data-to-decision',
'u01-n03-knowledge-check':'u01-n01-data-to-decision',
'u02-n01-slides':'u02-n01-system-map',
'u02-n02-knowledge-check':'u02-n01-system-map',
'u02-n03-his-context':'u02-n01-system-map',
'u02-n04-case-study':'u02-n01-system-map',
'u02-n05-group-work':'u02-n01-system-map',
'u02-n06-assignment-1':'u02-n01-system-map',
'u02-n07-explore-datasets':'u03-n02-explore-dataset',
'u02-n08-assignment-2':'u03-n02-explore-dataset',
'u02-n09-assignment-3':'u09-n01-dictionary-value-map',
'u02-n10-data-quality':'u08-n01-quality-audit-repair',
'u02-n11-assignment-4':'u08-n01-quality-audit-repair',
'u02-n12-compile-analyze':'u12-n01-link-exchange',
'u02-n13-analyze-visualize':'u13-n01-analysis-dashboard',
'u02-n14-assignment-5':'u12-n01-link-exchange',
'u02-n15-assignment-6':'u13-n01-analysis-dashboard',
}
# Explanations become part of the same opening narrative. Prompts and quizzes
# follow the core task; slides remain collapsible in the relevant unit.
LESSONS={'u01-n02-lesson','u02-n03-his-context','u02-n04-case-study','u02-n07-explore-datasets','u02-n10-data-quality','u02-n12-compile-analyze','u02-n13-analyze-visualize'}
ASSIGNMENTS={'u02-n05-group-work','u02-n06-assignment-1','u02-n08-assignment-2','u02-n09-assignment-3','u02-n11-assignment-4','u02-n14-assignment-5','u02-n15-assignment-6'}

# Questions are authored against the destination's displayed data, never parsed
# from procedural bullets. Source assignments remain traceable in the inventory.
REFLECTIONS = {
 'u01-n01-data-to-decision': ('exercise:u01-n01', [
  'Which district change supports your chosen action, and what should be verified before calling it an outbreak?']),
 'u02-n01-system-map': ('exercise:u02-n01', [
  'Which case and laboratory records would Laila need for the measles summary, and which systems hold them?',
  'Who needs the case and laboratory reports at the district level?',
  'What access question would you verify before obtaining these records?',
  'If facility or community reports arrive late, which district responsibility is affected and what would you verify?']),
 'u03-n02-explore-dataset': ('integrated:u02-n08-assignment-2', [
  'How many vaccination records are in register, and which vaccination dates and locations does it cover?',
  'What do the youngest and oldest recorded ages tell you about the population represented?',
  'What would you check before using this register to answer a question about vaccination coverage?']),
 'u08-n01-quality-audit-repair': ('exercise:u08-quality-audit-repair', [
  'Which rows in the displayed incoming extract have missing, duplicate, invalid, or late values?',
  'Which supplied source confirmations justify the corrections, and what should the correction log retain?',
  'Why does the late report remain late after correcting its values?']),
 'u09-n01-dictionary-value-map': ('exercise:u09-dictionary-value-map', [
  'Why should the case identifier be text, and what could happen to 0012 if treated as a number?',
  'How does the supplied dictionary explain P, NEG, and PEND, and why must X remain unresolved?']),
}

SEQUENCE = [
 'u00-n00-start-here','u01-n01-data-to-decision','u02-n01-system-map',
 'u03-n01-data-or-information','u03-n02-explore-dataset','u03-n03-filter-records',
 'u03-n04-coverage','u03-n05-machine-readable','u03-n06-case-or-aggregate',
 'u03-n07-dhis2-query','u03-n08-my-learning-record','u04-n01-source-inventory',
 'u05-n01-access-and-safe-release','u06-n01-ai-use-and-review','u07-n01-form-design-validation',
 'u08-n01-quality-audit-repair','u09-n01-dictionary-value-map','u10-n01-table-design-data-flow',
 'u11-n01-recode-reconcile','u12-n01-link-exchange','u13-n01-analysis-dashboard','u14-n01-interpret-with-ai']

def text(cell):return ''.join(cell['source'])
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def markdown(source,ident):return {'cell_type':'markdown','id':ident,'metadata':{},'source':source.splitlines(keepends=True)}
def transform(source,language='python',reading=False):
    asset='assets/' if language=='python' else '../assets/'
    source=source.replace('`exercises/python`','`notebooks`')
    if reading:source=re.sub(r'(?<![/\w-])assets/',asset,source)
    # Explicit PDF preview links are browser URLs, rather than contents paths.
    source=source.replace('../files/readings/ucsf/assets/',asset)
    source=source.replace('../../readings/ucsf/assets/',asset)
    source=source.replace('../assets/',asset) if language=='python' else source
    # Rebase every link to a former reading into its destination narrative.
    def notebook_link(match):
        label,path=match.group(1),match.group(2)
        stem=Path(path).stem
        if stem=='u00-n02-version3-form-library':stem='u01-n01-data-to-decision'
        elif stem in TARGETS:stem=TARGETS[stem]
        if stem.startswith('u'):
            prefix='' if language=='python' or (SOURCE/'exercises/r'/(stem+'.ipynb')).exists() else '../'
            return '['+label+']('+prefix+stem+'.ipynb)'
        return match.group(0)
    return re.sub(r'\[([^\]]+)\]\(([^)]+\.ipynb)\)',notebook_link,source)

def clean_lesson(source):
    # The destination already has one course cue and one assessed objective.
    lines=source.splitlines();out=[];skip=False
    for line in lines:
        if re.match(r'^#{1,6} .*Learning Objectives',line):skip=True;continue
        if skip and (line.startswith('#') or line=='---'):skip=False
        if skip:continue
        if re.match(r'^#{1,6} .*Unit Slides',line):skip=True;continue
        if re.match(r'^# ',line):line='## '+line[2:]
        if line.strip()=='---':continue
        out.append(line)
    return '\n'.join(out).strip()

def prompts(source):
    result=[]
    current=None
    for line in source.splitlines():
        match=re.match(r'^\s*(?:\d+[.)]|[-*])\s+(.*)',line)
        if match:
            if current:result.append(current.strip())
            current=match.group(1).strip()
        elif not line.strip() or line.lstrip().startswith('#'):
            if current:result.append(current.strip());current=None
        elif current is not None:
            current+=' '+line.strip()
    if current:result.append(current.strip())
    return result or ['What decision would you make in this situation, and why?']


def validate(folder):
    for p in folder.rglob('*.ipynb'):
        doc=read(p);ids=[c['id'] for c in doc['cells']]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate cell ID: '+str(p))
        if not text(doc['cells'][-1]).startswith('## References'):raise ValueError('Missing final References: '+str(p))
        for c in doc['cells']:
            if c['cell_type']!='markdown':continue
            s=text(c)
            if re.search(r'(?:exercises|readings)/',s):raise ValueError('Retired learner path remains: '+str(p))
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',s):
                if target.startswith(('http:','https:','attachment:','#')):continue
                if target.startswith('../files/'):raise ValueError('Use contents-relative PDF links: '+target)
                clean=target.split('#')[0]
                if clean and not (p.parent/clean).is_file():raise ValueError(f'Missing local dependency: {p.name}: {target}')
        if not re.fullmatch(r'u\d{2}-n\d{2}-.+\.ipynb',p.name):raise ValueError('Invalid notebook name: '+p.name)

def main():
    output=OUTPUT.resolve()
    if output.parent!=ROOT.resolve() or output.name!='.course-content':raise ValueError('Unexpected assembly path')
    # This generated directory is dedicated to course assembly.
    for old in output.rglob('*.ipynb') if output.exists() else []:old.unlink()
    course=output/'notebooks';course.mkdir(parents=True,exist_ok=True)
    shutil.copytree(SOURCE/'exercises/assets',course/'assets',dirs_exist_ok=True)
    shutil.copytree(READINGS/'assets',course/'assets',dirs_exist_ok=True)
    docs={p.stem:read(p) for p in (SOURCE/'exercises/python').glob('*.ipynb')}
    added={name:[] for name in docs};coverage=[]
    for src,dest in TARGETS.items():
        doc=read(READINGS/(src+'.ipynb'));target=docs[dest]
        if src in {'u02-n12-compile-analyze','u02-n14-assignment-5','u02-n13-analyze-visualize','u02-n15-assignment-6'}:
            # These topics are now reimagined in the canonical narrative. Keep
            # source coverage, not a second Excel workflow or extra dataset.
            detail=('supplied case/laboratory tables, matching checks, validated link, and Record reflections'
                    if dest.startswith('u12-') else
                    'supplied records, descriptive statistics, Seaborn person/place/time charts, explicit data limitations, and structured Record briefing')
            coverage.append({'source':src,'destination':dest,'integration':detail})
        elif src == 'u02-n07-explore-datasets':
            coverage.append({'source':src,'destination':dest,'integration':'exploration concepts adapted to the supplied immunization register and authored Record questions; no separate Excel task'})
        elif src in LESSONS:
            if src == 'u01-n02-lesson':
                target['cells'][0]['source'] += ['\n\nPublic health informatics applies information and computer science to collecting, managing, analyzing, and using public health data. A pattern can suggest a question to investigate; it does not establish why disease occurred.\n']
                added[dest].append(markdown("""## Explore the concepts further

<details><summary>How informatics supports surveillance</summary>

![Laila faces data overload](assets/slide-previews/unit-1-022.jpg)

![What public health informatics does](assets/slide-previews/unit-1-019.jpg)

![From data to wisdom](assets/slide-previews/unit-1-025.jpg)

Use these diagrams to connect the reported counts, their interpretation, and the next action. An interpretation still needs verification.

</details>
""", 'concept-visuals'))
            elif src == 'u02-n03-his-context':
                target['cells'][0]['source'] += ['\n\nAt each reporting step, check who records the data, who reviews it, and who is authorized to access it. Patient and community records feed case reports; laboratory records feed laboratory reports. Both branches reach the district system.\n']
            elif src == 'u02-n04-case-study':
                target['cells'][0]['source'] += ['\n\nThis is a practice scenario set in October 2021. The district team collects reports, checks quality, summarizes person/place/time, and follows up signals. The diagram is the reporting arrangement for this scenario; verify the actual systems and responsibilities in your own setting.\n']
            elif src == 'u02-n10-data-quality':
                target['cells'][0]['source'] += ['\n\nA shared data dictionary and entry checks can prevent some missing or invalid values. Repeated entry into separate systems can introduce inconsistencies. These are scenario examples; inspect the incoming rows and supplied confirmations before changing a value.\n']
            coverage.append({'source':src,'destination':dest,'integration':'essential concepts rewritten into concise canonical scenario; duplicate diagrams, task directions, and historical operational assertions omitted'})
        elif src in ASSIGNMENTS:
            coverage.append({'source':src,'destination':dest,'integration':'concepts adapted into the destination task and explicit Record questions about its supplied data; procedural bullets and cross-assignment numbering omitted'})
        elif src.endswith('-slides'):
            added[dest].append(markdown('## Explore the slides\n\nOpen a page range below to connect the diagrams to your work.',src+'-intro'))
            for i,c in enumerate(doc['cells']):
                if c['cell_type']=='markdown' and text(c).startswith('<details>'):
                    added[dest].append(markdown(transform(text(c),reading=True),src+'-'+str(i)))
            coverage.append({'source':src,'destination':dest,'integration':'local collapsible slide previews and PDF page links'})
        elif 'knowledge-check' in src:
            coverage.append({'source':src,'destination':dest,'integration':'knowledge-check concepts consolidated in the destination task and authored reflection fields'})
        else:coverage.append({'source':src,'destination':dest,'integration':'navigation replaced by unified course contents'})
    library=read(READINGS/'u00-n02-version3-form-library.ipynb')
    current=None
    for i,c in enumerate(library['cells']):
        s=text(c)
        match=re.match(r'## Unit (\d+)',s)
        if match and 'Written case study' in s:
            current=None
        elif match:
            u=int(match.group(1));current=next(k for k in docs if k.startswith(f'u{u:02d}-n01-'))
        elif s.startswith('## References'):current=None
        if current:
            c=copy.deepcopy(c);c['id']='practice-'+str(i)
            c['source']=transform(s,reading=True).splitlines(keepends=True)
            if c['cell_type']=='code':
                c['metadata']['jupyter']={'source_hidden':True}
                if 'choose answers for Unit ' in s:
                    # Keep quiz variables from replacing the task controls on Run All.
                    split=s.index('display(HTML(')
                    scoped=s[:split]+'def _show_practice_quiz():\n'+textwrap.indent(s[split:],'    ')+'\n_show_practice_quiz()\n'
                    c['source']=scoped.splitlines(keepends=True)
            added[current].append(c)
    coverage.append({'source':'u00-n02-version3-form-library','destination':'Units 1, 2, 4, 5, 7','integration':'interactive quizzes with provisional feedback; written case concepts adapted into canonical task reflections rather than repeating later assignments'})
    for name,doc in docs.items():
        refs=doc['cells'].pop()
        if name in REFLECTIONS:
            section,questions=REFLECTIONS[name]
            response={'cell_type':'code','id':'reflection-fields','metadata':{'jupyter':{'source_hidden':True}},'source':reflection_code(section,questions).splitlines(keepends=True),'outputs':[],'execution_count':None}
            existing=next((i for i,c in enumerate(doc['cells']) if c['id']=='reflection-fields'),None)
            if existing is None:
                doc['cells'].extend([markdown('## Reflect on the records\n\nRun the next cell, write your answers, and select **Record** to save them in this browser. These reflections are unscored.','reflection-intro'),response])
            else:doc['cells'][existing]=response
        doc['cells'].extend(added[name]);doc['cells'].append(refs)
        for c in doc['cells']:
            c['source']=transform(text(c)).splitlines(keepends=True)
        # Centralize the UCSF attribution in Notebook 00 References.
        refs_text=text(doc['cells'][-1])
        refs_lines=[]
        for line in refs_text.splitlines():
            if 'UCSF' in line:
                before=line.split('UCSF')[0].rstrip(' ;,')
                if before.strip('- ').strip():refs_lines.append(before)
            else:refs_lines.append(line)
        if not any(line.startswith('- ') and not line.startswith('- [') for line in refs_lines):
            refs_lines.insert(2,'- Public Health Informatics for FETP, course lessons, slides, and practice materials.')
        if name=='u00-n00-start-here':
            refs_lines.append('- UCSF Institute for Global Health Sciences. *FETP JupyterBook*. Informatics lessons, case studies, and practice assignments adapted throughout this course.')
        doc['cells'][-1]['source']=('\n'.join(refs_lines)+'\n').splitlines(keepends=True)
        # The orientation is the one table of contents, not a link to a second library.
        if name=='u00-n00-start-here':
            doc['cells']=[c for c in doc['cells'] if not text(c).startswith('## Optional course source library')]
            s='## Course contents\n\nFollow this sequence, or use the Learning panel to revisit recommended practice.\n\n'
            for stem in SEQUENCE:
                title=re.search(r'(?m)^# (.+)',text(docs[stem]['cells'][0])).group(1)
                s+=f'- [{stem[:7].upper()}: {title}]({stem}.ipynb)\n'
            s+='\nRun supplied computation cells with **Shift+Enter**. Select **Submit** to check an answer and **Record** to save an unscored reflection. Running setup or computation alone does not record an attempt.\n\nUse **Download reflections** in the Learning panel to keep a readable copy of recorded writing. **Export evidence** downloads scored attempts and progress as RDF; it excludes reflection text and notebook edits. Download an edited notebook separately from the File menu. These downloads do not provide automatic restoration.\n'
            doc['cells'][2]['source']=s.splitlines(keepends=True)
        # One explicit onward route, after optional practice and before References.
        doc['cells']=[c for c in doc['cells'] if c.get('id')!='continue' and not text(c).startswith(("## Continue Laila", "## Continue the case", "## Continue learning"))]
        index=SEQUENCE.index(name)
        next_name=SEQUENCE[index+1] if index+1<len(SEQUENCE) else 'u03-n08-my-learning-record'
        nav=markdown(f'## Continue learning\n\n[Next: {next_name[:7].upper()}]({next_name}.ipynb) · [Course start](u00-n00-start-here.ipynb) · [Review your learning record](u03-n08-my-learning-record.ipynb)','continue')
        doc['cells'].insert(len(doc['cells'])-1,nav)
        (course/(name+'.ipynb')).write_text(json.dumps(doc,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
    for p in (SOURCE/'exercises/r').glob('*.ipynb'):
        doc=read(p)
        for c in doc['cells']:
            c['source']=transform(text(c),'r').splitlines(keepends=True)
        # The DHIS2 continuation is Python only.
        (course/'r').mkdir(exist_ok=True)
        (course/'r'/p.name).write_text(json.dumps(doc,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
    validate(course)
    (ROOT/'docs/audit/unified-course-coverage.json').write_text(json.dumps(coverage,indent=2)+'\n',encoding='utf-8')
    print(f'Assembled one course sequence: {len(docs)} Python notebooks; 6 existing R alternatives; {len(coverage)} source mappings. No reading notebooks published.')
if __name__=='__main__':main()
