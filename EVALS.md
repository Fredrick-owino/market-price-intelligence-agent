# Evaluation evidence and current limits

All market records below are synthetic. The actual local HTTP/model attempt on
12 October 2026 used 500 kg. Deterministic expected results are Market A gross
KES 20,000, costs KES 2,000, net KES 18,000; Market B gross KES 22,500, costs
KES 8,000, net KES 14,500. Market A leads by KES 3,500. These are scenario
calculations, not observed market opportunities or an income claim.

| Check | Actual result |
|---|---|
| Backend regression after final request/frontend integration | 147 passed in 147.84s using freshly synced locked application and borrowed-server environments; includes real local MCP transport with mocked network/model cases. |
| Frontend TypeScript and Vite production build | Both passed; build produced static assets. |
| Live HTTP attempt 01 | Failed closed after 222.297s with `request_timeout`; no review outcome. Retained in [attempt 01](evals/results/I01.13-actual-http-attempt-01.json). |
| Live HTTP attempt 02 | Actual public synthetic Fetch over borrowed MCP, actual pinned local Qwen, three own tools, persisted draft in 147.214s; test officer HTTP approval → `approved_internal_review`, retry 200, anonymous 401. [Attempt 02](evals/results/I01.13-actual-http-attempt-02.json). |
| Rejection path | Separate pending synthetic own-MCP workflow rejected through actual HTTP; status `REJECTED`, retry 200. No model/borrowed fetch in that specific check. [Rejection](evals/results/I01.13-rejection-http.json). |
| API restart | Approved and rejected outcomes persisted; draft/action/decision/audit counts unchanged. [Restart](evals/results/I01.13-restart-http.json). |
| Local deployment | `infra/run-local-demo.sh` served built UI, health and authenticated pending route on loopback; all returned HTTP 200. |
| Actual Chrome UI | Two real local Qwen/borrowed-Fetch workflows: 500 kg approved in 234.38 s to review, 1,000 kg rejected in 246.07 s to review. Auth, progress, arithmetic, provenance, refresh, duplicate retries, failed request and narrow layout passed. [Browser report](docs/runs/I01.13-browser-verification.md). |

The live model evidence is one successful 500 kg attempt after one timeout, not
a reliability rate. Eight diverse model tasks, repeated runs, independently
prepared expected answers, practitioner review and fresh-clone reproduction
are still outstanding. The earlier browser-surface blocker was resolved with
local Playwright/Chrome; no independent UI reviewer is claimed. G0–G6 remain open.

The local API has no public TLS, rate limiting, production identity or
multi-worker recovery lock. Synthetic prices/capacity do not establish real
data rights, market freshness, buyer capacity or farmer benefit. The exact
organizer cutoff and publication decision also remain unresolved.
