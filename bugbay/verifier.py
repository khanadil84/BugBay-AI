from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bugbay.interceptor import run_target


@dataclass
class VerificationResult:
    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


def verify_runtime(target: Path) -> VerificationResult:
    result = run_target(target)

    return VerificationResult(
        passed=result.success,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_seconds=result.duration_seconds,
    )
