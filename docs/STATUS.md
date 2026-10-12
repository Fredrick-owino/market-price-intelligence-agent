# Project status — update from execution evidence

Last evidence update: 12 October 2026 (I01.13 local preparation addendum). Synthetic
local demo implementation and HTTP evidence are recorded on main; release gates
remain open.

- stage: LOCAL_SYNTHETIC_DEMO
- implementation_start_confirmed: true
- official_window_start: 2026-10-09
- official_window_start_time_and_timezone: UNCONFIRMED
- official_window_end: UNCONFIRMED
- published_deadline_date: 2026-10-15
- cutoff_time_and_timezone: UNCONFIRMED
- official_evidence_reference: Lead-reported organiser confirmation supplied in the P02.1 user prompt, dated 2026-10-09; see [P02.1 handoff](handoffs/P02.1-A-2026-10-09.md). Original organiser message not independently inspected.
- person_A: Fredrick Onyango — Git identity configured (name and email)
- active_contributor: Fredrick Onyango — temporarily owns both workstreams
- person_B: colleague — GitHub username ianmuriuki; actual name remains unconfirmed
- colleague_participation: UNCONFIRMED
- colleague_invitation_acceptance: UNCONFIRMED
- colleague_clone: UNCONFIRMED
- person_A_P00_audit: COMPLETED — driver-confirmed in P05.2 prompt
- person_B_P00_audit: OUTSTANDING — completion unconfirmed
- docker_server: 29.8.2 — verified in ordinary Ubuntu terminal per driver; access inside Codex previously failed
- daily_available_hours_A: UNKNOWN
- daily_available_hours_B: UNKNOWN
- overlap_time: UNKNOWN
- repository_local: Dedicated project repository initialized on main at /home/fred/Projects/market-intelligence-challenge
- repository_remote: https://github.com/Fredrick-owino/market-price-intelligence-agent.git (origin)
- repository_visibility: PUBLIC — Fredrick changed it manually on 12 October 2026; unauthenticated GitHub API and raw README both returned HTTP 200. Historical KAMIS redistribution rights remain unresolved.
- initial_preparation_commit: bce05d079ebb88d77d1e55d3a797a37de1487668 — pushed and remote main verified in P04.2; main tracks origin/main
- P05.1_driver_review: REVIEWED — ignore/licence preparation, confirmed in P05.2 prompt
- team_licence_review: PENDING — proposed MIT for original work only
- target_institution_and_reviewer: NOT_CONFIRMED
- crop_origin_and_three_markets: NOT_CONFIRMED
- data_access_and_redistribution_rights: NOT_VERIFIED
- runtime_model_and_dependency_versions: PINNED_LOCAL_DEMO — see I01.11 and I01.13 reports; broader reliability not benchmarked
- current_task: I01.13 integrated request/frontend/local demo verification
- next_task_after_P00: P01 team capacity/roles

| Gate | Status | Evidence needed |
|---|---|---|
| G0 readiness/calendar | NOT_PASSED | Both environment audits, roles, repository setup, official window/cutoff evidence |
| G1 scope/data/contracts | NOT_PASSED | Practitioner scope, comparable permitted records, signed contract |
| G2 vertical slice | NOT_PASSED | Actual open-weights/model/MCP/pause-resume runs and calculation tests |
| G3 complete workflow | NOT_PASSED | Real API/interface approval, rejection, revision, restart evidence |
| G4 reliability | NOT_PASSED | Eight-plus evals, repeats, invariant tests and limitations |
| G5 reproducibility | NOT_PASSED | Fresh-clone one-command run, licence and document review |
| G6 submission | NOT_PASSED | Public artifacts, verified form submission, receipt, commit freeze |

Record task evidence under docs/handoffs/ and sanitized durable run evidence under evals/results/. No empty file or placeholder qualifies as a completed deliverable.

## I01.13 — integrated local synthetic demo

The [I01.13 report](runs/I01.13-demo-integration.md) and
[handoff](handoffs/I01.13-A-2026-10-12.md) record a running API, built frontend,
actual public synthetic borrowed fetch, actual local Qwen workflow, HTTP test
officer approval, separate HTTP rejection, and restart persistence. Backend
regression: 147 passed; frontend typecheck/build passed. The first live HTTP
attempt timed out and remains retained. Browser UI interaction was subsequently
verified in the Chrome addendum below. Independent
officer/practitioner review, real data, public deployment and all G0–G6 gates
remain outstanding.

### Public repository visibility addendum — 12 October 2026

Fredrick reported manually changing the original repository to public. An
unauthenticated GitHub repository API response returned HTTP 200 with
`private: false` and `visibility: public`; anonymous raw `main/README.md`
also returned HTTP 200. See the [verification record](runs/I01.13-public-visibility.md).
Earlier statements that this repository was private describe its state when
written. No history was rewritten or visibility changed by Codex.
The application still uses only the labelled project-authored synthetic
fixture; historical KAMIS redistribution rights remain unresolved. The API
remains bound to loopback, and no release gate is marked complete.

### Chrome browser verification addendum — 12 October 2026

The [actual Chrome report](runs/I01.13-browser-verification.md) records two
browser-driven local Qwen/borrowed-Fetch synthetic workflows (500 kg approved,
1,000 kg rejected), invalid/valid authentication, progress, comparison and
provenance, refresh, duplicate retries, a failed request, and desktop/narrow
screenshots. Playwright used an isolated profile and ignored test credential.
The visible comparison matched fixture-derived arithmetic; higher gross at
Market B became lower net after transport in both cases. Measured pre-review
times were 234.38 s and 246.07 s. This supersedes the earlier statement that
browser interaction was unavailable. Fredrick's review remains solo; G0–G6
stay NOT_PASSED.

### Controlled HTTPS preparation — 12 October 2026

Fredrick selected the existing Ubuntu machine with Cloudflare Tunnel and Access
for a future controlled HTTPS demonstration. The
[prepared configuration and account requirements](../infra/DEPLOYMENT.md)
do not enable a route or expose the API. Exact domain/account control, named
viewer identities, demo window and spending limit remain owner inputs. No
hosting or public-exposure gate is passed.

## I01.12 — local authenticated review evidence

The [I01.12 report](runs/I01.12-review-api.md) and
[handoff](handoffs/I01.12-A-2026-10-12.md) record the bounded review API, 142
passing backend tests and an actual loopback HTTP review/resume check against a
pending synthetic workflow. Authentication uses ignored local configuration and
is not production identity assurance. Fredrick performed solo review; no
independent officer or peer validation is implied. G0–G6 stay NOT_PASSED.

P05.2 evidence: [preparation handoff](handoffs/P05.2-A-2026-10-07.md).
The driver supplied the P00 completion, ordinary-terminal Docker verification and
P05.1 review facts on 7 October 2026. Raw P00/terminal outputs are not present in
this repository; P05.2 does not claim to have rerun them or completed peer review.
The published deadline above is retained from the planning pack, not newly
verified official evidence; the build-start date is now recorded below, while
exact start time/timezone, end date/time and cutoff timezone remain unconfirmed.
Earlier planning-pack and P05.1 statements describe their original preparation
state; this status records the supplied updates.

Temporary arrangement recorded at the user's direction: Fredrick may continue
independently on permitted work in both workstreams. Colleague participation
or review is not implied, and no peer-review gate is passed by solo work.
Colleague onboarding resumes when ianmuriuki becomes available, including
confirmation of participation, invitation acceptance, clone and audit.
The build-start date is confirmed as described below; independent task
prerequisites and gates still govern implementation readiness.
P04.2 execution verified that the initial preparation commit above matched
remote main after the push; this does not establish colleague access or review.

Decisions pending: colleague details; both contributors' availability and overlap; team licence review; exact crop/market coverage; allowed dataset/snapshots; inference hardware; validated open-weights model; compatible MCP adapter/library set; officer identity mechanism; fresh-price threshold; bounded live retrieval; deadline/window clarification.

## P02.1 — build-start confirmation and readiness

On 9 October 2026, project lead Fredrick stated:

> “Organizers have confirmed that the build starts today at 9th”

Source: the dated lead statement supplied in the P02.1 user prompt. This is
**lead-reported organiser confirmation**, not independent inspection of the
organiser's message. At the lead's explicit direction, this records
`official_window_start: 2026-10-09` and `implementation_start_confirmed: true`.
The flag confirms the build-window start only; it does not pass I00, G0, G1 or
any other task or gate. Stage remains PREPARATION because no implementation is
verified. Exact start time/timezone, end date/time and cutoff timezone remain
unconfirmed; the retained published deadline is not an inferred cutoff.

P02.1 superseded earlier false/disabled calendar wording in preparation
records. P11.1 now aligns COLLABORATION.md and defines the limited foundation
entry path below; ownership and independent review requirements still apply.

Evidence already present: driver-confirmed Person A P00/Docker facts, named
lead and temporary solo ownership, Git repository/remote and documentation
commits, ignore rules/proposed MIT licence, and the bounded P08 source audit.
These are partial prerequisite evidence, not completed peer-reviewed tasks.

**Historical P02.1 conclusion before the P11.1 sequencing change:** no
implementation task was dependency-ready under the original ordering.
I00 requires P02, P04 and P11 plus preparation/eligibility evidence and two-person
signoff. P02 still lacks eligibility/form and remaining calendar evidence;
P04 lacks colleague access/clone/audit evidence; P11 depends on unresolved
P06–P10 scope, practitioner, data-rights/comparability, independent examples
and reviewed contract decisions. I01 requires I00 and P00. Its runtime/model
benchmarking is future I01 work, not evidence already obtained.

The [P02.1 handoff](handoffs/P02.1-A-2026-10-09.md) maps specific missing facts
and owners. Next independent preparation can collect the outstanding P02
calendar/eligibility facts and colleague P00 evidence; no such task is executed
here. No colleague onboarding, practitioner validation, data permission or
peer review is implied, and all gates above remain NOT_PASSED.

## P11.1 — phased readiness

[ADR 0002](adr/0002-phased-implementation-readiness.md) supersedes only the
blanket P02.1 start-order restriction. Confirmed start, Fredrick's recorded
machine/repository evidence, temporary solo ownership and defined experiment
scope/contracts permit bounded foundation work on labelled synthetic fixtures.
This includes toolchain/model/real-MCP, deterministic calculation and private
checkpoint/recovery experiments. Stage remains PREPARATION until actual
execution evidence is recorded; no experiment has run in this task.

**First dependency-ready subtask: I01.1**, read-only toolchain readiness checks
and the two reports specified in ADR 0002. No missing software is established
from retained evidence; versions/runtime/model availability need checking.
The earlier Docker access error must be distinguished from missing software.

Real-data integration still needs permission, provenance, normalization and
comparability evidence; field-validity claims need practitioner validation.
I00 and all original full-task/gate acceptance requirements remain incomplete.
Release still requires evaluation, independent review, reproducibility, access,
calendar/eligibility and submission evidence. Solo execution is not peer review.
The ADR lists unresolved facts with owners; [P11.1 handoff](handoffs/P11.1-A-2026-10-09.md)
records this documentation task. No next task is executed here.

## Standing sole-contributor arrangement — 11 October 2026

Source: Fredrick’s explicit I01.9 ownership clarification in the task conversation.
Fredrick is the sole active contributor and owns both Person A and Person B
workstreams, including all existing uncommitted I01.9 changes. No other Codex
session is editing this project. Continue those changes without asking again
about ownership unless new evidence indicates another contributor or concurrent
editing. Use isolated task branches, appropriate checks and accurate handoffs.
Attribute reviews as solo reviews; they are not independent peer review. This
arrangement does not complete any project gate. Earlier collaboration and status
records remain historical; this standing arrangement supersedes their temporary
ownership wording for ongoing work.

## I01.9 — bounded synthetic execution evidence (11 October 2026)

The [I01.9 report](runs/I01.9-model-workflow.md) records an actual local
qwen3:4b-instruct-2507-q4_K_M run selecting three own MCP tools, saving a
private synthetic draft, pausing, and resuming after a separate simulated review.
Earlier preparation/runtime status statements above are historical, not claims
about this new run. This evidence does not change any gate status, establish
independent peer review, complete I01, or authorize live data/release. See the
[handoff](handoffs/I01.9-A-2026-10-11.md) for checks, publication and limitations.

## I01.10 — public-fixture prerequisite blocked (2026-10-11)

[Actual prerequisite probes and source review](runs/I01.10-borrowed-fetch.md)
found the repository PRIVATE and the required unauthenticated commit-pinned
synthetic fixture returning 404. No public fixture hash match, borrowed-MCP
runtime, implemented destination control or new retrieval test is established.
Fetch 2026.8.18 requires an isolated MCP-1.x environment; no application SDK
change was made. Owner: Fredrick; solo review. Continue the same bounded task
after the public-fixture prerequisite is resolved. All gates remain unchanged.

## I01.10 — synthetic public fixture and real borrowed retrieval (2026-10-11)

The [resumed execution](runs/I01.10-borrowed-fetch-execution.md) resolves the
previous fixture-access blocker using the authorized fresh public repository
`Fredrick-owino/sokosignal-demo-fixtures`. Anonymous HTTP 200 and exact original
fixture hash were verified. A real MCP 2.3.0 client called isolated Fetch
2026.8.18 / MCP 1.30.0 through fixed URL, DNS/connection, redirect, size and
content-integrity controls. Full actual input/output and provenance are retained.
Review: Fredrick, solo. The original repository remains PRIVATE because its
historical KAMIS rights blocker is unchanged. Model integration, independent
review and all gate acceptance remain outstanding; no gate is marked complete.

## I01.11 — integrated synthetic workflow (2026-10-11)

[Execution report](runs/I01.11-integrated-workflow.md) and
[handoff](handoffs/I01.11-A-2026-10-11.md): actual public borrowed Fetch plus
pinned local Qwen selected all three own MCP tools, saved a provenance-bound
private draft, paused, and resumed after a stored exact-hash simulated decision.
136 regression tests passed. Initial model-unavailable attempt is retained.
Pre-review time 282.448s exceeds the demo target; authentication, broader
reliability and independent review remain open. Fredrick owns both workstreams;
review is solo. No gate status, publication visibility or real-data rights changed.

## I01.13 — local video/submission preparation, 12 October 2026

Source: Fredrick's task conversation reports no domain and requests preparation
without enabling remote access. Prepared [video script](demo-script.md),
[submission checklist and missing answers](SUBMISSION_CHECKLIST.md),
[browser evaluation summary](../EVALS.md) and
[Ubuntu operations guide](../infra/LOCAL_OPERATIONS.md). The
[preparation handoff](handoffs/I01.13-preparation-A-2026-10-12.md) records checks.
These documents reuse verified Chrome results; no new model run, rehearsal,
service restart, deployment or submission is implied. Measured browser times
234.38/246.07 s exceed the planned short-video duration before human review.
Practitioner/institution feedback and actual form answers remain missing.
Remote access stays disabled, credentials stay private, and G0–G6 stay NOT_PASSED.


## I01.13 — protected Quick Tunnel preparation, 12 October 2026

The owner requests domain-free, email-restricted preparation and explicitly
prohibits tunnel launch pending specific authorization. Current official
[Quick Tunnel documentation](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
and official binary help support `--allowed-mail`. Installed the checksum-verified
2026.10.0 standalone binary in ignored project-local cache. Prepared one exact
owner-email rule outside Git, a blank private tunnel config and dedicated
synthetic demo officer credential files. Existing local configuration is intact.
Current API/Ollama listeners were verified loopback-only; API health, pinned
model metadata and anonymous-access rejection checked. No tunnel or new API
configuration started. See [command/operations](../infra/QUICK_TUNNEL.md) and
[handoff](handoffs/I01.13-quick-tunnel-A-2026-10-12.md).

No domain is required for this temporary option. The generated URL will change
on connector restart; remote authentication/availability/recovery remain
unverified. Script, checklist and EVALS continue to label synthetic data and
measured local latency, with practitioner/form answers missing. G0–G6 remain
NOT_PASSED; readiness is prepared CLI/local prerequisites, not verified exposure.


## I01.13 — owner-authorized one-hour test prerequisites

Owner explicitly authorizes one exact-email restricted remote test for at most
3,600 seconds, after software concurrency/local auth/tests/commit/push. Added
one active model-workflow slot per single-worker API process and bounded
connector watchdog (3,590 seconds with safety margin); no app/model shutdown
on expiry. Temporary verifier/database activated and local unauthorized/scope
checks passed, original state/config preserved. The
[execution handoff](handoffs/I01.13-one-hour-demo-A-2026-10-12.md) distinguishes
prelaunch checks from actual exposure/login/workflow/expiry evidence. All gates
remain NOT_PASSED; the prior no-launch wording describes preparation history.


### I01.13 — authorized test expiry evidence, 12 October 2026

The protected one-address test started at 15:04:54.200817 EAT and automatically
stopped at 16:04:44.232186 EAT (Africa/Nairobi), within 3,600 seconds.
[Expiry evidence](../evals/results/I01.13-one-hour-expiry.json) records absent
connector/metrics, remote HTTP 502 without application content, and local
API/model readiness immediately afterwards. Anonymous visitors were redirected
to the email gate. The owner reported email verification and officer sign-in;
remote officer completion remains unverified. One actual loopback synthetic
Qwen/MCP workflow reached pending review in 249.488 s; zero decisions stored.
A [later host recheck](../evals/results/I01.13-one-hour-post-expiry-recheck.json)
found no connector, unresolved expired hostname and closed API/model ports.
Services were running at expiry; continued uptime cannot be claimed.
No second launch, audience expansion or public deployment occurred in this
closeout. Review remains solo and all G0–G6 remain NOT_PASSED. Next bounded
work: preserve/recover local pending review using the same private state and
verifier, then collect missing practitioner/form and reliability evidence.


### I01.13 — local service recovery and integration review

Host power-off at 19:19:27 EAT and boot at 21:07:23 establish later host
lifecycle as the service-loss explanation; the tunnel expired hours earlier
with local services healthy. Restored API/model to loopback with existing
pinned environment/model and dedicated private configuration. Original exact
pending draft/checkpoint and zero decisions preserved. New distinct overlapping
starts now reject atomically; retries and older recovery backlog remain safe.
Full backend 155 passed; frontend type/build and Ruff passed.
[Current handoff](handoffs/I01.13-local-recovery-video-A-2026-10-12.md) records
merge/video/checklist continuation. No tunnel, upload or submission authorized;
all release gates remain open and solo review is not independent review.


### I01.13 — integrated main and local edited video closeout

Main fast-forward integration `7432273f274ff10d8344191c9bd2d2469685a2c3`
was pushed/remote-verified. Local recording first failed because the system-path
Ollama lacked its runner despite metadata health; existing complete pinned
user-local runtime restored actual generation with no weight download.
Second actual Chrome/Qwen/borrowed-and-own-MCP run reached pending review in
220.794 s. Final local video is 110.0 s, with waiting shortened, measured
latency visible and labelled post-run inspection of comparison/provenance.
No approval, upload, submission or new tunnel. Original pending draft and
checkpoint rows/configuration preserved; both local services loopback/ready.
Checklist/field-answer/English-description drafts now list only outstanding
practitioner, evaluation/independent-review, reproducibility/rights, official
calendar/form/eligibility and qualifying durable-link requirements. The edited
video is not the retained unedited competition artifact. No gate completed.


### I01.13 qualifying-demo continuation — 12–13 October 2026

Owner clarified Agriculture requires continuous unedited video under 180 s
with actual tools visible; the 110 s edited file is supplementary only.
Isolated branch/worktree protects the original running demo and two pending
drafts. Baseline model bottleneck profiled; compact context/explicit schema
retains exact validation, full stored evidence and real model-selected tools.
Two final-schema actual rehearsals: 138.603/138.577 s, demo approval.
A nested-summary failure remains in evidence. Live sanitized tool UI and
backend-derived demo reviewer label added. Full regression 157 passed,
frontend type/build and Ruff passed. EVALS now records 10 distinct tasks
(9 pass/1 unresolved request-changes failure), distinguishing real model
and deterministic/mocked cases. No gate, practitioner or independent review
completion implied. Native recording and fresh setup results follow actual
verification; no new exposure or upload.


### I01.13 qualifying video and fresh setup evidence — 13 October 2026

Final continuous native 650 kg video **158.12 s** with actual Fetch and
model-selected own tools on screen, comparison, private draft and authenticated
labelled demo approval. No cuts/compression/substituted footage; private
pre-auth content concealed. Earlier 159.68 s native attempt retained for brief
save-event visibility; edited 110 s file is supplementary only. No upload.

Fresh remote clone of 88b25a0: documented make demo installed locked envs,
built UI, generated new 0600 credentials and separate state; real 900 kg
Qwen/borrowed/own-MCP task and internal demo approval passed, 129.541 s to
review. Same host/cache/model service reused, not independent peer review.
Only temporary fresh API stopped. Original API/model ready; two original
exact pending drafts/config unchanged, zero decisions, no connector.
EVALS records 10 distinct tasks, 9 pass/1 unresolved request-changes failure.
Independent review, named practitioner/institution, rights/licences, exact
official cutoff/eligibility/form, public video playback and final submission
remain open. No release gate completed from solo verification.
