"""Actual stdio-MCP and LangGraph/SQLite recovery spike; deterministic, no model."""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from mcp import Client, StdioServerParameters, stdio_client

from backend.app.services.draft_store import DraftStore, StoreConflict

ROOT = Path(__file__).resolve().parents[3]
DB_DEFAULT = ROOT / ".state/I01.8.sqlite"
RESOURCE_URI = "synthetic://sokosignal/I01.7"


def event(kind: str, **data) -> None:
    print(
        json.dumps(
            {"timestamp": datetime.now(UTC).isoformat(), "event": kind, "synthetic": True, **data},
            sort_keys=True,
        ),
        flush=True,
    )


class State(TypedDict, total=False):
    workflow_id: str
    idempotency_key: str
    comparison: dict
    draft: dict
    review: dict
    outcome: str


async def exchange(workflow_id: str, idempotency_key: str, db_path: Path) -> dict:
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    stderr_path = log_dir / f"I01.8-server-{workflow_id}-{uuid4()}.log"
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.app.mcp.synthetic_server"],
        cwd=str(ROOT),
        env={"PYTHONUNBUFFERED": "1", "SOKOSIGNAL_STATE_DB": str(db_path)},
    )
    with stderr_path.open("x", encoding="utf-8") as diagnostics:
        async with Client(
            stdio_client(params, errlog=diagnostics), mode="legacy", read_timeout_seconds=15
        ) as client:
            discovered = await client.list_tools()
            resource = await client.read_resource(RESOURCE_URI)
            fixture = json.loads(resource.contents[0].text)
            if fixture.get("synthetic") is not True or fixture.get("data_status") != "synthetic":
                raise RuntimeError("Refusing an unlabeled fixture")
            request = fixture["default_request"]
            result = await client.call_tool("compare_market_options", request)
            comparison = result.structured_content
            event(
                "mcp_comparison",
                tool="compare_market_options",
                input=request,
                output=comparison,
                discovered_tools=[tool.name for tool in discovered.tools],
            )
            if result.is_error:
                raise RuntimeError("MCP comparison returned an error")
            saved = await client.call_tool(
                "save_advisory_draft",
                {
                    "workflow_id": workflow_id,
                    "idempotency_key": idempotency_key,
                    "comparison": {"request": request, "result": comparison},
                },
            )
            event("mcp_draft", tool="save_advisory_draft", output=saved.structured_content)
            if saved.is_error:
                raise RuntimeError("MCP draft save returned an error")
            output = {"request": request, "result": comparison}, saved.structured_content
    lifecycle = []
    for line in stderr_path.read_text(encoding="utf-8").splitlines():
        try:
            diagnostic = json.loads(line)
        except json.JSONDecodeError:
            continue
        if diagnostic.get("event") in {"server_starting", "server_stopped"}:
            lifecycle.append(diagnostic)
    if [entry["event"] for entry in lifecycle] != ["server_starting", "server_stopped"]:
        raise RuntimeError("MCP server did not report a normal start/stop lifecycle")
    try:
        os.kill(lifecycle[0]["pid"], 0)
    except ProcessLookupError:
        process_gone = True
    else:
        process_gone = False
    if not process_gone:
        raise RuntimeError("MCP server process remained after the client session closed")
    event(
        "mcp_server_lifecycle",
        lifecycle=lifecycle,
        client_session_closed=True,
        server_process_gone=process_gone,
    )
    return output


async def conflict_call(workflow_id: str, idempotency_key: str, db_path: Path) -> dict:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.app.mcp.synthetic_server"],
        cwd=str(ROOT),
        env={"PYTHONUNBUFFERED": "1", "SOKOSIGNAL_STATE_DB": str(db_path)},
    )
    async with Client(params, mode="legacy", read_timeout_seconds=15) as client:
        resource = await client.read_resource(RESOURCE_URI)
        request = json.loads(resource.contents[0].text)["default_request"]
        request["quantity"] = "999"
        comparison = await client.call_tool("compare_market_options", request)
        result = await client.call_tool(
            "save_advisory_draft",
            {
                "workflow_id": workflow_id,
                "idempotency_key": idempotency_key,
                "comparison": {"request": request, "result": comparison.structured_content},
            },
        )
        return {"is_error": result.is_error, "result": result.structured_content}


def build_graph(db_path: Path):
    async def prepare(state: State) -> dict:
        comparison, draft = await exchange(state["workflow_id"], state["idempotency_key"], db_path)
        return {"comparison": comparison, "draft": draft}

    def pause(state: State) -> dict:
        review = interrupt(
            {
                "workflow_id": state["workflow_id"],
                "draft_id": state["draft"]["draft_id"],
                "version": state["draft"]["version"],
                "content_hash": state["draft"]["content_hash"],
                "review_status": "PENDING_REVIEW",
                "reviewer_mode": "simulated command only",
            }
        )
        return {"review": review}

    def finalize(state: State) -> dict:
        review = state["review"]
        if (review["draft_id"], review["version"], review["content_hash"]) != (
            state["draft"]["draft_id"],
            state["draft"]["version"],
            state["draft"]["content_hash"],
        ):
            raise StoreConflict("Resume decision does not match the checkpointed draft.")
        return {
            "outcome": "approved_internal_review" if review["decision"] == "approve" else "rejected"
        }

    graph = StateGraph(State)
    graph.add_node("prepare", prepare)
    graph.add_node("review_pause", pause)
    graph.add_node("finalize", finalize)
    graph.add_edge(START, "prepare")
    graph.add_edge("prepare", "review_pause")
    graph.add_edge("review_pause", "finalize")
    graph.add_edge("finalize", END)
    return graph


def run_start(args) -> None:
    args.db.parent.mkdir(parents=True, exist_ok=True)
    config = {"configurable": {"thread_id": args.workflow_id}}

    async def invoke():
        async with AsyncSqliteSaver.from_conn_string(str(args.db)) as saver:
            app = build_graph(args.db).compile(checkpointer=saver)
            snapshot = await app.aget_state(config)
            if snapshot.values.get("outcome") or snapshot.values.get("draft"):
                return {"replay": True, "snapshot": snapshot}
            if snapshot.next:
                return await app.ainvoke(None, config)
            return await app.ainvoke(
                {"workflow_id": args.workflow_id, "idempotency_key": args.idempotency_key}, config
            )

    result = asyncio.run(invoke())
    if result.get("replay"):
        snapshot = result["snapshot"]
        event(
            "workflow_replay_noop",
            workflow_id=args.workflow_id,
            outcome=snapshot.values.get("outcome"),
            pending_nodes=list(snapshot.next),
            persistent_counts=DraftStore(str(args.db)).counts(args.workflow_id),
        )
        return
    pending = result.get("__interrupt__", [])
    if not pending:
        raise RuntimeError("Workflow did not pause for review")
    event("workflow_paused", interrupt=pending[0].value, checkpoint_thread_id=args.workflow_id)


def run_review(args) -> None:
    store = DraftStore(str(args.db))
    record = store.decide(
        args.workflow_id,
        args.draft_id,
        args.version,
        args.content_hash,
        args.decision,
        args.reviewer_id,
        args.decision_key,
    )
    event("simulated_review_recorded", decision=record)
    config = {"configurable": {"thread_id": args.workflow_id}}

    async def invoke():
        async with AsyncSqliteSaver.from_conn_string(str(args.db)) as saver:
            app = build_graph(args.db).compile(checkpointer=saver)
            snapshot = await app.aget_state(config)
            if not snapshot.next:
                return None
            return await app.ainvoke(Command(resume=record), config)

    result = asyncio.run(invoke())
    if result is None:
        event(
            "workflow_replay_noop",
            workflow_id=args.workflow_id,
            persistent_counts=store.counts(args.workflow_id),
        )
        return
    event(
        "workflow_resumed",
        workflow_id=args.workflow_id,
        outcome=result["outcome"],
        persistent_counts=store.counts(args.workflow_id),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic private draft recovery experiment")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--workflow-id", required=True)
    start.add_argument("--idempotency-key", required=True)
    review = commands.add_parser("review")
    for key in ("workflow-id", "draft-id", "content-hash", "reviewer-id", "decision-key"):
        review.add_argument(f"--{key}", required=True)
    review.add_argument("--version", type=int, required=True)
    review.add_argument("--decision", choices=("approve", "reject"), required=True)
    revise = commands.add_parser("revise")
    revise.add_argument("--workflow-id", required=True)
    revise.add_argument("--idempotency-key", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--workflow-id", required=True)
    conflict = commands.add_parser("conflict")
    conflict.add_argument("--workflow-id", required=True)
    conflict.add_argument("--idempotency-key", required=True)
    replay_create = commands.add_parser("replay-create")
    replay_create.add_argument("--workflow-id", required=True)
    replay_create.add_argument("--idempotency-key", required=True)
    args = parser.parse_args()
    try:
        if args.command == "start":
            run_start(args)
        elif args.command == "review":
            run_review(args)
        elif args.command == "revise":
            revised = DraftStore(str(args.db)).revise(args.workflow_id, args.idempotency_key)
            config = {"configurable": {"thread_id": args.workflow_id}}

            async def update_checkpoint():
                async with AsyncSqliteSaver.from_conn_string(str(args.db)) as saver:
                    app = build_graph(args.db).compile(checkpointer=saver)
                    await app.aupdate_state(config, {"draft": revised}, as_node="prepare")

            asyncio.run(update_checkpoint())
            event("draft_revised", draft=revised)
        elif args.command == "conflict":
            result = asyncio.run(conflict_call(args.workflow_id, args.idempotency_key, args.db))
            event("conflicting_mcp_retry", **result)
            if not result["is_error"]:
                raise RuntimeError("Conflicting MCP idempotency retry unexpectedly succeeded")
        elif args.command == "replay-create":
            _, draft = asyncio.run(exchange(args.workflow_id, args.idempotency_key, args.db))
            event("draft_creation_replay", draft=draft)
        else:
            event("workflow_store", counts=DraftStore(str(args.db)).counts(args.workflow_id))
    except (StoreConflict, ValueError) as error:
        event("operation_rejected", error_type=type(error).__name__, message=str(error))
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
