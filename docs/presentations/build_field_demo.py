"""Prepare editable slide layouts for export_field_demo.ps1.

Uses the Python standard library. The companion PowerShell exporter builds
and renders the presentation with the installed Microsoft PowerPoint document
object model. Images are embedded course screenshots.
"""
from pathlib import Path
import json
import struct
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSETS = HERE / 'assets'
BUILD = ROOT / '.tools' / 'field-demo-build'
BUILD.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(exist_ok=True)
shutil.copyfile(ROOT / '.course-content/notebooks/assets/laila-unit01-notebook01-comic.png', ASSETS / 'laila-comic.png')
INK, TEAL, GRAY, BG, GOLD = '173B49', '007F83', '52656E', 'FFFDFA', 'D89E2B'
BASE = 'https://adaptive-learning-network.github.io/jupyterlite-prototype/'
START = BASE + 'lab/index.html?path=notebooks/u00-n00-start-here.ipynb'
DEMO = BASE + 'lab/index.html?path=notebooks/u03-n06-case-or-aggregate.ipynb'
DOCS = 'https://jupyterlite.readthedocs.io/en/stable/'
USING = DOCS + 'quickstart/using.html'


class Slide:
    def __init__(self, title, notes, dark=False):
        self.title, self.notes, self.dark = title, notes, dark
        self.model = []

    def text(self,text,x,y,w,h,size=29,color=INK,bold=False,font='Arial',align='l',link=None):
        self.model.append(dict(kind='text',text=text,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,font=font,align=align,link=link))

    def rect(self,x,y,w,h,color):
        self.model.append(dict(kind='rect',x=x,y=y,w=w,h=h,color=color))

    def image(self,name,x,y,w,h,alt=''):
        path=ASSETS/name
        iw,ih=struct.unpack('>II',path.read_bytes()[16:24])
        scale=min(w/iw,h/ih)
        dw,dh=iw*scale,ih*scale
        self.model.append(dict(kind='image',path=str(path),x=x+(w-dw)/2,y=y+(h-dh)/2,w=dw,h=dh,alt=alt))

    def table(self,rows,x,y,widths,rowh=64,size=26):
        self.model.append(dict(kind='table',rows=rows,x=x,y=y,w=sum(widths),h=len(rows)*rowh,widths=widths,rowh=rowh,size=size))

    def finish(self,n):
        if n!=1:
            self.text(self.title,64,42,1152,75,44,'FFFFFF' if self.dark else INK,True)
            self.rect(64,126,70,4,GOLD)
        self.text(str(n),1175,677,40,26,17,'B7CDCD' if self.dark else GRAY,align='r')

slides=[]
def add(title,notes,dark=False):
    s=Slide(title,notes,dark);slides.append(s);return s

s=add('Learning public health informatics with interactive notebooks',
'''Introduce this as a field demonstration of a browser-based course. Participants will see how the notebook connects a surveillance question, data, computation, interpretation, and reflection. Laila is a teaching character. The records shown are invented. Allow about 25 minutes plus discussion, including the three slides on becoming a course contributor. Ask participants to watch for places where instructions or feedback need improvement.
Source: current course Notebook 00 and Unit 1 Notebook 01. Artwork: bundled course teaching comic, laila-unit01-notebook01-comic.png.''',True)
s.text('Learning public health informatics\nwith interactive notebooks',64,45,1145,150,54,'FFFFFF',True)
s.text('Field demonstration',66,211,1000,40,29,'CDE7E4')
s.image('laila-comic.png',64,285,1152,352,'Laila reviews records, inspects a chart, and discusses findings with a colleague at a professional distance.')

s=add("Laila's weekly surveillance summary",'''This slide introduces the data used again on slide 4. The numbers come from the course's invented weekly reported case counts. For this presentation, explicitly define a training scenario: each number is the count of suspected measles cases reported in that district during one reporting week. Week 1 and Week 2 are consecutive reporting weeks. The disease label and numbered weeks are presentation assumptions added to make the example understandable; the underlying Unit 1 fixture does not specify a disease or calendar dates. The slide identifies the scenario as invented.
Ask the answerable descriptive question: which district has the largest absolute increase in reported cases? Kambia increases by 5, Port Loko by 1, and Bombali decreases by 1. Invite a prediction here, then work through Kambia's calculation on slide 4. These counts do not establish incidence, relative disease risk, outbreak status, or a complete priority ranking. Those interpretations require additional information such as population, reporting completeness, consistent case definitions, and verification of the underlying reports. Reporting week describes when cases were reported, not necessarily when illness began. Keep the discussion about what the available data can answer.
Source: scripts/make_unit01_pilot.py, WEEKLY_COUNTS. Presentation context added 27 October 2026.''')
s.text('Invented scenario: suspected measles cases reported by district',64,160,1150,49,28,INK)
s.text('Each count covers one week. Weeks 1 and 2 are consecutive.',64,214,1150,45,27,INK)
s.text('Which district has the largest increase in reported cases?',64,274,1150,55,32,TEAL,True)
s.table([['District','Week 1: cases','Week 2: cases'],['Kambia','2','7'],['Port Loko','3','4'],['Bombali','4','3']],64,348,[390,360,400],54,29)
s.text('What would you verify before interpreting that increase?',64,590,1145,60,29,INK)
s.text('Invented training data for comparing weekly counts',64,655,1100,30,20,GRAY)

s=add('JupyterLite: where to start',f'''JupyterLite provides a computing workspace that runs in the browser. This course runs Python in the browser and does not require learners to install desktop Python. First load the course link. Open Notebook 00, named Start here, and use its Course contents links to open an activity. The file browser also lists the notebooks. The Learning panel offers a few suggested activities, while Notebook 00 provides the full course sequence. Point out each area on the screenshot before continuing. Initial loading requires access to the site and its resources.
Technical source: {DOCS}
Storage and usage: {USING}
Screenshot: current public course, Notebook 00, captured 23 October 2026.
Course start: {START}''')
s.text('A computing workspace that runs in your browser',64,160,1150,52,32,INK)
s.text('1  Open Notebook 00',64,242,540,47,30,TEAL,True)
s.text('2  Choose an activity link',666,242,548,47,30,TEAL,True)
s.image('open-notebook00.png',64,305,540,280,'The file browser highlights u00-n00-start-here.ipynb. Double-click this notebook to open it.')
s.image('contents-detail.png',666,305,548,280,'Course contents links in Notebook 00 open each activity.')
s.text('Read the activity instructions before running cells.',64,611,1150,45,28)
s.text('Open the course start page',64,660,1050,30,23,TEAL,link=START)

s=add('A computational narrative',f'''A computational narrative connects an explanation to executable steps and the results those steps produce. Return explicitly to the invented suspected-measles reporting scenario on slide 2. Kambia's counts are 2 in Week 1 and 7 in Week 2. Ask how much that reported count changed. The visible Python calculation subtracts Week 1 from Week 2 and gives an increase of 5 reported cases. The other districts change by 1 and minus 1 respectively, so Kambia has the largest absolute increase among these three rows. This is a comparison of reported counts, not an epidemiologic priority score or an outbreak determination.
A learner can inspect the inputs and run the calculation. The interpretation should match the data: Kambia's reported count rose by 5, while the reason remains to be verified. In a notebook, read cells from top to bottom. Select a code cell and use the Run control or Shift+Enter. Output appears below that cell. A separate Submit control records an assessed answer when the activity asks for one.
Source: Unit 1 Notebook 01 and scripts/make_unit01_pilot.py. This slide simplifies the calculation for explanation and uses the explicit training scenario introduced on slide 2. Revised together with slide 2 on 27 October 2026.
Notebook concepts: https://docs.jupyter.org/en/latest/''')
s.text('The question',64,166,350,45,29,TEAL,True)
s.text("How much did Kambia's\nreported count change?",64,222,355,130,30)
s.text('The calculation',469,166,730,45,29,TEAL,True)
s.rect(455,222,760,192,'EEF4F3')
s.text('week_1 = 2\nweek_2 = 7\nweek_2 - week_1',478,244,706,145,28,INK,font='Consolas')
s.text('The result',64,446,350,44,29,TEAL,True)
s.text('Kambia: an increase of 5 reported cases',64,501,1145,55,36,INK,True)
s.text('The count rose. Verify the reports before explaining why.',64,588,1145,65,29)

s=add('The tools supporting the activity',f'''Use the visible learning task to explain the ecosystem. A notebook is the document combining narrative, code, and outputs. JupyterLab is the workspace interface with tabs, files, and Run controls. JupyterLite brings that workspace into the browser. Python and compatible libraries calculate and display results. Interactive controls collect answers and reflections. Our custom adaptive-learning extension adds rules-based feedback, a local learner record, and suggested activities. These custom course features are distinct from the underlying JupyterLite platform. Do not imply that every Python package or JupyterLab extension runs in JupyterLite.
Sources: {DOCS} and {USING}; repository README and current extension implementation.''')
s.table([['Tool','What the learner uses it for'],['Jupyter notebook','Read the case, run steps, inspect results'],['JupyterLab interface','Open files and use notebook controls'],['JupyterLite','Work through the course in a browser'],['Python and its libraries','Calculate summaries and draw charts'],['Course extension','Get feedback and suggested activities']],64,167,[395,755],73,27)

s=add('Learning through a notebook', '''Present this as a proposed facilitation approach, not a measured learning effect. Before running the calculation, ask participants to predict which district stands out. Let them try it, inspect the result, and explain what it means. A revision should include a reason. Then change the example and ask them to apply the same reasoning. A facilitator can pause at any step for paired explanation or a group discussion. The computational narrative keeps the data and method available for inspection rather than asking participants to accept the output without examining how it was produced.
Sources: proposed instructional sequence in field-demo-presentation-plan.md; shipped Unit 1 and U03-N06 activities. Educational effectiveness remains unvalidated.''')
for i,(word,detail) in enumerate([('Predict','What do you expect to find?'),('Try','Run a step or choose an answer.'),('Inspect','Compare the result with the data.'),('Explain','Describe the reasoning in your own words.'),('Revise','Use feedback to improve the answer.'),('Apply','Work through a different example.')]):
 y=165+i*79;s.text(f'{i+1:02}',64,y,64,46,30,GOLD,True);s.text(word,155,y,220,47,32,TEAL,True);s.text(detail,415,y,790,53,29)

s=add('Adaptive learning support', '''Show this as an actual result of a submitted response. The learner receives per-table feedback. In U03-N06, the feedback also directs attention to the meaning of a row. Hints are authored help. The extension records submitted outcomes and recorded guidance. The Learning panel uses authored curriculum rules and recorded results to suggest activities and explain their reasons. The full course sequence stays available. Learners explicitly submit answers. Running setup or computation alone does not record an assessed attempt. The prototype uses deterministic assessment and authored help rather than a conversational model diagnosing the learner.
Source: current public U03-N06 screenshot and docs/design/classification-reassessment-pilot.md. The illustrated feedback is from invented training tables.''')
s.text('Submit an answer and inspect the feedback.',64,165,1145,52,32,TEAL,True)
s.image('feedback-detail.png',64,263,1150,165,'Actual feedback for Table A identifies an incorrect classification and explains that each row describes one case.')
s.text('Use authored hints to work through a difficulty.',64,477,1145,55,31)
s.text('The Learning panel uses recorded results and help\nto suggest what to try next.',64,565,1140,100,31,TEAL)

s=add('The Learning panel', '''Use these close-ups of the actual Learning panel to orient participants. Suggested next lists activities and the reasons for suggesting them. Open takes the learner to the activity. This exercise identifies the current task and shows its available support or task progress. Progress summarizes recorded task results. The snapshots show an invented demonstration learner who completed the classification activity but has not yet attempted the earlier tasks. This explains why the suggestions still include earlier course activities. The panel records only submitted attempts and recorded help. It does not infer every action or thought, and the estimates do not certify workplace proficiency.
Source: current public Learning panel and src/extension/panel.ts, captured 23 October 2026. The progress image shows the beginning of a longer scrollable list.''')
s.text('Suggested activities',64,173,355,45,29,TEAL,True)
s.text('Current exercise',490,173,330,45,29,TEAL,True)
s.text('Recorded progress',897,173,320,45,29,TEAL,True)
s.image('learner-panel-next.png',64,238,355,270,'One recommendation in Suggested next, with its reason and Open control.')
s.image('learner-panel-exercise.png',490,238,330,270,'This exercise names the classification task and its different-case progress.')
s.image('learner-panel-progress.png',897,238,320,270,'One task in the Progress list, currently not assessed.')
s.text('Open a recommended\nactivity.',64,524,355,72,25)
s.text('See support for the\ncurrent task.',490,524,330,72,25)
s.text('Review progress on\ncourse tasks.',897,524,320,72,25)
s.text('Suggestions reflect your recorded attempts and help used.',64,615,1150,55,29)

s=add('Practice and a different case', '''Explain the distinction in this bounded U03-N06 pilot. Practice can include hints and corrections after feedback. Try another case opens a different authored set that this browser learner has not already seen. Hints are unavailable during that check. A correct first complete submission supports the task-specific label Demonstrated on a different case. Once the learner has seen correctness feedback, correcting that same case remains practice. The earlier assisted attempt stays in the history. This policy currently applies to U03-N06, not to every notebook. No recorded hints does not prove absence of outside help. The task result does not establish workplace proficiency or retention.
Source: docs/design/classification-reassessment-pilot.md; catalog/case-aggregate-v1.json. Screenshots: current published course, captured 23 October 2026.''')
s.text('Practice',64,173,520,48,36,TEAL,True)
s.text('Use feedback and hints.\nRevise your classifications.',64,241,520,110,31)
s.image('practice-status.png',64,387,520,145,'Actual progress label: Practice completed with assistance.')
s.text('A different case',690,173,520,48,36,TEAL,True)
s.text('Apply the same reasoning\nto unfamiliar tables.',690,241,520,110,31)
s.image('different-status.png',690,387,520,145,'Actual progress label: Demonstrated on a different case.')
s.text('These labels describe performance on this classification task.',64,599,1145,60,28,GRAY)

s=add('Walkthrough: choices and feedback',f'''Open the linked U03-N06 activity for the four-minute live demonstration. First run the collapsed setup cell using the notebook Run control or Run All Cells. Select a classification for every table. Submit a prepared set containing one deliberate mistake, read the feedback, request a hint, and correct the practice answer. Then choose Try another case and classify the different tables. Explain the resulting progress label. The first screenshot is an individual case register. The second is a different-case table. These embedded screenshots provide a fallback if the live site cannot load. Say explicitly when showing the recorded example.
The pool has three different-case sets. Rehearse with a separate disposable demonstration browser profile. Preserve genuine learner work.
Direct demo: {DEMO}
Screenshots captured from that public activity on 23 October 2026.''')
s.text('Run a selected code cell with Shift+Enter',64,166,1150,46,29,TEAL,True)
s.image('run-toolbar.png',64,232,575,62,'The notebook toolbar includes the triangular Run control. Code is the selected cell type.')
s.image('table-choice.png',64,326,575,277,'Actual practice table with case-based and aggregate radio-button choices.')
s.text('1  Run the setup cell',710,241,500,72,31,TEAL,True)
s.text('2  Choose an answer\n    for every table',710,351,500,115,31,TEAL,True)
s.text('3  Submit and read feedback',710,495,500,85,31,TEAL,True)
s.text('4  Try another case',710,609,500,50,31,TEAL,True)
s.text('Open the live activity',64,649,575,32,23,TEAL,link=DEMO)

s=add('Your learning record and reflections',f'''Use the screenshot to show the reflection question, the entered reasoning, the Record button, and the save confirmation. Learners must select Record to retain their writing in the browser record. The writing is unscored and does not automatically change capability estimates. My learning record displays submitted attempts and task progress alongside recorded reflections. Storage belongs to the current browser and site. Opening another browser, another device, or another site does not automatically transfer the record. Clearing browser data can remove it. Evidence, reflections, and edited notebooks have separate download routes. These copies do not provide automatic restoration. Explain those details if participants ask, and include them in the handout.
Sources: docs/design/browser-storage.md; current extension and reflection widgets. General browser storage: {USING}
Screenshot: invented demonstration reflection captured 23 October 2026.''')
s.image('reflection.png',64,166,1150,340,'Actual reflection text field, Record button, and successful save confirmation.')
s.text('Select Record to save your reflection.',64,535,1150,47,31,TEAL,True)
s.text('Review attempts and progress in My learning record.',64,594,1150,47,28)
s.text('Work stays in this browser for this course site.',64,650,1150,35,24,GRAY)

s=add('Learning with a facilitator', '''Offer these prompts during the same surveillance-table exercise. The first asks for an explanation of the data rather than recognition of a label. The second asks the learner to connect feedback to a revision. The third connects the learning activity to field practice and the need to verify a report. Participants can first answer individually and then compare explanations in pairs. Facilitators can listen for misunderstandings and choose examples for a group discussion. The browser-local record belongs to the learner. This prototype does not provide an automatic facilitator dashboard or upload learner records to an instructor.
Source: proposed field facilitation approach; current course reflection prompts and storage design. No claim of demonstrated learning effectiveness.''')
for y,num,q in [(178,'01','What does one row in this table represent?'),(323,'02','What changed in your answer after the feedback?'),(468,'03','What would you verify before using this report?')]:
 s.text(num,64,y,80,70,40,GOLD,True);s.text(q,185,y,1000,100,35,INK,True)

s=add('Epidemiologists as course authors', '''This slide changes the audience's role from completing the course to producing its next version. Epidemiologists contribute knowledge of field work, realistic questions, public health meaning, and appropriate local examples. They can use an approved AI assistant alongside the course to help draft explanations, code, controls, and checks. The AI authoring assistant is separate from this prototype's deterministic adaptive-learning extension. No conversational AI model is embedded in the current learner workflow.
Use this actual kind of problem from development: a reflection prompt says Write your reasoning, but offers no response field. A contributor can specify a text field, an explicit Record action, and restoration after reload. Ask for one bounded change and its review steps. Supply invented data. Describe the intended learner outcome so that the contributor can evaluate the proposed implementation. Participation can begin by specifying and reviewing an improvement with a maintainer, without independently managing the publishing tools.
Sources: course development history; docs/audit/pre-field-test-audit.md, response-widget findings; docs/design/browser-storage.md. The suggested authoring workflow is a practical proposal, not a validated learning result.''')
s.text('Use your field experience to shape the next version.',64,167,1150,54,32,TEAL,True)
s.text('An example from this course',64,266,500,45,29,TEAL,True)
s.text('Give a reflection question\na working response field\nand a Record button.',64,335,470,175,32)
s.text('An example request to an AI assistant',616,266,595,77,28,TEAL,True)
s.text('"Inspect this activity. Add a response field and a Record button. Show how to check that the saved response returns after reload."',616,363,595,215,30)
s.text('Work with invented data and an approved AI tool.',64,628,1150,44,27,GRAY)

s=add('A typical improvement workflow', '''Describe the workflow we have used in this course in terms a field epidemiologist can participate in. First identify one learner problem, naming the notebook and including the exact sentence or a screenshot with invented data. State what the learner should be able to do. Next ask the AI assistant to inspect the current material and propose a small change before editing. Inspect the actual source and any supporting references. Revise the source and regenerate the notebook where the course uses generators.
Try the revised activity in the local browser as a learner: use a correct answer, an incorrect answer, and an incomplete response. Check that feedback explains the outcome. For a reflection, record text and reload to check that it returns. Review the public health meaning with an epidemiologist and have a colleague try the activity. Record what changed and why. After course-owner review, a maintainer commits, pushes, publishes, replicates, and checks the public site with a fresh browser profile as well as preservation of returning learner work. A successful build alone does not establish useful teaching. Keep the contributor's field judgment visible throughout.
Sources: this course's implemented review and release workflow; docs/audit/pre-field-test-audit.md; AGENTS.md source/generation, preview, and release requirements. This is a practical contributor workflow adapted from development experience.''')
for i,(word,detail) in enumerate([('Identify','Name the gap and the learner goal.'),('Plan','Review a small change proposed with AI.'),('Build','Revise one activity using invented data.'),('Try','Check correct, incorrect, and empty answers.'),('Review','Check meaning, usability, and saved work.'),('Publish','Share the reviewed version and verify it live.')]):
 y=165+i*79;s.text(f'{i+1:02}',64,y,64,46,30,GOLD,True);s.text(word,155,y,220,47,32,TEAL,True);s.text(detail,415,y,790,53,29)

s=add('Reviewing an AI-assisted contribution', '''AI can propose plausible but wrong content, code, or citations. Epidemiologists provide the domain review that checks what a revised activity actually means. Use the earlier development example: an eight-year-old cannot correctly receive the category under 5. A program running without an error does not show that its categories match the public health question. Compare the data, expected answer, explanation, and actual feedback. Read each cited source to confirm that it supports the claim. Have a colleague attempt the activity without coaching and note where they hesitate.
Keep a short explanation of the change, the source checked, and the checks performed with the revised activity. A course owner reviews the contribution before release. These actions apply to improving teaching materials. Use invented training data and the organization's approved AI tools and sharing process. Do not imply that the current course automatically transmits content to an external AI service.
Sources: course development history and pre-field audit. General supporting guidance: NIST AI 600-1 (2024), sections 2.2 and MEASURE 2.5, including review of generated sources and citations. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf (checked 23 October 2026). The local workflow is our adaptation, not a NIST certification.''')
for y,label,detail in [(177,'Public health meaning','Do the categories answer the intended question?'),(283,'Results and feedback','Do the calculation, label, and explanation agree?'),(389,'Supporting sources','Does each reference support the claim?'),(495,'A colleague\'s experience','Can someone complete the activity without coaching?')]:
 s.text(label,64,y,350,83,29,TEAL,True);s.text(detail,455,y,755,86,30)
s.text('Contribute the revised activity with a short change and review note.',64,624,1150,54,27,GRAY)

s=add('Questions for the field test',f'''Invite participants to try the public course and comment on the instructions and feedback. Ask whether they could find the starting point, understand the task, interpret the feedback, choose a next step, and explain an unfamiliar example. Observe what they do and ask them to explain their reasoning. Successful software checks establish observed application behavior. Field observation is needed to assess clarity, usability, and learning. Record proposed improvements separately from demonstrated outcomes.
Course start: {START}
Technical references: {DOCS} and {USING}
Course references: FETP Public Health Informatics course materials used with permission, acknowledged in Notebook 00 References. Internal planning evidence: docs/audit/pre-field-test-audit.md and docs/design/classification-reassessment-pilot.md.
Presentation prepared 23 October 2026. The screenshots contain invented data and demonstration responses.''',True)
s.text('Could you find where to start?',64,185,1135,56,38,'FFFFFF',True)
s.text('Did the feedback help you explain your answer?',64,287,1135,100,38,'FFFFFF',True)
s.text('What improvement would you contribute?',64,429,1135,100,38,'FFFFFF',True)
s.text('Choose one activity to review and improve',64,581,1135,45,29,'B8E5DF',link=START)
s.text('adaptive-learning-network.github.io/jupyterlite-prototype',64,635,1135,32,22,'B8E5DF',link=BASE)

for i,s in enumerate(slides,1):
    s.finish(i)
(HERE/'field-demo-speaker-notes.md').write_text('# Field demonstration speaker notes\n\n'+ '\n\n'.join(f'## {i}. {s.title}\n\n{s.notes}' for i,s in enumerate(slides,1))+'\n',encoding='utf-8')
(BUILD/'slide-titles.json').write_text(json.dumps([s.title for s in slides],indent=2),encoding='utf-8')
(BUILD/'presentation.json').write_text(json.dumps({'slides':[{'title':s.title,'notes':s.notes,'background':INK if s.dark else BG,'elements':s.model} for s in slides]},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Prepared {len(slides)} slide layouts for native PowerPoint export.')
