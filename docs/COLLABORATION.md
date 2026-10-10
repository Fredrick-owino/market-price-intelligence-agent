# Collaboration and local Codex execution

## Temporary solo working arrangement

Fredrick Onyango is the active contributor and temporarily owns both workstreams:
backend/runtime/infrastructure and data/frontend/evaluation. He may continue
independently on permitted tasks while the colleague is unavailable. This
temporary ownership supersedes the normal A/B division below; it does not
constitute colleague review or satisfy gates that require peer evidence.
[STATUS](STATUS.md) records the lead-reported confirmed start of 9 October
2026 and `implementation_start_confirmed: true`. Under
[ADR 0002](adr/0002-phased-implementation-readiness.md), Fredrick may execute
separately assigned synthetic foundation experiments with recorded machine/
repository evidence, explicit solo ownership and bounded scope/contracts.
This is not completion of I00 or any preparation/gate requirement. Real-data
integration, field claims and release retain their original evidence barriers.
Exact start/end times and cutoff timezone remain unconfirmed.

The colleague's GitHub username is `ianmuriuki`. Participation, invitation
acceptance, clone and audit remain unconfirmed. Resume colleague onboarding
when they become available; confirm those steps before recording them complete.
Availability, team licence review and other unresolved facts remain pending.

The configured GitHub origin is
`https://github.com/Fredrick-owino/market-price-intelligence-agent.git`.
The initial preparation commit `bce05d079ebb88d77d1e55d3a797a37de1487668`
was pushed and verified against remote main during P04.2; local main tracks
origin/main. This confirms the preparation push, not colleague access or review.

## Repository setup after audits
Person A is provisional repository custodian; B reviews root setup. Create a new repository or verify an existing one first. Set the actual contributor identity; do not invent email/name or globally overwrite an existing identity. Create a named shared remote under the agreed owner, authenticate using each person’s normal account and invite the colleague. Never share a token/private key. During preparation, only documentation and allowed structure are committed.

A creates initial documentation main branch, chooses an OSI-approved code licence (proposed MIT) and confirms both contributors agree. Upstream licences and data permissions remain independent of the project’s own licence. B clones the shared repository to a separate directory/machine. Verify fetch/push permissions on a non-production task branch and inspect history. Record the remote privately if it embeds credential material; use clean remote URLs.

## Before a task, on each machine
The commands below are examples after origin/main exists; substitute the actual task ID. Check status first. Do not run checkout/pull if a dirty tree could be disrupted.

```bash
git status --short
git branch --show-current
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c task/PXX-short-description
```

If status is dirty, inspect and preserve changes. If main has diverged, stop for a reviewed resolution. If the task branch exists already, resume it after checking its history rather than recreating it. Each machine/checkout can have one active editing session. On one machine, separate worktrees need unique paths, branches and development ports; choose those only after the initial repository commit exists.

## Task execution and handoff
Use prompts/TASK_PROMPT_TEMPLATE.md with one task row. A owns the shared Python/API contract editor role, B reviews it; agree that ownership can be reassigned explicitly. Root docs/TASK_BOARD.md and docs/STATUS.md are updated by A after B supplies evidence, preventing concurrent board edits. Each person’s handoff file has a unique task/owner/date name. For P11.1, Fredrick is the designated editor of the six authorized documents under the temporary solo arrangement; this does not imply B supplied evidence or review.

Codex implements task scope, runs relevant checks and reports results. The owner reads the diff. Commit only explicit intended files after checking for secrets/data permission. Push the task branch and request the other person’s review through the team’s normal repository workflow. No automatic reviewer message is sent by this chat.

Reviewer checks requirements, source/cost assumptions, failure cases, tests actually executed and interface compatibility. Merge after required checks/review. Both update main before dependent work. Shared contract changes land before implementations that depend on them. If conflict arises, read both changes, agree intended behavior, resolve and rerun affected checks; never select a whole side blindly.

## Daily coordination
Start: each person selects a dependency-ready task and announces file ownership. Midpoint: synchronize contract changes and blockers. End: integrate a working slice, update status and retain task handoffs. Driver feedback uses those reports; silence or elapsed time does not establish success.

## Local secrets and artifacts
Keep .env/private datasets/model weights/generated databases out of commits. Prepare an .env.example with names and harmless examples during setup. Use an ignored local officer credential; show a clear demo-only identity mode. Public artifacts use public/synthetic data. Any practitioner interview notes in the repository need consent and removal of private contact details.

## Release freeze
Before the confirmed deadline, record the judged commit and package version. Do not push later changes to the submitted repository under the current post-deadline rule. The live-review exercise uses a separate clone/branch that remains local unless organizers explicitly permit a later push. Document every exception using actual dated organizer evidence.

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
