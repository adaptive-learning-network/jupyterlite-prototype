# Adaptive-learning JupyterLite prototype

A JupyterLite site in which learners work through exercises in **Python or R**
while an **ontology-driven adaptive-learning engine** observes results, builds
evidence, estimates capabilities, and recommends what to do next. The curriculum,
targets, evidence rules, and estimator policy are data in the `al:` upper
ontology (`../adaptive-learning-ontology`). Everything runs in the browser.

## How it works

```text
catalog/outbreak-analysis.trig  ──build_catalog.py (SHACL-validated)──▶  content/al/catalog.json
scripts/make_exercises.py       ──▶  content/exercises/{python,r}/*.ipynb + content/checks/*.{py,R}

JupyterLite page
  extension "jupyterlite-al-engine"
    observer   learner runs an exercise cell → its check runs in the same Jupyter kernel
               → one al:Observation (action, exercise, outcome, guidance level)
    engine     observations → evidence → estimates → gaps → recommendations (pure, deterministic)
    panel      next activities with reasons, progress, hint ladder, export/reset
    store      opaque learner IRI + observations in browser storage; Export → al: N-Quads
  Jupyter kernels   Python (Pyodide), R (xeus-r): where learners do exercises; not the engine
```

Terminology: a **Jupyter kernel** runs notebook code. The **adaptive-learning
engine** (`src/engine/`) is the deterministic component that interprets
observations. It never runs in a Jupyter kernel.

### Rules the prototype demonstrates

- **Evidence comes from observations.** A correct result checked in the learner's
  Jupyter kernel is simulation-stage evidence. The policy caps simulation at
  *Competent* on the Dreyfus scale.
- **Wrong or unfinished attempts are not negative evidence.** They lead to "not yet
  demonstrated" recommendations.
- **Hints affect evidence, not the score.** Up to two hints still count. A third,
  near-answer hint means that attempt is recorded but excluded
  (`al:GuidanceExceeded`).
- **Repeats count once.** Repeated success on one activity is one dependence group.
- **Prerequisites gate recommendations,** and critical targets come first.
- **The language doesn't matter.** The same observations give the same
  assessment in Python and in R.
- **Exports are validated.** The exported learner graph conforms to the `al:`
  SHACL shapes.

## Setup

Requirements: Node 20+, Python 3.10+, `curl`, and `Rscript` for the parity test.
The ontology repository is expected next to this one (`../adaptive-learning-ontology`).
Set `AL_ONTOLOGY_DIR` to use another location.

```bash
scripts/setup.sh        # idempotent; installs only inside this repository
```

The script creates `.venv/` (pinned build tooling from `lite/requirements.txt`),
installs Node dependencies, downloads `micromamba` for your platform into
`.tools/` (it builds the WebAssembly R environment), links the extension, and
installs the Playwright browser. Use `SKIP_PLAYWRIGHT=1` to skip the browser.

## Build the site

```bash
jlpm build:site          # catalog → exercises → engine tests → extension → _output/
python -m http.server 8765 --directory _output
# open http://127.0.0.1:8765/lab/index.html?path=exercises/python/01-frequency.ipynb
```

The site is about 150 MB, mostly the R runtime and its packages. The Python
Jupyter kernel downloads Pyodide from a CDN at first use. For fully offline use,
configure a local Pyodide distribution (see the jupyterlite-pyodide-kernel
documentation).

## Tests

`jlpm test:all` runs everything below.

| Command | What it checks |
| --- | --- |
| `jlpm test` | Engine unit tests (Node): prerequisites, guidance ceiling, dependence, language neutrality, order independence, fail-closed input |
| `jlpm test:export` | The exported learner graph conforms to the `al:` SHACL shapes |
| `jlpm test:checks` | Python and R checks agree on correct / incorrect / unanswered inputs (needs `Rscript`) |
| `jlpm test:ui` | Playwright end to end in Chromium against `_output/`, with both Jupyter kernels |

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

1. check out this repository and the ontology repository side by side;
2. validate the ontology (`scripts/validate.py` there);
3. `scripts/setup.sh`, then `jlpm build:site`, which validates the catalog,
   generates exercises, runs engine tests and export validation, builds the
   extension, and builds the site;
4. the Python/R parity test and the Playwright browser tests;
5. on `main`, publish `_output/` to GitHub Pages when the variable
   `PAGES_ENABLED` is `true`.

Repository settings:

- **Pages:** enable GitHub Pages with source **GitHub Actions** and set the
  variable `PAGES_ENABLED` to `true`. Private repositories need a paid plan for Pages.
- **Ontology ref:** set the variable `AL_ONTOLOGY_REF` to pin an ontology
  branch, tag, or SHA (default `main`).
- **Private ontology repository:** add a read-only token as the secret
  `AL_ONTOLOGY_TOKEN`.

## Layout

```text
catalog/outbreak-analysis.trig   curriculum in al: (source of truth)
content/                         site contents: catalog projection, notebooks, checks
src/engine/                      adaptive-learning engine (no JupyterLab dependency)
src/extension/                   JupyterLab/JupyterLite plugin: observer, panel, store, guide
scripts/                         catalog build, exercise generator, validators, site build
test/                            engine unit tests        ui-tests/  Playwright tests
environment.yml                  emscripten-forge env for the xeus-r Jupyter kernel
lite/requirements.txt            pinned build tooling
```

## Known limits (prototype)

- **Self-checks can be spoofed.** Checks run in the learner's own Jupyter kernel
  and contain the expected values, so a determined learner can fake them. This
  evidence is formative and capped at the simulation stage.
- **Storage is not durable.** The learner record lives in browser storage, which
  can be cleared or evicted. Export is the durable copy, and there is no import
  yet.
- **Hints are static.** The guide shows authored hints from the cell metadata. A
  local-model guide can implement the same `INotebookGuide` interface
  (`src/extension/guide.ts`) and must respect the same ladder.
- **Simplified estimator.** It supports only "correct evidence → stage ceiling
  level". There is no self-assessment instrument, no expiry, and no numeric
  bounds yet.
