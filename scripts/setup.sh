#!/usr/bin/env bash
# One-command, idempotent setup for local development and CI.
#
#   scripts/setup.sh              # everything, including the Playwright browser
#   SKIP_PLAYWRIGHT=1 scripts/setup.sh
#
# Installs into the repository only: .venv/ (Python tooling), node_modules/,
# and Playwright browsers. Nothing global.
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON=${PYTHON:-python3}
# Nested package scripts call jlpm/jupyter by name; resolve them from .venv.
export PATH="$PWD/.venv/bin:$PATH"

echo "==> Python tooling (.venv)"
[ -x .venv/bin/python ] || "$PYTHON" -m venv .venv
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r lite/requirements.txt

echo "==> Node dependencies"
.venv/bin/jlpm install --immutable 2>/dev/null || .venv/bin/jlpm install

echo "==> Extension (editable) and labextension link"
.venv/bin/jlpm build
.venv/bin/python -m pip install --quiet -e . --no-build-isolation
.venv/bin/jupyter labextension develop --overwrite . >/dev/null
extensions=$(.venv/bin/jupyter labextension list 2>&1)
case "$extensions" in *jupyterlite-al-engine*) ;; *) echo "labextension not registered"; exit 1 ;; esac

if [ -z "${SKIP_PLAYWRIGHT:-}" ]; then
  echo "==> Playwright browser"
  if [ -n "${CI:-}" ]; then npx playwright install --with-deps chromium; else npx playwright install chromium; fi
fi

echo "==> Setup complete. Next: jlpm build:site && jlpm test:all"
