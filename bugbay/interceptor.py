from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RuntimeResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def success(self) -> bool:
        return self.exit_code == 0


def run_target(target: Path) -> RuntimeResult:
    start = time.perf_counter()

    process = subprocess.run(
        [sys.executable, str(target)],
        capture_output=True,
        text=True,
    )

    duration = time.perf_counter() - start

    return RuntimeResult(
        command=[sys.executable, str(target)],
        exit_code=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
        duration_seconds=duration,
    )
