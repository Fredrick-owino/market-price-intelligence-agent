# English submission description — provisional evidence draft

Updated 13 October 2026. **Not submitted**. Narrative word count 297;
named institution/practitioner and actual form remain unconfirmed.
[Field answers](submission-answers-draft.md), [checklist](SUBMISSION_CHECKLIST.md).

SokoSignal is an Agriculture market access and price intelligence prototype for a proposed extension office or cooperative. The institution, practitioner and final crop and market scope remain unconfirmed. Demonstrations use invented maize prices, transport costs, capacity and markets, without claims about current prices, demand or farmer income.

A local demo officer enters a kilogram quantity. A pinned Qwen model runs through LangGraph; borrowed Fetch MCP retrieves a public commit pinned synthetic fixture. The model selects search_market_quotes, compare_market_options and save_advisory_draft on our own MCP server. Software validates sources and computes gross proceeds, explicit costs and estimated net proceeds. The model cannot override arithmetic or approve advice.

SQLite preserves immutable drafts, provenance, checkpoints and decisions. Review pauses until an authenticated decision matches the exact version and hash. Approval means internal review; no farmer message, sale, payment or advisory delivery occurs. One API worker rejects overlapping new starts, preserves identical retries and serializes recovery. Status polling and independent review remain available.

Profiling found repeated model context dominated a retained 220.794 second run. Shorter prompts and tool results reduced fresh observed review times to 135.706–141.145 seconds across four successful final-schema attempts. One earlier invalid nested advisory failed validation and is retained. Actual sanitized tool events are visible in the interface.

A continuous unedited 650 kilogram demonstration lasts 158.12 seconds and shows actual retrieval, model-selected tools, comparison, pending draft and authenticated demo approval. Ten distinct evaluation tasks report nine passes and one unresolved request-changes failure, separating actual model and deterministic tests. A fresh checkout completed documented one-command setup and real model/MCP approval with new credentials and state, using existing model files.

The video remains local. Partner feedback, data rights, independent review, revision capability, official deadline and form verification remain outstanding. Remote officer completion is unverified. Public upload and submission require separate authorization.
