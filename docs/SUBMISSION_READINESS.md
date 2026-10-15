# Official submission audit — 13 October 2026

Audit base: verified public main `15725b73699776a624487f0bc6aeb7b1f5d4afd2`.
Package changes are documentation/evidence only; no new feature, upload,
submission, tunnel, history rewrite or repository freeze.

Sources re-read: [Agriculture brief](https://agentic-africa-challenge.lovable.app/tracks/agriculture)
(B), [official FAQ](https://agentic-africa-challenge.lovable.app/) (F).
The [official linked form](https://docs.google.com/forms/d/e/1FAIpQLSeVEqZtEasdjqNjDfOqZnS5_XmT6fyz2nHmnPtX6xz0Ppc9FQ/viewform?track=agriculture)
redirected an unsigned-in browser to Google sign-in; question labels were not visible to that read-only browser. Owner subsequently
supplied the portal introduction and first applicant section; exact first fields
are mapped in the answer bank. Later fields remain uninspected. No sign-in data
or form answers were entered by Codex. The FAQ identifies
this as the submission form, not a separate registration step.

PASS means the stated local/artifact check passed, not organiser acceptance.
PARTIAL/OPEN identify the particular unmet requirement, not a failed internal gate.

## Mandatory build and submission items

| ID / item | Source | File/link and actual verification | Result / remaining gap |
|---|---|---|---|
| R01 Agriculture theme and office/workflow | B | [297-word description](submission-description-draft.md); owner supplies intended Kenyan maize-extension workflow. | PARTIAL: no named office/collective. Intended target is not a partnership, endorsement or adoption. |
| R02 Own MCP, at least three tools and an action | B | [Server](../backend/app/mcp/synthetic_server.py); [actual recording trace](../evals/results/I01.13-continuous-recordings-trace.jsonl) resolves search, compare and private-draft save. | PASS: save persists a private immutable advisory, not only read access. |
| R03 Borrowed MCP plus reuse rationale | B | [Fetch pin/notice](../infra/borrowed-fetch/UPSTREAM.md), [README](../README.md), actual public retrieval/provenance in recording evidence. | PASS: adapted upstream Fetch, actual MCP call; separate compatible locked environment. |
| R04 Open orchestration | B | [LangGraph implementation](../backend/app/agent/draft_recovery.py), [licence inventory](../evals/results/I01.13-submission-license-inventory.json). | PASS: actual persistent graph, MIT dependency. |
| R05 Complete task with downloadable weights | B | [650 kg recording](../evals/results/I01.13-continuous-video-2026-10-12T21-00-59-705Z.json), pinned local Qwen digest and actual model-selected tool sequence. | PASS for synthetic task; no replay/frontier substitution. |
| R06 Action audit and named human gate | B | [Review API](../backend/app/api/review.py), [full actual trace](../evals/results/I01.13-continuous-recordings-trace.jsonl), exact draft/hash decision. | PARTIAL: software authentication/logs/pause/resume verified. Approval was automated through `test:local-demo-officer`; owner provides no named human approver. Do not claim real officer/human review. |
| R07 New implementation in communicated window | B/F | [Lead-reported start](handoffs/P02.1-A-2026-10-09.md), Git chronology: dependency foundation 9 October, application behavior 10–13 October. | PARTIAL: original new work evidenced; original organiser window message/exact timestamps not inspected. No existing agent resubmission identified. |
| R08 Public runnable source with OSI licence | B | Anonymous repo/API and README HTTP 200; [public check](../evals/results/I01.13-submission-public-repository-check.json), [MIT](../LICENSE), [notices](../THIRD_PARTY_NOTICES.md). | PASS for source/declared licence; concrete historical source-note question remains in publication review, not proof of a leaked dataset. |
| R09 Single-command README | B | [README](../README.md), `make demo`; [fresh clone verification](../evals/results/I01.13-fresh-checkout-verification.json) with new environments, credentials and state, real 900 kg task/approval. | PASS on stated prerequisites. Same host/cache/model reused; not an independent-machine/operator trial. |
| R10 Public unedited video, tools visible, under 180 s | B | [Media verification](../evals/results/I01.13-submission-video-verification.json): 158.12 s, 3,953 frames, original/copy identical; [Chrome playback](../evals/results/I01.13-upload-copy-browser-playback.json). | PARTIAL: local timing/content passed. No public YouTube/Vimeo URL or signed-out playback. Demo identity does not resolve R06. |
| R11 Approximately 300-word text | B | [Description](submission-description-draft.md), 297 narrative words checked; intended users/workflow explicit. | PARTIAL: named-office information absent (R01). No institution invented. |
| R12 One-page architecture, agent/built-borrowed rationale | B | [ARCHITECTURE.md](../ARCHITECTURE.md), current flow and limitations; A4 reference-layout check recorded in package evidence. | PASS after compact-layout/source review; renderer/page settings remain stated. |
| R13 Eight or more tasks, pass/fail, unfixed case/next idea | B | [EVALS.md](../EVALS.md), [nine-case matrix](../evals/results/I01.13-distinct-task-matrix.json), [T10](../evals/results/I01.13-unresolved-revision-task.json). | PASS: 10 distinct tasks, 9 pass/1 unresolved. Actual model versus deterministic/mocked modes distinguished. No obligation to implement T10 before submission. |
| R14 English materials | B | README, architecture, evaluations, description and actual English video UI/tool text inspected; no audio. | PASS for prepared materials; owner must keep final form answers in English. |
| R15 Data conduct and household-action safeguards | B | [Synthetic fixture](../data/synthetic/I01.7-market-comparison.json), source/provenance validation, approval tests; no farmer delivery/order/credit action. | PASS for implemented synthetic scope. No real household data identified; no current-price or field-impact claims. |

## Eligibility, calendar and review stage

| Item / classification | Evidence | Remaining gap |
|---|---|---|
| Adult/African residency, allowed team size and exclusions — eligibility rule (B) | Current owner is sole active contributor; solo is allowed, up to three entrants. | Owner has not confirmed age/residency/exclusion eligibility. Private contact data belong in the form, not Git/chat. |
| One project/theme — eligibility rule (B) | Prepared project SokoSignal, Agriculture/market access. | Owner must confirm no conflicting entry; no other submission checked. |
| Deadline/version/freeze — submission rule (B/F) | FAQ now explicitly verifies **15 October 2026**. Brief still leaves window timestamps unspecified. | Exact cutoff/timezone/communicated window missing. Owner-supplied form says late commits are not evaluated; track warns disqualification. Record the discrepancy, do not infer closure from congratulations text, and obtain actual policy/timestamp. No receipt/freeze. |
| Code walkthrough/new live requirement — later review stage (B) | Architecture, source and real traces support preparation. | Walkthrough rehearsal remains a later internal preparation task; not another artifact needed for this package. |

The brief's judging factors reward depth, usefulness, robustness, defensibility
and clarity. Practitioner feedback, costs under real conditions and broader
variation can improve scores; no interview, endorsement or adoption exists.
A hosted app/domain is not listed as mandatory; the form's hidden questions
must still be inspected before claiming its exact required fields.

## Internal goals — do not add eligibility conditions

The [engineering plan](../ENGINEERING_PLAN.md) and [task board](TASK_BOARD.md)
include extra release gates. Independent peer/different-host review, eight
*live* model tasks, three repeats per task, revision UI, three markets, Docker/CI
packaging, a manual baseline, public app hosting and a 24-hour buffer are not
extra mandatory submission artifacts in B/F. Safety restrictions still apply;
no feature or evidence may be fabricated to close those internal goals.

T10 is an honestly disclosed unsupported request-changes capability relative to
our broader internal contract. Keeping that failure and proposing a next step
satisfies R13; it does not automatically require another feature. No evaluated
application source was changed during this package audit.

## Remaining mandatory completion

1. Supply a real named intended office/collective and identify/evidence the
   named human review required by R06, without implying institutional adoption.
2. Confirm entrant eligibility/single-entry facts privately and inspect the
   actual signed-in form question labels; [prepared answers](submission-answers-draft.md).
3. Obtain exact cutoff/timezone and communicated window evidence; keep the
   repository editable until the actual rule/timestamp is established.
4. When separately authorised, upload the unchanged video, wait for processing,
   verify public signed-out playback, then complete the real form and retain
   its receipt. [Title/description/instructions](VIDEO_UPLOAD_PACKAGE.md).

Historical KAMIS notes contain small attributed aggregate-price excerpts; current
runtime/data are synthetic. [Publication/licence review](SUBMISSION_PUBLICATION_REVIEW.md)
records the limited finding and permissions question. No automatic history
rewrite, new dataset import or broad publication approval flow was introduced.


## 15 October publication update

Fredrick explicitly requests committing and pushing all pending project changes.
The owner-reported organiser cutoff is 15 October 2026 23:59 Africa/Nairobi
(20:59 UTC); see docs/STATUS.md for source/verification limits. Earlier cutoff-
unknown and no-commit wording records the historical preparation state.
This source publication does not upload a video, submit the form, expose a
network route, establish named-human review or complete a release gate.
