# Start here

This pack contains planning documents and Codex task instructions. It does not contain a runnable competition entry. Build application code only in local Codex, within the verified competition window.

Read in this order:

1. ENGINEERING_PLAN.md — full scope, responsibility split, architecture and phase gates.
2. AGENTS.md — instructions local Codex must follow.
3. docs/STATUS.md — current facts, blockers and gates.
4. docs/TASK_BOARD.md — ordered task checklist.
5. prompts/00_ENVIRONMENT_AUDIT.md — the first local Codex task.

Extract into a new folder named `market-intelligence-challenge` under `~/Projects`. The archive includes that top-level folder. Use the Ubuntu archive manager or ask local Codex to list the archive, check for an existing destination and safely extract it without overwriting files. The ZIP does not contain secrets, binaries, an installer or application code.

If a folder/repository with this name already exists, stop and report its contents before changing it. Keep this separate from any existing project.

Open this folder in the installed Codex desktop/IDE interface, or run `codex` from its root if the CLI is installed. Use the root as the working directory so project instructions are found. Do not reinstall Codex just because a terminal command is missing; the desktop/IDE interface may be the installed surface.

Paste the prompt in prompts/00_ENVIRONMENT_AUDIT.md. After it finishes, return its summary and command outputs to the driver chat. Person B performs the same audit on their machine. No application implementation is authorized by this first prompt.

The proposed source tree is specified in docs/ARCHITECTURE_AND_CONTRACTS.md. Empty application directories need not exist before the official window; Codex creates them during the relevant approved task.
