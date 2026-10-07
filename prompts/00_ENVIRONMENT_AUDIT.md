# First Codex prompt — read-only machine audit

Paste the text below into Codex while its project directory is the extracted pack root.

---

Read AGENTS.md, START_HERE.md, docs/STATUS.md and task P00 in docs/TASK_BOARD.md. We are preparing a two-person market-price intelligence competition project. Application implementation has not started.

Perform a read-only audit of this actual Ubuntu machine and project location. Do not install or upgrade software, initialize Git, change permissions, edit dotfiles, alter services, or create application code. Do not read or print environment variables, secret files or credentials.

Inspect the current directory, whether a Git repository exists, and Git status if applicable. Check /etc/os-release, git --version, python3 --version, node --version, npm --version, docker --version, docker compose version, and whether the ordinary Docker daemon is reachable using docker info with a minimal server-version output. Check command -v codex and codex --version only if available; if the CLI is missing, record that the current desktop/IDE session may still be the installed Codex interface. Check command -v uv and uv --version if present; check command -v ollama and ollama --version if present. Do not start missing services.

Check free -h, df -h . and CPU count. If nvidia-smi exists, query only GPU name, total VRAM and driver version. If it does not, record unavailable; lack of an NVIDIA GPU is not proof that all model inference is impossible.

For each command, report available/missing/error and the actual concise output. Do not turn a permission error into an instruction to run everything with sudo. List only prerequisites needed for this project and defer model size/dependency decisions until the audit is reviewed. Do not assert that packages are installed based on old conversation history.

Return task ID P00, actual working directory, existing-repository status, software versions, CPU/RAM/disk/GPU summary, blockers and a proposed smallest next step. Do not write or implement anything in this task.

---
