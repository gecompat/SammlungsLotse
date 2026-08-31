#!/usr/bin/env python3
"""Validate frozen EXP-0009 evidence against its historical Git preimage."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0009.py"
RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0009" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "2ef2de0395e485283f3be4ca339ab5fed8657fee"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0009/case-manifest.json",
        "experiments/ebook/exp-0009/execution-profile.json",
        "tests/experiments/test_exp_0009.py",
        "tools/experiments/run_exp_0009.py",
    }
)


class HistoricalValidationError(RuntimeError):
    """Raised when frozen evidence cannot be verified from Git history."""


def load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_exp_0009_historical",
        RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise HistoricalValidationError("EXP-0009 runner cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner()


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
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise HistoricalValidationError(
            f"Git history cannot provide EXP-0009 evidence: {detail or arguments[0]}"
        )
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
            "EXP-0009 preimage commit is unavailable or not an ancestor; full Git history is required"
        )


def historical_preimage(result: dict[str, Any]) -> dict[str, str]:
    preimage = result.get("preimage")
    if not isinstance(preimage, dict):
        raise HistoricalValidationError("EXP-0009 preimage record is missing")
    authority = preimage.get("authority")
    expected = preimage.get("sha256_by_locator")
    if not isinstance(authority, dict) or not isinstance(expected, dict):
        raise HistoricalValidationError("EXP-0009 preimage binding is incomplete")
    commit = authority.get("preimage_commit")
    if commit != EXPECTED_PREIMAGE_COMMIT or not re.fullmatch(r"[0-9a-f]{40}", str(commit)):
        raise HistoricalValidationError("EXP-0009 preimage commit differs")
    if set(expected) != set(RUNNER.PREIMAGE_FILES):
        raise HistoricalValidationError("EXP-0009 preimage locator set differs")

    ensure_ancestor(commit)
    actual = {
        locator: hashlib.sha256(git_bytes("show", f"{commit}:{locator}")).hexdigest()
        for locator in RUNNER.PREIMAGE_FILES
    }
    if actual != expected:
        raise HistoricalValidationError("EXP-0009 historical preimage hashes differ")

    for locator in FROZEN_EXPERIMENT_LOCATORS:
        path = ROOT / locator
        if not path.is_file() or RUNNER.sha256_file(path) != expected[locator]:
            raise HistoricalValidationError(
                f"EXP-0009 frozen experiment file differs: {locator}"
            )
    return actual


def validate(path: Path) -> dict[str, Any]:
    result = RUNNER.load_json(path)
    frozen_preimage = historical_preimage(result)
    current_preimage = RUNNER.current_preimage
    RUNNER.current_preimage = lambda: frozen_preimage
    try:
        return RUNNER.validate_result(path)
    finally:
        RUNNER.current_preimage = current_preimage


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
        f"EXP-0009 historical result valid: {sum(result['acceptance'].values())}/"
        f"{len(RUNNER.ACCEPTANCE_NAMES)} quality={result['quality_verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
