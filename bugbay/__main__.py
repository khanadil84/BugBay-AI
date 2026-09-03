from __future__ import annotations

import argparse
from pathlib import Path

from bugbay.orchestrator import run_recovery


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BugBay autonomous runtime recovery engine."
    )
    parser.add_argument(
        "target",
        help="Python runtime target to execute and recover.",
    )
    parser.add_argument(
        "--manifest",
        default="manifests/diagnostic-manifest.json",
        help="Path for the diagnostic manifest.",
    )
    parser.add_argument(
        "--replacement-module",
        default="bugbay_dependency_fallback",
        help="Controlled dependency replacement module.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=1,
        help="Maximum bounded recovery attempts.",
    )

    args = parser.parse_args()

    target = Path(args.target)
    manifest = Path(args.manifest)

    print("BugBay runtime recovery starting...")
    print("TARGET:", target)

    success = run_recovery(
        target=target,
        manifest_path=manifest,
        replacement_module=args.replacement_module,
        max_retries=args.max_retries,
    )

    print("BUGBAY RESULT:", "SUCCESS" if success else "FAILURE")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
