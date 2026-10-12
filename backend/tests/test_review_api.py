"""HTTP officer boundary over a real paused synthetic MCP workflow."""

import hashlib
import json
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.api.review import create_app
from backend.app.services.draft_store import DraftStore

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
    path = "/api/v1/runs/allowed/decisions"
    assert (
        client.post(path, json=body(pending, content_hash="0" * 64), headers=auth()).status_code
        == 409
    )
    assert client.post(path, json=body(pending, version=2), headers=auth()).status_code == 409
    with ThreadPoolExecutor(max_workers=2) as pool:
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
