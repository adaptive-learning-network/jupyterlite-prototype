# Field demonstration speaker notes

## 1. Learning public health informatics with interactive notebooks

Introduce this as a field demonstration of a browser-based course. Participants will see how the notebook connects a surveillance question, data, computation, interpretation, and reflection. Laila is a teaching character. The records shown are invented. Allow about 25 minutes plus discussion, including the three slides on becoming a course contributor. Ask participants to watch for places where instructions or feedback need improvement.
Source: current course Notebook 00 and Unit 1 Notebook 01. Artwork: bundled course teaching comic, laila-unit01-notebook01-comic.png.

## 2. Laila's weekly surveillance summary

This slide introduces the data used again on slide 4. The numbers come from the course's invented weekly reported case counts. For this presentation, explicitly define a training scenario: each number is the count of suspected measles cases reported in that district during one reporting week. Week 1 and Week 2 are consecutive reporting weeks. The disease label and numbered weeks are presentation assumptions added to make the example understandable; the underlying Unit 1 fixture does not specify a disease or calendar dates. The slide identifies the scenario as invented.
Ask the answerable descriptive question: which district has the largest absolute increase in reported cases? Kambia increases by 5, Port Loko by 1, and Bombali decreases by 1. Invite a prediction here, then work through Kambia's calculation on slide 4. These counts do not establish incidence, relative disease risk, outbreak status, or a complete priority ranking. Those interpretations require additional information such as population, reporting completeness, consistent case definitions, and verification of the underlying reports. Reporting week describes when cases were reported, not necessarily when illness began. Keep the discussion about what the available data can answer.
Source: scripts/make_unit01_pilot.py, WEEKLY_COUNTS. Presentation context added 27 October 2026.

## 3. JupyterLite: where to start

JupyterLite provides a computing workspace that runs in the browser. This course runs Python in the browser and does not require learners to install desktop Python. First load the course link. Open Notebook 00, named Start here, and use its Course contents links to open an activity. The file browser also lists the notebooks. The Learning panel offers a few suggested activities, while Notebook 00 provides the full course sequence. Point out each area on the screenshot before continuing. Initial loading requires access to the site and its resources.
Technical source: https://jupyterlite.readthedocs.io/en/stable/
Storage and usage: https://jupyterlite.readthedocs.io/en/stable/quickstart/using.html
Screenshot: current public course, Notebook 00, captured 23 October 2026.
Course start: https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=notebooks/u00-n00-start-here.ipynb

## 4. A computational narrative

A computational narrative connects an explanation to executable steps and the results those steps produce. Return explicitly to the invented suspected-measles reporting scenario on slide 2. Kambia's counts are 2 in Week 1 and 7 in Week 2. Ask how much that reported count changed. The visible Python calculation subtracts Week 1 from Week 2 and gives an increase of 5 reported cases. The other districts change by 1 and minus 1 respectively, so Kambia has the largest absolute increase among these three rows. This is a comparison of reported counts, not an epidemiologic priority score or an outbreak determination.
A learner can inspect the inputs and run the calculation. The interpretation should match the data: Kambia's reported count rose by 5, while the reason remains to be verified. In a notebook, read cells from top to bottom. Select a code cell and use the Run control or Shift+Enter. Output appears below that cell. A separate Submit control records an assessed answer when the activity asks for one.
Source: Unit 1 Notebook 01 and scripts/make_unit01_pilot.py. This slide simplifies the calculation for explanation and uses the explicit training scenario introduced on slide 2. Revised together with slide 2 on 27 October 2026.
Notebook concepts: https://docs.jupyter.org/en/latest/

## 5. The tools supporting the activity

Use the visible learning task to explain the ecosystem. A notebook is the document combining narrative, code, and outputs. JupyterLab is the workspace interface with tabs, files, and Run controls. JupyterLite brings that workspace into the browser. Python and compatible libraries calculate and display results. Interactive controls collect answers and reflections. Our custom adaptive-learning extension adds rules-based feedback, a local learner record, and suggested activities. These custom course features are distinct from the underlying JupyterLite platform. Do not imply that every Python package or JupyterLab extension runs in JupyterLite.
Sources: https://jupyterlite.readthedocs.io/en/stable/ and https://jupyterlite.readthedocs.io/en/stable/quickstart/using.html; repository README and current extension implementation.

## 6. Learning through a notebook

Present this as a proposed facilitation approach, not a measured learning effect. Before running the calculation, ask participants to predict which district stands out. Let them try it, inspect the result, and explain what it means. A revision should include a reason. Then change the example and ask them to apply the same reasoning. A facilitator can pause at any step for paired explanation or a group discussion. The computational narrative keeps the data and method available for inspection rather than asking participants to accept the output without examining how it was produced.
Sources: proposed instructional sequence in field-demo-presentation-plan.md; shipped Unit 1 and U03-N06 activities. Educational effectiveness remains unvalidated.

## 7. Adaptive learning support

Show this as an actual result of a submitted response. The learner receives per-table feedback. In U03-N06, the feedback also directs attention to the meaning of a row. Hints are authored help. The extension records submitted outcomes and recorded guidance. The Learning panel uses authored curriculum rules and recorded results to suggest activities and explain their reasons. The full course sequence stays available. Learners explicitly submit answers. Running setup or computation alone does not record an assessed attempt. The prototype uses deterministic assessment and authored help rather than a conversational model diagnosing the learner.
Source: current public U03-N06 screenshot and docs/design/classification-reassessment-pilot.md. The illustrated feedback is from invented training tables.

## 8. The Learning panel

Use these close-ups of the actual Learning panel to orient participants. Suggested next lists activities and the reasons for suggesting them. Open takes the learner to the activity. This exercise identifies the current task and shows its available support or task progress. Progress summarizes recorded task results. The snapshots show an invented demonstration learner who completed the classification activity but has not yet attempted the earlier tasks. This explains why the suggestions still include earlier course activities. The panel records only submitted attempts and recorded help. It does not infer every action or thought, and the estimates do not certify workplace proficiency.
Source: current public Learning panel and src/extension/panel.ts, captured 23 October 2026. The progress image shows the beginning of a longer scrollable list.

## 9. Practice and a different case

Explain the distinction in this bounded U03-N06 pilot. Practice can include hints and corrections after feedback. Try another case opens a different authored set that this browser learner has not already seen. Hints are unavailable during that check. A correct first complete submission supports the task-specific label Demonstrated on a different case. Once the learner has seen correctness feedback, correcting that same case remains practice. The earlier assisted attempt stays in the history. This policy currently applies to U03-N06, not to every notebook. No recorded hints does not prove absence of outside help. The task result does not establish workplace proficiency or retention.
Source: docs/design/classification-reassessment-pilot.md; catalog/case-aggregate-v1.json. Screenshots: current published course, captured 23 October 2026.

## 10. Walkthrough: choices and feedback

Open the linked U03-N06 activity for the four-minute live demonstration. First run the collapsed setup cell using the notebook Run control or Run All Cells. Select a classification for every table. Submit a prepared set containing one deliberate mistake, read the feedback, request a hint, and correct the practice answer. Then choose Try another case and classify the different tables. Explain the resulting progress label. The first screenshot is an individual case register. The second is a different-case table. These embedded screenshots provide a fallback if the live site cannot load. Say explicitly when showing the recorded example.
The pool has three different-case sets. Rehearse with a separate disposable demonstration browser profile. Preserve genuine learner work.
Direct demo: https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=notebooks/u03-n06-case-or-aggregate.ipynb
Screenshots captured from that public activity on 23 October 2026.

## 11. Your learning record and reflections

Use the screenshot to show the reflection question, the entered reasoning, the Record button, and the save confirmation. Learners must select Record to retain their writing in the browser record. The writing is unscored and does not automatically change capability estimates. My learning record displays submitted attempts and task progress alongside recorded reflections. Storage belongs to the current browser and site. Opening another browser, another device, or another site does not automatically transfer the record. Clearing browser data can remove it. Evidence, reflections, and edited notebooks have separate download routes. These copies do not provide automatic restoration. Explain those details if participants ask, and include them in the handout.
Sources: docs/design/browser-storage.md; current extension and reflection widgets. General browser storage: https://jupyterlite.readthedocs.io/en/stable/quickstart/using.html
Screenshot: invented demonstration reflection captured 23 October 2026.

## 12. Learning with a facilitator

Offer these prompts during the same surveillance-table exercise. The first asks for an explanation of the data rather than recognition of a label. The second asks the learner to connect feedback to a revision. The third connects the learning activity to field practice and the need to verify a report. Participants can first answer individually and then compare explanations in pairs. Facilitators can listen for misunderstandings and choose examples for a group discussion. The browser-local record belongs to the learner. This prototype does not provide an automatic facilitator dashboard or upload learner records to an instructor.
Source: proposed field facilitation approach; current course reflection prompts and storage design. No claim of demonstrated learning effectiveness.

## 13. Epidemiologists as course authors

This slide changes the audience's role from completing the course to producing its next version. Epidemiologists contribute knowledge of field work, realistic questions, public health meaning, and appropriate local examples. They can use an approved AI assistant alongside the course to help draft explanations, code, controls, and checks. The AI authoring assistant is separate from this prototype's deterministic adaptive-learning extension. No conversational AI model is embedded in the current learner workflow.
Use this actual kind of problem from development: a reflection prompt says Write your reasoning, but offers no response field. A contributor can specify a text field, an explicit Record action, and restoration after reload. Ask for one bounded change and its review steps. Supply invented data. Describe the intended learner outcome so that the contributor can evaluate the proposed implementation. Participation can begin by specifying and reviewing an improvement with a maintainer, without independently managing the publishing tools.
Sources: course development history; docs/audit/pre-field-test-audit.md, response-widget findings; docs/design/browser-storage.md. The suggested authoring workflow is a practical proposal, not a validated learning result.

## 14. A typical improvement workflow

Describe the workflow we have used in this course in terms a field epidemiologist can participate in. First identify one learner problem, naming the notebook and including the exact sentence or a screenshot with invented data. State what the learner should be able to do. Next ask the AI assistant to inspect the current material and propose a small change before editing. Inspect the actual source and any supporting references. Revise the source and regenerate the notebook where the course uses generators.
Try the revised activity in the local browser as a learner: use a correct answer, an incorrect answer, and an incomplete response. Check that feedback explains the outcome. For a reflection, record text and reload to check that it returns. Review the public health meaning with an epidemiologist and have a colleague try the activity. Record what changed and why. After course-owner review, a maintainer commits, pushes, publishes, replicates, and checks the public site with a fresh browser profile as well as preservation of returning learner work. A successful build alone does not establish useful teaching. Keep the contributor's field judgment visible throughout.
Sources: this course's implemented review and release workflow; docs/audit/pre-field-test-audit.md; AGENTS.md source/generation, preview, and release requirements. This is a practical contributor workflow adapted from development experience.

## 15. Reviewing an AI-assisted contribution

AI can propose plausible but wrong content, code, or citations. Epidemiologists provide the domain review that checks what a revised activity actually means. Use the earlier development example: an eight-year-old cannot correctly receive the category under 5. A program running without an error does not show that its categories match the public health question. Compare the data, expected answer, explanation, and actual feedback. Read each cited source to confirm that it supports the claim. Have a colleague attempt the activity without coaching and note where they hesitate.
Keep a short explanation of the change, the source checked, and the checks performed with the revised activity. A course owner reviews the contribution before release. These actions apply to improving teaching materials. Use invented training data and the organization's approved AI tools and sharing process. Do not imply that the current course automatically transmits content to an external AI service.
Sources: course development history and pre-field audit. General supporting guidance: NIST AI 600-1 (2024), sections 2.2 and MEASURE 2.5, including review of generated sources and citations. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf (checked 23 October 2026). The local workflow is our adaptation, not a NIST certification.

## 16. Questions for the field test

Invite participants to try the public course and comment on the instructions and feedback. Ask whether they could find the starting point, understand the task, interpret the feedback, choose a next step, and explain an unfamiliar example. Observe what they do and ask them to explain their reasoning. Successful software checks establish observed application behavior. Field observation is needed to assess clarity, usability, and learning. Record proposed improvements separately from demonstrated outcomes.
Course start: https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=notebooks/u00-n00-start-here.ipynb
Technical references: https://jupyterlite.readthedocs.io/en/stable/ and https://jupyterlite.readthedocs.io/en/stable/quickstart/using.html
Course references: FETP Public Health Informatics course materials used with permission, acknowledged in Notebook 00 References. Internal planning evidence: docs/audit/pre-field-test-audit.md and docs/design/classification-reassessment-pilot.md.
Presentation prepared 23 October 2026. The screenshots contain invented data and demonstration responses.
