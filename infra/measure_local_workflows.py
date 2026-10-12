"""Actual loopback model/MCP measurements; no remote login evidence."""

import json
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8001"


def main():
    token = (ROOT / ".env.token.local").read_text().strip()
    history = ROOT / "evals/results/I01.13-compact-live-measurements.json"
    results = json.loads(history.read_text()) if history.exists() else []
    for quantity in (500, 750):
        key = "latency-" + str(uuid4())
        record = {
            "evidence_mode": "actual_loopback_model_real_mcp",
            "quantity_kg": quantity,
            "started_at": datetime.now(UTC).isoformat(),
            "model_warming": "Existing model service reused; no scripted substitute or fixture fallback",
        }

        def call(path, payload=None):
            request = urllib.request.Request(
                BASE + path,
                data=None if payload is None else json.dumps(payload).encode(),
                headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, json.load(response)

        start = time.monotonic()
        _, run = call(
            "/api/v1/requests",
            {
                "idempotency_key": key,
                "quantity_kg": quantity,
                "commodity": "demo-maize",
                "variant": "dry-demo",
                "grade": "DEMO-1",
                "origin": "synthetic-region",
                "sale_basis": "wholesale",
                "as_of_date": "2026-10-10",
                "markets": "Market A and Market B",
            },
        )
        workflow = run["workflow_id"]
        print(json.dumps({"started": workflow, "quantity": quantity}), flush=True)
        while time.monotonic() - start < 910:
            _, run = call(f"/api/v1/runs/{workflow}")
            if run["status"] != "RUNNING":
                break
            time.sleep(1)
        record.update(
            workflow_id=workflow,
            measured_start_to_review_seconds=round(time.monotonic() - start, 3),
            result=run,
        )
        _, activity = call(f"/api/v1/runs/{workflow}/events")
        record["actual_sanitized_events"] = activity["events"]
        if run["status"] == "PENDING_REVIEW":
            expected = [f"{quantity * 40 - 2000:.2f}", f"{quantity * 45 - 8000:.2f}"]
            record["arithmetic_pass"] = [
                m["estimated_net_proceeds"] for m in run["comparison"]["markets"]
            ] == expected
            _, decision = call(
                f"/api/v1/runs/{workflow}/decisions",
                {
                    "draft_id": run["draft_id"],
                    "version": run["version"],
                    "content_hash": run["content_hash"],
                    "decision": "approve",
                    "idempotency_key": "rehearsal-review-" + key,
                    "note": "Authorized synthetic rehearsal; demo identity, no independent practitioner review.",
                },
            )
            record["authenticated_demo_decision"] = decision
            record["measured_start_to_approval_seconds"] = round(time.monotonic() - start, 3)
        results.append(record)
        (ROOT / "evals/results/I01.13-compact-live-measurements.json").write_text(
            json.dumps(results, indent=2) + "\n"
        )
        print(
            json.dumps(
                {
                    "workflow": workflow,
                    "status": run["status"],
                    "seconds": record["measured_start_to_review_seconds"],
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
