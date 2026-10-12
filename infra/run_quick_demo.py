"""Run only the authorized protected connector under a hard, bounded watchdog."""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
LIMIT_SECONDS = 3590  # Ten-second margin within the owner's maximum 3,600 seconds.
EXPECTED_SHA = "d33ff2d14475178d2012c2c56beba87389ac5ded27649519f198a7d3134a99db"


def bounded_command(command: list[str], seconds: int = LIMIT_SECONDS) -> list[str]:
    if not 0 < seconds <= LIMIT_SECONDS:
        raise ValueError("Connector duration exceeds the authorized bound")
    return ["/usr/bin/timeout", "--foreground", "--signal=KILL", f"{seconds}s", *command]


def main() -> None:
    binary = ROOT / ".cache/cloudflared/2026.10.0/cloudflared"
    if hashlib.sha256(binary.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise SystemExit("Connector checksum mismatch; launch refused")
    if any(k.startswith("TUNNEL_") or k in {"NO_AUTOUPDATE", "NO_TLS_VERIFY"} for k in os.environ):
        raise SystemExit("Inherited tunnel overrides present; launch refused")
    email_file = ROOT / ".env.quick-mail.local"
    config = ROOT / ".env.quick-tunnel.local.yml"
    if config.read_text().strip() != "{}":
        raise SystemExit("Unexpected tunnel config; launch refused")
    for path in [email_file, config]:
        if path.stat().st_mode & 0o777 != 0o600:
            raise SystemExit("Private launch-file permissions are not 0600")
    email = email_file.read_text().strip()
    # The request authorizes one exact owner address; pin its hash without publishing it.
    expected_email = "64f74a25efdd8d42a0bc0c62af6210fd898b843d59a0721f18d5a6449218e583"
    if hashlib.sha256(email.encode()).hexdigest() != expected_email:
        raise SystemExit("Email allowlist differs from authorized single address")
    command = [
        str(binary),
        "tunnel",
        "--config",
        str(config),
        "--no-autoupdate",
        "--loglevel",
        "info",
        "--metrics",
        "127.0.0.1:20241",
        "--url",
        "http://127.0.0.1:8000",
        "--allowed-mail",
        email,
    ]
    state_dir = ROOT / ".state/quick-tunnel"
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    run_file = state_dir / "run.local.json"
    if run_file.exists():
        raise SystemExit("Existing connector run evidence preserved; no relaunch")
    log_fd = os.open(state_dir / "connector.local.log", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    started = datetime.now(ZoneInfo("Africa/Nairobi"))
    record = {
        "started_at_nairobi": started.isoformat(),
        "planned_expiry_nairobi": (started + timedelta(seconds=LIMIT_SECONDS)).isoformat(),
        "limit_seconds": LIMIT_SECONDS,
        "origin": "http://127.0.0.1:8000",
        "allowed_address_count": 1,
        "wildcard_rules": 0,
    }
    with os.fdopen(log_fd, "w") as log:
        process = subprocess.Popen(bounded_command(command), stdout=log, stderr=log, cwd=ROOT)
        record["watchdog_pid"] = process.pid
        with os.fdopen(
            os.open(run_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
        ) as output:
            json.dump(record, output, indent=2)
        print(json.dumps(record), flush=True)
        # Stop the exact connector PID separately if access checks fail.
        # The bounded timeout remains alive if this supervisor is interrupted;
        # no application or model PID is managed here.
        returncode = process.wait()
    record.update(
        {
            "watchdog_exit_code": returncode,
            "stopped_at_nairobi": datetime.now(ZoneInfo("Africa/Nairobi")).isoformat(),
        }
    )
    run_file.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
