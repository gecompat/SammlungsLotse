#!/usr/bin/env python3
"""Run or validate the bounded, product-code-free EXP-0014 experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0014"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
RESULT_PATH = EXPERIMENT / "result.json"
INTAKE_CLI_PATH = ROOT / "tools" / "run_ebook_intake.py"
TEST_0001_MANIFEST_PATH = (
    ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "manifest.json"
)
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse\exp-0014")

CONTROL_CASES = (
    (
        "tests/fixtures/ebook/test-0001/v0.3/cases/ingress-stable-minimal/stable.epub",
        "continue_deep_read_only",
    ),
    (
        "tests/fixtures/ebook/test-0001/v0.3/cases/epub-active-or-remote/active-remote.epub",
        "review",
    ),
    (
        "tests/fixtures/ebook/test-0001/v0.3/cases/container-corrupt/corrupt.epub",
        "stop",
    ),
    (
        "tests/fixtures/ebook/test-0001/v0.3/cases/format-unknown/unknown.epub",
        "abstain",
    ),
)
RUNTIME_LOCATORS = (
    "tools/run_ebook_intake.py",
    "src/sammlungslotse/ebook_intake/__init__.py",
    "src/sammlungslotse/ebook_intake/application.py",
    "src/sammlungslotse/ebook_intake/batch.py",
    "src/sammlungslotse/ebook_intake/cli.py",
    "src/sammlungslotse/ebook_intake/deep_application.py",
    "src/sammlungslotse/ebook_intake/deep_model.py",
    "src/sammlungslotse/ebook_intake/deep_ports.py",
    "src/sammlungslotse/ebook_intake/deep_profile.py",
    "src/sammlungslotse/ebook_intake/deep_workspace.py",
    "src/sammlungslotse/ebook_intake/epubcheck_provider.py",
    "src/sammlungslotse/ebook_intake/model.py",
    "src/sammlungslotse/ebook_intake/podman_executor.py",
    "src/sammlungslotse/ebook_intake/ports.py",
    "src/sammlungslotse/ebook_intake/preflight.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    *(locator for locator, _action in CONTROL_CASES),
)
PREIMAGE_FILES = (
    "docs/planning/EBOOK_PRIVATE_INGRESS_PREFLIGHT_CAUSE_EXPERIMENT.md",
    "experiments/ebook/exp-0014/README.md",
    "experiments/ebook/exp-0014/execution-profile.json",
    "tests/experiments/test_exp_0014.py",
    "tools/experiments/run_exp_0014.py",
    *RUNTIME_LOCATORS,
)

PRIVATE_PATH_PATTERN = re.compile(
    r"(?:(?<![A-Za-z0-9_])[A-Za-z]:[\\/]|/(?:home|Users|tmp|library|input|private)(?:[\\/]|$))",
    re.IGNORECASE,
)
CODE_PATTERN = re.compile(
    r"[a-z][a-z0-9_]{0,31}(?:\.[a-z][a-z0-9_]{0,31}){1,3}"
)
VALUE_KEY_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")

INTAKE_SCHEMA = "sammlungslotse/ebook-intake-report/v1"
RESULT_SCHEMA = "sammlungslotse/exp-0014-private-preflight-cause-result/v1"
SYNTHETIC_SCHEMA = "sammlungslotse/exp-0014-synthetic-control-summary/v1"
NEXT_ACTIONS = (
    "continue_deep_read_only",
    "defer",
    "stop",
    "review",
    "abstain",
)
FORMAT_CAPABILITIES = ("supported", "unsupported", "unknown")
OBSERVATION_CODES = (
    "container.compressed_size",
    "container.encryption_xml",
    "container.entry_count",
    "container.entry_parent_escape",
    "container.expanded_size",
    "container.mimetype.epub",
    "container.mimetype_missing_or_ambiguous",
    "container.open_error",
    "container.zip_encrypted",
    "epub.remote_reference.present",
    "epub.script.present",
    "filename.extension.epub",
    "format.signature.pdf",
    "format.signature.zip",
    "format.signature_unknown",
    "input.not_regular_file",
    "input.read_error",
    "input.reparse_point",
    "input.sha256",
    "input.size",
    "input.size_limit_exceeded",
    "input.symlink",
    "input.unavailable",
    "markup.shallow_scan",
    "snapshot.changed",
    "snapshot.stable",
)
FINDING_CODES = (
    "container.corrupt",
    "format.epub",
    "format.extension_mismatch",
    "format.pdf_unsupported_for_deep_epub",
    "format.zip_not_epub",
    "ingress.unstable",
    "input.not_regular_file",
    "input.reparse_not_allowed",
    "input.symlink_not_allowed",
    "input.unavailable",
    "protection.present",
    "resource.entry_limit_exceeded",
    "resource.expansion_limit_exceeded",
    "resource.input_limit_exceeded",
    "resource.markup_limit_exceeded",
    "security.active_content",
    "security.duplicate_entry",
    "security.path_traversal",
    "security.remote_resource",
)
REPORT_FIELDS = frozenset(
    {
        "deep_read_only_allowed",
        "effects",
        "findings",
        "format_capability",
        "limits",
        "next_action",
        "observations",
        "schema",
        "snapshot",
    }
)
EFFECTS = {
    "deep_tool_started": False,
    "domain_system_writes": False,
    "filesystem_writes": False,
    "network_access": False,
    "original_modified": False,
}
TRIAGE_LIMITS = {
    "max_archive_entries": 512,
    "max_expanded_bytes": 128 * 1024 * 1024,
    "max_input_bytes": 32 * 1024 * 1024,
    "max_markup_entry_bytes": 2 * 1024 * 1024,
    "max_markup_total_bytes": 16 * 1024 * 1024,
    "max_report_bytes": 128 * 1024,
}
PROJECTION_FIELDS = frozenset(
    {
        "finding_codes",
        "next_action",
        "observation_codes",
        "unclassified_finding_count",
        "unclassified_observation_count",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "finding_code_counts",
        "next_action_counts",
        "observation_code_counts",
        "status",
        "unclassified_finding_count",
        "unclassified_observation_count",
    }
)
RESULT_FIELDS = frozenset(
    {
        "artifact",
        "cleanup_complete",
        "finding_code_counts",
        "input_count",
        "intake_runs",
        "next_action_counts",
        "observation_code_counts",
        "path_free",
        "schema",
        "source_unchanged",
        "status",
        "unclassified_finding_count",
        "unclassified_observation_count",
    }
)
NEGATIVE_CONTROLS = (
    "two_inputs",
    "four_inputs",
    "duplicate_input",
    "directory_input",
    "link_input",
    "oversized_input",
    "partial_execution",
    "invalid_json",
    "unknown_codes",
    "private_output_field",
    "incomplete_cleanup",
)


class ExperimentError(RuntimeError):
    """Raised when an EXP-0014 boundary cannot be proven."""


class SafeArgumentParser(argparse.ArgumentParser):
    """Avoid reflecting private argument values in parser failures."""

    def error(self, message: str) -> None:
        raise ExperimentError("command line differs")


@dataclass(frozen=True, slots=True)
class ValidatedInput:
    path: Path
    sha256: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class BoundedProcess:
    returncode: int
    stderr: bytes
    stderr_truncated: bool
    stdout: bytes
    stdout_truncated: bool
    timed_out: bool


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_output(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise ExperimentError("Git preimage is unavailable")
    return completed.stdout


def current_preimage() -> dict[str, str]:
    return {locator: sha256_file(ROOT / locator) for locator in PREIMAGE_FILES}


def require_committed_preimage() -> str:
    commit = git_output("rev-parse", "HEAD").decode("ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ExperimentError("Git preimage commit differs")
    for locator in PREIMAGE_FILES:
        committed = sha256_bytes(git_output("show", f"HEAD:{locator}"))
        if committed != sha256_file(ROOT / locator):
            raise ExperimentError("EXP-0014 preimage is not fully committed")
    return commit


def _expected_input_contract() -> dict[str, Any]:
    return {
        "confirmation_flag": "--confirm-same-exp-0013-inputs",
        "count": 3,
        "max_file_bytes": 4 * 1024 * 1024,
        "max_total_bytes": 12 * 1024 * 1024,
        "regular_files_only": True,
        "suffix": ".epub",
    }


def _expected_limits() -> dict[str, int]:
    return {
        "intake_timeout_seconds": 20,
        "max_code_bytes": 96,
        "max_evidence_items_per_group": 128,
        "max_value_fields_per_evidence": 8,
        "output_bytes": 16384,
        "private_intake_runs": 3,
        "stderr_bytes": 8192,
        "stdout_bytes": 131072,
        "synthetic_intake_runs": 4,
    }


def _expected_projection_matrix() -> dict[str, Any]:
    reports = [
        {
            "finding_codes": ["format.epub"],
            "next_action": "continue_deep_read_only",
            "observation_codes": ["input.sha256", "input.size", "snapshot.stable"],
            "unclassified_finding_count": 0,
            "unclassified_observation_count": 0,
        },
        {
            "finding_codes": [
                "format.epub",
                "security.active_content",
                "security.remote_resource",
            ],
            "next_action": "review",
            "observation_codes": [
                "epub.remote_reference.present",
                "epub.script.present",
            ],
            "unclassified_finding_count": 0,
            "unclassified_observation_count": 0,
        },
        {
            "finding_codes": ["container.corrupt"],
            "next_action": "stop",
            "observation_codes": ["container.open_error", "format.signature.zip"],
            "unclassified_finding_count": 0,
            "unclassified_observation_count": 0,
        },
        {
            "finding_codes": [],
            "next_action": "abstain",
            "observation_codes": ["format.signature_unknown"],
            "unclassified_finding_count": 0,
            "unclassified_observation_count": 0,
        },
        {
            "finding_codes": ["ingress.unstable"],
            "next_action": "defer",
            "observation_codes": ["snapshot.changed"],
            "unclassified_finding_count": 1,
            "unclassified_observation_count": 1,
        },
    ]
    return {"expected": aggregate_projections(reports), "reports": reports}


def validate_contract() -> dict[str, Any]:
    profile = load_json(PROFILE_PATH)
    if not isinstance(profile, dict) or set(profile) != {
        "artifact",
        "commands",
        "implementation",
        "input_contract",
        "limits",
        "output_contract",
        "profile_id",
        "public_contract",
        "runtime_bindings",
        "schema",
        "synthetic_controls",
    }:
        raise ExperimentError("EXP-0014 profile fields differ")
    if profile.get("schema") != "sammlungslotse/exp-0014-execution-profile/v1":
        raise ExperimentError("EXP-0014 profile schema differs")
    if profile.get("artifact") != "EXP-0014":
        raise ExperimentError("EXP-0014 artifact differs")
    if profile.get("profile_id") != "exp-0014-private-ingress-preflight-causes/v1":
        raise ExperimentError("EXP-0014 profile identity differs")
    if profile.get("commands") != {
        "arguments": ["tools/run_ebook_intake.py", "--json"],
        "intake_runs_per_private_input": 1,
    }:
        raise ExperimentError("EXP-0014 command binding differs")
    if profile.get("input_contract") != _expected_input_contract():
        raise ExperimentError("EXP-0014 input contract differs")
    if profile.get("limits") != _expected_limits():
        raise ExperimentError("EXP-0014 limits differ")
    implementation = profile.get("implementation")
    if not isinstance(implementation, dict) or set(implementation) != {
        "deep_tool_execution",
        "direct_database_access",
        "directory_discovery",
        "network_access",
        "persistence",
        "private_values_retained",
        "product_code_changes",
        "writer_surface",
    } or any(value is not False for value in implementation.values()):
        raise ExperimentError("EXP-0014 implementation boundary differs")
    if profile.get("public_contract") != {
        "effect_fields": sorted(EFFECTS),
        "finding_codes": list(FINDING_CODES),
        "format_capabilities": list(FORMAT_CAPABILITIES),
        "next_actions": list(NEXT_ACTIONS),
        "observation_codes": list(OBSERVATION_CODES),
        "report_fields": sorted(REPORT_FIELDS),
        "report_schema": INTAKE_SCHEMA,
        "triage_limits": TRIAGE_LIMITS,
    }:
        raise ExperimentError("EXP-0014 public WI-0004 contract differs")
    if profile.get("output_contract") != {
        "allowed_fields": sorted(RESULT_FIELDS),
        "schema": RESULT_SCHEMA,
        "statuses": ["pass", "inconclusive"],
    }:
        raise ExperimentError("EXP-0014 output contract differs")

    bindings = profile.get("runtime_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {
        "files",
        "test_0001_version",
    }:
        raise ExperimentError("EXP-0014 runtime bindings differ")
    files = bindings.get("files")
    if not isinstance(files, list) or len(files) != len(RUNTIME_LOCATORS):
        raise ExperimentError("EXP-0014 runtime file bindings differ")
    for binding, locator in zip(files, RUNTIME_LOCATORS, strict=True):
        if binding != {
            "locator": locator,
            "sha256": sha256_file(ROOT / locator),
        }:
            raise ExperimentError("EXP-0014 runtime file binding differs")
    manifest = load_json(TEST_0001_MANIFEST_PATH)
    if (
        bindings.get("test_0001_version") != "0.3.0"
        or manifest.get("corpus_ref") != "TEST-0001"
        or manifest.get("fixture_version") != "0.3.0"
    ):
        raise ExperimentError("EXP-0014 TEST-0001 binding differs")

    controls = profile.get("synthetic_controls")
    if not isinstance(controls, dict) or set(controls) != {
        "actual_cli_cases",
        "aggregation_repetitions",
        "negative_controls",
        "projection_matrix",
    }:
        raise ExperimentError("EXP-0014 synthetic controls differ")
    if controls.get("actual_cli_cases") != [
        {"locator": locator, "next_action": action}
        for locator, action in CONTROL_CASES
    ]:
        raise ExperimentError("EXP-0014 actual CLI controls differ")
    if controls.get("aggregation_repetitions") != 2:
        raise ExperimentError("EXP-0014 aggregation repetitions differ")
    if controls.get("negative_controls") != list(NEGATIVE_CONTROLS):
        raise ExperimentError("EXP-0014 negative controls differ")
    if controls.get("projection_matrix") != _expected_projection_matrix():
        raise ExperimentError("EXP-0014 projection matrix differs")
    return profile


def _read_limited(pipe: BinaryIO, limit: int, result: dict[str, object]) -> None:
    retained = bytearray()
    truncated = False
    while chunk := pipe.read(8192):
        remaining = limit - len(retained)
        if remaining > 0:
            retained.extend(chunk[:remaining])
        if len(chunk) > max(remaining, 0):
            truncated = True
    result["content"] = bytes(retained)
    result["truncated"] = truncated


def run_bounded(
    arguments: list[str],
    *,
    timeout: float,
    stdout_limit: int,
    stderr_limit: int,
) -> BoundedProcess:
    process = subprocess.Popen(
        arguments,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None or process.stderr is None:
        process.kill()
        raise ExperimentError("bounded intake pipes are unavailable")
    stdout: dict[str, object] = {}
    stderr: dict[str, object] = {}
    threads = [
        threading.Thread(
            target=_read_limited,
            args=(process.stdout, stdout_limit, stdout),
            daemon=True,
        ),
        threading.Thread(
            target=_read_limited,
            args=(process.stderr, stderr_limit, stderr),
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=5)
    except BaseException:
        process.kill()
        process.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
        process.stdout.close()
        process.stderr.close()
        raise
    for thread in threads:
        thread.join(timeout=5)
        if thread.is_alive():
            raise ExperimentError("bounded intake output reader did not finish")
    process.stdout.close()
    process.stderr.close()
    return BoundedProcess(
        returncode=process.returncode,
        stderr=stderr.get("content", b""),
        stderr_truncated=bool(stderr.get("truncated", False)),
        stdout=stdout.get("content", b""),
        stdout_truncated=bool(stdout.get("truncated", False)),
        timed_out=timed_out,
    )


def parse_intake_stdout(payload: bytes) -> dict[str, Any]:
    if not payload or len(payload) > _expected_limits()["stdout_bytes"]:
        raise ExperimentError("WI-0004 JSON output size differs")
    try:
        decoded = payload.decode("utf-8")
        value = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExperimentError("WI-0004 JSON output is invalid") from exc
    if not isinstance(value, dict):
        raise ExperimentError("WI-0004 JSON report differs")
    return value


def _safe_code(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value.encode("utf-8")) > _expected_limits()["max_code_bytes"]
        or CODE_PATTERN.fullmatch(value) is None
        or PRIVATE_PATH_PATTERN.search(value)
    ):
        raise ExperimentError("WI-0004 code differs")
    return value


def _validate_evidence_group(value: Any, *, group: str) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) > _expected_limits()["max_evidence_items_per_group"]
    ):
        raise ExperimentError(f"WI-0004 {group} group differs")
    codes: list[str] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"code", "values"}:
            raise ExperimentError(f"WI-0004 {group} item differs")
        code = _safe_code(item.get("code"))
        values = item.get("values")
        if (
            not isinstance(values, dict)
            or len(values) > _expected_limits()["max_value_fields_per_evidence"]
        ):
            raise ExperimentError(f"WI-0004 {group} values differ")
        for key, scalar in values.items():
            if not isinstance(key, str) or VALUE_KEY_PATTERN.fullmatch(key) is None:
                raise ExperimentError(f"WI-0004 {group} value key differs")
            if not isinstance(scalar, (str, int, bool)):
                raise ExperimentError(f"WI-0004 {group} scalar differs")
            if isinstance(scalar, str) and (
                len(scalar.encode("utf-8")) > 512
                or PRIVATE_PATH_PATTERN.search(scalar)
            ):
                raise ExperimentError(f"WI-0004 {group} scalar differs")
        codes.append(code)
    if len(codes) != len(set(codes)):
        raise ExperimentError(f"WI-0004 {group} codes repeat")
    return codes


def validate_intake_report_dict(
    report: dict[str, Any],
    *,
    expected_sha256: str,
    expected_size: int,
) -> dict[str, Any]:
    if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
        raise ExperimentError("WI-0004 report fields differ")
    if report.get("schema") != INTAKE_SCHEMA:
        raise ExperimentError("WI-0004 report schema differs")
    action = report.get("next_action")
    capability = report.get("format_capability")
    if action not in NEXT_ACTIONS or capability not in FORMAT_CAPABILITIES:
        raise ExperimentError("WI-0004 decision differs")
    deep_allowed = report.get("deep_read_only_allowed")
    if not isinstance(deep_allowed, bool) or deep_allowed != (
        action == "continue_deep_read_only"
    ):
        raise ExperimentError("WI-0004 deep gate differs")
    if report.get("effects") != EFFECTS or report.get("limits") != TRIAGE_LIMITS:
        raise ExperimentError("WI-0004 safety or limit contract differs")
    snapshot = report.get("snapshot")
    if not isinstance(snapshot, dict) or set(snapshot) != {"sha256", "size_bytes"}:
        raise ExperimentError("WI-0004 snapshot differs")
    if (
        snapshot.get("sha256") != expected_sha256
        or SHA256_PATTERN.fullmatch(str(snapshot.get("sha256"))) is None
        or snapshot.get("size_bytes") != expected_size
    ):
        raise ExperimentError("WI-0004 snapshot binding differs")
    observation_codes = _validate_evidence_group(
        report.get("observations"), group="observation"
    )
    _validate_evidence_group(report.get("findings"), group="finding")
    observations = {
        item["code"]: item["values"] for item in report["observations"]
    }
    if (
        observations.get("input.sha256") != {"sha256": expected_sha256}
        or observations.get("input.size") != {"size_bytes": expected_size}
        or "snapshot.stable" not in observation_codes
    ):
        raise ExperimentError("WI-0004 snapshot evidence differs")
    encoded = canonical_json(report)
    if (
        len(encoded.encode("utf-8")) > _expected_limits()["stdout_bytes"]
        or PRIVATE_PATH_PATTERN.search(encoded)
    ):
        raise ExperimentError("WI-0004 report privacy boundary differs")
    return report


def project_intake_report(report: dict[str, Any]) -> dict[str, Any]:
    observation_codes = [item["code"] for item in report["observations"]]
    finding_codes = [item["code"] for item in report["findings"]]
    known_observations = sorted(
        code for code in observation_codes if code in OBSERVATION_CODES
    )
    known_findings = sorted(code for code in finding_codes if code in FINDING_CODES)
    result = {
        "finding_codes": known_findings,
        "next_action": report["next_action"],
        "observation_codes": known_observations,
        "unclassified_finding_count": len(finding_codes) - len(known_findings),
        "unclassified_observation_count": (
            len(observation_codes) - len(known_observations)
        ),
    }
    return validate_projection(result)


def validate_projection(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != PROJECTION_FIELDS:
        raise ExperimentError("EXP-0014 projection fields differ")
    if value.get("next_action") not in NEXT_ACTIONS:
        raise ExperimentError("EXP-0014 projected action differs")
    for field, allowlist in (
        ("observation_codes", OBSERVATION_CODES),
        ("finding_codes", FINDING_CODES),
    ):
        codes = value.get(field)
        if (
            not isinstance(codes, list)
            or codes != sorted(codes)
            or len(codes) != len(set(codes))
            or any(code not in allowlist for code in codes)
        ):
            raise ExperimentError(f"EXP-0014 projected {field} differ")
    for field in (
        "unclassified_observation_count",
        "unclassified_finding_count",
    ):
        count = value.get(field)
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ExperimentError("EXP-0014 unclassified count differs")
    encoded = canonical_json(value)
    if PRIVATE_PATH_PATTERN.search(encoded):
        raise ExperimentError("EXP-0014 projection contains private data")
    return value


def run_intake_projection(
    path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
    profile: dict[str, Any],
) -> dict[str, Any]:
    limits = profile["limits"]
    completed = run_bounded(
        [sys.executable, str(INTAKE_CLI_PATH), "--json", str(path)],
        timeout=limits["intake_timeout_seconds"],
        stdout_limit=limits["stdout_bytes"],
        stderr_limit=limits["stderr_bytes"],
    )
    if (
        completed.returncode != 0
        or completed.timed_out
        or completed.stdout_truncated
        or completed.stderr_truncated
        or completed.stderr
    ):
        raise ExperimentError("WI-0004 intake process failed closed")
    report = parse_intake_stdout(completed.stdout)
    validate_intake_report_dict(
        report,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
    )
    projection = project_intake_report(report)
    del report
    return projection


def aggregate_projections(reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not reports:
        raise ExperimentError("EXP-0014 projection set is empty")
    actions: Counter[str] = Counter()
    observations: Counter[str] = Counter()
    findings: Counter[str] = Counter()
    unclassified_observations = 0
    unclassified_findings = 0
    for report in reports:
        validated = validate_projection(report)
        actions[validated["next_action"]] += 1
        observations.update(validated["observation_codes"])
        findings.update(validated["finding_codes"])
        unclassified_observations += validated[
            "unclassified_observation_count"
        ]
        unclassified_findings += validated["unclassified_finding_count"]
    return {
        "finding_code_counts": dict(sorted(findings.items())),
        "next_action_counts": {key: actions[key] for key in NEXT_ACTIONS},
        "observation_code_counts": dict(sorted(observations.items())),
        "status": (
            "inconclusive"
            if unclassified_observations or unclassified_findings
            else "pass"
        ),
        "unclassified_finding_count": unclassified_findings,
        "unclassified_observation_count": unclassified_observations,
    }


def build_private_result(
    aggregate: dict[str, Any],
    *,
    input_count: int,
    intake_runs: int,
    execution_complete: bool,
    source_unchanged: bool,
    cleanup_complete: bool,
) -> dict[str, Any]:
    if (
        not execution_complete
        or not source_unchanged
        or not cleanup_complete
        or input_count != 3
        or intake_runs != 3
        or not isinstance(aggregate, dict)
        or set(aggregate) != AGGREGATE_FIELDS
    ):
        raise ExperimentError("private diagnostic completion differs")
    result = {
        "artifact": "EXP-0014",
        "cleanup_complete": True,
        "finding_code_counts": aggregate["finding_code_counts"],
        "input_count": 3,
        "intake_runs": 3,
        "next_action_counts": aggregate["next_action_counts"],
        "observation_code_counts": aggregate["observation_code_counts"],
        "path_free": True,
        "schema": RESULT_SCHEMA,
        "source_unchanged": True,
        "status": aggregate["status"],
        "unclassified_finding_count": aggregate[
            "unclassified_finding_count"
        ],
        "unclassified_observation_count": aggregate[
            "unclassified_observation_count"
        ],
    }
    return validate_private_result_dict(result)


def _validate_count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ExperimentError("EXP-0014 aggregate count differs")
    return value


def _validate_code_counts(value: Any, allowlist: tuple[str, ...]) -> dict[str, int]:
    if (
        not isinstance(value, dict)
        or list(value) != sorted(value)
        or any(key not in allowlist for key in value)
    ):
        raise ExperimentError("EXP-0014 code counts differ")
    for count in value.values():
        if _validate_count(count) < 1:
            raise ExperimentError("EXP-0014 code count differs")
    return value


def validate_private_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict) or set(result) != RESULT_FIELDS:
        raise ExperimentError("EXP-0014 result fields differ")
    if result.get("schema") != RESULT_SCHEMA or result.get("artifact") != "EXP-0014":
        raise ExperimentError("EXP-0014 result identity differs")
    if result.get("input_count") != 3 or result.get("intake_runs") != 3:
        raise ExperimentError("EXP-0014 result run count differs")
    if (
        result.get("source_unchanged") is not True
        or result.get("cleanup_complete") is not True
        or result.get("path_free") is not True
    ):
        raise ExperimentError("EXP-0014 result safety differs")
    actions = result.get("next_action_counts")
    if not isinstance(actions, dict) or set(actions) != set(NEXT_ACTIONS):
        raise ExperimentError("EXP-0014 action counts differ")
    for count in actions.values():
        _validate_count(count)
    if sum(actions.values()) != 3:
        raise ExperimentError("EXP-0014 action total differs")
    observations = _validate_code_counts(
        result.get("observation_code_counts"), OBSERVATION_CODES
    )
    _validate_code_counts(result.get("finding_code_counts"), FINDING_CODES)
    unclassified_observations = _validate_count(
        result.get("unclassified_observation_count")
    )
    unclassified_findings = _validate_count(
        result.get("unclassified_finding_count")
    )
    if sum(observations.values()) + unclassified_observations < 3:
        raise ExperimentError("EXP-0014 observation total differs")
    expected_status = (
        "inconclusive"
        if unclassified_observations or unclassified_findings
        else "pass"
    )
    if result.get("status") != expected_status:
        raise ExperimentError("EXP-0014 result status differs")
    encoded = canonical_json(result)
    if (
        len(encoded.encode("utf-8")) > _expected_limits()["output_bytes"]
        or PRIVATE_PATH_PATTERN.search(encoded)
    ):
        raise ExperimentError("EXP-0014 result contains private data")
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    return validate_private_result_dict(load_json(path))


def _has_reparse_attribute(value: os.stat_result) -> bool:
    return bool(getattr(value, "st_file_attributes", 0) & 0x400)


def _validate_no_indirect_component(path: Path) -> None:
    for component in (path, *path.parents):
        try:
            value = component.lstat()
        except OSError as exc:
            raise ExperimentError("private input is unavailable") from exc
        if component.is_symlink() or _has_reparse_attribute(value):
            raise ExperimentError("private input uses an indirect locator")


def validate_private_inputs(values: list[Path]) -> tuple[ValidatedInput, ...]:
    contract = _expected_input_contract()
    if len(values) != contract["count"]:
        raise ExperimentError("exactly three private EPUB inputs are required")
    validated: list[ValidatedInput] = []
    locator_keys: set[str] = set()
    file_keys: set[tuple[int, int]] = set()
    total = 0
    for raw in values:
        if ".." in raw.parts:
            raise ExperimentError("private input uses an indirect locator")
        absolute = Path(os.path.abspath(os.fspath(raw)))
        _validate_no_indirect_component(absolute)
        try:
            value = absolute.stat(follow_symlinks=False)
            resolved = absolute.resolve(strict=True)
        except OSError as exc:
            raise ExperimentError("private input is unavailable") from exc
        if not stat.S_ISREG(value.st_mode) or absolute.suffix.lower() != ".epub":
            raise ExperimentError("private input is not a regular EPUB")
        if not 0 < value.st_size <= contract["max_file_bytes"]:
            raise ExperimentError("private input size differs")
        absolute_key = os.path.normcase(os.path.normpath(os.fspath(absolute)))
        resolved_key = os.path.normcase(os.path.normpath(os.fspath(resolved)))
        if absolute_key != resolved_key or resolved_key in locator_keys:
            raise ExperimentError("private input locator is indirect or duplicated")
        file_key = (value.st_dev, value.st_ino)
        if value.st_ino and file_key in file_keys:
            raise ExperimentError("private input file is duplicated")
        locator_keys.add(resolved_key)
        file_keys.add(file_key)
        total += value.st_size
        validated.append(
            ValidatedInput(
                path=resolved,
                sha256=sha256_file(resolved),
                size_bytes=value.st_size,
            )
        )
    if total > contract["max_total_bytes"]:
        raise ExperimentError("private input total size differs")
    return tuple(validated)


def _source_matches(value: ValidatedInput) -> bool:
    try:
        current = value.path.stat(follow_symlinks=False)
        return (
            stat.S_ISREG(current.st_mode)
            and not _has_reparse_attribute(current)
            and not value.path.is_symlink()
            and current.st_size == value.size_bytes
            and sha256_file(value.path) == value.sha256
        )
    except OSError:
        return False


def _ensure_temp_root(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve(strict=True)
    allowed = ALLOWED_TEMP_ROOT.resolve(strict=True)
    if resolved != allowed:
        raise ExperimentError("EXP-0014 temp root differs")
    return resolved


def _create_task_root(temp_root: Path, prefix: str) -> Path:
    task = Path(tempfile.mkdtemp(prefix=prefix, dir=temp_root)).resolve(strict=True)
    if task.parent != temp_root or not task.name.startswith(prefix):
        raise ExperimentError("owned task root differs")
    return task


def _remove_owned_task(task_root: Path, temp_root: Path, prefix: str) -> bool:
    resolved = task_root.resolve(strict=True)
    if resolved.parent != temp_root or not resolved.name.startswith(prefix):
        raise ExperimentError("owned task cleanup boundary differs")
    for item in sorted(
        resolved.rglob("*"), key=lambda value: len(value.parts), reverse=True
    ):
        if item.is_symlink():
            continue
        if item.is_file():
            item.chmod(stat.S_IREAD | stat.S_IWRITE)
        elif item.is_dir():
            item.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    resolved.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    shutil.rmtree(resolved)
    return not resolved.exists()


def _expect_failure(action: Callable[[], Any]) -> None:
    try:
        action()
    except ExperimentError:
        return
    raise ExperimentError("synthetic negative control did not fail closed")


def _synthetic_report(
    *,
    observation_codes: list[str] | None = None,
    finding_codes: list[str] | None = None,
    next_action: str = "continue_deep_read_only",
    sensitive_value: str | None = None,
) -> dict[str, Any]:
    expected_hash = "a" * 64
    observations = [
        {"code": "input.size", "values": {"size_bytes": 1}},
        {"code": "input.sha256", "values": {"sha256": expected_hash}},
        {"code": "snapshot.stable", "values": {}},
    ]
    for code in observation_codes or []:
        values = {"private_value": sensitive_value} if sensitive_value else {}
        observations.append({"code": code, "values": values})
    return {
        "deep_read_only_allowed": next_action == "continue_deep_read_only",
        "effects": dict(EFFECTS),
        "findings": [
            {"code": code, "values": {}} for code in (finding_codes or [])
        ],
        "format_capability": "supported",
        "limits": dict(TRIAGE_LIMITS),
        "next_action": next_action,
        "observations": observations,
        "schema": INTAKE_SCHEMA,
        "snapshot": {"sha256": expected_hash, "size_bytes": 1},
    }


def run_negative_controls(control_root: Path) -> int:
    control_root.mkdir()
    inputs: list[Path] = []
    for name in ("a.epub", "b.epub", "c.epub", "d.epub"):
        path = control_root / name
        path.write_bytes(f"synthetic-{name}".encode("ascii"))
        inputs.append(path)
    validate_private_inputs(inputs[:3])
    directory = control_root / "directory.epub"
    directory.mkdir()
    link = control_root / "link.epub"
    try:
        link.symlink_to(inputs[0])
    except OSError as exc:
        raise ExperimentError("synthetic link control is unavailable") from exc
    oversized = control_root / "oversized.epub"
    with oversized.open("wb") as stream:
        stream.truncate(4 * 1024 * 1024 + 1)
    _expect_failure(lambda: validate_private_inputs(inputs[:2]))
    _expect_failure(lambda: validate_private_inputs(inputs))
    _expect_failure(
        lambda: validate_private_inputs([inputs[0], inputs[0], inputs[1]])
    )
    _expect_failure(
        lambda: validate_private_inputs([inputs[0], inputs[1], directory])
    )
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], link]))
    _expect_failure(
        lambda: validate_private_inputs([inputs[0], inputs[1], oversized])
    )

    complete_projection = {
        "finding_codes": ["format.epub"],
        "next_action": "continue_deep_read_only",
        "observation_codes": ["snapshot.stable"],
        "unclassified_finding_count": 0,
        "unclassified_observation_count": 0,
    }
    aggregate = aggregate_projections([complete_projection] * 3)
    _expect_failure(
        lambda: build_private_result(
            aggregate,
            input_count=3,
            intake_runs=2,
            execution_complete=False,
            source_unchanged=True,
            cleanup_complete=True,
        )
    )
    _expect_failure(lambda: parse_intake_stdout(b"{"))

    unknown_report = _synthetic_report(
        observation_codes=["future.unknown_observation"],
        finding_codes=["future.unknown_finding"],
        sensitive_value="SENSITIVE_EVIDENCE_VALUE",
    )
    validate_intake_report_dict(
        unknown_report,
        expected_sha256="a" * 64,
        expected_size=1,
    )
    masked = project_intake_report(unknown_report)
    if (
        masked["unclassified_observation_count"] != 1
        or masked["unclassified_finding_count"] != 1
        or "future.unknown" in canonical_json(masked)
        or "SENSITIVE_EVIDENCE_VALUE" in canonical_json(masked)
    ):
        raise ExperimentError("unknown code masking differs")

    valid = build_private_result(
        aggregate,
        input_count=3,
        intake_runs=3,
        execution_complete=True,
        source_unchanged=True,
        cleanup_complete=True,
    )
    private_field = dict(valid)
    private_field["title"] = "private"
    _expect_failure(lambda: validate_private_result_dict(private_field))
    _expect_failure(
        lambda: build_private_result(
            aggregate,
            input_count=3,
            intake_runs=3,
            execution_complete=True,
            source_unchanged=True,
            cleanup_complete=False,
        )
    )
    return len(NEGATIVE_CONTROLS)


def run_synthetic_controls(
    temp_root: Path = ALLOWED_TEMP_ROOT,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = profile or validate_contract()
    require_committed_preimage()
    temp_root = _ensure_temp_root(temp_root)
    fixture_before = {
        locator: sha256_file(ROOT / locator) for locator, _action in CONTROL_CASES
    }
    task_root = _create_task_root(temp_root, "synthetic-")
    control_root = task_root / "negative-controls"
    projections: list[dict[str, Any]] = []
    negative_count = 0
    repetitions_identical = False
    source_unchanged = False
    task_removed = False
    failure: BaseException | None = None
    cleanup_failure: BaseException | None = None
    try:
        for locator, expected_action in CONTROL_CASES:
            source = ROOT / locator
            projection = run_intake_projection(
                source,
                expected_sha256=fixture_before[locator],
                expected_size=source.stat().st_size,
                profile=profile,
            )
            if projection["next_action"] != expected_action:
                raise ExperimentError("synthetic WI-0004 action differs")
            if (
                projection["unclassified_observation_count"]
                or projection["unclassified_finding_count"]
            ):
                raise ExperimentError("synthetic WI-0004 code binding differs")
            projections.append(projection)
        if len(projections) != 4 or aggregate_projections(projections)["status"] != "pass":
            raise ExperimentError("synthetic WI-0004 controls differ")
        matrix = profile["synthetic_controls"]["projection_matrix"]
        first = aggregate_projections(matrix["reports"])
        second = aggregate_projections(
            json.loads(canonical_json(matrix["reports"]))
        )
        repetitions_identical = canonical_json(first) == canonical_json(second)
        if first != matrix["expected"] or not repetitions_identical:
            raise ExperimentError("synthetic projection control differs")
        negative_count = run_negative_controls(control_root)
        source_unchanged = fixture_before == {
            locator: sha256_file(ROOT / locator) for locator, _action in CONTROL_CASES
        }
    except BaseException as exc:
        failure = exc
    try:
        source_unchanged = fixture_before == {
            locator: sha256_file(ROOT / locator) for locator, _action in CONTROL_CASES
        }
    except OSError:
        source_unchanged = False
    try:
        task_removed = _remove_owned_task(task_root, temp_root, "synthetic-")
    except BaseException as exc:
        cleanup_failure = exc
    cleanup_complete = task_removed
    if cleanup_failure is not None or not cleanup_complete or not source_unchanged:
        raise ExperimentError("synthetic cleanup or source proof differs") from (
            cleanup_failure or failure
        )
    if failure is not None:
        raise failure
    summary = {
        "artifact": "EXP-0014",
        "cleanup_complete": True,
        "intake_runs": len(projections),
        "negative_controls": negative_count,
        "path_free": True,
        "repetitions_identical": repetitions_identical,
        "schema": SYNTHETIC_SCHEMA,
        "source_unchanged": True,
        "status": "pass",
    }
    if PRIVATE_PATH_PATTERN.search(canonical_json(summary)):
        raise ExperimentError("synthetic summary contains private data")
    return summary


def _write_result_once(path: Path, result: dict[str, Any]) -> None:
    if path.exists():
        raise ExperimentError("EXP-0014 result already exists")
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()


def execute_private_diagnostic(
    values: list[Path],
    *,
    confirmed_same_inputs: bool,
    temp_root: Path = ALLOWED_TEMP_ROOT,
    result_path: Path = RESULT_PATH,
) -> dict[str, Any]:
    profile = validate_contract()
    require_committed_preimage()
    if not confirmed_same_inputs:
        raise ExperimentError("same EXP-0013 input set is not confirmed")
    validated = validate_private_inputs(values)
    if result_path.exists():
        raise ExperimentError("EXP-0014 result already exists")
    temp_root = _ensure_temp_root(temp_root)
    run_synthetic_controls(temp_root, profile)

    task_root = _create_task_root(temp_root, "private-")
    inputs_root = task_root / "inputs"
    projections: list[dict[str, Any]] = []
    copied: list[tuple[Path, ValidatedInput]] = []
    execution_complete = False
    source_unchanged = False
    targets_unchanged = False
    task_removed = False
    failure: BaseException | None = None
    cleanup_failure: BaseException | None = None
    try:
        inputs_root.mkdir()
        for index, source in enumerate(validated, start=1):
            target = inputs_root / f"input-{index}.epub"
            shutil.copyfile(source.path, target)
            if sha256_file(target) != source.sha256:
                raise ExperimentError("private copy differs")
            target.chmod(stat.S_IREAD)
            copied.append((target, source))
        for target, source in copied:
            projections.append(
                run_intake_projection(
                    target,
                    expected_sha256=source.sha256,
                    expected_size=source.size_bytes,
                    profile=profile,
                )
            )
        execution_complete = len(projections) == 3
        targets_unchanged = all(
            target.is_file() and sha256_file(target) == source.sha256
            for target, source in copied
        )
        source_unchanged = all(_source_matches(source) for source in validated)
    except BaseException as exc:
        failure = exc
    try:
        source_unchanged = all(_source_matches(source) for source in validated)
    except OSError:
        source_unchanged = False
    try:
        targets_unchanged = all(
            target.is_file() and sha256_file(target) == source.sha256
            for target, source in copied
        )
    except OSError:
        targets_unchanged = False
    try:
        task_removed = _remove_owned_task(task_root, temp_root, "private-")
    except BaseException as exc:
        cleanup_failure = exc
    cleanup_complete = task_removed
    if (
        cleanup_failure is not None
        or not cleanup_complete
        or not source_unchanged
        or not targets_unchanged
    ):
        raise ExperimentError("private cleanup or source proof differs") from (
            cleanup_failure or failure
        )
    if failure is not None:
        raise failure
    aggregate = aggregate_projections(projections)
    result = build_private_result(
        aggregate,
        input_count=len(validated),
        intake_runs=len(projections),
        execution_complete=execution_complete,
        source_unchanged=source_unchanged,
        cleanup_complete=cleanup_complete,
    )
    _write_result_once(result_path, result)
    return result


def parser() -> SafeArgumentParser:
    value = SafeArgumentParser(description=__doc__)
    value.add_argument("--validate-profile", action="store_true")
    value.add_argument("--validate-result", action="store_true")
    value.add_argument("--synthetic-controls", action="store_true")
    value.add_argument("--private-epub", action="append", type=Path, default=[])
    value.add_argument("--confirm-same-exp-0013-inputs", action="store_true")
    return value


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        modes = sum(
            (
                args.validate_profile,
                args.validate_result,
                args.synthetic_controls,
                bool(args.private_epub),
            )
        )
        if modes != 1:
            raise ExperimentError("exactly one EXP-0014 execution mode is required")
        if args.confirm_same_exp_0013_inputs and not args.private_epub:
            raise ExperimentError("input confirmation differs")
        if args.validate_profile:
            validate_contract()
            print("EXP-0014 profile valid")
            return 0
        if args.validate_result:
            result = validate_result()
            print(f"EXP-0014 result valid: {result['status']}")
            return 0
        profile = validate_contract()
        if args.synthetic_controls:
            summary = run_synthetic_controls(ALLOWED_TEMP_ROOT, profile)
            print(canonical_json(summary))
            return 0
        result = execute_private_diagnostic(
            args.private_epub,
            confirmed_same_inputs=args.confirm_same_exp_0013_inputs,
        )
        print(canonical_json(result))
        return 2 if result["status"] == "inconclusive" else 0
    except KeyboardInterrupt:
        return 130
    except ExperimentError as exc:
        print(f"EXP-0014 failed closed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"EXP-0014 failed closed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
