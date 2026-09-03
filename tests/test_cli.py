import subprocess
import sys


def test_cli_requires_target() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bugbay"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "target" in result.stderr.lower()


def test_cli_runs_target_and_reports_success() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bugbay",
            "fixtures/retry_failure.py",
            "--max-retries",
            "3",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "BugBay" in result.stdout
    assert "BUGBAY RESULT: SUCCESS" in result.stdout
