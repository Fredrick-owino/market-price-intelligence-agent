"""Explicit public-token sample workspace, isolated from private officer state."""

import hashlib
import json
from pathlib import Path

from backend.app.api.review import create_app

ROOT = Path(__file__).resolve().parents[1]
# Intentionally public, sample-only access code; never a private officer credential.
DEMO_TOKEN = "SOKO-DEMO"


def local_app():
    directory = ROOT / ".state/public-demo"
    directory.mkdir(parents=True, exist_ok=True)
    config = directory / "officers.json"
    if not config.exists():
        with config.open("x", encoding="utf-8") as file:
            json.dump(
                {
                    "officers": [
                        {
                            "id": "test:public-demo",
                            "token_sha256": hashlib.sha256(DEMO_TOKEN.encode()).hexdigest(),
                            "workflows": [],
                            "workflow_prefix": "public-demo-",
                        }
                    ]
                },
                file,
            )
    return create_app(directory / "demo.sqlite", config, public_demo_token=DEMO_TOKEN)
