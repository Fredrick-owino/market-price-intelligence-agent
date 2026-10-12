"""Real checkpoints/review/MCP retrieval, gated synthetic model failures."""

import asyncio
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from uuid import NAMESPACE_URL, uuid5

import httpx
import pytest

from backend.app.agent import draft_recovery
from backend.app.api.review import create_app
from backend.app.services.draft_store import DraftStore, StoreConflict
from backend.tests.test_integrated_workflow import mocked_pipeline
from backend.tests.test_review_api import auth, body, paused


def test_concurrent_start_admission_is_atomic_and_retry_safe(tmp_path):
    store = DraftStore(str(tmp_path / "admission.sqlite"))

    def start(workflow):
        try:
            return store.create_run(
                workflow, "test:officer", {"quantity": 500}, reject_if_running=True
            )
        except StoreConflict:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(start, ["demo-first", "demo-second"]))
    accepted = [r for r in results if r is not None]
    assert len(accepted) == 1
    workflow = accepted[0]["workflow_id"]
    assert start(workflow) == accepted[0]
    with pytest.raises(StoreConflict):
        store.create_run(workflow, "test:officer", {"quantity": 600}, reject_if_running=True)
    other = "demo-second" if workflow == "demo-first" else "demo-first"
    assert store.run(other) is None
    store.update_run(workflow, "FAILED", "synthetic_failure")
    assert start(other)["status"] == "RUNNING"


@pytest.mark.asyncio
@pytest.mark.parametrize("recover_committed_starts", [False, True])
async def test_model_queue_preserves_responsive_review_and_idempotent_retries(
    tmp_path, monkeypatch, recover_committed_starts
):
    db = tmp_path / "concurrency.sqlite"
    pending = paused(db, "demo-review")
    config = tmp_path / ".env.officers.local"
    config.write_text(
        json.dumps(
            {
                "officers": [
                    {
                        "id": "test:queue-officer",
                        "token_sha256": hashlib.sha256(b"queue-token").hexdigest(),
                        "workflows": [],
                        "workflow_prefix": "demo-",
                    }
                ]
            }
        )
    )
    mocked_pipeline(monkeypatch)
    entered = asyncio.Event()
    release = asyncio.Event()
    active = 0
    peak = 0
    calls = []

    async def gated_failure(workflow, *args, **kwargs):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        calls.append(workflow)
        try:
            if len(calls) == 1:
                entered.set()
                await release.wait()
            raise RuntimeError("Synthetic model failure; verifies slot release")
        finally:
            active -= 1

    monkeypatch.setattr(draft_recovery, "model_exchange", gated_failure)
    request = {
        "idempotency_key": "first",
        "quantity_kg": 500,
        "commodity": "demo-maize",
        "variant": "dry-demo",
        "grade": "DEMO-1",
        "origin": "synthetic-region",
        "sale_basis": "wholesale",
        "as_of_date": "2026-10-10",
        "markets": "Market A and Market B",
    }
    headers = auth("queue-token")
    store = DraftStore(str(db))
    ids = []
    if recover_committed_starts:
        for key in ["first", "second"]:
            workflow = "demo-" + str(uuid5(NAMESPACE_URL, f"sokosignal:test:queue-officer:{key}"))
            store.create_run(workflow, "test:queue-officer", {**request, "idempotency_key": key})
            ids.append(workflow)
    transport = httpx.ASGITransport(app=create_app(db, config))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            if recover_committed_starts:
                await client.get(f"/api/v1/runs/{ids[0]}", headers=headers)
            else:
                started = await client.post("/api/v1/requests", json=request, headers=headers)
                assert started.status_code == 202
                ids.append(started.json()["workflow_id"])
            await asyncio.wait_for(entered.wait(), 15)
            second_request = {**request, "idempotency_key": "second"}
            second = await client.post("/api/v1/requests", json=second_request, headers=headers)
            if recover_committed_starts:
                assert second.status_code == 202
                assert second.json()["workflow_id"] == ids[1]
            else:
                assert second.status_code == 409
                assert "already running" in second.json()["detail"]
                with store.connect() as connection:
                    assert connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1

            # An API backlog must not block polling, auth failures or real review.
            async with asyncio.timeout(3):
                for _ in range(3):
                    for index, workflow in enumerate(ids):
                        status = await client.get(f"/api/v1/runs/{workflow}", headers=headers)
                        assert status.json()["status"] == "RUNNING"
                        assert status.json()["phase"] == [
                            "retrieval_and_model" if index == 0 else "queued_for_model"
                        ]
                    retry = await client.post("/api/v1/requests", json=request, headers=headers)
                    assert retry.status_code == 202 and retry.json()["workflow_id"] == ids[0]
                conflict = await client.post(
                    "/api/v1/requests", json={**request, "quantity_kg": 600}, headers=headers
                )
                assert conflict.status_code == 409
                assert (await client.get("/api/v1/drafts/pending")).status_code == 401
                listed = await client.get("/api/v1/drafts/pending", headers=headers)
                assert len(listed.json()["drafts"]) == 1
                decided = await client.post(
                    "/api/v1/runs/demo-review/decisions", json=body(pending), headers=headers
                )
                assert decided.status_code == 200
                assert decided.json()["outcome"] == "approved_internal_review"
                retry = await client.post(
                    "/api/v1/runs/demo-review/decisions", json=body(pending), headers=headers
                )
                assert retry.status_code == 200
                assert store.counts("demo-review")["decisions"] == 1
            assert calls == [ids[0]] and peak == 1
        finally:
            release.set()
            # Drain both tasks so failure must release the slot for the second run.
            async with asyncio.timeout(20):
                while any(store.run(workflow)["status"] == "RUNNING" for workflow in ids):
                    await asyncio.sleep(0.05)
        if not recover_committed_starts:
            second = await client.post("/api/v1/requests", json=second_request, headers=headers)
            assert second.status_code == 202
            ids.append(second.json()["workflow_id"])
            async with asyncio.timeout(20):
                while store.run(ids[1])["status"] == "RUNNING":
                    await asyncio.sleep(0.05)
        assert calls == ids and peak == 1 and active == 0
        assert all(store.run(workflow)["status"] == "FAILED" for workflow in ids)
        assert all(store.counts(workflow)["drafts"] == 0 for workflow in ids)
        assert len({workflow for workflow in calls}) == 2
