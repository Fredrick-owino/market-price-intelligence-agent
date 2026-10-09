# SokoSignal: project and colleague onboarding guide

Version 1.0 | 9 October 2026 | Project lead: Fredrick Onyango

Repository: https://github.com/Fredrick-owino/market-price-intelligence-agent

> **Preparation only:** This guide describes the target workflow and proposed responsibilities, not implemented capabilities or completed onboarding. [Current status](STATUS.md) keeps `implementation_start_confirmed: false`; official window evidence and colleague participation remain unconfirmed. Follow the [collaboration agreement](COLLABORATION.md) and [shared contracts](ARCHITECTURE_AND_CONTRACTS.md).


## 1. What we are building

SokoSignal is a market-price intelligence agent for the Agriculture track of the African Agentic AI Design Challenge. It helps an agricultural extension officer or cooperative adviser compare selling options for a crop and prepare an evidence-based advisory for human review.

The initial working scope is Kenyan white maize and a small set of markets. The specific institution, officer, origin and final market coverage must be established through practitioner validation and the data audit. We should build one reliable comparison workflow before adding more crops or features.

The core question is: **Given a quantity of maize, comparable market quotes and explicit selling costs, which market offers the strongest estimated return, and what evidence or uncertainty affects that conclusion?**

The highest quoted price may not produce the highest net return. Dates, units, sale basis, grade compatibility, transport, handling and market fees all matter. A quote also does not prove that a buyer will purchase the entire quantity.

Our first users are officers and cooperative advisers. A named human reviews the exact advisory before it is treated as approved. Direct farmer messaging, sales, purchases, credit, payments and automated orders are outside this build.

## 2. What a complete user journey looks like

1. The officer provides the crop/variant, quantity, candidate markets, reference date and explicit costs. Missing information remains unknown rather than becoming zero.
2. The agent examines the request and asks for clarification when necessary.
3. Through MCP, it retrieves market records and supporting source evidence.
4. Deterministic services validate units, currency, dates, sale basis and grade compatibility. Unusable quotes are excluded with reasons.
5. The comparison service computes gross proceeds and, where costs are complete, estimated net returns. It identifies ties and uncertainty.
6. The agent explains the results using the returned evidence and saves a private advisory draft.
7. The workflow pauses. The officer inspects the comparison, sources, assumptions and tool trace.
8. The officer approves, rejects or requests changes through a protected backend endpoint. Approval applies to an exact immutable draft version and hash.
9. A revision creates a new draft version and requires a new decision. Restarting a run must preserve its recorded state and avoid duplicate writes.

The interface displays authoritative backend state. It must never manufacture tool results, totals, approvals or successful completion.

## 3. A simple example

**These numbers and market names are synthetic development examples. They are not KAMIS records or current prices.** Assume the same crop, compatible declared demo grade, currency, wholesale basis and observation date for both quotes. Quantity is 1,000 kg and the explicit loss assumption is 0%.

| Item | Demo Market A | Demo Market B |
|---|---:|---:|
| Price per kg, KES | 50 | 47 |
| Gross proceeds, KES | 50,000 | 47,000 |
| Total transport, KES | 8,000 | 2,000 |
| Total handling, KES | 1,000 | 1,000 |
| Total market fees, KES | 500 | 500 |
| Estimated net proceeds, KES | 40,500 | 43,500 |

Market B has the lower quoted price but the higher estimated net proceeds under these supplied assumptions. The system should show the calculation and evidence, then request human review.

The deterministic formula is:

```text
sellable_kg = input_kg * (1 - explicit_loss_fraction)
gross_proceeds = normalized_price_per_kg * sellable_kg
net_proceeds = gross_proceeds - transport_total - handling_total - fees_total
```

Total costs are charged once. Per-unit charges require explicit conversion. If a necessary cost is missing, the system may show gross proceeds but must not declare a net-return winner. An unspecified sack must not silently become a 90 kg sack.

## 4. The architecture in plain language

| Component | Responsibility | Target technology |
|---|---|---|
| Officer interface | Capture requests; show comparisons, evidence, tool events and review decisions | React, TypeScript, Vite |
| Application API | Validate inputs; manage identity, run status and protected decisions | Python 3.12, FastAPI, Pydantic |
| Agent and orchestration | Plan, choose tools, clarify, explain, pause and resume | LangGraph |
| Open-weights model | Reason about workflow steps and produce grounded explanations | Target: Qwen3 4B through Ollama; benchmark before final selection |
| MCP client | Discover/call tools and read supported resources | Compatible, pinned MCP adapter and SDK |
| Own MCP server | Search quotes, compare markets and save private drafts | Python server with validated schemas |
| Borrowed MCP server | Retrieve useful supporting public source documents | Pinned upstream Fetch server and its `fetch` tool |
| Domain services | Validate evidence and perform Decimal arithmetic and state transitions | Deterministic Python |
| Persistence and memory | Store quotes, evidence, drafts, decisions, audit events and durable workflow checkpoints | SQLite plus the selected LangGraph checkpointer |
| Deployment | Reproduce the integrated demo with one documented launch command | Docker Compose and project launch scripts |

Memory means persisted request/run state and evidence across steps and restarts. Long-term farmer profiles and a vector database are outside the current scope.

The model may suggest the next step. Software validates inputs and authorizes actions. Tools execute bounded operations. Logs record what actually happened. The model cannot approve its own recommendation.

### MCP tools and resources

The proposed own server must provide three tools:

- `search_market_quotes`: returns sourced records, missing-data status and exclusions.
- `compare_market_options`: returns deterministic calculations and evidence references.
- `save_advisory_draft`: writes a versioned, private pending draft using an idempotency key.

The expanded target architecture also includes read-only source manifests, quote snapshots and evidence resources. Their exact MCP resource identifiers and client/server contracts must be incorporated into the shared contract before implementation. The diagram in the [shared architecture contract](ARCHITECTURE_AND_CONTRACTS.md) describes the proposed flow; it is not evidence of working endpoints.

The borrowed Fetch server supplies public-source retrieval. Its results must be treated as data, validated and bounded by approved URLs, timeouts and response-size limits. Fetching an unrelated URL solely to increase the tool count is not a meaningful integration.

## 5. Who does what

The proposed colleague workstream covers **data, frontend and independent evaluation**. Fredrick retains **backend, agent/MCP runtime, persistence, approval enforcement, infrastructure and integration**. Only an authenticated named officer can approve an advisory. Under the current temporary solo arrangement, Fredrick owns both workstreams until participation and task ownership are explicitly agreed; this guide does not record acceptance or peer review.

| Work area | Fredrick | Colleague (`ianmuriuki`; participation unconfirmed) |
|---|---|---|
| Scope and practitioner workflow | Coordinate decisions and approvals | Help validate the real workflow and record consented findings |
| Data sources and permissions | Review integration feasibility | Lead source manifests, metadata, rights evidence and data-quality checks |
| Schema/import, task I02 | Own backend boundaries and review importer integration | Lead task-assigned dataset/import work against the agreed schema |
| Arithmetic and domain rules | Implement deterministic services | Independently calculate expected answers and review assumptions |
| MCP and agent, I01/I06-I10 | Implement and integrate | Supply valid evidence cases; review returned data and UI needs |
| Identity and approvals, I11-I13 | Implement authoritative backend behavior | Review contracts and verify UI never bypasses authorization |
| Frontend, I14-I16 | Supply stable API contracts and review integration | Implement request, comparison, evidence, trace and review screens |
| Evaluation, I17-I20 | Support real runtime runs and fix measured failures | Lead independent cases, expected answers, results and failure analysis |
| Packaging and release | Own deployment, dependency locks and final integration | Lead fresh-clone trial, documentation review and demo support |
| Shared status/task board/contracts | Designated editor | Provide evidence and proposed changes rather than editing concurrently |

Each task has one active owner. These responsibilities do not authorize every listed task at once; follow its task-board dependencies and agreed file ownership. You are a product engineer with defined deliverables, not simply an additional reviewer.

## 6. Your concrete deliverables

### Data and workflow evidence

- A source manifest for each usable dataset, including owner, URL/reference, observation coverage, retrieval date, units, currency, licence/permission evidence, attribution and redistribution limits.
- A clear distinction between permitted real records, historical replay and synthetic fixtures.
- Validation cases for missing grades, stale dates, conflicting quotes, inconsistent units and absent costs.
- Practitioner evidence that establishes the intended officer workflow, comparison policy and useful output. A team simulation is labelled as a simulation.
- Only permitted, reviewed snapshots in Git. Private records and unapproved raw source exports remain outside the public repository.

### Frontend

- A request form using the agreed API schema.
- Visible loading, missing-information, insufficient-evidence, failed and pending-review states.
- A comparison table with gross/net values, costs, excluded records and ranking basis.
- Source/date/unit/grade information, assumptions and actual tool events.
- A reviewer interface for the exact draft version: approve, reject or request changes.
- Clear stale-version/conflict handling and a visible new review requirement after revision.

Start against an agreed contract. If the backend is not ready, use explicitly labelled development fixtures; fixture behavior does not count as an integrated demonstration.

### Independent evaluation

Prepare at least eight meaningful cases with input, expected outcome and rationale before inspecting live agent results. Suitable cases include:

| Case | Expected behavior |
|---|---|
| Comparable quotes and complete costs | Correct calculation and sourced draft; human review required |
| Lower price but lower selling costs | Rank using net returns rather than quoted price alone |
| Missing cost | No invented zero and no unsupported net winner |
| Unspecified sack size | Request confirmed conversion or exclude the quote |
| Stale or future-dated quote | Apply the documented policy and explain exclusions |
| Missing/incompatible grade or sale basis | Apply the explicit comparability policy; no silent equivalence |
| Conflicting source records | Flag ambiguity rather than choose an arbitrary value |
| Equal results or changing cost ranges | Explain tie or sensitivity; no false certainty |
| Duplicate draft/decision retry | No duplicate business action; consistent result or conflict |
| Rejection, revision and restart | Preserve decision history and require review of the new version |

Expected arithmetic must be calculated independently, not copied from the implementation under test. Record actual runs, pass/fail outcomes, environment/model versions and limitations. Document any observed unresolved failure and a concrete next improvement. If none is observed, follow [the evaluation contract](DATA_AND_EVALUATION.md): broaden relevant checks and seek clarification rather than inventing a failure. Tests that were blocked are recorded as blocked.

## 7. Where your work belongs

| Path | What belongs there |
|---|---|
| `frontend/src/` and `frontend/tests/` | Frontend implementation and critical interface verification |
| `data/` | Permitted snapshots, source manifests and labelled synthetic fixtures |
| `evals/` | Independent cases, expected outcomes and evaluation tooling/results |
| `docs/data/` | Source access, permission and metadata evidence |
| `docs/runs/` | Reviewed, sanitized execution evidence |
| `docs/handoffs/` | Your task-specific results, blockers and verification record |

Backend importer work, shared schema changes and evaluation-runner integration may cross these boundaries. Agree the exact files before editing them. Fredrick coordinates backend/API/MCP changes, root configuration, shared contracts and task-board/status edits.

## 8. Getting started on your machine

1. Accept the repository invitation for `ianmuriuki`, if it has not already been accepted. Confirm the repository opens under your own GitHub account. Authenticate with your own account; do not borrow Fredrick's credentials.
2. Use a separate clone on your machine. If the destination already exists, inspect it and resume safely rather than overwriting it.

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/Fredrick-owino/market-price-intelligence-agent.git
cd market-price-intelligence-agent
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

These commands are for a new clone; its folder name differs from Fredrick's local `market-intelligence-challenge` folder. Git identifies the project through the repository, not through matching directory names.

3. Read [AGENTS.md](../AGENTS.md), this guide, [START_HERE.md](../START_HERE.md), [ENGINEERING_PLAN.md](../ENGINEERING_PLAN.md), [STATUS.md](STATUS.md), [COLLABORATION.md](COLLABORATION.md), [ARCHITECTURE_AND_CONTRACTS.md](ARCHITECTURE_AND_CONTRACTS.md) and your task row in [TASK_BOARD.md](TASK_BOARD.md). Read the merged [source audit](data/SOURCE_AUDIT.md) and its [handoff](handoffs/P08.1-A-2026-10-07.md).
4. Open that repository root in your installed Codex app. Application coding is done in local Codex on each contributor's machine. This guide is not a software installation script.
5. Perform P00 using `prompts/00_ENVIRONMENT_AUDIT.md`. Return actual versions, hardware, Git root/status and blockers. Do not install packages as part of the read-only audit.
6. Tell Fredrick your name, daily available hours, overlap time and current skills. Confirm your first task, branch and file boundaries.
7. Verify your own collaborator access using a lead-approved task branch. Do not assume invitation acceptance or read access proves push permission.
8. Begin the first dependency-ready assigned task. The lead must record the confirmed build start in repository status before enabling evaluated implementation. Report stale or contradictory status rather than silently overriding it.

## 9. Your first work sequence

| Order | Action | Completion evidence |
|---|---|---|
| 1 | Confirm access and perform P00 | Actual machine/repository report |
| 2 | Confirm role, capacity and first task | Agreed ownership and availability |
| 3 | Read P08.1/P08.2 audit and help resolve P07-P09 scope/data questions | Explicit permission/metadata findings and independently calculated paper cases |
| 4 | Review/freeze the shared contracts with Fredrick under P06/P11 | Agreed schema, states, resource/tool/API contract and file ownership |
| 5 | Begin assigned implementation tasks after their prerequisites | Reviewed data/frontend changes and actual checks |
| 6 | Freeze independent evaluation cases, then run the integrated agent | Expected versus actual results and failure evidence |
| 7 | Perform fresh-clone verification and support the demo/release | Reproducible run, documentation corrections and tested public artifacts |

Practical parallelism: while Fredrick builds deterministic services and the MCP/agent runtime, you prepare evidence and evaluation expectations, then implement the frontend once the API contract is stable. Do not create a second competing backend or redesign the product in parallel.

## 10. Git and Codex collaboration

Check the working tree before switching branches. If it contains unfinished work, inspect it and preserve it first. Do not discard it or pull over it blindly.

For a clean checkout starting a new assigned task:

```bash
git status --short --branch
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c task/I14-frontend-colleague
```

The branch above is an example for an assigned I14 task. Substitute your actual approved task ID/name. If it already exists, inspect and resume it rather than trying to recreate it. Never switch an active Codex session's checkout underneath it. Simultaneous local sessions require separate worktrees.

Use this pattern for each Codex task:

```text
Read AGENTS.md, current status, my assigned task row and relevant contracts.
Inspect the actual repository root, branch and Git status.
Implement only the assigned task and necessary prerequisites in agreed files.
Preserve other contributors' changes and report contract conflicts.
Use real data/tool/test evidence; label fixtures and replay.
Run checks appropriate to the change.
Return task ID, changed files, actual checks/results, blockers and Git status.
Write the uniquely named handoff required by the project instructions.
Do not start another task or mark shared gates complete automatically.
```

Review the diff and stage only explicit task files before committing. Push your task branch and obtain the review required by the collaboration agreement before merging into `main`. A file is shared with your colleague only after its commit has been pushed to the remote revision they fetch.

## 11. Handoff and daily coordination

Each handoff records the task ID, owner, base revision, changed files, implemented behavior, commands and actual results, known failures, relevant source/model/contract versions and next dependency-ready action. Use a unique filename under `docs/handoffs/` following the existing template. Do not insert another person's review or a test success that did not happen.

At the start of each work session, confirm your task and owned files with Fredrick. When blocked, report the exact missing contract, data field, runtime capability or failing command. At the end, provide the handoff and pushed commit. Fredrick integrates accepted work and updates shared status.

The driver chat supplies bounded next steps based on these reports. Each local Codex session edits its own assigned checkout; it is not an independent product manager. If Fredrick covers your task while you are unavailable, explicitly agree ownership before you resume it.

## 12. Current evidence and remaining decisions

The following reflects repository evidence and the fetched remote main checked for this documentation publication on 9 October 2026. It does not verify source observations anew or establish organizer approval:

| Item | Verified repository state or remaining limitation |
|---|---|
| Official build start | UNCONFIRMED in STATUS; no dated official evidence recorded; implementation remains disabled |
| Exact build end/cutoff time and timezone | UNCONFIRMED in STATUS; do not infer |
| Published deadline | STATUS retains 15 October 2026 from the planning pack; not independently reverified for this guide |
| Source audit | P08.1/P08.2 documentation committed; source access observed, rights/comparability unresolved |
| Audit revision | `9ce7c36cae182c9984b9222eeb028284a6255eb3`; verified as fetched `origin/main` before this documentation task |
| Audit integration into main | Complete by fast-forward; local main and fetched origin/main match the audit revision above |
| Application implementation | PREPARATION; no local implementation verified in STATUS |
| Colleague onboarding and machine audit | Not yet evidenced |
| Target institution/reviewer and final market scope | Not yet confirmed |
| Runtime, final model and compatible dependency versions | Still require measured verification |

The source audit reported white-maize records for Kutus, Eldoret Main and Kerugoya on 31 August 2026 with wholesale/retail columns and KES/kg evidence. Missing grades and conflicting records prevent an assumption of full comparability. This is historical evidence, not proof of today's prices. Original temporary HTML was later reported missing, which limits independent rechecking; retain permitted evidence durably in future work.

KAMIS and FAO FPMA are target source candidates, not verified live API integrations. Do not invent a public KAMIS REST endpoint or assume redistribution permission because a page is accessible. Keep uncertainty visible and use labelled synthetic fixtures when real data is not yet usable.

The repository's current instructions, contracts, task evidence and lead-recorded decisions govern implementation. This guide explains the intended build and work split; it does not mark any gate complete.

## 13. What success looks like

Your workstream is successful when an officer can understand and review a real agent run through your interface, the evidence can be traced to permitted sources or labelled fixtures, and independently prepared evaluations show where the system succeeds and fails.

Together, we need a reproducible repository, real MCP/tool execution, an open-weights model run, correct deterministic comparisons, durable human review and recovery, honest evaluation results, clear documentation and an accessible demonstration. The final code and evidence must support every capability claimed in the form.
