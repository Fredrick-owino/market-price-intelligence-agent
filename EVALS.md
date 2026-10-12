# SokoSignal evaluations — actual evidence and limitations

I01.13 qualifying-demo continuation; Fredrick, solo review. Official Agriculture
rules require at least eight distinct tasks; they need not all use a live model.
The 110-second edited video is supplementary only, not a qualifying artifact.
All cases below use labelled synthetic fixtures. Expected arithmetic/policies
were recorded before the deterministic run; no independent peer review is implied.

## Distinct task matrix

| Task | Mode / input | Expected | Actual | Result |
|---|---|---|---|---|
| T01 baseline | Deterministic software through actual MCP | `{"nets": ["38000.00", "37000.00"], "winner": "Market A"}` | `{"nets": ["38000.00", "37000.00"], "winner": "Market A"}` | PASS |
| T02 half_quantity | Deterministic software through actual MCP | `{"nets": ["18000.00", "14500.00"], "winner": "Market A"}` | `{"nets": ["18000.00", "14500.00"], "winner": "Market A"}` | PASS |
| T03 explicit_loss | Deterministic software through actual MCP | `{"nets": ["34000.00", "32500.00"], "winner": "Market A"}` | `{"nets": ["34000.00", "32500.00"], "winner": "Market A"}` | PASS |
| T04 missing_fee | Deterministic software through actual MCP | `{"ranking": "gross_only_no_net_ranking", "winner": null}` | `{"ranking": "gross_only_no_net_ranking", "winner": null}` | PASS |
| T05 sack | Deterministic software through actual MCP | `{"error": "incompatible_unit"}` | `{"error": "incompatible_unit"}` | PASS |
| T06 unknown_grade | Deterministic software through actual MCP | `{"error": "unknown_grade"}` | `{"error": "unknown_grade"}` | PASS |
| T07 future_observation | Deterministic software through actual MCP | `{"error": "incomparable_date"}` | `{"error": "incomparable_date"}` | PASS |
| T08 insufficient_capacity | Deterministic software through actual MCP | `{"error": "unconfirmed_capacity"}` | `{"error": "unconfirmed_capacity"}` | PASS |
| T09 duplicate_quotes | Deterministic software through actual MCP | `{"error": "invalid_quote_selection"}` | `{"error": "invalid_quote_selection"}` | PASS |
| T10 request-changes/revision | Actual ASGI API + real model-free MCP pending checkpoint | Authenticated request-changes accepted (HTTP 200), followed by immutable revision | HTTP 422; API only supports approve/reject | **FAIL — unresolved** |

Denominator: **10 distinct tasks, 9 pass / 1 fail**. Nine deterministic cases
executed through a real separate own MCP server; no model mocked into those
results. T10 uses actual local API and real model-free MCP checkpoint, not a
practitioner decision. [Matrix](evals/results/I01.13-distinct-task-matrix.json),
[actual MCP trace](evals/results/I01.13-distinct-task-mcp-trace.jsonl),
[observed revision failure](evals/results/I01.13-unresolved-revision-task.json).

**Unresolved failure and improvement:** request-changes/revision cannot be
performed through the decision UI/API. A separate bounded task should implement
exact-version request-changes, an immutable revised draft and fresh named review,
with old-approval invalidation/recovery tests. Current unsupported state remains
visible; no feature is silently invented for this evaluation.

## Actual model measurements and preserved variation

All runs below use actual pinned Qwen and real borrowed/own MCP. These are
separate from deterministic tasks and labelled regression mocks.

| Adapter / quantity | Actual review state | Request to observed review | Authenticated demo approval |
|---|---|---|---|
| compact-v1-generic-advisory / 500 kg | FAILED: invalid_advisory | 121.509 s | No draft/decision |
| compact-v1-generic-advisory / 750 kg | PENDING_REVIEW | 126.520 s | Yes, isolated synthetic demo identity |
| compact-v2-explicit-advisory-schema / 500 kg | PENDING_REVIEW | 138.603 s | Yes, isolated synthetic demo identity |
| compact-v2-explicit-advisory-schema / 750 kg | PENDING_REVIEW | 138.577 s | Yes, isolated synthetic demo identity |

Initial compact-schema failure is retained: the model nested the advisory under
an unexpected wrapper; validation rejected it before any draft write. The later
explicit model-visible schema returned valid summaries in two measured runs.
[All attempts](evals/results/I01.13-compact-live-measurements.json),
[actual request/response/tool trace](evals/results/I01.13-compact-rehearsal-trace.jsonl).

The two final-schema runs took **138.603 / 138.577 s**. Their observed range
is 0.026 s across only two attempts; this small sample is not a reliability or
hardware-independent guarantee. Recorded UI/browser runtime overhead must still
fit the 180-second limit. Actual continuous cases: 625 kg observed review 141.145 s; 650 kg 135.706 s.
Final-schema observed range across these four successful attempts is
135.706–141.145 s (5.439 s). Both native recordings reached demo approval;
first retained for insufficient save-event dwell, second locally verified.

## Baseline profile and bounded improvements

The retained 220.794-second browser run used 3.485 s retrieval and 211.744 s
in model HTTP requests. Requests: search 29.925 s, compare 59.677 s, save
122.141 s. Own tools together: 0.016882 s; save (including validation, SQL
persistence and MCP response) 0.010680 s. SQL-only duration was not retained.
Final model prompt: 3,199 tokens, with 63.813 s prompt evaluation and 58.134 s
generation. Full comparison/provenance and long assumptions were repeated.
[Profile](evals/results/I01.13-baseline-latency-profile.json).

Removed duplicate comparison/provenance and source manifests from model context,
shortened instructions and redundant schema titles, and projected only required
quote fields. Model still chooses among all three tools on every turn. Its save
summary must exactly match validated core fields; the host restores immutable
assumptions/sources, then full validation is repeated at the real MCP server.
All numbers, references, ordering, provenance, pending state and exact-hash
review controls remain enforced. Search/compare output caps are 256 tokens,
save 384; truncated output fails closed. No model response or tool result is
replaced, hardcoded or replayed. Actual prior evidence and original pending
drafts remain intact. Live UI events expose only whitelisted synthetic
inputs/outputs/timestamps, not headers, free model text or credentials.

## Regression and reproducibility

Final affected/full regression: **157 passed in 113.64 s**; Ruff check and
format passed; frontend typecheck/build passed. Earlier affected suite: 45
passed in 61.03 s. A prior full suite: 157 passed in 144.44 s before explicit
schema tightening; final checks above cover the tightened schema. Regression
model/network responses are labelled mocked where used, with actual MCP/state
for relevant invariants. They are not 157 live-model tasks.

Fresh remote clone of tested milestone **88b25a0** ran documented
`SOKOSIGNAL_PORT=8020 make demo` (existing package cache selected). New root
and Fetch environments and node_modules installed from locks; new mode-0600
private credential pair generated, distinct from original/task credentials.
Separate .state/demo.sqlite; existing pinned model service/files reused without
copy/download. Actual 900 kg Qwen/Fetch/own-MCP workflow reached review in
**129.541 s**, correct net 34,000 / 32,500 KES and authenticated demo approval.
Health 200, anonymous pending 401, valid pending 200; fresh Git status clean.
Stopped only its temporary API afterwards; original API/model stayed healthy.
[Setup/workflow evidence](evals/results/I01.13-fresh-checkout-verification.json),
[preservation check](evals/results/I01.13-original-demo-preservation.json).
This is a same-host, package-cache-backed fresh clone, not an independent
reviewer/different-machine trial or uncached download benchmark.

## Evidence boundaries and remaining limitations

No practitioner or named partner validation, real price integration, independent
review, submitted form or public qualifying-video link. Remote email verification
was owner-reported; remote officer completion is unverified. No new tunnel/upload.
API is single worker with one model workflow slot; multiple workers/independent
inference clients are unsupported. Historical source/data-rights review, exact
official cutoff/eligibility/form and release signoff remain outstanding.

Earlier real Chrome approval/rejection, failures, service recovery and edited
supplementary recording are retained in [historical evaluations](docs/runs/I01.13-evaluation-history.md) and their original linked evidence. No gate is completed by this solo report.


## Final continuous video

Native **650 kg** recording decoded duration **158.12 s**, request-to-review
135.706 s, authenticated demo internal approval visible. Actual Fetch/search/
compare/save inputs/outputs/timestamps appear live; save event held four
seconds. Correct net 24,000 / 21,250 KES, advantage 2,750. No cuts, accelerated
waiting, substituted footage or approval bypass. Credential entry concealed
before document paint; no token/PIN/header screens. English UI, no audio.
[Recording](evals/results/I01.13-continuous-video-2026-10-12T21-00-59-705Z.json),
[actual recordings trace](evals/results/I01.13-continuous-recordings-trace.jsonl).
The earlier 159.68 s native attempt and edited supplementary file are retained.
Local duration/content checks are not organiser acceptance, independent
practitioner validation, public playback or release-gate completion.
