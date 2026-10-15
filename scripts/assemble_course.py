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

def text(cell):return ''.join(cell['source'])
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def markdown(source,ident):return {'cell_type':'markdown','id':ident,'metadata':{},'source':source.splitlines(keepends=True)}
def transform(source,language='python',reading=False):
    asset='assets/' if language=='python' else '../assets/'
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
            if 'readings/ucsf' in s:raise ValueError('Separate reading route remains: '+str(p))
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
        if src in LESSONS:
            s=clean_lesson(text(doc['cells'][1]))
            target['cells'][0]['source']+=['\n\n'+transform(s,reading=True)+'\n']
            coverage.append({'source':src,'destination':dest,'integration':'explanation and visuals in opening narrative'})
        elif src in ASSIGNMENTS:
            s=clean_lesson(text(doc['cells'][1]))
            # The questions become writable reflections rather than another assignment notebook.
            added[dest].append(markdown('## Apply the decision\n\nWrite a response for each prompt below, then select **Record**. These reflections are unscored.',src+'-intro'))
            code=reflection_code('integrated:'+src,prompts(s))
            added[dest].append({'cell_type':'code','id':src+'-response','metadata':{'jupyter':{'source_hidden':True}},'source':code.splitlines(keepends=True),'outputs':[],'execution_count':None})
            coverage.append({'source':src,'destination':dest,'integration':'question-by-question Record fields'})
        elif src.endswith('-slides'):
            added[dest].append(markdown('## Explore the slides\n\nOpen a page range below to connect the diagrams to your work.',src+'-intro'))
            for i,c in enumerate(doc['cells']):
                if c['cell_type']=='markdown' and text(c).startswith('<details>'):
                    added[dest].append(markdown(transform(text(c),reading=True),src+'-'+str(i)))
            coverage.append({'source':src,'destination':dest,'integration':'local collapsible slide previews and PDF page links'})
        elif 'knowledge-check' in src:
            # Keep the already implemented response fields and storage section IDs.
            for i,c in enumerate(doc['cells']):
                if c['cell_type']=='code':
                    c=copy.deepcopy(c);c['id']=src+'-'+str(i);added[dest].append(c)
            coverage.append({'source':src,'destination':dest,'integration':'knowledge-check reflection fields'})
        else:coverage.append({'source':src,'destination':dest,'integration':'navigation replaced by unified course contents'})
    library=read(READINGS/'u00-n02-version3-form-library.ipynb')
    current=None
    for i,c in enumerate(library['cells']):
        s=text(c)
        match=re.match(r'## Unit (\d+)',s)
        if match:
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
    coverage.append({'source':'u00-n02-version3-form-library','destination':'Units 1, 2, 4, 5, 7','integration':'interactive quiz and written-case sections within their units; provisional feedback retained'})
    for name,doc in docs.items():
        refs=doc['cells'].pop()
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
            s=text(doc['cells'][2]).replace('The readings are optional source material.','Explanations, slides, practice questions, and computation are in this one sequence.')
            s=re.sub(r'^3\. If you want fuller.*$', '3. Use the slides, explanations, and practice questions within each course notebook.',s,flags=re.M)
            doc['cells'][2]['source']=s.splitlines(keepends=True)
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
