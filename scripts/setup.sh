#!/usr/bin/env bash
# One-command, idempotent setup for local development and CI.
#
#   scripts/setup.sh              # everything, including the Playwright browser
#   SKIP_PLAYWRIGHT=1 scripts/setup.sh
#
# Installs into the repository only: .venv/ (Python tooling), node_modules/,
# .tools/bin/micromamba (builds the WebAssembly R environment). Nothing global.
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON=${PYTHON:-python3}

echo "==> Python tooling (.venv)"
[ -x .venv/bin/python ] || "$PYTHON" -m venv .venv
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r lite/requirements.txt

echo "==> Node dependencies"
.venv/bin/jlpm install --immutable 2>/dev/null || .venv/bin/jlpm install

echo "==> micromamba (.tools/bin)"
if [ ! -x .tools/bin/micromamba ]; then
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) platform=osx-arm64 ;;
    Darwin-x86_64) platform=osx-64 ;;
    Linux-x86_64) platform=linux-64 ;;
    Linux-aarch64|Linux-arm64) platform=linux-aarch64 ;;
    *) echo "Unsupported platform $(uname -s)-$(uname -m)"; exit 1 ;;
  esac
  mkdir -p .tools
  curl -fsSL "https://micro.mamba.pm/api/micromamba/${platform}/latest" | tar -xj -C .tools bin/micromamba
fi
.tools/bin/micromamba --version

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
