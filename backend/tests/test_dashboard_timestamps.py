"""Persisted timestamp mapping, historical absence and polling stability."""

import sqlite3

from backend.app.services.draft_store import DraftStore
from backend.tests.test_review_api import auth, body, setup


def test_run_times_survive_retries_polling_and_restart(tmp_path, monkeypatch):
    db = tmp_path / "times.sqlite"
    store = DraftStore(str(db))
    monkeypatch.setattr("backend.app.services.draft_store.now", lambda: "2026-10-14T22:00:00Z")
    start = store.create_run("new", "test:officer", {"quantity_kg": 650})
    assert start["started_at"] == "2026-10-14T22:00:00Z"
    assert start["completed_at"] is None
    monkeypatch.setattr("backend.app.services.draft_store.now", lambda: "2026-10-14T22:02:00Z")
    store.update_run("new", "PENDING_REVIEW")
    assert store.run("new")["completed_at"] is None
    store.update_run("new", "COMPLETED")
    monkeypatch.setattr("backend.app.services.draft_store.now", lambda: "2026-10-15T10:00:00Z")
    restarted = DraftStore(str(db))
    restarted.update_run("new", "COMPLETED")
    retry = restarted.create_run("new", "test:officer", {"quantity_kg": 650})
    assert retry["started_at"] == start["started_at"]
    assert retry["completed_at"] == "2026-10-14T22:02:00Z"
    restarted.create_run("failed", "test:officer", {})
    restarted.update_run("failed", "FAILED", "test_failure")
    assert restarted.run("failed")["completed_at"] == "2026-10-15T10:00:00Z"


def test_legacy_migration_does_not_invent_times(tmp_path):
    db = tmp_path / "legacy.sqlite"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE runs(workflow_id TEXT PRIMARY KEY,owner_id TEXT NOT NULL,"
            "request_json TEXT NOT NULL,request_hash TEXT NOT NULL,status TEXT NOT NULL,"
            "error_code TEXT,updated_at TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO runs VALUES('old','test:officer','{}','hash','COMPLETED',"
            "NULL,'2026-10-10T00:00:00Z')"
        )
    store = DraftStore(str(db))
    store.update_run("old", "COMPLETED")
    assert store.run("old")["started_at"] is None
    assert store.run("old")["completed_at"] is None


def test_api_maps_exact_draft_and_decision_times_without_modifying_content(tmp_path):
    db, pending, client = setup(tmp_path)
    store = DraftStore(str(db))
    original = store.current_draft("allowed")
    before = client.get("/api/v1/runs/allowed", headers=auth()).json()
    assert before["advisory_created_at"] == original["created_at"]
    assert before["started_at"] is None  # deterministic replay has no workflow clock
    assert before["completed_at"] is None
    assert before["officer_decision_at"] is None
    decision = client.post(
        "/api/v1/runs/allowed/decisions", headers=auth(), json=body(pending)
    ).json()["decision"]
    after = client.get("/api/v1/runs/allowed", headers=auth()).json()
    assert after["officer_decision_at"] == decision["decided_at"]
    assert after["officer_decision"] == "approve"
    assert after["advisory_created_at"] == original["created_at"]
    assert store.current_draft("allowed")["content_hash"] == original["content_hash"]
    assert after["completed_at"] is None  # replay had no persisted HTTP run record
    assert after["comparison"]["as_of_date"] == "2026-10-10"
