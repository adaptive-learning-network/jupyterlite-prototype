# One learner notebook sequence

Updated 2026-10-15.

The learner sees one course under `notebooks/`. Each Python notebook combines explanatory text, source graphics/slides, practice, computation, adaptive checks, and reflection. `uNN-nNN-topic.ipynb` identifies the course location. Unit 3 notebooks 02–08 now follow this convention too; activity and evidence IDs remain stable across the rename.

## TODO: Evaluate WebLLM with JupyterLite AI

- [ ] Evaluate an optional AI guide using WebLLM inference in the learner's browser.

Added 2026-10-22. This is a planned evaluation; compatibility with this course build has not been established.

Evaluation criteria:

- Assess the existing [jupyterlab-browser-ai WebLLM integration](https://github.com/jtpio/jupyterlab-browser-ai#webllm-models) before building a custom adapter. Compare it with JupyterLite AI's [custom provider interface](https://jupyterlite-ai.readthedocs.io/en/latest/custom-providers/) and the [AI SDK WebLLM provider](https://ai-sdk.dev/providers/community-providers/browser-ai).
- Verify compatible JupyterLab/JupyterLite and AI SDK versions, chat and streaming behavior, and notebook-context handling.
- Measure model download size, loading time, response latency, and GPU/memory requirements on representative learner devices. Check WebGPU availability and behavior when it is unavailable.
- Evaluate serving the runtime and model assets with the course, browser caching, and offline use after initial loading. Verify where prompts and responses travel.
- Keep the guide optional, respect the existing hint ladder, and preserve the deterministic assessment checks and browser learner record. Core notebooks must remain usable when AI is unavailable.

## Assembly and preservation

Authoring generators continue writing to `content/`, including imported UCSF material and the reviewed form library. `scripts/assemble_course.py` builds the single learner sequence in ignored `.course-content/`. JupyterLite publishes that assembly exclusively. Source copies stay in the repository for auditing and future editing. The generated [coverage map](../audit/unified-course-coverage.json) accounts for all 20 former reading/library notebooks.

- Unit 1: informatics lesson and visuals, slides, quiz, and reflection on the computed decision.
- Unit 2: HIS context/case, slides, quiz, and reflections on reporting systems, access, and delay.
- Unit 3 exploration: dataset exploration explanation and dataset-fit prompts.
- Unit 8: data-quality explanation, Martha scenario, repair questions.
- Unit 9: variable/dictionary questions.
- Unit 12: compilation/linkage explanation and merge questions.
- Unit 13: analysis/visualization explanation and briefing questions.
- Units 4, 5, 7: their local practice quiz sections.

Source section objectives are removed where the destination already states its own objective; source headings become subordinate to the one notebook title. Local slide previews are collapsible. As of 2026-10-22, canonical reflection questions are authored against each destination's displayed data; assignment bullets are not automatically converted into questions. Repeated written projects and references to missing numbered assignments are omitted from the learner route while their concepts remain mapped. Practice quizzes retain provisional feedback and remain unscored by the adaptive engine. Existing stored sections are retained in browser storage and the reflection download even when a former question no longer appears as a task.

Notebook 00 links all 22 Python notebooks. Each notebook has an explicit onward link and Course start; the record view leads on to Unit 4. Every scored Python task has an explicit Submit action; running setup/computation does not create attempts. Computation remains visible, while submission infrastructure is collapsed. The sidebar offers Python for the current pilot and no longer launches the external Unit 3 form. Export evidence and Download reflections have distinct scopes; neither automatically restores browser storage or notebook edits.

The former reading index becomes the orientation/table of contents. All former reading links resolve to the destination course notebook. Required images, datasets, dictionaries, and PDFs are bundled under `notebooks/assets`; there is no learner dependency on the source notebook tree. The published course is Python only. Legacy R notebooks and the R kernel have been removed.

## Build and checks

Generate exercises/forms, run references/dependency checks on authoring inputs, assemble the course, compile the extension, run `scripts/sync_labextension.py`, then build JupyterLite. The sync prevents an older installed extension from entering a new site build. `configure_site.py` hashes the assembled files for local review refreshes and normalizes extension loader URLs on Windows. Assembly validates unique cell IDs, canonical names, final References, and local notebook/media/PDF dependencies. Catalog paths and the Learning panel point at `notebooks/`.

Old notebooks already saved in a browser may remain in that browser's storage after a deployment. Production must preserve learner work during migration; assembly does not delete browser-saved files or the learner record. Local review mode refreshes supplied canonical notebooks on open. The unified layout needs a release before it replaces the currently published site.

UCSF attribution is centralized in Notebook 00 References, as requested. Shared assets use `notebooks/assets/` directly, without an institution-named folder. Source mappings and revision history remain in repository audit files.

## Validation - 2026-10-15

Five assembly checks passed: one course root, canonical names, local notebook/media/PDF dependencies, complete 20-source mapping, attribution only in Notebook 00 References, preserved full wrapped questions, integrated quiz controls, and stable assessment IDs. All assembled Python cells compile. All 23 engine/identity tests passed.

Targeted Chromium checks passed for the combined Unit 1 lesson/local images/slide PDFs, quiz feedback and four Record fields with reload persistence, and Unit 4 incorrect/repeated/correct attempts with capability/recommendation changes after Run All initialized its integrated quiz. Quiz state is scoped to avoid replacing exercise controls. Slide links use contents-relative paths to avoid duplicated `/files/files/` URLs.

The local site serves the final assembly on ports 8765 and 8774. This work has not been committed, pushed, or published; the public Pages site still requires a release. Existing R content was renamed consistently but its runtime was not tested in this Python-focused task.

## Unit 2 reporting-pathway submission - 2026-10-19

U02 N01 now uses a Submit button beside its reorder controls. Each submission snapshots the current case and laboratory pathways, shows the submitted order, and provides feedback for each pathway. Moving a stage marks the displayed result as awaiting a new submission. The old printed check cell has been removed. The learner-facing term is reporting pathway; existing filenames and activity IDs remain stable to preserve links and evidence history.

Widget submissions use the `al.submit` Jupyter comm target. The extension resolves assessment metadata from the submitting notebook cell and runs the existing Python check in that Jupyter kernel. It records an observation through the same store and emits the same event used by cell assessments, so capability estimates and recommendations update normally. Widget-marked setup cells do not record an attempt simply by running. The Submit control stays disabled until connected and while a check is pending; result feedback acknowledges successful recording, or reports a storage/check failure.

The browser scenario submits untouched, incorrect, repeated incorrect, and corrected orders; it checks inline feedback, stored observations, and the capability/recommendation changes.

Validation: the targeted Chromium pathway scenario passed for incomplete, incorrect, repeated incorrect, and correct submissions, including per-pathway feedback and adaptive recommendations. The existing Python dataset cell-assessment scenario also passed. All 19 Python tests and 23 engine/identity tests passed. The local review preview was rebuilt and updated; this change has not been published.

## Unit 2 diagram direction - 2026-10-19

The Country HIS Context diagram places MOH above the district system, reporting systems, and source records; reporting arrows point upward. The previous reorder control interpreted top-to-bottom placement as source-to-destination flow, so a learner who reproduced the diagram layout received incorrect feedback. The control now explicitly uses the diagram layout: MOH at the top, source records at the bottom, reporting upward. It reverses each displayed list when capturing the canonical source-to-MOH pathway for assessment. The criterion and stable activity/evidence IDs are unchanged. Submitted reporting-flow text explicitly labels its horizontal source-to-MOH direction. This corrects the interface ambiguity; prior observations are retained.

The regression scenario reproduces the learner's screenshot for both branches, checks correct per-pathway feedback and the adaptive outcome, and retains incomplete/incorrect/retry coverage.

Validation: Chromium reproduced MOH/district/reports/source top-to-bottom on both branches and received Correct feedback and a Correct observation, following incomplete and repeated incorrect attempts. All 19 Python tests passed. The rendered controls/feedback were visually inspected, and the VS Code preview copy was verified against the assembled notebook.

## Unit 3 Submit and stale review copies - 2026-10-19

U03 N01 now has a Submit button below its sorting board. It captures the current six classifications, runs the existing assessment through the widget submission bridge, and displays incomplete, incorrect, or correct feedback. The board is disabled while the check is pending; changing a choice marks the feedback as awaiting submission. The former executable check cell is replaced by a short instruction. Setup and board state are scoped to the interaction so other notebook widgets do not replace them. Python activity IDs and evidence semantics remain unchanged; the deferred R alternative is unchanged.

Local review mode now compares supplied cell sources and attachments on each notebook open even when a saved version marker is current. This addresses stale restored/saved copies whose marker alone incorrectly suggested they were up to date. Production learner mode remains opt-out and preserves saved notebooks and learner records. An already running preview application must be reloaded to load the updated extension.

Validation: Chromium passed U03 incomplete, incorrect, and correct submissions using the button, including inline feedback, recorded outcomes, capability change, and hidden setup code. The review-update scenario passed for stale source with a current marker and preserved learner-mode work and the learner record. The revised U03 comic was rendered and verified against the source PNG. The active VS Code preview matches the assembled notebook.

## TODO: rebuild R after Python stabilizes

- [ ] Rebuild R notebooks from the beginning using the stabilized Python course as the baseline; do not adapt the retired R notebooks.
- [ ] Establish parity for learning objectives, narrative, supplied data, interactions, Submit feedback, Record reflections, assessments, and learner-record outcomes.
- [ ] Add and validate an R browser kernel and R CI checks only when the rebuilt notebooks are ready for review.
