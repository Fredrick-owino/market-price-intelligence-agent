"""Separate CLI processes exercise real MCP transport and durable LangGraph pause/resume."""

import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = [sys.executable, "-m", "backend.app.agent.draft_recovery"]


def run(db: Path, *args, expected=0):
    completed = subprocess.run(
        [*CLI, "--db", str(db), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == expected, (completed.stdout, completed.stderr)
    records = [json.loads(line) for line in completed.stdout.splitlines() if line.startswith("{")]
    return records


def start(db: Path, workflow: str, key="create-v1"):
    records = run(db, "start", "--workflow-id", workflow, "--idempotency-key", key)
    lifecycle = next(row for row in records if row["event"] == "mcp_server_lifecycle")
    assert lifecycle["client_session_closed"] is True
    assert lifecycle["server_process_gone"] is True
    event = next(row for row in records if row["event"] == "workflow_paused")
    return event["interrupt"]


def review(db: Path, pending: dict, decision="approve", **overrides):
    args = {
        "workflow-id": pending["workflow_id"],
        "draft-id": pending["draft_id"],
        "version": str(pending["version"]),
        "content-hash": pending["content_hash"],
        "reviewer-id": "simulated:officer-001",
        "decision-key": "review-v1",
        "decision": decision,
    }
    args.update(overrides)
    flat = [
        f"--{key}" if value is True else item
        for key, value in args.items()
        for item in ([value] if value is True else [f"--{key}", value])
    ]
    return run(db, "review", *flat)


def counts(db: Path, workflow: str) -> dict:
    with sqlite3.connect(db) as connection:
        return {
            table: connection.execute(
                f"SELECT count(*) FROM {table} WHERE workflow_id=?", (workflow,)
            ).fetchone()[0]
            for table in ("drafts", "actions", "decisions", "audit")
        }


def test_real_mcp_draft_survives_process_exit_and_approval_resume(tmp_path):
    db = tmp_path / "state.sqlite"
    workflow = f"wf-{uuid4()}"
    pending = start(db, workflow)
    assert pending["review_status"] == "PENDING_REVIEW"
    assert pending["reviewer_mode"] == "simulated command only"
    assert counts(db, workflow) == {"drafts": 1, "actions": 1, "decisions": 0, "audit": 1}
    # This invocation is a different OS process and reloads the SQLite checkpoint.
    records = review(db, pending)
    resumed = next(row for row in records if row["event"] == "workflow_resumed")
    assert resumed["outcome"] == "approved_internal_review"
    assert resumed["persistent_counts"] == {"drafts": 1, "actions": 1, "decisions": 1, "audit": 2}
    assert counts(db, workflow)["decisions"] == 1
    replay = review(db, pending)
    assert replay[-1]["event"] == "workflow_replay_noop"
    assert counts(db, workflow) == resumed["persistent_counts"]


def test_rejection_has_no_approved_advisory(tmp_path):
    db = tmp_path / "reject.sqlite"
    workflow = f"wf-{uuid4()}"
    pending = start(db, workflow)
    records = review(db, pending, "reject")
    assert (
        next(row for row in records if row["event"] == "workflow_resumed")["outcome"] == "rejected"
    )
    with sqlite3.connect(db) as connection:
        status = connection.execute(
            "SELECT status FROM drafts WHERE workflow_id=?", (workflow,)
        ).fetchone()[0]
    assert status == "REJECTED"


@pytest.mark.parametrize(
    "overrides",
    [
        {"reviewer-id": ""},
        {"reviewer-id": "model:assistant"},
        {"workflow-id": "wrong-workflow"},
        {"draft-id": "wrong-draft"},
        {"version": "99"},
        {"content-hash": "0" * 64},
    ],
)
def test_invalid_reviewer_binding_and_stale_hash_rejected(tmp_path, overrides):
    db = tmp_path / f"reject-{uuid4()}.sqlite"
    workflow = f"wf-{uuid4()}"
    pending = start(db, workflow)
    try:
        review(db, pending, **overrides)
    except AssertionError as error:
        assert error.args[0][0] != 0
    else:
        raise AssertionError("invalid review unexpectedly succeeded")
    assert counts(db, workflow)["decisions"] == 0


def test_missing_reviewer_identity_is_rejected_by_explicit_command(tmp_path):
    db = tmp_path / "missing-identity.sqlite"
    workflow = f"wf-{uuid4()}"
    pending = start(db, workflow)
    completed = subprocess.run(
        [
            *CLI,
            "--db",
            str(db),
            "review",
            "--workflow-id",
            workflow,
            "--draft-id",
            pending["draft_id"],
            "--version",
            str(pending["version"]),
            "--content-hash",
            pending["content_hash"],
            "--decision-key",
            "missing-identity",
            "--decision",
            "approve",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 2
    assert "--reviewer-id" in completed.stderr
    assert counts(db, workflow)["decisions"] == 0


def test_revision_invalidates_old_approval_and_exact_new_version_resumes(tmp_path):
    db = tmp_path / "revision.sqlite"
    workflow = f"wf-{uuid4()}"
    old = start(db, workflow)
    review(db, old)
    revised_args = ("revise", "--workflow-id", workflow, "--idempotency-key", "revision-v1")
    revised = run(db, *revised_args)[0]["draft"]
    assert revised["version"] == old["version"] + 1
    count_after_revision = counts(db, workflow)
    assert run(db, *revised_args)[0]["draft"] == revised
    assert counts(db, workflow) == count_after_revision
    with pytest.raises(AssertionError):
        review(db, old)
    assert counts(db, workflow)["decisions"] == 1
    pending = {
        "workflow_id": workflow,
        **{key: revised[key] for key in ("draft_id", "version", "content_hash")},
    }
    records = review(db, pending, **{"decision-key": "review-v2"})
    assert (
        next(row for row in records if row["event"] == "workflow_resumed")["outcome"]
        == "approved_internal_review"
    )
    with sqlite3.connect(db) as connection:
        states = connection.execute(
            "SELECT version,status FROM drafts WHERE workflow_id=? ORDER BY version", (workflow,)
        ).fetchall()
    assert states == [(1, "SUPERSEDED"), (2, "APPROVED")]


def test_replay_and_conflicting_idempotency_key(tmp_path):
    db = tmp_path / "replay.sqlite"
    workflow = f"wf-{uuid4()}"
    pending = start(db, workflow)
    review(db, pending)
    before = counts(db, workflow)
    # Repeat the action through actual MCP, then replay the completed workflow.
    repeated = run(db, "replay-create", "--workflow-id", workflow, "--idempotency-key", "create-v1")
    assert repeated[-1]["event"] == "draft_creation_replay"
    assert repeated[-1]["draft"]["draft_id"] == pending["draft_id"]
    replayed = run(db, "start", "--workflow-id", workflow, "--idempotency-key", "create-v1")
    assert replayed[-1]["event"] == "workflow_replay_noop"
    assert replayed[-1]["outcome"] == "approved_internal_review"
    assert counts(db, workflow) == before
    conflict = run(db, "conflict", "--workflow-id", workflow, "--idempotency-key", "create-v1")
    assert conflict[-1]["event"] == "conflicting_mcp_retry"
    assert conflict[-1]["is_error"] is True
    assert "conflicts" in conflict[-1]["result"]["error"]["message"]
    assert counts(db, workflow) == before
