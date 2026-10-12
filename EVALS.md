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

The live model evidence is one successful 500 kg attempt after one timeout, not
a reliability rate. Eight diverse model tasks, repeated runs, independently
prepared expected answers, practitioner review, UI browser exercise and
fresh-clone reproduction are still outstanding. The computer-use browser
surface was unavailable in this session; the frontend was compiled and served
over HTTP but visual interaction was not verified. G0–G6 remain open.

The local API has no public TLS, rate limiting, production identity or
multi-worker recovery lock. Synthetic prices/capacity do not establish real
data rights, market freshness, buyer capacity or farmer benefit. The exact
organizer cutoff and publication decision also remain unresolved.
