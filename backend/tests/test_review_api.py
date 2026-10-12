"""HTTP officer boundary over a real paused synthetic MCP workflow."""

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.api.review import create_app
from backend.app.services.draft_store import DraftStore
from backend.tests.test_integrated_workflow import mocked_pipeline
from backend.tests.test_model_workflow import ScriptedProvider

ROOT = Path(__file__).resolve().parents[2]


def paused(db: Path, workflow: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backend.app.agent.draft_recovery",
            "--db",
            str(db),
            "start",
            "--workflow-id",
            workflow,
            "--idempotency-key",
            "create-v1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return next(
        row["interrupt"]
        for line in result.stdout.splitlines()
        if line.startswith("{") and (row := json.loads(line))["event"] == "workflow_paused"
    )


def setup(tmp_path: Path):
    db = tmp_path / "state.sqlite"
    pending = paused(db, "allowed")
    paused(db, "other")
    config = tmp_path / ".env.officers.local"
    config.write_text(
        json.dumps(
            {
                "officers": [
                    {
                        "id": "test:officer-a",
                        "token_sha256": hashlib.sha256(b"secret-a").hexdigest(),
                        "workflows": ["allowed"],
                    },
                    {
                        "id": "test:officer-b",
                        "token_sha256": hashlib.sha256(b"secret-b").hexdigest(),
                        "workflows": ["other"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    client = TestClient(create_app(db, config))
    return db, pending, client


def body(pending: dict, decision="approve", key="review-v1", **changes):
    return {
        "draft_id": pending["draft_id"],
        "version": pending["version"],
        "content_hash": pending["content_hash"],
        "decision": decision,
        "idempotency_key": key,
        "note": "Synthetic local API test",
        **changes,
    }


def auth(token="secret-a"):
    return {"Authorization": f"Bearer {token}"}


def test_auth_access_spoof_and_validation(tmp_path):
    db, pending, client = setup(tmp_path)
    path = "/api/v1/runs/allowed/decisions"
    assert client.get("/api/v1/drafts/pending").status_code == 401
    assert client.get("/api/v1/drafts/pending", headers=auth("wrong")).status_code == 401
    assert client.get("/api/v1/runs/allowed", headers=auth("secret-b")).status_code == 403
    assert client.get("/api/v1/runs/other/draft", headers=auth()).status_code == 403
    assert client.post(path, json=body(pending), headers=auth("wrong")).status_code == 401
    assert client.post(path, json=body(pending), headers=auth("secret-b")).status_code == 403
    assert (
        client.post(path, json=body(pending, reviewer_id="spoofed"), headers=auth()).status_code
        == 422
    )
    assert client.post(path, json=body(pending, role="officer"), headers=auth()).status_code == 422
    assert client.post(path, json=body(pending, note="x" * 501), headers=auth()).status_code == 422
    listed = client.get("/api/v1/drafts/pending", headers=auth()).json()["drafts"]
    assert [item["workflow_id"] for item in listed] == ["allowed"]
    assert listed[0]["content"]["calculation"]
    assert listed[0]["content"]["quote_references"]
    assert DraftStore(str(db)).counts("allowed")["decisions"] == 0


@pytest.mark.parametrize(
    "decision,outcome,status",
    [
        ("approve", "approved_internal_review", "APPROVED"),
        ("reject", "rejected", "REJECTED"),
    ],
)
def test_decision_retry_conflict_and_status(tmp_path, decision, outcome, status):
    db, pending, client = setup(tmp_path)
    path = "/api/v1/runs/allowed/decisions"
    payload = body(pending, decision)
    response = client.post(path, json=payload, headers=auth())
    assert response.status_code == 200, response.text
    assert response.json()["outcome"] == outcome
    assert response.json()["decision"]["reviewer_id"] == "test:officer-a"
    counts = DraftStore(str(db)).counts("allowed")
    assert counts == {"drafts": 1, "actions": 1, "decisions": 1, "audit": 2}
    assert client.post(path, json=payload, headers=auth()).json() == response.json()
    assert DraftStore(str(db)).counts("allowed") == counts
    assert (
        client.post(
            path,
            json=body(pending, "reject" if decision == "approve" else "approve"),
            headers=auth(),
        ).status_code
        == 409
    )
    assert (
        client.post(path, json=body(pending, decision, "different"), headers=auth()).status_code
        == 409
    )
    run = client.get("/api/v1/runs/allowed", headers=auth()).json()
    assert (run["outcome"], run["draft_status"], run["pending_nodes"]) == (outcome, status, [])
    with sqlite3.connect(db) as connection:
        events = [
            r[0]
            for r in connection.execute(
                "SELECT event_type FROM audit WHERE workflow_id='allowed' ORDER BY event_id"
            )
        ]
    assert events == ["draft_created", "officer_review_decision"]


def test_stale_and_concurrent_decisions(tmp_path):
    db, pending, client = setup(tmp_path)
    store = DraftStore(str(db))
    store.create_run("allowed", "test:officer-a", {"synthetic": True})
    store.update_run("allowed", "PENDING_REVIEW")
    path = "/api/v1/runs/allowed/decisions"
    assert (
        client.post(path, json=body(pending, content_hash="0" * 64), headers=auth()).status_code
        == 409
    )
    assert client.post(path, json=body(pending, version=2), headers=auth()).status_code == 409
    assert store.run("allowed")["status"] == "PENDING_REVIEW"
    assert store.counts("allowed")["decisions"] == 0
    # A running single-worker ASGI service has one event loop for all requests.
    with client, ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda choice: (
                    client.post(
                        path, json=body(pending, choice, choice), headers=auth()
                    ).status_code
                ),
                ["approve", "reject"],
            )
        )
    assert sorted(results) == [200, 409]
    assert DraftStore(str(db)).counts("allowed")["decisions"] == 1


def test_committed_decision_recovers_on_status_request(tmp_path, monkeypatch):
    db, pending, client = setup(tmp_path)
    import backend.app.api.review as module

    original = module.resume_stored_workflow

    async def interrupted(*_args):
        raise RuntimeError("synthetic interruption after decision commit")

    monkeypatch.setattr(module, "resume_stored_workflow", interrupted)
    with pytest.raises(RuntimeError, match="synthetic interruption"):
        client.post("/api/v1/runs/allowed/decisions", json=body(pending), headers=auth())
    assert DraftStore(str(db)).counts("allowed")["decisions"] == 1
    monkeypatch.setattr(module, "resume_stored_workflow", original)
    restarted = TestClient(create_app(db, tmp_path / ".env.officers.local"))
    assert (
        restarted.get("/api/v1/runs/allowed", headers=auth()).json()["outcome"]
        == "approved_internal_review"
    )
    assert DraftStore(str(db)).counts("allowed")["audit"] == 2


def test_superseded_draft_rejected(tmp_path):
    db, pending, client = setup(tmp_path)
    DraftStore(str(db)).revise("allowed", "revision-v1")
    assert (
        client.post(
            "/api/v1/runs/allowed/decisions", json=body(pending), headers=auth()
        ).status_code
        == 409
    )
    assert DraftStore(str(db)).counts("allowed")["decisions"] == 0


@pytest.mark.parametrize(
    "choice,outcome",
    [
        ("approve", "approved_internal_review"),
        ("reject", "rejected"),
    ],
)
def test_http_start_to_review_uses_real_mcp_with_mocked_http_and_model(
    tmp_path, monkeypatch, choice, outcome
):
    provider = mocked_pipeline(monkeypatch, provider=ScriptedProvider(quantity="500"))
    db = tmp_path / "end-to-end.sqlite"
    config = tmp_path / ".env.officers.local"
    config.write_text(
        json.dumps(
            {
                "officers": [
                    {
                        "id": "test:demo-officer",
                        "token_sha256": hashlib.sha256(b"test-token").hexdigest(),
                        "workflows": [],
                        "workflow_prefix": "demo-",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    request = {
        "idempotency_key": "request-v1",
        "quantity_kg": 500,
        "commodity": "demo-maize",
        "variant": "dry-demo",
        "grade": "DEMO-1",
        "origin": "synthetic-region",
        "sale_basis": "wholesale",
        "as_of_date": "2026-10-10",
        "markets": "Market A and Market B",
    }
    app = create_app(db, config)
    with TestClient(app) as client:
        headers = auth("test-token")
        started = client.post("/api/v1/requests", json=request, headers=headers)
        assert started.status_code == 202, started.text
        workflow = started.json()["workflow_id"]
        assert (
            client.post("/api/v1/requests", json=request, headers=headers).json() == started.json()
        )
        assert (
            client.post(
                "/api/v1/requests", json={**request, "quantity_kg": 600}, headers=headers
            ).status_code
            == 409
        )
        path = f"/api/v1/runs/{workflow}"
        for _ in range(100):
            result = client.get(path, headers=headers).json()
            if result["status"] != "RUNNING":
                break
            time.sleep(0.1)
        assert result["status"] == "PENDING_REVIEW", result
        assert len(provider.requests) == 3
        assert result["comparison"]["markets"][0]["estimated_net_proceeds"] == "18000.00"
        assert result["retrieval_provenance"]["http"][0]["mocked_http"] is True
        assert client.get(path + "/events").status_code == 401
        assert client.get("/api/v1/runs/other/events", headers=headers).status_code == 403
        activity = client.get(path + "/events", headers=headers).json()["events"]
        completed = [
            e["tool"] for e in activity if e["phase"] == "completed" and e["server"] == "own MCP"
        ]
        assert completed == [
            "search_market_quotes",
            "compare_market_options",
            "save_advisory_draft",
        ]
        assert "test-token" not in json.dumps(activity)
        assert client.get("/api/v1/drafts/pending", headers=headers).json()["reviewer"] == {
            "id": "test:demo-officer",
            "demo": True,
        }
        draft = client.get(path + "/draft", headers=headers).json()
        payload = body(draft, choice)
        decided = client.post(path + "/decisions", json=payload, headers=headers)
        assert decided.status_code == 200, decided.text
        assert decided.json()["outcome"] == outcome
        assert client.get(path, headers=headers).json()["status"] == "COMPLETED"
        assert DraftStore(str(db)).counts(workflow)["decisions"] == 1
    with TestClient(create_app(db, config)) as restarted:
        assert restarted.get(path + "/events", headers=headers).json()["events"] == activity


def test_http_failed_retrieval_is_visible_without_draft(tmp_path, monkeypatch):
    provider = mocked_pipeline(monkeypatch, case="unavailable")
    db = tmp_path / "failed.sqlite"
    config = tmp_path / ".env.officers.local"
    config.write_text(
        json.dumps(
            {
                "officers": [
                    {
                        "id": "test:demo-officer",
                        "token_sha256": hashlib.sha256(b"test-token").hexdigest(),
                        "workflows": [],
                        "workflow_prefix": "demo-",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    request = {
        "idempotency_key": "failed-v1",
        "quantity_kg": 1000,
        "commodity": "demo-maize",
        "variant": "dry-demo",
        "grade": "DEMO-1",
        "origin": "synthetic-region",
        "sale_basis": "wholesale",
        "as_of_date": "2026-10-10",
        "markets": "Market A and Market B",
    }
    with TestClient(create_app(db, config)) as client:
        workflow = client.post("/api/v1/requests", json=request, headers=auth("test-token")).json()[
            "workflow_id"
        ]
        for _ in range(100):
            run = client.get(f"/api/v1/runs/{workflow}", headers=auth("test-token")).json()
            if run["status"] != "RUNNING":
                break
            time.sleep(0.1)
        assert run["status"] == "FAILED"
        assert run["error_code"] == "borrowed_retrieval_failed"
        assert DraftStore(str(db)).counts(workflow)["drafts"] == 0
        assert provider.requests == []


def test_committed_start_recovers_after_api_restart(tmp_path, monkeypatch):
    provider = mocked_pipeline(monkeypatch, provider=ScriptedProvider(quantity="500"))
    db = tmp_path / "restart-start.sqlite"
    config = tmp_path / ".env.officers.local"
    config.write_text(
        json.dumps(
            {
                "officers": [
                    {
                        "id": "test:demo-officer",
                        "token_sha256": hashlib.sha256(b"test-token").hexdigest(),
                        "workflows": [],
                        "workflow_prefix": "demo-",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    request = {
        "idempotency_key": "persisted-before-start",
        "quantity_kg": 500,
        "commodity": "demo-maize",
        "variant": "dry-demo",
        "grade": "DEMO-1",
        "origin": "synthetic-region",
        "sale_basis": "wholesale",
        "as_of_date": "2026-10-10",
        "markets": "Market A and Market B",
    }
    workflow = "demo-persisted-before-graph"
    DraftStore(str(db)).create_run(workflow, "test:demo-officer", request)
    with TestClient(create_app(db, config)) as client:
        for _ in range(100):
            run = client.get(f"/api/v1/runs/{workflow}", headers=auth("test-token")).json()
            if run["status"] != "RUNNING":
                break
            time.sleep(0.1)
        assert run["status"] == "PENDING_REVIEW", run
        assert len(provider.requests) == 3
        assert DraftStore(str(db)).counts(workflow)["drafts"] == 1
