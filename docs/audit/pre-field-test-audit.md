# Pre-field test audit: Python informatics notebooks

**Review date:** 22 October 2026

**Scope:** All 22 assembled Python learner notebooks, course navigation, feedback, reflections, learner-record display, and local application resources. Existing R alternatives are deferred.

**Status:** Baseline review with P1 and P2 remediation records below. Publication and learner-effectiveness validation are separate steps.

**Snapshot:** Working tree based on `5c83970`, including the current uncommitted course revisions. This is not an audit of that commit alone or of a published release.

## P1 remediation — 22 October 2026

The baseline findings below describe the pre-fix review. **C01–C05 are resolved for the supplied Python course and local review preview.** C06–C09 and C11 were the P2 follow-up findings; see the implementation record below. C10's obsolete README route was corrected as part of the navigation cleanup. This does not establish learning effectiveness or approve a production release.

| Finding | Change | Acceptance evidence |
| --- | --- | --- |
| C01 | Explicit questions tied to each canonical dataset; imported procedural bullets, repeated written projects, and separate exploration CSV task removed from the learner route. Source concepts remain mapped in the coverage inventory. | Assembly tests check for absent question numbers, procedural nonquestions, and the second dataset. |
| C02 | Explicit Submit with inline feedback for every scored Python task; computation remains visible, assessment infrastructure stays collapsed. Run All initializes controls without submitting. Failed checks show the error and allow retry without adding an observation. | Native metadata/syntax checks and browser retry/Run All scenarios pass, including the guided and all Units 4–14 workflows. |
| C03 | Full linked 22-notebook contents and explicit onward links, including learning record → Unit 4. Sidebar uses Python and ignores an old R preference. | Link validation, all 22 contents destinations, actual notebook-link navigation, and old-R-preference Open behavior pass. |
| C04 | External Unit 3 form removed from the catalog/sidebar. Its identity and pending export-review disposition remain in the course form-link audit. No new quiz key invented. | Catalog validates against the ontology; native catalog and browser absence checks pass. |
| C05 | Export evidence explicitly excludes writing; Download reflections creates a readable text file with recorded answers, questions, and save times. Notebook edits and restoration limits are explained, including in Reset. | Native export preservation/nonmutation and actual browser download/content checks pass. Reset cancellation retains the saved reflection after reload. |

Validation for the remediation: **22 native Python tests, 24 Node engine/identity/export tests, and 39 distinct Chromium scenarios pass.** The browser scenarios passed as an initial group of 27 and a targeted continuation of 12 after updating obsolete content expectations (the removed exploration heading and revised reflection count). R and two OIDC runtime scenarios remain excluded. All supplied Python cells compile; catalog and RDF export conform to the ontology shapes; the 48-authoring-notebook references check passes.

The active local review preview matches all 22 assembled Python notebook files. Its configured frontend loader also matches the current compiled extension bytes. The review uncovered an older installed shared-data extension entering a new site build: `scripts/sync_labextension.py` now synchronizes the compiled frontend before site generation, and a browser regression guards the loader/hash agreement. Windows extension-loader URLs are normalized. The GitLab build artifact now includes the compiled extension for that comparison in its separate browser job; CI itself was not run during this local remediation.

A targeted Unit 4 rerun also passes the explicit inline-feedback assertion. Its Submit → computed table → Correct feedback screenshot and recorded-response view were visually checked at the 1,050-pixel review width; text wraps without overlap. This spot check is not an accessibility conformance review.

The cleanup also removes the obsolete README learner-route paragraph (C10). At the end of P1, stable question IDs and preservation across substantive prompt revisions (C11) remained future work; P2 addresses that update risk below. Existing stored reflections are not cleared. The reflection download preserves all currently recorded sections, including older sections no longer shown as a task.

## P2 remediation - 22 October 2026

Implementation covers C06-C09 and C11. C10 was already corrected during P1. Course-owner review of provisional keys, objectives, and capability interpretation remains required before a field trial; software checks do not replace that review.

| Finding | Implemented change | Evidence |
| --- | --- | --- |
| C06 | Separate observable objectives for filtering, vaccination proportion, combined-value cells, and table classification. Units 1, 7, 9, 10, and 13 describe the selection/review work actually performed. Capability labels agree with those tasks. Progress explicitly describes practice performance, not certification of independent proficiency. | Catalog SHACL validation; generated objective/task review; engine regression. |
| C07 | U03 N02-N04 show register rows, a supplied-code route, and runnable summaries. Filtering proceeds from one condition to combined conditions, displayed matching rows, and count. Coverage reconstructs the supplied 92% example using 46 distinct qualifying children / 50 eligible children, with the dates, scope, proportion, percent, and training assumptions displayed. Copying/sorting promises absent from these tasks were removed. | Native execution of all three examples checks their results against the source records. Browser incomplete/incorrect/correct retries retain visible computation and explicit Submit. |
| C08 | Shared checkbox groups replace modifier-key multiselect in Units 4-14. Count fields start blank; non-whole-number entries remain unanswered with an explicit instruction. Submission shows each decision, its result, and the evidence to inspect before the artifact. U03 classification gives item-level reasons and sample table rows. | Shared collector/locking and numeric-input tests; browser keyboard selection, per-question feedback, retries, and narrow-layout checks. |
| C09 | Units 1 and 2 use the canonical scenario rather than appended duplicate lessons; the second HIS diagram and repeated setup were removed. Unit 1 concept images and slide decks are optional deeper material after the task/reflection. Unit 8 no longer presents a historical national strategy as current. Interpreting a pattern is distinguished from establishing cause. | Assembly/dependency checks; learner-source review; local visuals and notebook navigation regression. Markdown totals are 853 words for Unit 1 and 1,904 for Unit 2, including optional slide-page listings; the opening narratives are 332 and 343 words respectively. |
| C11 | Registered stable question IDs and meaning versions; wording-only updates restore answers by identity. Changed meanings start blank with a review notice. Record preserves earlier writing, earlier prompts/times, removed questions, and separate meaning versions. Exact legacy migration is limited to version 1; unmatched legacy answers remain available in record view and download. | Pure merge/export tests cover wording, new meaning, legacy entries, removed questions, intentional clearing, and immutability. Browser tests cover restoration and readable download. See [question identity](../design/reflection-question-identity.md). |

**Validation:** 26 Python tests and 28 Node tests pass. All supplied Python code cells compile; 48 authoring notebooks pass the References check. The catalog and exported learner evidence conform to the ontology shapes.

**42 distinct Chromium scenarios pass**, one worker, excluding the deferred R scenario and two OIDC scenarios. The final browser verification comprised 24 passing scenarios, followed by an 18-scenario continuation after updating a stale Unit 1 assertion from the former Justify capability label to Select. Earlier runs exposed the blank-viewport problem described below and a test-fixture audience error; those failures were resolved before this evidence was recorded. A transient local-server connection failure was also rerun successfully. This is a bounded software regression, not a learner-effectiveness result.

A reproduced blank viewport while scrolling past collapsed media was corrected by setting JupyterLab notebook windowing to `none` for these short teaching notebooks. The visuals/PDF navigation test passes with that setting. The final local preview uses `p2-review-v5`, on ports 8774 (VS Code review) and 8765 (tests). All 22 assembled Python notebooks byte-match the supplied local copies. No browser learner storage was cleared. The final small change to incomplete-answer wording was checked in all eleven later-unit workflows on this preview.

Browser checks include ordinary checkbox clicks, Space-key selection, empty numeric fields, explanatory feedback, retries, Run All without manufactured attempts, reflection history/download, fresh and returning notebook saves, plots, and reload persistence. Unit 4 and Unit 8 feedback tables were visually inspected at the 1,050-pixel review width; the visible text wraps without overlap. Full keyboard/screen-reader conformance and Firefox/WebKit validation remain outside this result.

These changes do not add the optional editable Unit 7 test record or the Unit 13 count/share toggle. Those remain bounded follow-on ideas rather than P2 acceptance requirements. No learner storage is cleared and no publication is performed by this work.

## Contents

- [Readiness assessment](#readiness-assessment)
- [Review method and evidence](#review-method-and-evidence)
- [Consistency findings](#consistency-findings)
- [Notebook-by-notebook review](#notebook-by-notebook-review)
- [Quick improvements to interactivity](#quick-improvements-to-interactivity)
- [Before the first field test](#before-the-first-field-test)
- [Field-test questions](#field-test-questions)
- [Validation limits](#validation-limits)

## Readiness assessment

The course has one supplied Python notebook sequence, local teaching visuals and slides, functioning examples of inline submission, and browser-local reflection storage. Units 11–14 now provide their own records and worked examples. These are useful foundations for an observed learner trial.

**At baseline, the P1 findings required resolution before an independent learner field test.** See the remediation table above for current implementation and validation status. A successful software regression run alone does not establish that an epidemiologist can follow the narrative or interpret the feedback without help.

For a facilitated usability session before those fixes, explicitly identify the unfinished interactions, preserve browser storage, and observe the points of confusion. Do not interpret completion of these guided exercises as independent professional competence.

Priorities used here:

| Priority | Meaning |
| --- | --- |
| P1 | Resolve before independent learner testing: likely to interrupt the route, confuse the task, or misrepresent retained work. |
| P2 | Make the change where practical before testing; otherwise observe it deliberately. |
| P3 | Useful follow-on improvement; not a reason to delay an observed pilot. |

## Review method and evidence

Reviewed the Markdown narrative and interaction setup in every assembled Python notebook, their authoring generators, the assembly rules, catalog, sidebar, record export, and existing browser tests. The review follows the current learner artifact rather than treating the authoring readings as a second course.

The table below records the **baseline** results; current remediation results are above.

| Check | Evidence on 22 October 2026 |
| --- | --- |
| Learner inventory and local preview | 22 Python notebooks; all 22 assembled files byte-match the copies supplied by the active local review preview. Persisted browser documents are a separate layer. |
| Notebook structure and dependencies | Assembly validation passes: naming, unique cell IDs, final References, retired-path checks, and local Markdown dependency targets. No missing Markdown attachments found in the 22 Python notebooks. |
| Python syntax | All code cells in the 22 supplied Python notebooks parse with top-level await support. This is not execution validation. |
| References check | `scripts/add_course_references.py --check`: 48 authoring notebooks checked; none need a References change. This count includes authoring material and existing R variants, not 48 learner notebooks. |
| Native Python regression | `python -m unittest discover -s test -p 'test_*.py'`: 20 tests pass. |
| Engine and identity regression | TypeScript test compilation succeeds; explicit Node test files: 23 tests pass. |
| Browser regression | 35 Chromium tests pass in 15.7 minutes, one worker; Playwright's last-run status is `passed` with no failed tests. R and two OIDC scenarios are excluded from this audit run. |

Browser coverage includes local application assets, unavailable-check recovery, integrated quiz/reflection controls, review-versus-learner updates, guided DHIS2 and missingno, register exploration, local materials, live record restoration, Unit 3 choice widgets, Unit 1 retries, Unit 2 pathways, fresh/missing-directory/Windows-path saves, and Units 4–14 choices, retries, recommendations, recorded reflections, and reloads. See [browser tests](../../ui-tests).

Run selection: `playwright test --grep-invert 'R: coverage|linking stores only|verifying with a different account'`, using the active local preview and skipping the mock OIDC server. The Windows PowerShell wrapper reported exit status 1 after treating a Node `NO_COLOR`/`FORCE_COLOR` stderr warning as `NativeCommandError`; the completed Playwright report says all 35 tests passed. This warning is a harness issue, not a failed notebook assertion. No optional repeat of the entire suite was performed solely to remove that warning.

The notebook Markdown contains only four distinct external URLs: three optional YouTube videos in Unit 1 and an optional Seaborn reference in Unit 13. This is a local dependency scan, not a fresh availability check of those destinations. The sidebar has an additional external Google Form, covered in C04.

Spot-checked screenshots from this run: Unit 2 pathway lists and feedback, Unit 3 Notebook 5 radio choices and explanation, and Unit 4 controls at a 1,050-pixel browser width. These show working examples of the existing interaction patterns; this is not a visual review of every output in all 22 notebooks.

Primary evidence:

- [Assembly rules](../../scripts/assemble_course.py), particularly `prompts`, assignment integration, and source-to-destination mappings.
- [Core exercise generator](../../scripts/make_exercises.py), [Unit 1 generator](../../scripts/make_unit01_pilot.py), [Units 4–8 generator](../../scripts/make_units04_08.py), [Units 9–14 generator](../../scripts/make_units09_14.py), and [local linking/analysis examples](../../scripts/local_linking_analysis.py).
- [Sidebar](../../src/extension/panel.ts), [execution observer](../../src/extension/observer.ts), [learner store](../../src/extension/store.ts), [record view](../../src/extension/record-view.ts), and [RDF export](../../src/engine/export.ts).
- [Source coverage map](unified-course-coverage.json), [earlier notebook content review](learner-notebook-content.md), and [comic portrayal review](comic-portrayal-review.md). These retain provenance and prior review detail; they do not substitute for the current assembled-notebook review.

## Consistency findings

### C01 — P1: finish adapting imported assignments into the current task

**Observed:** Unit 2 has two consecutive sections titled “Apply the decision,” followed by a written case study that repeats several later assignments. Its recorded prompts still ask how learners will use Excel. Unit 3 Notebook 2 has both an immunization `register` exercise and a separate case-register CSV task; its imported reflection prompts include “Answer Question #3” and “These are easy to follow, step by step instructions with screenshots.” Unit 9 has “Answer Questions 4 and 5.” Unit 8 still asks learners to use Excel to fix data quality problems after presenting a Python quality audit.

The assembler's `prompts()` function turns list items into response fields. It cannot distinguish an actual reflection question from a procedural instruction. Providing a text box for every extracted bullet does not make the assignment coherent.

**Change:** Author the prompts for each destination explicitly. Retain one set of data, one decision, and one reflection sequence per topic. Replace cross-assignment question numbers and Excel instructions with questions about the table or artifact visible in that notebook. Move wider project questions to a clearly optional transfer exercise with all required data supplied. Retain provenance in the coverage map.

**Acceptance:** Every response field asks an answerable question; no required question refers to an absent worksheet, numbered assignment, or different dataset. Unit 2 no longer repeats the later data-preparation project as its main written case study.

### C02 — P1: make submitting and receiving feedback consistent

**Observed:** Unit 2 and Unit 3 Notebooks 1, 5, 6, and 7 use a Submit interaction. Unit 1, Unit 3 Notebooks 2–4, and Units 4–14 still assess execution of a code cell. Later notebooks require learners to select widgets and then locate and run a separate “Check my work” cell. The sidebar's generic incomplete message also says to run the check cell, including when a task uses Submit.

The Units 4–14 browser tests deliberately Run All with untouched answers and expect an Incomplete observation. That behavior is currently tested, but it mixes initialization with an intentional learner submission. It can make attempt counts harder to interpret during a field trial.

**Change:** Use **Submit** for choice/numeric review tasks, **Record** for unscored writing, and visible execution for computation that the learner is meant to understand. Show task-specific feedback next to the submitted artifact. Initialize controls without recording an attempt; record only an explicit submission. In code exercises, keep the computation visible and make the intentional submission step clear.

**Acceptance:** Run All displays controls without creating an unanswered attempt. An explicit wrong submission, revision, and correct submission produce two attempts and current inline feedback. Setup code stays collapsed. A computation exercise still exposes the relevant computation.

### C03 — P1: complete the course route and remove unavailable destinations

**Observed:** Notebook 00 names early notebooks as code text, while its clickable continuation list covers Units 4–14. It lacks a complete clickable inventory of Unit 3 Notebooks 2–7. Unit 2 says to use recommendations rather than providing an obvious next notebook. Unit 3 Notebook 7 leads to the record view, and that view has no explicit next link to Unit 4. The sidebar says that Course start contains the course order.

The sidebar always offers Python and R. Its `open()` method silently does nothing when the selected language has no notebook path; many activities are Python-only.

**Change:** Add one complete, ordered, clickable contents list to Notebook 00. Give each notebook an explicit next destination and Course start link, including record view → Unit 4. Offer Python only for the current pilot, or disable unsupported language destinations with an explanation. Keep the existing R files deferred.

**Acceptance:** A fresh learner can follow all 22 notebooks using visible links without relying on the file browser or adaptive recommendations. Every enabled Open button has a valid destination.

### C04 — P1: remove the remaining external assessment route

**Observed:** [Unit 3 catalog](../../catalog/informatics-unit-03.trig) still declares `https://forms.gle/Y4yG5gMbFznczrBd9`. The sidebar opens it in a new tab and states that its results are not recorded. The browser test intercepts the URL with a stub page; passing that test establishes opening behavior, not form availability or content equivalence.

**Change:** Verify this form against the [course form-link audit](../../../fetp-phi-course/docs/audit/form-links-audit.md) and exported materials. Replace the sidebar destination with its appropriate local practice interaction, or remove the learner-facing entry while the contents are unresolved. Do not create an invented answer key to fill the gap.

**Acceptance:** No course assessment requires Google Forms. Optional reference links remain clearly optional. The dependency audit records the original destination and disposition.

### C05 — P1: correct the promise made by “Export record”

**Observed:** Notebook 8 tells learners to export before clearing browser storage. Reflections are present in `LearnerRecord.reflections` and the live record view, but `exportNQuads()` does not serialize their text. The README documents this limit; the learner instruction does not. Exporting is therefore not a complete backup of the work visible in the record view.

**Change:** Immediately state what the current export contains and that it excludes written reflections. Provide a separate local download of reflections, or a versioned learner backup containing them. If restoration is offered, specify and test its behavior before describing it as a backup-and-restore workflow. Keep the RDF evidence export available for its current purpose.

**Acceptance:** A learner can identify what will survive an export. A recorded reflection appears in the promised downloaded artifact. No instruction suggests clearing storage after exporting an artifact that omits the learner's writing.

### C06 — P2: align objectives, tasks, and claims about progress

**Observed:** Unit 3 Notebooks 3 and 4 share “Combine variables to meet your information needs”; Notebooks 5 and 6 share “See how database organization enables automation.” Unit 9 says Create a dictionary and Unit 10 says Design linked tables, while their scored artifacts are constrained selections. Unit 1's scored artifact supports choosing an action; its written justification is unscored. Units 12–14 are guided review slices, not independent project assessments.

**Change:** Give each notebook one observable action that matches its assessed artifact. Suggested wording: Filter records using several conditions; Calculate a vaccination proportion; Identify a rule violated by a combined-value cell; Classify case-based and aggregate tables; Select field meanings and a code-mapping policy; Select keys and relationships for linked tables. Retain broader creation/design goals only if the learner actually constructs and reviews those artifacts. Describe progress as performance on this practice task.

**Acceptance:** Each objective names the work the learner can demonstrate in that notebook. Course-owner review confirms that provisional quiz keys and capability labels do not imply more evidence than the task supplies.

### C07 — P2: make early computation as approachable as the guided DHIS2 example

**Observed:** Unit 3 Notebooks 2–4 ask for Pandas summaries and a compound filter with little worked syntax. Notebook 2 promises copying and sorting practice, but its scored answer fields primarily check summaries. Notebook 3 mentions sorting, while the actual task checks a filtered count. Notebook 4 gives the 92% statement before asking learners to calculate it; the generator explicitly asserts that the supplied records reproduce 0.92. This is a worked reconstruction, rather than an unseen-answer assessment.

**Change:** Show the register before asking for code. Demonstrate one filter condition, then combine the conditions and display matching rows before counting. In the coverage notebook display numerator, denominator, unit, population scope, and resulting proportion together. State the period and the assumption that a qualifying row represents a distinct eligible child. State that learners are reconstructing the 92% example and check their calculation, not simply recall of the displayed answer. Add a short prerequisite or supplied-code route for learners new to Python.

**Acceptance:** The learner can locate the records being counted and explain the denominator without inventing Pandas syntax. Every advertised operation has a corresponding visible example or task.

### C08 — P2: reduce selection friction and add explanatory feedback

**Observed:** Units 4–14 reuse `SelectMultiple` controls; Unit 4 explicitly requires Ctrl/Command for multiple selections. Numeric controls begin at `-1` as an unanswered sentinel. Checks give a global verdict, even when an artifact preview provides more detailed evidence. The early widget notebooks already demonstrate a simpler selection-and-Submit pattern.

**Change:** Use checkboxes for independent multiple choices. Give numeric blanks a clear unanswered state. Report feedback by question: what was submitted, whether it meets the stated rule, and which displayed evidence to inspect. Keep meaningful incorrect alternatives for retries; do not simply display the whole answer key on initialization.

**Acceptance:** Multiple choices work with ordinary clicks and keyboard navigation. No learner has to interpret `-1` as a meaningful case count. Feedback identifies the decision that needs revision.

### C09 — P2: shorten repeated narrative and clarify source-derived assertions

**Observed:** Unit 1 has approximately 1,560 Markdown words and Unit 2 approximately 2,490, before generated widget text. Unit 2 repeats its HIS diagram and case setup. Unit 1 retains source numbering beginning at 1.3, generic knowledge-check directions, then substantial material after its continuation section. Several Unit 3 notebooks repeat Submit directions in adjacent cells. Unit 8 describes a historical national strategy as “Today,” which may be read as a current operational assertion.

**Change:** Use a consistent order: question → essential explanation → data/example → task → feedback → reflection → optional deeper material → next notebook → References. Consolidate duplicate sections and renumber headings. Identify historical case scenarios as scenarios rather than asserting present national conditions. Review language such as “knowledge uncovers how and why” alongside the later cautions about causal interpretation.

**Acceptance:** Learners can identify the core task without navigating optional decks and duplicate instructions. References retain attribution; editorial and material history stay in repository documentation.

### C10 — P2: bring the README into agreement with the supplied course

**Observed:** The current README correctly describes the unified sequence near the top, but its later source-reading paragraph still says the reading index opens 18 pages and that the remainder of Unit 2 is planned. These statements conflict with the assembled course and could misdirect facilitators preparing a trial.

**Change:** Replace the obsolete learner-route paragraph with current assembly and review instructions. Keep historical counts only in dated audit records. Include this audit in the documentation links.

### C11 — P2: preserve recorded answers when questions are rewritten

**Observed:** The [reflection controls](../../scripts/reflection_widgets.py) correctly show “Changes not recorded” after editing and restore recorded text. However, restoration matches entries by the full prompt text, and recording replaces all entries for that section. Rewording a prompt can leave its previous answer absent from the field; recording the revised section can then replace the older entries. This is a source-derived update risk, not a data-loss event reproduced in this audit.

**Change:** Give questions stable identifiers independent of their wording. Preserve prior answers and the prompt version they answered; offer review when a question changes meaning. Test this alongside the proposed prompt cleanup in C01. Keep disposable local review replacement separate from production learner updates.

**Acceptance:** A saved answer remains discoverable after a wording-only course update. A substantively changed question does not silently inherit an unrelated answer or overwrite its history.

## Notebook-by-notebook review

“Cell” below means the scored submission is triggered by executing a cell. It does not mean that the notebook lacks widgets. Reflections and local practice quizzes are separate from the scored task.

| Notebook | Current interaction | Main consistency issue / quickest useful improvement |
| --- | --- | --- |
| U00 N00 — Start here | Unscored practice execution | Complete clickable contents; explain Submit versus Record; correct export expectations. C03, C05. |
| U01 N01 — Data to decision | Code response; practice quiz; Record fields | Consolidate the long introduction; show inline Submit feedback for the computed decision; distinguish chosen action from written justification. C02, C06, C09. |
| U02 N01 — Reporting pathways | Reorder lists + Submit; quizzes and Record fields | Top-to-bottom display now matches MOH-at-top instructions. Remove duplicate assignment sections and unrelated Excel project prompts; add explicit onward navigation. C01, C03. |
| U03 N01 — Data or information | Sorting board + Submit | Useful drag and menu alternatives. Remove repeated directions; show item-level reasons and a concise completion summary. C08, C09. |
| U03 N02 — Explore dataset | Pandas answer cell; Record fields | Choose the immunization register or case CSV as the primary task; remove extracted nonquestions; supply visible worked summaries. C01, C07. |
| U03 N03 — Filter records | Pandas answer cell | Display data, progressive filter steps, matching rows and count; align objective with filtering. C06, C07. |
| U03 N04 — Coverage | Pandas answer cell | Show numerator/denominator and proportion-to-percent conversion; label this as reconstructing the supplied 92% example. C07. |
| U03 N05 — Machine-readable | Radio choices + Submit | Preserve current working choice pattern; replace “See…” objective and duplicate directions; explain the combined-value violation. C06, C09. |
| U03 N06 — Case or aggregate | Per-table choices + Submit | Show small example tables, not only column lists; refine objective and classification rationale. C06, C08. |
| U03 N07 — Simulated DHIS2 | Supplied stepwise code, tables, missingno, Submit | Strong scaffolding model. Keep simulation explicit; add a small final summary card for district, count, missing dates and known period. C07. |
| U03 N08 — Learning record | Live unscored browser view | Correct export guidance; add onward link and optional self-evaluation reflection. C03, C05. |
| U04 N01 — Data sources | Select controls + check cell | Four required fields now agree with task and checker. Replace modifier-key multiselect and use Submit. C02, C08. |
| U05 N01 — Access and release | Select controls, extract previews, check cell | Retain explicit training suppression rule; use checkboxes and explain why an allowed field may still be unnecessary. C08. |
| U06 N01 — AI draft review | Claim choices + check cell | No live AI needed. Put each claim beside the supporting/missing evidence and give inline feedback. C02, C08. |
| U07 N01 — Form validation | Rule controls, validation results, check cell | Add one editable test record to try the chosen rules; retain valid and invalid test examples. C06, C08. |
| U08 N01 — Quality audit | Counts, repair choice, corrected-copy/log preview | Remove residual Excel assignment. Pair quality counts with a highlighted row/table view; keep source-backed repairs and untouched originals. C01, C08. |
| U09 N01 — Dictionary | Semantics/policy choices, reconciliation preview | Remove absent question-number references. Let learners inspect/edit one dictionary row, or narrow the Create objective. C01, C06. |
| U10 N01 — Tables and flow | Key/relationship/flow choices | Show linked case/lab rows beside key audit; reuse Unit 2 ordering controls for data flow if useful. C06, C08. |
| U11 N01 — Recode | Visible 4/5/8/missing worked example; review controls | Fixed group definitions and supplied rows address earlier ambiguity. Place prediction and recoded result together, with per-answer feedback. C08. |
| U12 N01 — Link/exchange | Visible Pandas tables/joins; review controls | Keep raw five-row join versus four-case checked table. Visually mark C02 conflict and unmatched cases; add Submit. C02, C08. |
| U13 N01 — Briefing | Supplied records, Seaborn plots, review and briefing fields | Keep exact counts and limits next to charts. Allow a small count/share comparison without introducing unsupported rates. C08. |
| U14 N01 — Interpretation | Supported-claim/review choices; Record fields | Keep supplied AI-style draft explicit. Show claim-level evidence and a final link to record review. C08. |

## Quick improvements to interactivity

Implement in this order. These are proposed bounded changes, not time estimates or a commitment to redesign every task.

| Order | Improvement | Reuse / scope | Learner benefit and verification |
| --- | --- | --- | --- |
| 1 | One submission pattern | Reuse the existing widget-submit bridge; pilot Unit 4, then apply to the other choice/numeric tasks. | Immediate local feedback; Run All does not manufacture attempts. Test incomplete, wrong, corrected, and double-click submissions. |
| 2 | Explicit reflection prompts | Replace generic list extraction with authored prompts in the assembly source. | Every field has a meaningful question; no extra worksheet hunt. Review every prompt against its displayed data. |
| 3 | Complete navigation | One contents table plus Next/Course start links. | Learner can continue independently; verify all enabled destinations, including record view → Unit 4. |
| 4 | Checkboxes and per-question results | Shared choice renderer for later-unit review controls. | No modifier keys; clear retry target. Check keyboard operation, long options, narrow notebook widths, and feedback announcements. |
| 5 | A visible computation ladder | Start with U03 N02–N04; show input → transformation → result. | Learner can see why an answer follows from data. Test a deliberate filter error and confirm the displayed rows explain it. |
| 6 | Safe reflection download | Download the actual recorded answers with prompt and save time; clarify current RDF scope. | Learner can retain writing. Verify a known reflection in the downloaded file; do not call it restorable until restoration is implemented and tested. |
| 7 | Predict, run, compare | U07 validation test record; U11 boundary examples; U12 join preview; U13 count/share toggle. | One small exploratory action produces a visible consequence. Keep original records unchanged and label optional exploration unscored. |
| 8 | Review progress in plain language | Record-view summary and optional “What can you now do, and where do you still need help?” field. | Connect attempts and reflections to learner self-evaluation without implying that every practice answer proves competence. |

## Before the first field test

- [x] Close C01–C05 for the supplied Python course and local preview.
- [ ] Have the course owner review provisional quiz feedback, answer keys, objectives, and claim-level explanations.
- [x] Remove obsolete README route instructions and confirm that canonical prompts and next links use the unified notebook sequence.
- [x] Add targeted Python browser coverage for U03 N03 filtering and N04 coverage, including visible computation, explicit submission, and incorrect/correct retries. R runtime coverage remains deferred.
- [ ] Test one fresh learner route from Notebook 00 and one returning learner with recorded reflections and edited code. Existing tests cover individual workflows and selected update/storage cases; they are not a complete uninterrupted 22-notebook journey.
- [x] Verify reflection preservation across edited wording, a different question version, and legacy entries without IDs, including readable download. C11.
- [ ] Check narrow VS Code notebook space, long choices, keyboard-only use, focus after feedback, and screen-reader labels/status announcements. No new accessibility conformance claim is made here.
- [ ] Confirm the production build omits `--course-review`, preserves learner documents during course updates, and exposes no application check/catalog files in the learner file browser.
- [ ] Repeat saved-document and Python-kernel folder checks on the actual field-test host, with a previously saved notebook as well as a fresh browser profile. Do not clear learner storage as an update procedure.
- [ ] Test the intended CDC-network route with optional external sites unavailable. Verify local plotting wheels, images, slide previews, required datasets, and assessments still work. A warm-cache run alone does not establish first-use availability.
- [ ] Freeze a release identifier, record the tested browser and build, then verify the actual deployed artifact before inviting learners. Publication is not part of this audit.

## Field-test questions

Use observed behavior and a short debrief. Keep usability observations separate from scored learning evidence.

1. Can the learner find the next notebook and identify the task without facilitator explanation?
2. Can they distinguish running supplied computation, submitting an answer, and recording a reflection?
3. After an incorrect response, can they locate the relevant evidence and revise for a reason they can explain?
4. Can they explain what one row represents in the displayed data source, the numerator/denominator of a proportion, and why an unmatched laboratory result is not negative?
5. Can they interpret the completeness matrix and one person/place/time chart without treating completeness as accuracy or count as population risk?
6. Can they find a saved reflection after reopening and explain exactly what the export includes?
7. Does the recommendation help them choose what to practice next, and does the displayed record agree with their experience?

Record where help was needed, task completion, incorrect interpretations, time spent searching/navigation, and whether feedback enabled a successful revision. Use invented data only. Do not treat faster clicking or a corrected guided answer as evidence of transfer to independent surveillance work.

## Validation limits

This review concerns current local source and supplied preview artifacts. It does not verify the current public Pages deployment or establish educational effectiveness. Browser regression uses Chromium; Firefox and WebKit are not validated by that result. Two OIDC tests and the R runtime scenario are intentionally outside this Python course audit run. The baseline included 23 Node tests; the P2 result above includes 28, including reflection-history and download tests.

Static file validation does not guarantee rendering, availability on a restricted network, persistence under browser eviction, or accessible interaction. Scripted workflows often seed prerequisites and enter known answers; they establish bounded software behavior rather than independent learner comprehension. The earlier external-form opening test used a stub; the unresolved form entry has since been removed from the learner route. Optional external reference URLs were enumerated, not fetched again for this audit.

WebLLM/browser-local AI remains a documented TODO in the [unified-course design](../design/unified-course.md). It is not implemented, required by the present activities, or a prerequisite for this field test.
