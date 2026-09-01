#!/usr/bin/env python3
"""Validate frozen EXP-0014 evidence against its historical Git preimage."""

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

from tools.experiments import run_exp_0014 as RUNNER  # noqa: E402


RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0014" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "e82d01e6d669e85646dafd6ab3d569fc38e0d71b"
EXPECTED_RESULT_SHA256 = "0eab4893eb85d05c07622bfe70721a58f03e8285e199738b1513237dc3207411"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0014/execution-profile.json",
        "tests/experiments/test_exp_0014.py",
        "tools/experiments/run_exp_0014.py",
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
        raise HistoricalValidationError("Git history cannot provide EXP-0014 evidence")
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
            "EXP-0014 preimage commit is unavailable or not an ancestor; "
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
                f"EXP-0014 frozen experiment file differs: {locator}"
            )
    return expected


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    historical_preimage()
    if not path.is_file() or RUNNER.sha256_file(path) != EXPECTED_RESULT_SHA256:
        raise HistoricalValidationError("EXP-0014 frozen result bytes differ")
    result = RUNNER.validate_result(path)
    if result != {
        "artifact": "EXP-0014",
        "cleanup_complete": True,
        "finding_code_counts": {
            "format.epub": 3,
            "security.remote_resource": 3,
        },
        "input_count": 3,
        "intake_runs": 3,
        "next_action_counts": {
            "abstain": 0,
            "continue_deep_read_only": 0,
            "defer": 0,
            "review": 3,
            "stop": 0,
        },
        "observation_code_counts": {
            "container.compressed_size": 3,
            "container.entry_count": 3,
            "container.expanded_size": 3,
            "container.mimetype.epub": 3,
            "epub.remote_reference.present": 3,
            "filename.extension.epub": 3,
            "format.signature.zip": 3,
            "input.sha256": 3,
            "input.size": 3,
            "markup.shallow_scan": 3,
            "snapshot.stable": 3,
        },
        "path_free": True,
        "schema": "sammlungslotse/exp-0014-private-preflight-cause-result/v1",
        "source_unchanged": True,
        "status": "pass",
        "unclassified_finding_count": 0,
        "unclassified_observation_count": 0,
    }:
        raise HistoricalValidationError("EXP-0014 frozen aggregate differs")
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
        "EXP-0014 historical result valid: "
        f"inputs={result['input_count']} status={result['status']} "
        f"review={result['next_action_counts']['review']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
