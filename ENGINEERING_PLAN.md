# Market-price intelligence — two-person engineering plan

Prepared 7 October 2026. Working repository name: `market-intelligence-challenge`. This is a preparation pack, not a functioning application. All application implementation is to happen in the team’s local Codex sessions. No installation, repository change, test run, or deployment on either team member’s machine has been performed by this chat.

## Objective and boundaries

Build an agent that helps a named agricultural extension office or cooperative compare reachable markets for a defined crop and quantity. It retrieves evidence, checks whether prices can be compared, calculates estimated net proceeds, handles missing information, saves a private advisory draft, and waits for a named officer’s decision. The officer can approve, reject, or request revision. There is no automatic farmer messaging, sale, booking, input order, payment, or credit decision in the competition scope.

The existing track choice is Agriculture → Market access & price intelligence. Exact commodity, origin, three candidate markets, institution, reference date, and usable source are not yet established. A provisional candidate is Kenyan dry white maize sold at wholesale; keep it only if the data and practitioner checks pass. Never imply that these local details were approved by a practitioner or that live price access is confirmed.

The system estimates proceeds using explicit prices and cost assumptions. It does not promise an actual buyer, capacity to purchase, a guaranteed selling price, or future prices. Weather, credit, price forecasting, multiple crops/countries, mobile applications, and automatic external communication are deferred.

## How the three of us work

| Role | Responsibility | Owns |
|---|---|---|
| Person A — you, provisionally | Backend, calculations, agent/MCP integration, infrastructure and release coordination | `backend/`, `infra/`, root dependency files, CI and release tooling |
| Person B — colleague, provisionally | Practitioner/data investigation, interface, independent evaluation and demo | `frontend/`, `data/`, `evals/`, `docs/data/`, demo evidence |
| Driver — this chat | Order work, explain each task, give bounded Codex prompts, assess evidence, resolve design choices and identify the next gate | Plan and task sequencing; no automatic visibility into local machines |
| Both people | Agree scope/contracts, review each other’s changes, rehearse code review and approve release | Shared documentation through one assigned editor per change |

Roles can be swapped once at kickoff to suit availability. Record the actual names in `docs/STATUS.md`. Each person uses a separate working copy and a separate branch. They must not run two editing Codex sessions in the same checkout. One lead owns each change; the other reviews it. A checks calculations; B independently verifies them against hand-calculated expected results. Neither can declare their own critical gate passed without peer evidence.

I can guide local Codex work when you return its task report, outputs, and relevant diffs. I cannot silently observe the Ubuntu machine or the colleague’s repository. A claim of success without execution evidence remains unverified.

## First preparation steps, in order

1. Download the pack, extract it into a new project directory, and read `START_HERE.md`. Do not overwrite an existing project. Keep this project separate from other repositories.
2. Person A runs the read-only environment audit in `prompts/00_ENVIRONMENT_AUDIT.md` using local Codex. Person B does the same on their machine. If only one machine is available, use separate Git worktrees after repository setup.
3. Record operating system, Git, Python, Node/npm, Docker/Compose, Codex interface, RAM, disk, GPU/VRAM and inference availability. Preserve command failures; do not install every dependency pre-emptively or alter system Python.
4. Identify the repository owner, reviewer, actual team names, daily working hours, overlap time, hardware available for the final demo, and a contact route for an extension officer/cooperative. Use public institutional information and consented conversations; no private farmer records in prompts.
5. Confirm age/residency/team eligibility, submission deadline timestamp/timezone, official implementation window, repository-link timing and the actual authenticated application fields. The user should inspect the Google form in their own signed-in session and supply the non-sensitive field wording. Record organizer clarifications with dated evidence; this chat has not contacted anyone.
6. Set up the Git repository and a shared remote with ordinary named team access. Use the organization/account owner’s normal login and invitation flow. Do not share passwords, tokens or SSH private keys. Configure the branch rules supported by the selected repository plan; otherwise enforce peer review manually.
7. Person B checks usable data and contacts a practitioner; A confirms the hardware/dependency plan. Neither implements the evaluated agent until the official window is established and the implementation-start condition is met.

The competition FAQ permits repository creation and structure beforehand. Preparation code in this pack is limited to examples of commands to run later; there is no agent implementation. Repository setup, dependency installation and a generic non-project tool check must be distinguished from evaluated agent development. If organizers treat even a technical project spike as implementation, schedule that spike inside the official window.

## Proposed architecture and early validation

| Component | Proposed choice | Why and release condition |
|---|---|---|
| Backend | Python 3.12 in a project-managed environment; FastAPI; Pydantic | Typed contracts, clear validation, familiarity of the ecosystem; actual versions pinned after a compatibility spike |
| Agent | LangGraph with bounded model/tool loops and persistent checkpoints | Multi-step work, conditional recovery, human pause and restart/resume |
| MCP client | An isolated adapter boundary selected through the spike | Current LangChain documentation has a new beta `langchain.mcp` API; compare it with a tested stable adapter path and pin one, never mix APIs from different tutorials |
| Our MCP server | Three typed domain tools with actual transport calls | Search quotes, compute comparable alternatives, save an advisory draft |
| Borrowed MCP server | Provisional upstream Fetch reference server | Reuse document retrieval; its source/version/licence and real protocol compatibility must be checked and its tool demonstrably called |
| Model runtime | Local Ollama; initial candidate `qwen3:4b` | Open weights, modest candidate footprint; full-task tool-use and latency benchmarks determine retention or replacement |
| State | SQLite for the bounded single-host prototype; a durable SQLite LangGraph checkpointer | Simple reproducible setup; schema changes versioned, transactions and repeat-action protection tested |
| Frontend | React + TypeScript + Vite | Small officer dashboard with request, comparison, evidence and decision views; supported Node LTS and lockfile pinned during setup |
| Packaging | Docker Compose and a root `make demo` entry point | One documented command for judge execution; initial model download/network and hardware prerequisites disclosed |
| Verification | pytest, frontend type/build checks, meaningful interface/E2E checks, separate live-model evaluation | Deterministic correctness plus honest evidence of actual agent behavior |

These are design decisions proposed by the driver, not competition-mandated brands. Checkpoint and MCP libraries must resolve together with the borrowed server. Keep the upstream Fetch server in a separate environment if it requires a different MCP SDK version. Prefer one application API worker initially. If measured contention or concurrency exceeds SQLite’s safe use, record an ADR and move to PostgreSQL; do not add Redis, queues or Kubernetes without a demonstrated need.

Early spike, inside the allowed implementation window: start the open-weights model; run tool discovery and a real call to each MCP server; execute a tiny model→tool→result loop; pause/resume with a persistent checkpoint; restart and resume without duplicating an action. Capture versions, model digest, quantization, memory use and latency. If this fails, resolve it before building the complete UI.

## Required application behavior

The officer submits a crop/variant, grade where available, sale basis, quantity and known weight, coarse origin, markets, as-of date and explicit cost inputs. The application accepts only quantities greater than zero and valid dates. It can request clarification when crop grade, sack weight, sale basis or costs are ambiguous.

The model chooses appropriate tools rather than a hard-coded script masquerading as an agent. Domain software performs numeric conversions and financial comparisons. The model may explain the results but cannot override the evidence, calculations or approval state. It must not manufacture missing quotes or claim to have called a tool that was not executed.

For the minimum viable flow:

1. Retrieve quotes with source identifiers, observation dates and retrieval times.
2. Exclude invalid, incompatible, future-dated or unacceptably stale quotes; present the reasons.
3. If a gap can be checked against an approved public document, call the borrowed MCP server and identify the document as context, not automatically authoritative structured price data.
4. Calculate alternatives using validated records and known costs. If costs are missing, offer a clearly labelled gross-price comparison and request the missing costs; do not rank it as a net-return winner.
5. Explain the selected option, competing options, data age, assumptions and uncertainty. If there is no defensible choice, save a reviewable insufficient-data result.
6. Save a private `PENDING_REVIEW` draft with an immutable evidence snapshot and version/hash. This is the own-server action tool.
7. Pause for human review. A server-validated named officer reviews the exact version and approves, rejects or requests changes. Changed evidence or content invalidates earlier approval.
8. Record the decision in the audit trail; expose the approved advisory only as a result for the officer. Do not deliver it to a farmer.

Never make the approved/published state depend on an LLM-supplied `approved=true` flag. Reviewer identity comes from the backend’s authenticated local officer session. Use a bounded local demo identity mechanism with secrets from environment, not a production identity-service build. Test that arbitrary callers and the model cannot mint reviewer identity or bypass the endpoint. If remotely hosted later, identity and network controls need a separate deployment decision.

## Data and calculation discipline

Person B first audits sources such as Kenya’s KAMIS and FAO price series. Search found KAMIS records, but the direct page fetch timed out during this planning turn; no working API, complete coverage, current observations or reuse licence is assumed. Verify actual rows, timestamps, definitions, access terms and redistribution rights before importing anything into a public repository. Public visibility alone does not grant redistribution rights.

Keep three data categories distinct: source records, allowed reproducible public snapshots, and synthetic test fixtures. Transport or fee inputs supplied by the team are explicit assumptions until validated. A current live advisory cannot be claimed from old records; a historical replay uses an honest past as-of date. Synthetic data support engineering and failure testing, but do not establish real-world price validity.

The normalized quote needs ID, source ID/reference, crop and variant, grade/unknown, market, county/region, sale basis, price, currency, original unit, confirmed unit weight, observation date, retrieval timestamp and synthetic flag. Preserve raw values and transformation history. One sack is not assumed to be 90 kg unless the source establishes it. Wholesale and retail prices must not be combined in one ranking. Different grades, varieties, dates or units require an explicit comparability policy.

For a validated scenario:

`sellable_kg = input_kg × (1 − assumed_loss_fraction)`

`gross_proceeds = comparable_price_per_kg × sellable_kg`

`estimated_net_proceeds = gross_proceeds − total_transport_cost − handling_cost − market_fees`

All costs have a stated basis and are converted to totals once; use Decimal money arithmetic and document rounding. Use zero loss only if explicitly provided as an assumption. The result must not double-count shared transport costs or invent a per-kilometre rate. Where assumptions are uncertain, show a range or sensitivity and flag a ranking that changes. Numeric observations do not prove buyer availability or sale capacity.

## Delivery phases and dependencies

The full ordered task checklist is in `docs/TASK_BOARD.md`. Every task has a lead, reviewer, dependencies and acceptance evidence. Every gate is documented in `docs/STATUS.md`. Preparation is G0–G1; G2 onwards is evaluated implementation.

| Phase | A workstream | B workstream | Acceptance gate |
|---|---|---|---|
| P0: Readiness | Machine/repository/rules coordination | Second machine, availability, form/practitioner route | G0: verified environment and implementation calendar; unknowns registered |
| P1: Scope/data/contracts | Architecture and schema agreement | Source audit, permitted dataset, domain conversation, independent examples | G1: one useful workflow, defensible data, signed contracts |
| P2: Early vertical slice | Versions/model/MCP/checkpoint spike, calculations, logging | Independent expected answers, wireframes, fixture preparation | G2: real open-weights and both-server execution; calculation checks pass |
| P3: Core behavior | Domain tools, agent recovery, protected decisions, persistence | UI request/evidence/review states, data imports, integration checks | G3: one complete officer workflow passes including rejection and restart |
| P4: Reliability | Fix measured failures, enforce invariants | Eight-plus eval tasks, repeated model runs, practitioner assessment | G4: honest measured results, critical correctness and gate checks pass |
| P5: Reproducibility | Containers, CI, fresh-clone run and release setup | README trial, licence/data review, description and demo preparation | G5: stranger can run documented command on stated hardware |
| P6: Submission | Final commit/artifacts/freeze and live-review rehearsal | Public video and form-field review, submission evidence | G6: verified submission receipt and frozen judged revision |

If the official window is seven days: Day 1 finalizes P0/P1 and the spike; Days 2–3 finish P2 and integrate P3; Days 4–5 complete P3/P4; Day 6 completes P5 and records/rehearses the demo; Day 7 completes P6 with a buffer. Preparation can precede Day 1 within the FAQ’s allowance. This is a relative schedule, not a claim of official dated kickoff. If five days are confirmed, retain the minimum workflow, combine days and remove optional polish; do not remove evaluation, approval, borrowed-MCP or packaging gates.

We have a published 15 October 2026 deadline from the research, but its exact hour/timezone and implementation window remain unresolved. A site recheck timed out on 7 October. Do not infer a kickoff date or midnight cutoff. Plan internal completion at least 24 hours before the verified timestamp where the allowed build window permits it.

## Team Git and Codex routine

Use `main` as the reviewed integration branch. Set up the remote, make one initial documentation commit, and clone it to B’s machine before splitting tasks. Each new task starts from an updated main branch with a clean working tree. Branch names include the task ID. If there are uncommitted changes, record and preserve them; do not hard-reset, force-push or indiscriminately stash someone else’s work.

Each Codex prompt identifies one task, its owner, permitted files, required tests and a finish condition. Codex reads root `AGENTS.md` and the task’s relevant contracts; it does not implement the entire board in one pass. For shared contract/root files, the assigned editor coordinates changes before they land. B may use fixtures matching the agreed contract while A builds endpoints, but all fixture/mock behavior must be clearly labelled and later replaced in the real demo.

The working loop is: choose the next dependency-ready task → run the bounded Codex prompt → inspect diff and execute verification → record actual results → peer review → merge and rerun affected integration checks → return the handoff report to this chat → receive the next task. A failed gate stays failed while unrelated preparation may continue. Every session ends with a current handoff and clean checkpoint where practical. Daily overlap is used to integrate completed work and unblock contracts, not add features casually.

Before a coding task, branch commands are explained in `docs/COLLABORATION.md`; they are to be executed locally after setup, not presumed to have run. Dependency installation occurs in project environments. Git author name/email must be supplied by the actual contributor; neither Codex nor this plan invents them.

## Evaluation and release standards

There are separate deterministic tests and actual model-task evaluations. Unit checks test conversions, totals, ordering and invariants against independent answers. MCP integration checks use real transports. Interface checks verify the real API state. Live evaluation executes the actual selected open-weights model, with real tool traces, on a fixed versioned dataset. Mocks alone do not establish agentic behavior.

Minimum release policy proposed by the driver: all calculation/comparability/approval/provenance safety invariants pass; at least eight diverse model tasks with honest outcomes; three repeated model runs per task where time allows; at least three consecutive successful complete runs of the representative demo task. Record failures rather than silently discarding them. Any unresolved failure must be bounded, visible and unable to compromise money arithmetic or human gates. A model that repeatedly produces malformed tool calls fails the early spike rather than being concealed behind a hard-coded sequence.

Record run IDs, timestamp, scenario, input/dataset hash, expected result, actual result, model tag/digest, settings, tool sequence, latency, tokens where available, and cost assumptions. Local model API fees may be zero; compute is not free. Report wall time and resource use; any electricity/hardware cost estimate states its assumptions. Compare a timed manual workflow with the agent on the same task; do not invent a speedup or claim increased income from a prototype comparison.

README explains prerequisites and first model download. The one-command launcher waits for health, ensures required model availability, seeds only the allowed demo dataset, and starts an accessible local UI. A separate offline replay can improve reproducibility, but the filmed qualifying run uses a real model and real MCP tool calls. Include a real upstream-server retrieval in its qualifying evidence; cached mode must be labelled and not impersonate a live request. Test with network failures as well as the normal path.

Required submission artifacts: public OSI-licensed repository; one-command README; a public YouTube/Vimeo video under three minutes showing an unedited agent run with tools visible; about 300 words naming the theme/institution/workflow; one-page ARCHITECTURE.md; EVALS.md with eight-plus tasks, results and one honest unresolved failure plus the next improvement. The initial pack’s placeholder documents are not final evidence. Judge review is 20 minutes including a ten-minute code walkthrough and a new live requirement.

On the final revision: verify public access while signed out, run a fresh clone, check every link and licence, record the commit SHA and any tag, submit through the verified form, and retain the actual receipt. Under the public rule about post-deadline commits, freeze the submitted repository at cutoff pending organizer clarification. Rehearse local live modifications in a separate clone and do not push them to the judged repository after cutoff. No unrequested submission is performed by this chat.

## Current unknowns and first handoff

Current status: preparation only; local machine not audited; colleague environment unknown; source access/rights not established; institution not confirmed; runtime/model not benchmarked; exact build window unresolved; no application code or test results exist.

The first handoff should include: Person A/B machine outputs, Codex interface type, daily hours, colleague’s name/role, whether separate machines are available, and any official dated window/cutoff announcement. Redact secrets and private paths where needed. Do not send API keys, tokens, private keys or private farmer records.

## Sources and freshness

- Competition [agriculture brief](https://agentic-africa-challenge.lovable.app/tracks/agriculture) and [FAQ](https://agentic-africa-challenge.lovable.app/), fully inspected during 6 October research. Recheck on 7 October timed out. Competition rules override this proposed engineering plan.
- [OpenAI AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), fetched on 7 October.
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [MCP tools](https://docs.langchain.com/oss/python/langchain/mcp/tools) and [MCP migration](https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters), fetched on 7 October. New adapter API is beta; freeze a tested version path.
- [Upstream Fetch server](https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/README.md). Inspect the actual pinned source licence and notices; the upstream repository is undergoing a licence transition. Do not disable robots protections. Apply application-level approved-URL controls.
- [Ollama Qwen3 4B](https://ollama.com/library/qwen3:4b) and [Qwen model licence](https://huggingface.co/Qwen/Qwen3-4B/blob/main/LICENSE); candidate, not a proven best model for this workflow.
- [KAMIS market search](https://kamis.kilimo.go.ke/site/market_search), search-index evidence only in this turn; direct retrieval timed out. [FAO FPMA](https://www.fao.org/giews/food-prices/home/en/) is a data candidate from earlier research. Verify chosen observation coverage and permissions directly before use.
