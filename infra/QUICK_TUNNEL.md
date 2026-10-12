# Protected Quick Tunnel — bounded owner-authorized test

I01.13, 12 October 2026; Fredrick, solo review. Owner has no domain. This
replaces the domain prerequisite for this temporary demonstration only.
The named-domain design in DEPLOYMENT remains a future alternative.
Preparation initially started no remote process. The owner subsequently
authorized one test of at most 3,600 seconds, exclusively for the supplied exact
email, no additional viewers, paid service or persistent deployment. The
authorized execution record below supersedes the earlier launch prohibition
only within that bound; no remote login result is implied by authorization.

## Official support and verified binary

[Current Quick Tunnel documentation](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
(last updated 30 September, read 12 October) supports `--allowed-mail` with
interactive email one-time-PIN authentication, without a domain/account.
Cloudflare's [protected-tunnel announcement](https://blog.cloudflare.com/protected-quick-tunnels/)
states support starts at 2026.9.3. An omitted allow flag produces a public tunnel;
**no unrestricted fallback is permitted**.

The [official download page](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/)
links Cloudflare's own GitHub releases. Installed the standalone x86-64 binary
from [release 2026.10.0](https://github.com/cloudflare/cloudflared/releases/tag/2026.10.0)
into ignored `.cache/cloudflared/2026.10.0/cloudflared` (mode 0700).
SHA-256, matched to both official asset metadata and release checksum:
`d33ff2d14475178d2012c2c56beba87389ac5ded27649519f198a7d3134a99db`.
Actual version: `cloudflared version 2026.10.0 (built 2026-10-05-17:37 UTC)`.
`tunnel --help` lists `--allowed-mail`; the complete intended command with
`--help` appended exited 0. This verifies CLI flag acceptance, not a live
remote authentication or connectivity result. No system package/PATH change.

## Exact prepared exposure

Only `http://127.0.0.1:8000` is the origin, including built UI and application
HTTP routes. Ollama, databases and credential files are not origins. One exact
owner email is stored in ignored `.env.quick-mail.local`, as supplied in the
request; no wildcard, domain rule or additional email is allowed initially.
The allowlist and credentials stay outside Git. The email gate controls who
can reach the app; it does not grant reviewer authority.

Ignored `.env.quick-tunnel.local.yml` contains only `{}` to prevent inheriting
another default tunnel's ingress/config. The preparation environment contained
no `TUNNEL_*`, `NO_AUTOUPDATE` or `NO_TLS_VERIFY` variables. Before a later
launch, check that no conflicting tunnel environment overrides have been added;
report variable names only, not values. Keep the explicit info log level and
loopback metrics binding; do not enable debug logging, which can log headers.

**Verified underlying connector command (use the bounded runner below):**

```sh
cd /home/fred/Projects/market-intelligence-challenge
SOKOSIGNAL_DEMO_EMAIL="$(cat .env.quick-mail.local)"
.cache/cloudflared/2026.10.0/cloudflared tunnel \
  --config .env.quick-tunnel.local.yml \
  --no-autoupdate --loglevel info --metrics 127.0.0.1:20241 \
  --url http://127.0.0.1:8000 \
  --allowed-mail "$SOKOSIGNAL_DEMO_EMAIL"
```

A literal owner-email command is supplied in the task response; do not copy
private allowlists into public release artifacts. If this binary/flag is lost,
unsupported, fails or does not report protected mode, stop. Never remove
`--allowed-mail`, add broad email rules or start a public workaround.

## Prepared application startup and local checks

The existing local service/authentication remains running unchanged. A separate
ignored mode-0600 token/verifier pair was prepared for this temporary demo:
`.env.token.quick-demo.local` and `.env.officers.quick-demo.local`. Its identity
is `test:temporary-demo-officer`, scoped to `quick-demo-` workflows. This is
synthetic test authority, not a practitioner or production officer. Existing
local test credentials are preserved and will not be reused remotely.
The verifier schema was checked by the actual application's `load_officers`.

For the temporary demo, first follow the idle/restart policy in
[LOCAL_OPERATIONS](LOCAL_OPERATIONS.md). Do not stop a RUNNING workflow or
launch a second API. After the old API exits, a foreground local startup can use:

```sh
cd /home/fred/Projects/market-intelligence-challenge
mkdir -p .state
SOKOSIGNAL_OFFICERS_CONFIG="$PWD/.env.officers.quick-demo.local" \
SOKOSIGNAL_STATE_DB="$PWD/.state/quick-demo.sqlite" \
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python -m uvicorn backend.app.api.review:local_app \
  --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

This uses a separate private database and verifier, preserving previous demo
state. The ordinary launcher hardcodes the original verifier/database; use
this explicit command for the temporary configuration. This configuration was subsequently activated locally and verified; see
[local authentication evidence](../evals/results/I01.13-quick-demo-local-auth.json). Keep Ollama on `127.0.0.1:11434` using the existing pinned
model/directory; do not route port 11434 or start a second model process.

Check listeners and health as in LOCAL_OPERATIONS. The current services were
actually observed at `127.0.0.1:8000` and `127.0.0.1:11434`; API health returned
`ready`, pinned model tag/digest matched, and anonymous pending access returned
401. Repeat checks after switching demo configuration. Privately authenticate
with the dedicated token and confirm the local review desk opens. Enter the
token only into the UI, never shell arguments, logs or a screen recording.

## Checks after authorization — unexecuted acceptance list

- Start the prepared tunnel in a foreground terminal. Confirm startup reports
  protected Quick Tunnel, One-Time PIN, **one address**, no domain rules, and
  the exact port-8000 origin. If any check fails, stop immediately.
- Record the actual HTTPS hostname privately. In a fresh browser session,
  confirm the UI/API are gated before email authentication. Complete the owner
  email PIN flow off-camera. Confirm a different email is denied; the denied
  visitor should perform that test, without exposing their PIN/mailbox.
- After email sign-in, verify missing/invalid officer credentials are still
  denied (401) and the dedicated valid officer can use only its scoped demo
  workflows. Verify the browser's same-origin bearer requests reach the API.
  Official pinned [credential-isolation source](https://github.com/cloudflare/cloudflared/blob/2026.10.0/quicktunnelauth/isolation.go)
  strips its own cookies; application bearer authentication remains in the
  application code. End-to-end header behavior remains to be tested.
- Run exactly one synthetic workflow and inspect current provenance, pending
  version/hash and authoritative decision. No parallel browser test, second
  tab/start or New attempt while RUNNING. The API now queues model workflows behind one process-local slot; still use
  one worker and avoid graph CLI inference outside that slot.
- Refresh/re-authenticate; verify persisted state. For an API restart, drain
  active work, retain the same demo database/verifier and restart the API.
  With the connector still running, the URL remains allocated but the app can
  be unavailable during restart; verify recovery before continuing.
- For a connector restart, retain the workflow ID privately, stop it and start
  the same restricted command. Use the **new URL** and repeat both email and
  officer login. Session storage belongs to the old origin; the new hostname
  will not automatically restore the old tab's workflow ID. Pending drafts can
  be selected after sign-in; interrupted RUNNING recovery may require the
  retained workflow ID and authenticated status polling. Do not create a new
  request while the earlier one is unresolved.

No remote acceptance item is passed by local health/help checks. Live sign-in,
denial, browser bearer forwarding, remote latency and restart recovery remain
unverified until actually executed; owner authorization alone is not evidence.

## Shutdown, restart limits and submission

Stop remote ingress first: press Ctrl-C once in the connector terminal, wait
for exit, and confirm the URL no longer serves the app. Tunnel shutdown does
not cancel an already accepted server workflow. Inspect/drain that workflow
locally, then stop the API and owned Ollama process per LOCAL_OPERATIONS.
Preserve database/checkpoints, tokens and verifier; never delete state to stop.
Do not save PINs, auth cookies, tunnel secrets or debug logs in Git.

[Official limitations](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/):
the URL changes with every new tunnel, access ends when its process stops,
there is no uptime guarantee, the limit is 200 in-flight requests and SSE is
unsupported. Email protection needs an interactive browser; ordinary remote
CLI/API clients cannot replace that login. The current UI polls rather than
using SSE. Keep Ubuntu awake, powered and online; network/connector/app/model
failures can interrupt the demonstration. Do not use this ephemeral, owner-only
URL as a durable public submission artifact or promise judge access. Only the
owner email is allowed initially; any audience expansion needs explicit approval.

Continue the [video script](../docs/demo-script.md) and
[submission checklist](../docs/SUBMISSION_CHECKLIST.md) locally. Public repository
and qualifying public video links are separate artifacts. Neither a tunnel nor
HTTPS improves measured model latency: retained browser pre-review times are
234.38 s and 246.07 s on invented data, already over the planned 180 s video
limit. Practitioner feedback, final form answers, diverse evaluation and
independent review remain outstanding; no release gate is passed.


## Authorized one-hour execution and hard shutdown

The owner explicitly authorized launch after tests, local config verification,
review, commit and push. Use `.venv/bin/python infra/run_quick_demo.py`, which
invokes the same pinned connector flags above with `/usr/bin/timeout
--foreground --signal=KILL 3590s`. The 10-second margin keeps the connection
within the 3,600-second maximum; hard expiry stops only this connector child.
The local API and Ollama are not children of the watchdog and remain running.
No automatic relaunch occurs. The runner checks the binary checksum, private
config permissions, empty ingress, exact email hash and absence of inherited
TUNNEL overrides. Private run/log evidence is exclusive-created under ignored
`.state/quick-tunnel/`; start/expiry times use Africa/Nairobi.

A one-second watchdog test killed its owned sleeping child while another
service process remained alive. This verifies process targeting without any
network exposure. Concurrency tests hold a synthetic model call while two
requests/recovered starts queue, verify responsive polling and real stored-draft
approval/duplicate review, then verify failure releases the slot. These tests
use mocked model/network responses with real MCP/checkpoints, not live inference.

Before launch, the actual temporary API rejected anonymous/invalid/original
credentials (401) and wrong workflow scope (403), accepted its dedicated token
(200), and both API/model listeners remained loopback-only. Original state and
credentials were byte-verified unchanged on switch. All remaining live remote
checks must be reported from actual observations. Owner login is performed on
the owner's phone; never collect email PIN or officer token in chat. If access
restriction fails, signal only the exact connector PID and confirm it exits.
At expiry, verify that PID is gone and an anonymous remote probe cannot serve
application content; confirm local app/model remain available. A still-visible
Cloudflare login page is not evidence that the origin remains reachable.
