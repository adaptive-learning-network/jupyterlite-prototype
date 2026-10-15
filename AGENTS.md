# AGENTS.md: jupyterlite-prototype

Guidance for coding agents and contributors working in this repository.

## What this repository is

A JupyterLite site plus a JupyterLab 4 extension. Learners do exercises in
Python or R notebooks, and an **ontology-driven adaptive-learning engine**
records observations, builds evidence, estimates capabilities, and recommends
what to do next. Current scored content: Public Health Informatics for FETP, Units 1, 2, and 3
(Version 3 course materials, used with permission). The repository is
**public** and published to GitHub Pages.

Read [README.md](README.md) and the design notes in [docs/design/](docs/design/).

## Layout

```text
catalog/*.trig               curriculum in al: terms: SOURCE OF TRUTH for capabilities, targets, activities, rules
scripts/build_catalog.py     validate catalog against al: shapes → app-assets/adaptive-learning/catalog.json (generated)
scripts/make_exercises.py    exercise SPEC → notebooks in content/, checks in app-assets/adaptive-learning/ (generated)
scripts/configure_site.py    publish versioned application assets outside the learner contents drive
scripts/make_unit01_pilot.py Python-only Unit 1 scored pilot (called by make_exercises.py)
scripts/prepare_widget_wheels.py  checksum-pinned local piplite wheels for U03 N01 controls
src/engine/                  adaptive-learning engine: pure, deterministic, no JupyterLab imports
scripts/import_ucsf_readings.py  pinned UCSF source to unscored reading notebooks and images
scripts/add_course_references.py  local, final References cell and dependency check
src/identity/                PKCE and identity-binding rules (pure)
src/extension/               JupyterLab plugin: observer, panel, store, guide, OIDC sign-in
site/oidc-callback.html      copied to the site root by scripts/configure_site.py
test/                        engine and identity unit tests (Node)
ui-tests/                    Playwright end-to-end tests + mock OIDC provider
docs/design/                 capability packs, learner identity
```

## Commands

```bash
scripts/setup.sh            # one-time, idempotent: .venv, node_modules, micromamba, Playwright
jlpm build:site             # catalog → exercises → engine tests → export validation → extension → _output/
jlpm test:all               # export SHACL validation, Python/R check parity, Playwright end to end
python -m http.server 8765 --directory _output   # preview
```

The `al:` ontology is expected at `../adaptive-learning-ontology`; override with
`AL_ONTOLOGY_DIR`.

## Rules

1. **Edit sources, not generated files.** Exercise notebooks in `content/` and
   checks in `app-assets/adaptive-learning/` come from `scripts/make_exercises.py`; UCSF readings come from
   `scripts/import_ucsf_readings.py`; `app-assets/adaptive-learning/catalog.json` comes from the
   TriG catalog. Change the source or generator, then regenerate.
2. **Use the course material as much as possible:** verbatim learning objectives,
   slide examples and definitions, course scenarios, Excel How-To Scribes, and
   quiz items. Synthetic data only fills gaps, and it extends the course's own
   examples. Expected answers are computed from the data, never typed in.
3. **Every shipped notebook ends with a References section.** Cite the course
   source in text and link bundled slides or companion readings where useful.
   Do not make learning content depend on external links. Include an external
   reference URL only after verifying that its destination works; add it to the
   reviewed allowlist in `scripts/add_course_references.py`.
4. **Python and R stay in parity** for the existing paired Unit 3 exercises.
   Develop new computational narratives in Python first; defer new R variants
   until the Python path is stable. Unit 1 Notebook 01 and the DHIS2 pilot are
   Python only. `jlpm test:checks` must pass (it needs `Rscript`).
5. **One case journey per topic.** Put the needed course explanation, local
   visual, data task, interpretation, and adaptive check in the scored notebook.
   Existing UCSF readings are an optional source library, not a second required
   route through the same case. Preserve source coverage in the course inventory.
6. **The engine stays pure.** No DOM, storage, network, clock, or randomness in
   `src/engine/` or `src/identity/`. Policy values are data in the catalog.
7. **Privacy.** Learner identity is an opaque `urn:uuid:`. OIDC sign-in keeps only
   the issuer and an opaque subject, under consent. Never store names, email
   addresses, or tokens. `lite/oidc.json` holds public values only;
   `configure_site.py` rejects secrets.
8. **Public repository.** No secrets, tokens, personal names (including
   facilitators named in course guides), or local paths. Course specifics belong
   in notebooks with attribution; design docs stay generic.
9. **Terminology.** Use **adaptive-learning engine** for the deterministic
   component and **Jupyter kernel** for Python or R runtimes. Never say "kernel"
   alone.
10. **Notebook cell IDs** must be unique. Core generated cells use numeric IDs;
    the final References cell uses its own ID, and slide preview cells use
    descriptive IDs.
11. **Update the local review preview.** After changing notebooks or application
    resources, update the site served in the VS Code browser and configure it with
    `scripts/configure_site.py --output <preview-directory> --course-review`.
    Reviewer responses are disposable: this mode replaces outdated supplied
    notebook copies on open. Omit the flag for published learner builds. Production
    must preserve learner answers and reflection notes across course updates.

## Before you commit

- `jlpm build:site` succeeds (engine tests and export validation run inside it).
- `jlpm test:checks` and `jlpm test:ui` pass.
- If catalog or export shapes depend on a new `al:` change, push the ontology
  repository first: CI validates against its `main`.
- CI (`.github/workflows/ci.yml`) builds, tests, and deploys Pages on `main`.
