# P03 — repository preparation prompt

Use only after P00–P02 preparation evidence has been reviewed and we have selected this directory as the new project. Do not run this blindly inside an existing repository. P04 remote setup and P05 licence/ignore setup have separate tasks.

```text
You are working on P03, preparation only. Read AGENTS.md, START_HERE.md,
docs/STATUS.md, docs/COLLABORATION.md and the P03 task in docs/TASK_BOARD.md.

Inspect the working directory, enclosing Git repository and all existing changes.
If the directory belongs to another project or has unaccounted changes, stop with
the specific findings. Preserve all files and history.

If it is the intended new preparation directory and no repository exists, initialize
a Git repository with main as the initial branch. Do not invent contributor identity;
report whether the owner's normal Git identity is configured, without exposing
credentials. Do not set or print tokens, private keys, passwords or full environment.

Inspect the preparation documents. Do not implement the agent, install dependencies,
create source scaffolding, submit a form or configure a remote. Do not commit until
the ignore/licence and tracked-file review in P05 are complete. Do not push.

Return the actual repository path, Git status, branch, identity readiness (no secrets),
files present, any blockers and proposed P04/P05 next steps. Record a preparation
handoff if authorized by the task; report every command actually run. Do not claim
P03 passed if a prerequisite or check failed.
```
