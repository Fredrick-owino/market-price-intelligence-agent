# I01.15 — HTTPS working-demonstration link preparation

Prepared 15 October 2026 for Fredrick. **No connector is launched or authorized.**
The previous one-hour authorization expired; it cannot authorize another route,
viewer, extension or unrestricted fallback. Owner reports no judge emails or
judging dates; current domain/account control has not been supplied. Owner says
form fields are already filled and does not want the form connected/operated.
No form edits or submission are performed.

## Current verified origin

`http://127.0.0.1:8001` serves published revision
`629ffbdae8a9fd06c67dd940fb9e0dbf4bc29a01` in both backend and frontend
(`/api/v1/preview-version`). Uvicorn uses one worker and
`.state/dashboard-preview.sqlite`; original `.state/quick-demo.sqlite` and port
8000 remain separate. Pinned Ollama is private on `127.0.0.1:11434`. UI uses
three-second polling, not Server-Sent Events. Real model/borrowed Fetch/three
own-MCP/approval already passed in I01.14; no new workflow in this task.

Current read-only checks: health 200, anonymous/invalid officer access 401,
valid prepared demo officer access 200, seven pending drafts. Preview has ten
existing drafts; original has seven; no RUNNING requests in either. No cloudflared
process exists. API/model listeners are loopback-only.

Verified installed cloudflared 2026.10.0 SHA-256:
`d33ff2d14475178d2012c2c56beba87389ac5ded27649519f198a7d3134a99db`.
Existing mail/config/officer/token files are 0600 and preserved. Prior connector
watchdog stopped on 12 October at 16:04:44 EAT with exit 124 as intended.

## Which route is suitable?

| Option | Suitability | Prerequisites / availability |
|---|---|---|
| Protected Quick Tunnel to 8001 | Fastest supervised demonstration without a domain/account | New approval, exact viewer emails, absolute expiry, remote gate/credential checks. Unreliable as a fixed submission link across restarts. |
| Named Cloudflare Tunnel + Access on the same Ubuntu host | Preferred for a judging URL expected to stay constant | Cloudflare account/domain control, deny-by-default Access policy, exact judge emails, approved window and service supervision. None created here. |

The installed binary supports repeated `--allowed-mail` inputs. The same-origin
UI/API and polling design are compatible with Quick Tunnel. Existing
`infra/run_quick_demo.py` is **not the new launcher**: it pins the old owner-only
address, port 8000, 3590 seconds and an already-used run record. Do not reset its
history, change its pinned email, or reuse its expired authorization.

Cloudflare documents interactive email-PIN gates, temporary changing hostnames,
no Quick Tunnel uptime guarantee and no SSE support. With the current app's
polling, the SSE limit is compatible. Changing Quick Tunnel audiences also means
restarting the connector and updating its URL. [Quick Tunnel documentation](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

Quick Tunnel compatibility is verified locally, **not remote connectivity or
judge accessibility**. There is no new HTTPS URL until a separately authorized
launch produces one. Never submit loopback, the expired URL or example.org.

## Concrete disabled configuration

[judging-access.example.json](judging-access.example.json) is a preparation
record, **not an executable deployment file**. Launch is false, viewer list empty,
start/end null, original authorization non-reusable. Proposed origin is pinned
to 8001, model exposure false, worker count one, snapshot unchanged and provider
spend capped at zero pending any explicit purchase approval.

For a newly approved short Quick Tunnel session, use the same checksum-pinned
binary, an ignored mode-0600 empty config copied from
[judging-quick-config.example.yml](judging-quick-config.example.yml), and this
argument-array design (not executed):

```text
/usr/bin/timeout --foreground --signal=KILL APPROVED_REMAINING_SECONDS
.cache/cloudflared/2026.10.0/cloudflared tunnel
--config .env.judging-quick-config.local.yml
--no-autoupdate --loglevel info --metrics 127.0.0.1:20242
--url http://127.0.0.1:8001
--allowed-mail EXACT_APPROVED_EMAIL_1
--allowed-mail EXACT_APPROVED_EMAIL_2
```

Build arguments from the private exact email list; do not evaluate a shell string.
Omit the second flag only if there is one approved viewer; refuse zero viewers.
No wildcard/domain/all-users grant. Check conflicting `TUNNEL_*`, `NO_AUTOUPDATE`
and `NO_TLS_VERIFY` environment **names only**; reject overrides. Validate config,
binary checksum, build SHA and loopback bindings before connecting. Never omit
`--allowed-mail`. No debug logs. Private logs/run records must be new mode-0600
files beneath a new `.state/judging-tunnel/` run ID; preserve expired records.
`APPROVED_REMAINING_SECONDS` is time until the approved absolute UTC end, capped
by the approved duration; reject expired/missing approval. A restart must not
reset the expiry. Stop only this connector on failed protection/expiry.

For the stable option, [judging-named-tunnel.example.yml](judging-named-tunnel.example.yml)
routes one placeholder hostname to port 8001 with a catch-all 404. Fill actual
UUID/domain/credential path privately only after account/domain/audience approval.
Configure a self-hosted Access application covering **every path** of that
hostname, email one-time PIN, one allow policy for exact approved emails, no
Everyone/Bypass/Service Auth bypass. Apply deny-by-default Access BEFORE publishing
DNS/routing; consider Cloudflare's account-level
[Require Access protection](https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/require-access-protection/).
Do not provision an unprotected intermediate route. Keep tunnel credentials in
ignored 0600 files; Cloudflare credential is distinct from officer/PIN credentials.

## Exact judge access packet and officer scope

Each approved judge needs these privately supplied items:

1. Actual tested HTTPS URL, supported browser, and authorized access start/end
   stated in EAT and UTC. Quick option also needs hostname-change/contact procedure.
2. Their **exact allowlisted email** and access to that inbox. They enter their
   own short-lived emailed PIN at Cloudflare; owner/agent does not ask for the PIN.
   No Cloudflare account or local app install is needed for the browser gate.
3. A **separate demo officer token**, entered in SokoSignal's `Officer token`
   input after email verification. Cloudflare email success does not approve a
   draft or replace the bearer credential. Never put that token/PIN in Git,
   screenshots, video, URL path/query/fragment, public document or contact link.
4. Labelled account ID/scope, brief 650 kg sample workflow instructions, and the
   statement that approval is an internal test with no farmer delivery. Review
   is per exact draft ID/version/hash. Only one workflow can run at a time.

The existing token path `.env.token.quick-demo.local` was verified; its value
remains private and is **not prepared for broad judge distribution**. That
`test:temporary-demo-officer` account can access existing snapshot pending drafts.
For unsupervised judging, prepare a fresh independent random token per judge and
an additive disjoint account, e.g. [judging-officer-entry.example.json](judging-officer-entry.example.json)
(`test:judge-001`, `judge-001-` prefix, no existing workflow grant). Store token
in ignored `.env.token.judge-001.local` (0600), only its SHA-256 verifier in the
private officer roster, and privately deliver it through the organiser's approved
channel. No new token/account was created here.

During authorized activation, back up the current private roster, retain all
existing entries/verifiers/scopes, add disjoint judge entries to the roster the
preview already reads (`.env.officers.quick-demo.local`), validate it through the
existing `load_officers` boundary and restart **only idle preview 8001** to load
it. Preserve every draft; do not delete/copy/reset SQLite. Existing original
8000 process remains untouched; keep it idle for model capacity. If altering this
shared private roster is unacceptable, a separately approved judging factory/
private roster is required; do not silently modify published app code after freeze.

Disjoint judge scopes protect old owner drafts (403) and attribute demo decisions
per test identity. Email and app token remain two independent checks; the app does
not auto-bind Cloudflare email headers to reviewer authority. Private token
sharing must preserve that distinction. No real extension-officer endorsement
is inferred. Revoke future judge accounts after the approved window only with
owner authorization, without rewriting their recorded decisions.

## Availability, duration and cost

**Proposal, not authorization:** an initial **seven-day** judging availability
window beginning on the agreed activation date, with an absolute recorded end
and a 30-minute owner-only protection test beforehand if separately authorized.
Dates are unknown; do not invent calendar endpoints or launch now. Extensions
require explicit new approval and organiser schedule. One hour is inadequate for
unknown asynchronous judging. Seven days is a planning cap, not an uptime promise
or proof it covers the organiser's review period.

Quick Tunnel has a new hostname whenever its connector is recreated, including
host reboot. A process supervisor cannot make that hostname stable. If selected,
Fredrick must keep the process up, monitor it and have organiser approval to
update the link after a restart. Existing form edit permissions/update policy are
unknown. If the organiser requires a fixed URL, choose the named tunnel or wait;
no unrestricted fallback. A static README redirect that requires post-cutoff Git
commits is not an acceptable recovery plan.

For the named route, retain the same tunnel UUID/DNS/Access application on restart.
After authorization, the owner/driver can supervise cloudflared as a Linux
service ([official service procedure](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/)).
Prepare API/model startup using the existing pinned model store and one worker;
never launch duplicate listeners. Install/enable no service or global setting in
this task. Use an absolute-expiry stop timer/check independent of process uptime,
so automatic restart does not renew the exposure. Restore Access deny-first on
restart before publishing any route. Local API/model may remain running after
connector expiry. Recheck gate, version and pending state after recovery.

The Ubuntu host must be powered, awake and connected throughout. Closing a
terminal, logging out without supervision, suspend, power loss, router outage or
upstream Internet failure can break availability. Stable DNS does not keep the
app/model alive. Public Fetch MCP also needs outbound Internet. Retain SQLite and
its journals; restart from the same paths, recover unfinished work before any new
request. Do not silently disable sleep, change global networking, add hardware,
provision a GPU or expand to multiple API workers.

Protected Quick Tunnel service price is **$0** per
[Cloudflare's announcement](https://blog.cloudflare.com/protected-quick-tunnels/).
[Current pricing](https://www.cloudflare.com/plans/) lists Zero Trust free for up
to 50 users at $0; verify actual account eligibility before named-route setup.
Existing Ubuntu compute has no new rental charge. Power/Internet usage and domain
registration/renewal are additional owner expenses, not estimated here. No paid
subscription, domain purchase or spending is approved/incurred in this task.

## Form: URL versus access instructions

**Unconfirmed.** Earlier inspection of the official linked form required sign-in;
no connected browser tabs were available now. Owner says fields are already
filled and declines connecting the form. The actual demonstration field type,
URL validation, access-notes field and edit permission were not inspected. Do not
claim the form accepts a combined URL/notes answer or that it has been submitted.

Prepared non-secret instruction text, to use only in an actual permitted notes
field/private organiser handoff:

> Protected browser demo. Sign in at the link using your pre-approved email and
> its emailed PIN, then enter the separately supplied SokoSignal demo officer
> token. The sample workflow supports up to 1,000 kg; only one workflow can run
> at a time. Approval is internal and sends no advisory to farmers. Availability
> dates and support contact will be supplied with your access details.

Put only the actual HTTPS URL in a URL-validated field. If there is no separate
instructions field, ask the organiser which private channel accepts the access
packet and whether email-gated demonstrations are allowed. Never append a token
or PIN to the URL. No judges can access the current owner-only allowlist unless
explicitly added after authorization.

## Verification procedure — remote steps NOT performed yet

1. Get explicit exposure authorization with exact emails, actual start/end,
   chosen route/hostname and spending limit; confirm organiser acceptance of
   protected access, private token delivery and any Quick-hostname updates.
2. Local preflight: pinned model/digest, current backend/frontend SHA, existing
   snapshot/credential backup, idle queues, one worker and loopback listeners.
   Confirm original 8000 is idle. Check no old connector, verified binary and
   new allowlist/config/private permissions. Do not launch until approval exists.
3. Add scoped judge credentials only after approval, preserving all prior
   records/verifiers; restart idle preview only. Verify anonymous/invalid token
   401, correct judge token 200, old-owner workflow access 403 and unchanged
   backend/frontend SHA. Bind no Ollama/database/file-server route.
4. Named option: configure and verify deny-by-default Access first, then route.
   Quick option: connector command MUST carry exact `--allowed-mail` arguments
   at creation. Start the bounded connector only when separately authorized.
5. From a fresh external browser: signed-out/unauthorized email cannot retrieve
   app content at `/`, `/api/v1/drafts/pending`, `/health` or version path.
   Correct judge types their PIN; successful gate then shows SokoSignal sign-in.
   Missing/wrong officer token still receives 401. Check TLS, all-path coverage,
   private `.env` paths unavailable and normal same-origin API bearer forwarding.
6. After separately authorized remote operational test, run a NEW labelled
   650 kg sample: real Fetch/Qwen/three MCP tools, actual progress/EAT times,
   pending exact draft/hash, invalid/stale decisions denied, valid demo approval
   and persisted completion. Inspect deterministic arithmetic/provenance.
   A second different request while RUNNING must return 409 without a new run.
   Record failures honestly, with no replay/fabricated result or model substitution.
7. Test controlled API/connector recovery without clearing state. Confirm pending
   draft/hash/decisions persist and model remains loopback. Named URL must stay
   the same; Quick URL changes on recreation and must be replaced through the
   organiser's permitted channel. Reverify access after restart.
8. On any failed protection, stop ONLY the new connector and confirm app content
   is no longer remotely retrievable. At absolute expiry, verify connector exit,
   remote origin unreachable, local API/model alive and all original rows intact.
9. Record final tested URL/access delivery/timezone/version/window. Only then
   fill the demonstration URL through the owner's form process. No accessible
   link, judge login, hosted-workflow or submission-readiness pass is claimed now.

Task status: **prepared, not activated**. Immediate blockers: launch authorization,
exact judge identities/window, private access delivery, stable-domain/account
control if required, and form acceptance/update policy. Next dependency-ready
step is owner/organiser agreement on those concrete access details, followed by
an explicitly authorized protection test. No commit/push in this preparation.

## Final preparation checks and observed local activity

Cloudflared `tunnel --help` accepted the exact 8001/two-email argument combination
using only reserved example.org addresses, without connecting. Named ingress
`ingress validate` returned `OK`. Disabled JSON configuration and placeholder
judge account validated. Focused isolated watchdog/concurrency/preview tests:
**10 passed in 8.56 seconds**. These tests do not launch a tunnel or operational
model run. Public preparation files contain neither the exact existing private
email nor officer token. Published application code remains unchanged.

A new local preview workflow `quick-demo-dd5e6178-b1d1-5987-ba44-f613998a1b7e`
was observed during preparation: draft created 15 Oct 2026 02:29:26 EAT, approved
02:30:09 EAT. This task did not start/approve that operational run. It is preserved.
Final preview counts: eleven drafts/four decisions; original seven/two unchanged.
After excluding only that new workflow, all preview draft/decision/audit/action/
run table hashes match the initial baseline. Existing private file hashes also
match. A first whole-table preservation assertion detected the addition and was
corrected to check pre-existing rows separately; no record was modified to make
that check pass. No cloudflared process or new HTTPS route exists.
