# Third-party notices and licence boundaries

Reviewed 13 October 2026. Root [LICENSE](LICENSE) is MIT for original project
work; it does not relicense dependencies, model weights or third-party data.
Installed environments, downloaded binaries and weights are excluded from Git.
[Inspected inventory](evals/results/I01.13-submission-license-inventory.json).

| Component / inspected version | Licence evidence | Use / retained notice |
|---|---|---|
| LangGraph 1.2.14; checkpoint 4.2.0; SQLite checkpoint 3.1.1 | Installed distribution metadata/licence files: MIT | Persistent orchestration; dependencies installed from uv.lock. |
| MCP SDK 2.3.0 | Installed package metadata: MIT | Own MCP and application client; do not confuse with current upstream repo relicensing. |
| Upstream Fetch 2026.8.18; isolated MCP 1.30.0 | Installed wheel MIT notice, Anthropic PBC 2024; exact retained bytes match | [UPSTREAM-LICENSE](infra/borrowed-fetch/UPSTREAM-LICENSE), [pin/source caveat](infra/borrowed-fetch/UPSTREAM.md). Wrapper adapts upstream HTTP handling; no stock-security claim. |
| FastAPI 0.143.0; Pydantic 2.14.0; aiosqlite 0.22.1 | Installed MIT metadata/notices; aiosqlite notice inspected where licence-expression field absent | API/schema/SQLite access. |
| HTTPX 0.28.1; Uvicorn 0.54.0 | Installed metadata: BSD-3-Clause | Local HTTP/model adapter and API serving. |
| React/React DOM 19.3.0; Vite 7.3.7; React plugin 5.2.0 | Installed package.json: MIT | Officer frontend/build. |
| IBM Plex Sans / IBM Plex Mono, Fontsource 5.3.0 | Installed SIL Open Font License 1.1; IBM copyright | Latin font subsets served locally; full [Sans licence](frontend/public/fonts/ibm-plex-sans-LICENSE.txt) and [Mono licence](frontend/public/fonts/ibm-plex-mono-LICENSE.txt) retained in public build assets. Added in the 15 October UI integration. |
| TypeScript 5.9.3; playwright-core 1.64.0 | Installed package.json: Apache-2.0; Playwright third-party notice files retained in its installed package | Typecheck/browser verification and native capture; no browser binary distributed here. |
| Ollama 0.40.2 | [Pinned upstream licence](https://raw.githubusercontent.com/ollama/ollama/v0.40.2/LICENSE): MIT | Existing complete user-local runtime; retain its bundled library notices if redistributing that runtime. No binary bundled in this repo. |
| Qwen3-4B-Instruct-2507, Q4_K_M | [Publisher licence](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE), [exact Ollama tag](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M): Apache-2.0 | Existing open weights; installed licence layer hash `d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12` matches its bytes. Model digest pinned separately; no weights bundled. |
| Synthetic fixture | Project-authored original invented data, not KAMIS | [Fixture](data/synthetic/I01.7-market-comparison.json); public pinned retrieval retains attribution/hash. |

The [current MCP upstream root licence](https://github.com/modelcontextprotocol/servers/blob/main/LICENSE)
contains a licensing transition; this review preserves the actual pinned Fetch
wheel's MIT notice instead of claiming every current upstream file is MIT or
that an entire source release is byte-identical to the wheel. Only the documented
server.py comparison was established.

This is a direct-component/source-package review, not a full legal certification
of every transitive binary bundle. The source-only install workflow retains
licences in downloaded distributions. Any later redistribution of environments,
browsers, runtime archives or weights needs their own notices/terms retained.
Historical KAMIS notes are addressed in [publication review](docs/SUBMISSION_PUBLICATION_REVIEW.md);
no reuse rights or institution endorsement are granted by this licence file.
