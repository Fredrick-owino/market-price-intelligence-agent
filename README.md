# SokoSignal — local synthetic market demo

This repository contains a **synthetic** market comparison and private officer
review workflow. The recorded review uses an authenticated automated demo
identity; no named real officer approval has been established. Prices, costs,
markets and capacity are invented. Approval
changes internal status; it does not send an advisory. No real KAMIS data is
ingested. Intended users are extension officers supporting smallholder maize
farmers in Kenya. The intended workflow compares quoted prices, harvest quantity,
transport and other confirmed costs, and prepares a sourced advisory for review.
No named office, partnership, endorsement, adoption or practitioner validation
is confirmed. The demo edits quantity only; prices/costs come from its invented
fixture, not a general live quote/cost entry system.

## Run locally

Prerequisites: Python 3.12, `uv`, Node 22, npm 9–10 and the existing pinned
Ollama model `qwen3:4b-instruct-2507-q4_K_M` with digest
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
We reuse upstream Fetch retrieval/robots behavior instead of recreating its MCP
protocol and text parsing; our wrapper restricts destination and verifies the
public synthetic snapshot. Fetch has a separate lock/environment because its
MCP SDK differs from the application SDK. Do not mix them.

```sh
# First start an existing complete Ollama runtime on 127.0.0.1:11434.
# Reuse its existing model directory; no weights are downloaded by this command.
make demo
```

`make demo` installs both locked project Python environments, runs `npm ci`,
builds the UI, creates a fresh private demo credential pair if absent, checks
model metadata and starts one loopback API worker. Existing credentials/state
are preserved. Python 3.12 must be available (`SOKOSIGNAL_PYTHON` can select its
path); no system packages or global settings are changed. Network access is
needed for dependencies on a fresh machine and for actual public fixture Fetch.
Use `SOKOSIGNAL_PORT=8020 make demo` for a separate checkout; its generated
credentials and `.state/demo.sqlite` stay in that checkout. Never copy another
checkout's private token/config. Sharing an existing model service is allowed,
but run inference serially. Stop only this API via Ctrl-C, retaining its state.
A host shutdown stops these manually started services; no autostart is installed.

For this verified Ubuntu host, the complete existing runtime is
`/home/fred/.local/share/sokosignal/ollama-0.40.2/bin/ollama` and existing weights
are `/home/fred/.local/share/sokosignal/models`. Set `OLLAMA_MODELS` to the actual
existing directory and `OLLAMA_HOST=127.0.0.1:11434` before `ollama serve`.
Use a complete installation: metadata can succeed even when its runner is
missing; actual workflow inference is a separate readiness check. CPU-only
measurements use this approximately 15 GiB RAM host; no GPU/VRAM requirement
or portable latency guarantee is claimed. Python/Node/uv/Ollama are prerequisites.

The configuration step creates two ignored, mode-0600 local files and prints no token.
`infra/officers.example.json` shows the shape only; its placeholder cannot
authenticate and must never be used as a real verifier.
It labels its generated officer `test:local-demo-officer`; this is an automated
demo identity, not independent officer validation. Read `.env.token.local`
locally and enter it into the UI. The token remains in page memory and is not
bundled or persisted by the frontend. Keep the config and token files private.

After `make demo`, the API is already running in that terminal; open the
browser below. Do not start a second API. For a later restart, once that API
has exited and dependencies/UI are already prepared, leave the pinned model
service on loopback and use this launcher:

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
decision. Actual sanitized tool events show inputs, outputs and timestamps.
New overlapping starts reject; identical retries remain idempotent. Model work
may take minutes. A failed run remains failed and visible;
start a new attempt after resolving its cause. Refresh requires reentering the
token; the workflow ID alone stays in session storage.

### Shared demonstration sign-in

To offer the intentionally visible sample code, stop any previous instance on
port 8002 and start the separate sample workspace after installing the above
prerequisites and building the frontend:

```sh
.venv/bin/python -m uvicorn infra.public_demo:local_app --factory --host 127.0.0.1 --port 8002 --workers 1
```

Open `http://127.0.0.1:8002`. Focus **Officer token** or select **Try the demo**,
then **Use demo token** and **Open review desk**. The deliberately public
`SOKO-DEMO` code accesses only the shared `test:public-demo` sample workspace in
`.state/public-demo/`; it cannot access existing officer workflows. Anyone with
the code can review its sample drafts. Demo decisions do not establish verified
officer identity or endorsement. Ordinary private mode never exposes its token.
This command binds locally; publishing a remote route remains a separate action.
Only one local demonstration should use the shared model at a time.

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


## Verified fresh-checkout scope

On 13 October 2026, a fresh remote clone of milestone 88b25a0 ran make demo
on loopback port 8020 with new locked Python environments, node_modules,
private credential pair and SQLite state. Existing package cache/model service
were reused; no credentials or model weights copied. Actual 900 kg model/Fetch/
own-MCP comparison and authenticated demo approval passed in 129.541 s to
review. This same-host solo trial is not independent cross-machine verification.
See [evidence](evals/results/I01.13-fresh-checkout-verification.json).
Current unresolved feature: request-changes/revision through UI/API, reported
as an evaluation failure. No public video, hosting or submission performed.


Submission package: [official-requirement audit](docs/SUBMISSION_READINESS.md),
[prepared form answers](docs/submission-answers-draft.md),
[video metadata/upload instructions](docs/VIDEO_UPLOAD_PACKAGE.md), and
[third-party notices](THIRD_PARTY_NOTICES.md). A documented unresolved evaluation
case is intentionally retained; it does not automatically require another
feature. Independent peer/different-host trials are internal goals, not extra
requirements added to the official submission list. No upload/submission/freeze
has been recorded. The owner reports the organiser cutoff as 15 October 2026,
23:59 Africa/Nairobi (20:59 UTC); original organiser notice was not independently
inspected. See [current status](docs/STATUS.md) for the evidence distinction.
