from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bugbay.diagnosis import Diagnosis


@dataclass
class RepairResult:
    applied: bool
    source_file: str
    description: str
    original_content: str | None = None


def is_safe_source_path(source_file: str) -> bool:
    project_root = Path.cwd().resolve()
    source_path = Path(source_file).resolve()

    try:
        source_path.relative_to(project_root)
    except ValueError:
        return False

    return True


def rollback_repair(repair: RepairResult) -> bool:
    if not repair.applied or repair.original_content is None:
        return False

    source_path = Path(repair.source_file)

    if not source_path.exists():
        return False

    source_path.write_text(repair.original_content)
    return True


def repair_missing_dependency(
    diagnosis: Diagnosis,
    replacement_module: str,
) -> RepairResult:
    if not diagnosis.repairable:
        return RepairResult(
            applied=False,
            source_file=diagnosis.source_file or "",
            description="Diagnosis is not safely repairable.",
        )

    if not diagnosis.source_file or not diagnosis.missing_module:
        return RepairResult(
            applied=False,
            source_file=diagnosis.source_file or "",
            description="Required diagnosis information is missing.",
        )

    source_path = Path(diagnosis.source_file)

    if not is_safe_source_path(diagnosis.source_file):
        return RepairResult(
            applied=False,
            source_file=str(source_path),
            description="Source file is outside the allowed project boundary.",
        )

    if not source_path.exists():
        return RepairResult(
            applied=False,
            source_file=str(source_path),
            description="Source file does not exist.",
        )

    original = source_path.read_text()

    expected_import = f"import {diagnosis.missing_module}"

    if expected_import not in original:
        return RepairResult(
            applied=False,
            source_file=str(source_path),
            description="Expected missing import was not found.",
        )

    repaired = original.replace(
        expected_import,
        f"import {replacement_module} as {diagnosis.missing_module}",
        1,
    )

    if repaired == original:
        return RepairResult(
            applied=False,
            source_file=str(source_path),
            description="No change was produced.",
        )

    source_path.write_text(repaired)

    return RepairResult(
        applied=True,
        source_file=str(source_path),
        description=(
            f"Replaced missing dependency "
            f"'{diagnosis.missing_module}' with "
            f"controlled module '{replacement_module}'."
        ),
        original_content=original,
    )
