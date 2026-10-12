"""Bounded local HTTP review for synthetic private drafts."""

import asyncio
import hashlib
import json
import os
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from backend.app.agent.draft_recovery import resume_stored_workflow, workflow_snapshot
from backend.app.services.draft_store import DraftStore, StoreConflict


class DecisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str = Field(min_length=1, max_length=100)
    version: int = Field(ge=1)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    decision: Literal["approve", "reject"]
    idempotency_key: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$")
    note: str = Field(default="", max_length=500)


def load_officers(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    officers = data["officers"]
    if not isinstance(officers, list) or not officers:
        raise ValueError("At least one local officer is required.")
    seen = set()
    for officer in officers:
        if set(officer) != {"id", "token_sha256", "workflows"}:
            raise ValueError("Officer config has invalid fields.")
        if (
            not isinstance(officer["id"], str)
            or not officer["id"]
            or officer["id"].startswith("simulated:")
            or not isinstance(officer["workflows"], list)
            or not officer["workflows"]
            or not all(isinstance(value, str) and value for value in officer["workflows"])
            or not isinstance(officer["token_sha256"], str)
            or len(officer["token_sha256"]) != 64
            or any(c not in "0123456789abcdef" for c in officer["token_sha256"])
            or officer["id"] in seen
        ):
            raise ValueError("Officer config is invalid.")
        seen.add(officer["id"])
    if len({officer["token_sha256"] for officer in officers}) != len(officers):
        raise ValueError("Officer token verifiers must be unique.")
    return officers


def create_app(db_path: Path, officers_path: Path) -> FastAPI:
    officers = load_officers(officers_path)
    store = DraftStore(str(db_path))
    app = FastAPI(title="SokoSignal local officer review", version="1")
    locks: dict[str, threading.Lock] = {}

    @asynccontextmanager
    async def workflow_lock(workflow_id: str):
        lock = locks.setdefault(workflow_id, threading.Lock())
        await asyncio.to_thread(lock.acquire)
        try:
            yield
        finally:
            lock.release()

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
        return {"id": match["id"], "workflows": tuple(match["workflows"])}

    def allow(workflow_id: str, officer: dict) -> None:
        if workflow_id not in officer["workflows"]:
            raise HTTPException(403, "Workflow access denied")

    async def reconcile(workflow_id: str) -> None:
        current = store.current_draft(workflow_id)
        if current is None or current["status"] not in {"APPROVED", "REJECTED"}:
            return
        try:
            store.decision(workflow_id)
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
        return {"drafts": store.pending_drafts(frozenset(officer["workflows"]))}

    @app.get("/api/v1/runs/{workflow_id}/draft")
    def draft(workflow_id: str, officer: Officer):
        allow(workflow_id, officer)
        result = store.current_draft(workflow_id)
        if result is None:
            raise HTTPException(404, "Draft not found")
        return result

    @app.get("/api/v1/runs/{workflow_id}")
    async def status(workflow_id: str, officer: Officer):
        allow(workflow_id, officer)
        async with workflow_lock(workflow_id):
            result = store.current_draft(workflow_id)
            if result is None:
                raise HTTPException(404, "Workflow not found")
            await reconcile(workflow_id)
            snapshot = await workflow_snapshot(db_path, workflow_id)
            result = store.current_draft(workflow_id)
            return {
                "workflow_id": workflow_id,
                "draft_id": result["draft_id"],
                "version": result["version"],
                "content_hash": result["content_hash"],
                "draft_status": result["status"],
                "outcome": snapshot.values.get("outcome"),
                "pending_nodes": list(snapshot.next),
            }

    @app.post("/api/v1/runs/{workflow_id}/decisions")
    async def decide(workflow_id: str, body: DecisionInput, officer: Officer):
        allow(workflow_id, officer)
        async with workflow_lock(workflow_id):
            current = store.current_draft(workflow_id)
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
                record = store.decide(
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
            except StoreConflict as error:
                raise HTTPException(409, str(error)) from error
            snapshot = await workflow_snapshot(db_path, workflow_id)
            return {
                "decision": {key: value for key, value in record.items() if key != "reason"},
                "outcome": snapshot.values.get("outcome"),
            }

    return app


def local_app() -> FastAPI:
    """Uvicorn factory. Configuration and state stay outside the repository."""
    config = os.environ.get("SOKOSIGNAL_OFFICERS_CONFIG")
    state = os.environ.get("SOKOSIGNAL_STATE_DB")
    if not config or not state:
        raise RuntimeError("Local officer config and state DB paths are required.")
    return create_app(Path(state), Path(config))
