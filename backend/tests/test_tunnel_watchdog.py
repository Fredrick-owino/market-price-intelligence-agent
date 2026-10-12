"""Watchdog targets only its owned foreground child; no network exposure."""

import subprocess
import sys
import time

import pytest

from infra.run_quick_demo import bounded_command


def test_watchdog_hard_stops_owned_child_and_preserves_other_service():
    service = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        started = time.monotonic()
        result = subprocess.run(
            bounded_command([sys.executable, "-c", "import time; time.sleep(30)"], seconds=1),
            timeout=4,
            check=False,
        )
        assert result.returncode == 124
        assert time.monotonic() - started < 3
        assert service.poll() is None
    finally:
        service.terminate()
        service.wait(timeout=3)


@pytest.mark.parametrize("seconds", [0, -1, 3591, 3600])
def test_watchdog_rejects_unbounded_duration(seconds):
    with pytest.raises(ValueError):
        bounded_command(["never-executed"], seconds)
