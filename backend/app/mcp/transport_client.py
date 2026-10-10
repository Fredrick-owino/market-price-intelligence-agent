"""Repeatable, model-free MCP stdio exchange; stdout is sanitized JSONL evidence."""

import asyncio
import json
import os
import sys
from copy import deepcopy
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from time import monotonic
from uuid import uuid4

from mcp import Client, StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parents[3]
RESOURCE_URI = "synthetic://sokosignal/I01.7"
TOOL = "compare_market_options"
MAX_RESPONSE_BYTES = 65536


class Trace:
    """Experiment subset of RunEvent; only fixed synthetic requests are logged."""

    def __init__(self):
        self.run_id = str(uuid4())
        self.sequence = 0

    def emit(self, event_type: str, **details) -> None:
        self.sequence += 1
        print(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "event_id": str(uuid4()),
                    "sequence": self.sequence,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "event_type": event_type,
                    "server": "sokosignal-synthetic-I01.7",
                    "sdk_version": version("mcp"),
                    "model_version": None,
                    "synthetic": True,
                    "redaction": "Fixed public synthetic fixtures only; no environment or credentials logged.",
                    **details,
                },
                sort_keys=True,
            ),
            flush=True,
        )


def bounded_result(result) -> dict:
    value = result.model_dump(mode="json", by_alias=True, exclude_none=True)
    if len(json.dumps(value).encode()) > MAX_RESPONSE_BYTES:
        raise ValueError("Experiment response exceeded 64 KiB application limit")
    return value


async def exchange(trace: Trace) -> None:
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    stderr_path = log_dir / f"I01.7-server-{trace.run_id}.log"
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.app.mcp.synthetic_server"],
        cwd=str(ROOT),
        env={"PYTHONUNBUFFERED": "1"},
    )
    trace.emit(
        "launch",
        transport="stdio",
        protocol_mode="legacy",
        request_timeout_seconds=10,
        total_timeout_seconds=45,
        retries=0,
    )
    with stderr_path.open("x") as diagnostics:
        async with asyncio.timeout(45):
            transport = stdio_client(parameters, errlog=diagnostics)
            async with Client(transport, mode="legacy", read_timeout_seconds=10) as client:
                trace.emit(
                    "initialize",
                    protocol_version=client.protocol_version,
                    server_info=client.server_info.model_dump(mode="json"),
                    capabilities=client.server_capabilities.model_dump(mode="json"),
                )
                tools = await client.list_tools()
                trace.emit("tools/list", output=bounded_result(tools))
                resources = await client.list_resources()
                trace.emit("resources/list", output=bounded_result(resources))
                resource = await client.read_resource(RESOURCE_URI)
                trace.emit(
                    "resources/read", input={"uri": RESOURCE_URI}, output=bounded_result(resource)
                )
                fixture = json.loads(resource.contents[0].text)
                if (
                    fixture.get("synthetic") is not True
                    or fixture.get("data_status") != "synthetic"
                ):
                    raise ValueError("Refusing a fixture without explicit synthetic metadata")
                baseline = fixture["default_request"]
                cases = [("baseline", baseline)]
                for label, patch in [
                    ("half_quantity", {"quantity": "500"}),
                    ("explicit_loss", {"loss_fraction": "0.1"}),
                    ("negative_quantity", {"quantity": "-1"}),
                    ("zero_quantity", {"quantity": "0"}),
                    ("nonfinite_quantity", {"quantity": "NaN"}),
                    ("incompatible_quantity_unit", {"unit": "sack"}),
                    ("invalid_loss", {"loss_fraction": "1"}),
                    ("future_observation", {"as_of_date": "2026-10-09"}),
                    ("unknown_snapshot", {"snapshot_id": "00000000-0000-4000-8000-000000000999"}),
                    ("duplicate_quotes", {"quote_ids": [baseline["quote_ids"][0]] * 2}),
                    ("insufficient_capacity", {"quantity": "1001"}),
                ]:
                    cases.append((label, {**deepcopy(baseline), **patch}))
                for label, quote_id in fixture["negative_quote_ids"].items():
                    cases.append(
                        (
                            label,
                            {
                                **deepcopy(baseline),
                                "quote_ids": [baseline["quote_ids"][0], quote_id],
                            },
                        )
                    )
                cases.append(("baseline_after_errors", deepcopy(baseline)))
                for label, arguments in cases:
                    started = monotonic()
                    result = await client.call_tool(TOOL, arguments)
                    trace.emit(
                        "tools/call",
                        case=label,
                        tool=TOOL,
                        input=arguments,
                        output=bounded_result(result),
                        latency_ms=round((monotonic() - started) * 1000, 3),
                    )
    # The SDK has closed stdin and waited for the subprocess before returning here.
    lifecycle = []
    for line in stderr_path.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # SDK diagnostics stay in the ignored local log, not public evidence.
        if event.get("event") in {"server_starting", "server_stopped"}:
            lifecycle.append(event)
    if [event["event"] for event in lifecycle] != ["server_starting", "server_stopped"]:
        raise RuntimeError(
            "No evidence of normal server lifecycle completion; inspect local stderr log"
        )
    server_pid = lifecycle[0]["pid"]
    try:
        os.kill(server_pid, 0)
    except ProcessLookupError:
        process_gone = True
    else:
        process_gone = False
    if not process_gone:
        raise RuntimeError("Server process still exists after transport closed")
    trace.emit(
        "shutdown",
        lifecycle=lifecycle,
        server_process_gone=process_gone,
        client_context_closed=True,
    )


def main() -> None:
    trace = Trace()
    try:
        asyncio.run(exchange(trace))
    except Exception as error:
        # Do not publish arbitrary exception text that might include environment details.
        trace.emit("exchange_failed", error_type=type(error).__name__)
        raise


if __name__ == "__main__":
    main()
