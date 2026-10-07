# Ordered two-person task board

Status: every task is initially NOT STARTED. This is a checklist, not execution evidence. A = backend/release lead; B = data/UI/evaluation lead. Actual names are recorded in STATUS. Dependencies are prerequisites, not calendar promises. Tasks with ready dependencies can proceed in parallel in separate checkouts. A failed critical gate blocks dependent implementation/release, while permitted independent preparation can continue.

Each task has the following micro-steps: (1) confirm prerequisites and official implementation permission; (2) agree lead, reviewer, branch and allowed files; (3) read relevant contracts and preserve existing changes; (4) have driver issue one bounded Codex prompt; (5) implement only this task, or audit only if read-only; (6) inspect the diff and run appropriate checks; (7) record actual evidence in a uniquely named handoff; (8) obtain peer review; (9) merge reviewed changes, rerun affected integration checks, update STATUS and board via the assigned editor; (10) return the report to the driver for the next task. No automatic commit/push, next-task execution or completion claim is authorized merely by this board. Follow the precise local task prompt.

Do not tick a box for an expected result. For every completion record date, branch/commit, report path, actual command results and reviewer. A blocked task stays unchecked with a blocker owner and next action. If a task proves too large, the driver splits it into numbered substeps within that ID; none of its acceptance checks may be dropped.

## Suggested parallel scheduling

| Point | A | B |
|---|---|---|
| After audit | Repository/rules preparation | Practitioner/source investigation |
| After I01 | Calculations/persistence/MCP | Data importer/expected results/frontend shell |
| After typed API | Agent/gate/recovery fixes | Real UI integration and evaluations |
| Release | Packaging/checks/freeze | Fresh clone/docs/video |

Shared contracts, root lockfiles and STATUS have one designated editor. P05 intentionally precedes P04 so the remote starts with reviewed ignore/licence/docs. R10 intentionally precedes R09 so the submission points at the already recorded final revision.

## P00 — Read-only environment audit

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: None.
- Ordered work: Open this new folder in each person’s installed Codex; read AGENTS.md and execute prompts/00_ENVIRONMENT_AUDIT.md. Identify the actual Ubuntu release, interface, tools, RAM, disk and GPU. Preserve failures; no installation.
- Acceptance evidence: Actual redacted command outputs for each machine; no inferred versions or access.
- Actual report/commit/reviewer/date: **not recorded**.

## P01 — Names, roles and daily capacity

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: P00.
- Ordered work: Record A/B names, repository owner, reviewer, available hours, overlap time, separate machines/worktrees, demo host and practitioner contact route. Agree daily handoff time and shared-file editor.
- Acceptance evidence: docs/STATUS.md contains agreed roles and capacity; unknowns have owners.
- Actual report/commit/reviewer/date: **not recorded**.

## P02 — Eligibility, official window and form

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: P01.
- Ordered work: Read current rules and authenticated form; record age/residency/team eligibility, one-project rule, implementation dates, exact cutoff/timezone, pre-window allowance and required fields. Distinguish registration from final submission. Obtain dated clarification if ambiguous; no guessed start.
- Acceptance evidence: Dated official references/non-sensitive field notes. Unresolved dates remain a blocker for I00; continue independent preparation.
- Actual report/commit/reviewer/date: **not recorded**.

## P03 — Safe local repository initialization

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: P01.
- Ordered work: Use prompts/01_REPOSITORY_PREPARATION.md after rules evidence is reviewed. Inspect parent repositories/changes, choose new directory, check actual Git identity, initialize main only if appropriate. No application scaffolding or forced cleanup.
- Acceptance evidence: Actual path, branch/status and identity readiness; all existing work preserved.
- Actual report/commit/reviewer/date: **not recorded**.

## P05 — Ignore, original-work licence and initial docs commit

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: P03.
- Ordered work: Choose an OSI-approved licence for original work, provisionally MIT if both agree. Add ignore rules for secrets, environments, weights, caches, databases and private data. Review tracked documentation, make explicit-file initial commit; no dependencies or app code.
- Acceptance evidence: Reviewed tracked-file list, licence and clean documentation commit; no secret files.
- Actual report/commit/reviewer/date: **not recorded**.

## P04 — Shared remote, collaborator access and separate clones

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: P05.
- Ordered work: Create chosen remote using normal named accounts, add B with necessary access, push initial docs and have B clone. Configure supported branch rules or documented manual peer review. Test each person’s branch/remote access without sharing credentials.
- Acceptance evidence: Both report separate checkout paths, same main SHA and normal access; no tokens in reports.
- Actual report/commit/reviewer/date: **not recorded**.

## P06 — Architecture decisions and ownership boundaries

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: P04.
- Ordered work: Read contracts/ADRs, agree directory ownership, state model, minimal topology and shared-file editor. Leave model/dependency versions proposed pending I01. Record discussion and risks.
- Acceptance evidence: Reviewed proposed ADR and architecture; no undocumented conflicting assumptions.
- Actual report/commit/reviewer/date: **not recorded**.

## P07 — Practitioner and institutional workflow

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: P01.
- Ordered work: Identify an extension office/cooperative and obtain consented domain input using interview template. Establish decision owner, actual crop/origin/markets, data freshness, costs and approval needs. If unavailable, record limitation rather than invent endorsement.
- Acceptance evidence: Consented/redacted notes or explicit lack of validation; institution and approval role established before field-validity claims.
- Actual report/commit/reviewer/date: **not recorded**.

## P08 — Source access, observation coverage and rights

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: P07.
- Ordered work: Open candidate sources, verify actual comparable rows in three candidate markets, units/grades/basis/dates and allowed use/redistribution. Record references, permission evidence and limitations. Do not assume API access or copy restricted data.
- Acceptance evidence: Source audit/manifest; usable common coverage or explicit change-of-scope decision.
- Actual report/commit/reviewer/date: **not recorded**.

## P09 — Paper normalization and independent expected answers

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: P08.
- Ordered work: Manually reconcile a small source sample, conversion lineage and date policy. Prepare distinctly synthetic arithmetic scenarios and expected totals independently. Document missing values, cost bases and possible price/grade conflicts.
- Acceptance evidence: Reviewed examples and independently computed answers; no tests generated from implementation output.
- Actual report/commit/reviewer/date: **not recorded**.

## P10 — Lock minimum product scope

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: P06, P07, P08, P09.
- Ordered work: Select one crop/variant, origin, three named reachable markets, institution, data mode/as-of date and officer workflow. Confirm whether historical rather than live. List deferred features and explicit assumptions; resolve failed coverage by changing scope.
- Acceptance evidence: Written scope and source/practitioner constraints accepted by both; no unverified live claim.
- Actual report/commit/reviewer/date: **not recorded**.

## P11 — Freeze initial contracts and preparation gate

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: P10.
- Ordered work: Review ARCHITECTURE_AND_CONTRACTS, field meanings, own tool schemas, API/state/error contracts, calculation rounding/freshness policy and task allocation. Update proposed ADRs and status; identify all unresolved rules/environment/data blockers.
- Acceptance evidence: G1 scope/data/contracts evidence; G0 cannot pass with an unconfirmed implementation calendar.
- Actual report/commit/reviewer/date: **not recorded**.

## I00 — Implementation-start gate

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: P02, P04, P11.
- Ordered work: Confirm current time is inside officially allowed implementation period and preparation/eligibility gates pass. Record evidence and set implementation_start_confirmed only after confirmation. If blocked, continue permitted documentation rather than project code.
- Acceptance evidence: Dated rule evidence, verified start condition and two-person signoff in STATUS.
- Actual report/commit/reviewer/date: **not recorded**.

## I01 — Compatible local toolchain and early real vertical slice

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I00, P00.
- Ordered work: Use audit to choose project Python/Node/tool environments; install only required supported dependencies without replacing system Python. Validate Docker/Compose availability or resolve setup with explicit local instructions. Benchmark candidate open-weights model, record licence/digest/resources. Spike LangGraph checkpoint, compatible MCP adapter and both real MCP transports; discover/call tools, save a tiny private action, pause/restart/resume. Resolve SDK isolation and pin versions before full build.
- Acceptance evidence: Actual versions/locks, commands, model/tool trace, memory/latency and restart evidence; fail early if full tool use cannot work.
- Actual report/commit/reviewer/date: **not recorded**.

## I02 — Normalized schema and permitted data import

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I01, P08, P09, P11.
- Ordered work: Implement agreed source transformation and manifest validation with raw-lineage preservation. Mark synthetic data, enforce explicit units/date/basis/grade. Reject malformed rows and avoid prohibited redistribution; review sample against source.
- Acceptance evidence: Import checks, reviewed sample, source/data hash and exclusion report.
- Actual report/commit/reviewer/date: **not recorded**.

## I03 — Deterministic calculation service

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I01, P09, P11.
- Ordered work: Implement Decimal validation/conversion, explicit loss/cost totals, gross/net formulas, missing-cost and tie/sensitivity behavior. Add independent meaningful checks, including gross-winner/net-loser and unknown sack.
- Acceptance evidence: B’s expected answers match actual outputs; invalid/ambiguous records do not rank silently.
- Actual report/commit/reviewer/date: **not recorded**.

## I04 — Domain database and versioned persistence

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I01, P11.
- Ordered work: Create versioned schemas/migrations, immutable snapshots/versions, unique action keys, atomic decisions/audit and managed graph checkpoints. Configure local persistent volumes; test restart and repeated action.
- Acceptance evidence: Actual migration/restart/duplicate-action results and schema review.
- Actual report/commit/reviewer/date: **not recorded**.

## I05 — Structured run and tool audit

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I04.
- Ordered work: Record run/event IDs, real inputs/outputs/timestamps, server/tool, errors, latency and versions. Distinguish model text from executed actions; redact secret/private fields before export.
- Acceptance evidence: Successful and failed call traces resolve to actual evidence; reviewed redaction.
- Actual report/commit/reviewer/date: **not recorded**.

## I06 — Own MCP quote-search tool

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I02, I05.
- Ordered work: Expose typed search_market_quotes through selected transport. Validate filters/as-of policy; return evidence and exclusions. Verify actual discovery/call, not direct-function-only tests.
- Acceptance evidence: Real MCP input/output trace and correct accepted/excluded source rows.
- Actual report/commit/reviewer/date: **not recorded**.

## I07 — Own MCP comparison tool

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I03, I06.
- Ordered work: Expose compare_market_options with validated quote IDs/snapshot, assumptions and costs. Enforce source resolution and deterministic computation; reject model-invented values.
- Acceptance evidence: Actual MCP calculation agrees with independent totals and handles invalid references.
- Actual report/commit/reviewer/date: **not recorded**.

## I08 — Own MCP private-draft action

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I04, I05, I07.
- Ordered work: Expose save_advisory_draft tied to validated comparison/source hashes. Save pending version only; enforce action-key repeat/conflict rules, no delivery or approval arguments.
- Acceptance evidence: Three own tools discovered; real private action, immutable version and repeated-call checks.
- Actual report/commit/reviewer/date: **not recorded**.

## I09 — Borrowed MCP retrieval integration

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I01, I05, P08.
- Ordered work: Pin upstream Fetch and preserve notices. Enforce approved public URLs, private-network/unsafe-redirect blocking, robots behavior, time/size caps and text-as-data boundary. Demonstrate useful contextual/evidence-gap retrieval via real MCP.
- Acceptance evidence: Actual borrowed-server trace and rationale; blocked unsafe URL and timeout behavior verified.
- Actual report/commit/reviewer/date: **not recorded**.

## I10 — Bounded agent graph and actual open-weights workflow

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I06, I07, I08, I09.
- Ordered work: Implement real model-driven tool selection, typed tool results, conditional clarification/recovery and bounded calls/retries. Preserve deterministic computations, provenance, explicit incomplete outcomes and graph checkpoints. Run representative full task on chosen open-weights model.
- Acceptance evidence: Tool trace shows dynamic complete task with both servers; no hard-coded substitute or fabricated outputs. G2 evidence.
- Actual report/commit/reviewer/date: **not recorded**.

## I11 — Named reviewer authentication and decision API

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I04, I08.
- Ordered work: Implement bounded local authentication with backend-derived identity. Enforce exact pending version/hash, allowed transitions and idempotency; reject anonymous/model/incorrect-role callers. Select documented safe session handling; no credentials in UI code.
- Acceptance evidence: Unauthorized/stale/repeated/conflicting decision tests and transaction/audit results.
- Actual report/commit/reviewer/date: **not recorded**.

## I12 — Human pause, rejection, revision and resume

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I10, I11.
- Ordered work: Connect persistent graph interrupt to decision state; approve/reject/request changes, immutable new revision and invalidation of old approval. Recover decision-before-resume crashes without duplicates.
- Acceptance evidence: Actual approval/rejection/revision/restart workflow; no model-controlled approval.
- Actual report/commit/reviewer/date: **not recorded**.

## I13 — Typed request/status/history API

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I10, I11, P11.
- Ordered work: Expose agreed routes and OpenAPI, validation/error/status semantics, evidence and authorized history. Make API accessible to B’s local UI. Freeze schema revision and coordinate changes.
- Acceptance evidence: API contract/integration results and real example payloads without secrets.
- Actual report/commit/reviewer/date: **not recorded**.

## I14 — Minimal frontend scaffolding and contract views

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I01, P11.
- Ordered work: Create React/TS/Vite with supported pinned toolchain; minimal request/comparison/evidence/review routes. Build against agreed typed contracts; temporary mocks visibly labelled and isolated.
- Acceptance evidence: Type/build checks, UI state design and contract review; no mock claimed as final.
- Actual report/commit/reviewer/date: **not recorded**.

## I15 — Request, comparison, evidence and trace interface

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I13, I14.
- Ordered work: Wire actual API, input validation, gross/net distinctions, excluded records, dates/units, assumptions, synthetic/historical labels and tool activity. Show empty/error/loading states and preserve requests.
- Acceptance evidence: Real API workflow and readable correct monetary/evidence states.
- Actual report/commit/reviewer/date: **not recorded**.

## I16 — Authenticated review and decision interface

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I12, I15.
- Ordered work: Show exact pending version/hash, named local session and approve/reject/request-changes controls. Handle expired identity, stale version, repeated clicks and failures from authoritative server state.
- Acceptance evidence: Real pending→decision flows including rejection/revision; no UI-only gate. G3 evidence.
- Actual report/commit/reviewer/date: **not recorded**.

## I17 — Freeze independent evaluation suite

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I02, I03, P09.
- Ordered work: Choose eight-plus diverse model tasks and all critical invariant checks from DATA_AND_EVALUATION. Freeze input/source hashes, hand-derived outcomes and scoring rules before live runs.
- Acceptance evidence: Versioned scenarios/expected answers reviewed independently; no assumed passes.
- Actual report/commit/reviewer/date: **not recorded**.

## I18 — Live-model evaluation runner and evidence

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I10, I12, I16, I17.
- Ordered work: Run actual selected model and real MCP workflow on fixed tasks; capture every attempt, pass/fail reasons, times/settings/tool events. Repeat three times where feasible; measure manual baseline only if genuinely observed.
- Acceptance evidence: Actual evaluated denominators/results, failure traces and resource/latency record.
- Actual report/commit/reviewer/date: **not recorded**.

## I19 — Failure, authorization and recovery gate

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: I12, I16, I17.
- Ordered work: Execute critical cases: arithmetic, incomparable/stale/future data, absent costs, prompt injection, private URL/redirect, unauthorized approval, stale hash, duplicate actions, model/tool unavailability and restart. Check interface reflects failures honestly.
- Acceptance evidence: Actual critical checks pass; failures recorded and block release rather than hidden.
- Actual report/commit/reviewer/date: **not recorded**.

## I20 — Integrated real workflow and domain assessment

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: I18, I19.
- Ordered work: Run complete representative task, both MCP servers, actual model, pending draft and human decision on final scope. Have practitioner assess usefulness if available. Capture three consecutive successful demo rehearsals if feasible; disclose validation gaps.
- Acceptance evidence: G4 measured results, actual approval evidence, no unsupported field-impact claim.
- Actual report/commit/reviewer/date: **not recorded**.

## I21 — Fix measured failures and freeze feature scope

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I20.
- Ordered work: Prioritize blocking correctness/gate issues, rerun affected checks and model tasks. Retain honest unresolved non-critical failure plus next step. Remove distracting optional features; update actual ADRs/contracts.
- Acceptance evidence: Reviewed fixes and passing affected checks; known limitations match behavior.
- Actual report/commit/reviewer/date: **not recorded**.

## R00 — One-command packaging and readiness

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: I21.
- Ordered work: Create Compose/launch tooling, pinned environments, health/model readiness, persistent storage and permitted seed data. Expose make demo. Document first model download/network/resources and stop/reset behavior; do not erase existing state silently.
- Acceptance evidence: Actual launcher output and full workflow; initial/cached start distinctions recorded.
- Actual report/commit/reviewer/date: **not recorded**.

## R01 — Final locks, automated checks and build

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: R00.
- Ordered work: Lock tested dependencies, automate meaningful backend/frontend/integration checks without secrets, verify production UI build and container behavior. Pin necessary images/model reference and record version limitations.
- Acceptance evidence: Actual final check/build outputs, matching lockfiles and SHA.
- Actual report/commit/reviewer/date: **not recorded**.

## R02 — Data/upstream/model licence and secret review

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: R01, P05, P08.
- Ordered work: Review public tracked files/history for credentials/private data and permission violations; verify original OSI licence plus notices/model/source restrictions. If leakage is found, stop publication and follow proper credential remediation.
- Acceptance evidence: Recorded file/licence/provenance review; permitted public dataset and redacted traces.
- Actual report/commit/reviewer/date: **not recorded**.

## R03 — Independent fresh-clone trial

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: R01, R02.
- Ordered work: On B’s stated environment clone reviewed repo, follow README prerequisites and exact command, then run real model/tools/approval. Record failures and fix documentation/setup before repeating affected trial.
- Acceptance evidence: G5 reproducibility report from fresh clone; no unreported A intervention.
- Actual report/commit/reviewer/date: **not recorded**.

## R04 — Final English submission documents

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: I21, R03.
- Ordered work: Write README from actual trial, one-page ARCHITECTURE.md, EVALS.md with eight-plus actual tasks and observed unresolved failure/next step, and ~300-word theme/institution/workflow description. Review every claim against measured evidence.
- Acceptance evidence: Final documents match actual SHA/model/data; word/page requirements checked.
- Actual report/commit/reviewer/date: **not recorded**.

## R05 — Timed unedited demo rehearsal

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: R03, R04.
- Ordered work: Prepare clean allowed scenario and visible UI/tool logs, actual model, both MCP calls, pending state and named approval. Time warm/cold behavior; rehearse complete unedited run under three minutes without hiding latency or failures.
- Acceptance evidence: Actual durations/run IDs, three successful representative attempts target and no private screen content.
- Actual report/commit/reviewer/date: **not recorded**.

## R06 — Record and publish public video

- [ ] Complete and peer-reviewed
- Lead/reviewer: B; A reviews. Dependencies: R05.
- Ordered work: Record qualifying unedited run; verify content/duration, upload to YouTube/Vimeo with public access, wait for processing and inspect signed out. Do not splice/replay model output as live.
- Acceptance evidence: Public working URL, duration <3min, observed tools/approval and no secrets.
- Actual report/commit/reviewer/date: **not recorded**.

## R07 — Both-person code/live-change rehearsal

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: R04.
- Ordered work: Rehearse ten-minute walkthrough within twenty-minute review; both explain modules, trace, calculations, persistence/gate and eval evidence. Practice a small new requirement with meaningful checks in a separate branch/clone.
- Acceptance evidence: Timed rehearsal, ownership understanding and sample local-change evidence.
- Actual report/commit/reviewer/date: **not recorded**.

## R08 — Final public-access and requirement review

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: R06, R07.
- Ordered work: Use REQUIREMENTS_TRACEABILITY and SUBMISSION_CHECKLIST. Verify public repo/video/docs signed out, final SHA, actual form fields, every requirement and unresolved limitations. Make changes before freeze then rerun affected checks.
- Acceptance evidence: Two-person final release signoff with exact links/SHA; no unpassed critical gates.
- Actual report/commit/reviewer/date: **not recorded**.

## R10 — Record frozen revision and release evidence

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: R08.
- Ordered work: Record exact final SHA, optional tag before cutoff, model/data hashes, reviewed artifacts and planned submitted links. Preserve local release evidence without secret/private exports.
- Acceptance evidence: Immutable release record corresponding to all final checks.
- Actual report/commit/reviewer/date: **not recorded**.

## R09 — Submit correct final form and retain receipt

- [ ] Complete and peer-reviewed
- Lead/reviewer: A; B reviews. Dependencies: R10, P02.
- Ordered work: Using team’s normal signed-in session complete actual final fields, double-check links/team/theme and submit before verified cutoff. Distinguish prior registration. Retain actual receipt/timezone; no assumed acceptance.
- Acceptance evidence: Actual submission receipt and submitted values reviewed by B.
- Actual report/commit/reviewer/date: **not recorded**.

## R11 — Enforce judged-repository freeze

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: R09.
- Ordered work: Verify recorded submitted SHA/links; cease changes to judged repo under published post-deadline rule. Tell both members exact freeze timestamp; avoid automated post-cutoff commits.
- Acceptance evidence: G6 receipt/final SHA/freeze recorded; no unauthorized post-deadline commits.
- Actual report/commit/reviewer/date: **not recorded**.

## R12 — Prepare live review without altering judged repo

- [ ] Complete and peer-reviewed
- Lead/reviewer: Both. Dependencies: R11.
- Ordered work: Keep separate local clone for permitted live modifications, confirm demo readiness and known limitations, follow organizer review instructions. Do not push local live exercise to frozen repo absent explicit authorization.
- Acceptance evidence: Ready review environment and compliance with actual post-deadline instructions.
- Actual report/commit/reviewer/date: **not recorded**.

## Gate mapping

| Gate | Evidence to inspect |
|---|---|
| G0 readiness | P00–P05; verified implementation calendar; unresolved dates block I00 |
| G1 scope/data/contracts | P06–P11 |
| G2 real technical foundation | I01–I10, especially actual model + both MCP servers + calculation checks |
| G3 full officer workflow | I11–I16 including protected rejection/revision/restart |
| G4 measured reliability | I17–I21 with actual results and critical invariants passing |
| G5 reproducibility | R00–R04 including independent fresh clone |
| G6 submitted and frozen | R05–R11, actual receipt and final SHA |

R12 is post-submission review preparation. Completion does not authorize a post-deadline push.
