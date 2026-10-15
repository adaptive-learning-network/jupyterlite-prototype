# One learner notebook sequence

Updated 2026-10-15.

The learner sees one course under `notebooks/`. Each Python notebook combines explanatory text, source graphics/slides, practice, computation, adaptive checks, and reflection. `uNN-nNN-topic.ipynb` identifies the course location. Unit 3 notebooks 02–08 now follow this convention too; activity and evidence IDs remain stable across the rename.

## Assembly and preservation

Authoring generators continue writing to `content/`, including imported UCSF material and the reviewed form library. `scripts/assemble_course.py` builds the single learner sequence in ignored `.course-content/`. JupyterLite publishes that assembly exclusively. Source copies stay in the repository for auditing and future editing. The generated [coverage map](../audit/unified-course-coverage.json) accounts for all 20 former reading/library notebooks.

- Unit 1: informatics lesson and visuals, slides, quiz, knowledge-check reflections, written case study.
- Unit 2: HIS context/case, slides, quiz, group-work and investigation responses.
- Unit 3 exploration: dataset exploration explanation and dataset-fit prompts.
- Unit 8: data-quality explanation, Martha scenario, repair questions.
- Unit 9: variable/dictionary questions.
- Unit 12: compilation/linkage explanation and merge questions.
- Unit 13: analysis/visualization explanation and briefing questions.
- Units 4, 5, 7: their local practice quiz sections.

Source section objectives are removed where the destination already states its own objective; source headings become subordinate to the one notebook title. Local slide previews are collapsible. Questions become Record fields rather than a second assignment notebook. Practice quizzes retain their provisional feedback and remain unscored by the adaptive engine. Saved sections that are reused keep their existing storage IDs; newly integrated assignment sections have explicit independent IDs.

The former reading index becomes the orientation/table of contents. All former reading links resolve to the destination course notebook. Required images, datasets, dictionaries, and PDFs are bundled under `notebooks/assets`; there is no learner dependency on the source notebook tree. Existing R counterparts remain alternatives under `notebooks/r/`, with new R development deferred.

## Build and checks

Generate exercises/forms, run references/dependency checks on authoring inputs, assemble the course, then build JupyterLite. `configure_site.py` hashes the assembled files for local review refreshes. Assembly validates unique cell IDs, canonical names, final References, and local notebook/media/PDF dependencies. Catalog paths and the Learning panel point at `notebooks/`.

Old notebooks already saved in a browser may remain in that browser's storage after a deployment. Production must preserve learner work during migration; assembly does not delete browser-saved files or the learner record. Local review mode refreshes supplied canonical notebooks on open. The unified layout needs a release before it replaces the currently published site.

UCSF attribution is centralized in Notebook 00 References, as requested. Shared assets use `notebooks/assets/` directly, without an institution-named folder. Source mappings and revision history remain in repository audit files.

## Validation - 2026-10-15

Five assembly checks passed: one course root, canonical names, local notebook/media/PDF dependencies, complete 20-source mapping, attribution only in Notebook 00 References, preserved full wrapped questions, integrated quiz controls, and stable assessment IDs. All assembled Python cells compile. All 23 engine/identity tests passed.

Targeted Chromium checks passed for the combined Unit 1 lesson/local images/slide PDFs, quiz feedback and four Record fields with reload persistence, and Unit 4 incorrect/repeated/correct attempts with capability/recommendation changes after Run All initialized its integrated quiz. Quiz state is scoped to avoid replacing exercise controls. Slide links use contents-relative paths to avoid duplicated `/files/files/` URLs.

The local site serves the final assembly on ports 8765 and 8774. This work has not been committed, pushed, or published; the public Pages site still requires a release. Existing R content was renamed consistently but its runtime was not tested in this Python-focused task.
