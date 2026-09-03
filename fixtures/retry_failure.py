from pathlib import Path

attempt_file = Path("manifests/retry-attempt.txt")

try:
    attempts = int(attempt_file.read_text(encoding="utf-8").strip())
except (FileNotFoundError, ValueError):
    attempts = 0

attempts += 1
attempt_file.write_text(str(attempts), encoding="utf-8")

if attempts == 1:
    print(database_connection)
elif attempts == 2:
    raise RuntimeError("Intentional post-repair verification failure")
else:
    print("Retry recovery succeeded")
