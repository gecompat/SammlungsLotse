#!/usr/bin/env python3
"""Validate frozen EXP-0015 evidence against its historical Git preimage."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.experiments import run_exp_0015 as RUNNER  # noqa: E402


RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0015" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "cefe2d29b54b8e6cbc60b07b1485da473565cda7"
EXPECTED_RESULT_SHA256 = "651ad195b54531d20e0fc6ff882df6e1d4b38765e877057faf7858f36dae50a1"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0015/execution-profile.json",
        "tools/experiments/run_exp_0015.py",
    }
)


class HistoricalValidationError(RuntimeError):
    """Raised when frozen evidence cannot be verified from Git history."""


def git_bytes(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise HistoricalValidationError("Git history cannot provide EXP-0015 evidence")
    return completed.stdout


def ensure_ancestor(commit: str) -> None:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise HistoricalValidationError(
            "EXP-0015 preimage commit is unavailable or not an ancestor; "
            "full Git history is required"
        )


def historical_preimage() -> dict[str, str]:
    ensure_ancestor(EXPECTED_PREIMAGE_COMMIT)
    expected = {
        locator: hashlib.sha256(
            git_bytes("show", f"{EXPECTED_PREIMAGE_COMMIT}:{locator}")
        ).hexdigest()
        for locator in RUNNER.PREIMAGE_FILES
    }
    for locator in FROZEN_EXPERIMENT_LOCATORS:
        path = ROOT / locator
        if not path.is_file() or RUNNER.sha256_file(path) != expected[locator]:
            raise HistoricalValidationError(
                f"EXP-0015 frozen experiment file differs: {locator}"
            )
    return expected


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    historical_preimage()
    if not path.is_file() or RUNNER.sha256_file(path) != EXPECTED_RESULT_SHA256:
        raise HistoricalValidationError("EXP-0015 frozen result bytes differ")
    result = RUNNER.validate_result(path)
    if result != {
        "artifact": "EXP-0015",
        "cleanup_complete": True,
        "context_input_counts": {"content.navigation": 3},
        "input_count": 3,
        "minimum_group_size": 2,
        "parser_runs": 3,
        "path_free": True,
        "qualification": "shared_context_present",
        "remote_reference_input_count": 3,
        "schema": "sammlungslotse/exp-0015-private-reference-context-result/v1",
        "source_unchanged": True,
        "status": "pass",
        "suppressed_context_present": False,
        "unclassified_input_count": 0,
    }:
        raise HistoricalValidationError("EXP-0015 frozen aggregate differs")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    args = parser.parse_args(argv)
    try:
        result = validate(args.result)
    except (OSError, HistoricalValidationError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        "EXP-0015 historical result valid: "
        f"inputs={result['input_count']} status={result['status']} "
        f"shared_navigation={result['context_input_counts']['content.navigation']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
