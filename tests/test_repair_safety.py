from pathlib import Path
from bugbay.diagnosis import Diagnosis
from bugbay.repair import repair_missing_dependency


def test_repair_rejects_source_outside_project() -> None:
    diagnosis = Diagnosis(
        error_type="ModuleNotFoundError",
        message="ModuleNotFoundError: No module named 'missing_dependency'",
        source_file="/tmp/outside.py",
        line_number=1,
        missing_module="missing_dependency",
        missing_variable=None,
        repairable=True,
    )

    result = repair_missing_dependency(
        diagnosis,
        "bugbay_dependency_fallback",
    )

    assert result.applied is False
    assert result.description == (
        "Source file is outside the allowed project boundary."
    )


def test_repair_rejects_unexpected_source_content(tmp_path) -> None:
    source = Path("tests/target.py")
    source.write_text("print('safe content')\n")

    diagnosis = Diagnosis(
        error_type="ModuleNotFoundError",
        message="ModuleNotFoundError: No module named 'missing_dependency'",
        source_file=str(source),
        line_number=1,
        missing_module="missing_dependency",
        missing_variable=None,
        repairable=True,
    )

    result = repair_missing_dependency(
        diagnosis,
        "bugbay_dependency_fallback",
    )

    assert result.applied is False
    assert result.description == (
        "Expected missing import was not found."
    )
