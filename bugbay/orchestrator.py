from __future__ import annotations

from pathlib import Path

from bugbay.diagnosis import diagnose
from bugbay.interceptor import run_target
from bugbay.manifest import write_manifest
from bugbay.repair import repair_missing_dependency, repair_missing_variable, rollback_repair
from bugbay.verifier import verify_runtime


def run_recovery(
    target: Path,
    manifest_path: Path,
    replacement_module: str,
) -> bool:
    # 1. Detect and capture the runtime failure.
    initial = run_target(target)

    if initial.success:
        print("TARGET ALREADY PASSED")
        return True

    # 2. Diagnose the captured failure.
    diagnosis = diagnose(initial.stderr)

    print("ERROR TYPE:", diagnosis.error_type)
    print("MISSING MODULE:", diagnosis.missing_module)
    print("MISSING VARIABLE:", diagnosis.missing_variable)
    print("REPAIRABLE:", diagnosis.repairable)

    # 3. Select a bounded repair based on the diagnosed failure class.
    if diagnosis.error_type == "ModuleNotFoundError":
        repair = repair_missing_dependency(
            diagnosis,
            replacement_module,
        )
    elif diagnosis.error_type == "NameError":
        repair = repair_missing_variable(
            diagnosis,
            "BUGBAY_DATABASE_CONNECTION",
        )
    else:
        repair = repair_missing_dependency(
            diagnosis,
            replacement_module,
        )

    print("REPAIR APPLIED:", repair.applied)

    if not diagnosis.repairable:
        write_manifest(
            manifest_path,
            target=str(target),
            diagnosis=diagnosis.__dict__,
            repair=repair.__dict__,
            verification={
                "passed": False,
                "exit_code": initial.exit_code,
                "stdout": initial.stdout,
                "stderr": initial.stderr,
                "duration_seconds": initial.duration_seconds,
            },
        )
        return False

    if not repair.applied:
        write_manifest(
            manifest_path,
            target=str(target),
            diagnosis=diagnosis.__dict__,
            repair=repair.__dict__,
            verification={
                "passed": False,
                "exit_code": initial.exit_code,
                "stdout": initial.stdout,
                "stderr": initial.stderr,
                "duration_seconds": initial.duration_seconds,
            },
        )
        return False

    # 4. Re-run and independently verify.
    verification = verify_runtime(target)

    print("VERIFICATION PASSED:", verification.passed)

    rolled_back = False

    if not verification.passed:
        rolled_back = rollback_repair(repair)
        print("ROLLBACK APPLIED:", rolled_back)

    # 5. Persist the complete recovery evidence.
    write_manifest(
        manifest_path,
        target=str(target),
        diagnosis=diagnosis.__dict__,
        repair=repair.__dict__,
        verification={
            **verification.__dict__,
            "before": {
                "exit_code": initial.exit_code,
                "stdout": initial.stdout,
                "stderr": initial.stderr,
                "passed": initial.success,
            },
            "after": {
                "exit_code": verification.exit_code,
                "stdout": verification.stdout,
                "stderr": verification.stderr,
                "passed": verification.passed,
            },
            "rollback": {
                "applied": rolled_back,
            },
        },
    )

    return verification.passed


if __name__ == "__main__":
    target = Path("fixtures/dependency_failure.py")
    manifest = Path("manifests/diagnostic-manifest.json")

    success = run_recovery(
        target=target,
        manifest_path=manifest,
        replacement_module="bugbay_dependency_fallback",
    )

    raise SystemExit(0 if success else 1)
