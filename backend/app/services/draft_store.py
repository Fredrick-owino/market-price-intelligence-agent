"""SQLite persistence for the bounded synthetic draft/review experiment."""

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5


class StoreConflict(ValueError):
    """A stale, conflicting, or unauthorized persistence operation."""


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def now() -> str:
    return datetime.now(UTC).isoformat()


class DraftStore:
    def __init__(self, path: str):
        self.path = path
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS drafts(
                    workflow_id TEXT NOT NULL, draft_id TEXT NOT NULL, version INTEGER NOT NULL,
                    content TEXT NOT NULL, content_hash TEXT NOT NULL, comparison_hash TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL,
                    PRIMARY KEY(workflow_id, version), UNIQUE(draft_id));
                CREATE TABLE IF NOT EXISTS actions(
                    workflow_id TEXT NOT NULL, action_key TEXT NOT NULL, payload_hash TEXT NOT NULL,
                    response TEXT NOT NULL, PRIMARY KEY(workflow_id, action_key));
                CREATE TABLE IF NOT EXISTS decisions(
                    workflow_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, draft_id TEXT NOT NULL,
                    version INTEGER NOT NULL, content_hash TEXT NOT NULL, decision TEXT NOT NULL,
                    reviewer_id TEXT NOT NULL, reason TEXT NOT NULL, decided_at TEXT NOT NULL,
                    PRIMARY KEY(workflow_id, idempotency_key),
                    UNIQUE(workflow_id, draft_id, version));
                CREATE TABLE IF NOT EXISTS audit(
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT, workflow_id TEXT NOT NULL,
                    event_type TEXT NOT NULL, event_json TEXT NOT NULL, timestamp TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs(
                    workflow_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
                    request_json TEXT NOT NULL, request_hash TEXT NOT NULL,
                    status TEXT NOT NULL, error_code TEXT, updated_at TEXT NOT NULL);
                """
            )

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    @staticmethod
    def _content(workflow_id: str, version: int, request: dict, comparison: dict) -> dict:
        rows = comparison["markets"]
        return {
            "label": "SYNTHETIC ONLY — no live prices or capacity",
            "workflow_id": workflow_id,
            "version": version,
            **(
                {
                    "synthetic": True,
                    "data_status": "synthetic",
                    "snapshot_sha256": comparison["snapshot_sha256"],
                    "retrieval_provenance": comparison["retrieval_provenance"],
                }
                if "retrieval_provenance" in comparison
                else {}
            ),
            "quote_references": [
                {"quote_id": row["quote_id"], "source_reference": "synthetic://sokosignal/I01.7"}
                for row in rows
            ],
            "calculation": {
                "quantity": request["quantity"],
                "unit": request["unit"],
                "currency": comparison["currency"],
                "net_proceeds": {row["market"]: row["estimated_net_proceeds"] for row in rows},
                "winner": comparison["winner"],
                "advantage_kes": comparison["advantage_kes"],
            },
            "assumptions": comparison["assumptions"],
            "limitations": comparison["limitations"]
            + [
                "No real-market data integration, advisory delivery, order or production approval is implemented."
            ],
            "review_status": "PENDING_REVIEW",
            "revision_note": None
            if version == 1
            else "Synthetic correction revision for recovery test.",
        }

    def _audit(self, db, workflow_id: str, event_type: str, event: dict):
        db.execute(
            "INSERT INTO audit(workflow_id,event_type,event_json,timestamp) VALUES(?,?,?,?)",
            (workflow_id, event_type, canonical(event), now()),
        )

    def create_draft(
        self,
        workflow_id: str,
        idempotency_key: str,
        request: dict,
        comparison: dict,
        advisory: dict | None = None,
    ) -> dict:
        content = self._content(workflow_id, 1, request, comparison)
        if advisory is not None:
            from backend.app.domain.synthetic_comparison import validate_advisory

            validate_advisory(advisory, comparison)
            content["advisory"] = advisory
        body = canonical(content)
        digest = hashlib.sha256(body.encode()).hexdigest()
        comparison_hash = hashlib.sha256(canonical(comparison).encode()).hexdigest()
        payload_hash = hashlib.sha256(
            canonical(
                {
                    "request": request,
                    "comparison_hash": comparison_hash,
                    **({"advisory": advisory} if advisory is not None else {}),
                }
            ).encode()
        ).hexdigest()
        draft_id = str(uuid5(NAMESPACE_URL, f"sokosignal:{workflow_id}:{idempotency_key}"))
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT * FROM actions WHERE workflow_id=? AND action_key=?",
                (workflow_id, idempotency_key),
            ).fetchone()
            if prior:
                if prior["payload_hash"] != payload_hash:
                    raise StoreConflict("Idempotency key conflicts with a different request.")
                db.execute("COMMIT")
                return json.loads(prior["response"])
            if db.execute("SELECT 1 FROM drafts WHERE workflow_id=?", (workflow_id,)).fetchone():
                raise StoreConflict(
                    "Workflow already has a draft; use the explicit revise command."
                )
            response = {
                "synthetic": True,
                "workflow_id": workflow_id,
                "draft_id": draft_id,
                "version": 1,
                "content_hash": digest,
                "review_status": "PENDING_REVIEW",
                "content": content,
            }
            db.execute(
                "INSERT INTO drafts VALUES(?,?,?,?,?,?,?,?)",
                (workflow_id, draft_id, 1, body, digest, comparison_hash, "PENDING_REVIEW", now()),
            )
            db.execute(
                "INSERT INTO actions VALUES(?,?,?,?)",
                (workflow_id, idempotency_key, payload_hash, canonical(response)),
            )
            self._audit(db, workflow_id, "draft_created", response)
            db.execute("COMMIT")
        return response

    def revise(self, workflow_id: str, idempotency_key: str) -> dict:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            action_key = f"revision:{idempotency_key}"
            prior = db.execute(
                "SELECT * FROM actions WHERE workflow_id=? AND action_key=?",
                (workflow_id, action_key),
            ).fetchone()
            if prior:
                db.execute("COMMIT")
                return json.loads(prior["response"])
            current = db.execute(
                "SELECT * FROM drafts WHERE workflow_id=? ORDER BY version DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
            if not current or current["status"] not in {"PENDING_REVIEW", "APPROVED", "REJECTED"}:
                raise StoreConflict("Only a pending or decided draft can be revised.")
            content = dict(
                json.loads(current["content"]),
                version=current["version"] + 1,
                revision_note="Synthetic correction revision for recovery test.",
                review_status="PENDING_REVIEW",
            )
            body = canonical(content)
            digest = hashlib.sha256(body.encode()).hexdigest()
            version = current["version"] + 1
            draft_id = str(uuid5(NAMESPACE_URL, f"sokosignal:{workflow_id}:revision:{version}"))
            db.execute(
                "UPDATE drafts SET status='SUPERSEDED' WHERE workflow_id=? AND version=?",
                (workflow_id, current["version"]),
            )
            db.execute(
                "INSERT INTO drafts VALUES(?,?,?,?,?,?,?,?)",
                (
                    workflow_id,
                    draft_id,
                    version,
                    body,
                    digest,
                    current["comparison_hash"],
                    "PENDING_REVIEW",
                    now(),
                ),
            )
            response = {
                "workflow_id": workflow_id,
                "draft_id": draft_id,
                "version": version,
                "content_hash": digest,
                "review_status": "PENDING_REVIEW",
                "content": content,
            }
            self._audit(db, workflow_id, "draft_revised", response)
            payload_hash = hashlib.sha256(
                canonical(
                    {
                        "operation": "revise",
                        "base_version": current["version"],
                        "base_hash": current["content_hash"],
                    }
                ).encode()
            ).hexdigest()
            db.execute(
                "INSERT INTO actions VALUES(?,?,?,?)",
                (workflow_id, action_key, payload_hash, canonical(response)),
            )
            db.execute("COMMIT")
        return response

    def decide(
        self,
        workflow_id: str,
        draft_id: str,
        version: int,
        content_hash: str,
        decision: str,
        reviewer_id: str,
        idempotency_key: str,
        reason: str = "Synthetic recovery test",
        *,
        authenticated: bool = False,
    ) -> dict:
        if authenticated:
            if not reviewer_id or reviewer_id.startswith("simulated:"):
                raise StoreConflict("Authenticated officer identity is required.")
        elif reviewer_id != "simulated:officer-001":
            raise StoreConflict("Reviewer identity must be simulated:officer-001.")
        if decision not in {"approve", "reject"}:
            raise StoreConflict("Decision must be approve or reject.")
        payload = {
            "draft_id": draft_id,
            "version": version,
            "content_hash": content_hash,
            "decision": decision,
            "reviewer_id": reviewer_id,
            "reason": reason,
        }
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT * FROM decisions WHERE workflow_id=? AND idempotency_key=?",
                (workflow_id, idempotency_key),
            ).fetchone()
            current = db.execute(
                "SELECT * FROM drafts WHERE workflow_id=? ORDER BY version DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
            if not current or (
                current["draft_id"],
                current["version"],
                current["content_hash"],
            ) != (draft_id, version, content_hash):
                raise StoreConflict(
                    "Decision does not match the exact current draft ID, version, and hash."
                )
            if prior:
                if any(prior[key] != payload[key] for key in payload):
                    raise StoreConflict(
                        "Decision idempotency key conflicts with a different decision."
                    )
                db.execute("COMMIT")
                return dict(prior)
            if current["status"] != "PENDING_REVIEW":
                raise StoreConflict("Draft is no longer pending review.")
            record = {
                **payload,
                "workflow_id": workflow_id,
                "idempotency_key": idempotency_key,
                "decided_at": now(),
            }
            db.execute(
                "INSERT INTO decisions VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    workflow_id,
                    idempotency_key,
                    draft_id,
                    version,
                    content_hash,
                    decision,
                    reviewer_id,
                    reason,
                    record["decided_at"],
                ),
            )
            db.execute(
                "UPDATE drafts SET status=? WHERE workflow_id=? AND version=?",
                ("APPROVED" if decision == "approve" else "REJECTED", workflow_id, version),
            )
            self._audit(
                db,
                workflow_id,
                "officer_review_decision" if authenticated else "simulated_review_decision",
                record,
            )
            db.execute("COMMIT")
        return record

    def decision(self, workflow_id: str) -> dict:
        with self.connect() as db:
            row = db.execute(
                "SELECT d.* FROM decisions d JOIN drafts v "
                "ON d.workflow_id=v.workflow_id AND d.draft_id=v.draft_id "
                "WHERE d.workflow_id=? AND v.version=(SELECT MAX(version) FROM drafts "
                "WHERE workflow_id=?)",
                (workflow_id, workflow_id),
            ).fetchone()
            if not row:
                raise StoreConflict("No recorded decision exists for the current draft.")
            return dict(row)

    def current_draft(self, workflow_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM drafts WHERE workflow_id=? ORDER BY version DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
            if row is None:
                return None
            return {**dict(row), "content": json.loads(row["content"])}

    def pending_drafts(self, permitted_workflows: frozenset[str], prefix: str = "") -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT d.* FROM drafts d WHERE d.status='PENDING_REVIEW' "
                "AND d.version=(SELECT MAX(version) FROM drafts WHERE workflow_id=d.workflow_id) "
                "ORDER BY d.created_at DESC"
            ).fetchall()
        return [
            {**dict(row), "content": json.loads(row["content"])}
            for row in rows
            if row["workflow_id"] in permitted_workflows
            or (prefix and row["workflow_id"].startswith(prefix))
        ]

    def create_run(
        self, workflow_id: str, officer_id: str, request: dict, *, reject_if_running: bool = False
    ) -> dict:
        body = canonical(request)
        digest = hashlib.sha256(body.encode()).hexdigest()
        prior = self.run(workflow_id)
        if prior:
            if prior["owner_id"] != officer_id or prior["request_hash"] != digest:
                raise StoreConflict("Run idempotency key conflicts with another request.")
            return prior
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT * FROM runs WHERE workflow_id=?", (workflow_id,)).fetchone()
            if (
                prior is None
                and reject_if_running
                and db.execute("SELECT 1 FROM runs WHERE status='RUNNING' LIMIT 1").fetchone()
            ):
                raise StoreConflict(
                    "A model workflow is already running. Wait before starting another."
                )
            db.execute(
                "INSERT OR IGNORE INTO runs VALUES(?,?,?,?,?,?,?)",
                (workflow_id, officer_id, body, digest, "RUNNING", None, now()),
            )
            prior = db.execute("SELECT * FROM runs WHERE workflow_id=?", (workflow_id,)).fetchone()
            db.execute("COMMIT")
        if prior["owner_id"] != officer_id or prior["request_hash"] != digest:
            raise StoreConflict("Run idempotency key conflicts with another request.")
        return dict(prior)

    def run(self, workflow_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM runs WHERE workflow_id=?", (workflow_id,)).fetchone()
            return dict(row) if row else None

    def update_run(self, workflow_id: str, status: str, error_code: str | None = None) -> None:
        if status not in {"RUNNING", "PENDING_REVIEW", "COMPLETED", "FAILED"}:
            raise ValueError("Invalid run status.")
        with self.connect() as db:
            db.execute(
                "UPDATE runs SET status=?, error_code=?, updated_at=? WHERE workflow_id=?",
                (status, error_code, now(), workflow_id),
            )

    def validate_review(self, workflow_id: str, draft: dict, review: dict) -> dict:
        """Resume authority comes only from the stored decision for the current version."""
        with self.connect() as db:
            row = db.execute(
                "SELECT d.*, v.status FROM decisions d JOIN drafts v "
                "ON d.workflow_id=v.workflow_id AND d.draft_id=v.draft_id "
                "WHERE d.workflow_id=? AND v.version=(SELECT MAX(version) FROM drafts "
                "WHERE workflow_id=?)",
                (workflow_id, workflow_id),
            ).fetchone()
            if not row:
                raise StoreConflict("No decision exists for the current draft.")
            record = dict(row)
            status = record.pop("status")
            if not isinstance(review, dict) or review != record:
                raise StoreConflict("Resume payload does not match the recorded decision.")
            if any(
                record[key] != draft.get(key) for key in ("draft_id", "version", "content_hash")
            ):
                raise StoreConflict("Stored decision does not match the checkpointed draft.")
            if status != {"approve": "APPROVED", "reject": "REJECTED"}.get(record["decision"]):
                raise StoreConflict("Current draft is not in the recorded decision state.")
            return record

    def counts(self, workflow_id: str) -> dict:
        with self.connect() as db:
            return {
                table: db.execute(
                    f"SELECT count(*) FROM {table} WHERE workflow_id=?", (workflow_id,)
                ).fetchone()[0]
                for table in ("drafts", "actions", "decisions", "audit")
            }
