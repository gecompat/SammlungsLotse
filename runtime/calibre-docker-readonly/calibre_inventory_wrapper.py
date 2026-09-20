#!/usr/bin/env python3
"""Container-side fixed Calibre list invocation with bounded output."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


MAX_STDOUT = 4 * 1024 * 1024
MAX_STDERR = 128 * 1024
OUTPUT = Path("/output")


def main() -> int:
    environment = {
        "CALIBRE_CONFIG_DIRECTORY": "/config",
        "HOME": "/tmp/home",
        "LANG": "C.UTF-8",
        "PATH": "/opt/calibre:/usr/local/bin:/usr/bin:/bin",
        "QT_QPA_PLATFORM": "offscreen",
    }
    command = [
        "/opt/calibre/calibredb",
        "list",
        "--with-library",
        "/library",
        "--for-machine",
        "--fields",
        "title,authors,languages,formats",
        "--sort-by",
        "id",
        "--ascending",
    ]
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        timeout=25,
        check=False,
    )
    stdout_truncated = len(completed.stdout) > MAX_STDOUT
    stderr_truncated = len(completed.stderr) > MAX_STDERR
    stdout = completed.stdout[:MAX_STDOUT]
    stderr = completed.stderr[:MAX_STDERR]
    (OUTPUT / "stderr.bin").write_bytes(stderr)
    if completed.returncode == 0 and not stdout_truncated and not stderr_truncated:
        json.loads(stdout.decode("utf-8"))
        (OUTPUT / "report.json").write_bytes(stdout)
    (OUTPUT / "complete.json").write_text(
        json.dumps(
            {
                "exit_code": completed.returncode,
                "stderr_truncated": stderr_truncated,
                "stdout_truncated": stdout_truncated,
            },
            separators=(",", ":"),
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return completed.returncode if not stdout_truncated and not stderr_truncated else 70


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        raise SystemExit(70)
