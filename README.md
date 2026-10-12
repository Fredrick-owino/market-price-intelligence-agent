# SokoSignal — local synthetic market demo

This repository contains a **synthetic** market comparison and private officer
review workflow. Prices, costs, markets and capacity are invented. Approval
changes internal status; it does not send an advisory. No real KAMIS data is
ingested.

## Run locally

Prerequisites: Python 3.12, `uv`, Node 22, npm 9–10 and the existing pinned
Ollama model `qwen3:4b-instruct-2507-q4_K_M` with digest
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
The borrowed Fetch server has its own lock and environment because its MCP SDK
version differs from the application SDK. Do not mix them.

```sh
uv sync --locked --all-groups --python /path/to/python3.12 --no-python-downloads
uv sync --project infra/borrowed-fetch --locked --python /path/to/python3.12 --no-python-downloads
npm ci --prefix frontend
npm run build --prefix frontend
.venv/bin/python infra/create_local_demo_config.py
```

The final command creates two ignored, mode-0600 local files and prints no token.
`infra/officers.example.json` shows the shape only; its placeholder cannot
authenticate and must never be used as a real verifier.
It labels its generated officer `test:local-demo-officer`; this is an automated
demo identity, not independent officer validation. Read `.env.token.local`
locally and enter it into the UI. The token remains in page memory and is not
bundled or persisted by the frontend. Keep the config and token files private.

Start Ollama separately on `127.0.0.1:11434` with the pinned model available in
its local model directory. Then run:

```sh
bash infra/run-local-demo.sh
```

Open `http://127.0.0.1:8000/`. The built frontend and API share this loopback
origin. For frontend development, `npm run dev --prefix frontend -- --host
127.0.0.1 --port 5173` proxies `/api` to the same local backend.

The UI accepts whole quantities from 1 to 1,000 kg for the one approved
synthetic fixture: demo maize, DEMO-1, synthetic region, wholesale, Market A and
Market B, observed 10 October 2026. It displays gross proceeds, costs, net
proceeds, source/provenance, limitations, pending draft version/hash and officer
decision. Model work may take minutes. A failed run remains failed and visible;
start a new attempt after resolving its cause. Refresh requires reentering the
token; the workflow ID alone stays in session storage.

## Checks

```sh
.venv/bin/python -m pytest -q backend/tests
.venv/bin/ruff check backend
.venv/bin/ruff format --check backend
npm run typecheck --prefix frontend
npm run build --prefix frontend
```

For an optional local Chrome walkthrough after the backend and Ollama are
running, use `npm run browser:check --prefix frontend`. This uses the pinned
`playwright-core` package with installed Google Chrome, a disposable browser
profile and the ignored `.env.token.local` credential. It writes synthetic-only
screenshots and a sanitized JSON result under `evals/results/I01.13-browser/`;
it performs two real model workflows and can take several minutes. No browser
trace or credential is retained.

See [architecture](ARCHITECTURE.md), [evaluation and limits](EVALS.md),
[demo script](docs/demo-script.md) and the detailed [I01.13 run report](docs/runs/I01.13-demo-integration.md).
The repository is public following Fredrick's manual visibility change on
12 October 2026. This local configuration is **not** a public deployment: no
public API, frontend hosting or submission is performed by this setup.
Historical KAMIS redistribution rights remain unresolved; repository visibility
does not grant rights to ingest or redistribute those records. The running app
uses only the labelled, project-authored synthetic fixture.
