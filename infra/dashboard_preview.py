"""Recording preview over an existing isolated snapshot; never copies/resets state."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from backend.app.api.review import create_app

ROOT = Path(__file__).resolve().parents[1]


def isolated_state(state: Path, original: Path) -> Path:
    if not state.is_file():
        raise RuntimeError("Existing preview snapshot required; no automatic initialization")
    if state.resolve() == original.resolve() or (
        original.exists() and os.path.samefile(state, original)
    ):
        raise RuntimeError("Preview must not use the original database")
    return state


def build_version(dist: Path, revision: str) -> dict:
    version = json.loads((dist / "version.json").read_text())
    if version["git_sha"] != revision:
        raise RuntimeError("Frontend build must match the checked-out recording revision")
    for relative, digest in version["assets_sha256"].items():
        file = (dist / relative).resolve()
        if not file.is_relative_to(dist.resolve()) or not file.is_file():
            raise RuntimeError("Invalid frontend build artifact")
        if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Frontend build artifact hash mismatch")
    return version


def local_app():
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
            "backend",
            "frontend",
            "infra/dashboard_preview.py",
        ],
        cwd=ROOT,
        check=True,
    )
    state = isolated_state(
        ROOT / ".state/dashboard-preview.sqlite", ROOT / ".state/quick-demo.sqlite"
    )
    config = ROOT / ".env.officers.quick-demo.local"
    dist = ROOT / "frontend/dist-dashboard"
    version = build_version(dist, revision)
    app = create_app(state, config)
    app.router.routes = [
        route for route in app.router.routes if getattr(route, "name", "") != "demo-frontend"
    ]

    @app.get("/api/v1/preview-version")
    def recording_version():
        return {"backend_git_sha": revision, "frontend": version}

    app.mount("/", StaticFiles(directory=dist, html=True), name="recording-preview")
    return app
