"""Create ignored local demo credentials once, without printing a token."""

import hashlib
import json
import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATH = ROOT / ".env.token.local"
CONFIG_PATH = ROOT / ".env.officers.local"


def main() -> None:
    if TOKEN_PATH.exists() or CONFIG_PATH.exists():
        raise SystemExit("Local credentials already exist; preserved without changes.")
    token = secrets.token_urlsafe(32)
    with os.fdopen(os.open(TOKEN_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as file:
        file.write(token)
    with os.fdopen(os.open(CONFIG_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as file:
        file.write(
            json.dumps(
                {
                    "officers": [
                        {
                            "id": "test:local-demo-officer",
                            "token_sha256": hashlib.sha256(token.encode()).hexdigest(),
                            "workflows": [],
                            "workflow_prefix": "demo-",
                        }
                    ]
                },
                indent=2,
            )
            + "\n"
        )
    print("Ignored local test-officer configuration created. Token contents were not printed.")


if __name__ == "__main__":
    main()
