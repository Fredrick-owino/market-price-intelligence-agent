"""Bounded, credential-free projections of actual synthetic execution events."""

from contextvars import ContextVar

sink: ContextVar = ContextVar("synthetic_demo_event_sink", default=None)
TOOLS = {"search_market_quotes", "compare_market_options", "save_advisory_draft"}


def publish(row: dict) -> None:
    listener = sink.get()
    if listener is None:
        return
    kind = row.get("event")
    result = {"timestamp": row["timestamp"], "synthetic": True}
    if kind in {
        "borrowed_retrieval_started",
        "borrowed_retrieval_verified",
        "borrowed_retrieval_failed",
    }:
        result.update(
            tool="fetch",
            server="borrowed Fetch MCP",
            phase={
                "borrowed_retrieval_started": "started",
                "borrowed_retrieval_verified": "completed",
                "borrowed_retrieval_failed": "failed",
            }[kind],
        )
        result["input"] = {"source": "fixed commit-pinned public synthetic fixture"}
        if kind == "borrowed_retrieval_verified":
            provenance = row["provenance"]
            result["output"] = {
                key: provenance[key] for key in ("sha256", "bytes", "evidence_mode")
            }
            result["elapsed_ms"] = row["retrieval_ms"]
    elif kind == "model_request":
        result.update(
            tool="model selection", server="local pinned Qwen", phase="started", step=row["step"]
        )
    elif kind == "model_response":
        response = row["response"]
        calls = response.get("message", {}).get("tool_calls", [])
        selected = calls[0].get("function", {}).get("name") if len(calls) == 1 else None
        result.update(
            tool="model selection",
            server="local pinned Qwen",
            phase="completed",
            elapsed_ms=row["elapsed_ms"],
            output={
                "selected_tool": selected if selected in TOOLS else "invalid selection",
                "prompt_tokens": response.get("prompt_eval_count"),
                "generated_tokens": response.get("eval_count"),
            },
        )
    elif kind in {"mcp_call_requested", "mcp_call"} and row.get("tool") in TOOLS:
        name = row["tool"]
        result.update(
            tool=name,
            server="own MCP",
            phase="started" if kind.endswith("requested") else "completed",
        )
        raw_input = row["input"]
        if name == "save_advisory_draft":
            result["input"] = {
                key: raw_input["advisory"][key]
                for key in ("winner", "net_proceeds", "advantage_kes")
            }
        else:
            allowed = {
                "commodity",
                "variant",
                "grade",
                "sale_basis",
                "as_of_date",
                "market_ids",
                "snapshot_id",
                "quote_ids",
                "quantity",
                "unit",
                "loss_fraction",
                "policy_version",
            }
            result["input"] = {key: value for key, value in raw_input.items() if key in allowed}
        if kind == "mcp_call":
            result["elapsed_ms"] = row["latency_ms"]
            if row.get("is_error"):
                result["phase"] = "failed"
            else:
                output = row["output"]
                if name == "search_market_quotes":
                    result["output"] = {
                        "quote_ids": [q["quote_id"] for q in output["quotes"]],
                        "markets": [q["market"] for q in output["quotes"]],
                    }
                elif name == "compare_market_options":
                    result["output"] = {
                        "winner": output["winner"],
                        "advantage_kes": output["advantage_kes"],
                        "net_proceeds": {
                            r["market"]: r["estimated_net_proceeds"] for r in output["markets"]
                        },
                    }
                else:
                    result["output"] = {
                        key: output[key]
                        for key in ("draft_id", "version", "content_hash", "review_status")
                    }
    elif kind == "model_workflow_failed":
        result.update(
            tool="workflow",
            server="local application",
            phase="failed",
            output={"failure_code": row["failure_code"]},
        )
    else:
        return
    listener(result)
