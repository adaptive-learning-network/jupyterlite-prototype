# DHIS2 adapter notebook pilot

**Status:** Python-only source, native checks, and a Python-only JupyterLite static build have passed. The scripted Chromium browser scenarios verified the Jupyter kernel, Learning panel, browser-local record, retries, recommendations, repeats, and hint ceiling in a local build. The R runtime was excluded from this Windows build.

The pilot is a JupyterLite notebook at `content/exercises/python/u03-n07-dhis2-query.ipynb`. Its setup cell contains a read-only `CourseDhis2Adapter` and seven synthetic measles events. Learners follow five supplied, explained code steps to inspect metadata, retrieve a district's events, read a flattened table, and summarize record count, known onset range, and missing onset dates. Submit runs the existing `app-assets/adaptive-learning/checks/dhis2-query.py` through the widget submission bridge and records a simulation-stage observation against the dataset-exploration capability. Intermediate steps are unscored.

## Course basis

- The [UCSF FETP JupyterBook Unit 2.1 case-study Assignment 2](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_2.ipynb) asks learners to describe dataset size, timeframe, locations, and population.
- [Assignment 3](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_3.ipynb) asks them to use the data dictionary to understand variables.
- The current prototype's FETP Version 3 Unit 3 exercises also teach dataset exploration. The UCSF book's current table of contents names Units 0–16, while `fetp-phi-course/units.json` names Units 0–14. This pilot is tied to the learning action and its cited source pages, pending a course-version crosswalk.

The pilot uses no course case records, names, identifiers, or source files. The seven events and their IDs are invented for this exercise.
The notebook adapts the source assignments' dataset-size, timeframe, and dictionary questions into one local guided narrative. Source attribution is centralized in Notebook 00; learner-facing sections focus on the investigation. The assignment's Excel-backup scenario informs the local API-shaped fixture. Future exercises should likewise keep source objectives and task wording where appropriate, with a link to the exact unit, while making any changed workflow explicit.

## Implemented contract

| Request | Response | Limit |
| --- | --- | --- |
| `GET /api/organisationUnits` | `organisationUnits` with IDs and names | Two synthetic districts |
| `GET /api/dataElements` | `dataElements` with IDs, names, and value types | Three synthetic elements |
| `GET /api/tracker/events` with `program` and `orgUnit` | `events` with `dataValues` | One synthetic program; exact district filtering |

The adapter is an in-memory Python object. `get()` returns copies, rejects unsupported paths or parameters, and makes no HTTP requests. The endpoint names and event shape are informed by the [DHIS2 Tracker API](https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-241/tracker.html); the pilot does not implement the full DHIS2 API, authentication, writes, or analytics.

## Rebuild and verify

`scripts/make_dhis2_pilot.py` is the source of the notebook, fixture, and check. `scripts/make_exercises.py` calls it after generating the existing paired Python and R exercises. `catalog/informatics-unit-03.trig` is the source of the Learning panel activity and asset; `scripts/build_catalog.py` projects it to `app-assets/adaptive-learning/catalog.json`.

Run the Python-only native check with:

```text
python -m unittest discover -s test -p test_dhis2_pilot.py -v
```

The native test checks query scope, rejection of unsupported requests, copy isolation, and the incomplete/correct/incorrect check outcomes. A Python-only `jupyter lite build` copied the notebook and check into the local site. The scripted Chromium run then exercised the Jupyter kernel and Learning panel. This demonstrates browser behavior for the Python pilot; it does not establish R parity or learner effectiveness. The intended integration uses the same browser-local learner storage and export behavior as the existing exercises.

### Scripted learner scenarios

After building the site with `jlpm build:site`, run `jlpm test:dhis2`. Playwright opens the real notebook in a fresh browser context for each scenario, runs the supplied guided cells, submits complete and deliberately altered summaries, and inspects the Learning panel and browser-local learner record. No tester has to write answers in JupyterLite.

| Scenario | Recorded attempts | Expected adaptive response |
| --- | --- | --- |
| Submit before completing steps, wrong missing-date count, wrong date range, then correct | Incomplete, Incorrect, Incorrect, Correct; all four retained after reload | Dataset exploration remains recommended with “not yet demonstrated” through the retries; success demonstrates it and unlocks filtering |
| Correct answer twice | Two Correct observations | Both attempts remain in the record; dataset exploration stays demonstrated (one exercise dependence group) |
| Three hints before a correct answer | One Correct observation at guidance level 3 | The outcome is recorded but excluded as evidence; dataset exploration stays recommended |

The matching engine test in `test/engine.test.ts` checks the recommendation transition without a browser. The browser test also checks that the real Jupyter kernel, observer, browser storage, and panel agree. These scripted outcomes test system behavior; they do not measure whether a learner can solve the exercise. The retry, repeat, third-hint, and learner-record-view scenarios passed locally in Chromium.

The unscored `u03-n08-my-learning-record.ipynb` displays the current browser-local record through a safe MIME renderer registered by the course extension. Its saved output contains only a version marker and no learner data. A hidden display-only cell re-emits this marker when Run or Run All clears the previous output; reporting logic stays in the extension. The cell carries view metadata only, so exercise checks do not assess it. The renderer reads the same store and pure assessment used by the Learning panel, uses text nodes for learner responses, subscribes to store changes, and provides Refresh. It neither calls the exercise observer nor writes to storage. Attempts, progress, recommendations, and explicitly recorded reflections appear without exporting files or running Python. A plain-text fallback explains where to open the notebook if the course renderer is unavailable.

N-Quads export and the developer-only `scripts/learning_record_view.py` and `jlpm demo:dhis2-graph` remain available for snapshot comparisons outside this learner workflow.

## Next slice

After the read workflow is observed in JupyterLite, a separate exercise could simulate `POST /api/tracker` validation and import for cleaned case records. That would need a distinct fixture, import rules, and course objective. R support can then use the same synthetic data and learning contract.

## Guided narrative revision - 2026-10-19

A reviewer identified excessive assumed knowledge in the original four-command task. The revised notebook supplies runnable Python rather than requiring an epidemiologist to invent API syntax or nested-list comprehensions. Each step states its epidemiologic purpose, explains the request/response vocabulary, displays a readable result, and provides a small interpretation checkpoint.

| Previous leap | New support |
| --- | --- |
| District name to opaque ID | Named district/ID table, explained lookup loop, printed selection. |
| Variable name to data-element ID | Dictionary table showing readable name, ID, and type; same lookup pattern. |
| Endpoint and filter syntax to scoped events | A what/where request-settings table and supplied program/district request. |
| Nested dataValues to useful observations | Optional raw-record preview, explained field-ID/value pairing, supplied flattening loop, and one-row-per-event table. |
| Multiple date concepts and blank values to a range | Event and onset columns side by side, visible Missing value, separate counting of records/blanks/known dates, explained len/min/max. |
| Executed code to an epidemiologic conclusion | Summary limitations, explicit warning against treating all records as confirmed cases or the known range as outbreak duration, and two Record reflections. |

Submit checks the existing result contract and records retries. Setup and Submit infrastructure are collapsed, while the short learning code remains visible. The optional transfer changes only the district name and reruns the same steps; Laila's submitted target remains Kambia. The existing activity/object IDs and simulated evidence rule are retained. **A correct guided run demonstrates completion of this supplied workflow; it does not establish independent API programming proficiency.** Reflection interpretation is unscored. Educational effectiveness still needs learner review.

Validation of the revised narrative: all three native adapter/guided-workflow tests and all three Chromium DHIS2 scenarios passed. Browser checks cover supplied-step execution, the expected dates and missing-date measure, incomplete and incorrect retries, corrected submission, repeated success, hint ceiling, and learner-record persistence. The rendered summary table was visually inspected. All supplied Python cells compile, and the active VS Code preview matches the assembled notebook. These checks establish execution behavior, not learner comprehension.

## Missingness visual pilot - 2026-10-19

U03 N07 has an optional missingno completeness matrix after the flattened event table. Rows retain event IDs and columns show event date and rash onset date; a companion table gives exact missing counts. Whitespace/empty strings are converted to pandas NA only in a separate display copy. Original event records and onset_rows are preserved. The narrative distinguishes completeness from correctness, uniqueness, and timeliness; no imputation or repair is performed, and viewing the chart does not add an observation.

The [missingno project](https://github.com/ResidentMario/missingno) documents its matrix and bar displays. This bounded pilot uses a matrix; a before/after completeness bar and matrix are candidates for U08, alongside its separate duplicate, validity, timeliness, and correction-log checks. Missingno does not replace those checks, and heatmaps/dendrograms would be unhelpful for this five-record example.

Build preparation pins missingno 0.5.2 and seaborn 0.13.2 by wheel checksum in the local piplite index. Matplotlib, SciPy, and their transitive compiled dependencies are selected from the pinned Pyodide 314.0.6 lockfile and bundled in the site. No native pip package is required for the learner. Python-only local review builds without xeus environments disable the unused xeus frontend to avoid its optional remote package-name map request; builds containing R environments retain that frontend.

Validation: the Chromium missingno scenario passed with all external HTTP requests blocked and none attempted. It rendered the matrix using locally hosted packages, verified one normalized missing onset, checked that the original onset_rows and event dataValues retained their blank strings, and confirmed no learning observation was added. The image was visually inspected. All three native DHIS2 tests passed; all supplied Python cells compile and the served notebook matches the assembly.

Rendering follow-up - 2026-10-19: the PNG output exposed Matplotlib float-coordinate deprecations from its Agg text drawing path. The chart now uses Matplotlib SVG output, keeping its labels and embedded matrix self-contained. No warning filters are added to the learner renderer and no global Matplotlib methods are patched. The WASM renderer and Chromium pilot passed with Matplotlib deprecations promoted to exceptions. The test also inspects the full output for warnings/tracebacks and captures the counts plus chart, rather than checking only that an image exists. The complete cell output was visually inspected and the active preview verified against assembly.
