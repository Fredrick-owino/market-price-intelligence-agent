# Evaluation evidence and current limits

All market records below are synthetic. The actual local HTTP/model attempt on
12 October 2026 used 500 kg. Deterministic expected results are Market A gross
KES 20,000, costs KES 2,000, net KES 18,000; Market B gross KES 22,500, costs
KES 8,000, net KES 14,500. Market A leads by KES 3,500. These are scenario
calculations, not observed market opportunities or an income claim.

| Check | Actual result |
|---|---|
| Backend regression after final request/frontend integration | 147 passed in 147.84s using freshly synced locked application and borrowed-server environments; includes real local MCP transport with mocked network/model cases. |
| Frontend TypeScript and Vite production build | Both passed; build produced static assets. |
| Live HTTP attempt 01 | Failed closed after 222.297s with `request_timeout`; no review outcome. Retained in [attempt 01](evals/results/I01.13-actual-http-attempt-01.json). |
| Live HTTP attempt 02 | Actual public synthetic Fetch over borrowed MCP, actual pinned local Qwen, three own tools, persisted draft in 147.214s; test officer HTTP approval → `approved_internal_review`, retry 200, anonymous 401. [Attempt 02](evals/results/I01.13-actual-http-attempt-02.json). |
| Rejection path | Separate pending synthetic own-MCP workflow rejected through actual HTTP; status `REJECTED`, retry 200. No model/borrowed fetch in that specific check. [Rejection](evals/results/I01.13-rejection-http.json). |
| API restart | Approved and rejected outcomes persisted; draft/action/decision/audit counts unchanged. [Restart](evals/results/I01.13-restart-http.json). |
| Local deployment | `infra/run-local-demo.sh` served built UI, health and authenticated pending route on loopback; all returned HTTP 200. |
| Actual Chrome UI | Two real local Qwen/borrowed-Fetch workflows: 500 kg approved in 234.38 s to review, 1,000 kg rejected in 246.07 s to review. Auth, progress, arithmetic, provenance, refresh, duplicate retries, failed request and narrow layout passed. [Browser report](docs/runs/I01.13-browser-verification.md). |

The I01.13 evidence includes two successful browser model workflows and a
separate successful HTTP model attempt after a timeout. These are different
checks and timing boundaries, not a reliability rate or independent scenarios.
Eight diverse model tasks, repeated runs, independently
prepared expected answers, practitioner review and fresh-clone reproduction
are still outstanding. The earlier browser-surface blocker was resolved with
local Playwright/Chrome; no independent UI reviewer is claimed. G0–G6 remain open.

The local API has no public TLS, rate limiting, production identity or
multi-worker recovery lock. Synthetic prices/capacity do not establish real
data rights, market freshness, buyer capacity or farmer benefit. The exact
organizer cutoff, final video publication and release decision remain unresolved.
The source repository is already public; the application is loopback-only.

## Browser evaluation summary — verified evidence, not the final suite

Source: [sanitized Chrome result](evals/results/I01.13-browser/result.json),
[inspection report](docs/runs/I01.13-browser-verification.md) and its six
screenshots, 12 October 2026. Test officer: `test:local-demo-officer`;
operator/reviewer: Fredrick, solo. This preparation reuses those results and
executes no new inference. Chrome 151.0.7922.137 / Playwright Core 1.64.0 used
actual loopback API, Qwen and borrowed public synthetic Fetch plus own MCP.

Model: `qwen3:4b-instruct-2507-q4_K_M`, digest
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
The implementation requests temperature 0 and context 4,096; see the
[workflow source](backend/app/agent/model_workflow.py). Hardware recorded in
[deployment evidence](infra/DEPLOYMENT.md): Ubuntu, i7-1165G7, 14 GiB RAM,
no NVIDIA GPU. Synthetic fixture snapshot SHA-256:
`01d764fe7226c8dd9d8cde68a70ccc5658b83876cbc6bed4c79078941396f9ef`.
All prices, costs, market names and capacity are invented; fixture as-of date
10 October 2026 is not a current market observation.

| Browser task / run ID | Expected synthetic result (KES) | Verified outcome | Measured time to review |
|---|---|---|---:|
| 500 kg / `demo-3f0883f4-bcaf-5fa0-9788-060942e08a91` | A: gross 20,000 − transport 2,000 = net 18,000; B: gross 22,500 − transport 8,000 = net 14,500. A leads by 3,500. | Rendered totals/provenance matched; exact-draft test-officer approval and duplicate decision yielded `approved_internal_review`. | 234.38 s |
| 1,000 kg / `demo-39400d45-480d-5876-843b-56680bac3be5` | A: gross 40,000 − transport 2,000 = net 38,000; B: gross 45,000 − transport 8,000 = net 37,000. A leads by 1,000. | Rendered totals/provenance matched; test-officer rejection and duplicate decision yielded `rejected`. | 246.07 s |

Both use zero loss, handling and fees as explicit assumptions and transport as
fixed scenario totals. Market B wins on gross, Market A on estimated net.
Expected values were derived from fixture arithmetic in the browser harness;
they were not independently prepared by a practitioner or second reviewer.
These are two quantity/decision variants of one fixture, not two diverse
field-validity tasks and not eight evaluated scenarios. Each variant has one
retained successful browser run; no three-repeat series was performed.

Invalid token produced expected 401; valid sign-in, RUNNING progress, refresh,
duplicate start (202), duplicate decisions, failed pending-fetch recovery and
390 px layout checks passed. The failed fetch was intentionally induced,
not a measured production outage. There were no browser page errors or
unexpected API failures. Three initial console errors were retained: intentional
401, intentionally aborted fetch and missing favicon; a separate post-fix page
load had zero console errors. Two earlier harness locator failures occurred
before model start; their short outputs were overwritten as disclosed in the
report. Do not count them as model failures or claim all harness attempts passed.

### Observed failure and next improvement

The HTTP attempt retained a `request_timeout` at 222.297 s; a later attempt
succeeded. Timeout reliability remains uncharacterized. More directly, both
measured browser times exceed 180 s **before human review**, so the current
workflow cannot support the planned unedited under-three-minute video based on
this evidence. Next: profile the measured phases and rehearse an authorized
improvement with actual wall time and tool visibility, or obtain official
format clarification. Do not substitute the faster 147.214 s HTTP result for
browser latency. No cold/warm split, throughput, resource peak, token usage,
manual baseline or income benefit was measured in these browser results.

### Missing evaluation and practitioner feedback

Eight-plus diverse actual-model tasks with frozen inputs/independent expected
answers, repeated runs, critical failure coverage, revision through the UI,
independent review and fresh-clone reproduction are outstanding. Completed-run
restart persistence is HTTP evidence, not browser crash-during-inference evidence.

No practitioner interview, consented feedback, named institution or independent
officer assessment is recorded. Obtain the office/cooperative and decision
owner; chosen crop, origin and three real candidate markets; grade/unit/basis
and freshness policy; realistic transport/handling/fees and sale capacity;
usefulness of comparison/provenance; approval/rejection/revision procedure;
acceptable latency; and a measured manual baseline if comparison is desired.
Confirm data permissions separately. Record consented notes with dates and
limitations, avoiding private farmer records. Test-officer approval is not
practitioner endorsement. All G0–G6 remain NOT_PASSED.


## Protected preview preparation — no new evaluation run

[Domain-free Quick Tunnel preparation](infra/QUICK_TUNNEL.md) verified official
cloudflared 2026.10.0 checksum/version/help and `--allowed-mail` support. Existing
API/model listeners were loopback-only, API health responded and anonymous
pending access returned 401. A separate synthetic test-officer verifier passed
schema validation; it is not practitioner authority. No tunnel or temporary
API configuration has started. Remote email login/denial, browser bearer
forwarding, latency, restart and shutdown are untested. These setup checks do
not add actual-model scenarios or change the retained browser timing results.


## One-hour test prerequisites — bounded software changes

Two new tests verify one active model workflow while polling and a real paused
draft review remain responsive, covering new and recovered starts, duplicate
retries/conflicts and release after failure. Five watchdog checks prove bounded
process termination while an unrelated process remains alive. These are
synthetic model/network checks, not new live-model evaluation scenarios.
Temporary loopback officer configuration has been activated: anonymous,
invalid and original credentials return 401, dedicated credentials 200 and
wrong scope 403; [actual local record](evals/results/I01.13-quick-demo-local-auth.json).
The authorized remote test's results will be recorded separately from these
local prerequisites. No phone login or remote workflow success is implied.


Final prelaunch regression after concurrency/SQLite changes: **154 passed in
171.73 s**; Ruff lint/format and frontend typecheck/build passed. An intermediate
full run had 153 passes and one second-start concurrency failure; fixed blocking
SQLite dispatch and reran. An earlier concurrent-review harness stall was fixed
by using one TestClient context/event loop, matching single-worker deployment.
These records do not erase the earlier failed/blocked checks. See the
[authorized test handoff](docs/handoffs/I01.13-one-hour-demo-A-2026-10-12.md).


## Authorized preview observations — evidence boundaries

Protected connector startup: 12 October 2026 15:04:54 EAT; planned hard expiry
16:04:44 EAT (3,590 seconds). Anonymous page/health/pending routes redirected
to login.trycloudflare.com without app content. A signed-out HTTP redirect
chain reached Cloudflare Access HTML with an email field. Mobile-user-agent
HTTP probes also redirected and set state cookies; they are not actual phone
browser tests. The owner reported “Bad request” on the tunnel hostname.
Later the owner confirmed email verification and reaching officer sign-in.
Officer access is owner-reported but remains uncorroborated by a stored decision.

One actual **loopback** 500 kg API/Qwen/borrowed-and-own-MCP check reached
PENDING_REVIEW in **249.488 s**; same fixture net results A 18,000 / B 14,500 KES.
Duplicate start returned the same workflow; one draft/action was stored and
no decision was made. This is neither remote phone success nor independent
practitioner review. [Run](evals/results/I01.13-one-hour-local-workflow.json),
[executed tool trace](evals/results/I01.13-one-hour-local-trace.jsonl),
[gate evidence](evals/results/I01.13-quick-demo-remote-gate.json).
The [expiry check](evals/results/I01.13-one-hour-expiry.json) recorded
connector exit at **16:04:44.232186 EAT**, absent PID/metrics, remote HTTP
**502** without app content, and local API/model readiness at 16:04:46 EAT.
A [later recheck](evals/results/I01.13-one-hour-post-expiry-recheck.json)
at 22:40 EAT found no connector, an unresolved expired hostname and closed
local API/model ports. Continued local service uptime is not established.


Phone follow-up: the owner confirmed successful email verification using the
fresh root-query entry and then saw officer sign-in. This is owner-reported
phone evidence; no agent screenshot/login interception. Invalid/valid officer
and exact-draft decision results remain pending until actually observed.


## Integrated recovery review — 12 October 2026

Full backend regression: **155 passed in 112.52 s**; frontend typecheck/build
and Ruff check/format passed. New atomic admission rejects distinct overlapping
starts (409, no row); identical retries reuse the stored run. Failed runs release
admission; older accepted RUNNING rows recover through one model slot.
Responsive polling/review, idempotency and connector-only expiry remain tested.
Stale review errors preserve pending run state rather than prematurely completing
it. [Recovery/integration handoff](docs/handoffs/I01.13-local-recovery-video-A-2026-10-12.md).
Host journal establishes later power-off, not tunnel-induced service shutdown.
Loopback API/model and exact pending draft restored with no decision.
