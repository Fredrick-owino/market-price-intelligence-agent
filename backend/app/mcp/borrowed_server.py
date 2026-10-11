"""Launch pinned upstream Fetch with a fixed tool and constrained HTTP transport.

This is an application wrapper, not an unmodified upstream security claim.
Run only with infra/borrowed-fetch/.venv/bin/python.
"""

import asyncio
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import httpx
import mcp_server_fetch.server as upstream
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData

from backend.app.mcp.borrowed_policy import (
    RetrievalRejected,
    download,
    validate_call,
)

UPSTREAM_VERSION = "2026.8.18"
UPSTREAM_SERVER_SHA = "f66dc973126c9251934fdb5355fa960529546660cad74147a6b31f725a79b358"


def audit(event, **details):
    print(
        json.dumps({"event": event, "timestamp": datetime.now(UTC).isoformat(), **details}),
        file=sys.stderr,
        flush=True,
    )


class FixedTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request):
        try:
            if request.method != "GET" or request.content:
                raise RetrievalRejected("get_only")
            async with asyncio.timeout(20):
                status, headers, body, provenance = await asyncio.to_thread(
                    download, str(request.url)
                )
            audit("outbound_http", **provenance)
            return httpx.Response(status, headers=headers, content=body, request=request)
        except (RetrievalRejected, OSError, ValueError, TimeoutError) as error:
            # Never copy exception text containing arbitrary input or server data.
            audit("outbound_rejected", error_type=type(error).__name__)
            raise httpx.RequestError("bounded_retrieval_failed", request=request) from error


class FixedClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        if args or kwargs.get("proxy") is not None:
            raise RetrievalRejected("proxy_rejected")
        super().__init__(transport=FixedTransport(), trust_env=False, follow_redirects=False)


class FixedServer(upstream.Server):
    def call_tool(self, *args, **kwargs):
        register = super().call_tool(*args, **kwargs)

        def decorate(handler):
            async def guarded(name, arguments):
                try:
                    validate_call(name, arguments)
                except RetrievalRejected as error:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(error))) from error
                return await handler(name, arguments)

            return register(guarded)

        return decorate

    def get_prompt(self, *args, **kwargs):
        register = super().get_prompt(*args, **kwargs)

        def decorate(_handler):
            async def denied(*_args, **_kwargs):
                raise McpError(ErrorData(code=INVALID_PARAMS, message="prompts_disabled"))

            return register(denied)

        return decorate

    def list_prompts(self, *args, **kwargs):
        register = super().list_prompts(*args, **kwargs)

        def decorate(_handler):
            async def empty():
                return []

            return register(empty)

        return decorate


async def main():
    source_hash = hashlib.sha256(Path(upstream.__file__).read_bytes()).hexdigest()
    if version("mcp-server-fetch") != UPSTREAM_VERSION or source_hash != UPSTREAM_SERVER_SHA:
        raise RetrievalRejected("upstream_pin_mismatch")
    audit(
        "borrowed_server_start",
        distribution="mcp-server-fetch",
        version=UPSTREAM_VERSION,
        sdk_version=version("mcp"),
        source_sha256=source_hash,
        wrapper="I01.10-fixed-target-v1",
        pid=os.getpid(),
    )
    # Both upstream HTTP paths instantiate httpx.AsyncClient at call time.
    # Version/source checks above make this explicit adaptation fail closed on upgrades.
    httpx.AsyncClient = FixedClient
    upstream.Server = FixedServer
    try:
        await upstream.serve()
    finally:
        audit("borrowed_server_stop")


if __name__ == "__main__":
    asyncio.run(main())
