# Ubuntu local demonstration operations

Prepared 12 October 2026, I01.13. Selected deployment: the existing Ubuntu
machine, built frontend and API at `http://127.0.0.1:8000`, Ollama at
`127.0.0.1:11434`, local SQLite. No domain is available and remote access stays
disabled. Do not activate the tunnel example, open inbound ports or change
these bindings. These instructions have been checked against the launcher and
API source; this task did not restart or stop running services.

## Ownership, prerequisites and concurrency

Run from `/home/fred/Projects/market-intelligence-challenge`. Keep the two locked
Python environments, existing model directory, built `frontend/dist`, ignored
`.env.officers.local` verifier and `.env.token.local` token. The launcher uses
`.state/demo.sqlite`; retain that database and any SQLite sidecar files. Do not
regenerate credentials or reset state as part of restart.

Use **one API process, one Uvicorn worker, one operator and one active workflow**.
The launcher already sets `--workers 1`. The API now enforces one active retrieval/model workflow per API process with
an async model slot. Additional RUNNING requests wait with API phase
`queued_for_model`; polling and unrelated draft review remain available. The
slot is released on success, failure or cancellation. Blocking SQLite work
in async routes is dispatched to threads so lock waits cannot stall the event
loop/checkpoint writer. This is a process-local
limit: multiple API workers or graph CLI processes are still unsupported. The UI's New attempt control can abandon its view of a
RUNNING workflow without cancelling server work. Do not click New attempt,
change quantity and start again, open another request tab, run the browser
test, or run a graph CLI against this database while a workflow is RUNNING.
Other Ollama inference clients should also be idle for this demonstration.

Wait until PENDING_REVIEW, then finish approval/rejection or explicitly defer
review before starting another workflow. Use one decision operator; wait for
the authoritative outcome before retrying. On an interrupted decision, recover
the same draft before any new request. Duplicate retries are tested only with
the same request/decision key and payload; a new tab/New attempt may generate
a new key. The software model slot complements this operator policy; it is not a
multi-process lock or measured concurrent-capacity claim. Multi-worker/multi-host operation is unsupported.

## Local readiness and start

In an ordinary Ubuntu terminal, inspect listeners without printing environment
variables or credentials:

```sh
cd /home/fred/Projects/market-intelligence-challenge
ss -ltnp 'sport = :8000 or sport = :11434'
```

If a port is already occupied, identify its owner. Reuse the existing correctly
bound service or stop it through its owning terminal/service manager; do not
launch a second instance. Both ports must be loopback-only. If an unexpected
public binding is present, resolve it before the demonstration.

If Ollama is not running, use its existing owner terminal and **the same model
directory used by the verified deployment**. If that directory is non-default,
set `OLLAMA_MODELS` locally to its actual path before the following command;
the path is not supplied by the repository. Do not download another model to
mask a missing-directory error. Foreground model terminal:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NUM_PARALLEL=1 ollama serve
```

`OLLAMA_NUM_PARALLEL=1` serializes model requests in this process; it does not
prevent concurrent application workflows. For an already manager-owned Ollama,
use its existing configuration/owner procedure rather than creating a second
service. No systemd unit is supplied or installed by this repository.

In a second foreground terminal:

```sh
cd /home/fred/Projects/market-intelligence-challenge
bash infra/run-local-demo.sh
```

In a third terminal, check readiness without credentials:

```sh
curl --noproxy '*' --fail --silent --show-error --max-time 5 http://127.0.0.1:8000/health
curl --noproxy '*' --fail --silent --show-error --max-time 5 http://127.0.0.1:11434/api/version
curl --noproxy '*' --fail --silent --show-error --max-time 5 http://127.0.0.1:11434/api/tags
ss -ltnp 'sport = :8000 or sport = :11434'
```

Expect API `status: ready`, a responding model service and installed tag
`qwen3:4b-instruct-2507-q4_K_M` with digest
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
Health alone does not verify model inference, borrowed public retrieval or
officer permission. Fetch still needs outbound public network access even
though the application is loopback-only. Open the local browser and authenticate
privately; check the current draft/status before starting work.

## Planned restart and recovery

1. Stop new requests and ask the sole operator to wait for RUNNING to become
   pending or failed. The UI polls every three seconds; latency can be minutes.
   Record the workflow ID, status and, where present, draft ID/version/hash and
   outcome in private local notes. The API allows up to 300 seconds per model
   request and 900 seconds total model workflow; these are caps, not promises.
2. Once idle, press Ctrl-C once in the foreground API terminal. Wait until it
   exits and port 8000 is free. Background model tasks are not explicitly
   drained by an application shutdown hook; do not assume Ctrl-C finishes an
   in-flight run. Never start a replacement until the old process has exited.
3. Leave Ollama running for an API-only restart. To restart Ollama too, stop it
   through its owning terminal/manager once no inference is active, confirm
   port 11434 is free, then start the same model directory and loopback settings.
4. Rerun the launcher from this checkout with the same SQLite and verifier
   files. Repeat readiness/binding checks. Refresh the existing browser tab,
   privately reauthenticate and inspect the same workflow. Session storage
   keeps the workflow ID; refresh clears the token.
5. Confirm approved/rejected outcomes and draft version/hash remain unchanged.
   Actual completed-outcome persistence is recorded in
   [the restart evidence](../evals/results/I01.13-restart-http.json). This is
   not evidence of a graceful shutdown during live inference.

After an unexpected crash with RUNNING state, authenticated status polling for
the **same workflow** schedules recovery from available checkpoints. Startup
alone does not sweep all runs. An uncheckpointed model step may execute again;
bounded private-draft idempotency does not imply exactly-once inference. If a
decision was stored before graph resume, status polling reconciles the stored
decision. Check the exact current state before retrying a decision. Never
manually set database status or use the simulated-review CLI as officer approval.
If the recovered run becomes FAILED, retain its failure and use a new attempt
only after the cause is resolved. Crash-during-inference recovery has not been
verified in this browser evidence.

## Shutdown and private state

Stop new starts, wait for active work to become pending/failed/completed and
record any deliberately deferred pending review. Stop the API with Ctrl-C and
wait for exit. Then stop Ollama through the terminal/manager that owns it, if
this demo exclusively owns that process. Confirm the respective listeners are
absent with `ss`; another service's listener must be reported, not killed by
name or port. Close the demo browser tab to remove its in-memory token.

Keep state and credentials for next startup. If making a private backup, stop
all database writers first, preserve the SQLite database and existing sidecars
together in a restricted local location outside Git, and treat copies as
private. Backup/restore has not been trialled here. Do not remove `.state`,
token/verifier files or model files for shutdown. Do not print tokens, put them
in shell arguments/history, record authorization headers or stage local state.


## Optional protected Quick Tunnel — preparation only

The owner requested domain-free preparation after this local guide was written.
Use [QUICK_TUNNEL](QUICK_TUNNEL.md) for the verified restricted launch command,
separate demo verifier/database, authorization boundary and post-launch checks.
Connector preparation originally had no running tunnel; see QUICK_TUNNEL for
the subsequently authorized one-hour execution boundary. After an authorized remote demonstration, stop the
connector first, then drain local work and stop services. A new tunnel origin
has different browser session storage; keep the interrupted workflow ID privately
and recover it before starting another. Email access does not replace officer
bearer authentication or establish practitioner authority.
