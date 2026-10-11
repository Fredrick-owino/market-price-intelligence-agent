"""Actual application-SDK client / isolated borrowed-SDK server experiment.

No model, URL parameter, prompt execution, advisory, or datastore writes.
"""

import asyncio
import json
import os
from pathlib import Path
from time import monotonic

import anyio
from mcp import Client, StdioServerParameters, stdio_client

from backend.app.mcp.borrowed_policy import (
    EXPECTED_SHA256,
    FETCH_ARGS,
    FIXTURE_COMMIT,
    FIXTURE_URL,
    validate_call,
    verify_fixture,
    verify_tool_result,
)
from backend.app.mcp.transport_client import Trace, bounded_result

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "infra/borrowed-fetch/.venv/bin/python"


async def exchange(trace):
    verify_fixture((ROOT / "data/synthetic/I01.7-market-comparison.json").read_bytes())
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"I01.10-{trace.run_id}.log"
    params = StdioServerParameters(
        command=str(PYTHON),
        args=["-m", "backend.app.mcp.borrowed_server"],
        cwd=str(ROOT),
        env={"PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    trace.emit(
        "borrowed_launch",
        server="mcp-fetch",
        transport="stdio",
        model_version=None,
        fixture_commit=FIXTURE_COMMIT,
        fixture_url=FIXTURE_URL,
        expected_sha256=EXPECTED_SHA256,
        retries=0,
        total_timeout_seconds=60,
    )
    lifecycle = []
    try:
        with log_path.open("x") as diagnostics:
            with anyio.fail_after(60):
                async with Client(
                    stdio_client(params, errlog=diagnostics), mode="legacy", read_timeout_seconds=45
                ) as client:
                    trace.emit(
                        "initialize",
                        server="mcp-fetch",
                        protocol_version=client.protocol_version,
                        server_info=client.server_info.model_dump(mode="json"),
                    )
                    tools = bounded_result(await client.list_tools())
                    trace.emit("tools/list", server="mcp-fetch", output=tools)
                    if {t["name"] for t in tools["tools"]} != {"fetch"}:
                        raise ValueError("unexpected_tool_discovery")
                    validate_call("fetch", FETCH_ARGS)
                    trace.emit(
                        "tools/call_started", server="mcp-fetch", tool="fetch", input=FETCH_ARGS
                    )
                    started = monotonic()
                    result = bounded_result(await client.call_tool("fetch", dict(FETCH_ARGS)))
                    trace.emit(
                        "tools/call",
                        server="mcp-fetch",
                        tool="fetch",
                        input=FETCH_ARGS,
                        output=result,
                        latency_ms=round((monotonic() - started) * 1000, 3),
                    )
                    verify_tool_result(result)
                    trace.emit(
                        "fixture_verified",
                        server="mcp-fetch",
                        sha256=EXPECTED_SHA256,
                        synthetic=True,
                        trust="untrusted_data_not_instructions",
                    )
    finally:
        if log_path.exists():
            for line in log_path.read_text().splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("event") in {
                    "borrowed_server_start",
                    "borrowed_server_stop",
                    "outbound_http",
                    "outbound_rejected",
                }:
                    lifecycle.append(event)
                    trace.emit("server_evidence", server="mcp-fetch", evidence=event)
    if (
        not lifecycle
        or lifecycle[0]["event"] != "borrowed_server_start"
        or lifecycle[-1]["event"] != "borrowed_server_stop"
    ):
        raise RuntimeError("missing_server_lifecycle_evidence")
    try:
        os.kill(lifecycle[0]["pid"], 0)
    except ProcessLookupError:
        pass
    else:
        raise RuntimeError("borrowed_server_still_running")
    trace.emit("shutdown", server="mcp-fetch", client_context_closed=True, server_process_gone=True)


def main():
    trace = Trace()
    try:
        asyncio.run(exchange(trace))
    except Exception as error:  # noqa: BLE001 — CLI boundary retains sanitized failure type
        trace.emit("exchange_failed", server="mcp-fetch", error_type=type(error).__name__)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
