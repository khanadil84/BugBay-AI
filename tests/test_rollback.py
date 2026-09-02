from pathlib import Path

from bugbay.repair import RepairResult, rollback_repair


def test_rollback_restores_original_file(tmp_path: Path) -> None:
    target = tmp_path / "target.py"

    original = 'print("original")\n'
    repaired = 'print("repaired")\n'

    target.write_text(repaired)

    repair = RepairResult(
        applied=True,
        source_file=str(target),
        description="Automated rollback test",
        original_content=original,
    )

    result = rollback_repair(repair)

    assert result is True
    assert target.read_text() == original
