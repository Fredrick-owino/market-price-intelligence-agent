"""One stdio MCP tool and one synthetic resource; diagnostics only on stderr."""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Annotated

from mcp.server import MCPServer
from mcp.types import CallToolResult, TextContent
from pydantic import Field

from backend.app.domain.synthetic_comparison import (
    RESOURCE_URI,
    ComparisonError,
    compare,
    load_fixture,
)

server = MCPServer(
    "sokosignal-synthetic-I01.7",
    version="0.1.0",
    instructions="Synthetic calculation only. No model, delivery, or officer approval.",
)


@server.resource(
    RESOURCE_URI,
    mime_type="application/json",
    name="synthetic_market_fixture",
    description="Clearly labelled synthetic fixture and invalid comparison variants; no live data.",
)
def synthetic_market_fixture() -> str:
    fixture, digest = load_fixture()
    return json.dumps({**fixture, "snapshot_sha256": digest})


@server.tool(
    description="Compare exactly two quote IDs from the synthetic snapshot with Decimal arithmetic."
)
def compare_market_options(
    snapshot_id: Annotated[str, Field(max_length=36)],
    quote_ids: Annotated[list[Annotated[str, Field(max_length=36)]], Field(max_length=2)],
    quantity: Annotated[str, Field(max_length=17)],
    unit: Annotated[str, Field(max_length=16)],
    loss_fraction: Annotated[str, Field(max_length=17)],
    as_of_date: Annotated[str, Field(max_length=10)],
    policy_version: Annotated[str, Field(max_length=32)],
) -> CallToolResult:
    request = {
        "snapshot_id": snapshot_id,
        "quote_ids": quote_ids,
        "quantity": quantity,
        "unit": unit,
        "loss_fraction": loss_fraction,
        "as_of_date": as_of_date,
        "policy_version": policy_version,
    }
    try:
        result = compare(request)
        failed = False
    except ComparisonError as error:
        result = {"synthetic": True, "data_status": "synthetic", "error": error.detail}
        failed = True
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(result))],
        structured_content=result,
        is_error=failed,
    )


def diagnostic(event: str) -> None:
    print(
        json.dumps(
            {
                "event": event,
                "timestamp": datetime.now(UTC).isoformat(),
                "pid": os.getpid(),
                "synthetic": True,
            }
        ),
        file=sys.stderr,
        flush=True,
    )


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    diagnostic("server_starting")
    server.run(transport="stdio")
    # Reached only after the SDK returns normally, not on a forced kill or exception.
    diagnostic("server_stopped")
