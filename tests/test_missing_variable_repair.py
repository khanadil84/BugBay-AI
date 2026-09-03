from pathlib import Path

from bugbay.diagnosis import Diagnosis
from bugbay.repair import repair_missing_variable


def test_missing_variable_repair_uses_explicit_value(tmp_path: Path) -> None:
    target = Path("tests") / "_temporary_missing_variable_target.py"

    target.write_text(
        'def start_application():\n'
        '    print(database_connection)\n'
        '\n'
        'start_application()\n'
    )

    diagnosis = Diagnosis(
        error_type="NameError",
        message="NameError: name 'database_connection' is not defined",
        source_file=str(target),
        line_number=2,
        missing_module=None,
        missing_variable="database_connection",
        repairable=True,
    )

    result = repair_missing_variable(
        diagnosis,
        "BUGBAY_DATABASE_CONNECTION",
    )

    assert result.applied is True
    assert "database_connection = 'BUGBAY_DATABASE_CONNECTION'" in (
        target.read_text()
    )
    target.unlink()
