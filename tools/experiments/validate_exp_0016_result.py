#!/usr/bin/env python3
"""Validate frozen EXP-0016 evidence against its historical Git preimage."""

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

from tools.experiments import run_exp_0016 as RUNNER  # noqa: E402


RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0016" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "969fa6331afdfc4ceb808ffeed71f7a30193205b"
EXPECTED_RESULT_SHA256 = "6c748dd1477dba56a37e19b7a5bf798d32e702e8d6d2a230ebfa3c98d775db08"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0016/cases.json",
        "experiments/ebook/exp-0016/execution-profile.json",
        "tools/experiments/run_exp_0016.py",
    }
)
EXPECTED_METRICS = {
    "classify_and_keep_review": {
        "abstention": 10,
        "conservative_review": 8,
        "context_false_negative": 0,
        "context_mismatch": 0,
        "critical_false_continue": 0,
    },
    "review_all_http_s": {
        "abstention": 10,
        "conservative_review": 8,
        "context_false_negative": 0,
        "context_mismatch": 0,
        "critical_false_continue": 0,
    },
    "strict_navigation_candidate": {
        "abstention": 10,
        "conservative_review": 0,
        "context_false_negative": 0,
        "context_mismatch": 0,
        "critical_false_continue": 0,
    },
}


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
        raise HistoricalValidationError("Git history cannot provide EXP-0016 evidence")
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
            "EXP-0016 preimage commit is unavailable or not an ancestor; "
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
                f"EXP-0016 frozen experiment file differs: {locator}"
            )
    return expected


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    preimage = historical_preimage()
    if not path.is_file() or RUNNER.sha256_file(path) != EXPECTED_RESULT_SHA256:
        raise HistoricalValidationError("EXP-0016 frozen result bytes differ")
    result = RUNNER.validate_result(path)
    if result["preimage_commit"] != EXPECTED_PREIMAGE_COMMIT:
        raise HistoricalValidationError("EXP-0016 result preimage differs")
    if result["bindings"] != {
        "case_manifest_sha256": preimage[
            "experiments/ebook/exp-0016/cases.json"
        ],
        "execution_profile_sha256": preimage[
            "experiments/ebook/exp-0016/execution-profile.json"
        ],
        "runner_sha256": preimage["tools/experiments/run_exp_0016.py"],
    }:
        raise HistoricalValidationError("EXP-0016 result bindings differ")
    if result["status"] != "pass" or not all(result["acceptance"].values()):
        raise HistoricalValidationError("EXP-0016 method result differs")
    if result["case_count"] != 48 or result["parser_runs"] != 96:
        raise HistoricalValidationError("EXP-0016 execution counts differ")
    if result["repetitions"] != 2 or not result["runs_semantically_identical"]:
        raise HistoricalValidationError("EXP-0016 repetition evidence differs")
    for strategy, metrics in EXPECTED_METRICS.items():
        if result["strategies"][strategy] != {
            "classification": "eligible_with_tradeoffs",
            "metrics": metrics,
        }:
            raise HistoricalValidationError(
                f"EXP-0016 strategy result differs: {strategy}"
            )
    if any(result["effects"].values()):
        raise HistoricalValidationError("EXP-0016 forbidden effect is present")
    if not result["cleanup_complete"] or not result["path_free"]:
        raise HistoricalValidationError("EXP-0016 boundary proof differs")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    args = parser.parse_args(argv)
    try:
        result = validate(args.result)
    except (OSError, HistoricalValidationError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    strict = result["strategies"]["strict_navigation_candidate"]["metrics"]
    print(
        "EXP-0016 historical result valid: "
        f"cases={result['case_count']} status={result['status']} "
        f"critical_false_continue={strict['critical_false_continue']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
