#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
test -f .env.officers.local || { echo 'Create ignored local officer configuration first.' >&2; exit 1; }
test -x .venv/bin/python || { echo 'Install the locked root Python environment first.' >&2; exit 1; }
test -x infra/borrowed-fetch/.venv/bin/python || { echo 'Install the isolated locked Fetch environment first.' >&2; exit 1; }
test -f frontend/dist/index.html || { echo 'Build the frontend first.' >&2; exit 1; }
mkdir -p .state
export SOKOSIGNAL_OFFICERS_CONFIG="${SOKOSIGNAL_OFFICERS_CONFIG:-$project_root/.env.officers.local}"
export SOKOSIGNAL_STATE_DB="${SOKOSIGNAL_STATE_DB:-$project_root/.state/demo.sqlite}"
export PYTHONDONTWRITEBYTECODE=1
exec .venv/bin/python -m uvicorn backend.app.api.review:local_app --factory --host 127.0.0.1 --port "${SOKOSIGNAL_PORT:-8000}" --workers 1 --no-access-log
