# Widget interaction plan for FETP notebooks

*2026-10-08 - Design and one browser-tested pilot*

## Current Python submission contract — 2026-10-22

All scored Python tasks now use an explicit **Submit** action with inline feedback.
Run All initializes controls without submitting. Units 1 and 3 Notebooks 2–4 retain
visible learner computation, with a separate collapsed Submit cell. Units 4–14
collect their current controls and show the resulting artifact on submission.
**Record** remains the separate unscored reflection action. Existing R alternatives
are deferred. The older planning tables below retain design history; current
acceptance and validation status are in the [pre-field test audit](../audit/pre-field-test-audit.md).

## Contents

- [Interaction and evidence contract](#interaction-and-evidence-contract)
- [Current local notebooks](#current-local-notebooks)
- [Planned local notebooks](#planned-local-notebooks)
- [UCSF source readings and external knowledge checks](#ucsf-source-readings-and-external-knowledge-checks)
- [Can learners reorder a workflow?](#can-learners-reorder-a-workflow)
- [Rollout gates](#rollout-gates)

This plan complements the [course notebook enrichment inventory](https://github.com/adaptive-learning-network/fetp-phi-course/blob/main/docs/notebook-enrichment-plan.md). It assigns an interaction to each local notebook concept so learners can make choices without writing Python for a classification task, while retaining code where the learning objective is to manipulate data. The existing U03 N01 Python notebook is the first implementation: six cards can be dragged into Data or Information bins. Each card also has a keyboard-accessible Move to menu. Its browser test covers incomplete, incorrect, and correct retries with the adaptive record. Other rows below are proposals until built and tested.

## Interaction and evidence contract

1. **State the learning objective first.** Use a choice widget when recognition or judgment is the target; use code when the target is calculating, transforming, querying, or validating data. A widget may select parameters for a code task, but it must not silently do the target work for the learner.
2. **Keep the source and answer separate.** Display the course slide or case prompt beside the control. Use opaque answer IDs in widget values; render readable labels. Compute expected answers from the local fixture when possible. Never place the answer in client-side feedback before submission.
3. **Submit an explicit attempt.** A changed widget value is draft state. In the pilot, the learner runs a short **Check my choices** cell; that cell reads values into the existing answer variable, and the Learning panel executes the existing check in the Python Jupyter kernel. The learner can change a control and run the same cell again. Widget creation belongs in the preceding setup cell so a retry does not reset selections.
4. **Record attempts, not every click.** An unanswered required control yields `incomplete`; a submitted wrong answer yields `incorrect`; a correct answer yields `correct`. The adaptive-learning engine retains every submitted observation, but only qualifying correct work contributes capability evidence. Hint use, activity identity, and evidence stage follow the catalog rule. Unsubmitted selections, hover, navigation, and time on task are not scored telemetry.
5. **Match claims to evidence.** A selected answer can demonstrate recognition or a bounded simulation decision. It cannot establish field proficiency, explain a learner's reasoning, or prove that a live system was used. A free-text justification or discussion can remain ungraded, or receive a documented human review; do not silently score prose by keyword.
6. **Keep access and privacy local.** Use synthetic data; do not put personal or patient information in widget labels, values, URLs, or saved notebook outputs. Give every control a visible prompt and a keyboard route. Check empty/default states, reset, repeated submission, returning browser sessions, and the exported learner graph.

Core `ipywidgets` includes [radio buttons, dropdowns, checkboxes, multiple selection, sliders, text and numeric inputs, buttons, and containers](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html). Its [button and value events](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html) can update local displays, but the current adaptive observer records **exercise-cell execution**, so a button callback alone is not a recorded attempt. The [JupyterLite Pyodide package guide](https://jupyterlite.readthedocs.io/en/stable/howto/pyodide/packages.html) notes that widgets also require a frontend extension. This site bundles `jupyterlab_widgets` and [`anywidget`](https://docs.anywidget.dev/) in the build environment and checksum-pinned Python wheels in its local `pypi` index; U03 N01 installs them into the browser-local Python Jupyter kernel on first use. The custom bin widget sends assignments to Python, and the collapsed setup cell displays the interface while hiding its infrastructure code.

## Current local notebooks

| Notebook | Interaction | What a submitted attempt can show |
| --- | --- | --- |
| U00 N00 start here | `Accordion` for orientation sections and links; an optional unscored "find the Learning panel" self-check | Navigation only; no capability observation. |
| U01 N01 data to decision, Python | Candidate: district `Dropdown`, weekly-change `IntText`, first-action `RadioButtons`; retain the ungraded justification | Correct district, computed change, and cautious action. A choice alone does not justify the action in prose. |
| **U03 N01 data or information, Python** | **Built:** drag six cards into Data or Information bins, or use each card's Move to menu; run **Check my choices** after sorting | Classification of all six examples. Incomplete, wrong, and corrected attempts remain distinct. |
| U03 N01 data or information, R | Current typed vector; later parity candidate after an R-compatible control and observer path are tested | Same classification criterion; do not claim widget parity yet. |
| U03 N02 explore dataset, Python/R | Keep code for counts, minima, maxima, and unique locations; optional `Dropdown` to choose a preview variable | Dataset exploration from the actual register, not recognition of a prefilled answer. |
| U03 N03 filter records, Python/R | `Dropdown` for district and period plus code that applies the selected filter; show matched row IDs | A correct filtered set, including boundary conditions; merely choosing a filter is weaker evidence. |
| U03 N04 coverage, Python/R | `Dropdown` for numerator/denominator definitions; retain numeric calculation and interpretation | Correct measure and calculation; distinguish numerator or denominator errors from arithmetic errors. |
| U03 N05 machine readable, Python | Implemented: three `RadioButtons`, no initial selection, Submit, and inline explanatory feedback | Existing single-value-rule assessment; incomplete and incorrect retries are recorded. R remains a typed answer, deferred. |
| U03 N06 case or aggregate, Python | Implemented: Case-based / Aggregate radios for each of five tables, one Submit, and per-table feedback | Existing aggregate-table assessment; unanswered classifications remain incomplete. R remains deferred. |
| U03 N07 guided district summary, Python | Implemented: five explained runnable steps with readable tables, final Submit, and Record reflections | Completion of the supplied retrieval/summary workflow; does not establish independent API programming. |
| U03 N08 my learning record, Python | Live browser-rendered tables with Refresh; no executable reporting code | Read-only attempts, progress, recommendations, and saved reflections from the current local record; opening or refreshing adds no observation. |

## Planned local notebooks

The interaction is a candidate design, not a claim that a notebook or widget has been built. Notebook names and scope follow the [enrichment inventory](https://github.com/adaptive-learning-network/fetp-phi-course/blob/main/docs/notebook-enrichment-plan.md).

| Notebook | Candidate widget interaction | Target evidence or explicit limit |
| --- | --- | --- |
| U00 N01 course aims | `Tab` for cast, course route, and source links | Orientation only. |
| U02 N01 system map, Python pilot built | Two `Select` lists with **Move up** and **Move down** buttons order case and laboratory reporting paths | Each route starts at its source record, reaches the district HIS, and ends at MOH. The access-permissions reflection remains unscored because the source diagram does not define those permissions. |
| U02 N02 application fit | Need-by-feature `RadioButtons`; `SelectMultiple` for constraints | Reasoned system fit against a local feature matrix, not product certification. |
| U03 N09 information-needs plan | Ordered workflow controls for question -> population -> place/time -> variables -> output; short `Text` fields | Complete, coherent plan; human review for open-ended wording. |
| U04 N01 source inventory | Source `Dropdown` and grain/provenance `RadioButtons` | Correct source choice and limitations. |
| U05 N01 access decisions | Role-by-task `Dropdown`s or radio matrix | Minimum access justified by the synthetic task. |
| U05 N02 safe release | `Checkbox` for disclosed fields and `RadioButtons` for release decision | Detecting a risky extract; require all relevant risks, not one guessed checkbox. |
| U06 N01 AI use and review | `RadioButtons` for suitable task; `SelectMultiple` for required human checks | Review plan for a supplied output; no live model claim. |
| U07 N01 form design | Field-type `Dropdown`, required `Checkbox`, allowed-value `TagsInput` | Coherent schema; validate IDs, types, and required fields in the local fixture. |
| U07 N02 validation | Toggle between synthetic submissions; run validation code and inspect messages | Application of rules to good and bad records, not merely selecting which looks wrong. |
| U08 N01 quality audit | Metric `Dropdown` to inspect completeness, validity, timeliness, duplicates; code computes each rate | Correct calculations and interpretation. |
| U08 N02 correction log | Suspect-record `Dropdown`, correction `Text`/`DatePicker`, reason `RadioButtons` | Preserved original and defensible correction; check date control support in target browsers. |
| U09 N01 data dictionary | Type `Dropdown`, required `Checkbox`, allowed-value `TagsInput` | Consistent field definitions and constraints. |
| U09 N02 value map | Source-code-to-standard-code `Dropdown` pairs; explicit "unmapped" option | Correct mapping and recognition of unresolved codes. |
| U10 N01 table design | Entity/field assignment controls and key `RadioButtons` | Correct table grain and keys; code or diagram checks relationships. |
| U10 N02 data flow | Ordered stage controls and source/destination `Dropdown`s | Valid route through collection, storage, access, and reporting. |
| U11 N01 recode reshape | `Dropdown` to choose recode rule; retain transformation code | Correct transformed values and shape. |
| U11 N02 transformation check | `Checkbox` for reconciliation tests; run the actual checks | Detecting missing, duplicated, or changed rows. |
| U12 N01 link records | Candidate-match `RadioButtons` plus code that joins synthetic tables | Correct matches, duplicates, and unmatched records; no real patient linkage. |
| U12 N02 exchange contract | Required-field and code-map controls; local validation button or cell | Contract conformance of a synthetic import, not a live POST. |
| U13 N01 analysis visualization | Variable and grouping `Dropdown`s; retain aggregation and plot code | Correct person/place/time summaries and suitable visual form. |
| U13 N02 dashboard critique | Indicator, denominator, audience, and update-cadence `Dropdown`s; optional layout ordering | Justified dashboard design against supplied criteria. |
| U14 N01 interpret with AI | Claim-by-claim `RadioButtons` and uncertainty `Checkbox` list | Detecting unsupported claims, bias, and disclosure risks in a static draft. |
| Conditional communication N01 | Audience/channel/release-level `Dropdown`s | Appropriate dissemination choice after its course home is decided. |
| Conditional communication N02 | Ordered brief sections with `TagsInput`; `Textarea` for narrative | Structure can be machine-checked; narrative quality requires review. |

## UCSF source readings and external knowledge checks

The existing Unit 1 and Unit 2 source pages and the 37 pending UCSF imports remain **unscored readings**. A slide wrapper can use `Accordion` to put the source deck link and local visual together; a lesson can use `Tab` to move among short sections; an assignment page can offer an optional reveal-after-attempt `Button`. These are reading aids, not local evidence. The reading index can use unit `Dropdown` navigation without recording a capability. Keep external Google Forms quiz links as links: opening one does not report a quiz result to the adaptive-learning engine. If a source prompt becomes a scored local activity, create an explicit activity, answer contract, check, and provenance link rather than retroactively scoring the reading page. Embed local teaching graphics as notebook attachments so browser-saved notebooks retain them.

## Can learners reorder a workflow?

**Yes.** Core ipywidgets 8 includes [`TagsInput`, whose tags can be dragged to reorder](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html#tag-widgets). Its `value` is the submitted sequence. For a workflow exercise, fix a clear starting point, require every step exactly once, and check the resulting order or documented partial-order constraints. A surveillance *cycle* has no inherent first step, so the prompt must specify the scenario's starting event before scoring a single linear sequence.

```python
import ipywidgets as widgets

steps = ["Detect", "Collect", "Analyze", "Interpret", "Communicate", "Act"]
order = widgets.TagsInput(value=steps, allowed_tags=steps, allow_duplicates=False)
display(order)

# In a separate, observed submission cell:
submitted_order = list(order.value)
complete = len(submitted_order) == len(steps) and set(submitted_order) == set(steps)
```

Drag ordering needs a **keyboard alternative**. A `Select` widget with **Move up** and **Move down** `Button`s can update the same ordered list; both controls must feed one answer variable and one check. This also avoids treating a removed tag as a wrong ordering: missing or duplicate steps are `incomplete`, while a complete but incorrect order is `incorrect`. We should browser-test mouse, keyboard, reset, and retry behavior before using ordering as scored evidence. A custom drag-and-drop extension is unnecessary for the first workflow pilot.

## Rollout gates

- Apply the U03 N01 pattern only to a second classification notebook after the pilot has been reviewed. Keep the R notebook's current typed task until an R-compatible widget path is validated.
- For each new scored widget, test untouched, partially answered, wrong, corrected, repeated-correct, and hint-heavy submissions; check the learner record and next recommendation. Confirm that reopening a saved notebook does not silently submit or reset an attempt.
- For workflow ordering, validate completeness and either an exact sequence or explicitly allowed alternatives. Score an explanation separately only with a defined rubric and human review.
- Reuse the slide graphic and course wording from the inventory. A widget is an input method; source parity and educational effectiveness still need separate review.

## U03 N05 implementation - 2026-10-19

The Python single-value question now uses three radio options and Submit, with no placeholder option and no preselected answer. The submitted value uses the existing assessment and activity ID through `al.submit`; feedback appears beside the question and explains why a selected rule is correct or incorrect. Scoped controls preserve the submitted value while checking. Radio labels wrap within their rows, and the infrastructure cell remains collapsed after execution. The existing R answer/check is unchanged.

Validation: Chromium passed no-selection, incorrect, repeated incorrect, and correct submissions, checking inline explanations and all four stored outcomes. Correct submission demonstrated the existing machine-readable capability. No radio option is initially selected. The setup code remained collapsed, and a screenshot at a 1000-pixel viewport was visually inspected for wrapping and overlapping controls. The U03 N01 sorting/Submit regression also passed. The local review preview was rebuilt and verified against the assembled U03 N05 notebook.

## U03 N06 implementation - 2026-10-19

Each of the five course table descriptions has Case-based / Aggregate radio choices with no initial selection. One Submit button captures all five classifications; any missing answer remains incomplete. Completed responses use the existing aggregate_tables check and activity ID. Inline feedback marks each table correct or incorrect and explains individual records versus grouped counts. Choices are scoped, disabled during submission, and can be changed for retries. Setup code stays collapsed. R is unchanged.

Validation: Chromium passed untouched, partially answered, incorrect, repeated incorrect, and corrected submissions, preserving all five observations and demonstrating the existing capability after success. The local preview matches the assembled notebook. A narrow-viewport screenshot was visually inspected for wrapping and overlap.
