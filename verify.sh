#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [[ -x "${ROOT}/.venv/bin/python3" ]]; then
  PYTHON="${ROOT}/.venv/bin/python3"
else
  PYTHON="python3"
fi
"$PYTHON" -m ruff check tools tests
"$PYTHON" -m ruff format --check tools tests
"$PYTHON" -m yamllint -c .yamllint.yaml campaigns
"$PYTHON" -m pytest
"$PYTHON" -m tools.campaign
