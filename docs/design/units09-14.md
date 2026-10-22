# Units 9–14 computational narratives

**Implementation review:** 2026-10-15

These six Python prototypes complete the consolidated Units 4–14 build map. They continue Laila's fictional case rather than introduce a separate required reading route. They are not official quiz keys or evidence of learner effectiveness.

## Teaching and source coverage

| Notebook | One-verb objective | Local artifact | Course connection |
| --- | --- | --- | --- |
| U09 dictionary and value map | Create a dictionary for a case dataset. | Field dictionary and code reconciliation | V2 U2 dictionary slide 56; V2 U5 terminology; UCSF U9 topic, U2.1 variable-selection assignment |
| U10 table design and data flow | Design linked case and laboratory tables. | Key uniqueness audit and ordered flow | HIS context image; V2 U5 storage; UCSF U10 topic and U5 Assignment 2 transmission map |
| U11 recode and reconcile | Evaluate a recoded table against the supplied case records. | Fixed under-five age groups; predictions of case group, under-five count, row count, and missing-age handling; preserved case identifiers | Dictionary visual; V2 U5 preparation; UCSF U11 topic and cleaning assignment |
| U12 link and exchange | Analyze matched, unmatched, and conflicting case keys. | Linked case view, validation log, candidate exchange rows | Local match_rows.png; V2 U2 matching and U5 exchange; UCSF U12 topic and U2.3 merge assignment |
| U13 analysis and dashboard | Create person, place, and time summaries. | District shares, age/sex summaries, onset-date chart | Local laila_analyze.png; V2 U6 analysis; UCSF U6 Assignment 2 Data/Period/Organization Unit framing, U2.3 analysis, U13–14 topics |
| U14 interpret with AI | Critique a supplied interpretation against case evidence. | Claim decisions and computed evidence table | Laila analysis cue; V2 U7 interpretation context; UCSF U15 AI topic |

Objectives are adapted/proposed for these computational tasks, not claimed as verbatim Version 3 objectives. Source topics are mapped by content rather than unit number. The pinned UCSF revision is `7eca2ec9d4d6082e76c7061a4746f1ac69d4ca7b`. Units 9–15 at that revision contain external slide wrappers only; their embedded slides have not been verified here. Required explanations, fixtures, controls, visuals, and checks are local. External wrapper URLs remain in the source inventory, not learner notebooks.

## Implementation

U11 uses fixed definitions: `under5` means age less than five, `5plus` includes
age five, and a missing age produces `unknown`. A visible, independent example
demonstrates ages 4, 5, 8, and a missing value. These examples are explicitly
separate from the four supplied case records. Learners review the resulting
classifications and record retention; they do not choose an arbitrary cutoff
under fixed category names. Their answers do not change the transformation or
delete cases. This is guided review, not evidence of independently writing
transformation code.

`scripts/make_units09_14.py` defines the six specifications, shared synthetic fixture, computed expectations, artifacts, and check generation. It reuses the existing Unit 4–8 controls, table renderer, local comic renderer, cell attachment handling, and Record reflection helper. `make_exercises.py` invokes it; `add_course_references.py` enforces final References and local dependencies.

Comics have editable native SVG sources in `artwork/` and hash-named raster attachments. Browser rendering creates the PNGs with `render_course_comics.cjs`; those PNGs ship with the source so builds do not need a browser for image generation. The second visual in each notebook is a bundled course image or slide preview.

The four case rows continue the earlier fictional records. A later laboratory extract introduces conflicting C02 results and orphan C99 with unmapped code X. These deliberate problems support linkage and exchange review. They do not overwrite the earlier fixture. All transformations operate on copies. C02 is marked conflict, cases without laboratory rows remain unmatched, and invalid rows cannot enter the candidate exchange table even when the learner requests sending them. The exchange table is a training contract, not a complete DHIS2 API request.

The analysis uses reported case counts, shares, onset dates, age groups, and sex. It supplies no population denominator or geographic boundaries. It therefore does not calculate population rates or pretend to provide a rate map. U13 uses locally bundled Seaborn 0.13.2 with Matplotlib SVG output. It displays count tables beside age-group, recorded-sex, district, and daily-onset charts, with integer count axes and no inferential error bars. This avoids a plotting CDN and the earlier raster text warnings. The bars plot precomputed counts; [the Seaborn reference](https://seaborn.pydata.org/generated/seaborn.barplot.html) documents the explicit `errorbar=None` setting. U14 uses a static AI-style draft with both supported and unsupported statements, no live model or health-data upload. The course's authoritative Version 3 AI deck and objectives remain pending.

## U12/U13 local workflow revision - 2026-10-22

The canonical generators now supply one local narrative per topic. Assembly
records the coverage of `u02-n12-compile-analyze`, `u02-n14-assignment-5`,
`u02-n13-analyze-visualize`, and `u02-n15-assignment-6` without appending a second
Excel workflow or expecting unshipped workbooks. The original source readings
remain authoring evidence; they are not a separate learner route.

U12 preserves preparation, identifier alignment, adding columns versus rows,
matching, duplicate/conflicting results, before/after checks, and post-link
review. The visible Pandas example demonstrates four cases becoming five rows
in an unchecked left join, then retains four distinct case identifiers while
holding C02 and C99 laboratory rows for follow-up. One validated C01 result
remains available for a possible exchange; no request is sent. The example is
a bounded review rule, not a general prohibition on multiple specimens.

U13 preserves person/place/time summaries, mean/median/mode/range, counts and
shares, onset timing, chart selection, and a finding/evidence/limitations/action
briefing. It explicitly identifies unavailable death, vaccination, population,
household-location, reporting-date, twelve-month, and outbreak-threshold inputs
rather than asking learners to calculate unsupported indicators. The plotting
and linkage examples are unscored; their cells do not add observations.

Local validation on 2026-10-22: six native narrative tests passed. The U12
Chromium workflow verified the unchecked and validated row counts, accepted C01
result, retries, and three reflection fields. The U13 Chromium workflow verified
person/place/time counts, four fully loaded responsive Seaborn images, no plot
warnings or tracebacks, retries, and four reflection fields. Plot image bounds
were checked against the narrow output pane, and exported screenshots were
inspected. These checks demonstrate runtime behavior, not learner effectiveness.

## Adaptive and reflection workflow

Six catalog capabilities and activities follow U08 in prerequisite order. Every check recomputes training expectations from the frozen fixture and explicit contracts. Checks use the existing OutputValidated/Correct evidence rule with maximum guidance 2; retries remain observations. Each notebook has question-specific response fields with Record; U12 has three and U13 has four structured briefing fields. These use the existing browser-local learner storage/restore path. Reflections are unscored and do not grant capability evidence.

`test/test_units09_14.py` checks every incomplete/incorrect/correct criterion, repeated check execution, source immutability, under-five boundary, missing ages, join cardinality, conflict/quarantine behavior, computed summaries, generated cell compilation, and local comic attachments. `ui-tests/units09-14.spec.ts` exercises all six in fresh Chromium contexts: initial incomplete, two incorrect retries, correct response, capability/recommendation update, reflection Record, and persistence after reload. Prior prerequisite observations are seeded solely to isolate each workflow.

## Remaining work

Zero additional required Python notebooks remain to create under the consolidated map. Further work includes full slide/source reconciliation, expanded person/event/aggregate schema authoring, reshaping, geographic fixtures/maps, a fuller dashboard, authoritative AI material, learner evaluation, and production update behavior that preserves user work. One communication narrative remains conditional on its course home. New R variants remain deferred. The source-library backlog is not an additional mandatory sequence.

Local review builds use `--course-review`; the stable browser URL remains port 8774. This mode refreshes supplied notebook copies while retaining browser-local learner records. Publishing is a separate release action.
## Validation result — 2026-10-15

- Fresh local JupyterLite build succeeded; Windows contents/runtime paths normalized.
- All six final Chromium scenarios passed (6.2 minutes): image loading, incomplete attempt, two incorrect retries, correct result, achieved capability, next recommendation where applicable, reflection recording, and reload persistence.
- Six Python narrative tests passed; the six existing Unit 4–8 Python tests also passed after shared setup reuse.
- All 23 engine/identity tests passed, including the expanded Unit 4–14 prerequisite/retry chain.
- Catalog and both learner exports conform to the ontology shapes.
- References/dependency audit passed for all 48 notebooks. All six notebooks served on local port 8774 match current source bytes; review mode is enabled.

Validation covers Chromium and the synthetic training fixtures, not Firefox/Safari, the CDC browser configuration, a live DHIS2 server, a live AI service, or learner effectiveness. Existing R variants were unchanged and not retested in this Python task. No commit, remote push, or publication was performed.
