"""Real stdio borrowed-server tests: rejection and explicitly mocked HTTP (no web fetch).

Requires the separately locked infra/borrowed-fetch environment. These tests
prove the wrapper's server boundary, not successful public retrieval.
"""

import asyncio
import json
from pathlib import Path

import pytest
from mcp import Client, StdioServerParameters, stdio_client
from mcp.shared.exceptions import MCPError

from backend.app.mcp.borrowed_policy import FETCH_ARGS, ROBOTS_URL

ROOT = Path(__file__).resolve().parents[2]
SERVER_PYTHON = ROOT / "infra/borrowed-fetch/.venv/bin/python"


@pytest.mark.asyncio
async def test_real_borrowed_server_rejects_arbitrary_arguments_and_prompt(tmp_path):
    assert SERVER_PYTHON.exists(), "Install the documented isolated Fetch environment first"
    params = StdioServerParameters(
        command=str(SERVER_PYTHON),
        args=["-m", "backend.app.mcp.borrowed_server"],
        cwd=str(ROOT),
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    logfile = tmp_path / "server.log"
    with logfile.open("w") as diagnostics:
        async with asyncio.timeout(20):
            async with Client(
                stdio_client(params, errlog=diagnostics), mode="legacy", read_timeout_seconds=10
            ) as client:
                assert client.server_info.name == "mcp-fetch"
                discovered = await client.list_tools()
                assert [t.name for t in discovered.tools] == ["fetch"]
                prompts = await client.list_prompts()
                assert prompts.prompts == []
                with pytest.raises(MCPError, match="prompts_disabled"):
                    await client.get_prompt("fetch", {"url": FETCH_ARGS["url"]})
                for patch in [
                    {"url": "http://127.0.0.1/"},
                    {"url": "https://example.com/"},
                    {"url": ROBOTS_URL},
                    {"start_index": 1},
                    {"raw": False},
                    {"max_length": 100000},
                ]:
                    result = await client.call_tool("fetch", {**FETCH_ARGS, **patch})
                    assert result.is_error is True
                    assert "fixed_fetch_arguments_required" in result.content[0].text
    events = []
    for line in logfile.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    assert [e["event"] for e in events] == ["borrowed_server_start", "borrowed_server_stop"]
    assert events[0]["version"] == "2026.8.18"
    assert events[0]["sdk_version"].startswith("1.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    ["allowed", "robots_deny", "unavailable", "http_failure", "truncated", "malformed", "mismatch"],
)
async def test_real_mcp_mocked_http_upstream_behavior(tmp_path, case):
    """Actual borrowed SDK/tool handlers; HTTP deliberately mocked, not live evidence."""
    from backend.app.mcp.borrowed_policy import RetrievalRejected, verify_tool_result

    script = """
import asyncio
from pathlib import Path
from backend.app.mcp import borrowed_server as server
from backend.app.mcp.borrowed_policy import FIXTURE_URL, ROBOTS_URL
CASE = CASE_VALUE
body = Path("data/synthetic/I01.7-market-comparison.json").read_bytes()
def fake(url):
    status = 200
    if url == ROBOTS_URL:
        content = b"User-agent: *\\nDisallow: /\\n" if CASE == "robots_deny" else b"User-agent: *\\nAllow: /\\n"
    elif url == FIXTURE_URL:
        if CASE == "unavailable":
            raise OSError("mock network unavailable")
        content = body
        if CASE == "http_failure": status, content = 404, b"mock missing"
        if CASE == "truncated": content = body[:100]
        if CASE == "malformed": content = b"{" + b" " * (len(body)-1)
        if CASE == "mismatch": content = body.replace(b'Market A', b'RUN CODE')
    else:
        raise AssertionError("unapproved mock request")
    return status, {"content-type":"text/plain"}, content, {"url":url,"http_status":status,"mocked_http":True}
server.download = fake
asyncio.run(server.main())
""".replace("CASE_VALUE", repr(case))
    params = StdioServerParameters(
        command=str(SERVER_PYTHON),
        args=["-c", script],
        cwd=str(ROOT),
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    logfile = tmp_path / "mocked-http.log"
    with logfile.open("w") as diagnostics:
        async with asyncio.timeout(20):
            async with Client(
                stdio_client(params, errlog=diagnostics), mode="legacy", read_timeout_seconds=10
            ) as client:
                result = await client.call_tool("fetch", dict(FETCH_ARGS))
                data = result.model_dump(mode="json", by_alias=True)
                if case == "allowed":
                    assert verify_tool_result(data)["synthetic"] is True
                else:
                    with pytest.raises(RetrievalRejected):
                        verify_tool_result(data)
                if case in {"robots_deny", "unavailable", "http_failure"}:
                    assert result.is_error is True
    if case == "robots_deny":
        events = []
        for line in logfile.read_text().splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        assert [e["url"] for e in events if e["event"] == "outbound_http"] == [ROBOTS_URL]
