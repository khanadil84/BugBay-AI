from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_manifest(
    path: Path,
    *,
    target: str,
    diagnosis: dict[str, Any],
    repair: dict[str, Any],
    verification: dict[str, Any],
) -> None:
    manifest = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "diagnosis": diagnosis,
        "repair": repair,
        "verification": verification,
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
