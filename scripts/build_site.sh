#!/usr/bin/env bash
# Build everything: catalog projection, exercises, engine tests, extension, JupyterLite site.
# Usage: scripts/build_site.sh   (run from the repository root)
set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$PWD/.tools/bin:$PWD/.venv/bin:$PATH"
export MAMBA_ROOT_PREFIX="$PWD/.tools/mamba-root"

command -v micromamba >/dev/null || { echo "micromamba not found: see README (Setup)"; exit 1; }

python scripts/build_catalog.py           # validate catalog with al: shapes, write app-assets/adaptive-learning/catalog.json
python scripts/make_exercises.py          # Python + R notebooks and checks from one spec
python scripts/make_form_library.py       # reviewed local text from supplied form exports
python scripts/add_course_references.py   # local references at the end of each notebook
python scripts/add_course_references.py --check  # reject missing media, external links, and editorial notes
python scripts/assemble_course.py          # one integrated learner sequence
python -m unittest discover -s test -p 'test_unified_course.py'
python -m unittest discover -s test -p 'test_p2_interactions.py'  # supplied calculations and common controls
python -m unittest discover -s test -p 'test_runtime_assets.py'  # pinned, offline xeus metadata
python -m unittest discover -s test -p 'test_units09_14.py'
python -m unittest discover -s test -p 'test_units04_08.py'  # new Python narratives
jlpm test                                 # engine unit tests (writes test-results/learner-export.nq)
python scripts/validate_export.py test-results/learner-export.nq
jlpm build                                # compile extension and labextension
python scripts/sync_labextension.py        # ensure discovery uses this build, not an older shared-data copy
python scripts/prepare_pyodide.py         # locally host the runtime and current notebook packages
python scripts/prepare_widget_wheels.py   # pin and host widget and missingness-plot wheels locally
rm -rf _output .jupyterlite.doit.db
jupyter lite build --pyodide "$PWD/.tools/pyodide"  # site in _output/ (Pyodide + xeus-r Jupyter kernels)
python scripts/fix_pyodide_windows_paths.py  # normalize notebook directories for Pyodide on Windows
python scripts/configure_site.py          # sign-in callback page; lite/oidc.json → alOidc (if present)
echo "Site built in _output/. Serve with: python -m http.server 8765 --directory _output"
