#!/usr/bin/env python3
"""Validate frozen EXP-0007 evidence against its recorded Git preimage."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULT_PATH = ROOT / "experiments/ebook/exp-0007/result.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.experiments import run_exp_0007 as RUNNER


HISTORICAL_FILES = {
    "profile_sha256": "experiments/ebook/exp-0007/execution-profile.json",
    "probe_sha256": "experiments/ebook/exp-0007/probe.py",
    "driver_sha256": "experiments/ebook/exp-0007/driver.py",
    "containerfile_sha256": "experiments/ebook/exp-0007/Containerfile",
    "runner_sha256": "tools/experiments/run_exp_0007.py",
    "fixture_manifest_sha256": "tests/fixtures/ebook/test-0001/v0.2/manifest.json",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def historical_bytes(commit: str, locator: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{locator}"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"EXP-0007 historical locator is unavailable: {locator}")
    return result.stdout


def require_ancestor(commit: str) -> None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "EXP-0007 preimage is unavailable or not an ancestor; full Git history is required"
        )


def historical_hashes(commit: str) -> dict[str, str]:
    return {
        key: sha256_bytes(historical_bytes(commit, locator))
        for key, locator in HISTORICAL_FILES.items()
    }


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    commit = result.get("authority", {}).get("preimage_commit")
    if (
        result.get("experiment") != "EXP-0007"
        or result.get("status") != "pass"
        or not isinstance(commit, str)
        or len(commit) != 40
    ):
        raise RuntimeError("EXP-0007 historical result identity differs")
    require_ancestor(commit)
    frozen_hashes = historical_hashes(commit)
    for key, expected in frozen_hashes.items():
        if result.get(key) != expected:
            raise RuntimeError(f"EXP-0007 historical {key} differs")

    # The driver changed under EXP-0023. All other bound inputs must remain
    # current so the frozen runner can safely recompute the historical result.
    current_hashes = RUNNER.result_hashes()
    for key, expected in frozen_hashes.items():
        if key != "driver_sha256" and current_hashes.get(key) != expected:
            raise RuntimeError(f"EXP-0007 current {key} differs from its preimage")

    original_hashes = RUNNER.result_hashes
    RUNNER.result_hashes = lambda: frozen_hashes
    try:
        validated = RUNNER.validate_result(path)
    finally:
        RUNNER.result_hashes = original_hashes
    if len(validated.get("acceptance", {})) != 16 or not all(
        validated["acceptance"].values()
    ):
        raise RuntimeError("EXP-0007 historical acceptance differs")
    return validated


if __name__ == "__main__":
    validate()
    print("[OK] EXP-0007 historical result")
