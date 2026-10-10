"""Synthetic MCP/LangGraph workflow with optional local-model tool selection."""

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

from backend.app.agent.model_workflow import DEFAULT_TASK, ModelWorkflowFailure, model_exchange
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
    mode: str
    user_task: str
    failure_code: str
    failure_message: str


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


def build_graph(
    db_path: Path,
    *,
    request_timeout_seconds: float = 120,
    max_tool_steps: int = 3,
    total_run_timeout_seconds: float = 900,
):
    async def prepare(state: State) -> dict:
        if state.get("mode") == "model":
            try:
                if not 0 < total_run_timeout_seconds <= 900:
                    raise ModelWorkflowFailure(
                        "invalid_limits", "Total run timeout must be in (0,900] seconds."
                    )
                async with asyncio.timeout(total_run_timeout_seconds):
                    comparison, draft = await model_exchange(
                        state["workflow_id"],
                        state["idempotency_key"],
                        db_path,
                        user_task=state["user_task"],
                        request_timeout_seconds=request_timeout_seconds,
                        max_tool_steps=max_tool_steps,
                    )
                return {"comparison": comparison, "draft": draft}
            except (
                RuntimeError,
                TimeoutError,
                ExceptionGroup,
                OSError,
                ValueError,
                KeyError,
                TypeError,
            ) as error:
                if isinstance(error, ModelWorkflowFailure):
                    code, message = error.code, str(error)
                elif isinstance(error, TimeoutError):
                    code, message = (
                        "total_run_timeout",
                        "Total model/MCP deadline expired. Inspect trace and persisted draft before explicit retry with a new workflow ID.",
                    )
                else:
                    code, message = (
                        "transport_or_provider_failure",
                        f"{type(error).__name__}: inspect the recorded MCP/model events and local diagnostics; no fallback used.",
                    )
                event(
                    "model_workflow_failed",
                    workflow_id=state["workflow_id"],
                    failure_code=code,
                    message=message,
                )
                return {"failure_code": code, "failure_message": message}
        comparison, draft = await exchange(state["workflow_id"], state["idempotency_key"], db_path)
        return {"comparison": comparison, "draft": draft}

    def fail(state: State) -> dict:
        return {"outcome": "model_failed", "failure_code": state["failure_code"]}

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
        review = DraftStore(str(db_path)).validate_review(
            state["workflow_id"], state["draft"], state["review"]
        )
        return {
            "outcome": "approved_internal_review" if review["decision"] == "approve" else "rejected"
        }

    graph = StateGraph(State)
    graph.add_node("prepare", prepare)
    graph.add_node("model_failure", fail)
    graph.add_node("review_pause", pause)
    graph.add_node("finalize", finalize)
    graph.add_edge(START, "prepare")
    graph.add_conditional_edges(
        "prepare",
        lambda state: "model_failure" if state.get("failure_code") else "review_pause",
    )
    graph.add_edge("model_failure", END)
    graph.add_edge("review_pause", "finalize")
    graph.add_edge("finalize", END)
    return graph


def run_start(args) -> None:
    args.db.parent.mkdir(parents=True, exist_ok=True)
    config = {"configurable": {"thread_id": args.workflow_id}}

    async def invoke():
        async with AsyncSqliteSaver.from_conn_string(str(args.db)) as saver:
            app = build_graph(
                args.db,
                request_timeout_seconds=args.request_timeout_seconds,
                max_tool_steps=args.max_tool_steps,
                total_run_timeout_seconds=args.total_run_timeout_seconds,
            ).compile(checkpointer=saver)
            snapshot = await app.aget_state(config)
            if snapshot.values and snapshot.values.get("idempotency_key") != args.idempotency_key:
                raise StoreConflict("Workflow start conflicts with its original idempotency key.")
            if snapshot.values and (snapshot.values.get("mode") == "model") != args.model_driven:
                raise StoreConflict("Workflow start conflicts with its original execution mode.")
            if (
                snapshot.values.get("mode") == "model"
                and snapshot.values.get("user_task") != args.user_task
            ):
                raise StoreConflict("Workflow start conflicts with its original user task.")
            if snapshot.values.get("outcome") or snapshot.values.get("draft"):
                return {"replay": True, "snapshot": snapshot}
            if snapshot.next:
                return await app.ainvoke(None, config)
            state = {"workflow_id": args.workflow_id, "idempotency_key": args.idempotency_key}
            if args.model_driven:
                state.update({"mode": "model", "user_task": args.user_task})
            return await app.ainvoke(state, config)

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
        if snapshot.values.get("outcome") == "model_failed":
            raise SystemExit(2)
        return
    if result.get("outcome") == "model_failed":
        event(
            "workflow_failed",
            workflow_id=args.workflow_id,
            failure_code=result.get("failure_code"),
            message=result.get("failure_message"),
            persistent_counts=DraftStore(str(args.db)).counts(args.workflow_id),
        )
        raise SystemExit(2)
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
    start.add_argument("--model-driven", action="store_true")
    start.add_argument("--user-task", default=DEFAULT_TASK)
    start.add_argument("--request-timeout-seconds", type=float, default=120)
    start.add_argument("--total-run-timeout-seconds", type=float, default=900)
    start.add_argument("--max-tool-steps", type=int, default=3)
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
                    snapshot = await app.aget_state(config)
                    # An idempotent revision retry must not reopen a completed revision.
                    if snapshot.values.get("draft", {}).get("version", 0) >= revised["version"]:
                        return
                    await app.aupdate_state(
                        config,
                        {"draft": revised, "review": None, "outcome": None, "failure_code": None},
                        as_node="prepare",
                    )
                    await app.ainvoke(None, config)

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
