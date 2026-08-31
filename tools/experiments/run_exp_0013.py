#!/usr/bin/env python3
"""Run or validate the bounded, product-code-free EXP-0013 diagnostic."""

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
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
for import_root in (ROOT / "src", ROOT / "tools"):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import materialize_calibre_qualification_library as materializer  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.ebook_intake.podman_executor import run_bounded  # noqa: E402


EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0013"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
RESULT_PATH = EXPERIMENT / "result.json"
EXP_0012_MANIFEST_PATH = ROOT / "experiments" / "ebook" / "exp-0012" / "case-manifest.json"
RUNTIME_PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
IDENTITY_PROFILE_PATH = ROOT / "runtime" / "ebook-calibre-identity" / "profile.json"
IDENTITY_CLI_PATH = ROOT / "tools" / "run_ebook_calibre_identity.py"
TEST_0001_MANIFEST_PATH = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "manifest.json"
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse\exp-0013")
CONTAINER_PREFIX = "sammlungslotse-exp0013-"
CONTROL_RECORD_IDS = (1, 4, 9)
CONTROL_FIXTURE_LOCATORS = (
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-byte-equal/source-a/same.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-title-collision/work-a.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-repackaged/package-b.epub",
)
PREIMAGE_FILES = (
    "docs/planning/EBOOK_PRIVATE_WI0011_NONCOMPLETION_DIAGNOSTIC_EXPERIMENT.md",
    "experiments/ebook/exp-0013/README.md",
    "experiments/ebook/exp-0013/execution-profile.json",
    "tests/experiments/test_exp_0013.py",
    "tools/experiments/run_exp_0013.py",
    "experiments/ebook/exp-0012/case-manifest.json",
    "runtime/calibre-readonly/profile.json",
    "runtime/ebook-calibre-identity/profile.json",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    "tools/materialize_calibre_qualification_library.py",
    "tools/run_ebook_calibre_identity.py",
    "src/sammlungslotse/calibre_inventory/profile.py",
    "src/sammlungslotse/calibre_inventory/workspace.py",
    "src/sammlungslotse/ebook_calibre_identity/application.py",
    "src/sammlungslotse/ebook_calibre_identity/cli.py",
    "src/sammlungslotse/ebook_calibre_identity/executor.py",
    "src/sammlungslotse/ebook_calibre_identity/model.py",
    "src/sammlungslotse/ebook_calibre_identity/profile.py",
    "src/sammlungslotse/ebook_calibre_identity/provider.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/application.py",
    "src/sammlungslotse/ebook_intake/model.py",
    "src/sammlungslotse/ebook_intake/podman_executor.py",
    "src/sammlungslotse/ebook_intake/ports.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    *CONTROL_FIXTURE_LOCATORS,
)

PRIVATE_PATH_PATTERN = re.compile(
    r"(?:(?<![A-Za-z0-9_])[A-Za-z]:[\\/]|/(?:home|Users|tmp|library|input|private)(?:[\\/]|$))",
    re.IGNORECASE,
)
REASON_CODE_PATTERN = re.compile(
    r"[a-z][a-z0-9_]{0,31}(?:\.[a-z][a-z0-9_]{0,31}){1,3}"
)
SEARCH_OUTPUT = re.compile(rb"\s*(?:[1-9][0-9]*(?:,[1-9][0-9]*)*)?\s*")
RESULT_SCHEMA = "sammlungslotse/exp-0013-private-diagnostic-result/v1"
SYNTHETIC_SCHEMA = "sammlungslotse/exp-0013-synthetic-control-summary/v1"
ASSESSMENT_KEYS = ("completed", "not_assessed")
ENTRY_STAGE_KEYS = (
    "completed",
    "identity_analysis",
    "ingress_preflight",
    "record_handoff",
    "unclassified",
)
RESULT_FIELDS = frozenset(
    {
        "artifact",
        "assessment_counts",
        "cleanup_complete",
        "entry_stage_counts",
        "input_count",
        "path_free",
        "reason_code_counts",
        "schema",
        "search_runs",
        "source_unchanged",
        "status",
        "wi0011_runs",
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
    "private_output_field",
    "incomplete_cleanup",
)


class ExperimentError(RuntimeError):
    """Raised when an EXP-0013 boundary cannot be proven."""


class SafeArgumentParser(argparse.ArgumentParser):
    """Avoid reflecting a private argument value in parser errors."""

    def error(self, message: str) -> None:
        raise ExperimentError("command line differs")


@dataclass(frozen=True, slots=True)
class ValidatedInput:
    path: Path
    sha256: str
    size_bytes: int


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
        if sha256_bytes(git_output("show", f"HEAD:{locator}")) != sha256_file(ROOT / locator):
            raise ExperimentError("EXP-0013 preimage is not fully committed")
    return commit


def _expected_commands() -> dict[str, Any]:
    return {
        "identity": "tools/run_ebook_calibre_identity.py --json",
        "projection_fields": ["title", "authors", "languages", "formats", "identifiers"],
        "search_limit": 5,
        "search_program": "calibredb",
        "search_variants": ["V1", "V2"],
    }


def _expected_input_contract() -> dict[str, Any]:
    return {
        "confirmation_flag": "--confirm-same-exp-0012-inputs",
        "count": 3,
        "max_file_bytes": 4 * 1024 * 1024,
        "max_total_bytes": 12 * 1024 * 1024,
        "regular_files_only": True,
        "suffix": ".epub",
    }


def _expected_limits() -> dict[str, int]:
    return {
        "identity_timeout_seconds": 40,
        "max_reason_code_bytes": 96,
        "max_reason_codes_per_report": 1,
        "output_bytes": 8192,
        "private_search_runs": 4,
        "query_bytes": 512,
        "stderr_bytes": 131072,
        "stdout_bytes": 131072,
        "step_timeout_seconds": 30,
        "synthetic_wi0011_runs": 3,
    }


def validate_contract() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profile = load_json(PROFILE_PATH)
    if set(profile) != {
        "artifact",
        "commands",
        "implementation",
        "input_contract",
        "limits",
        "output_contract",
        "profile_id",
        "runtime_bindings",
        "schema",
        "synthetic_controls",
    }:
        raise ExperimentError("EXP-0013 profile fields differ")
    if profile.get("schema") != "sammlungslotse/exp-0013-execution-profile/v1":
        raise ExperimentError("EXP-0013 profile schema differs")
    if profile.get("artifact") != "EXP-0013":
        raise ExperimentError("EXP-0013 artifact differs")
    if profile.get("profile_id") != "exp-0013-private-wi0011-noncompletion/v1":
        raise ExperimentError("EXP-0013 profile identity differs")
    if profile.get("commands") != _expected_commands():
        raise ExperimentError("EXP-0013 commands differ")
    if profile.get("input_contract") != _expected_input_contract():
        raise ExperimentError("EXP-0013 input contract differs")
    if profile.get("limits") != _expected_limits():
        raise ExperimentError("EXP-0013 limits differ")
    implementation = profile.get("implementation")
    if not isinstance(implementation, dict) or set(implementation) != {
        "direct_database_access",
        "directory_discovery",
        "network_access",
        "persistence",
        "private_values_retained",
        "product_code_changes",
        "writer_surface",
    } or any(value is not False for value in implementation.values()):
        raise ExperimentError("EXP-0013 implementation boundary differs")
    output = profile.get("output_contract", {})
    if output != {
        "allowed_fields": sorted(RESULT_FIELDS),
        "schema": RESULT_SCHEMA,
        "statuses": ["pass", "not_qualified", "inconclusive"],
    }:
        raise ExperimentError("EXP-0013 output contract differs")

    bindings = profile.get("runtime_bindings", {})
    expected_bindings = {
        "calibre": (
            RUNTIME_PROFILE_PATH,
            "runtime/calibre-readonly/profile.json",
            "wi-0007-calibre-9.13.0-podman-linux-amd64/v1",
        ),
        "exp_0012_manifest": (
            EXP_0012_MANIFEST_PATH,
            "experiments/ebook/exp-0012/case-manifest.json",
            None,
        ),
        "identity": (
            IDENTITY_PROFILE_PATH,
            "runtime/ebook-calibre-identity/profile.json",
            "wi-0011-calibre-identity-handoff/v1",
        ),
        "test_0001": (
            TEST_0001_MANIFEST_PATH,
            "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
            None,
        ),
    }
    if set(bindings) != set(expected_bindings):
        raise ExperimentError("EXP-0013 runtime bindings differ")
    for name, (path, locator, profile_id) in expected_bindings.items():
        binding = bindings.get(name, {})
        expected_fields = {"locator", "sha256"}
        if profile_id is not None:
            expected_fields.add("profile_id")
        if name == "calibre":
            expected_fields.add("image_id")
        if name == "test_0001":
            expected_fields.add("version")
        if not isinstance(binding, dict) or set(binding) != expected_fields:
            raise ExperimentError(f"EXP-0013 {name} binding fields differ")
        if binding.get("sha256") != sha256_file(path):
            raise ExperimentError(f"EXP-0013 {name} binding differs")
        if binding.get("locator") != locator:
            raise ExperimentError(f"EXP-0013 {name} locator differs")
        if profile_id is not None and binding.get("profile_id") != profile_id:
            raise ExperimentError(f"EXP-0013 {name} profile differs")
    if bindings["calibre"].get("image_id") != (
        "sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5"
    ):
        raise ExperimentError("EXP-0013 Calibre image differs")
    if bindings["test_0001"].get("version") != "0.3.0":
        raise ExperimentError("EXP-0013 TEST-0001 version differs")

    manifest = load_json(EXP_0012_MANIFEST_PATH)
    records = [
        record for record in manifest.get("records", [])
        if record.get("expected_id") in CONTROL_RECORD_IDS
    ]
    if [record.get("expected_id") for record in records] != list(CONTROL_RECORD_IDS):
        raise ExperimentError("EXP-0013 control records differ")
    for record, locator in zip(records, CONTROL_FIXTURE_LOCATORS, strict=True):
        if record.get("fixture") != locator or record.get("sha256") != sha256_file(ROOT / locator):
            raise ExperimentError("EXP-0013 control fixture differs")

    controls = profile.get("synthetic_controls", {})
    if controls.get("actual_wi0011_record_ids") != list(CONTROL_RECORD_IDS):
        raise ExperimentError("EXP-0013 WI-0011 controls differ")
    if controls.get("aggregation_repetitions") != 2:
        raise ExperimentError("EXP-0013 aggregation repetitions differ")
    if controls.get("negative_controls") != list(NEGATIVE_CONTROLS):
        raise ExperimentError("EXP-0013 negative controls differ")
    matrix = controls.get("aggregation_matrix", {})
    reports = matrix.get("reports")
    if not isinstance(reports, list) or aggregate_diagnostics(reports) != matrix.get("expected"):
        raise ExperimentError("EXP-0013 aggregation matrix differs")
    return profile, records


def _container_names() -> list[str]:
    completed = run_bounded(
        ["podman", "ps", "-a", "--format", "{{.Names}}"],
        timeout=15,
        stdout_limit=131072,
        stderr_limit=131072,
    )
    if completed.returncode != 0 or completed.timed_out or completed.stdout_truncated:
        raise ExperimentError("Podman container inventory failed")
    return sorted(completed.stdout.decode("utf-8").splitlines())


def _image_matches(profile: CalibreRuntimeProfile) -> bool:
    completed = run_bounded(
        ["podman", "image", "inspect", profile.image["id"], "--format", "json"],
        timeout=15,
        stdout_limit=131072,
        stderr_limit=131072,
    )
    if completed.returncode != 0 or completed.timed_out:
        return False
    value = json.loads(completed.stdout)[0]
    actual_id = str(value.get("Id", ""))
    if actual_id and not actual_id.startswith("sha256:"):
        actual_id = f"sha256:{actual_id}"
    return (
        actual_id == profile.image["id"]
        and value.get("Architecture") == "amd64"
        and value.get("Os") == "linux"
        and value.get("Config", {}).get("Entrypoint") == profile.image["entrypoint"]
    )


def run_calibre(
    library: Path,
    profile: CalibreRuntimeProfile,
    arguments: list[str],
    fixture: Path | None = None,
) -> bytes:
    name = f"{CONTAINER_PREFIX}{uuid.uuid4().hex[:16]}"
    created = False
    try:
        create = materializer._create_arguments(name, library, profile, arguments, fixture)
        create[create.index("--name") + 1] = name
        completed = run_bounded(
            create,
            timeout=15,
            stdout_limit=4096,
            stderr_limit=131072,
        )
        if completed.returncode != 0 or completed.timed_out:
            raise ExperimentError("Calibre container could not be created")
        created = True
        inspection = run_bounded(
            ["podman", "inspect", name, "--format", "json"],
            timeout=15,
            stdout_limit=262144,
            stderr_limit=131072,
        )
        if inspection.returncode != 0 or inspection.timed_out:
            raise ExperimentError("Calibre container inspection failed")
        if not materializer._isolation_matches(
            json.loads(inspection.stdout)[0], profile, fixture is not None
        ):
            raise ExperimentError("Calibre container isolation differs")
        execution = run_bounded(
            ["podman", "start", "--attach", name],
            timeout=30,
            stdout_limit=131072,
            stderr_limit=131072,
        )
        empty_search = (
            arguments[0] == "search"
            and execution.returncode == 1
            and not execution.stdout.strip()
            and execution.stderr
            == b"No books matching the search expression: " + arguments[-1].encode("utf-8") + b"\n"
        )
        if (
            (execution.returncode != 0 and not empty_search)
            or execution.timed_out
            or execution.stdout_truncated
            or execution.stderr_truncated
        ):
            raise ExperimentError("Calibre command failed closed")
        return bytes(execution.stdout)
    finally:
        if created:
            removed = run_bounded(
                ["podman", "rm", "--force", name],
                timeout=15,
                stdout_limit=4096,
                stderr_limit=4096,
            )
            if removed.returncode != 0 or removed.timed_out:
                raise ExperimentError("Calibre container cleanup failed")


def _format_tokens(value: Any) -> list[str]:
    if value is None:
        values: list[str] = []
    elif isinstance(value, str):
        values = [item.strip() for item in value.split(",") if item.strip()]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        values = value
    else:
        raise ExperimentError("Calibre format projection differs")
    result = sorted({Path(item).suffix.lower().removeprefix(".") or item.lower() for item in values})
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9+_-]{0,15}", item) for item in result):
        raise ExperimentError("Calibre format token differs")
    return result


def project_records(
    library: Path,
    runtime: CalibreRuntimeProfile,
    external_record_id: int | None = None,
) -> list[dict[str, Any]]:
    arguments = [
        "list", "--with-library", "/library", "--for-machine",
        "--fields", "title,authors,languages,formats,identifiers",
        "--sort-by", "id", "--ascending",
    ]
    if external_record_id is not None:
        arguments.extend(("--search", f"id:={external_record_id}", "--limit", "1"))
    value = json.loads(run_calibre(library, runtime, arguments).decode("utf-8"))
    if not isinstance(value, list):
        raise ExperimentError("Calibre projection root differs")
    result: list[dict[str, Any]] = []
    for record in value:
        if not isinstance(record, dict) or not set(record).issubset(
            {"id", "_source_id", "title", "authors", "languages", "formats", "identifiers"}
        ):
            raise ExperimentError("Calibre projection fields differ")
        source_id = record.get("id", record.get("_source_id"))
        if isinstance(source_id, bool) or not isinstance(source_id, int) or source_id < 1:
            raise ExperimentError("Calibre projection ID differs")
        authors = record.get("authors", [])
        if isinstance(authors, str):
            authors = [item.strip() for item in authors.split(" & ") if item.strip()]
        languages = record.get("languages", [])
        if isinstance(languages, str):
            languages = [item.strip() for item in languages.split(",") if item.strip()]
        identifiers = record.get("identifiers") or {}
        if (
            not isinstance(authors, list)
            or not all(isinstance(item, str) for item in authors)
            or not isinstance(languages, list)
            or not all(isinstance(item, str) for item in languages)
            or not isinstance(identifiers, dict)
            or not all(isinstance(key, str) and isinstance(item, str) for key, item in identifiers.items())
            or not isinstance(record.get("title", ""), str)
        ):
            raise ExperimentError("Calibre projection value type differs")
        result.append(
            {
                "authors": authors,
                "external_record_id": source_id,
                "formats": _format_tokens(record.get("formats")),
                "identifiers": dict(sorted(identifiers.items())),
                "languages": languages,
                "title": record.get("title", ""),
            }
        )
    result.sort(key=lambda item: item["external_record_id"])
    if external_record_id is not None and (
        len(result) != 1 or result[0]["external_record_id"] != external_record_id
    ):
        raise ExperimentError("Calibre single-record projection differs")
    return result


def _authors_argument(authors: list[str]) -> str:
    if not authors or any("&" in author for author in authors):
        raise ExperimentError("Calibre author separator is ambiguous")
    return " & ".join(authors)


def materialize_control_library(
    library: Path,
    runtime: CalibreRuntimeProfile,
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    library.mkdir()
    for assigned_id, record in enumerate(records, start=1):
        arguments = [
            "add", "--with-library", "/library", "--duplicates",
            "--title", record["title"], "--authors", _authors_argument(record["authors"]),
            "--languages", ",".join(record["languages"]), "--empty",
        ]
        for key, value in sorted(record["identifiers"].items()):
            arguments.extend(("--identifier", f"{key}:{value}"))
        run_calibre(library, runtime, arguments)
        run_calibre(
            library,
            runtime,
            ["add_format", "--with-library", "/library", str(assigned_id), "/input/book.epub"],
            ROOT / record["fixture"],
        )
    projection = project_records(library, runtime)
    if [item["external_record_id"] for item in projection] != [1, 2, 3]:
        raise ExperimentError("synthetic Calibre IDs differ")
    for index, item in enumerate(projection):
        record = records[index]
        compared = {key: item[key] for key in ("authors", "identifiers", "languages", "title")}
        expected = {key: record[key] for key in ("authors", "identifiers", "languages", "title")}
        if compared != expected or item["formats"] != ["epub"]:
            raise ExperimentError("synthetic Calibre projection differs")
    return projection


def materialize_private_library(
    library: Path,
    runtime: CalibreRuntimeProfile,
    inputs: list[Path],
) -> list[dict[str, Any]]:
    library.mkdir()
    for value in inputs:
        run_calibre(
            library,
            runtime,
            ["add", "--with-library", "/library", "--duplicates", "/input/book.epub"],
            value,
        )
    projection = project_records(library, runtime)
    if len(projection) != 3 or [item["external_record_id"] for item in projection] != [1, 2, 3]:
        raise ExperimentError("private materialization count differs")
    return projection


def _quoted(value: str) -> str:
    if not value or any(character in value for character in ('"', "\r", "\n")):
        raise ExperimentError("search literal differs")
    return value


def query_for(record: dict[str, Any], variant: str) -> str:
    if variant == "V1":
        identifiers = record["identifiers"]
        if not identifiers:
            raise ExperimentError("identifier search is not applicable")
        key, value = sorted(identifiers.items())[0]
        query = f"identifiers:={_quoted(key)}:={_quoted(value)}"
    elif variant == "V2":
        if not record["title"] or not record["authors"]:
            raise ExperimentError("title-author search is not applicable")
        query = f'title:"={_quoted(record["title"])}" and author:"={_quoted(record["authors"][0])}"'
    else:
        raise ExperimentError("unknown search variant")
    if len(query.encode("utf-8")) > 512:
        raise ExperimentError("search query exceeds bound")
    return query


def search_ids(library: Path, runtime: CalibreRuntimeProfile, query: str) -> list[int]:
    raw = run_calibre(
        library,
        runtime,
        ["search", "--with-library", "/library", "--limit", "5", query],
    )
    if not SEARCH_OUTPUT.fullmatch(raw):
        raise ExperimentError("Calibre search output differs")
    stripped = raw.strip()
    values = [] if not stripped else [int(item) for item in stripped.split(b",")]
    result = sorted(set(values))
    if len(result) != len(values) or len(result) > 5:
        raise ExperimentError("Calibre search candidate bound differs")
    return result


def run_self_searches(
    library: Path,
    runtime: CalibreRuntimeProfile,
    record: dict[str, Any],
) -> int:
    runs = 0
    if record["title"] and record["authors"]:
        if record["external_record_id"] not in search_ids(library, runtime, query_for(record, "V2")):
            raise ExperimentError("private exact search missed its own record")
        runs += 1
    if record["identifiers"]:
        if record["external_record_id"] not in search_ids(library, runtime, query_for(record, "V1")):
            raise ExperimentError("private identifier search missed its own record")
        runs += 1
    return runs


def _safe_reason_code(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value.encode("utf-8")) > 96
        or REASON_CODE_PATTERN.fullmatch(value) is None
        or PRIVATE_PATH_PATTERN.search(value)
    ):
        raise ExperimentError("WI-0011 reason code differs")
    return value


def run_identity_diagnostic(
    input_path: Path,
    library: Path,
    external_record_id: int,
    identity_temp_root: Path,
) -> dict[str, Any]:
    identity_temp_root.mkdir(parents=True, exist_ok=True)
    completed = run_bounded(
        [
            sys.executable,
            str(IDENTITY_CLI_PATH),
            str(input_path),
            str(library),
            str(external_record_id),
            "--json",
            "--profile",
            str(IDENTITY_PROFILE_PATH),
            "--runtime-profile",
            str(RUNTIME_PROFILE_PATH),
            "--temp-root",
            str(identity_temp_root),
        ],
        timeout=40,
        stdout_limit=131072,
        stderr_limit=131072,
    )
    if (
        completed.returncode not in (0, 4)
        or completed.timed_out
        or completed.stdout_truncated
        or completed.stderr_truncated
    ):
        raise ExperimentError("WI-0011 diagnostic failed closed")
    report = json.loads(completed.stdout.decode("utf-8"))
    if PRIVATE_PATH_PATTERN.search(canonical_json(report)):
        raise ExperimentError("WI-0011 report contains a path")
    if report.get("schema") != "sammlungslotse/ebook-calibre-identity-candidate-report/v1":
        raise ExperimentError("WI-0011 report schema differs")
    assessment = report.get("assessment")
    codes = report.get("handoff_reason_codes")
    if assessment not in ASSESSMENT_KEYS or not isinstance(codes, list):
        raise ExperimentError("WI-0011 diagnostic assessment differs")
    if assessment == "completed" and (codes or completed.returncode != 0):
        raise ExperimentError("WI-0011 completed diagnostic differs")
    if assessment == "not_assessed" and (len(codes) != 1 or completed.returncode != 4):
        raise ExperimentError("WI-0011 noncompletion diagnostic differs")
    safe_codes = [_safe_reason_code(value) for value in codes]
    effects = report.get("effects")
    if not isinstance(effects, dict) or set(effects) != {
        "cleanup_complete",
        "container_started",
        "domain_system_writes",
        "network_access",
        "persistence",
        "source_modified",
        "task_materialized",
        "writer",
    } or any(not isinstance(value, bool) for value in effects.values()):
        raise ExperimentError("WI-0011 effects differ")
    if (
        effects["cleanup_complete"] is not True
        or effects["domain_system_writes"] is not False
        or effects["network_access"] is not False
        or effects["persistence"] is not False
        or effects["source_modified"] is not False
        or effects["writer"] is not False
    ):
        raise ExperimentError("WI-0011 safety effects differ")
    return {"assessment": assessment, "handoff_reason_codes": safe_codes}


def classify_entry_stage(report: dict[str, Any]) -> str:
    if not isinstance(report, dict) or set(report) != {"assessment", "handoff_reason_codes"}:
        raise ExperimentError("diagnostic report fields differ")
    assessment = report.get("assessment")
    codes = report.get("handoff_reason_codes")
    if assessment == "completed" and codes == []:
        return "completed"
    if assessment != "not_assessed" or not isinstance(codes, list) or len(codes) != 1:
        raise ExperimentError("diagnostic report shape differs")
    code = _safe_reason_code(codes[0])
    if code == "ingress.preflight_gate_not_open":
        return "ingress_preflight"
    if code == "identity.not_assessed":
        return "identity_analysis"
    if code.split(".", 1)[0] in {"configuration", "executor", "library", "provider", "workspace"}:
        return "record_handoff"
    return "unclassified"


def aggregate_diagnostics(reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not reports:
        raise ExperimentError("diagnostic report set is empty")
    assessments: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    stages: Counter[str] = Counter()
    for report in reports:
        assessment = report.get("assessment")
        if assessment not in ASSESSMENT_KEYS:
            raise ExperimentError("diagnostic assessment differs")
        stage = classify_entry_stage(report)
        assessments[assessment] += 1
        stages[stage] += 1
        for code in report["handoff_reason_codes"]:
            reasons[_safe_reason_code(code)] += 1
    status = (
        "inconclusive"
        if stages["unclassified"]
        else "pass"
        if assessments["completed"] == len(reports)
        else "not_qualified"
    )
    return {
        "assessment_counts": {key: assessments[key] for key in ASSESSMENT_KEYS},
        "entry_stage_counts": {key: stages[key] for key in ENTRY_STAGE_KEYS},
        "reason_code_counts": dict(sorted(reasons.items())),
        "status": status,
    }


def build_private_result(
    aggregate: dict[str, Any],
    *,
    input_count: int,
    search_runs: int,
    wi0011_runs: int,
    execution_complete: bool,
    source_unchanged: bool,
    cleanup_complete: bool,
) -> dict[str, Any]:
    if (
        not execution_complete
        or not source_unchanged
        or not cleanup_complete
        or input_count != 3
        or wi0011_runs != 3
        or search_runs != 4
    ):
        raise ExperimentError("private diagnostic completion differs")
    result = {
        "artifact": "EXP-0013",
        "assessment_counts": aggregate["assessment_counts"],
        "cleanup_complete": True,
        "entry_stage_counts": aggregate["entry_stage_counts"],
        "input_count": 3,
        "path_free": True,
        "reason_code_counts": aggregate["reason_code_counts"],
        "schema": RESULT_SCHEMA,
        "search_runs": search_runs,
        "source_unchanged": True,
        "status": aggregate["status"],
        "wi0011_runs": 3,
    }
    return validate_private_result_dict(result)


def validate_private_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict) or set(result) != RESULT_FIELDS:
        raise ExperimentError("EXP-0013 result fields differ")
    if result.get("schema") != RESULT_SCHEMA or result.get("artifact") != "EXP-0013":
        raise ExperimentError("EXP-0013 result identity differs")
    if result.get("input_count") != 3 or result.get("wi0011_runs") != 3:
        raise ExperimentError("EXP-0013 result run count differs")
    search_runs = result.get("search_runs")
    if search_runs != 4:
        raise ExperimentError("EXP-0013 search count differs")
    if result.get("source_unchanged") is not True or result.get("cleanup_complete") is not True:
        raise ExperimentError("EXP-0013 result safety differs")
    if result.get("path_free") is not True:
        raise ExperimentError("EXP-0013 path-free proof differs")
    assessments = result.get("assessment_counts")
    stages = result.get("entry_stage_counts")
    reasons = result.get("reason_code_counts")
    if not isinstance(assessments, dict) or tuple(assessments) != ASSESSMENT_KEYS:
        raise ExperimentError("EXP-0013 assessment counts differ")
    if not isinstance(stages, dict) or tuple(stages) != ENTRY_STAGE_KEYS:
        raise ExperimentError("EXP-0013 stage counts differ")
    if not isinstance(reasons, dict) or list(reasons) != sorted(reasons):
        raise ExperimentError("EXP-0013 reason counts differ")
    all_counts = [*assessments.values(), *stages.values(), *reasons.values()]
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in all_counts):
        raise ExperimentError("EXP-0013 aggregate count differs")
    if any(value < 1 for value in reasons.values()):
        raise ExperimentError("EXP-0013 reason count differs")
    if sum(assessments.values()) != 3 or sum(stages.values()) != 3:
        raise ExperimentError("EXP-0013 aggregate totals differ")
    if assessments["completed"] != stages["completed"]:
        raise ExperimentError("EXP-0013 completed stage differs")
    if sum(reasons.values()) != assessments["not_assessed"]:
        raise ExperimentError("EXP-0013 reason total differs")
    expected_stages: Counter[str] = Counter()
    for code, count in reasons.items():
        safe = _safe_reason_code(code)
        stage = classify_entry_stage(
            {"assessment": "not_assessed", "handoff_reason_codes": [safe]}
        )
        expected_stages[stage] += count
    expected_stages["completed"] = assessments["completed"]
    if stages != {key: expected_stages[key] for key in ENTRY_STAGE_KEYS}:
        raise ExperimentError("EXP-0013 stage derivation differs")
    expected_status = (
        "inconclusive"
        if stages["unclassified"]
        else "pass"
        if assessments["completed"] == 3
        else "not_qualified"
    )
    if result.get("status") != expected_status:
        raise ExperimentError("EXP-0013 result status differs")
    encoded = canonical_json(result).encode("utf-8")
    if len(encoded) > 8192 or PRIVATE_PATH_PATTERN.search(encoded.decode("utf-8")):
        raise ExperimentError("EXP-0013 result contains private data")
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
    if len(values) != 3:
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
        if not 0 < value.st_size <= 4 * 1024 * 1024:
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
    if total > 12 * 1024 * 1024:
        raise ExperimentError("private input total size differs")
    return tuple(validated)


def _ensure_temp_root(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve(strict=True)
    allowed = ALLOWED_TEMP_ROOT.resolve(strict=True)
    if resolved != allowed:
        raise ExperimentError("EXP-0013 temp root differs")
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
    for item in sorted(resolved.rglob("*"), key=lambda value: len(value.parts), reverse=True):
        if item.is_symlink():
            continue
        if item.is_file():
            item.chmod(stat.S_IREAD | stat.S_IWRITE)
        elif item.is_dir():
            item.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    resolved.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    shutil.rmtree(resolved)
    return not resolved.exists()


def tree_digest(path: Path) -> str:
    entries = []
    for item in sorted(path.rglob("*"), key=lambda value: value.as_posix()):
        if item.is_symlink():
            raise ExperimentError("task library contains a link")
        if item.is_file():
            entries.append((item.relative_to(path).as_posix(), item.stat().st_size, sha256_file(item)))
    return sha256_bytes(canonical_json(entries).encode("utf-8"))


def _expect_failure(action: Callable[[], Any]) -> None:
    try:
        action()
    except ExperimentError:
        return
    raise ExperimentError("synthetic negative control did not fail closed")


def run_negative_controls(control_root: Path) -> int:
    control_root.mkdir()
    inputs = []
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
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[0], inputs[1]]))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], directory]))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], link]))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], oversized]))
    complete = aggregate_diagnostics(
        [{"assessment": "completed", "handoff_reason_codes": []} for _ in range(3)]
    )
    _expect_failure(
        lambda: build_private_result(
            complete,
            input_count=3,
            search_runs=4,
            wi0011_runs=3,
            execution_complete=False,
            source_unchanged=True,
            cleanup_complete=True,
        )
    )
    valid = build_private_result(
        complete,
        input_count=3,
        search_runs=4,
        wi0011_runs=3,
        execution_complete=True,
        source_unchanged=True,
        cleanup_complete=True,
    )
    private_field = dict(valid)
    private_field["title"] = "private"
    _expect_failure(lambda: validate_private_result_dict(private_field))
    _expect_failure(
        lambda: build_private_result(
            complete,
            input_count=3,
            search_runs=4,
            wi0011_runs=3,
            execution_complete=True,
            source_unchanged=True,
            cleanup_complete=False,
        )
    )
    return len(NEGATIVE_CONTROLS)


def run_synthetic_controls(
    temp_root: Path,
    profile: dict[str, Any],
    records: list[dict[str, Any]],
    runtime: CalibreRuntimeProfile,
) -> dict[str, Any]:
    if not _image_matches(runtime):
        raise ExperimentError("bound Calibre image is unavailable or changed")
    temp_root = _ensure_temp_root(temp_root)
    containers_before = _container_names()
    fixture_before = {locator: sha256_file(ROOT / locator) for locator in CONTROL_FIXTURE_LOCATORS}
    task_root = _create_task_root(temp_root, "synthetic-")
    library = task_root / "library"
    identity_temp = task_root / "identity"
    controls = task_root / "negative-controls"
    task_removed = False
    identity_empty = False
    source_unchanged = False
    actual_reports: list[dict[str, Any]] = []
    repetitions_identical = False
    negative_count = 0
    failure: BaseException | None = None
    cleanup_failure: BaseException | None = None
    try:
        projection = materialize_control_library(library, runtime, records)
        library_before = tree_digest(library)
        for index, record in enumerate(records):
            actual_reports.append(
                run_identity_diagnostic(
                    ROOT / record["fixture"],
                    library,
                    projection[index]["external_record_id"],
                    identity_temp,
                )
            )
        actual = aggregate_diagnostics(actual_reports)
        if actual != {
            "assessment_counts": {"completed": 3, "not_assessed": 0},
            "entry_stage_counts": {
                "completed": 3,
                "identity_analysis": 0,
                "ingress_preflight": 0,
                "record_handoff": 0,
                "unclassified": 0,
            },
            "reason_code_counts": {},
            "status": "pass",
        }:
            raise ExperimentError("synthetic WI-0011 controls did not complete")
        matrix = profile["synthetic_controls"]["aggregation_matrix"]
        first = aggregate_diagnostics(matrix["reports"])
        second = aggregate_diagnostics(json.loads(canonical_json(matrix["reports"])))
        repetitions_identical = canonical_json(first) == canonical_json(second)
        if first != matrix["expected"] or not repetitions_identical:
            raise ExperimentError("synthetic aggregation control differs")
        negative_count = run_negative_controls(controls)
        if tree_digest(library) != library_before:
            raise ExperimentError("synthetic library changed")
        identity_empty = not identity_temp.exists() or not any(identity_temp.iterdir())
        source_unchanged = fixture_before == {
            locator: sha256_file(ROOT / locator) for locator in CONTROL_FIXTURE_LOCATORS
        }
    except BaseException as exc:
        failure = exc
    try:
        identity_empty = not identity_temp.exists() or not any(identity_temp.iterdir())
    except OSError:
        identity_empty = False
    try:
        source_unchanged = fixture_before == {
            locator: sha256_file(ROOT / locator) for locator in CONTROL_FIXTURE_LOCATORS
        }
    except OSError:
        source_unchanged = False
    try:
        task_removed = _remove_owned_task(task_root, temp_root, "synthetic-")
    except BaseException as exc:
        cleanup_failure = exc
    containers_after = _container_names()
    cleanup_complete = task_removed and identity_empty and containers_before == containers_after
    if cleanup_failure is not None or not cleanup_complete or not source_unchanged:
        raise ExperimentError("synthetic control cleanup or source proof differs") from (
            cleanup_failure or failure
        )
    if failure is not None:
        raise failure
    summary = {
        "artifact": "EXP-0013",
        "cleanup_complete": True,
        "negative_controls": negative_count,
        "path_free": True,
        "repetitions_identical": repetitions_identical,
        "schema": SYNTHETIC_SCHEMA,
        "source_unchanged": True,
        "status": "pass",
        "wi0011_completed": len(actual_reports),
    }
    if PRIVATE_PATH_PATTERN.search(canonical_json(summary)):
        raise ExperimentError("synthetic control summary contains a path")
    return summary


def _write_result_once(path: Path, result: dict[str, Any]) -> None:
    if path.exists():
        raise ExperimentError("EXP-0013 result already exists")
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
    profile, records = validate_contract()
    require_committed_preimage()
    if not confirmed_same_inputs:
        raise ExperimentError("same EXP-0012 input set is not confirmed")
    validated = validate_private_inputs(values)
    if result_path.exists():
        raise ExperimentError("EXP-0013 result already exists")
    runtime = CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
    if not _image_matches(runtime):
        raise ExperimentError("bound Calibre image is unavailable or changed")
    temp_root = _ensure_temp_root(temp_root)
    run_synthetic_controls(temp_root, profile, records, runtime)

    containers_before = _container_names()
    task_root = _create_task_root(temp_root, "private-")
    inputs_root = task_root / "inputs"
    library = task_root / "library"
    identity_temp = task_root / "identity"
    inputs_root.mkdir()
    reports: list[dict[str, Any]] = []
    search_runs = 0
    execution_complete = False
    source_unchanged = False
    identity_empty = False
    task_removed = False
    failure: BaseException | None = None
    cleanup_failure: BaseException | None = None
    try:
        copied: list[Path] = []
        for index, source in enumerate(validated, start=1):
            target = inputs_root / f"input-{index}.epub"
            shutil.copyfile(source.path, target)
            if sha256_file(target) != source.sha256:
                raise ExperimentError("private copy differs")
            target.chmod(stat.S_IREAD)
            copied.append(target)
        projection = materialize_private_library(library, runtime, copied)
        for index, record in enumerate(projection):
            search_runs += run_self_searches(library, runtime, record)
            reports.append(
                run_identity_diagnostic(
                    copied[index],
                    library,
                    record["external_record_id"],
                    identity_temp,
                )
            )
        execution_complete = len(reports) == 3
        identity_empty = not identity_temp.exists() or not any(identity_temp.iterdir())
        source_unchanged = all(
            sha256_file(source.path) == source.sha256 for source in validated
        )
    except BaseException as exc:
        failure = exc
    if not source_unchanged:
        try:
            source_unchanged = all(
                sha256_file(source.path) == source.sha256 for source in validated
            )
        except OSError:
            source_unchanged = False
    try:
        identity_empty = not identity_temp.exists() or not any(identity_temp.iterdir())
    except OSError:
        identity_empty = False
    try:
        task_removed = _remove_owned_task(task_root, temp_root, "private-")
    except BaseException as exc:
        cleanup_failure = exc
    containers_after = _container_names()
    cleanup_complete = task_removed and identity_empty and containers_before == containers_after
    if cleanup_failure is not None or not cleanup_complete or not source_unchanged:
        raise ExperimentError("private diagnostic cleanup or source proof differs") from (
            cleanup_failure or failure
        )
    if failure is not None:
        raise failure
    aggregate = aggregate_diagnostics(reports)
    result = build_private_result(
        aggregate,
        input_count=len(validated),
        search_runs=search_runs,
        wi0011_runs=len(reports),
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
    value.add_argument("--confirm-same-exp-0012-inputs", action="store_true")
    return value


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        modes = sum((args.validate_profile, args.validate_result, args.synthetic_controls, bool(args.private_epub)))
        if modes != 1:
            raise ExperimentError("exactly one EXP-0013 execution mode is required")
        if args.validate_profile:
            validate_contract()
            print("EXP-0013 profile valid")
            return 0
        if args.validate_result:
            result = validate_result()
            print(f"EXP-0013 result valid: {result['status']}")
            return 0
        profile, records = validate_contract()
        require_committed_preimage()
        runtime = CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
        if args.synthetic_controls:
            summary = run_synthetic_controls(ALLOWED_TEMP_ROOT, profile, records, runtime)
            print(canonical_json(summary))
            return 0
        result = execute_private_diagnostic(
            args.private_epub,
            confirmed_same_inputs=args.confirm_same_exp_0012_inputs,
        )
        print(canonical_json(result))
        return 2 if result["status"] == "inconclusive" else 0
    except KeyboardInterrupt:
        return 130
    except ExperimentError as exc:
        print(f"EXP-0013 failed closed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"EXP-0013 failed closed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
