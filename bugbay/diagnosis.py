from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Diagnosis:
    error_type: str
    message: str
    source_file: str | None
    line_number: int | None
    missing_module: str | None
    missing_variable: str | None
    repairable: bool


TRACEBACK_FILE_PATTERN = re.compile(
    r'File "([^"]+)", line (\d+),'
)

MISSING_MODULE_PATTERN = re.compile(
    r"No module named ['\"]([^'\"]+)['\"]"
)

MISSING_VARIABLE_PATTERN = re.compile(
    r"name '([^']+)' is not defined"
)


def diagnose(stderr: str) -> Diagnosis:
    error_type = "UNKNOWN"
    message = ""
    source_file = None
    line_number = None
    missing_module = None
    missing_variable = None

    lines = [line.strip() for line in stderr.splitlines() if line.strip()]

    if lines:
        final_line = lines[-1]

        if final_line.startswith("ModuleNotFoundError:"):
            error_type = "ModuleNotFoundError"
            message = final_line

            match = MISSING_MODULE_PATTERN.search(final_line)
            if match:
                missing_module = match.group(1)

        elif final_line.startswith("NameError:"):
            error_type = "NameError"
            message = final_line

            match = MISSING_VARIABLE_PATTERN.search(final_line)
            if match:
                missing_variable = match.group(1)

        elif final_line.startswith("TypeError:"):
            error_type = "TypeError"
            message = final_line

    traceback_match = None

    for line in stderr.splitlines():
        match = TRACEBACK_FILE_PATTERN.search(line)
        if match:
            traceback_match = match

    if traceback_match:
        source_file = str(Path(traceback_match.group(1)))
        line_number = int(traceback_match.group(2))

    repairable = (
        (
            error_type == "ModuleNotFoundError"
            and missing_module is not None
        )
        or (
            error_type == "NameError"
            and missing_variable is not None
        )
    ) and source_file is not None and line_number is not None

    return Diagnosis(
        error_type=error_type,
        message=message,
        source_file=source_file,
        line_number=line_number,
        missing_module=missing_module,
        missing_variable=missing_variable,
        repairable=repairable,
    )
