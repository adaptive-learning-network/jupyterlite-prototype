# Units 4–8: five Python computational narratives

Built for local course review, 2026-10-15. These are bounded teaching prototypes;
browser/runtime checks do not establish educational effectiveness or full source parity.
The source and enrichment inventory remains in `fetp-phi-course/docs/notebook-enrichment-plan.md`.

## Three course goals

| Notebook and single-verb objective | Source parity and visual connection | Usability and artifact | Adaptive workflow |
| --- | --- | --- | --- |
| U04 N01: **Compare** case, laboratory, and aggregate data sources. | UCSF Assessing HIS Software Applications: reuse existing HIS data; Version 2 Unit 2 slides 29–37. The bundled Unit 2 PDF page 29 frames surveillance information needs; the former page 37 preview was a section title and did not illustrate fragmented data sources. | Data source catalogue, accessible multiple selection and a dropdown asking what each row should represent; case/lab join preserves unmatched results as unknown. | `u04-source-inventory`; requires case/aggregate capability. |
| U05 N01: **Evaluate** role-specific access and disclosure risks. | UCSF Unit 3 Assignment 3 security-feature/practice prompts; Version 2 Unit 3 slides 53–61 and 68. The local table adapts slide 60's security/confidentiality/privacy comparison. | Least-needed internal fields and a separate suppressed public summary; all records invented. | `u05-access-and-safe-release`; follows U04. |
| U06 N01: **Evaluate** an AI-assisted draft against surveillance evidence. | Information-value pathway: Version 2 Unit 1 slide 26, locally displayed; interpretation and information bias from Version 2 Unit 7. Authoritative local Version 3 AI Unit 6 material remains missing. | Static draft, recomputed case/result counts, unsupported-claim selection and human-review decision. No model or remote API. | `u06-ai-use-and-review`; follows U05. |
| U07 N01: **Design** a case form with validation rules. | Version 2 Unit 2 slides 65–67 (Martha), Unit 3 slides 44–49 (field controls); UCSF Unit 4 Assignment 2 asks about DHIS2 modifications. Local slide 67 connects controls to Martha's scenario. | Required fields, age limit and controlled district list; computed pass/fail/error table for valid and malformed submissions. | `u07-form-design-validation`; follows U06. |
| U08 N01: **Analyze** completeness, validity, duplication, and timeliness. | Version 2 Unit 2 slides 60–68; UCSF Unit 2.2/Assignment 4. Local slide 68 carries the quality definition. | Quality counts, a separate cleaned copy, and a correction log with original values and source evidence. Only supplied source confirmations authorize changes; conflicting repeated IDs are retained. | `u08-quality-audit-repair`; follows U07. |

Each notebook has a three-panel local Laila/Martha/supervisor cue. Its vector
source is generated in `artwork/` by `scripts/make_units04_08.py`; authored
dialogue is not quoted from the slides. `node scripts/render_course_comics.cjs`
renders the committed PNG copies used as notebook attachments, because this
JupyterLab build blocks SVG attachments. A source hash in each PNG filename
prevents a changed vector from silently reusing an outdated image. The two-row
layout keeps text readable in a narrow notebook pane. Teaching slide images
are local files already bundled with the course. References are final cells.
New R variants are deferred.

## Source crosswalk and open gaps

Source review used UCSF commit `7eca2ec9d4d6082e76c7061a4746f1ac69d4ca7b`:

- `Unit_3_Assesing_HIS_Applications.ipynb`: selected application-assessment and HIS-reuse text is integrated in U04/U05. Its full feature comparison and original flashcards are not yet fully integrated.
- `Unit_3_Assignment_3.ipynb`: security-feature and additional-practice questions are adapted into U05 reflections.
- `Unit_4_Assignment_2.ipynb`: form-modification and authorization questions are adapted into U07 reflections.
- `Unit_4.ipynb` through `Unit_8.ipynb` are Google Slides wrappers. Reading a wrapper does not verify the actual deck. Their deck coverage remains unresolved.
- `Unit_6_Assignment_2.ipynb` concerns analysis, tables, graphs, maps and DHIS2 pivots; it belongs in future local U13, not in local AI Unit 6.

No hidden form answer key was inferred. These new exercise checks derive their
answers from synthetic records and explicit training constraints. The disclosure
threshold of 3, age bounds 0–120, and timeliness bound of 2 days are authored
training rules, not CDC or national operating standards. AI draft review is a
provisional teaching scenario pending authoritative Unit 6 material and course-owner review.

## Artifacts and evidence

`scripts/make_units04_08.py` generates five notebooks, five Python check scripts,
five vector cues and `test/fixtures/units04-08-scenarios.json`. The shared fixture
uses case IDs consistently across notebooks. Each notebook contains its own
copy so it runs independently; artifacts are recomputed, not automatically
passed between separate Jupyter kernels. A file-backed cross-notebook handoff
can be added later if needed by the course.

The TriG catalog adds five capabilities, targets, assets, activities and evidence
rules. All checks use the existing observer and browser learner record. Incomplete
and incorrect attempts remain observations; only a correct attempt with at most
two hints supports simulation-stage capability evidence. A third hint remains
available but excludes the later attempt from that evidence. The prerequisite
chain is a prototype teaching sequence, not a claim that AI proficiency is a
universal prerequisite for form design.

Reflections use the shared Record/restore bridge. They do not add scored evidence.
The browser record and reflections remain local to that site/browser. The final
navigation offers `u03-n08-my-learning-record.ipynb` to review the current browser-local learner record;
the existing RDF export still excludes reflection text.

## Validation harness

- `python -m unittest discover -s test -p 'test_units04_08.py'`: untouched input, every wrong criterion,
  partial and correct answers; join semantics; release boundary; changing evidence;
  positive/negative validation cases; and original-row preservation.
- Engine tests: repeated wrong attempts, success, capability state and prerequisite-aware
  recommendations across the five-unit chain.
- `ui-tests/units04-08.spec.ts`: actual controls, incomplete → wrong → retry → correct,
  recording, next recommendations and persistence across reload. Prior units are
  seeded as completed so reviewers need not answer those exercises.
  The Unit 4 scenario also serves an older checker using the retired field name
  on the first attempt. Python checks execute with a copied global namespace,
  so their helper definitions cannot replace notebook functions during retries.
  This isolates names, not mutable objects or untrusted code; checks remain
  application-owned resources. Reloading the app loads the current check assets.
- Notebook audit: local media, attachments, references, no response placeholders,
  Record controls and Python Jupyter kernel metadata.

Use the local preview for review; this document does not claim that these changes
have been committed, published, or validated with learners.

### Local validation on 2026-10-15

The 23 engine/identity tests and six native narrative tests passed. The catalog
and both learner-export fixtures conform to the ontology shapes; all 42 notebook
reference/media checks pass. All five Chromium scenarios passed, and U05/U07
were rechecked after adding permission-denial and missing-field cases. Intro and
control screenshots were visually inspected. Existing R variants were unchanged;
the local preview validates the Python path. Learner effectiveness and full source
parity remain review work.
