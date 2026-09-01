#!/usr/bin/env python3
"""Validate frozen EXP-0017 evidence against its historical Git preimage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.experiments import run_exp_0017 as RUNNER  # noqa: E402


RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0017" / "result.json"
EXPECTED_PREIMAGE_COMMIT = "53a1e2dbefd03c7d770e949490ea1ec7783bfe98"
EXPECTED_RESULT_SHA256 = "ffb748bc7429b4362392c1464b6268bf404df74625420a8498d405558c88db61"
PROFILE_LOCATOR = "experiments/ebook/exp-0017/execution-profile.json"
FROZEN_EXPERIMENT_LOCATORS = frozenset(
    {
        "experiments/ebook/exp-0017/cases.json",
        PROFILE_LOCATOR,
        "tools/experiments/run_exp_0017.py",
    }
)
EXPECTED_PROVIDER_CODES = {
    "NAV-010": 1,
    "OPF-014": 5,
    "OPF-094": 1,
    "RSC-005": 23,
    "RSC-006": 5,
    "RSC-017": 1,
}


class HistoricalValidationError(RuntimeError):
    """Raised when frozen EXP-0017 evidence cannot be verified."""


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
        raise HistoricalValidationError("Git history cannot provide EXP-0017 evidence")
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
            "EXP-0017 preimage is unavailable or not an ancestor; full history is required"
        )


def _historical_hash(locator: str) -> str:
    content = RUNNER.canonical_source_bytes(
        git_bytes("show", f"{EXPECTED_PREIMAGE_COMMIT}:{locator}")
    )
    return hashlib.sha256(content).hexdigest()


def historical_preimage() -> tuple[dict[str, str], dict[str, Any]]:
    ensure_ancestor(EXPECTED_PREIMAGE_COMMIT)
    try:
        profile = json.loads(
            git_bytes("show", f"{EXPECTED_PREIMAGE_COMMIT}:{PROFILE_LOCATOR}")
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise HistoricalValidationError("historical EXP-0017 profile is invalid") from exc
    bindings = profile.get("runtime_bindings", {}).get("files")
    if not isinstance(bindings, list) or not bindings:
        raise HistoricalValidationError("historical EXP-0017 bindings are missing")
    locators = tuple(binding.get("locator") for binding in bindings)
    if any(not isinstance(locator, str) for locator in locators):
        raise HistoricalValidationError("historical EXP-0017 locator differs")
    expected = {locator: _historical_hash(locator) for locator in locators}
    expected[PROFILE_LOCATOR] = _historical_hash(PROFILE_LOCATOR)
    if bindings != [
        {"locator": locator, "sha256": expected[locator]} for locator in locators
    ]:
        raise HistoricalValidationError("historical EXP-0017 file binding differs")
    aggregate = RUNNER.sha256_bytes(RUNNER.canonical_bytes(bindings))
    if profile["runtime_bindings"].get("aggregate_sha256") != aggregate:
        raise HistoricalValidationError("historical EXP-0017 aggregate binding differs")
    for locator in FROZEN_EXPERIMENT_LOCATORS:
        path = ROOT / locator
        if not path.is_file() or RUNNER.sha256_file(path) != expected[locator]:
            raise HistoricalValidationError(
                f"EXP-0017 frozen experiment file differs: {locator}"
            )
    return expected, profile


def _expected_result_bindings(
    preimage: dict[str, str], profile: dict[str, Any]
) -> dict[str, str]:
    product_bindings = [
        binding
        for binding in profile["runtime_bindings"]["files"]
        if binding["locator"].startswith("src/sammlungslotse/ebook_intake/")
    ]
    return {
        "case_manifest_sha256": preimage[
            "experiments/ebook/exp-0017/cases.json"
        ],
        "deep_profile_sha256": preimage[
            "runtime/ebook-deep-readonly/profile.json"
        ],
        "execution_profile_sha256": preimage[PROFILE_LOCATOR],
        "exp0016_manifest_sha256": preimage[
            "experiments/ebook/exp-0016/cases.json"
        ],
        "exp0016_runner_sha256": preimage["tools/experiments/run_exp_0016.py"],
        "product_tree_sha256": RUNNER.sha256_bytes(
            RUNNER.canonical_bytes(product_bindings)
        ),
        "runner_sha256": preimage["tools/experiments/run_exp_0017.py"],
        "runtime_bindings_sha256": profile["runtime_bindings"][
            "aggregate_sha256"
        ],
    }


def _validate_provider_repetitions(result: dict[str, Any]) -> None:
    expected = []
    for index, total in ((1, 57451), (2, 57453)):
        expected.append(
            {
                "assessments": {"epubcheck_conformance_findings": 12},
                "cleanup_complete": 12,
                "execution_states": {"completed": 12},
                "isolation_verified": 12,
                "process_started": 12,
                "provider_codes": EXPECTED_PROVIDER_CODES,
                "raw_report_max_bytes": 5702,
                "raw_report_total_bytes": total,
                "repetition": index,
            }
        )
    if result.get("provider_repetitions") != expected:
        raise HistoricalValidationError("EXP-0017 provider aggregates differ")


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    preimage, profile = historical_preimage()
    if not path.is_file() or RUNNER.sha256_file(path) != EXPECTED_RESULT_SHA256:
        raise HistoricalValidationError("EXP-0017 frozen result bytes differ")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HistoricalValidationError("EXP-0017 frozen result is invalid") from exc
    if set(result) != RUNNER.RESULT_FIELDS:
        raise HistoricalValidationError("EXP-0017 result fields differ")
    if (
        result.get("schema") != RUNNER.RESULT_SCHEMA
        or result.get("artifact") != "EXP-0017"
        or result.get("preimage_commit") != EXPECTED_PREIMAGE_COMMIT
        or result.get("status") != "pass"
        or result.get("path_free") is not True
    ):
        raise HistoricalValidationError("EXP-0017 result identity differs")
    if result.get("bindings") != _expected_result_bindings(preimage, profile):
        raise HistoricalValidationError("EXP-0017 result bindings differ")
    acceptance = result.get("acceptance", {})
    if set(acceptance) != set(RUNNER.ACCEPTANCE_KEYS) or not all(
        value is True for value in acceptance.values()
    ):
        raise HistoricalValidationError("EXP-0017 acceptance differs")
    if (
        result.get("case_count") != 12
        or result.get("repetitions") != 2
        or result.get("provider_runs") != 24
        or result.get("runs_semantically_identical") is not True
        or result.get("group_counts")
        != {
            "ambiguous_or_deceptive": 4,
            "resource_or_active": 4,
            "s3_navigation": 4,
        }
        or result.get("parser_oracle_mismatches")
        != {"context": 0, "s3_action": 0, "scheme_group": 0}
    ):
        raise HistoricalValidationError("EXP-0017 matrix evidence differs")
    _validate_provider_repetitions(result)
    if result.get("canary") != {
        "control_connections": 1,
        "deep_path_connections": 0,
    }:
        raise HistoricalValidationError("EXP-0017 canary evidence differs")
    if result.get("boundary_probes") != {
        "output": {
            "attempted_bytes": 4 * 1024 * 1024,
            "bounded_bytes": 2 * 1024 * 1024,
            "container_removed": True,
            "write_rejected": True,
        },
        "timeout": {
            "assessment": "not_assessed",
            "container_removed": True,
            "process_started": True,
            "state": "timeout",
            "task_root_empty": True,
        },
    }:
        raise HistoricalValidationError("EXP-0017 boundary probes differ")
    if not all(result.get("cleanup", {}).values()) or len(result["cleanup"]) != 10:
        raise HistoricalValidationError("EXP-0017 cleanup evidence differs")
    if result.get("effects") != {
        "collection_modified": False,
        "deep_tool_execution": True,
        "domain_system_writes": False,
        "external_network_access": False,
        "local_loopback_measurement": True,
        "persistence": False,
        "private_inputs": False,
        "product_code_modified": False,
        "wi0004_gate_modified": False,
    }:
        raise HistoricalValidationError("EXP-0017 effect boundary differs")
    if result.get("materialization") != {
        "aggregate_sha256": "4c23c3f96bc7e054abd89f775a5eded677f14373a92ebe7d297ead519832bc2d",
        "archive_entries_max": 5,
        "deterministic": True,
        "expanded_bytes_max": 1134,
        "max_bytes": 1295,
        "total_unique_bytes": 13649,
    }:
        raise HistoricalValidationError("EXP-0017 materialization differs")
    isolation = result.get("isolation", {})
    if (
        isolation.get("network") != "none"
        or isolation.get("verified_by_executor") is not True
        or isolation.get("container_removed") is not True
        or isolation.get("task_root_empty") is not True
        or isolation.get("privileged") is not False
        or isolation.get("read_only_root") is not True
        or isolation.get("input_read_only") is not True
        or isolation.get("tmpfs_exact") is not True
        or isolation.get("ulimits_exact") is not True
    ):
        raise HistoricalValidationError("EXP-0017 isolation evidence differs")
    if result.get("runtime") != {
        "client_version": "6.1.0",
        "deep_profile_id": (
            "wi-0005-epubcheck-5.3.0-temurin-21.0.12.1+1-"
            "podman-linux-amd64/v1"
        ),
        "image_id_exact": True,
        "provider_id": "epubcheck",
        "provider_version": "5.3.0",
        "server_os_arch": "linux/amd64",
        "server_version": "6.1.0",
    }:
        raise HistoricalValidationError("EXP-0017 runtime evidence differs")
    if not RUNNER._public_result_safe(result) or not re.fullmatch(
        r"[0-9a-f]{64}", EXPECTED_RESULT_SHA256
    ):
        raise HistoricalValidationError("EXP-0017 privacy boundary differs")
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
    print(
        "EXP-0017 historical result valid: "
        f"cases={result['case_count']} provider_runs={result['provider_runs']} "
        f"status={result['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
