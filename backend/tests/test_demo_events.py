"""Sanitized actual-event projections; no private transport data exposed."""

from backend.app.agent.demo_events import publish, sink
from backend.app.agent.model_workflow import model_advisory
from backend.app.domain.synthetic_comparison import advisory_for, compare, load_fixture


def test_model_projection_preserves_decisions_and_host_evidence():
    fixture, _ = load_fixture()
    result = compare(fixture["default_request"])
    full = advisory_for(result)
    compact = model_advisory(result)
    assert compact["net_proceeds"] == full["net_proceeds"]
    assert compact["quote_ids"] == full["quote_ids"]
    assert compact["review_status"] == "PENDING_REVIEW"
    assert full["assumptions"] and full["source_references"]
    assert set(full) - set(compact) == {"assumptions", "source_references"}


def test_private_transport_fields_and_untrusted_model_text_are_not_projected():
    rows = []
    token = sink.set(rows.append)
    try:
        publish(
            {
                "timestamp": "2026-10-12T00:00:00Z",
                "event": "model_response",
                "step": 1,
                "elapsed_ms": 10,
                "Authorization": "Bearer PRIVATE_SENTINEL",
                "response": {
                    "message": {
                        "content": "PRIVATE_SENTINEL",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "search_market_quotes",
                                    "arguments": {"token": "PRIVATE_SENTINEL"},
                                }
                            }
                        ],
                    },
                    "headers": {"cookie": "PRIVATE_SENTINEL"},
                },
            }
        )
        publish(
            {
                "timestamp": "2026-10-12T00:00:00Z",
                "event": "mcp_call",
                "tool": "compare_market_options",
                "input": {"quantity": "500", "Authorization": "PRIVATE_SENTINEL"},
                "output": {
                    "winner": "Market A",
                    "advantage_kes": "3500.00",
                    "markets": [{"market": "Market A", "estimated_net_proceeds": "18000.00"}],
                    "headers": {"cookie": "PRIVATE_SENTINEL"},
                },
                "latency_ms": 4,
                "is_error": False,
            }
        )
    finally:
        sink.reset(token)
    assert len(rows) == 2
    assert "PRIVATE_SENTINEL" not in str(rows)
    assert rows[0]["output"]["selected_tool"] == "search_market_quotes"
    assert rows[1]["output"]["net_proceeds"] == {"Market A": "18000.00"}
