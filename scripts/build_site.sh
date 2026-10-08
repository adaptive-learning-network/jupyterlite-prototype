#!/usr/bin/env bash
# Build everything: catalog projection, exercises, engine tests, extension, JupyterLite site.
# Usage: scripts/build_site.sh   (run from the repository root)
set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$PWD/.tools/bin:$PWD/.venv/bin:$PATH"
export MAMBA_ROOT_PREFIX="$PWD/.tools/mamba-root"

command -v micromamba >/dev/null || { echo "micromamba not found: see README (Setup)"; exit 1; }

python scripts/build_catalog.py           # validate catalog with al: shapes, write content/al/catalog.json
python scripts/make_exercises.py          # Python + R notebooks and checks from one spec
jlpm test                                 # engine unit tests (writes test-results/learner-export.nq)
python scripts/validate_export.py test-results/learner-export.nq
jlpm build                                # compile extension and labextension
python scripts/prepare_pyodide.py         # locally host the runtime and current notebook packages
python scripts/prepare_widget_wheels.py   # pin and host the U03 N01 sorting-widget wheels locally
rm -rf _output .jupyterlite.doit.db
jupyter lite build --pyodide "$PWD/.tools/pyodide"  # site in _output/ (Pyodide + xeus-r Jupyter kernels)
python scripts/configure_site.py          # sign-in callback page; lite/oidc.json → alOidc (if present)
echo "Site built in _output/. Serve with: python -m http.server 8765 --directory _output"
