"""Bounded local HTTP review for synthetic private drafts."""

import asyncio
import hashlib
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal
from uuid import NAMESPACE_URL, uuid5

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel, ConfigDict, Field

from backend.app.agent.demo_events import sink
from backend.app.agent.draft_recovery import (
    build_graph,
    resume_stored_workflow,
    workflow_snapshot,
)
from backend.app.agent.model_workflow import task_for
from backend.app.services.draft_store import DraftStore, StoreConflict


class DecisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str = Field(min_length=1, max_length=100)
    version: int = Field(ge=1)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    decision: Literal["approve", "reject"]
    idempotency_key: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$")
    note: str = Field(default="", max_length=500)


class StartInput(BaseModel):
    """Only the supported synthetic comparison; whole kg vary within capacity."""

    model_config = ConfigDict(extra="forbid")

    idempotency_key: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$")
    quantity_kg: int = Field(ge=1, le=1000)
    commodity: Literal["demo-maize"]
    variant: Literal["dry-demo"]
    grade: Literal["DEMO-1"]
    origin: Literal["synthetic-region"]
    sale_basis: Literal["wholesale"]
    as_of_date: Literal["2026-10-10"]
    markets: Literal["Market A and Market B"]


def load_officers(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    officers = data["officers"]
    if not isinstance(officers, list) or not officers:
        raise ValueError("At least one local officer is required.")
    seen = set()
    for officer in officers:
        if not {"id", "token_sha256", "workflows"} <= set(officer) or set(officer) - {
            "id",
            "token_sha256",
            "workflows",
            "workflow_prefix",
        }:
            raise ValueError("Officer config has invalid fields.")
        if (
            not isinstance(officer["id"], str)
            or not officer["id"]
            or officer["id"].startswith("simulated:")
            or not isinstance(officer["workflows"], list)
            or (not officer["workflows"] and not officer.get("workflow_prefix"))
            or not all(isinstance(value, str) and value for value in officer["workflows"])
            or not isinstance(officer["token_sha256"], str)
            or len(officer["token_sha256"]) != 64
            or any(c not in "0123456789abcdef" for c in officer["token_sha256"])
            or officer["id"] in seen
            or not isinstance(officer.get("workflow_prefix", ""), str)
            or len(officer.get("workflow_prefix", "")) > 20
            or any(
                c not in "abcdefghijklmnopqrstuvwxyz0123456789-"
                for c in officer.get("workflow_prefix", "")
            )
        ):
            raise ValueError("Officer config is invalid.")
        seen.add(officer["id"])
    if len({officer["token_sha256"] for officer in officers}) != len(officers):
        raise ValueError("Officer token verifiers must be unique.")
    prefixes = [
        officer["workflow_prefix"] for officer in officers if officer.get("workflow_prefix")
    ]
    if any(a.startswith(b) for a in prefixes for b in prefixes if a != b) or len(
        set(prefixes)
    ) != len(prefixes):
        raise ValueError("Officer workflow prefixes must not overlap.")
    return officers


def create_app(db_path: Path, officers_path: Path) -> FastAPI:
    officers = load_officers(officers_path)
    store = DraftStore(str(db_path))
    app = FastAPI(title="SokoSignal local officer review", version="1")
    locks: dict[str, asyncio.Lock] = {}
    active_tasks: dict[str, asyncio.Task] = {}
    live_events: dict[str, list[dict]] = {}
    model_slot = asyncio.Lock()
    active_model_workflow: str | None = None

    @asynccontextmanager
    async def workflow_lock(workflow_id: str):
        lock = locks.setdefault(workflow_id, asyncio.Lock())
        async with lock:
            yield

    @asynccontextmanager
    async def model_execution(workflow_id: str):
        """One model workflow per API process; queued runs never hold review locks."""
        nonlocal active_model_workflow
        async with model_slot:
            active_model_workflow = workflow_id
            try:
                yield
            finally:
                active_model_workflow = None

    def authenticate(authorization: str | None = Header(default=None)) -> dict:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                401, "Bearer credential required", headers={"WWW-Authenticate": "Bearer"}
            )
        token = authorization[7:]
        if not token or len(token) > 256:
            raise HTTPException(401, "Invalid credential", headers={"WWW-Authenticate": "Bearer"})
        digest = hashlib.sha256(token.encode()).hexdigest()
        match = None
        for officer in officers:
            if secrets.compare_digest(digest, officer["token_sha256"]):
                match = officer
        if match is None:
            raise HTTPException(401, "Invalid credential", headers={"WWW-Authenticate": "Bearer"})
        return {
            "id": match["id"],
            "workflows": tuple(match["workflows"]),
            "workflow_prefix": match.get("workflow_prefix", ""),
        }

    def allow(workflow_id: str, officer: dict) -> None:
        if workflow_id not in officer["workflows"] and not (
            officer["workflow_prefix"] and workflow_id.startswith(officer["workflow_prefix"])
        ):
            raise HTTPException(403, "Workflow access denied")

    async def drive_graph(workflow_id: str) -> None:
        """Resume checkpoints after a process restart; one local API worker only."""
        async with model_execution(workflow_id), workflow_lock(workflow_id):
            run = await asyncio.to_thread(store.run, workflow_id)
            if run is None or run["status"] != "RUNNING":
                return
            request = json.loads(run["request_json"])
            config = {"configurable": {"thread_id": workflow_id}}
            try:
                async with AsyncSqliteSaver.from_conn_string(str(db_path)) as saver:
                    app_graph = build_graph(
                        db_path, request_timeout_seconds=300, total_run_timeout_seconds=900
                    ).compile(checkpointer=saver)
                    snapshot = await app_graph.aget_state(config)
                    if snapshot.values.get("draft"):
                        await asyncio.to_thread(store.update_run, workflow_id, "PENDING_REVIEW")
                        return
                    if snapshot.values.get("outcome") == "model_failed":
                        await asyncio.to_thread(
                            store.update_run,
                            workflow_id,
                            "FAILED",
                            snapshot.values.get("failure_code"),
                        )
                        return
                    if snapshot.next:
                        result = await app_graph.ainvoke(None, config)
                    else:
                        result = await app_graph.ainvoke(
                            {
                                "workflow_id": workflow_id,
                                "idempotency_key": request["idempotency_key"],
                                "mode": "integrated",
                                "user_task": task_for(str(request["quantity_kg"])),
                                "quantity": str(request["quantity_kg"]),
                            },
                            config,
                        )
                if result.get("outcome") == "model_failed":
                    await asyncio.to_thread(
                        store.update_run, workflow_id, "FAILED", result.get("failure_code")
                    )
                elif result.get("draft"):
                    await asyncio.to_thread(store.update_run, workflow_id, "PENDING_REVIEW")
                else:
                    await asyncio.to_thread(
                        store.update_run, workflow_id, "FAILED", "missing_review_pause"
                    )
            except Exception as error:  # noqa: BLE001 — never expose provider/HTTP diagnostics
                await asyncio.to_thread(
                    store.update_run, workflow_id, "FAILED", type(error).__name__
                )

    async def drive(workflow_id: str) -> None:
        events = live_events.setdefault(workflow_id, [])

        def receive(row):
            if len(events) < 100:
                events.append(row)

        token = sink.set(receive)
        try:
            await drive_graph(workflow_id)
        finally:
            sink.reset(token)
            if events:
                await asyncio.to_thread(store.save_events, workflow_id, events)

    def schedule(workflow_id: str) -> None:
        prior = active_tasks.get(workflow_id)
        if prior is None or prior.done():
            task = asyncio.create_task(drive(workflow_id))
            active_tasks[workflow_id] = task

    async def reconcile(workflow_id: str) -> None:
        current = await asyncio.to_thread(store.current_draft, workflow_id)
        if current is None or current["status"] not in {"APPROVED", "REJECTED"}:
            return
        try:
            await asyncio.to_thread(store.decision, workflow_id)
        except StoreConflict:
            return
        try:
            await resume_stored_workflow(db_path, workflow_id)
        except StoreConflict as error:
            raise HTTPException(409, str(error)) from error

    @app.get("/health")
    def health():
        return {"status": "ready"}

    Officer = Annotated[dict, Depends(authenticate)]

    @app.get("/api/v1/drafts/pending")
    def pending(officer: Officer):
        return {
            "reviewer": {"id": officer["id"], "demo": officer["id"].startswith("test:")},
            "drafts": store.pending_drafts(
                frozenset(officer["workflows"]), officer["workflow_prefix"]
            ),
        }

    @app.post("/api/v1/requests", status_code=202)
    async def start(body: StartInput, officer: Officer):
        prefix = officer["workflow_prefix"]
        if not prefix:
            raise HTTPException(403, "Officer cannot start workflows")
        workflow_id = prefix + str(
            uuid5(NAMESPACE_URL, f"sokosignal:{officer['id']}:{body.idempotency_key}")
        )
        try:
            run = await asyncio.to_thread(
                store.create_run,
                workflow_id,
                officer["id"],
                body.model_dump(),
                reject_if_running=True,
            )
        except StoreConflict as error:
            raise HTTPException(409, str(error)) from error
        if run["status"] == "RUNNING":
            schedule(workflow_id)
        return {"workflow_id": workflow_id, "status": run["status"]}

    @app.get("/api/v1/runs/{workflow_id}/draft")
    def draft(workflow_id: str, officer: Officer):
        allow(workflow_id, officer)
        result = store.current_draft(workflow_id)
        if result is None:
            raise HTTPException(404, "Draft not found")
        return result

    @app.get("/api/v1/runs/{workflow_id}/events")
    def events(workflow_id: str, officer: Officer):
        allow(workflow_id, officer)
        return {
            "events": list(live_events[workflow_id])
            if workflow_id in live_events
            else store.events(workflow_id)
        }

    @app.get("/api/v1/runs/{workflow_id}")
    async def status(workflow_id: str, officer: Officer):
        allow(workflow_id, officer)
        run = await asyncio.to_thread(store.run, workflow_id)
        if run is not None and run["status"] == "RUNNING":
            schedule(workflow_id)
            current = await asyncio.to_thread(store.current_draft, workflow_id)
            if current is None:
                return {
                    "workflow_id": workflow_id,
                    "status": "RUNNING",
                    "error_code": None,
                    "phase": [
                        "retrieval_and_model"
                        if active_model_workflow == workflow_id
                        else "queued_for_model"
                    ],
                    "outcome": None,
                }
        async with workflow_lock(workflow_id):
            result = await asyncio.to_thread(store.current_draft, workflow_id)
            if result is None and run is None:
                raise HTTPException(404, "Workflow not found")
            if result is not None:
                await reconcile(workflow_id)
            snapshot = await workflow_snapshot(db_path, workflow_id)
            result = await asyncio.to_thread(store.current_draft, workflow_id)
            run = await asyncio.to_thread(store.run, workflow_id)
            if result is None:
                return {
                    "workflow_id": workflow_id,
                    "status": run["status"],
                    "error_code": run["error_code"],
                    "phase": list(snapshot.next),
                    "outcome": snapshot.values.get("outcome"),
                }
            if run is not None and result["status"] in {"APPROVED", "REJECTED"}:
                await asyncio.to_thread(store.update_run, workflow_id, "COMPLETED")
            return {
                "workflow_id": workflow_id,
                "status": "COMPLETED"
                if result["status"] in {"APPROVED", "REJECTED"}
                else "PENDING_REVIEW",
                "draft_id": result["draft_id"],
                "version": result["version"],
                "content_hash": result["content_hash"],
                "draft_status": result["status"],
                "outcome": snapshot.values.get("outcome"),
                "pending_nodes": list(snapshot.next),
                "comparison": snapshot.values.get("comparison", {}).get("result"),
                "retrieval_provenance": result["content"].get("retrieval_provenance"),
            }

    @app.post("/api/v1/runs/{workflow_id}/decisions")
    async def decide(workflow_id: str, body: DecisionInput, officer: Officer):
        allow(workflow_id, officer)
        async with workflow_lock(workflow_id):
            current = await asyncio.to_thread(store.current_draft, workflow_id)
            if current is None:
                raise HTTPException(404, "Draft not found")
            snapshot = await workflow_snapshot(db_path, workflow_id)
            if (
                not snapshot.values
                or snapshot.values.get("draft", {}).get("draft_id") != current["draft_id"]
            ):
                raise HTTPException(409, "Checkpoint does not match current draft")
            if snapshot.next not in {("review_pause",), ("finalize",), ()}:
                raise HTTPException(409, "Workflow is not at its review gate")
            try:
                record = await asyncio.to_thread(
                    store.decide,
                    workflow_id,
                    body.draft_id,
                    body.version,
                    body.content_hash,
                    body.decision,
                    officer["id"],
                    body.idempotency_key,
                    body.note,
                    authenticated=True,
                )
                await resume_stored_workflow(db_path, workflow_id)
                await asyncio.to_thread(store.update_run, workflow_id, "COMPLETED")
            except StoreConflict as error:
                raise HTTPException(409, str(error)) from error
            snapshot = await workflow_snapshot(db_path, workflow_id)
            return {
                "decision": {key: value for key, value in record.items() if key != "reason"},
                "outcome": snapshot.values.get("outcome"),
            }

    frontend_dist = Path(__file__).resolve().parents[3] / "frontend/dist"
    if frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="demo-frontend")
    return app


def local_app() -> FastAPI:
    """Uvicorn factory. Configuration and state stay outside the repository."""
    config = os.environ.get("SOKOSIGNAL_OFFICERS_CONFIG")
    state = os.environ.get("SOKOSIGNAL_STATE_DB")
    if not config or not state:
        raise RuntimeError("Local officer config and state DB paths are required.")
    return create_app(Path(state), Path(config))
