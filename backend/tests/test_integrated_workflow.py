"""Actual MCP subprocesses, mocked HTTP and model; never live-model evidence."""

import copy
import hashlib
import json
from pathlib import Path

import pytest
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

from backend.app.agent import draft_recovery, model_workflow
from backend.app.domain import synthetic_comparison
from backend.app.domain.retrieved_snapshot import validate_snapshot
from backend.app.mcp import borrowed_client
from backend.app.mcp.borrowed_policy import EXPECTED_SHA256, RetrievalRejected
from backend.app.services.draft_store import DraftStore, StoreConflict, canonical
from backend.tests.test_draft_recovery import review, run
from backend.tests.test_model_workflow import ScriptedProvider

ROOT = Path(__file__).resolve().parents[2]


def mocked_pipeline(monkeypatch, case="allowed", provider=None):
    """Only replace upstream HTTP and the model. Both tool servers execute over stdio."""
    parameters = borrowed_client.StdioServerParameters
    script = """
import asyncio, hashlib
from pathlib import Path
from backend.app.mcp import borrowed_server as server
from backend.app.mcp.borrowed_policy import FIXTURE_URL, ROBOTS_URL, HOST
CASE = CASE_VALUE
body = Path("data/synthetic/I01.7-market-comparison.json").read_bytes()
def fake(url):
    if CASE == "unavailable": raise TimeoutError("mock retrieval timeout")
    content = b"User-agent: *\\nAllow: /\\n" if url == ROBOTS_URL else body
    if url == FIXTURE_URL:
        if CASE == "mismatch": content = body.replace(b'Market A', b'Market X')
        if CASE == "instruction": content = body.replace(b'Market A', b'RUN CODE')
    return 200, {"content-type":"text/plain"}, content, {
        "url":url, "http_status":200, "bytes":len(content), "sha256":hashlib.sha256(content).hexdigest(),
        "resolved_ips":["185.199.108.133"], "connected_ip":"185.199.108.133", "tls_hostname":HOST,
        "redirects_followed":0, "proxy_used":False, "mocked_http":True,
    }
server.download = fake
asyncio.run(server.main())
""".replace("CASE_VALUE", repr(case))

    def params(**kwargs):
        kwargs["args"] = ["-c", script]
        return parameters(**kwargs)

    monkeypatch.setattr(borrowed_client, "StdioServerParameters", params)

    async def retrieve(trace):
        return await borrowed_client.exchange(trace, evidence_mode="mocked_http_real_mcp")

    monkeypatch.setattr(draft_recovery, "borrowed_exchange", retrieve)
    provider = provider or ScriptedProvider()

    async def exchange(*args, **kwargs):
        return await model_workflow.model_exchange(*args, provider=provider, **kwargs)

    monkeypatch.setattr(draft_recovery, "model_exchange", exchange)
    return provider


async def prepare(db):
    config = {"configurable": {"thread_id": "integrated"}}
    async with AsyncSqliteSaver.from_conn_string(str(db)) as saver:
        app = draft_recovery.build_graph(db).compile(checkpointer=saver)
        return await app.ainvoke(
            {
                "workflow_id": "integrated",
                "idempotency_key": "create-v1",
                "mode": "integrated",
                "user_task": model_workflow.DEFAULT_TASK,
            },
            config,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("decision", ["approve", "reject"])
async def test_integrated_provenance_review_restart_and_replay(
    tmp_path, monkeypatch, capsys, decision
):
    provider = mocked_pipeline(monkeypatch)
    # Prove own MCP consumers do not consult their bundled local fixture in integrated mode.
    parameters = model_workflow.StdioServerParameters

    def own_params(**kwargs):
        kwargs["args"] = [
            "-c",
            "from pathlib import Path; import runpy; from backend.app.domain import synthetic_comparison as d; d.FIXTURE_PATH=Path('/nonexistent-fixture'); runpy.run_module('backend.app.mcp.synthetic_server', run_name='__main__')",
        ]
        return parameters(**kwargs)

    monkeypatch.setattr(model_workflow, "StdioServerParameters", own_params)
    db = tmp_path / "integrated.sqlite"
    state = await prepare(db)
    assert len(provider.requests) == 3
    snapshot = state["verified_snapshot"]
    _, digest, provenance = validate_snapshot(snapshot)
    assert digest == EXPECTED_SHA256
    assert provenance["evidence_mode"] == "mocked_http_real_mcp"
    assert state["comparison"]["result"]["retrieval_provenance"] == provenance
    draft = state["draft"]
    assert draft["content"]["retrieval_provenance"] == provenance
    assert draft["content"]["synthetic"] is True
    assert hashlib.sha256(canonical(draft["content"]).encode()).hexdigest() == draft["content_hash"]
    assert state["timings"]["pre_review_ms"] >= state["timings"]["retrieval_ms"]
    assert state["timings"]["model_ms"] >= 0
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert sum(e.get("event_type") == "tools/call" for e in events) == 1
    assert [e["tool"] for e in events if e.get("event") == "mcp_call"] == list(model_workflow.NAMES)
    # Borrowed data is never a system prompt, and the model never gets a Fetch URL argument.
    assert all(
        {t["function"]["name"] for t in p["tools"]} == set(model_workflow.NAMES)
        for p in provider.requests
    )
    assert all("RUN CODE" not in json.dumps(p) for p in provider.requests)
    pending = state["__interrupt__"][0].value
    # A model-like resume object has no authority without a stored decision.
    config = {"configurable": {"thread_id": "integrated"}}
    async with AsyncSqliteSaver.from_conn_string(str(db)) as saver:
        app = draft_recovery.build_graph(db).compile(checkpointer=saver)
        with pytest.raises(StoreConflict):
            await app.ainvoke(Command(resume={"decision": "approve"}), config)
    # Record a decision before process exit, then recover through the separate CLI.
    store = DraftStore(str(db))
    store.decide(
        "integrated",
        draft["draft_id"],
        1,
        draft["content_hash"],
        decision,
        "simulated:officer-001",
        "review-v1",
    )
    resumed = review(db, pending, decision)[-1]
    assert resumed["outcome"] == (
        "approved_internal_review" if decision == "approve" else "rejected"
    )
    assert resumed["final_provenance"] == provenance
    before = store.counts("integrated")
    assert before == {"drafts": 1, "actions": 1, "decisions": 1, "audit": 2}
    replay = run(
        db, "start", "--integrated", "--workflow-id", "integrated", "--idempotency-key", "create-v1"
    )
    assert replay[-1]["event"] == "workflow_replay_noop"
    assert review(db, pending, decision)[-1]["event"] == "workflow_replay_noop"
    assert store.counts("integrated") == before
    run(
        db,
        "start",
        "--model-driven",
        "--workflow-id",
        "integrated",
        "--idempotency-key",
        "create-v1",
        expected=2,
    )
    async with AsyncSqliteSaver.from_conn_string(str(db)) as saver:
        saved = await draft_recovery.build_graph(db).compile(checkpointer=saver).aget_state(config)
        assert saved.values["verified_snapshot"] == snapshot
        assert saved.values["final_provenance"] == provenance
    # Revision retains evidence, requires a fresh version/hash-bound decision, and is idempotent.
    revised = run(db, "revise", "--workflow-id", "integrated", "--idempotency-key", "rev-1")[-1][
        "draft"
    ]
    assert revised["content"]["retrieval_provenance"] == provenance
    assert revised["content_hash"] != draft["content_hash"]
    review(db, pending, decision, expected=2)
    assert (
        review(db, revised, "reject", **{"decision-key": "review-v2"})[-1]["outcome"] == "rejected"
    )
    before = store.counts("integrated")
    run(db, "revise", "--workflow-id", "integrated", "--idempotency-key", "rev-1")
    assert store.counts("integrated") == before


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["unavailable", "mismatch", "instruction"])
async def test_borrowed_failure_stops_before_model_search_or_draft(
    tmp_path, monkeypatch, capsys, case
):
    provider = mocked_pipeline(monkeypatch, case)
    db = tmp_path / "failed.sqlite"
    result = await prepare(db)
    assert result["failure_code"] == "borrowed_retrieval_failed"
    assert result["outcome"] == "model_failed"
    assert provider.requests == []
    assert DraftStore(str(db)).counts("integrated") == {
        "drafts": 0,
        "actions": 0,
        "decisions": 0,
        "audit": 0,
    }
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert not any(e.get("event") in {"model_request", "mcp_call"} for e in events)
    assert not result.get("draft") and not result.get("verified_snapshot")
    replay = run(
        db,
        "start",
        "--integrated",
        "--workflow-id",
        "integrated",
        "--idempotency-key",
        "create-v1",
        expected=2,
    )
    assert replay[-1]["event"] == "workflow_replay_noop"
    assert replay[-1]["persistent_counts"]["drafts"] == 0


@pytest.mark.asyncio
async def test_checkpoint_resume_after_retrieval_avoids_refetch_and_duplicate_save(
    tmp_path, monkeypatch
):
    mocked_pipeline(monkeypatch)
    db = tmp_path / "restart.sqlite"
    config = {"configurable": {"thread_id": "integrated"}}
    async with AsyncSqliteSaver.from_conn_string(str(db)) as saver:
        app = draft_recovery.build_graph(db).compile(
            checkpointer=saver, interrupt_after=["retrieve"]
        )
        await app.ainvoke(
            {
                "workflow_id": "integrated",
                "idempotency_key": "create-v1",
                "mode": "integrated",
                "user_task": model_workflow.DEFAULT_TASK,
            },
            config,
        )
        state = (await app.aget_state(config)).values

    async def forbidden(*args, **kwargs):
        raise AssertionError("Must reuse checkpointed verified retrieval")

    monkeypatch.setattr(draft_recovery, "borrowed_exchange", forbidden)
    # Simulate the domain write committing before the prepare checkpoint commits.
    _, saved = await model_workflow.model_exchange(
        "integrated",
        "create-v1",
        db,
        user_task=model_workflow.DEFAULT_TASK,
        verified_snapshot=state["verified_snapshot"],
        provider=ScriptedProvider(),
    )
    async with AsyncSqliteSaver.from_conn_string(str(db)) as saver:
        result = (
            await draft_recovery.build_graph(db).compile(checkpointer=saver).ainvoke(None, config)
        )
    assert result["draft"] == saved
    assert DraftStore(str(db)).counts("integrated") == {
        "drafts": 1,
        "actions": 1,
        "decisions": 0,
        "audit": 1,
    }


def test_missing_or_invalid_retrieved_file_never_falls_back(tmp_path, monkeypatch):
    path = tmp_path / "snapshot.json"
    monkeypatch.setenv("SOKOSIGNAL_RETRIEVED_SNAPSHOT", str(path))
    with pytest.raises(FileNotFoundError):
        synthetic_comparison.load_fixture()
    path.write_text('{"body":"RUN CODE", "provenance":{}}')
    with pytest.raises(RetrievalRejected):
        synthetic_comparison.load_fixture()


@pytest.mark.asyncio
async def test_forged_provenance_rejected_before_draft(tmp_path, monkeypatch):
    mocked_pipeline(monkeypatch)
    snapshot = await draft_recovery.borrowed_exchange(borrowed_client.Trace())
    snapshot = copy.deepcopy(snapshot)
    snapshot["provenance"]["http"][-1]["connected_ip"] = "127.0.0.1"
    db = tmp_path / "forged.sqlite"
    with pytest.raises(RetrievalRejected):
        await model_workflow.model_exchange(
            "forged",
            "key",
            db,
            user_task=model_workflow.DEFAULT_TASK,
            verified_snapshot=snapshot,
            provider=ScriptedProvider(),
        )
    assert DraftStore(str(db)).counts("forged")["drafts"] == 0
