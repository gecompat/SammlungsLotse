#!/usr/bin/env python3
"""Validate frozen EXP-0013 evidence against its historical Git preimage."""

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

from tools.experiments import run_exp_0013 as RUNNER  # noqa: E402


RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0013" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "6d32f5dad32481ef9ec163e742acb1ae77aaf226"
EXPECTED_RESULT_SHA256 = "6ea2a583956602466edc5b8c11f658d86b975f22ca2b96821c22e4a21265b941"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0013/execution-profile.json",
        "tests/experiments/test_exp_0013.py",
        "tools/experiments/run_exp_0013.py",
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
        raise HistoricalValidationError("Git history cannot provide EXP-0013 evidence")
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
            "EXP-0013 preimage commit is unavailable or not an ancestor; full Git history is required"
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
                f"EXP-0013 frozen experiment file differs: {locator}"
            )
    return expected


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    historical_preimage()
    if not path.is_file() or RUNNER.sha256_file(path) != EXPECTED_RESULT_SHA256:
        raise HistoricalValidationError("EXP-0013 frozen result bytes differ")
    result = RUNNER.validate_result(path)
    if result != {
        "artifact": "EXP-0013",
        "assessment_counts": {"completed": 0, "not_assessed": 3},
        "cleanup_complete": True,
        "entry_stage_counts": {
            "completed": 0,
            "identity_analysis": 0,
            "ingress_preflight": 3,
            "record_handoff": 0,
            "unclassified": 0,
        },
        "input_count": 3,
        "path_free": True,
        "reason_code_counts": {"ingress.preflight_gate_not_open": 3},
        "schema": "sammlungslotse/exp-0013-private-diagnostic-result/v1",
        "search_runs": 4,
        "source_unchanged": True,
        "status": "not_qualified",
        "wi0011_runs": 3,
    }:
        raise HistoricalValidationError("EXP-0013 frozen aggregate differs")
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
        "EXP-0013 historical result valid: "
        f"inputs={result['input_count']} status={result['status']} "
        f"ingress_preflight={result['entry_stage_counts']['ingress_preflight']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
