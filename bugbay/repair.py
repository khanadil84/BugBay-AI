from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tempfile

from bugbay.diagnosis import Diagnosis


@dataclass
class RepairResult:
    applied: bool
    source_file: str
    description: str
    original_content: str | None = None


def is_safe_source_path(source_file: str, project_root: Path) -> bool:
    project_root = project_root.resolve()
    source_path = Path(source_file).resolve()

    try:
        source_path.relative_to(project_root)
    except ValueError:
        return False

    return True


def atomic_write_text(path: Path, content: str) -> None:
    directory = path.parent

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=directory,
        delete=False,
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)

    try:
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def rollback_repair(repair: RepairResult) -> bool:
    if not repair.applied or repair.original_content is None:
        return False

    source_path = Path(repair.source_file)

    if not source_path.exists():
        return False

    atomic_write_text(source_path, repair.original_content)
    return True


def repair_missing_dependency(
    diagnosis: Diagnosis,
    replacement_module: str,
    project_root: Path,
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

    if not is_safe_source_path(diagnosis.source_file, project_root):
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
    source_lines = original.splitlines()

    if (
        diagnosis.line_number is None
        or diagnosis.line_number < 1
        or diagnosis.line_number > len(source_lines)
    ):
        return RepairResult(
            applied=False,
            source_file=str(source_path),
            description="Diagnosed source line is outside the source file.",
        )

    expected_import = f"import {diagnosis.missing_module}"

    if source_lines[diagnosis.line_number - 1].strip() != expected_import:
        return RepairResult(
            applied=False,
            source_file=str(source_path),
            description="Diagnosed source line does not contain the expected missing import.",
        )

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

    atomic_write_text(source_path, repaired)

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


def repair_missing_variable(
    diagnosis: Diagnosis,
    replacement_value: str,
    project_root: Path,
) -> RepairResult:
    if not diagnosis.repairable:
        return RepairResult(
            applied=False,
            source_file=diagnosis.source_file or "",
            description="Diagnosis is not safely repairable.",
        )

    if not diagnosis.source_file or not diagnosis.missing_variable:
        return RepairResult(
            applied=False,
            source_file=diagnosis.source_file or "",
            description="Required missing-variable information is missing.",
        )

    source_path = Path(diagnosis.source_file)

    if not is_safe_source_path(diagnosis.source_file, project_root):
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

    declaration = (
        f"{diagnosis.missing_variable} = "
        f"{replacement_value!r}\n"
    )

    repaired = declaration + original

    atomic_write_text(source_path, repaired)

    return RepairResult(
        applied=True,
        source_file=str(source_path),
        description=(
            f"Defined missing variable "
            f"'{diagnosis.missing_variable}' "
            f"with an explicit controlled value."
        ),
        original_content=original,
    )
