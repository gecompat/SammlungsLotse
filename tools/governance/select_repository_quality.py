"""Conservative runtime-check selection for the required Repository Quality job."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


STATUS_ONLY_PATHS = frozenset(
    {"docs/project/PROJECT_STATUS.md", "docs/project/HANDOVER.md"}
)
SHA = re.compile(r"[0-9a-f]{40}\Z")


def runtime_required(paths: list[str] | None) -> bool:
    """Unknown input and every path outside the exact status allowlist use full checks."""
    return not paths or any(path not in STATUS_ONLY_PATHS for path in paths)


def changed_paths(base: str, head: str, cwd: Path | None = None) -> list[str] | None:
    if not SHA.fullmatch(base) or not SHA.fullmatch(head) or base == "0" * 40:
        return None
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--no-renames", "-z", base, head, "--"],
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    try:
        return [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]
    except UnicodeDecodeError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--github-output", type=Path, required=True)
    args = parser.parse_args()

    paths = changed_paths(args.base, args.head)
    required = runtime_required(paths)
    disposition = "full" if required else "status-only"
    print(f"Repository Quality scope: {disposition}; changed_paths={len(paths) if paths is not None else 'unknown'}")
    with args.github_output.open("a", encoding="utf-8") as output:
        output.write(f"runtime_required={'true' if required else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
