"""Expected vs actual distinct tasks through a real deterministic MCP server."""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "baseline": {"nets": ["38000.00", "37000.00"], "winner": "Market A"},
    "half_quantity": {"nets": ["18000.00", "14500.00"], "winner": "Market A"},
    "explicit_loss": {"nets": ["34000.00", "32500.00"], "winner": "Market A"},
    "missing_fee": {"ranking": "gross_only_no_net_ranking", "winner": None},
    "sack": {"error": "incompatible_unit"},
    "unknown_grade": {"error": "unknown_grade"},
    "future_observation": {"error": "incomparable_date"},
    "insufficient_capacity": {"error": "unconfirmed_capacity"},
    "duplicate_quotes": {"error": "invalid_quote_selection"},
}


def main():
    destination = ROOT / "evals/results/I01.13-distinct-task-matrix.json"
    if destination.exists():
        raise SystemExit("Existing matrix preserved; use a separately identified repeat")
    frozen = datetime.now(UTC).isoformat()
    run = subprocess.run(
        [sys.executable, "-m", "backend.app.mcp.transport_client"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if run.returncode:
        raise SystemExit("Actual MCP evaluation command failed; no pass claimed")
    rows = [json.loads(x) for x in run.stdout.splitlines()]
    (ROOT / "evals/results/I01.13-distinct-task-mcp-trace.jsonl").write_text(run.stdout)
    results = []
    for number, (case, expected) in enumerate(CASES.items(), 1):
        row = next(r for r in rows if r.get("case") == case)
        result = row["output"]["structuredContent"]
        if "error" in expected:
            actual = {"error": result.get("error", {}).get("code")}
        elif "nets" in expected:
            actual = {
                "nets": [m["estimated_net_proceeds"] for m in result["markets"]],
                "winner": result["winner"],
            }
        else:
            actual = {"ranking": result["ranking_basis"], "winner": result["winner"]}
        results.append(
            {
                "task_id": f"T{number:02d}",
                "case": case,
                "mode": "actual deterministic software via real MCP; no model",
                "input": row["input"],
                "expected": expected,
                "actual": actual,
                "passed": actual == expected,
                "trace_event_id": row["event_id"],
                "latency_ms": row["latency_ms"],
            }
        )
    report = {
        "expectations_frozen_at": frozen,
        "expectation_basis": "Manual fixture arithmetic and explicit validation policies; solo, not independent peer review",
        "performed_at": datetime.now(UTC).isoformat(),
        "distinct_tasks": len(results),
        "passed": sum(r["passed"] for r in results),
        "actual_model_tasks": 0,
        "results": results,
    }
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Distinct deterministic/real-MCP tasks: {report['passed']}/{len(results)} passed; 0 model tasks"
    )
    if not all(r["passed"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
