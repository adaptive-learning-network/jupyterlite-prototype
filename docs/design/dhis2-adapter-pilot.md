# DHIS2 adapter notebook pilot

**Status:** Python-only source, native checks, and a Python-only JupyterLite static build have passed. The scripted Chromium browser scenarios verified the Jupyter kernel, Learning panel, browser-local record, retries, recommendations, repeats, and hint ceiling in a local build. The R runtime was excluded from this Windows build.

The pilot is a JupyterLite notebook at `content/exercises/python/07-dhis2-query.ipynb`. Its setup cell contains a read-only `CourseDhis2Adapter` and seven synthetic measles events. Learners query two metadata lists and a district's events, then report the number of records, the range of nonblank rash-onset dates, and the number of missing onset dates. The existing Learning panel runs `content/checks/dhis2-query.py` after the learner's exercise cell and records a simulation-stage observation against the dataset-exploration capability.

## Course basis

- The [UCSF FETP JupyterBook Unit 2.1 case-study Assignment 2](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_2.ipynb) asks learners to describe dataset size, timeframe, locations, and population.
- [Assignment 3](https://github.com/UCSF-IGHS/FETP/blob/main/FETP_book/Unit_2.1_Case_study_Assignment_3.ipynb) asks them to use the data dictionary to understand variables.
- The current prototype's FETP Version 3 Unit 3 exercises also teach dataset exploration. The UCSF book's current table of contents names Units 0–16, while `fetp-phi-course/units.json` names Units 0–14. This pilot is tied to the learning action and its cited source pages, pending a course-version crosswalk.

The pilot uses no course case records, names, identifiers, or source files. The seven events and their IDs are invented for this exercise.
The notebook keeps the source assignments' short question wording and links to both pages. It states the change in access path: the assignment supplies an Excel backup during a network outage, while this pilot supplies a local API-shaped fixture. Future exercises should likewise keep source objectives and task wording where appropriate, with a link to the exact unit, while making any changed workflow explicit.

## Implemented contract

| Request | Response | Limit |
| --- | --- | --- |
| `GET /api/organisationUnits` | `organisationUnits` with IDs and names | Two synthetic districts |
| `GET /api/dataElements` | `dataElements` with IDs, names, and value types | Three synthetic elements |
| `GET /api/tracker/events` with `program` and `orgUnit` | `events` with `dataValues` | One synthetic program; exact district filtering |

The adapter is an in-memory Python object. `get()` returns copies, rejects unsupported paths or parameters, and makes no HTTP requests. The endpoint names and event shape are informed by the [DHIS2 Tracker API](https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-241/tracker.html); the pilot does not implement the full DHIS2 API, authentication, writes, or analytics.

## Rebuild and verify

`scripts/make_dhis2_pilot.py` is the source of the notebook, fixture, and check. `scripts/make_exercises.py` calls it after generating the existing paired Python and R exercises. `catalog/informatics-unit-03.trig` is the source of the Learning panel activity and asset; `scripts/build_catalog.py` projects it to `content/al/catalog.json`.

Run the Python-only native check with:

```text
python -m unittest discover -s test -p test_dhis2_pilot.py -v
```

The native test checks query scope, rejection of unsupported requests, copy isolation, and the incomplete/correct/incorrect check outcomes. A Python-only `jupyter lite build` copied the notebook and check into the local site. The scripted Chromium run then exercised the Jupyter kernel and Learning panel. This demonstrates browser behavior for the Python pilot; it does not establish R parity or learner effectiveness. The intended integration uses the same browser-local learner storage and export behavior as the existing exercises.

### Scripted learner scenarios

After building the site with `jlpm build:site`, run `jlpm test:dhis2`. Playwright opens the real notebook in a fresh browser context for each scenario, runs its setup cell, supplies scripted answers to the exercise cell, and inspects the Learning panel and browser-local learner record. No tester has to write answers in JupyterLite.

| Scenario | Recorded attempts | Expected adaptive response |
| --- | --- | --- |
| Placeholder, wrong missing-date count, wrong date range, then correct | Incomplete, Incorrect, Incorrect, Correct; all four retained after reload | Dataset exploration remains recommended with “not yet demonstrated” through the retries; success demonstrates it and unlocks filtering |
| Correct answer twice | Two Correct observations | Both attempts remain in the record; dataset exploration stays demonstrated (one exercise dependence group) |
| Three hints before a correct answer | One Correct observation at guidance level 3 | The outcome is recorded but excluded as evidence; dataset exploration stays recommended |

The matching engine test in `test/engine.test.ts` checks the recommendation transition without a browser. The browser test also checks that the real Jupyter kernel, observer, browser storage, and panel agree. These scripted outcomes test system behavior; they do not measure whether a learner can solve the exercise. The retry, repeat, third-hint, and learner-record-view scenarios passed locally in Chromium.

The unscored `08-my-learning-record.ipynb` notebook reads the learner's own N-Quads export from the Learning panel. With sequential exports uploaded beside the notebook, it reports attempt history, graph counts, current interpretation, and graph changes between exports. It reads snapshots and does not add learning observations.
For a no-coding demo, `jlpm demo:dhis2-graph` generates four synthetic exports under `.tools/dhis2-graph-demo/`; the final notebook can read them in order. The browser test verified that the notebook renders a local graph and leaves the observation count unchanged. The native viewer also parsed the four real N-Quads exports from the demo generator.

## Next slice

After the read workflow is observed in JupyterLite, a separate exercise could simulate `POST /api/tracker` validation and import for cleaned case records. That would need a distinct fixture, import rules, and course objective. R support can then use the same synthetic data and learning contract.
