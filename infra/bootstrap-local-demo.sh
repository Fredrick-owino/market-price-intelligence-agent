#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
command -v uv >/dev/null || { echo 'Missing uv prerequisite.' >&2; exit 1; }
command -v npm >/dev/null || { echo 'Missing Node/npm prerequisite.' >&2; exit 1; }
uv sync --locked --all-groups --python "${SOKOSIGNAL_PYTHON:-python3.12}" --no-python-downloads
uv sync --project infra/borrowed-fetch --locked --python "${SOKOSIGNAL_PYTHON:-python3.12}" --no-python-downloads
npm ci --prefix frontend
npm run build --prefix frontend
if [[ ! -e .env.token.local && ! -e .env.officers.local ]]; then
  .venv/bin/python infra/create_local_demo_config.py
fi
.venv/bin/python - <<'PY'
import hashlib,json
from pathlib import Path
from urllib.request import urlopen
from backend.app.agent.model_workflow import MODEL, EXPECTED_DIGEST
from backend.app.api.review import load_officers
config=Path('.env.officers.local');token=Path('.env.token.local')
for file in [config,token]:
    if file.stat().st_mode & 0o777 != 0o600:raise SystemExit('Local credential permissions must be 0600')
officers=load_officers(config)
if hashlib.sha256(token.read_bytes().strip()).hexdigest() not in {o['token_sha256'] for o in officers}:
    raise SystemExit('Existing credential pair does not match; preserved, not regenerated')
try:
    with urlopen('http://127.0.0.1:11434/api/tags',timeout=10) as response:tags=json.load(response)
except Exception:
    raise SystemExit('Start the existing complete pinned Ollama runtime on loopback first; no model downloaded')
if not any(m['name']==MODEL and m['digest']==EXPECTED_DIGEST for m in tags['models']):
    raise SystemExit('Existing model/digest missing; no download or fallback')
print('Pinned model metadata and new/existing private demo configuration checked; inference verified by workflow separately.')
PY
exec bash infra/run-local-demo.sh
