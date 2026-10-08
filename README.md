# Adaptive-learning JupyterLite prototype

## Open the course notebooks

- **[CDC GitLab Pages: launch JupyterLite](https://jupyterlite-prototype-4a4d87.gitpages.cdc.gov/)** (CDC sign-in required)
- **[GitHub Pages: launch JupyterLite](https://adaptive-learning-network.github.io/jupyterlite-prototype/)** (public)

A JupyterLite site in which learners work through exercises in **Python or R**
while an **ontology-driven adaptive-learning engine** observes results, builds
evidence, estimates capabilities, and recommends what to do next.

The current exercises convert **Public Health Informatics for FETP, Unit 3:
Using Informatics to Get Information Faster** (Version 3 course materials, used
with permission). Each notebook follows the unit's slides and ends with
references to the original guide, slides, quiz, and Excel How-To Scribes. The
unit's quiz opens from the Learning panel. The curriculum,
targets, evidence rules, and estimator policy are data in the `al:` upper
ontology (`../adaptive-learning-ontology`). Everything runs in the browser.

**Start with** [Notebook 00](https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=exercises/python/u00-n00-start-here.ipynb)
on GitHub Pages, then try the
[Unit 1 Notebook 01 Python pilot](https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=exercises/python/u01-n01-data-to-decision.ipynb),
[Unit 3 Python exercise](https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=exercises/python/u03-n01-data-or-information.ipynb),
[Unit 3 R exercise](https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=exercises/r/u03-n01-data-or-information.ipynb).
The site is rebuilt and published by CI on every push to `main` on GitHub and
GitLab.

Notebook 00 is an unscored orientation with the course cast and slide visuals.
**Review the UCSF source readings:** [Unit 1 and Unit 2 index on GitHub Pages](https://adaptive-learning-network.github.io/jupyterlite-prototype/lab/index.html?path=readings/ucsf/u00-n01-reading-index.ipynb)
or [the same index on CDC GitLab Pages](https://jupyterlite-prototype-4a4d87.gitpages.cdc.gov/lab/index.html?path=readings/ucsf/u00-n01-reading-index.ipynb).
The index links to the non-code lessons, cases, and assignments in source order.
Its notebook links stay on whichever JupyterLite host you opened.
If JupyterLite asks for a kernel while opening a reading, select **No Kernel**.
The Notebook 01 pilot uses `u03-n01-data-or-information.ipynb` in both language
folders: `uNN-nNN-topic.ipynb` means unit number, notebook number, and topic.
The Python U03 N01 notebook now uses a drag-and-drop board with **Data** and
**Information** bins for its six classifications. Run its collapsed setup cell,
sort the cards, then run **Check my choices**. Each card also has a **Move to**
menu for keyboard use. The R notebook still uses a typed vector. See the
[widget interaction plan](docs/design/notebook-widget-interactions.md)
for proposed controls across the course, including workflow ordering.
JupyterLite preserves browser-saved notebook copies across site updates. To see
the latest supplied notebook, first download or rename any personal copy you
want to keep, then refresh the file list and reopen the supplied filename.
The remaining existing exercise filenames will be converted after this pilot.
The reading index opens 18 unscored source pages with the original case text, questions, and seven
local images. They were imported from pinned UCSF revision `7eca2ec9` by
`scripts/import_ucsf_readings.py`; external slides, forms, and videos remain
links. UCSF's unit numbering differs from the local Version 3 plan, so each
reading states its topic alignment. One scored Python pilot now covers Unit 1;
Unit 2 scored work remains planned in the [course notebook inventory](../fetp-phi-course/docs/notebook-inventory.md).

The Unit 1 pilot uses the course's data–information–knowledge–wisdom slide graphic,
an original Laila teaching comic, synthetic weekly reported case counts, a
reflection prompt, and an adaptive check. The check scores the district,
numeric increase, and cautious first action; it does not grade the prose
reflection or establish outbreak status. R adaptation is planned after the
Python approach is reviewed.

A [Python-only DHIS2 adapter pilot](docs/design/dhis2-adapter-pilot.md) adds a
generated notebook at `content/exercises/python/07-dhis2-query.ipynb`. It uses
synthetic case events and a browser-local, read-only API-shaped adapter. This
pilot is available in the Python exercises as notebook 07.

The unscored final notebook, `content/exercises/python/08-my-learning-record.ipynb`,
reads a `learner-record.nq` export from the Learning panel. It shows attempts,
evidence, capability estimates, gaps, and recommendations. Upload successive
exports beside the notebook to see how the learner graph changes after retries.
For a ready-made synthetic retry sequence, run `jlpm demo:dhis2-graph` and upload
the four `.tools/dhis2-graph-demo/learner-record-*.nq` files to that notebook's
folder. These demonstration files are kept out of version control.

## How it works

```text
catalog/informatics-unit-03.trig ──build_catalog.py (SHACL-validated)──▶  content/al/catalog.json
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
- **Optional sign-in.** OpenID Connect (PKCE, public client) links an issuer and an
  opaque subject to the record under recorded consent. Names, emails, and tokens
  are never stored.

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
# open http://127.0.0.1:8765/lab/index.html?path=exercises/python/u03-n01-data-or-information.ipynb
```

The build downloads a checksum-verified Pyodide 314.0.6 core and the pinned
packages needed by the current Python notebooks, then serves them from the site.
Learners do not need the Pyodide CDN for these exercises. The R runtime and its
packages are also included in the site. If a new Python notebook imports another
package, add it to `REQUIRED_PACKAGES` in `scripts/prepare_pyodide.py`.
The U03 N01 widget setup uses `jupyterlab_widgets` and `anywidget` in the
JupyterLite frontend; `scripts/prepare_widget_wheels.py` adds checksum-pinned
Python widget wheels to the local `pypi/` index at build time. First use
installs them within the browser-local Python Jupyter kernel without a runtime
PyPI request. Teaching images in the orientation and pilot notebooks are
embedded as notebook attachments so browser-saved copies retain them.

On this Windows workspace, the local Node and Chromium installs live under
`.tools/`. The full R build requires the separate micromamba setup. For the
Python-only browser scenarios, use these commands in PowerShell from the repo root:

```powershell
$env:Path="$(Resolve-Path .tools/node-v22.23.3-win-x64);$(Resolve-Path .venv/Scripts);$env:Path"
$env:PLAYWRIGHT_BROWSERS_PATH=(Resolve-Path .tools/ms-playwright).Path
$env:NODE_USE_SYSTEM_CA='1'
$site=".tools/site-$(Get-Date -Format yyyyMMdd-HHmmss)"
python scripts/prepare_pyodide.py
python scripts/prepare_widget_wheels.py
jupyter-lite build --pyodide=.tools/pyodide --output-dir=$site --disable-addons=jupyterlite-xeus
$env:JUPYTERLITE_TEST_SITE=$site
node scripts/run_dhis2_browser.cjs
```

## Tests

`jlpm test:all` runs everything below.

| Command | What it checks |
| --- | --- |
| `jlpm test` | Engine unit tests (Node): prerequisites, guidance ceiling, dependence, language neutrality, order independence, fail-closed input |
| `jlpm test:export` | The exported learner graph conforms to the `al:` SHACL shapes |
| `jlpm test:checks` | Python and R checks agree on correct / incorrect / unanswered inputs (needs `Rscript`) |
| `jlpm test:ui` | Playwright end to end in Chromium against `_output/`: both Jupyter kernels, plus sign-in against a mock OpenID Connect provider |
| `jlpm test:dhis2` | Scripted DHIS2 notebook retries, learner-record assertions, hint ceiling, and changing recommendations; no manual cell editing |

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

`.gitlab-ci.yml` builds the same site, runs the Python/R parity and browser
tests in separate jobs, and deploys GitLab Pages only after those jobs pass.

Repository settings:

- **Pages:** enable GitHub Pages with source **GitHub Actions** and set the
  variable `PAGES_ENABLED` to `true`. Private repositories need a paid plan for Pages.
- **Ontology ref:** set the variable `AL_ONTOLOGY_REF` to pin an ontology
  branch, tag, or SHA (default `main`).
- **Private ontology repository:** add a read-only token as the secret
  `AL_ONTOLOGY_TOKEN`.

## Layout

```text
catalog/informatics-unit-03.trig  Unit 3 curriculum in al: (source of truth)
content/                         site contents: catalog projection, notebooks, checks
src/engine/                      adaptive-learning engine (no JupyterLab dependency)
src/extension/                   JupyterLab/JupyterLite plugin: observer, panel, store, guide
scripts/                         catalog build, exercise generator, validators, site build
test/                            engine unit tests        ui-tests/  Playwright tests
environment.yml                  emscripten-forge env for the xeus-r Jupyter kernel
lite/requirements.txt            pinned build tooling
```

## Design documents

- [Capability packs](docs/design/capability-packs.md): versioned, downloadable packs of adaptive-learning content, a pack catalog per programme, and the runtime changes needed to install them.
- [Learner identity](docs/design/learner-identity.md): optional OpenID Connect sign-in that links an issuer and an opaque subject to the anonymous learner record. To enable it, configure `lite/oidc.json`.

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
