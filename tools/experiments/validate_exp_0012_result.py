#!/usr/bin/env python3
"""Validate frozen EXP-0012 evidence against its historical Git preimage."""

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
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0012.py"
RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0012" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "deddef016ed61dbbddc4a938c7f2ec0cabb8228e"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0012/case-manifest.json",
        "experiments/ebook/exp-0012/execution-profile.json",
        "tests/experiments/test_exp_0012.py",
        "tools/experiments/run_exp_0012.py",
    }
)


class HistoricalValidationError(RuntimeError):
    """Raised when frozen evidence cannot be verified from Git history."""


def load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_exp_0012_historical",
        RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise HistoricalValidationError("EXP-0012 runner cannot be loaded")
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
        raise HistoricalValidationError("Git history cannot provide EXP-0012 evidence")
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
            "EXP-0012 preimage commit is unavailable or not an ancestor; full Git history is required"
        )


def historical_preimage(result: dict[str, Any]) -> dict[str, str]:
    expected = result.get("preimage")
    commit = result.get("preimage_commit")
    if not isinstance(expected, dict) or set(expected) != set(RUNNER.PREIMAGE_FILES):
        raise HistoricalValidationError("EXP-0012 preimage locator set differs")
    if commit != EXPECTED_PREIMAGE_COMMIT or not re.fullmatch(r"[0-9a-f]{40}", str(commit)):
        raise HistoricalValidationError("EXP-0012 preimage commit differs")
    ensure_ancestor(commit)
    actual = {
        locator: hashlib.sha256(git_bytes("show", f"{commit}:{locator}")).hexdigest()
        for locator in RUNNER.PREIMAGE_FILES
    }
    if actual != expected:
        raise HistoricalValidationError("EXP-0012 historical preimage hashes differ")
    for locator in FROZEN_EXPERIMENT_LOCATORS:
        path = ROOT / locator
        if not path.is_file() or RUNNER.sha256_file(path) != expected[locator]:
            raise HistoricalValidationError(f"EXP-0012 frozen experiment file differs: {locator}")
    return actual


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
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
        f"EXP-0012 historical result valid: {sum(result['acceptance'].values())}/"
        f"{len(result['acceptance'])} variants={len(result['metrics']['variants'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
