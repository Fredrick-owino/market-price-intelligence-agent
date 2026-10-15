"""Recording preview must preserve isolation and reject mismatched build evidence."""

import hashlib
import json
import os

import pytest

from infra.dashboard_preview import build_version, isolated_state


def test_preview_requires_existing_distinct_state(tmp_path):
    original = tmp_path / "original.sqlite"
    original.write_bytes(b"preserved original")
    missing = tmp_path / "preview.sqlite"
    with pytest.raises(RuntimeError, match="Existing preview"):
        isolated_state(missing, original)
    assert not missing.exists()
    with pytest.raises(RuntimeError, match="original database"):
        isolated_state(original, original)
    alias = tmp_path / "alias.sqlite"
    os.link(original, alias)
    with pytest.raises(RuntimeError, match="original database"):
        isolated_state(alias, original)
    missing.write_bytes(b"isolated existing snapshot")
    assert isolated_state(missing, original) == missing
    assert original.read_bytes() == b"preserved original"


def test_preview_rejects_revision_or_asset_mismatch(tmp_path):
    (tmp_path / "index.html").write_text("test build")
    manifest = {
        "git_sha": "a" * 40,
        "assets_sha256": {"index.html": hashlib.sha256(b"test build").hexdigest()},
    }
    (tmp_path / "version.json").write_text(json.dumps(manifest))
    assert build_version(tmp_path, "a" * 40) == manifest
    with pytest.raises(RuntimeError, match="recording revision"):
        build_version(tmp_path, "b" * 40)
    (tmp_path / "index.html").write_text("changed build")
    with pytest.raises(RuntimeError, match="hash mismatch"):
        build_version(tmp_path, "a" * 40)
    manifest["assets_sha256"] = {"../outside.html": "unused"}
    (tmp_path / "version.json").write_text(json.dumps(manifest))
    with pytest.raises(RuntimeError, match="Invalid frontend"):
        build_version(tmp_path, "a" * 40)
