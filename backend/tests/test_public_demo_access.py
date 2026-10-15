"""The published sample code cannot reveal or grant ordinary officer access."""

import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from backend.app.api.review import create_app


def roster(tmp_path, **changes):
    officer = {
        "id": "test:public-demo",
        "token_sha256": hashlib.sha256(b"sample-code").hexdigest(),
        "workflows": [],
        "workflow_prefix": "public-demo-",
    }
    officer.update(changes)
    config = tmp_path / "officers.json"
    config.write_text(json.dumps({"officers": [officer]}))
    return config


def test_public_demo_is_opt_in_and_private_credentials_are_never_returned(tmp_path):
    config = roster(tmp_path, id="real-officer")
    with TestClient(create_app(tmp_path / "state.sqlite", config)) as client:
        assert client.get("/api/v1/demo-access").json() == {"enabled": False}
        assert client.get("/api/v1/drafts/pending").status_code == 401


@pytest.mark.parametrize(
    "changes",
    [
        {"id": "real-officer"},
        {"workflows": ["private-officer-draft"]},
        {"workflow_prefix": "quick-demo-"},
        {"token_sha256": "a" * 64},
    ],
)
def test_publication_refuses_private_or_broader_authority(tmp_path, changes):
    with pytest.raises(ValueError, match="restricted test-officer roster"):
        create_app(
            tmp_path / "state.sqlite", roster(tmp_path, **changes), public_demo_token="sample-code"
        )


def test_sample_code_authenticates_only_disjoint_demo_scope(tmp_path):
    with TestClient(
        create_app(tmp_path / "state.sqlite", roster(tmp_path), public_demo_token="sample-code")
    ) as client:
        assert client.get("/api/v1/demo-access").json() == {
            "enabled": True,
            "token": "sample-code",
            "shared": True,
        }
        assert client.get("/api/v1/drafts/pending").status_code == 401
        headers = {"Authorization": "Bearer sample-code"}
        pending = client.get("/api/v1/drafts/pending", headers=headers)
        assert pending.status_code == 200
        assert pending.json() == {
            "reviewer": {"id": "test:public-demo", "demo": True},
            "drafts": [],
        }
        for suffix in ("", "/draft", "/events", "/decisions"):
            path = f"/api/v1/runs/quick-demo-private{suffix}"
            response = (
                client.post(
                    path,
                    headers=headers,
                    json={
                        "draft_id": "private",
                        "version": 1,
                        "content_hash": "a" * 64,
                        "decision": "approve",
                        "idempotency_key": "attempt",
                    },
                )
                if suffix == "/decisions"
                else client.get(path, headers=headers)
            )
            assert response.status_code == 403
