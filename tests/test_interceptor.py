from pathlib import Path

from bugbay.interceptor import run_target


def test_run_target_captures_runtime_failure() -> None:
    target = Path("fixtures/permanent_failure.py")

    result = run_target(target)

    assert result.success is False
    assert result.exit_code != 0
    assert result.stdout == ""
    assert "Permanent controlled failure" in result.stderr
    assert result.command[0].endswith("python")
    assert result.command[-1].endswith("fixtures/permanent_failure.py")
    assert result.duration_seconds >= 0
