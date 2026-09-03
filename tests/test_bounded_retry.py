from pathlib import Path

from bugbay.interceptor import run_target


def test_retry_fixture_requires_bounded_attempts():
    target = Path("fixtures/retry_failure.py")
    attempt_file = Path("manifests/retry-attempt.txt")

    attempt_file.unlink(missing_ok=True)

    results = []

    for _ in range(3):
        results.append(run_target(target))

    assert results[0].success is False
    assert results[1].success is False
    assert results[2].success is True

    attempt_file.unlink(missing_ok=True)


def test_orchestrator_retries_and_recovers(tmp_path):
    from bugbay.orchestrator import run_recovery

    target = Path("fixtures/retry_failure.py")
    attempt_file = Path("manifests/retry-attempt.txt")
    manifest = tmp_path / "diagnostic-manifest.json"

    attempt_file.unlink(missing_ok=True)

    result = run_recovery(
        target=target,
        manifest_path=manifest,
        replacement_module="bugbay_dependency_fallback",
        max_retries=3,
    )

    assert result is True
    assert attempt_file.read_text().strip() == "3"

    attempt_file.unlink(missing_ok=True)


def test_orchestrator_stops_at_retry_limit(tmp_path):
    from bugbay.orchestrator import run_recovery

    target = Path("fixtures/permanent_failure.py")
    manifest = tmp_path / "diagnostic-manifest.json"

    result = run_recovery(
        target=target,
        manifest_path=manifest,
        replacement_module="bugbay_dependency_fallback",
        max_retries=2,
    )

    assert result is False


def test_non_repairable_failure_writes_manifest(tmp_path):
    from bugbay.orchestrator import run_recovery

    target = Path("fixtures/permanent_failure.py")
    manifest = tmp_path / "diagnostic-manifest.json"

    result = run_recovery(
        target=target,
        manifest_path=manifest,
        replacement_module="bugbay_dependency_fallback",
        max_retries=2,
    )

    assert result is False
    assert manifest.exists()

    content = manifest.read_text()
    assert '"repairable": false' in content
    assert '"applied": false' in content
    assert "No safe repair strategy is available for this failure type." in content
    assert "Permanent controlled failure" in content


def test_successful_retry_writes_manifest(tmp_path):
    from bugbay.orchestrator import run_recovery

    target = Path("fixtures/retry_failure.py")
    attempt_file = Path("manifests/retry-attempt.txt")
    manifest = tmp_path / "diagnostic-manifest.json"

    attempt_file.unlink(missing_ok=True)

    result = run_recovery(
        target=target,
        manifest_path=manifest,
        replacement_module="bugbay_dependency_fallback",
        max_retries=3,
    )

    assert result is True
    assert manifest.exists()

    content = manifest.read_text()
    assert '"passed": true' in content
    assert '"rollback":' in content
    assert '"before":' in content
    assert '"passed": false' in content
    assert "database_connection" in content

    attempt_file.unlink(missing_ok=True)
