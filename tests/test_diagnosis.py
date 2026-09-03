from bugbay.diagnosis import diagnose


def test_unknown_failure_is_not_repairable() -> None:
    stderr = """Traceback (most recent call last):
  File "/home/asus/BugBay-AI/fixtures/permanent_failure.py", line 1, in <module>
    raise RuntimeError("Permanent controlled failure")
RuntimeError: Permanent controlled failure
"""

    result = diagnose(stderr)

    assert result.error_type == "UNKNOWN"
    assert result.repairable is False
    assert result.missing_module is None
    assert result.missing_variable is None


def test_type_error_is_not_repairable() -> None:
    stderr = """Traceback (most recent call last):
  File "/home/asus/BugBay-AI/fixtures/type_error_failure.py", line 3, in <module>
    value = 1 + "broken"
TypeError: unsupported operand type(s) for +: 'int' and 'str'
"""

    result = diagnose(stderr)

    assert result.error_type == "TypeError"
    assert result.repairable is False


def test_multiframe_traceback_uses_crash_frame() -> None:
    stderr = """Traceback (most recent call last):
  File "/home/asus/BugBay-AI/fixtures/app.py", line 10, in start_application
    connect()
  File "/home/asus/BugBay-AI/fixtures/database.py", line 25, in connect
    print(database_connection)
NameError: name 'database_connection' is not defined
"""

    result = diagnose(stderr)

    assert result.error_type == "NameError"
    assert result.missing_variable == "database_connection"
    assert result.source_file == "/home/asus/BugBay-AI/fixtures/database.py"
    assert result.line_number == 25
    assert result.repairable is True
