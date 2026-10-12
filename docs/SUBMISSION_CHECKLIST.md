# Submission and review checklist

Release checklist; evidence snapshot updated 12 October 2026. Local integration and edited video
preparation do not complete the broader release requirements. Fredrick currently
owns both workstreams; his review is solo. A/B independence below remains a
release requirement, not evidence of an available second reviewer. Rules verified
by the team override proposals. Record exact evidence and reviewer initials
beside each completed item. No check is complete merely because a document exists.

## Rules before evaluated implementation

- [ ] Both members meet age/residency rules; final team size and single-project rule checked.
- [ ] Confirm official implementation dates, cutoff time/timezone and allowed pre-window preparation with dated source evidence. Resolve five/seven-day ambiguity; do not guess.
- [ ] Inspect actual application form fields in the team’s signed-in session; distinguish entry/registration from final submission if applicable.
- [ ] Confirm all evaluated implementation is new and within the permitted window; upstream dependencies attributed.
- [ ] Institution/workflow and data permissions recorded; officer approval requirement applied.

## Function and engineering evidence

- [ ] Full task runs on selected open-weights model; model digest/licence and settings recorded.
- [ ] Open-source orchestration actually used; pinned libraries and upstream licences verified.
- [x] Own MCP server exposes three distinct tools including private-draft action; actual synthetic inputs/outputs retained in [model/MCP evidence](../evals/results/I01.13-one-hour-local-trace.jsonl). Official action-rule interpretation remains to be confirmed.
- [x] Borrowed Fetch MCP actually retrieves the permitted public synthetic fixture; [version/provenance/rationale](runs/I01.11-integrated-workflow.md) and actual traces retained.
- [ ] Logs contain actual tool/action inputs, outputs and timestamps, with secrets/private records excluded from public artifacts.
- [ ] Named officer approval enforced server-side; pending, reject, changes requested, revised version, unauthorized decision and restart checks pass.
- [x] Advice remains a private review draft; no household delivery, order or credit flag exists. The preserved owner-test draft remains pending; no automatic approval.
- [ ] Arithmetic, units, freshness, comparable grades/basis and absent-data behavior verified independently.
- [ ] Eight or more actual-model tasks recorded honestly; critical gates pass; at least one observed unresolved failure and next step documented as required.

## Repository and reproducibility

- [ ] Public repo accessible while signed out; no leaked credentials, private identities, restricted datasets, weights or local state.
- [ ] OSI-approved licence for original work; separate upstream/data/model licences and notices preserved.
- [x] Root and isolated Fetch lockfiles and frontend package lock are committed; integrated backend/frontend checks passed. Fresh-clone verification remains separate and open.
- [ ] README says prerequisites, hardware/RAM/VRAM, ports, env setup without secrets, initial model/network download requirements, exact one-command launch, example workflow, stop/reset behavior and troubleshooting.
- [ ] B runs a fresh clone using that README without A silently repairing it; command/output and commit recorded.
- [ ] Real-model run includes both MCP servers. Offline/replay limitations clearly labelled.
- [ ] Final tests/build/integration/eval evidence corresponds to the final reviewed SHA; later changes trigger affected checks.

## Documents, video and form

- [ ] English ~300-word description names Agriculture/theme, specific institution, problem, complete workflow, human role and observed evidence; no unsupported impact claims.
- [ ] One-page `ARCHITECTURE.md` matches actual system; check page rendering/export if supplying a page artifact.
- [ ] `EVALS.md` contains actual task results and limitations, not the planned suite alone.
- [ ] Public YouTube/Vimeo video is under three minutes; unedited agent run, real tool visibility, pending state and named approval visible; no keys or private records on screen.
- [ ] Rehearse the run before recording; time it on actual demo hardware. If it exceeds the limit, optimize/reduce scope rather than cut away tool execution or accelerate and misrepresent wall time.
- [ ] Verify public video, repository and any supplied document links while signed out. Confirm uploaded video processing is complete and access is public.
- [ ] Inspect every actual form field; complete final answers using verified artifacts and the right team/project links.
- [ ] A submits before verified cutoff with B reviewing; retain actual receipt, submission timestamp/timezone and submitted links. This chat has not submitted anything.

## Freeze and live review

- [ ] Record final SHA and optional tag before submission; retain local release evidence.
- [ ] Tell both members the freeze starts; no post-deadline commits to judged repo under published rule, pending explicit clarification.
- [ ] Each person rehearses the ten-minute code walkthrough: source normalization, deterministic calculation, graph/tool loop, MCP calls, protected decision and evaluation.
- [ ] Rehearse the full 20-minute review and a new small requirement. Practice examples: add a fee basis, change freshness policy, show a cost sensitivity. These are exercises, not predictions of the judges’ request.
- [ ] Each person can explain their own and the other person’s code without relying on Codex’s claims.
- [ ] Prepare a separate local clone for live changes after cutoff; do not push it to the judged repository unless organizers explicitly authorize that path.

Release record fields: repository URL, exact SHA, tag, data hash, model digest, verified environment, README command, actual test/eval artifacts, video URL/duration, description, form receipt, freeze timestamp, A signoff, B signoff, unresolved limitations.

## Current evidence snapshot — I01.13 preparation

This section distinguishes retained verification from release completion.
The full checklist above stays open where its broader acceptance is unfulfilled.

| Item | Evidence now available | Remaining requirement |
|---|---|---|
| Public source repository | Fredrick's manual visibility change; anonymous API/raw README HTTP 200, [record](runs/I01.13-public-visibility.md). | Final SHA, final signed-out review, history/rights/licence review and release signoff. |
| Actual model and MCP workflow | Two browser workflows with Qwen, borrowed Fetch and own tools; [report](runs/I01.13-browser-verification.md). | Diverse/repeated evaluations and independent technical review. |
| Comparison and review UI | Synthetic 500 kg approval / 1,000 kg rejection; auth, provenance, refresh, retries and narrow layout verified. | Practitioner/named officer validation; changes-requested/revision UI and full gate evidence. |
| Automated checks | Integrated 155 backend passes (112.52 s), frontend typecheck/build and Ruff; [summary](../EVALS.md). | Final reviewed SHA and reproducibility; these are not eight actual-model tasks. |
| Video | Local **110 s** edited captioned recording, actual new browser latency **220.794 s**, live MCP evidence and labelled post-run inspection; [record](../evals/results/I01.13-local-video.json). | Edited local capture with measured latency is authorized. Qualifying uninterrupted recording or official edited-format clarification, named human decision, public URL and playback verification remain open; browser latency exceeds 180 s before review. |
| Local Ubuntu operation | [Restart, concurrency and shutdown instructions](../infra/LOCAL_OPERATIONS.md) verified after host power-off; original dedicated pending draft preserved, pinned actual inference passed. | Operator rehearsal as needed; no inference-time shutdown or backup/restore trial claimed. |
| Remote access/domain | Owner reports no domain; application remains loopback-only. | No remote setup is authorized in this task. The prior restricted tunnel expired; no new tunnel is authorized. Domain absence does not block local recording. |

## Missing submission answers — owner and official form inputs

The actual final submission form has not been inspected in this task. These
are preparation fields from project requirements, not an invented form schema.
Fredrick should supply/verify answers against the real form; do not enter
placeholders as confirmed facts.

| Answer/artifact | Safe prepared content | Missing answer or verification |
|---|---|---|
| Project/theme | SokoSignal; Agriculture; synthetic market comparison and internal review. | Confirm exact form theme/category and final project title. |
| Team and eligibility | Fredrick is sole active contributor; historical colleague records remain historical. | Permitted final team size; entrant details and age/residency eligibility; colleague participation if required. Keep private form data out of Git. |
| Institution and use case | Proposed extension-office/cooperative review workflow. | Exact named institution, practitioner/decision owner, selected origin/crop/markets and consented feedback. Do not invent a partner. |
| Description (~300 English words) | Actual retrieval → deterministic comparison → private draft → exact-hash officer decision; all inputs labelled synthetic. | Final institution-specific text, counted/reviewed against actual evidence; no farmer-impact claim. |
| Technology/reuse | Local pinned Qwen, LangGraph, three own MCP tools, isolated borrowed Fetch; [architecture](../ARCHITECTURE.md). | Final model/dataset hashes and upstream/data/model licence review; confirm private draft action meets official rule. |
| Evaluation | Two browser variants, measured 234.38/246.07 s, retained HTTP timeout; [EVALS](../EVALS.md). | Eight-plus actual tasks, independently derived expectations, repeat denominators, manual baseline only if observed. |
| Repository | `https://github.com/Fredrick-owino/market-price-intelligence-agent` is public. | Final exact commit/tag, source/history rights audit, independent fresh-clone result and one-command requirement (no `make demo` exists). |
| Video | Local edited recording, shortened waiting explicitly disclosed, English captions; no remote hostname needed. | Qualifying public YouTube/Vimeo URL, actual duration, signed-out playback and secret review. |
| Calendar/rules | Lead-reported build start 9 October; planning pack lists 15 October deadline. | Official exact cutoff time/timezone, eligibility/form requirements and post-deadline instructions with dated source. |
| Submission/freeze | No submission performed. | Final signed-in form answers, link review, receipt, actual timestamp/timezone, frozen SHA and required signoff. |
| Deployment URL, if asked | Local-only Ubuntu demonstration; no domain and no remote application URL. | Verify whether the actual form requires a hosted app; do not present loopback or GitHub as a remotely usable application. |

Practitioner feedback remains absent: useful crop/markets and quantity; realistic
costs and capacity; units/grades/freshness; clarity of evidence and net ranking;
review authority/revision workflow; acceptable latency and observed manual
baseline. The synthetic test identity is not an interview or endorsement.
All release gates stay NOT_PASSED. Do not upload, publish or submit from this
preparation alone.


## Temporary preview addendum — prepared, not public submission evidence

- [x] Owner authorized the exact email-restricted, port-8000
  [Quick Tunnel command](../infra/QUICK_TUNNEL.md) and bounded demo window.
- [ ] After launch, protected-mode startup and allowed/denied email access are
  verified; officer authentication, one-workflow policy and recovery pass.
- [x] The actual temporary hostname, availability window and teardown outcome
  are retained privately. Do not put the allowlist, credentials or PINs in Git.
- [ ] Any form requesting a deployment URL is inspected for public-access and
  durability requirements. The initial owner-only preview cannot demonstrate
  judge access; its URL changes after connector restart and is not durable.
- [ ] Public repository/video links are independently checked. No temporary
  hostname substitutes for the missing qualifying public video, final form
  answers, practitioner validation, final SHA or receipt.

No domain was needed for this preview. The subsequent one-hour test expired;
see the [execution handoff](handoffs/I01.13-one-hour-demo-A-2026-10-12.md).
Measured latency remains unchanged.


A [provisional English description](submission-description-draft.md) now uses
measured synthetic evidence and explicitly leaves the named institution and
practitioner unconfirmed. It is a preparation draft, not a submitted answer.
The phone test initially reported “Bad request”, then owner-confirmed email
verification and officer sign-in. No stored remote officer decision or remote
model run was verified; signed-out HTTP and loopback inference have separate
evidence boundaries.


Use the [practitioner feedback preparation](practitioner-feedback-preparation.md)
to collect the missing institution, workflow, data, cost and latency answers.
It contains questions only; no interview or endorsement has occurred.


## Final preparation answers and remaining concrete requirements

Prepared [field answers](submission-answers-draft.md) and
[English description](submission-description-draft.md) use actual evidence,
with unknown fields clearly marked. Inspect the real final form before mapping
these answers; no receipt or submission exists.

| Requirement | Concrete outstanding evidence |
|---|---|
| Practitioner/institution | Named consented extension office/cooperative and decision owner; selected crop/grade/origin/three markets; realistic prices, costs, capacity, freshness and units; usefulness/latency feedback. |
| Evaluation/review | Eight diverse actual-model tasks with independently derived expected results and honest repeat counts; independent technical/officer review; revision UI/gate evidence. Two prior browser quantities and new recording attempts are not eight distinct tasks. |
| Reproducibility/rights | Independent fresh-clone one-command trial; final upstream/model/data/history-rights review, including unresolved historical KAMIS redistribution. |
| Deadline/eligibility/form | Dated official end-window and exact cutoff time/timezone, freeze instructions, permitted entrant/team eligibility, actual final form fields and required signoff. Planning-pack 15 October is not a confirmed cutoff. |
| Qualifying video/link | Local edited video deliberately shortens waiting and performs no human approval. It needs official format acceptance or a new qualifying uninterrupted run with named review; then separately authorized public upload, processing and signed-out playback. |
| Durable application link if required | Inspect form hosting requirement; no durable public app URL exists. Expired owner-only Quick Tunnel is not judge access or a submission link. No new exposure authorized. |
| Submission/freeze | Final verified answers/links and authorized signed-in submission, retained receipt/timezone and frozen SHA. |

Local browser/model/MCP success and synthetic approval/rejection are supported
by actual local records. Phone email verification is owner-reported; remote
officer completion remains unverified, with zero stored remote decisions.
This checklist is complete as a preparation inventory; incomplete release
requirements are intentionally left unchecked.


Local recording acceptance for this authorized task: duration 110.0 s <180 s;
actual request-to-review 220.794 s explicitly disclosed; credentials/PINs
excluded; comparison and exact pending draft visible; no decision/upload.
The final local readiness check confirms 200 health/authorized draft, 401
unauthorized access, loopback-only app/model and unchanged original draft,
checkpoint rows and private configuration. [Readiness](../evals/results/I01.13-final-local-readiness.json).
