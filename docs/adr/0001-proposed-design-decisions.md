# Proposed decisions — accept only after evidence

Date: 7 October 2026. Status: PROPOSED. A edits; B reviews. Split into individual ADRs if changed independently. These choices are not organizer requirements.

| Decision | Proposal and reason | Evidence before acceptance | Revisit trigger |
|---|---|---|---|
| Scope | One crop/origin, three reachable markets, one officer workflow; sufficient focus for measured correctness | Practitioner usefulness, comparable permitted records, recorded boundaries | Coverage/right failures or practitioner rejects decision |
| Model/MCP path | Small open-weights candidate plus LangGraph and a pinned compatible MCP adapter; isolate borrowed Fetch dependencies | Full model tool loop, real calls to both servers, licence/digest, latency/memory, durable pause/restart | Malformed tool calls, incompatible protocol, poor latency/resource fit |
| Persistence | SQLite with one API worker and durable graph checkpoints; atomic decision/audit and unique action keys | Restart, repeat-action and concurrency checks on demo host | Measured contention or need for multiple application instances |
| Human gate | Exact immutable draft version/hash, backend-authenticated named reviewer; model cannot approve | Unauthorized/replay/stale-version/revision tests, practitioner approval process | External delivery or production authentication added |
| Data mode | Prefer permitted source-backed records; historical replay allowed only when visibly labelled; synthetic fixtures for testing | Dates, unit meanings, source licence and manifest reviewed | Live claims, new crop/market or changed source format |
| Packaging | One-command local demo with explicit first-download/network requirements | Fresh clone on B’s machine, measured cold/warm startup | Judge environment differs or network unavailable |

Accepted decision record: date, actual version/choice, alternatives considered, measurements, consequences, A name, B reviewer and linked handoff. Never mark accepted because it sounds plausible.
