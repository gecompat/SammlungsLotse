#!/usr/bin/env python3
"""Run or validate the bounded, product-code-free EXP-0015 experiment."""

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
import warnings
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0015"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
RESULT_PATH = EXPERIMENT / "result.json"
REGISTRY_PATH = ROOT / ".ai" / "artifact_registry.json"
TEST_0001_MANIFEST_PATH = (
    ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "manifest.json"
)
PREFLIGHT_PATH = ROOT / "src" / "sammlungslotse" / "ebook_intake" / "preflight.py"
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse\exp-0015")

RUNTIME_LOCATORS = (
    "src/sammlungslotse/ebook_intake/preflight.py",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
)
PREIMAGE_FILES = (
    ".ai/artifact_registry.json",
    "docs/planning/EBOOK_PRIVATE_REMOTE_REFERENCE_CONTEXT_EXPERIMENT.md",
    "experiments/ebook/exp-0015/README.md",
    "experiments/ebook/exp-0015/execution-profile.json",
    "tests/experiments/test_exp_0015.py",
    "tools/experiments/run_exp_0015.py",
    *RUNTIME_LOCATORS,
)

MARKUP_SUFFIXES = (".xhtml", ".html", ".htm", ".svg", ".opf", ".xml", ".css")
CONTEXT_CLASSES = (
    "content.embedded_resource",
    "content.navigation",
    "markup.other_attribute",
    "package.metadata_or_link",
    "stylesheet.resource",
    "svg.resource",
    "text_or_script.literal",
)
QUALIFICATIONS = (
    "shared_context_present",
    "no_shared_context",
    "inconclusive",
)
ATTRIBUTE_REMOTE = re.compile(
    rb"(?P<attribute>href|poster|src)\s*=\s*['\"]\s*https?://",
    re.IGNORECASE,
)
CSS_REMOTE = re.compile(rb"url\(\s*['\"]?\s*https?://", re.IGNORECASE)
TAG_NAME = re.compile(rb"/?\s*([A-Za-z][A-Za-z0-9_.:-]*)")
STYLESHEET_REL = re.compile(
    rb"\brel\s*=\s*(?:['\"][^'\"]*stylesheet[^'\"]*['\"]|stylesheet\b)",
    re.IGNORECASE,
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:(?<![A-Za-z0-9_])[A-Za-z]:[\\/]|/(?:home|Users|tmp|library|input|private)(?:[\\/]|$))",
    re.IGNORECASE,
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")

RESULT_SCHEMA = "sammlungslotse/exp-0015-private-reference-context-result/v1"
SYNTHETIC_SCHEMA = "sammlungslotse/exp-0015-synthetic-control-summary/v1"
RESULT_FIELDS = frozenset(
    {
        "artifact",
        "cleanup_complete",
        "context_input_counts",
        "input_count",
        "minimum_group_size",
        "parser_runs",
        "path_free",
        "qualification",
        "remote_reference_input_count",
        "schema",
        "source_unchanged",
        "status",
        "suppressed_context_present",
        "unclassified_input_count",
    }
)
PROJECTION_FIELDS = frozenset(
    {"contexts", "remote_reference_present", "unclassified"}
)
NEGATIVE_CONTROLS = (
    "two_inputs",
    "four_inputs",
    "duplicate_input",
    "directory_input",
    "link_input",
    "oversized_input",
    "invalid_archive",
    "path_traversal",
    "duplicate_entry",
    "encrypted_entry",
    "entry_limit",
    "expanded_limit",
    "markup_entry_limit",
    "markup_total_limit",
    "compression_ratio",
    "private_output_field",
    "partial_execution",
    "incomplete_cleanup",
    "source_change",
)


class ExperimentError(RuntimeError):
    """Raised when an EXP-0015 boundary cannot be proven."""


class SafeArgumentParser(argparse.ArgumentParser):
    """Avoid reflecting private argument values in parser failures."""

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
        committed = sha256_bytes(git_output("show", f"HEAD:{locator}"))
        if committed != sha256_file(ROOT / locator):
            raise ExperimentError("EXP-0015 preimage is not fully committed")
    return commit


def _expected_input_contract() -> dict[str, Any]:
    return {
        "confirmation_flag": "--confirm-same-exp-0014-inputs",
        "count": 3,
        "max_file_bytes": 4 * 1024 * 1024,
        "max_total_bytes": 12 * 1024 * 1024,
        "regular_files_only": True,
        "suffix": ".epub",
    }


def _expected_limits() -> dict[str, int]:
    return {
        "max_archive_entries": 512,
        "max_compression_ratio": 200,
        "max_expanded_bytes": 128 * 1024 * 1024,
        "max_markup_entry_bytes": 2 * 1024 * 1024,
        "max_markup_total_bytes": 16 * 1024 * 1024,
        "max_relative_name_bytes": 512,
        "minimum_group_size": 2,
        "output_bytes": 8192,
        "private_parser_runs": 3,
    }


def _expected_parser_contract() -> dict[str, Any]:
    return {
        "context_classes": list(CONTEXT_CLASSES),
        "implementation": "python-3.12-standard-library",
        "markup_suffixes": list(MARKUP_SUFFIXES),
        "parser_runs_per_private_input": 1,
        "product_imports": False,
        "remote_trigger_patterns": [
            "attribute:href|poster|src=http(s)",
            "stylesheet:url(http(s))",
        ],
        "zip_extraction": False,
    }


def _expected_privacy_contract() -> dict[str, Any]:
    return {
        "minimum_group_size": 2,
        "occurrence_counts_retained": False,
        "per_input_assignments_retained": False,
        "private_values_retained": False,
        "rare_context_literal_retained": False,
        "remote_values_retained": False,
        "zip_entry_names_retained": False,
    }


def validate_contract() -> dict[str, Any]:
    profile = load_json(PROFILE_PATH)
    if not isinstance(profile, dict) or set(profile) != {
        "artifact",
        "implementation",
        "input_contract",
        "limits",
        "output_contract",
        "parser",
        "privacy_contract",
        "profile_id",
        "runtime_bindings",
        "schema",
        "synthetic_controls",
    }:
        raise ExperimentError("EXP-0015 profile fields differ")
    if profile.get("schema") != "sammlungslotse/exp-0015-execution-profile/v1":
        raise ExperimentError("EXP-0015 profile schema differs")
    if profile.get("artifact") != "EXP-0015":
        raise ExperimentError("EXP-0015 artifact differs")
    if profile.get("profile_id") != "exp-0015-private-remote-context/v1":
        raise ExperimentError("EXP-0015 profile identity differs")
    if profile.get("input_contract") != _expected_input_contract():
        raise ExperimentError("EXP-0015 input contract differs")
    if profile.get("limits") != _expected_limits():
        raise ExperimentError("EXP-0015 limits differ")
    if profile.get("parser") != _expected_parser_contract():
        raise ExperimentError("EXP-0015 parser contract differs")
    if profile.get("privacy_contract") != _expected_privacy_contract():
        raise ExperimentError("EXP-0015 privacy contract differs")
    implementation = profile.get("implementation")
    if not isinstance(implementation, dict) or set(implementation) != {
        "analysis_subprocess_execution",
        "deep_tool_execution",
        "direct_database_access",
        "directory_discovery",
        "git_preimage_read_only_process",
        "network_access",
        "persistence",
        "product_code_changes",
        "writer_surface",
    }:
        raise ExperimentError("EXP-0015 implementation boundary differs")
    if implementation != {
        "analysis_subprocess_execution": False,
        "deep_tool_execution": False,
        "direct_database_access": False,
        "directory_discovery": False,
        "git_preimage_read_only_process": True,
        "network_access": False,
        "persistence": False,
        "product_code_changes": False,
        "writer_surface": False,
    }:
        raise ExperimentError("EXP-0015 implementation boundary differs")
    if profile.get("output_contract") != {
        "allowed_fields": sorted(RESULT_FIELDS),
        "qualifications": list(QUALIFICATIONS),
        "schema": RESULT_SCHEMA,
        "statuses": ["pass", "inconclusive"],
    }:
        raise ExperimentError("EXP-0015 output contract differs")
    bindings = profile.get("runtime_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {
        "files",
        "test_0001_version",
        "wi_0004_remote_pattern_bound",
    }:
        raise ExperimentError("EXP-0015 runtime bindings differ")
    files = bindings.get("files")
    if not isinstance(files, list) or len(files) != len(RUNTIME_LOCATORS):
        raise ExperimentError("EXP-0015 runtime file bindings differ")
    for binding, locator in zip(files, RUNTIME_LOCATORS, strict=True):
        if binding != {"locator": locator, "sha256": sha256_file(ROOT / locator)}:
            raise ExperimentError("EXP-0015 runtime file binding differs")
    manifest = load_json(TEST_0001_MANIFEST_PATH)
    if (
        bindings.get("test_0001_version") != "0.3.0"
        or manifest.get("corpus_ref") != "TEST-0001"
        or manifest.get("fixture_version") != "0.3.0"
        or bindings.get("wi_0004_remote_pattern_bound") is not True
    ):
        raise ExperimentError("EXP-0015 upstream binding differs")
    source = PREFLIGHT_PATH.read_bytes()
    if (
        b"href|poster|src" not in source
        or b"https?://" not in source
        or b"url\\(" not in source
    ):
        raise ExperimentError("EXP-0015 WI-0004 pattern differs")
    controls = profile.get("synthetic_controls")
    if controls != {
        "aggregation_repetitions": 2,
        "context_classes": list(CONTEXT_CLASSES),
        "negative_controls": list(NEGATIVE_CONTROLS),
        "private_media_used": False,
    }:
        raise ExperimentError("EXP-0015 synthetic controls differ")
    registry = load_json(REGISTRY_PATH).get("artifacts", {})
    if (
        registry.get("GATE-0017", {}).get("status") != "done"
        or registry.get("EXP-0014", {}).get("status") != "done"
        or registry.get("EXP-0015", {}).get("status") != "accepted"
    ):
        raise ExperimentError("EXP-0015 registry state differs")
    return profile


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


def _safe_entry_name(name: str, maximum_bytes: int) -> str:
    try:
        encoded = name.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ExperimentError("archive entry name differs") from exc
    if (
        not name
        or len(encoded) > maximum_bytes
        or "\x00" in name
        or "\\" in name
        or name.startswith("/")
        or re.match(r"^[A-Za-z]:", name)
    ):
        raise ExperimentError("archive entry name differs")
    parts = PurePosixPath(name).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ExperimentError("archive entry path differs")
    return name


def _entry_is_link(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return bool(mode and stat.S_ISLNK(mode))


def _inside_script(payload: bytes, position: int) -> bool:
    lowered = payload[:position].lower()
    return lowered.rfind(b"<script") > lowered.rfind(b"</script")


def _attribute_context(
    payload: bytes,
    match: re.Match[bytes],
    suffix: str,
) -> str | None:
    position = match.start()
    last_open = payload.rfind(b"<", 0, position)
    last_close = payload.rfind(b">", 0, position)
    if last_open <= last_close:
        return "text_or_script.literal"
    prefix = payload[last_open + 1 : position]
    if prefix.lstrip().startswith((b"!", b"?")):
        return None
    tag_match = TAG_NAME.match(prefix)
    if tag_match is None:
        return None
    tag = tag_match.group(1).split(b":")[-1].lower()
    attribute = match.group("attribute").lower()
    closing = payload.find(b">", match.end())
    tag_bytes = payload[last_open : closing + 1] if closing >= 0 else prefix
    if suffix == ".opf":
        return "package.metadata_or_link"
    if suffix == ".svg" or tag in {b"svg", b"image", b"use", b"feimage"}:
        return "svg.resource"
    if tag == b"link" and attribute == b"href" and STYLESHEET_REL.search(tag_bytes):
        return "stylesheet.resource"
    if (tag in {b"a", b"area"} and attribute == b"href") or (
        tag == b"content" and attribute == b"src"
    ):
        return "content.navigation"
    if tag in {
        b"audio",
        b"embed",
        b"iframe",
        b"img",
        b"input",
        b"object",
        b"source",
        b"track",
        b"video",
    } and attribute in {b"href", b"poster", b"src"}:
        return "content.embedded_resource"
    if _inside_script(payload, position):
        return "text_or_script.literal"
    return "markup.other_attribute"


def classify_markup(payload: bytes, suffix: str) -> dict[str, Any]:
    contexts: set[str] = set()
    unclassified = False
    css_matches = list(CSS_REMOTE.finditer(payload))
    if css_matches:
        contexts.add("stylesheet.resource")
    attribute_matches = list(ATTRIBUTE_REMOTE.finditer(payload))
    for match in attribute_matches:
        context = _attribute_context(payload, match, suffix)
        if context is None:
            unclassified = True
        else:
            contexts.add(context)
    return {
        "contexts": sorted(contexts),
        "remote_reference_present": bool(css_matches or attribute_matches),
        "unclassified": unclassified,
    }


def validate_projection(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != PROJECTION_FIELDS:
        raise ExperimentError("EXP-0015 projection fields differ")
    contexts = value.get("contexts")
    if (
        not isinstance(contexts, list)
        or contexts != sorted(set(contexts))
        or any(context not in CONTEXT_CLASSES for context in contexts)
    ):
        raise ExperimentError("EXP-0015 context projection differs")
    if not isinstance(value.get("remote_reference_present"), bool):
        raise ExperimentError("EXP-0015 remote projection differs")
    if not isinstance(value.get("unclassified"), bool):
        raise ExperimentError("EXP-0015 unclassified projection differs")
    if value["remote_reference_present"] is not bool(
        contexts or value["unclassified"]
    ):
        raise ExperimentError("EXP-0015 projection is inconsistent")
    return value


def scan_epub(path: Path, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    limits = (profile or {"limits": _expected_limits()})["limits"]
    contexts: set[str] = set()
    remote_reference_present = False
    unclassified = False
    try:
        with zipfile.ZipFile(path, mode="r") as archive:
            infos = archive.infolist()
            if not infos or len(infos) > limits["max_archive_entries"]:
                raise ExperimentError("archive entry limit differs")
            names: set[str] = set()
            expanded = 0
            selected: list[zipfile.ZipInfo] = []
            mimetypes: list[zipfile.ZipInfo] = []
            for info in infos:
                name = _safe_entry_name(
                    info.filename, limits["max_relative_name_bytes"]
                )
                key = name.casefold()
                if key in names:
                    raise ExperimentError("archive contains duplicate entries")
                names.add(key)
                if info.flag_bits & 0x1:
                    raise ExperimentError("archive contains encrypted entries")
                if _entry_is_link(info):
                    raise ExperimentError("archive contains indirect entries")
                if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    raise ExperimentError("archive compression differs")
                if info.file_size < 0 or info.compress_size < 0:
                    raise ExperimentError("archive size differs")
                expanded += info.file_size
                if name == "mimetype":
                    mimetypes.append(info)
                if not info.is_dir() and Path(name).suffix.lower() in MARKUP_SUFFIXES:
                    selected.append(info)
            if expanded > limits["max_expanded_bytes"]:
                raise ExperimentError("archive expanded size differs")
            if len(mimetypes) != 1 or archive.read(mimetypes[0]) != b"application/epub+zip":
                raise ExperimentError("archive EPUB marker differs")
            if any(
                info.file_size > limits["max_markup_entry_bytes"]
                for info in selected
            ):
                raise ExperimentError("markup entry limit differs")
            if sum(info.file_size for info in selected) > limits["max_markup_total_bytes"]:
                raise ExperimentError("markup total limit differs")
            for info in infos:
                if info.is_dir() or info.file_size == 0:
                    continue
                if info.compress_size == 0 or (
                    info.file_size / info.compress_size
                    > limits["max_compression_ratio"]
                ):
                    raise ExperimentError("archive compression ratio differs")
            actual_total = 0
            for info in selected:
                with archive.open(info, mode="r") as stream:
                    payload = stream.read(limits["max_markup_entry_bytes"] + 1)
                actual_total += len(payload)
                if (
                    len(payload) != info.file_size
                    or actual_total > limits["max_markup_total_bytes"]
                ):
                    raise ExperimentError("markup read limit differs")
                projection = classify_markup(
                    payload, Path(info.filename).suffix.lower()
                )
                contexts.update(projection["contexts"])
                remote_reference_present = (
                    remote_reference_present
                    or projection["remote_reference_present"]
                )
                unclassified = unclassified or projection["unclassified"]
    except ExperimentError:
        raise
    except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile) as exc:
        raise ExperimentError("archive scan failed closed") from exc
    return validate_projection(
        {
            "contexts": sorted(contexts),
            "remote_reference_present": remote_reference_present,
            "unclassified": unclassified,
        }
    )


def aggregate_projections(values: list[dict[str, Any]]) -> dict[str, Any]:
    if len(values) != 3:
        raise ExperimentError("EXP-0015 aggregate input count differs")
    reports = [validate_projection(value) for value in values]
    counts = Counter(
        context for report in reports for context in report["contexts"]
    )
    minimum = _expected_limits()["minimum_group_size"]
    visible = {
        context: counts[context]
        for context in CONTEXT_CLASSES
        if counts[context] >= minimum
    }
    suppressed = any(0 < count < minimum for count in counts.values())
    remote_count = sum(
        1 for report in reports if report["remote_reference_present"]
    )
    unclassified_count = sum(1 for report in reports if report["unclassified"])
    if unclassified_count or remote_count != 3:
        qualification = "inconclusive"
    elif visible:
        qualification = "shared_context_present"
    else:
        qualification = "no_shared_context"
    return {
        "context_input_counts": visible,
        "qualification": qualification,
        "remote_reference_input_count": remote_count,
        "status": "inconclusive" if qualification == "inconclusive" else "pass",
        "suppressed_context_present": suppressed,
        "unclassified_input_count": unclassified_count,
    }


def build_private_result(
    aggregate: dict[str, Any],
    *,
    input_count: int,
    parser_runs: int,
    execution_complete: bool,
    source_unchanged: bool,
    cleanup_complete: bool,
) -> dict[str, Any]:
    if (
        input_count != 3
        or parser_runs != 3
        or not execution_complete
        or not source_unchanged
        or not cleanup_complete
    ):
        raise ExperimentError("EXP-0015 private completion differs")
    result = {
        "artifact": "EXP-0015",
        "cleanup_complete": True,
        "context_input_counts": aggregate["context_input_counts"],
        "input_count": 3,
        "minimum_group_size": 2,
        "parser_runs": 3,
        "path_free": True,
        "qualification": aggregate["qualification"],
        "remote_reference_input_count": aggregate[
            "remote_reference_input_count"
        ],
        "schema": RESULT_SCHEMA,
        "source_unchanged": True,
        "status": aggregate["status"],
        "suppressed_context_present": aggregate[
            "suppressed_context_present"
        ],
        "unclassified_input_count": aggregate["unclassified_input_count"],
    }
    return validate_private_result_dict(result)


def _bounded_count(value: Any, maximum: int = 3) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
        raise ExperimentError("EXP-0015 count differs")
    return value


def validate_private_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict) or set(result) != RESULT_FIELDS:
        raise ExperimentError("EXP-0015 result fields differ")
    if result.get("schema") != RESULT_SCHEMA or result.get("artifact") != "EXP-0015":
        raise ExperimentError("EXP-0015 result identity differs")
    if (
        result.get("input_count") != 3
        or result.get("parser_runs") != 3
        or result.get("minimum_group_size") != 2
    ):
        raise ExperimentError("EXP-0015 result run count differs")
    if (
        result.get("source_unchanged") is not True
        or result.get("cleanup_complete") is not True
        or result.get("path_free") is not True
    ):
        raise ExperimentError("EXP-0015 result safety differs")
    contexts = result.get("context_input_counts")
    if not isinstance(contexts, dict) or list(contexts) != sorted(contexts):
        raise ExperimentError("EXP-0015 result contexts differ")
    for context, count in contexts.items():
        if context not in CONTEXT_CLASSES or not 2 <= _bounded_count(count) <= 3:
            raise ExperimentError("EXP-0015 visible context differs")
    if not isinstance(result.get("suppressed_context_present"), bool):
        raise ExperimentError("EXP-0015 suppression proof differs")
    remote_count = _bounded_count(result.get("remote_reference_input_count"))
    unclassified_count = _bounded_count(result.get("unclassified_input_count"))
    if unclassified_count > remote_count or any(
        count > remote_count for count in contexts.values()
    ):
        raise ExperimentError("EXP-0015 result counts are inconsistent")
    qualification = result.get("qualification")
    if qualification not in QUALIFICATIONS:
        raise ExperimentError("EXP-0015 qualification differs")
    expected = (
        "inconclusive"
        if unclassified_count or remote_count != 3
        else "shared_context_present"
        if contexts
        else "no_shared_context"
    )
    if qualification != expected:
        raise ExperimentError("EXP-0015 qualification is inconsistent")
    expected_status = "inconclusive" if expected == "inconclusive" else "pass"
    if result.get("status") != expected_status:
        raise ExperimentError("EXP-0015 status differs")
    if expected == "no_shared_context" and not result["suppressed_context_present"]:
        raise ExperimentError("EXP-0015 suppression proof is inconsistent")
    encoded = canonical_json(result)
    if (
        len(encoded.encode("utf-8")) > _expected_limits()["output_bytes"]
        or PRIVATE_PATH_PATTERN.search(encoded)
        or SHA256_PATTERN.search(encoded)
        or "http://" in encoded.lower()
        or "https://" in encoded.lower()
    ):
        raise ExperimentError("EXP-0015 result contains private data")
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    return validate_private_result_dict(load_json(path))


def _ensure_temp_root(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve(strict=True)
    allowed = ALLOWED_TEMP_ROOT.resolve(strict=True)
    if resolved != allowed:
        raise ExperimentError("EXP-0015 temp root differs")
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


def _write_synthetic_epub(path: Path, entries: dict[str, bytes] | None = None) -> None:
    base = {
        "META-INF/container.xml": (
            b"<container><rootfiles><rootfile full-path='OEBPS/content.opf'/>"
            b"</rootfiles></container>"
        ),
        "OEBPS/content.opf": b"<package><metadata/></package>",
        "OEBPS/content.xhtml": b"<html><body><a href='#local'>local</a></body></html>",
    }
    base.update(entries or {})
    with zipfile.ZipFile(path, mode="w") as archive:
        archive.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, payload in base.items():
            archive.writestr(name, payload, compress_type=zipfile.ZIP_DEFLATED)


def _context_entries(context: str) -> dict[str, bytes]:
    remote = b"https://example.invalid/resource"
    if context == "package.metadata_or_link":
        return {"OEBPS/content.opf": b"<package><metadata><link HREF=\"HTTPS://example.invalid/resource?a=1&amp;b=2\"/></metadata></package>"}
    if context == "content.navigation":
        return {"OEBPS/content.xhtml": b"<html><body><a href='" + remote + b"'>link</a></body></html>"}
    if context == "content.embedded_resource":
        return {"OEBPS/content.xhtml": b"<html><body><video POSTER=\"HTTP://example.invalid/resource\"/></body></html>"}
    if context == "stylesheet.resource":
        return {"OEBPS/style.css": b"@IMPORT URL(\"HTTPS://example.invalid/resource?a=1&amp;b=2\");"}
    if context == "svg.resource":
        return {"OEBPS/image.svg": b"<svg><image href='" + remote + b"'/></svg>"}
    if context == "markup.other_attribute":
        return {"OEBPS/content.xhtml": b"<html><body><custom SRC = \"" + remote + b"\"/></body></html>"}
    if context == "text_or_script.literal":
        return {"OEBPS/content.xhtml": b"<html><script>const x=\"href='" + remote + b"'\";</script></html>"}
    raise ExperimentError("synthetic context differs")


def _patch_zip_flags(path: Path, flag: int) -> None:
    payload = bytearray(path.read_bytes())
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        position = 0
        while (position := payload.find(signature, position)) >= 0:
            value = int.from_bytes(payload[position + offset : position + offset + 2], "little")
            payload[position + offset : position + offset + 2] = (value | flag).to_bytes(2, "little")
            position += 4
    path.write_bytes(payload)


def _patch_first_declared_size(path: Path, size: int) -> None:
    payload = bytearray(path.read_bytes())
    local = payload.find(b"PK\x03\x04")
    central = payload.find(b"PK\x01\x02")
    if local < 0 or central < 0:
        raise ExperimentError("synthetic ZIP patch differs")
    payload[local + 22 : local + 26] = size.to_bytes(4, "little")
    payload[central + 24 : central + 28] = size.to_bytes(4, "little")
    path.write_bytes(payload)


def _expect_failure(action: Callable[[], Any]) -> None:
    try:
        action()
    except ExperimentError:
        return
    raise ExperimentError("synthetic negative control did not fail closed")


def run_negative_controls(root: Path, profile: dict[str, Any]) -> int:
    root.mkdir()
    inputs = []
    for name in ("a.epub", "b.epub", "c.epub", "d.epub"):
        path = root / name
        _write_synthetic_epub(path)
        inputs.append(path)
    validate_private_inputs(inputs[:3])
    directory = root / "directory.epub"
    directory.mkdir()
    link = root / "link.epub"
    try:
        link.symlink_to(inputs[0])
    except OSError as exc:
        raise ExperimentError("synthetic link control is unavailable") from exc
    oversized = root / "oversized.epub"
    with oversized.open("wb") as stream:
        stream.truncate(_expected_input_contract()["max_file_bytes"] + 1)
    _expect_failure(lambda: validate_private_inputs(inputs[:2]))
    _expect_failure(lambda: validate_private_inputs(inputs))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], inputs[1]]))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], directory]))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], link]))
    _expect_failure(lambda: validate_private_inputs([inputs[0], inputs[1], oversized]))

    invalid = root / "invalid.epub"
    invalid.write_bytes(b"not-a-zip")
    _expect_failure(lambda: scan_epub(invalid, profile))

    traversal = root / "traversal.epub"
    _write_synthetic_epub(traversal, {"../escape.xhtml": b"<html/>"})
    _expect_failure(lambda: scan_epub(traversal, profile))

    duplicate = root / "duplicate.epub"
    _write_synthetic_epub(duplicate)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(duplicate, mode="a") as archive:
            archive.writestr("OEBPS/content.xhtml", b"<html/>")
    _expect_failure(lambda: scan_epub(duplicate, profile))

    encrypted = root / "encrypted.epub"
    _write_synthetic_epub(encrypted)
    _patch_zip_flags(encrypted, 0x1)
    _expect_failure(lambda: scan_epub(encrypted, profile))

    entry_limit = root / "entry-limit.epub"
    extras = {f"OEBPS/empty-{index}.bin": b"" for index in range(510)}
    _write_synthetic_epub(entry_limit, extras)
    _expect_failure(lambda: scan_epub(entry_limit, profile))

    expanded = root / "expanded.epub"
    _write_synthetic_epub(expanded)
    _patch_first_declared_size(
        expanded, _expected_limits()["max_expanded_bytes"] + 1
    )
    _expect_failure(lambda: scan_epub(expanded, profile))

    markup_entry = root / "markup-entry.epub"
    _write_synthetic_epub(
        markup_entry,
        {"OEBPS/large.xhtml": b"x" * (_expected_limits()["max_markup_entry_bytes"] + 1)},
    )
    _expect_failure(lambda: scan_epub(markup_entry, profile))

    markup_total = root / "markup-total.epub"
    _write_synthetic_epub(
        markup_total,
        {
            f"OEBPS/large-{index}.xhtml": b"x" * (2 * 1024 * 1024)
            for index in range(9)
        },
    )
    _expect_failure(lambda: scan_epub(markup_total, profile))

    ratio = root / "ratio.epub"
    _write_synthetic_epub(ratio, {"OEBPS/repeated.bin": b"x" * (1024 * 1024)})
    _expect_failure(lambda: scan_epub(ratio, profile))

    source_snapshot = validate_private_inputs(inputs[:3])[0]
    inputs[0].write_bytes(inputs[0].read_bytes() + b"changed")
    if _source_matches(source_snapshot):
        raise ExperimentError("synthetic source-change control differs")

    valid = build_private_result(
        aggregate_projections(
            [
                {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                {"contexts": ["markup.other_attribute"], "remote_reference_present": True, "unclassified": False},
            ]
        ),
        input_count=3,
        parser_runs=3,
        execution_complete=True,
        source_unchanged=True,
        cleanup_complete=True,
    )
    private = dict(valid)
    private["url"] = "https://example.invalid/private"
    _expect_failure(lambda: validate_private_result_dict(private))
    _expect_failure(
        lambda: build_private_result(
            aggregate_projections(
                [
                    {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                    {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                    {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                ]
            ),
            input_count=3,
            parser_runs=2,
            execution_complete=False,
            source_unchanged=True,
            cleanup_complete=True,
        )
    )
    _expect_failure(
        lambda: build_private_result(
            aggregate_projections(
                [
                    {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                    {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                    {"contexts": ["content.navigation"], "remote_reference_present": True, "unclassified": False},
                ]
            ),
            input_count=3,
            parser_runs=3,
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
    temp_root = _ensure_temp_root(temp_root)
    task_root = _create_task_root(temp_root, "synthetic-")
    parser_runs = 0
    contexts_verified = 0
    repetitions_identical = False
    negative_count = 0
    failure: BaseException | None = None
    cleanup_failure: BaseException | None = None
    try:
        for context in CONTEXT_CLASSES:
            projections = []
            for index in range(3):
                path = task_root / f"context-{contexts_verified}-{index}.epub"
                _write_synthetic_epub(
                    path, _context_entries(context) if index < 2 else None
                )
                projections.append(scan_epub(path, profile))
                parser_runs += 1
            aggregate = aggregate_projections(projections)
            if (
                aggregate["context_input_counts"] != {context: 2}
                or aggregate["qualification"] != "inconclusive"
            ):
                raise ExperimentError("synthetic context control differs")
            contexts_verified += 1

        shared = []
        for index in range(3):
            path = task_root / f"shared-{index}.epub"
            _write_synthetic_epub(path, _context_entries("content.navigation"))
            shared.append(scan_epub(path, profile))
            parser_runs += 1
        first = aggregate_projections(shared)
        second = aggregate_projections(shared)
        repetitions_identical = canonical_json(first) == canonical_json(second)
        if (
            first["qualification"] != "shared_context_present"
            or first["context_input_counts"] != {"content.navigation": 3}
            or not repetitions_identical
        ):
            raise ExperimentError("synthetic shared context control differs")

        suppressed = []
        for index in range(3):
            path = task_root / f"suppressed-{index}.epub"
            _write_synthetic_epub(
                path,
                _context_entries("svg.resource")
                if index == 0
                else _context_entries("content.navigation"),
            )
            suppressed.append(scan_epub(path, profile))
            parser_runs += 1
        suppression = aggregate_projections(suppressed)
        if (
            suppression["context_input_counts"] != {"content.navigation": 2}
            or suppression["suppressed_context_present"] is not True
            or "svg.resource" in suppression["context_input_counts"]
        ):
            raise ExperimentError("synthetic suppression control differs")

        unclassified = []
        for index in range(3):
            path = task_root / f"unclassified-{index}.epub"
            entries = (
                {"OEBPS/content.xhtml": b"<!-- href='https://example.invalid/x' -->"}
                if index == 0
                else _context_entries("content.navigation")
            )
            _write_synthetic_epub(path, entries)
            unclassified.append(scan_epub(path, profile))
            parser_runs += 1
        ambiguous = aggregate_projections(unclassified)
        if (
            ambiguous["qualification"] != "inconclusive"
            or ambiguous["unclassified_input_count"] != 1
        ):
            raise ExperimentError("synthetic unclassified control differs")

        nonremote_path = task_root / "nonremote.epub"
        _write_synthetic_epub(
            nonremote_path,
            {
                "OEBPS/content.xhtml": (
                    b"<a href='#fragment'><img src='data:image/png;base64,AA=='/>"
                    b"</a>"
                )
            },
        )
        nonremote = scan_epub(nonremote_path, profile)
        parser_runs += 1
        if nonremote != {
            "contexts": [],
            "remote_reference_present": False,
            "unclassified": False,
        }:
            raise ExperimentError("synthetic local reference control differs")

        multi_path = task_root / "multiple-contexts.epub"
        _write_synthetic_epub(
            multi_path,
            {
                "OEBPS/content.xhtml": (
                    b"<a href='https://example.invalid/navigation'>"
                    b"<img src=\"https://example.invalid/image\"/>"
                    b"<img src='https://example.invalid/image-again'/></a>"
                    b"<style>body{background:url(https://example.invalid/css)}</style>"
                )
            },
        )
        multi = scan_epub(multi_path, profile)
        parser_runs += 1
        if multi != {
            "contexts": [
                "content.embedded_resource",
                "content.navigation",
                "stylesheet.resource",
            ],
            "remote_reference_present": True,
            "unclassified": False,
        }:
            raise ExperimentError("synthetic multi-context control differs")

        negative_count = run_negative_controls(task_root / "negative", profile)
    except BaseException as exc:
        failure = exc
    try:
        task_removed = _remove_owned_task(task_root, temp_root, "synthetic-")
    except BaseException as exc:
        task_removed = False
        cleanup_failure = exc
    if cleanup_failure is not None or not task_removed:
        raise ExperimentError("synthetic cleanup differs") from (
            cleanup_failure or failure
        )
    if failure is not None:
        raise failure
    summary = {
        "artifact": "EXP-0015",
        "cleanup_complete": True,
        "context_classes": contexts_verified,
        "negative_controls": negative_count,
        "parser_runs": parser_runs,
        "path_free": True,
        "repetitions_identical": repetitions_identical,
        "schema": SYNTHETIC_SCHEMA,
        "status": "pass",
    }
    if PRIVATE_PATH_PATTERN.search(canonical_json(summary)):
        raise ExperimentError("synthetic summary contains private data")
    return summary


def _write_result_once(path: Path, result: dict[str, Any]) -> None:
    if path.exists():
        raise ExperimentError("EXP-0015 result already exists")
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
        raise ExperimentError("same EXP-0014 input set is not confirmed")
    validated = validate_private_inputs(values)
    if result_path.exists():
        raise ExperimentError("EXP-0015 result already exists")
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
        for target, _source in copied:
            projections.append(scan_epub(target, profile))
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
    if (
        cleanup_failure is not None
        or not task_removed
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
        parser_runs=len(projections),
        execution_complete=execution_complete,
        source_unchanged=source_unchanged,
        cleanup_complete=task_removed,
    )
    _write_result_once(result_path, result)
    return result


def parser() -> SafeArgumentParser:
    value = SafeArgumentParser(description=__doc__)
    value.add_argument("--validate-profile", action="store_true")
    value.add_argument("--validate-result", action="store_true")
    value.add_argument("--synthetic-controls", action="store_true")
    value.add_argument("--private-epub", action="append", type=Path, default=[])
    value.add_argument("--confirm-same-exp-0014-inputs", action="store_true")
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
            raise ExperimentError("exactly one EXP-0015 execution mode is required")
        if args.confirm_same_exp_0014_inputs and not args.private_epub:
            raise ExperimentError("input confirmation differs")
        if args.validate_profile:
            validate_contract()
            print("EXP-0015 profile valid")
            return 0
        if args.validate_result:
            result = validate_result()
            print(
                "EXP-0015 result valid: "
                f"{result['status']} qualification={result['qualification']}"
            )
            return 0
        profile = validate_contract()
        if args.synthetic_controls:
            print(canonical_json(run_synthetic_controls(ALLOWED_TEMP_ROOT, profile)))
            return 0
        result = execute_private_diagnostic(
            args.private_epub,
            confirmed_same_inputs=args.confirm_same_exp_0014_inputs,
        )
        print(canonical_json(result))
        return 2 if result["status"] == "inconclusive" else 0
    except KeyboardInterrupt:
        return 130
    except ExperimentError as exc:
        print(f"EXP-0015 failed closed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"EXP-0015 failed closed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
