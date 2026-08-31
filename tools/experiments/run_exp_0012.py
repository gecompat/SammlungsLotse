#!/usr/bin/env python3
"""Run or validate the bounded, product-code-free EXP-0012 experiment."""

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
import uuid
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
for import_root in (ROOT / "src", ROOT / "tools"):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import materialize_calibre_qualification_library as materializer  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.ebook_intake.podman_executor import run_bounded  # noqa: E402


EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0012"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
MANIFEST_PATH = EXPERIMENT / "case-manifest.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNTIME_PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
IDENTITY_PROFILE_PATH = ROOT / "runtime" / "ebook-calibre-identity" / "profile.json"
IDENTITY_CLI_PATH = ROOT / "tools" / "run_ebook_calibre_identity.py"
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")
CONTAINER_PREFIX = "sammlungslotse-exp0012-"
VARIANTS = ("V1", "V2", "V3")
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:(?<![A-Za-z0-9_])[A-Za-z]:[\\/]|/(?:home|Users|tmp|library|input|private)(?:[\\/]|$))",
    re.IGNORECASE,
)
SEARCH_OUTPUT = re.compile(rb"\s*(?:[1-9][0-9]*(?:,[1-9][0-9]*)*)?\s*")
FIXTURE_LOCATORS = (
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-byte-equal/source-a/same.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-title-collision/work-b.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-repackaged/package-a.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-title-collision/work-a.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/edition-sample-vs-full/sample.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/edition-sample-vs-full/full.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-repackaged/package-b.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/metadata-multilingual-rtl/multilingual-rtl.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-edition-vs-translation/source-en.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-edition-vs-translation/translation-de.epub",
)
PREIMAGE_FILES = (
    "docs/planning/EBOOK_CALIBRE_CANDIDATE_SEARCH_EXPERIMENT.md",
    "experiments/ebook/exp-0012/README.md",
    "experiments/ebook/exp-0012/execution-profile.json",
    "experiments/ebook/exp-0012/case-manifest.json",
    "tests/experiments/test_exp_0012.py",
    "tools/experiments/run_exp_0012.py",
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
    *FIXTURE_LOCATORS,
)


class ExperimentError(RuntimeError):
    """Raised when an EXP-0012 boundary cannot be proven."""


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
            raise ExperimentError("EXP-0012 preimage is not fully committed")
    return commit


def _safe_relative_locator(value: str) -> Path:
    locator = Path(value)
    if locator.is_absolute() or ".." in locator.parts or "\\" in value:
        raise ExperimentError("manifest locator differs")
    return locator


def validate_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    profile = load_json(PROFILE_PATH)
    manifest = load_json(MANIFEST_PATH)
    if profile.get("schema") != "sammlungslotse/exp-0012-execution-profile/v1":
        raise ExperimentError("EXP-0012 profile schema differs")
    if profile.get("artifact") != "EXP-0012" or profile.get("strategies") != list(VARIANTS):
        raise ExperimentError("EXP-0012 profile identity differs")
    limits = profile.get("limits", {})
    if limits != {
        "candidate_limit": 5,
        "library_records": 12,
        "private_epub_limit": 3,
        "query_bytes": 512,
        "repetitions": 2,
        "stderr_bytes": 131072,
        "stdout_bytes": 131072,
        "step_timeout_seconds": 30,
        "synthetic_tasks": 8,
    }:
        raise ExperimentError("EXP-0012 limits differ")
    implementation = profile.get("implementation", {})
    if any(implementation.get(key) is not False for key in (
        "direct_database_access", "multiple_libraries", "network_access",
        "product_code_changes", "ranking_claim", "versioned_private_media",
        "writer_effects",
    )):
        raise ExperimentError("EXP-0012 effects boundary differs")
    bindings = profile.get("runtime_bindings", {})
    expected_bindings = (
        ("calibre", RUNTIME_PROFILE_PATH, "wi-0007-calibre-9.13.0-podman-linux-amd64/v1"),
        ("identity", IDENTITY_PROFILE_PATH, "wi-0011-calibre-identity-handoff/v1"),
        (
            "test_0001",
            ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "manifest.json",
            None,
        ),
    )
    for name, path, profile_id in expected_bindings:
        binding = bindings.get(name, {})
        if binding.get("sha256") != sha256_file(path):
            raise ExperimentError(f"EXP-0012 {name} binding differs")
        if profile_id is not None and binding.get("profile_id") != profile_id:
            raise ExperimentError(f"EXP-0012 {name} profile differs")
    if manifest.get("schema") != "sammlungslotse/exp-0012-case-manifest/v1":
        raise ExperimentError("EXP-0012 manifest schema differs")
    if manifest.get("synthetic_only") is not True:
        raise ExperimentError("EXP-0012 manifest is not synthetic-only")
    records = manifest.get("records")
    tasks = manifest.get("tasks")
    if not isinstance(records, list) or len(records) != 12:
        raise ExperimentError("EXP-0012 record count differs")
    if not isinstance(tasks, list) or len(tasks) != 8:
        raise ExperimentError("EXP-0012 task count differs")
    if [item.get("expected_id") for item in records] != list(range(1, 13)):
        raise ExperimentError("EXP-0012 record IDs differ")
    for record in records:
        if set(record) != {
            "authors", "expected_id", "fixture", "identifiers", "languages", "sha256", "title"
        }:
            raise ExperimentError("EXP-0012 record fields differ")
        fixture = ROOT / _safe_relative_locator(record["fixture"])
        if not fixture.is_file() or sha256_file(fixture) != record["sha256"]:
            raise ExperimentError("EXP-0012 record fixture differs")
        if not record["title"] or not record["authors"]:
            raise ExperimentError("EXP-0012 record metadata differs")
        if any(not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", key) for key in record["identifiers"]):
            raise ExperimentError("EXP-0012 identifier type differs")
    cases = [task.get("case") for task in tasks]
    if len(set(cases)) != 8:
        raise ExperimentError("EXP-0012 task keys differ")
    for task in tasks:
        if set(task) != {
            "author", "case", "identifier", "input_fixture", "input_sha256", "oracle", "title"
        }:
            raise ExperimentError("EXP-0012 task fields differ")
        fixture = ROOT / _safe_relative_locator(task["input_fixture"])
        if not fixture.is_file() or sha256_file(fixture) != task["input_sha256"]:
            raise ExperimentError("EXP-0012 task fixture differs")
        if set(task["oracle"]) != set(VARIANTS):
            raise ExperimentError("EXP-0012 task oracle variants differ")
        for oracle in task["oracle"].values():
            if set(oracle) != {"allowed_extra_ids", "relevant_ids"}:
                raise ExperimentError("EXP-0012 task oracle fields differ")
            values = oracle["allowed_extra_ids"] + oracle["relevant_ids"]
            if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > 12 for value in values):
                raise ExperimentError("EXP-0012 task oracle IDs differ")
    return profile, manifest


def _container_names() -> list[str]:
    completed = run_bounded(
        ["podman", "ps", "-a", "--format", "{{.Names}}"],
        timeout=15,
        stdout_limit=131072,
        stderr_limit=131072,
    )
    if completed.returncode != 0 or completed.timed_out:
        raise ExperimentError("Podman container inventory failed")
    return sorted(
        line for line in completed.stdout.decode("utf-8").splitlines()
        if line.startswith(CONTAINER_PREFIX)
    )


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
            == (
                b"No books matching the search expression: "
                + arguments[-1].encode("utf-8")
                + b"\n"
            )
        )
        if (
            (execution.returncode != 0 and not empty_search)
            or execution.timed_out
            or execution.stdout_truncated
            or execution.stderr_truncated
        ):
            reason = (
                "timeout"
                if execution.timed_out
                else "output_limit"
                if execution.stdout_truncated or execution.stderr_truncated
                else f"exit_{execution.returncode}"
            )
            raise ExperimentError(f"Calibre {arguments[0]} command failed closed ({reason})")
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


def _authors_argument(authors: list[str]) -> str:
    if not authors or any("&" in author for author in authors):
        raise ExperimentError("Calibre author separator is ambiguous")
    return " & ".join(authors)


def materialize_synthetic_library(
    library: Path,
    runtime: CalibreRuntimeProfile,
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    library.mkdir()
    for record in manifest["records"]:
        fixture = ROOT / record["fixture"]
        arguments = [
            "add", "--with-library", "/library", "--duplicates",
            "--title", record["title"], "--authors", _authors_argument(record["authors"]),
            "--languages", ",".join(record["languages"]),
            "--empty",
        ]
        for key, value in sorted(record["identifiers"].items()):
            arguments.extend(("--identifier", f"{key}:{value}"))
        run_calibre(library, runtime, arguments)
        run_calibre(
            library,
            runtime,
            [
                "add_format",
                "--with-library",
                "/library",
                str(record["expected_id"]),
                "/input/book.epub",
            ],
            fixture,
        )
    projection = project_records(library, runtime, None)
    if [item["external_record_id"] for item in projection] != list(range(1, 13)):
        raise ExperimentError("materialized Calibre IDs differ")
    expected = {
        record["expected_id"]: {
            "authors": record["authors"],
            "identifiers": record["identifiers"],
            "languages": record["languages"],
            "title": record["title"],
        }
        for record in manifest["records"]
    }
    for item in projection:
        compared = {key: item[key] for key in ("authors", "identifiers", "languages", "title")}
        if compared != expected[item["external_record_id"]] or item["formats"] != ["epub"]:
            raise ExperimentError("materialized Calibre projection differs")
    return projection


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
    external_record_id: int | None,
) -> list[dict[str, Any]]:
    arguments = [
        "list", "--with-library", "/library", "--for-machine",
        "--fields", "title,authors,languages,formats,identifiers",
        "--sort-by", "id", "--ascending",
    ]
    if external_record_id is not None:
        arguments.extend(("--search", f"id:={external_record_id}", "--limit", "1"))
    raw = run_calibre(library, runtime, arguments)
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, list):
        raise ExperimentError("Calibre projection root differs")
    result = []
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
        if not isinstance(authors, list) or not isinstance(languages, list) or not isinstance(identifiers, dict):
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


def _quoted(value: str) -> str:
    if not value or any(character in value for character in ('"', "\r", "\n")):
        raise ExperimentError("search literal differs")
    return value


def query_for(task: dict[str, Any], variant: str) -> str | None:
    if variant == "V1":
        identifier = task["identifier"]
        if identifier is None:
            return None
        query = f"identifiers:={identifier['type']}:={identifier['value']}"
    elif variant == "V2":
        query = f'title:"={_quoted(task["title"])}" and author:"={_quoted(task["author"])}"'
    elif variant == "V3":
        query = f'title:"{_quoted(task["title"])}" and author:"{_quoted(task["author"])}"'
    else:
        raise ExperimentError("unknown search variant")
    if len(query.encode("utf-8")) > 512:
        raise ExperimentError("search query exceeds bound")
    return query


def search_ids(
    library: Path,
    runtime: CalibreRuntimeProfile,
    query: str,
) -> list[int]:
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


def run_identity(
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
    if completed.returncode not in (0, 4) or completed.timed_out or completed.stdout_truncated or completed.stderr_truncated:
        raise ExperimentError("WI-0011 candidate comparison failed closed")
    report = json.loads(completed.stdout.decode("utf-8"))
    if PRIVATE_PATH_PATTERN.search(canonical_json(report)):
        raise ExperimentError("WI-0011 candidate report contains a path")
    identity = report.get("identity")
    stages = [] if identity is None else [
        {"decision": item["decision"], "rule_id": item["rule_id"], "stage": item["stage"]}
        for item in identity["stages"]
    ]
    return {
        "assessment": report["assessment"],
        "effects": report["effects"],
        "overall": None if identity is None else identity["overall"],
        "stages": stages,
    }


def tree_digest(path: Path) -> str:
    entries = []
    for item in sorted(path.rglob("*"), key=lambda value: value.as_posix()):
        if item.is_symlink():
            raise ExperimentError("library contains a link")
        if item.is_file():
            entries.append((item.relative_to(path).as_posix(), item.stat().st_size, sha256_file(item)))
    return sha256_bytes(canonical_json(entries).encode("utf-8"))


def execute_observations(
    library: Path,
    runtime: CalibreRuntimeProfile,
    manifest: dict[str, Any],
    identity_temp_root: Path,
) -> list[dict[str, Any]]:
    observations = []
    for task in manifest["tasks"]:
        for variant in VARIANTS:
            query = query_for(task, variant)
            oracle = task["oracle"][variant]
            if query is None:
                observations.append(
                    {
                        "case": task["case"],
                        "identity_evidence": [],
                        "oracle": oracle,
                        "search_evidence": None,
                        "status": "not_applicable",
                        "variant": variant,
                    }
                )
                continue
            try:
                ids = search_ids(library, runtime, query)
                candidate_evidence = []
                for external_record_id in ids:
                    projection = project_records(library, runtime, external_record_id)[0]
                    identity = run_identity(
                        ROOT / task["input_fixture"],
                        library,
                        external_record_id,
                        identity_temp_root,
                    )
                    candidate_evidence.append(
                        {
                            "external_record_id": external_record_id,
                            "identity": identity,
                            "projection": projection,
                        }
                    )
            except ExperimentError as exc:
                raise ExperimentError(f"{task['case']} {variant}: {exc}") from exc
            relevant = set(oracle["relevant_ids"])
            found = relevant.intersection(ids)
            observations.append(
                {
                    "case": task["case"],
                    "identity_evidence": candidate_evidence,
                    "oracle": oracle,
                    "search_evidence": {
                        "candidate_count": len(ids),
                        "candidate_ids": ids,
                        "candidate_limit_reached": len(ids) == 5,
                        "missed_relevant_ids": sorted(relevant.difference(ids)),
                        "query": query,
                        "relevant_found_ids": sorted(found),
                        "unexpected_ids": sorted(set(ids).difference(relevant, oracle["allowed_extra_ids"])),
                    },
                    "status": "executed",
                    "variant": variant,
                }
            )
    return observations


def critical_false_same(observation: dict[str, Any]) -> int:
    relevant = set(observation["oracle"]["relevant_ids"])
    result = 0
    for candidate in observation["identity_evidence"]:
        if candidate["external_record_id"] in relevant:
            continue
        stages = candidate["identity"]["stages"]
        if any(
            item["stage"] in {"edition", "work"} and item["decision"] == "candidate_same"
            for item in stages
        ):
            result += 1
    return result


def derive_metrics(observations: list[dict[str, Any]]) -> dict[str, Any]:
    variants: dict[str, Any] = {}
    for variant in VARIANTS:
        executed = [
            item for item in observations
            if item["variant"] == variant and item["status"] == "executed"
        ]
        applicable_relevant = sum(len(item["oracle"]["relevant_ids"]) for item in executed)
        relevant_found = sum(len(item["search_evidence"]["relevant_found_ids"]) for item in executed)
        candidates = sum(item["search_evidence"]["candidate_count"] for item in executed)
        extra = candidates - relevant_found
        misses = applicable_relevant - relevant_found
        unexpected = sum(len(item["search_evidence"]["unexpected_ids"]) for item in executed)
        false_same = sum(critical_false_same(item) for item in executed)
        if unexpected or false_same:
            classification = "inconclusive"
        elif misses:
            classification = "not_qualified"
        else:
            classification = "eligible_with_tradeoffs"
        variants[variant] = {
            "applicable_runs": len(executed),
            "candidate_limit_reached_runs": sum(
                item["search_evidence"]["candidate_limit_reached"] for item in executed
            ),
            "candidates": candidates,
            "classification": classification,
            "critical_false_same": false_same,
            "extra_candidates": extra,
            "missed_relevant": misses,
            "not_applicable_runs": 8 - len(executed),
            "precision": 1.0 if candidates == 0 else relevant_found / candidates,
            "recall": 1.0 if applicable_relevant == 0 else relevant_found / applicable_relevant,
            "unexpected_candidates": unexpected,
        }
    return {"variants": variants}


def result_has_no_private_paths(result: dict[str, Any]) -> bool:
    return PRIVATE_PATH_PATTERN.search(canonical_json(result)) is None


def derive_acceptance(result: dict[str, Any]) -> dict[str, bool]:
    runs = result.get("runs", [])
    first = runs[0]["observations"] if len(runs) == 2 else []
    observations = [item for run in runs for item in run.get("observations", [])]
    executed = [item for item in observations if item.get("status") == "executed"]
    identity = [candidate for item in executed for candidate in item.get("identity_evidence", [])]
    effects = result.get("effects", {})
    cleanup = result.get("cleanup", {})
    return {
        "exact_profile_image_and_preimage": (
            result.get("profile_id") == "exp-0012-calibre-candidate-search/v1"
            and result.get("image_id") == "sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5"
            and isinstance(result.get("preimage"), dict)
            and set(result.get("preimage", {})) == set(PREIMAGE_FILES)
        ),
        "matrix_three_variants_eight_tasks_two_runs": (
            len(runs) == 2
            and all(len(run.get("observations", [])) == 24 for run in runs)
            and {item.get("variant") for item in first} == set(VARIANTS)
        ),
        "synthetic_fixtures_prebound_and_unchanged": (
            result.get("synthetic_only") is True
            and result.get("fixtures", {}).get("before") == result.get("fixtures", {}).get("after")
            and len(result.get("fixtures", {}).get("before", {})) == len(FIXTURE_LOCATORS)
        ),
        "supported_search_and_list_only": effects.get("supported_calibredb_only") is True,
        "candidate_limit_enforced": all(
            item["search_evidence"]["candidate_count"] <= 5 for item in executed
        ),
        "failures_and_limit_visible": all(
            "candidate_limit_reached" in item["search_evidence"]
            and "unexpected_ids" in item["search_evidence"]
            for item in executed
        ),
        "minimal_projection_path_free": all(
            set(candidate["projection"]) == {
                "authors", "external_record_id", "formats", "identifiers", "languages", "title"
            }
            for candidate in identity
        ),
        "every_candidate_uses_wi0011": bool(identity) and all(
            candidate["identity"]["assessment"] == "completed" for candidate in identity
        ),
        "recall_precision_and_misses_reported": set(
            next(iter(result.get("metrics", {}).get("variants", {}).values()), {})
        ).issuperset({"recall", "precision", "missed_relevant", "extra_candidates"}),
        "search_and_identity_evidence_separate": all(
            isinstance(item.get("search_evidence"), dict)
            and isinstance(item.get("identity_evidence"), list)
            for item in executed
        ),
        "critical_false_same_counted": all(
            "critical_false_same" in value
            for value in result.get("metrics", {}).get("variants", {}).values()
        ),
        "repetitions_semantically_identical": (
            len(runs) == 2
            and canonical_json(runs[0].get("observations")) == canonical_json(runs[1].get("observations"))
        ),
        "source_and_library_unchanged": (
            result.get("library", {}).get("before") == result.get("library", {}).get("after")
        ),
        "network_database_persistence_product_and_writer_false": all(
            effects.get(key) is False
            for key in (
                "direct_database_access", "network", "persistence", "product_code", "writer"
            )
        ),
        "checked_in_result_path_free": result_has_no_private_paths(result),
        "task_and_container_cleanup_complete": (
            cleanup.get("containers_before") == []
            and cleanup.get("containers_after") == []
            and cleanup.get("task_root_removed") is True
            and cleanup.get("identity_temp_empty") is True
        ),
    }


def execute_experiment(temp_root: Path, result_path: Path) -> dict[str, Any]:
    profile, manifest = validate_contract()
    preimage_commit = require_committed_preimage()
    runtime = CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
    if not _image_matches(runtime):
        raise ExperimentError("bound Calibre image is unavailable or changed")
    temp_root = temp_root.resolve(strict=True)
    allowed = ALLOWED_TEMP_ROOT.resolve(strict=True)
    if temp_root != allowed / "exp-0012":
        raise ExperimentError("EXP-0012 temp root differs")
    temp_root.mkdir(exist_ok=True)
    task_root = temp_root / f"synthetic-{uuid.uuid4().hex}"
    task_root.mkdir()
    library = task_root / "library"
    identity_temp = task_root / "identity"
    containers_before = _container_names()
    fixtures_before = {locator: sha256_file(ROOT / locator) for locator in FIXTURE_LOCATORS}
    task_removed = False
    identity_empty = False
    try:
        materialize_synthetic_library(library, runtime, manifest)
        library_before = tree_digest(library)
        runs = []
        for repetition in (1, 2):
            observations = execute_observations(library, runtime, manifest, identity_temp)
            runs.append({"observations": observations, "repetition": repetition})
        library_after = tree_digest(library)
        identity_empty = identity_temp.is_dir() and not any(identity_temp.iterdir())
    finally:
        shutil.rmtree(task_root, ignore_errors=True)
        task_removed = not task_root.exists()
    containers_after = _container_names()
    fixtures_after = {locator: sha256_file(ROOT / locator) for locator in FIXTURE_LOCATORS}
    result = {
        "artifact": "EXP-0012",
        "cleanup": {
            "containers_after": containers_after,
            "containers_before": containers_before,
            "identity_temp_empty": identity_empty,
            "task_root_removed": task_removed,
        },
        "effects": {
            "direct_database_access": False,
            "network": False,
            "persistence": False,
            "product_code": False,
            "supported_calibredb_only": True,
            "writer": False,
        },
        "executed_on": date.today().isoformat(),
        "fixtures": {"after": fixtures_after, "before": fixtures_before},
        "image_id": runtime.image["id"],
        "library": {"after": library_after, "before": library_before, "records": 12},
        "limitations": [
            "synthetic TEST-0001 evidence only",
            "one task-private Calibre library",
            "maximum five candidates",
            "no completeness or ranking claim",
            "private smoke is separate and not retained",
            "no product authorization",
        ],
        "metrics": derive_metrics(runs[0]["observations"]),
        "preimage": current_preimage(),
        "preimage_commit": preimage_commit,
        "privacy": {"path_free_result": True, "private_values_retained": False},
        "profile_id": profile["profile_id"],
        "runs": runs,
        "schema": "sammlungslotse/exp-0012-result/v1",
        "status": "inconclusive",
        "synthetic_only": True,
    }
    result["privacy"]["path_free_result"] = result_has_no_private_paths(result)
    result["acceptance"] = derive_acceptance(result)
    result["status"] = "pass" if all(result["acceptance"].values()) else "not_qualified"
    if not result_has_no_private_paths(result):
        result["privacy"]["path_free_result"] = False
        result["acceptance"] = derive_acceptance(result)
        result["status"] = "not_qualified"
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    result = load_json(path)
    if result.get("schema") != "sammlungslotse/exp-0012-result/v1" or result.get("artifact") != "EXP-0012":
        raise ExperimentError("EXP-0012 result identity differs")
    if result.get("preimage") != current_preimage():
        raise ExperimentError("EXP-0012 result preimage differs")
    acceptance = derive_acceptance(result)
    if result.get("acceptance") != acceptance:
        raise ExperimentError("EXP-0012 acceptance differs from evidence")
    if result.get("metrics") != derive_metrics(result["runs"][0]["observations"]):
        raise ExperimentError("EXP-0012 metrics differ from evidence")
    if result.get("status") != "pass" or not all(acceptance.values()):
        raise ExperimentError("EXP-0012 result is not a method pass")
    if not result_has_no_private_paths(result):
        raise ExperimentError("EXP-0012 result contains a path")
    return result


def _is_private_epub_candidate(path: Path) -> bool:
    try:
        value = path.stat(follow_symlinks=False)
    except OSError:
        return False
    attributes = getattr(value, "st_file_attributes", 0)
    return (
        stat.S_ISREG(value.st_mode)
        and not path.is_symlink()
        and not bool(attributes & 0x400)
        and path.suffix.lower() == ".epub"
        and 0 < value.st_size <= 4 * 1024 * 1024
    )


def select_private_epubs(source: Path, limit: int = 3) -> list[Path]:
    selected: list[Path] = []
    for current, directories, files in os.walk(source, followlinks=False):
        directories.sort(key=str.casefold)
        files.sort(key=str.casefold)
        base = Path(current)
        directories[:] = [name for name in directories if not (base / name).is_symlink()]
        for name in files:
            candidate = base / name
            if _is_private_epub_candidate(candidate):
                selected.append(candidate)
                if len(selected) == limit:
                    return selected
    return selected


def execute_private_smoke(source: Path, temp_root: Path) -> dict[str, Any]:
    profile, _ = validate_contract()
    runtime = CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
    if not profile["private_smoke"]["explicit_opt_in"] or not _image_matches(runtime):
        raise ExperimentError("private smoke boundary differs")
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ExperimentError("private source is unavailable")
    selected = select_private_epubs(source, profile["limits"]["private_epub_limit"])
    if not selected:
        raise ExperimentError("private source has no bounded EPUB candidate")
    source_before = [sha256_file(path) for path in selected]
    task_root = temp_root / f"private-{uuid.uuid4().hex}"
    task_root.mkdir()
    inputs = task_root / "inputs"
    library = task_root / "library"
    identity_temp = task_root / "identity"
    inputs.mkdir()
    library.mkdir()
    containers_before = _container_names()
    searches = 0
    identity_completed = 0
    cleanup = False
    source_unchanged = False
    try:
        copied = []
        for index, source_path in enumerate(selected, start=1):
            target = inputs / f"input-{index}.epub"
            shutil.copyfile(source_path, target)
            if sha256_file(target) != source_before[index - 1]:
                raise ExperimentError("private copy differs")
            copied.append(target)
            run_calibre(
                library,
                runtime,
                ["add", "--with-library", "/library", "--duplicates", "/input/book.epub"],
                target,
            )
        projection = project_records(library, runtime, None)
        if len(projection) != len(copied):
            raise ExperimentError("private materialization count differs")
        for index, item in enumerate(projection):
            if item["title"] and item["authors"]:
                task = {"title": item["title"], "author": item["authors"][0], "identifier": None}
                ids = search_ids(library, runtime, query_for(task, "V2") or "")
                searches += 1
                if item["external_record_id"] not in ids:
                    raise ExperimentError("private exact search missed its own record")
            if item["identifiers"]:
                key, value = sorted(item["identifiers"].items())[0]
                task = {"title": "unused", "author": "unused", "identifier": {"type": key, "value": value}}
                ids = search_ids(library, runtime, query_for(task, "V1") or "")
                searches += 1
                if item["external_record_id"] not in ids:
                    raise ExperimentError("private identifier search missed its own record")
            summary = run_identity(
                copied[index], library, item["external_record_id"], identity_temp
            )
            identity_completed += summary["assessment"] == "completed"
        source_unchanged = source_before == [sha256_file(path) for path in selected]
    finally:
        shutil.rmtree(task_root, ignore_errors=True)
        cleanup = not task_root.exists()
    containers_after = _container_names()
    result = {
        "anonymous_aggregate_only": True,
        "cleanup_complete": cleanup and containers_before == containers_after == [],
        "identity_completed": identity_completed,
        "private_values_retained": False,
        "schema": "sammlungslotse/exp-0012-private-smoke-summary/v1",
        "search_runs": searches,
        "selected_epubs": len(selected),
        "source_unchanged": source_unchanged,
    }
    result["status"] = "pass" if (
        result["cleanup_complete"]
        and result["identity_completed"] == result["selected_epubs"]
        and result["search_runs"] >= result["selected_epubs"]
        and result["source_unchanged"]
    ) else "not_qualified"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--temp-root", type=Path, default=ALLOWED_TEMP_ROOT / "exp-0012")
    parser.add_argument("--private-source", type=Path)
    args = parser.parse_args(argv)
    try:
        args.temp_root.mkdir(parents=True, exist_ok=True)
        if args.validate_profile:
            validate_contract()
            print("EXP-0012 profile valid")
            return 0
        if args.validate_result:
            result = validate_result(args.result)
            print(f"EXP-0012 result valid: {sum(result['acceptance'].values())}/{len(result['acceptance'])}")
            return 0
        result = execute_experiment(args.temp_root, args.result)
        print(f"EXP-0012 {result['status']}: {sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria")
        if args.private_source is not None:
            private = execute_private_smoke(args.private_source, args.temp_root)
            print(canonical_json(private))
            if private["status"] != "pass":
                return 1
        return 0 if result["status"] == "pass" else 1
    except KeyboardInterrupt:
        return 130
    except ExperimentError as exc:
        print(f"EXP-0012 failed closed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"EXP-0012 failed closed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
