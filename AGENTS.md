# AGENTS.md: jupyterlite-prototype

Guidance for coding agents and contributors working in this repository.

## What this repository is

A JupyterLite site plus a JupyterLab 4 extension. Learners do exercises in
Python or R notebooks, and an **ontology-driven adaptive-learning engine**
records observations, builds evidence, estimates capabilities, and recommends
what to do next. Current scored content: Public Health Informatics for FETP, Units 1 and 3
(Version 3 course materials, used with permission). The repository is
**public** and published to GitHub Pages.

Read [README.md](README.md) and the design notes in [docs/design/](docs/design/).

## Layout

```text
catalog/*.trig               curriculum in al: terms: SOURCE OF TRUTH for capabilities, targets, activities, rules
scripts/build_catalog.py     validate catalog against al: shapes → content/al/catalog.json (generated)
scripts/make_exercises.py    exercise SPEC → Python + R notebooks and checks in content/ (generated)
scripts/make_unit01_pilot.py Python-only Unit 1 scored pilot (called by make_exercises.py)
scripts/prepare_widget_wheels.py  checksum-pinned local piplite wheels for U03 N01 controls
src/engine/                  adaptive-learning engine: pure, deterministic, no JupyterLab imports
scripts/import_ucsf_readings.py  pinned UCSF source to unscored reading notebooks and images
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

1. **Edit sources, not generated files.** Exercise notebooks and checks in
   `content/` come from `scripts/make_exercises.py`; UCSF readings come from
   `scripts/import_ucsf_readings.py`; `content/al/catalog.json` comes from the
   TriG catalog. Change the source or generator, then regenerate.
2. **Use the course material as much as possible:** verbatim learning objectives,
   slide examples and definitions, course scenarios, Excel How-To Scribes, and
   quiz items. Synthetic data only fills gaps, and it extends the course's own
   examples. Expected answers are computed from the data, never typed in.
3. **Every scored exercise notebook ends with a References section** linking the original Google
   Docs and Slides (with slide numbers), the quiz, and guides. The Docs are
   retired once content is in notebooks; the links remain.
4. **Python and R stay in parity** for the existing paired Unit 3 exercises.
   The user requested Python first for new notebooks; Unit 1 Notebook 01 and
   the DHIS2 pilot are explicitly Python only. `jlpm test:checks` must pass
   (it needs `Rscript`).
5. **The engine stays pure.** No DOM, storage, network, clock, or randomness in
   `src/engine/` or `src/identity/`. Policy values are data in the catalog.
6. **Privacy.** Learner identity is an opaque `urn:uuid:`. OIDC sign-in keeps only
   the issuer and an opaque subject, under consent. Never store names, email
   addresses, or tokens. `lite/oidc.json` holds public values only;
   `configure_site.py` rejects secrets.
7. **Public repository.** No secrets, tokens, personal names (including
   facilitators named in course guides), or local paths. Course specifics belong
   in notebooks with attribution; design docs stay generic.
8. **Terminology.** Use **adaptive-learning engine** for the deterministic
   component and **Jupyter kernel** for Python or R runtimes. Never say "kernel"
   alone.
9. **Notebook cell IDs** are "0", "1", "2", "3". A global `nbstripout` git filter
   renumbers IDs this way, so the generator matches it.

## Before you commit

- `jlpm build:site` succeeds (engine tests and export validation run inside it).
- `jlpm test:checks` and `jlpm test:ui` pass.
- If catalog or export shapes depend on a new `al:` change, push the ontology
  repository first: CI validates against its `main`.
- CI (`.github/workflows/ci.yml`) builds, tests, and deploys Pages on `main`.
