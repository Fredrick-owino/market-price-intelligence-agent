# ADR 0002 — phased implementation readiness

Date: 9 October 2026. Decision: lead-directed sequencing change in P11.1.
Owner/executor: Fredrick Onyango under the recorded temporary solo arrangement.
Independent peer review: pending; no task or G0–G6 gate is passed by this ADR.

## Context and authority

The [P02.1 assessment](../handoffs/P02.1-A-2026-10-09.md) correctly found no
implementation task ready under the original all-preparation-first ordering.
The P11.1 user instruction now authorizes a narrower synthetic foundation path.
This ADR supersedes that blanket scheduling conclusion, not the evidence gaps.
All original tasks, ordered work and acceptance requirements remain in the
[task board](../TASK_BOARD.md). This changes when bounded experiments may start,
not what is needed to complete a task, pass a gate or claim a working product.

The start is 2026-10-09, recorded in [STATUS](../STATUS.md) from Fredrick's dated
lead-reported organiser confirmation. The original organiser message was not
independently inspected. Exact start time/timezone, end date/time and cutoff
timezone remain unconfirmed. This ADR does not infer them, certify eligibility
or authorize work after a verified cutoff or submitted-repository freeze.
Fredrick must resolve the calendar before release and reassess future work if
new organiser evidence restricts the allowed period.

## Decision and changed dependencies

| Phase | Entry evidence and work allowed | Evidence still required before advancement or claims |
|---|---|---|
| Synthetic foundation | Confirmed start; Fredrick's recorded machine/repository evidence; explicit temporary solo ownership; bounded experiment scope and contracts below. May perform project-toolchain work, model benchmarks, real MCP transport experiments, deterministic calculation experiments and private checkpoint/recovery experiments using labelled synthetic fixtures. | Each experiment records actual versions, commands, inputs, outputs, failures and scope. A solo run is not independent review. Real MCP calls are required for transport evidence; mocks/replays remain labelled. No original task or gate passes automatically. |
| Real-data integration | Foundation results relevant to the importer/runtime, plus source permission, provenance, normalization and comparability evidence under P08/P09 and the applicable original I02/P11 requirements. | Permission for the intended retrieval/storage/redistribution, permitted snapshot/manifest, row lineage, units/currency/basis/grade/date policy and conflict handling. Historical replay must be explicit; foundation fixtures are not a source audit. |
| Field-validity claims | Practitioner/institution validation under P07/P10 and permitted, suitable evidence for the intended claim. | Named decision owner, consented workflow evidence, useful crop/origin/reachable markets, freshness/cost/approval policy. A synthetic or historical technical demo does not prove field usefulness, current prices, buyer capacity or income gains. |
| Release/submission | Original I00/preparation, G0–G6, evaluation, review, reproducibility, collaborator/public-access and submission requirements. | All original acceptance evidence remains: actual integrated runs, independent expected answers/review, fresh clone, rights/licences, confirmed calendar/eligibility/form, final access checks, signoff, frozen SHA and actual receipt. |

The former start dependency I00 + full preparation is replaced **only for the
named foundation experiments** by the four foundation prerequisites above.
I00's P02/P04/P11 dependencies and two-person signoff remain requirements for
I00 completion; I01's full acceptance remains unchanged. G0/G1 need not be
claimed passed to collect bounded foundation evidence.

After I01.1 verifies the available environment, separately assigned I01
subtasks may establish an isolated compatible toolchain, benchmark the model
and exercise actual MCP discovery/calls and private pause/restart/resume.
Synthetic calculation work corresponding to I03 may start once its required
Python environment and explicit fixture arithmetic contract are verified;
private recovery work corresponding to I04 requires the chosen persistence/
checkpoint dependencies and state contract. They need not wait for live source
permission or practitioner selection. These are partial experiments, not
completion of I03/I04. Original I02/I03/I04 and later task dependencies and
acceptance checks still govern full integration and completion. No broader
frontend, approval service, deployment or product feature is authorized here.

## Foundation scope and contracts

Use [the shared architecture contracts](../ARCHITECTURE_AND_CONTRACTS.md) as
the provisional experiment boundary and [data/evaluation rules](../DATA_AND_EVALUATION.md)
for evidence. Their proposed status is unchanged; this ADR freezes no release
API, model choice or source policy. A later experiment prompt must name its
owner, exact files, inputs/outputs, bounds and acceptance checks before coding.

- Synthetic fixtures carry `synthetic: true` in structured metadata and visible
  output. Use invented market IDs and declared demo grade/date/currency/unit;
  never relabel copied KAMIS observations as synthetic or field-validated.
- Decimal arithmetic follows explicit quantities, loss fraction and cost
  totals. Unknown stays null, not zero; unknown sack weights/grades cannot
  silently become comparable. Declare experiment-only rounding/freshness
  policies. Precompute expected totals separately from the implementation;
  Fredrick's own check remains a solo check, not colleague review.
- Real MCP experiments use actual protocol discovery and calls with bounded
  schemas, timeouts, response sizes and retries. Record tool/server/version
  and trace evidence; a direct Python call or mock does not pass real transport
  checks. No live market ingestion is authorized by a synthetic experiment.
  Any borrowed Fetch retrieval needs an explicitly approved public URL,
  permitted access and the existing private-network/redirect protections;
  selection/approval is required in that experiment's bounded prompt.
- Private state experiments use synthetic pending drafts, immutable versions/
  hashes and idempotency keys. Check pause/restart/resume and repeat/conflict
  behavior without duplicate writes. No real reviewer authority, external
  delivery or production approval is created. Synthetic decision simulations
  remain labelled and do not satisfy the protected human-review workflow.
- Keep source within agreed backend/data/evals boundaries. Do not commit
  credentials, weights, private databases or unsanitized traces. Record pinned
  compatible dependencies only after actual checks. Missing software is a
  concrete blocker for its dependent experiment, not a reason to install
  system packages, change global Python or weaken Docker security.

## Exact first bounded subtask — I01.1

**I01.1: verify Fredrick's available local toolchain and write an experiment
readiness record.** This is dependency-ready as a read-only verification and
documentation subtask; it is not executed by P11.1. Owner: Fredrick, solo.
Start from this ADR revision in an exclusively owned task checkout; preserve
changes and record root, branch, HEAD and actual observation date.

Required input files: AGENTS, STATUS, COLLABORATION, TASK_BOARD, this ADR,
ARCHITECTURE_AND_CONTRACTS, P02.1 handoff and P05.2 recorded machine evidence.
Only output files allowed for I01.1:

- `docs/runs/I01.1-toolchain-readiness.md`
- `docs/handoffs/I01.1-A-<actual-execution-date>.md`

No source, fixture, lockfile, environment, installation, model download or
service creation is part of I01.1. These two reports must contain actual
results and a bounded follow-up proposal, not assumed passes.

Verification to run in I01.1, with failures captured individually:

1. Confirm Git root/branch/cleanliness and read `/etc/os-release`. Check
   `git --version`, `python3 --version`, and whether `python3.12`, `uv`, `node`,
   `npm`, `docker` and `ollama` are present using `command -v`; run their
   version commands only when available. Distinguish missing from inaccessible.
2. Check `docker compose version` and minimal daemon access via
   `docker info --format '{{.ServerVersion}}'`; record exact errors. Do not
   start services, alter groups/socket permissions or treat sandbox denial as
   missing Docker. The driver may supply an ordinary-terminal result.
3. Check `free -h`, `df -h .`, CPU count and, if present, `nvidia-smi` limited to
   GPU name, total VRAM and driver version. CPU inference remains a candidate.
   If Ollama is reachable, inspect `ollama list` for already available model
   tags only; do not download or execute a model in this subtask.
4. Report suitability for the proposed Python 3.12 and isolated dependency
   workflow, runtime/model availability, RAM/disk/accelerator constraints and
   any actual missing prerequisite. No secret files, full environment dumps
   or private records are inspected. No package compatibility is claimed until
   the later dependency spike runs. Node/Compose are not automatic blockers
   for a Python-only local experiment; identify the exact consumer blocked.
5. Propose one next experiment with exact files, synthetic contract, runtime
   bounds and checks based on the findings. Review both reports, use explicit
   staging if authorized, and run documentation/link/whitespace checks.

**Concrete software prerequisite status:** none is verified missing by the
retained evidence. P05.2 records Person A P00 completion and ordinary-terminal
Docker server 29.8.2, with earlier Codex Docker access failure; it does not
retain raw Python/Node/uv/Ollama/model/hardware outputs. Those are unknown, not
installed or missing by inference. I01.1 can run with the available shell/Git;
unavailable commands are findings. Later experiments require a usable project
Python environment and, where relevant, model runtime/weights and compatible
MCP/checkpoint dependencies. Fredrick/local driver resolves proven blockers
through a separately authorized setup task, with no global system changes.

## Outstanding facts and owners

| Missing evidence or decision | Owner | Boundary still affected |
|---|---|---|
| Exact calendar/cutoff, eligibility, authenticated form and rules evidence | Fredrick | P02/I00 completion and release; reassess work against new official restrictions |
| Machine details, runtime access, model licence/digest, resource fit, tested dependency versions | Fredrick | I01.1 findings and each subsequent foundation experiment |
| Colleague participation/name, invitation, clone, P00, push access, capacity/overlap, independent reviewer and team licence agreement | Fredrick coordinates; colleague supplies own evidence when available | P00/P01/P04/P05 completion, peer review and release; solo execution cannot substitute |
| Institution/officer, consented workflow, crop/origin/markets, freshness/cost/approval policy | Fredrick temporarily owns practitioner/data work | P07/P10 and field validity |
| Source rights, permitted snapshot/provenance, grades/units/basis/dates, normalization and duplicate resolution | Fredrick temporarily owns data work; source owner clarifies | P08/P09/I02 real-data integration; historical replay remains conditional |
| Accepted scope, reviewed shared contracts, independent expected answers and gate signoffs | Fredrick edits; designated independent reviewer still pending | P06/P09/P10/P11/I00 completion and G0–G6 evidence as originally specified |

Risks: a synthetic result can be mistaken for field readiness, or a solo check
for independent review. Labels, separate evidence records and unchanged gate
requirements are mandatory. P02.1 remains immutable historical evidence; its
blanket sequencing conclusion is superseded by this dated decision. Future
scope/contract changes require a bounded task/ADR, not silent expansion.
