"""Assertions inspect a separate CLI client talking to an actual stdio subprocess."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def trace():
    # No direct domain/server imports and no in-memory MCP transport.
    completed = subprocess.run(
        [sys.executable, "-m", "backend.app.mcp.transport_client"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    events = [json.loads(line) for line in completed.stdout.splitlines()]
    assert events[-1]["event_type"] == "shutdown"
    return events


def test_initialize_discovery_resource_and_shutdown(trace):
    events = {event["event_type"]: event for event in trace}
    assert events["initialize"]["protocol_version"] == "2025-11-25"
    assert events["initialize"]["server_info"]["name"] == "sokosignal-synthetic-I01.7"
    tools = events["tools/list"]["output"]["tools"]
    assert {tool["name"] for tool in tools} == {
        "search_market_quotes",
        "compare_market_options",
        "save_advisory_draft",
    }
    assert (
        next(tool for tool in tools if tool["name"] == "compare_market_options")["inputSchema"][
            "properties"
        ]["quantity"]["type"]
        == "string"
    )
    resources = events["resources/list"]["output"]["resources"]
    assert len(resources) == 1
    assert resources[0]["uri"] == "synthetic://sokosignal/I01.7"
    assert resources[0]["mimeType"] == "application/json"
    fixture = json.loads(events["resources/read"]["output"]["contents"][0]["text"])
    assert fixture["synthetic"] is True
    assert fixture["data_status"] == "synthetic"
    assert "SYNTHETIC ONLY" in fixture["label"]
    assert (
        fixture["snapshot_sha256"]
        == hashlib.sha256(
            (ROOT / "data/synthetic/I01.7-market-comparison.json").read_bytes()
        ).hexdigest()
    )
    assert events["shutdown"]["server_process_gone"] is True
    assert [item["event"] for item in events["shutdown"]["lifecycle"]] == [
        "server_starting",
        "server_stopped",
    ]
    for number, event in enumerate(trace, 1):
        assert event["sequence"] == number
        assert event["synthetic"] is True
        UUID(event["run_id"])
        UUID(event["event_id"])
        assert event["timestamp"].endswith("+00:00")


def call(trace, case):
    return next(e for e in trace if e.get("case") == case)["output"]


def test_net_calculation_and_recovery_through_mcp(trace):
    for case in ["baseline", "baseline_after_errors"]:
        result = call(trace, case)
        assert result["isError"] is False
        data = result["structuredContent"]
        assert data["synthetic"] is True
        assert data["winner"] == "Market A"
        assert data["advantage_kes"] == "1000.00"
        assert data["tie"] is False
        assert [m["estimated_net_proceeds"] for m in data["markets"]] == ["38000.00", "37000.00"]
        assert [m["gross_proceeds"] for m in data["markets"]] == ["40000.00", "45000.00"]
        assert [m["total_cost"] for m in data["markets"]] == ["2000.00", "8000.00"]
        assert json.loads(result["content"][0]["text"]) == data


@pytest.mark.parametrize(
    ("case", "code"),
    [
        ("negative_quantity", "invalid_quantity"),
        ("zero_quantity", "invalid_quantity"),
        ("nonfinite_quantity", "invalid_decimal"),
        ("incompatible_quantity_unit", "incompatible_unit"),
        ("invalid_loss", "invalid_loss"),
        ("future_observation", "incomparable_date"),
        ("unknown_snapshot", "unknown_snapshot"),
        ("duplicate_quotes", "invalid_quote_selection"),
        ("insufficient_capacity", "unconfirmed_capacity"),
        ("sack", "incompatible_unit"),
        ("unknown_grade", "unknown_grade"),
        ("different_grade", "incomparable_quotes"),
        ("different_date", "incomparable_date"),
        ("unconfirmed_capacity", "unconfirmed_capacity"),
    ],
)
def test_rejection_through_mcp(trace, case, code):
    result = call(trace, case)
    assert result["isError"] is True
    data = result["structuredContent"]
    assert data["error"]["code"] == code
    assert data["error"]["field"]
    assert data["error"]["message"]
    assert "winner" not in data


def test_missing_cost_is_not_zero_or_net_winner(trace):
    result = call(trace, "missing_fee")
    assert result["isError"] is False
    data = result["structuredContent"]
    assert data["ranking_basis"] == "gross_only_no_net_ranking"
    assert data["winner"] is None
    assert data["advantage_kes"] is None
    assert data["tie"] is None
    assert data["markets"][1]["estimated_net_proceeds"] is None
    assert data["markets"][1]["costs"]["market_fees_total"] is None
    assert data["markets"][1]["missing_costs"] == ["market_fees_total"]


@pytest.mark.parametrize(
    ("case", "nets", "advantage"),
    [
        ("half_quantity", ["18000.00", "14500.00"], "3500.00"),
        ("explicit_loss", ["34000.00", "32500.00"], "1500.00"),
    ],
)
def test_quantity_and_loss_change_calculation(trace, case, nets, advantage):
    result = call(trace, case)
    assert result["isError"] is False
    data = result["structuredContent"]
    assert [m["estimated_net_proceeds"] for m in data["markets"]] == nets
    assert data["advantage_kes"] == advantage
    assert data["winner"] == "Market A"
