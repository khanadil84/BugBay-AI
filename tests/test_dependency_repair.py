from pathlib import Path

from bugbay.diagnosis import Diagnosis
from bugbay.repair import repair_missing_dependency


def test_missing_dependency_repair_replaces_expected_import() -> None:
    target = Path("tests") / "_temporary_dependency_target.py"

    original = (
        "import missing_dependency\n"
        "\n"
        "print('application started')\n"
    )

    target.write_text(original)

    diagnosis = Diagnosis(
        error_type="ModuleNotFoundError",
        message="ModuleNotFoundError: No module named 'missing_dependency'",
        source_file=str(target),
        line_number=1,
        missing_module="missing_dependency",
        missing_variable=None,
        repairable=True,
    )

    result = repair_missing_dependency(
        diagnosis,
        "bugbay_dependency_fallback",
        Path.cwd(),
    )

    assert result.applied is True
    assert target.read_text() == (
        "import bugbay_dependency_fallback as missing_dependency\n"
        "\n"
        "print('application started')\n"
    )

    target.unlink()
