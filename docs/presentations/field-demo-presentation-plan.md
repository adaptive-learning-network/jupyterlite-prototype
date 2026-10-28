# Field demo presentation plan

Date: 23 October 2026

Status: Initial presentation authored as 16 slides. The 12-slide outline below
was extended with a dedicated Learning panel screenshot slide and three slides
that shift the audience from course consumers to producers using AI.

The added contributor sequence covers epidemiologists as course authors, the
typical improvement workflow, and review of an AI-assisted contribution.
The current deck takes approximately 25 minutes plus discussion.

## Audience and purpose

Field epidemiologists with varied experience of programming and interactive notebooks. Assume familiarity with surveillance questions, case records, laboratory reports, and district reporting. Introduce computing terms through those familiar tasks.

Explain how the browser-based course brings the public health question, explanation, data, computation, feedback, and reflection into one learning sequence. Show how the custom adaptive-learning extension supports that sequence.

Working title: **Learning public health informatics with interactive notebooks**

Proposed format: 12 core slides, approximately 20 minutes including a four-minute demonstration, followed by five minutes of discussion. Duration is a planning assumption. Keep implementation details in optional reference material.

## What participants should be able to explain

1. What JupyterLite lets them do in a browser and where their work is kept.
2. How a computational narrative connects a public health question to data, computation, interpretation, and reflection.
3. How feedback, hints, suggested activities, and the learner record support practice in this prototype.

## Presentation thread

Follow Laila as she prepares a district surveillance report. Use her need to distinguish individual case records from grouped summaries as the central demonstration. Briefly show a computed summary or chart to make the role of computation visible. Keep these examples within the same investigation.

Introduce the learner's task before naming the software. Explain the supporting tools after participants have seen what they help the learner do.

## Proposed slides

| # | Title | Main message and content | Visual or audience action | Time |
| --- | --- | --- | --- | --- |
| 1 | Learning public health informatics with interactive notebooks | Introduce the field demonstration and its purpose: learning to make and explain decisions using data. | One course image of Laila and a short surveillance-report prompt. | 0:30 |
| 2 | Laila's district surveillance report | Laila has case records, laboratory reports, and summaries. She needs to decide which records answer her question and what their limitations are. | A small, readable invented dataset beside the reporting question. Ask: what would you need to check first? | 1:30 |
| 3 | JupyterLite | A computing workspace opened through a web link. In this course, Python runs in the browser; the learner does not install a desktop Python environment. Initial loading requires access to the course site and its resources. | Annotated course screenshot identifying the notebook, Run control, output, and Learning panel. | 1:30 |
| 4 | A computational narrative | A notebook connects the question, explanation, data, executable steps, results, and interpretation. Define the term as a story in which the learner can run and inspect the analysis. | A vertically arranged excerpt from one actual notebook: question, short calculation, result, interpretation. Use only a few readable lines of code. | 2:00 |
| 5 | The tools supporting the learning activity | The notebook holds the narrative; the JupyterLab interface provides the workspace; JupyterLite runs it in the browser; Python and its libraries calculate, summarize, and plot; interactive controls collect choices; the custom extension supplies adaptive support. | One simple annotated workspace or layered illustration. Link each named tool to a visible learner action. | 1:30 |
| 6 | Learning through a notebook | Proposed teaching sequence: predict, try, inspect, explain, revise, and apply to another example. Explain what a learner does and what a facilitator can ask at each stage. | One continuous learning sequence, with a short example such as checking whether a table contains individual records or grouped counts. | 1:30 |
| 7 | Support during practice | Submit returns feedback; authored hints offer help; the Learning panel suggests activities using recorded task results and curriculum rules. The complete course contents remain available. Identify these as features of this course extension. | A close-up of actual feedback, a hint, and a suggested activity with its reason. | 1:30 |
| 8 | Practice and a different case | U03-N06 records guided practice separately from performance on an unseen case in its authored pool. After correctness feedback, a correction on the same case remains practice. Explain what the labels mean in everyday language. | Two actual record excerpts: Practice completed with assistance; Demonstrated on a different case. Invite a prediction about what should happen after using hints. | 1:30 |
| 9 | Demonstration: case records and summaries | Classify tables, submit, inspect feedback, use practice help, try a different case, and inspect the resulting record. | Live U03-N06 demonstration using invented data, with embedded screenshots as fallback. | 4:00 |
| 10 | Your learning record and reflections | Task attempts and recorded help support the progress display. Reflection fields let learners explain their reasoning and select Record. Reflections remain unscored. Work stays in this site's storage in the current browser; downloads are separate and do not automatically restore it. | Actual My learning record view plus a reflection field and Record confirmation. | 1:30 |
| 11 | Learning with a facilitator | Use individual attempts, paired explanation, and group discussion. Ask learners to explain what one row represents, justify an interpretation, and discuss what they would verify before acting. Describe this as a proposed facilitation approach. | Three brief facilitator prompts tied to the demonstrated tables. | 1:00 |
| 12 | Questions for the field test | Ask whether the task was clear, feedback helped, the next step made sense, and the learner could explain an unfamiliar example. Invite participants to try the course. State that the prototype is ready for field review and learning benefits still need evaluation. | Three or four review questions, a clickable course link, and a QR code accompanied by the written link. | 1:30 |

Total: approximately 20 minutes. Discussion follows the core presentation.

## Demonstration run sheet

Use a separate demonstration browser profile with invented learner responses. Keep the reviewer's normal browser record intact. Rehearse on the published site and the equipment and network intended for the session.

1. Open U03-N06, run its setup cells, and show one individual-record table and one grouped-summary table. Explain what a row represents before selecting answers.
2. Submit a prepared set of classifications containing one deliberate mistake. Read the feedback and show one practice hint. Correct the classifications and submit again.
3. Point out the practice result and the retained hint history. Select **Try another case**. Explain that this case has different tables and recorded hints are unavailable for this check.
4. Classify the new tables and submit. Explain the displayed result. If the first complete submission is incorrect, use that outcome to explain further practice; do not promise that correction will produce an independent demonstration.
5. Use the learning-record screenshot on slide 10 to show how the attempts remain visible. If time permits, type a short reflection and select **Record** live.

Use a fresh demonstration profile for each rehearsal intended to show an unseen case. The pilot has three different-case sets and does not recycle previously displayed cases as new. Learners' genuine records must be preserved.

Keep a static, embedded fallback sequence showing the tables, submitted feedback, hint, practice status, different-case result, and saved reflection. Display the fallback as a recorded example if used. No live Google Drive, Google Forms, or video embed is needed for the presentation.

## Content and visual direction

- Use course screenshots and a few small, legible invented tables. Crop screenshots to the interaction being discussed and label them directly.
- Use a clear light background, large text, and one main idea per slide. Prefer a single explanatory visual to dense feature lists.
- Preserve respectful professional distance in any character artwork. Reuse reviewed local artwork where appropriate.
- Keep code to one brief example that makes the connection between a calculation and its result understandable. Presenters explain the public health meaning of the output.
- Use plain labels: notebook, data source, case record, grouped summary, feedback, hint, reflection, and suggested activity. Define computational narrative on its first use.
- Put references in speaker notes and an optional final reference slide. Keep links clickable and include readable text alongside any QR code.
- Embed demonstration images in the final presentation. Any eventual PDF companion should also contain the essential example and screenshots.

## Claims and boundaries to preserve

| Topic | Presentation wording or boundary |
| --- | --- |
| JupyterLite | Browser-based Jupyter workspace; this deployment runs Python in the browser. Avoid implying that every Python package or Jupyter extension works in JupyterLite. |
| Course package | One integrated Python course sequence. R redevelopment is deferred and does not need a core slide. |
| Adaptive support | This course's custom extension checks defined responses, records outcomes and help, and applies authored rules to suggest activities. Authored feedback is not generated by a conversational AI model. |
| Different-case pilot | The practice/different-case distinction applies specifically to U03-N06. Do not imply that all course notebooks implement this policy. |
| Interpretation of progress | A successful different-case classification is evidence about that bounded task. Workplace competence, retention, and effectiveness of the teaching approach require additional evaluation. |
| Reflections | Learners explicitly Record their writing. Reflections are unscored and do not automatically change capability estimates or recommendations. |
| Local storage | This prototype keeps the learner record in the current browser for the current site; it does not automatically synchronize devices or send learner records to facilitators. Browser data deletion can remove the record. |
| Downloads | Evidence, reflections, and edited notebooks have different download paths. They are copies for the learner; automatic cross-device restoration is not implemented. Keep detailed instructions in the handout or appendix. |
| Connectivity | The site and resources must load. Offline operation on a particular field device and network needs its own rehearsal and verification. |
| Training data | Demonstrate with invented data. Local execution alone is not authorization to use identifiable patient information. |
| Evidence of readiness | Software/browser tests support claims about observed application behavior. Field observation is needed to assess clarity, usability, and learning. |

## Optional supporting slides

Prepare only those useful for the session; these are outside the 12-slide core:

- Getting started: opening Notebook 00, running a cell, submitting, recording, and returning to the course contents.
- Keeping a copy of your work: evidence, reflection, and notebook downloads, and browser/site storage boundaries.
- A worked computation: a small surveillance summary or visualization from the same investigation.
- References and acknowledgments.

## Inputs for slide production

- A current, readable screenshot of one notebook and its Learning panel.
- A short question/calculation/output example from the shipped course.
- Close-ups of U03-N06 practice feedback, hint history, a different-case result, and My learning record.
- A reflection field with its successful Record confirmation.
- Embedded demonstration fallback images.
- Verified public course and direct-notebook links.
- Presenter name, event, and date if supplied later; omit placeholders from the final cover.

## Sources and production checks

Technical descriptions checked on 23 October 2026:

- [JupyterLite documentation](https://jupyterlite.readthedocs.io/en/stable/): browser execution, static deployment, extension and visualization support.
- [Using an existing JupyterLite deployment](https://jupyterlite.readthedocs.io/en/stable/quickstart/using.html): browser storage, supplied files, local copies, and circumstances under which code/extensions can send data externally.
- [Course README](../../README.md): integrated course sequence, interactions, current deployment links, downloads, and course scope. Check descriptions against the current learner interface rather than copying historical implementation paragraphs.
- [Practice and different-case pilot](../design/classification-reassessment-pilot.md): exact U03-N06 behavior and bounded interpretation of progress.
- [Browser storage](../design/browser-storage.md): local record and download boundaries. Use the current interface for labels and reflection identity behavior.
- [Pre-field test audit](../audit/pre-field-test-audit.md): usability questions and limits of software validation.

The instructional sequence and facilitation suggestions above are proposed presentation choices. They do not assert measured improvements in learning.

Before authoring: review the outline, timing, and demonstration emphasis with the course owner. Before delivery: inspect all slides at presentation size, rehearse the live path, confirm the actual progress labels, check every outbound link, and verify that the fallback conveys the complete example.
