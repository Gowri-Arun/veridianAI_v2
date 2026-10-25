#!/usr/bin/env sh
set -eu

PYTHON_BIN="${PYTHON:-python3}"
echo "Using interpreter: $PYTHON_BIN"
"$PYTHON_BIN" -c "import sys; print(sys.executable); print(sys.version)"

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

VENV_PYTHON="./.venv/bin/python"
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel
"$VENV_PYTHON" -m pip install -r requirements.txt
"$VENV_PYTHON" -m scripts.check_environment

echo "Next commands:"
echo "$VENV_PYTHON -m pytest"
echo "$VENV_PYTHON -m scripts.run_sql_eval"
