#!/usr/bin/env python3
"""Run the bounded EXP-0017 synthetic downstream-isolation experiment."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import secrets
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
for import_root in (ROOT, SRC):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from sammlungslotse.ebook_intake.deep_profile import (  # noqa: E402
    DeepRuntimeProfile,
)
from sammlungslotse.ebook_intake.deep_workspace import (  # noqa: E402
    TaskWorkspaceManager,
)
from sammlungslotse.ebook_intake.epubcheck_provider import (  # noqa: E402
    EpubCheckProvider,
)
from sammlungslotse.ebook_intake.model import Snapshot  # noqa: E402
from sammlungslotse.ebook_intake.podman_executor import (  # noqa: E402
    PodmanExecutor,
    run_bounded,
)
from tools.experiments import run_exp_0016  # noqa: E402


EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0017"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
CASE_MANIFEST_PATH = EXPERIMENT / "cases.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0017.py"
DEEP_PROFILE_PATH = ROOT / "runtime" / "ebook-deep-readonly" / "profile.json"

WINDOWS_TEMP_BASE = Path(r"C:\rep\tmp\SammlungsLotse\exp-0017")
WINDOWS_ARTIFACT_BASE = Path(r"C:\rep\artifacts\SammlungsLotse\exp-0017")

PROFILE_SCHEMA = "sammlungslotse/exp-0017-execution-profile/v1"
MANIFEST_SCHEMA = "sammlungslotse/exp-0017-case-manifest/v1"
RESULT_SCHEMA = "sammlungslotse/exp-0017-downstream-isolation-result/v1"

EXPECTED_CASE_COUNT = 12
EXPECTED_REPETITIONS = 2
EXPECTED_PROVIDER_RUNS = EXPECTED_CASE_COUNT * EXPECTED_REPETITIONS
MAX_EPUB_BYTES = 128 * 1024
MAX_EXPANDED_BYTES = 256 * 1024
MAX_ARCHIVE_ENTRIES = 8
MAX_RESULT_BYTES = 32 * 1024

GROUP_CASES = {
    "ambiguous_or_deceptive": ("amb-001", "amb-003", "amb-006", "amb-009"),
    "resource_or_active": ("pkg-001", "res-002", "act-001", "res-009"),
    "s3_navigation": ("usr-001", "usr-004", "usr-006", "usr-007"),
}
SELECTED_CASES = (
    "usr-001",
    "usr-004",
    "usr-006",
    "usr-007",
    "pkg-001",
    "res-002",
    "act-001",
    "res-009",
    "amb-001",
    "amb-003",
    "amb-006",
    "amb-009",
)
EXPECTED_PLACEMENTS = {
    "act-001": "content_document",
    "amb-001": "content_document",
    "amb-003": "content_document",
    "amb-006": "content_document",
    "amb-009": "content_document",
    "pkg-001": "package_metadata",
    "res-002": "content_document",
    "res-009": "stylesheet",
    "usr-001": "content_document",
    "usr-004": "navigation_document",
    "usr-006": "content_document",
    "usr-007": "svg_content_document",
}
FORBIDDEN_EFFECTS = (
    "collection_modification",
    "domain_system_writes",
    "external_network_access",
    "persistence",
    "product_modification",
)

ACCEPTANCE_KEYS = (
    "preimage_and_green_ci_bound",
    "runtime_and_dependencies_exact",
    "exact_case_matrix",
    "deterministic_bounded_epubs",
    "exp0016_oracles_match",
    "exact_repetitions_and_provider_runs",
    "provider_runs_complete_and_isolated",
    "repetitions_semantically_identical",
    "parser_and_provider_evidence_separate",
    "canary_control_sensitive",
    "deep_path_canary_quiet",
    "effective_isolation_exact",
    "timeout_fails_closed_and_cleans",
    "output_limit_rejects_and_cleans",
    "inputs_unchanged_and_tasks_clean",
    "result_private_raw_url_path_free",
    "forbidden_effects_absent",
    "separate_result_gate_required",
)
RESULT_FIELDS = frozenset(
    {
        "acceptance",
        "artifact",
        "bindings",
        "boundary_probes",
        "canary",
        "case_count",
        "cleanup",
        "effects",
        "group_counts",
        "isolation",
        "materialization",
        "parser_oracle_mismatches",
        "path_free",
        "preimage_commit",
        "provider_repetitions",
        "provider_runs",
        "repetitions",
        "runs_semantically_identical",
        "runtime",
        "schema",
        "status",
    }
)

PRODUCT_LOCATORS = tuple(
    path.relative_to(ROOT).as_posix()
    for path in sorted((ROOT / "src" / "sammlungslotse" / "ebook_intake").glob("*.py"))
)
RUNTIME_LOCATORS = (
    "docs/planning/EBOOK_GATE_0019_AFTER_EXP0016.md",
    "docs/planning/EBOOK_SYNTHETIC_DOWNSTREAM_ISOLATION_EXPERIMENT.md",
    "experiments/ebook/exp-0016/cases.json",
    "experiments/ebook/exp-0017/cases.json",
    "runtime/ebook-deep-readonly/Containerfile",
    "runtime/ebook-deep-readonly/EpubCheckWrapper.java",
    "runtime/ebook-deep-readonly/profile.json",
    *PRODUCT_LOCATORS,
    "tools/experiments/run_exp_0016.py",
    "tools/experiments/run_exp_0017.py",
    "tools/provision_ebook_deep_profile.py",
    "tools/qualify_ebook_deep_profile.py",
    "tools/run_ebook_intake.py",
)
PREIMAGE_FILES = (
    "experiments/ebook/exp-0017/execution-profile.json",
    *RUNTIME_LOCATORS,
)

PROVIDER_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")
PRIVATE_POSIX_HOME_PREFIX = b"/ho" + b"me/"
PRIVATE_OR_RAW_LITERALS = (
    b"C:\\",
    PRIVATE_POSIX_HOME_PREFIX,
    b"/Users/",
    b"127.0.0.1",
    b"localhost",
    b"example.invalid",
    b"http://",
    b"https://",
)


class ExperimentError(RuntimeError):
    """Raised when an EXP-0017 boundary or contract differs."""


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise ExperimentError("invalid EXP-0017 arguments")


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_source_bytes(value: bytes) -> bytes:
    """Normalize text checkout line endings for cross-platform bindings."""

    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_file(path: Path) -> str:
    return sha256_bytes(canonical_source_bytes(path.read_bytes()))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


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
        raise ExperimentError("read-only Git preimage check failed")
    return completed.stdout


def current_preimage() -> str:
    value = git_output("rev-parse", "HEAD").decode("ascii").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ExperimentError("invalid Git preimage")
    return value


def require_committed_preimage() -> str:
    if git_output("status", "--porcelain", "--untracked-files=all"):
        raise ExperimentError("EXP-0017 execution requires a clean preimage")
    commit = current_preimage()
    for locator in PREIMAGE_FILES:
        path = ROOT / locator
        if not path.is_file():
            raise ExperimentError("bound preimage file is missing")
        committed = canonical_source_bytes(git_output("show", f"{commit}:{locator}"))
        working = canonical_source_bytes(path.read_bytes())
        if committed != working:
            raise ExperimentError("bound preimage differs from the worktree")
    return commit


def _bindings(locators: tuple[str, ...]) -> list[dict[str, str]]:
    return [
        {"locator": locator, "sha256": sha256_file(ROOT / locator)}
        for locator in locators
    ]


def _bindings_sha256(locators: tuple[str, ...]) -> str:
    return sha256_bytes(canonical_bytes(_bindings(locators)))


def _product_tree_sha256() -> str:
    return _bindings_sha256(PRODUCT_LOCATORS)


def validate_manifest(manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    if set(manifest) != {
        "artifact",
        "cases",
        "distribution",
        "schema",
        "source_artifact",
        "standards_date",
    }:
        raise ExperimentError("case manifest fields differ")
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["artifact"] != "EXP-0017":
        raise ExperimentError("case manifest identity differs")
    if manifest["source_artifact"] != "EXP-0016":
        raise ExperimentError("case manifest source differs")
    if manifest["standards_date"] != "2026-09-01":
        raise ExperimentError("case manifest standards date differs")
    if manifest["distribution"] != {key: 4 for key in sorted(GROUP_CASES)}:
        raise ExperimentError("case manifest distribution differs")

    source_cases = run_exp_0016.validate_manifest(
        run_exp_0016.load_json(run_exp_0016.CASE_MANIFEST_PATH)
    )
    source_by_id = {case["case_id"]: case for case in source_cases}
    cases = manifest["cases"]
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ExperimentError("case manifest must contain exactly twelve cases")
    if tuple(case.get("case_id") for case in cases) != SELECTED_CASES:
        raise ExperimentError("case manifest selection or order differs")

    seen: set[str] = set()
    group_counts: Counter[str] = Counter()
    normalized: list[dict[str, Any]] = []
    expected_fields = {
        "case_id",
        "document_type",
        "expected_context",
        "expected_s3_action",
        "expected_scheme_group",
        "forbidden_effects",
        "group",
        "placement",
        "snippet",
        "source_case_id",
    }
    for case in cases:
        if not isinstance(case, dict) or set(case) != expected_fields:
            raise ExperimentError("synthetic case fields differ")
        case_id = case["case_id"]
        if case_id in seen or case_id not in SELECTED_CASES:
            raise ExperimentError("duplicate or unknown synthetic case")
        seen.add(case_id)
        source = source_by_id.get(case["source_case_id"])
        if source is None or case["source_case_id"] != case_id:
            raise ExperimentError("EXP-0016 source case differs")
        expected_group = next(
            group for group, identifiers in GROUP_CASES.items() if case_id in identifiers
        )
        if case["group"] != expected_group:
            raise ExperimentError("synthetic group differs")
        if case["placement"] != EXPECTED_PLACEMENTS[case_id]:
            raise ExperimentError("synthetic placement differs")
        if case["forbidden_effects"] != list(FORBIDDEN_EFFECTS):
            raise ExperimentError("forbidden effects differ")
        expected_values = {
            "document_type": source["document_type"],
            "expected_context": source["expected_context"],
            "expected_s3_action": source["expected_actions"][
                "strict_navigation_candidate"
            ],
            "expected_scheme_group": source["expected_scheme_group"],
            "snippet": source["snippet"],
        }
        if any(case[key] != value for key, value in expected_values.items()):
            raise ExperimentError("EXP-0016 oracle or snippet differs")
        if len(case["snippet"].encode("utf-8")) > 4096:
            raise ExperimentError("synthetic snippet exceeds its bound")
        group_counts[case["group"]] += 1
        normalized.append(case)
    if dict(sorted(group_counts.items())) != manifest["distribution"]:
        raise ExperimentError("actual case distribution differs")
    return tuple(normalized)


def _expected_runtime_contract(deep: DeepRuntimeProfile) -> dict[str, Any]:
    execution = deep.execution
    return {
        "deep_profile_id": deep.profile_id,
        "image": {
            "id": deep.image["id"],
            "platform": deep.image["platform"],
        },
        "isolation": {
            "cap_drop": execution["cap_drop"],
            "cpus": execution["cpus"],
            "environment": execution["environment"],
            "http_proxy": execution["http_proxy"],
            "input_max_bytes": execution["input_max_bytes"],
            "log_driver": execution["log_driver"],
            "memory_bytes": execution["memory_bytes"],
            "memory_swap_bytes": execution["memory_swap_bytes"],
            "network": execution["network"],
            "no_new_privileges": execution["no_new_privileges"],
            "pids_limit": execution["pids_limit"],
            "provider_arguments": execution["provider_arguments"],
            "raw_report_max_bytes": execution["raw_report_max_bytes"],
            "read_only_root": execution["read_only_root"],
            "read_only_tmpfs": execution["read_only_tmpfs"],
            "security_opt": execution["security_opt"],
            "stderr_max_bytes": execution["stderr_max_bytes"],
            "stdout_max_bytes": execution["stdout_max_bytes"],
            "timeout_seconds": execution["timeout_seconds"],
            "tmpfs": execution["tmpfs"],
            "ulimit_core": execution["ulimit_core"],
            "ulimit_nofile": execution["ulimit_nofile"],
            "user": execution["user"],
        },
        "podman": {
            "client_version": "6.1.0",
            "server_os_arch": "linux/amd64",
            "server_version": "6.1.0",
        },
        "provider": {
            "id": deep.provider["id"],
            "version": deep.provider["version"],
        },
    }


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if set(profile) != {
        "artifact",
        "case_manifest",
        "execution_gate",
        "implementation",
        "materialization",
        "output_contract",
        "profile_id",
        "repetitions",
        "runtime_bindings",
        "runtime_contract",
        "schema",
        "standards",
        "threat_model",
    }:
        raise ExperimentError("execution profile fields differ")
    if profile["schema"] != PROFILE_SCHEMA or profile["artifact"] != "EXP-0017":
        raise ExperimentError("execution profile identity differs")
    if profile["profile_id"] != "exp-0017-downstream-isolation/v1":
        raise ExperimentError("execution profile id differs")
    if profile["repetitions"] != EXPECTED_REPETITIONS:
        raise ExperimentError("execution profile repetitions differ")
    if profile["execution_gate"] != {
        "confirmation_flag": "--confirm-green-preimage-ci",
        "green_preimage_ci_required": True,
    }:
        raise ExperimentError("execution profile CI gate differs")

    implementation = profile["implementation"]
    expected_implementation = {
        "deep_tool_execution": True,
        "direct_database_access": False,
        "domain_system_writes": False,
        "downloads": False,
        "external_network_access": False,
        "git_preimage_read_only_process": True,
        "image_build": False,
        "local_loopback_measurement": True,
        "persistence": False,
        "private_input_access": False,
        "product_code_changes": False,
        "product_code_imports": True,
        "writer_surface": False,
    }
    if implementation != expected_implementation:
        raise ExperimentError("execution profile effect boundary differs")
    if profile["materialization"] != {
        "archive_entry_max": MAX_ARCHIVE_ENTRIES,
        "epub_max_bytes": MAX_EPUB_BYTES,
        "expanded_max_bytes": MAX_EXPANDED_BYTES,
        "fixed_zip_timestamp": "1980-01-01T00:00:00",
        "in_memory_only": True,
        "mimetype_first_uncompressed": True,
        "order": "mimetype-then-lexicographic",
    }:
        raise ExperimentError("materialization profile differs")
    if profile["threat_model"] != {
        "canary_control_connections": 1,
        "canary_deep_connections": 0,
        "canary_listener": "ipv4_loopback",
        "network_evidence": "executor-readback-plus-loopback-canary",
        "output_attempt_bytes": 4 * 1024 * 1024,
        "output_bound_bytes": 2 * 1024 * 1024,
        "timeout_probe_seconds": 0.001,
    }:
        raise ExperimentError("threat-model profile differs")

    manifest_binding = profile["case_manifest"]
    if manifest_binding != {
        "case_count": EXPECTED_CASE_COUNT,
        "locator": "experiments/ebook/exp-0017/cases.json",
        "sha256": sha256_file(CASE_MANIFEST_PATH),
        "source_artifact": "EXP-0016",
    }:
        raise ExperimentError("case manifest binding differs")
    bindings = _bindings(RUNTIME_LOCATORS)
    if profile["runtime_bindings"] != {
        "aggregate_sha256": sha256_bytes(canonical_bytes(bindings)),
        "files": bindings,
    }:
        raise ExperimentError("runtime bindings differ")
    deep = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
    if profile["runtime_contract"] != _expected_runtime_contract(deep):
        raise ExperimentError("runtime contract differs")

    output = profile["output_contract"]
    if output != {
        "allowed_fields": sorted(RESULT_FIELDS),
        "max_bytes": MAX_RESULT_BYTES,
        "raw_reports": False,
        "schema": RESULT_SCHEMA,
        "statuses": ["inconclusive", "pass"],
    }:
        raise ExperimentError("result contract differs")
    if profile["standards"] != [
        {
            "id": "w3c-epub-33",
            "published_on": "2026-01-13",
            "url": "https://www.w3.org/TR/2026/REC-epub-33-20260113/",
        },
        {
            "id": "w3c-epub-rs-33",
            "published_on": "2024-10-17",
            "url": "https://www.w3.org/TR/2024/REC-epub-rs-33-20241017/",
        },
        {
            "id": "epubcheck-5.3.0",
            "released_on": "2025-09-01",
            "url": "https://github.com/w3c/epubcheck/releases/tag/v5.3.0",
        },
    ]:
        raise ExperimentError("standards binding differs")
    return profile


def load_contract() -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    profile = validate_profile(load_json(PROFILE_PATH))
    cases = validate_manifest(load_json(CASE_MANIFEST_PATH))
    return profile, cases


def _replace_remote_target(snippet: str, authority: str) -> str:
    match = re.fullmatch(r"127\.0\.0\.1:([1-9][0-9]{0,4})", authority)
    if match is None or int(match.group(1)) > 65535:
        raise ExperimentError("canary authority is not loopback-bounded")
    if "example.invalid" not in snippet:
        raise ExperimentError("synthetic snippet lacks its bound target")
    return snippet.replace("example.invalid", authority)


def _xhtml_document(snippet: str) -> bytes:
    namespaces = (
        ' xmlns="http://www.w3.org/1999/xhtml"'
        ' xmlns:epub="http://www.idpf.org/2007/ops"'
        ' xmlns:foreign="urn:synthetic:foreign"'
    )
    if "<html" not in snippet:
        raise ExperimentError("XHTML snippet lacks a document root")
    body = snippet.replace("<html", f"<html{namespaces}", 1)
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + body).encode(
        "utf-8"
    )


def _svg_document(snippet: str) -> bytes:
    if "<svg" not in snippet:
        raise ExperimentError("SVG snippet lacks a document root")
    body = snippet.replace(
        "<svg",
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink"',
        1,
    )
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + body).encode(
        "utf-8"
    )


def _minimal_xhtml(stylesheet: bool = False) -> bytes:
    link = '<link rel="stylesheet" href="style.css"/>' if stylesheet else ""
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml"><head>'
        f"<title>Synthetic</title>{link}</head><body><p>Synthetic</p></body></html>"
    ).encode("utf-8")


def _package_document(
    manifest_items: list[tuple[str, str, str, str]],
    *,
    metadata_extra: str = "",
) -> bytes:
    manifest = "".join(
        f'<item id="{item_id}" href="{href}" media-type="{media_type}"{properties}/>'
        for item_id, href, media_type, properties in manifest_items
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="pub-id">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="pub-id">urn:uuid:00000000-0000-0000-0000-000000000017</dc:identifier>'
        '<dc:title>Synthetic EXP-0017</dc:title><dc:language>en</dc:language>'
        '<meta property="dcterms:modified">2026-09-01T00:00:00Z</meta>'
        f"{metadata_extra}</metadata><manifest>{manifest}</manifest>"
        '<spine><itemref idref="main"/></spine></package>'
    ).encode("utf-8")


def _zip_info(name: str, *, stored: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def materialize_epub(case: dict[str, Any], authority: str) -> bytes:
    snippet = _replace_remote_target(case["snippet"], authority)
    placement = case["placement"]
    content: dict[str, bytes]
    metadata_extra = ""
    if placement == "stylesheet":
        content = {
            "EPUB/content.xhtml": _minimal_xhtml(stylesheet=True),
            "EPUB/style.css": snippet.encode("utf-8"),
        }
        items = [
            ("main", "content.xhtml", "application/xhtml+xml", ""),
            ("style", "style.css", "text/css", ""),
        ]
    elif placement == "package_metadata":
        match = re.fullmatch(r"<package><metadata>(.*)</metadata></package>", snippet)
        if match is None:
            raise ExperimentError("package metadata snippet differs")
        metadata_extra = match.group(1)
        content = {"EPUB/content.xhtml": _minimal_xhtml()}
        items = [("main", "content.xhtml", "application/xhtml+xml", "")]
    elif placement == "svg_content_document":
        content = {"EPUB/content.svg": _svg_document(snippet)}
        items = [("main", "content.svg", "image/svg+xml", "")]
    elif placement in {"content_document", "navigation_document"}:
        name = "nav.xhtml" if placement == "navigation_document" else "content.xhtml"
        properties = ' properties="nav"' if placement == "navigation_document" else ""
        content = {f"EPUB/{name}": _xhtml_document(snippet)}
        items = [("main", name, "application/xhtml+xml", properties)]
    else:
        raise ExperimentError("unknown synthetic placement")

    fixed = {
        "META-INF/container.xml": (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" '
            'version="1.0"><rootfiles><rootfile full-path="EPUB/package.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>'
        ).encode("utf-8"),
        "EPUB/package.opf": _package_document(items, metadata_extra=metadata_extra),
        **content,
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr(_zip_info("mimetype", stored=True), b"application/epub+zip")
        for name in sorted(fixed):
            archive.writestr(_zip_info(name), fixed[name])
    payload = stream.getvalue()
    inspect_materialized_epub(payload)
    return payload


def inspect_materialized_epub(payload: bytes) -> dict[str, int | bool]:
    if not payload or len(payload) > MAX_EPUB_BYTES:
        raise ExperimentError("materialized EPUB exceeds its byte bound")
    with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
        entries = archive.infolist()
        if not entries or len(entries) > MAX_ARCHIVE_ENTRIES:
            raise ExperimentError("materialized EPUB entry count differs")
        if entries[0].filename != "mimetype" or entries[0].compress_type != 0:
            raise ExperimentError("materialized EPUB mimetype contract differs")
        if archive.read("mimetype") != b"application/epub+zip":
            raise ExperimentError("materialized EPUB media type differs")
        expanded = 0
        for entry in entries:
            logical = Path(entry.filename)
            if logical.is_absolute() or ".." in logical.parts or entry.is_dir():
                raise ExperimentError("materialized EPUB entry is unsafe")
            expanded += entry.file_size
        if expanded > MAX_EXPANDED_BYTES:
            raise ExperimentError("materialized EPUB expansion exceeds its bound")
        return {
            "entry_count": len(entries),
            "expanded_bytes": expanded,
            "mimetype_first_uncompressed": True,
            "size_bytes": len(payload),
        }


class LoopbackCanary:
    """Counts only ephemeral IPv4-loopback TCP accepts."""

    def __init__(self) -> None:
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(8)
        self._listener.settimeout(0.1)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._count = 0
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    @property
    def authority(self) -> str:
        return f"127.0.0.1:{self._listener.getsockname()[1]}"

    @property
    def count(self) -> int:
        with self._lock:
            return self._count

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                connection, _ = self._listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with connection:
                with self._lock:
                    self._count += 1

    def prove_and_reset(self) -> int:
        with socket.create_connection(self._listener.getsockname(), timeout=2):
            pass
        deadline = time.monotonic() + 2
        while self.count != 1 and time.monotonic() < deadline:
            time.sleep(0.01)
        observed = self.count
        if observed != 1:
            raise ExperimentError("loopback canary sensitivity differs")
        with self._lock:
            self._count = 0
        return observed

    def close(self) -> bool:
        self._stop.set()
        self._thread.join(timeout=2)
        self._listener.close()
        return not self._thread.is_alive()


def _command(
    arguments: list[str],
    *,
    timeout: float,
    stdout_limit: int = 128 * 1024,
    stderr_limit: int = 128 * 1024,
) -> Any:
    result = run_bounded(
        arguments,
        timeout=timeout,
        stdout_limit=stdout_limit,
        stderr_limit=stderr_limit,
    )
    if result.timed_out or result.returncode != 0:
        raise ExperimentError("bounded local runtime command failed")
    return result


def _podman_json(arguments: list[str], *, timeout: float = 15) -> Any:
    result = _command(arguments, timeout=timeout)
    try:
        return json.loads(result.stdout)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ExperimentError("local runtime returned invalid JSON") from exc


def _container_names() -> set[str]:
    result = _command(
        [
            "podman",
            "ps",
            "-a",
            "--filter",
            "name=sammlungslotse-wi0005-",
            "--format",
            "{{.Names}}",
        ],
        timeout=15,
        stdout_limit=64 * 1024,
        stderr_limit=64 * 1024,
    )
    return {
        line.decode("utf-8").strip()
        for line in result.stdout.splitlines()
        if line.strip()
    }


def runtime_preflight(deep: DeepRuntimeProfile) -> dict[str, Any]:
    executor = PodmanExecutor(deep)
    executor._inspect_runtime()
    image = executor._inspect_image()
    version = _podman_json(["podman", "version", "--format", "json"])
    runtime = {
        "client_version": version.get("Client", {}).get("Version"),
        "server_os_arch": version.get("Server", {}).get("OsArch"),
        "server_version": version.get("Server", {}).get("Version"),
    }
    if runtime != {
        "client_version": "6.1.0",
        "server_os_arch": "linux/amd64",
        "server_version": "6.1.0",
    }:
        raise ExperimentError("Podman runtime differs from the bound preimage")
    actual_id = str(image.get("Id", ""))
    if actual_id and not actual_id.startswith("sha256:"):
        actual_id = f"sha256:{actual_id}"
    if actual_id != deep.image["id"]:
        raise ExperimentError("container image differs from the bound preimage")
    return {
        **runtime,
        "deep_profile_id": deep.profile_id,
        "image_id_exact": True,
        "provider_id": deep.provider["id"],
        "provider_version": deep.provider["version"],
    }


def _remove_container(name: str, deep: DeepRuntimeProfile) -> bool:
    result = run_bounded(
        ["podman", "rm", "--force", name],
        timeout=15,
        stdout_limit=deep.execution["stdout_max_bytes"],
        stderr_limit=deep.execution["stderr_max_bytes"],
    )
    return result.returncode == 0 and not result.timed_out


def isolation_prestart(
    deep: DeepRuntimeProfile, temp_root: Path, snapshot: Snapshot
) -> dict[str, Any]:
    manager = TaskWorkspaceManager(temp_root, deep)
    workspace = manager.create(snapshot)
    executor = PodmanExecutor(deep)
    name = f"sammlungslotse-wi0005-exp0017-isolation-{uuid.uuid4().hex[:12]}"
    created = False
    removed = False
    try:
        create = run_bounded(
            executor._create_arguments(name, workspace),
            timeout=15,
            stdout_limit=deep.execution["stdout_max_bytes"],
            stderr_limit=deep.execution["stderr_max_bytes"],
        )
        if create.timed_out or create.returncode != 0:
            raise ExperimentError("isolation probe container creation failed")
        created = True
        image = executor._inspect_image()
        inspection = executor._inspect_container(name)
        host = inspection.get("HostConfig", {})
        config = inspection.get("Config", {})
        mounts = inspection.get("Mounts", [])
        input_mounts = [
            value for value in mounts if value.get("Destination") == "/input/input.epub"
        ]
        expected_tmpfs = {
            "/output": (
                "rw,nosuid,nodev,noexec,size=2097152,mode=1777,rprivate,tmpcopyup"
            ),
            "/tmp": (
                "rw,nosuid,nodev,noexec,size=16777216,mode=1777,rprivate,tmpcopyup"
            ),
        }
        expected_ulimits = {
            ("RLIMIT_CORE", 0, 0),
            ("RLIMIT_NOFILE", 256, 256),
        }
        actual_ulimits = {
            (item.get("Name"), item.get("Soft"), item.get("Hard"))
            for item in (host.get("Ulimits") or [])
        }
        return {
            "cap_drop": sorted(host.get("CapDrop") or []),
            "command_exact": config.get("Cmd") == deep.execution["provider_arguments"],
            "container_removed": False,
            "cpu_nanos": host.get("NanoCpus"),
            "environment_exact": set(config.get("Env") or [])
            == {
                f"{key}={value}"
                for key, value in deep.execution["environment"].items()
            },
            "input_read_only": len(input_mounts) == 1
            and input_mounts[0].get("RW") is False,
            "memory_bytes": host.get("Memory"),
            "memory_swap_bytes": host.get("MemorySwap"),
            "network": host.get("NetworkMode"),
            "no_new_privileges": "no-new-privileges"
            in (host.get("SecurityOpt") or []),
            "pids_limit": host.get("PidsLimit"),
            "privileged": host.get("Privileged"),
            "read_only_root": host.get("ReadonlyRootfs"),
            "task_root_empty": False,
            "tmpfs_exact": host.get("Tmpfs") == expected_tmpfs,
            "ulimits_exact": actual_ulimits == expected_ulimits,
            "verified_by_executor": executor._isolation_matches(inspection, image),
        }
    finally:
        if created:
            removed = _remove_container(name, deep)
        manager.cleanup(workspace)
        if not removed:
            raise ExperimentError("isolation probe container cleanup failed")


def _finalize_isolation_probe(
    isolation: dict[str, Any], temp_root: Path
) -> dict[str, Any]:
    if not temp_root.is_dir() or list(temp_root.iterdir()):
        raise ExperimentError("isolation probe task cleanup differs")
    return {**isolation, "container_removed": True, "task_root_empty": True}


def output_limit_probe(deep: DeepRuntimeProfile) -> dict[str, Any]:
    execution = deep.execution
    name = f"sammlungslotse-wi0005-exp0017-output-{uuid.uuid4().hex[:12]}"
    result = None
    removed = False
    arguments = [
        "podman",
        "run",
        "--name",
        name,
        "--pull=never",
        "--network",
        execution["network"],
        "--http-proxy=false",
        "--read-only",
        "--read-only-tmpfs=false",
        "--cap-drop",
        "all",
        "--security-opt",
        "no-new-privileges",
        "--user",
        execution["user"],
        "--pids-limit",
        str(execution["pids_limit"]),
        "--cpus",
        execution["cpus"],
        "--memory",
        str(execution["memory_bytes"]),
        "--memory-swap",
        str(execution["memory_swap_bytes"]),
        "--ulimit",
        f"core={execution['ulimit_core']}",
        "--ulimit",
        f"nofile={execution['ulimit_nofile']}",
        "--tmpfs",
        f"/tmp:rw,nosuid,nodev,noexec,size={execution['tmpfs']['/tmp']},mode=1777",
        "--tmpfs",
        f"/output:rw,nosuid,nodev,noexec,size={execution['tmpfs']['/output']},mode=1777",
        "--log-driver",
        execution["log_driver"],
    ]
    for key, value in sorted(execution["environment"].items()):
        arguments.extend(["--env", f"{key}={value}"])
    arguments.extend(
        [
            "--entrypoint",
            "/bin/dd",
            deep.image["id"],
            "if=/dev/zero",
            "of=/output/limit.bin",
            "bs=1048576",
            "count=4",
        ]
    )
    try:
        result = run_bounded(
            arguments,
            timeout=30,
            stdout_limit=execution["stdout_max_bytes"],
            stderr_limit=execution["stderr_max_bytes"],
        )
    finally:
        removed = _remove_container(name, deep)
    return {
        "attempted_bytes": 4 * 1024 * 1024,
        "bounded_bytes": execution["tmpfs"]["/output"],
        "container_removed": removed,
        "write_rejected": result is not None
        and not result.timed_out
        and result.returncode != 0,
    }


def timeout_probe(
    deep: DeepRuntimeProfile, temp_root: Path, snapshot: Snapshot
) -> dict[str, Any]:
    changed = deepcopy(deep.data)
    changed["execution"]["timeout_seconds"] = 0.001
    timeout_profile = DeepRuntimeProfile(changed)
    before = _container_names()
    result = EpubCheckProvider(
        profile=timeout_profile,
        temp_root=temp_root,
    ).inspect(snapshot)
    after = _container_names()
    task_root_empty = temp_root.is_dir() and not list(temp_root.iterdir())
    return {
        "assessment": result.assessment,
        "container_removed": before == after,
        "process_started": result.effects.process_started,
        "state": result.execution_state,
        "task_root_empty": task_root_empty,
    }


def classify_cases(cases: tuple[dict[str, Any], ...]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for case in cases:
        actual = run_exp_0016.classify_snippet(
            case["document_type"], case["snippet"]
        )
        results.append(
            {
                "case_id": case["case_id"],
                "context": actual["context"],
                "s3_action": run_exp_0016.strategy_action(
                    "strict_navigation_candidate",
                    actual["context"],
                    actual["scheme_group"],
                ),
                "scheme_group": actual["scheme_group"],
            }
        )
    return results


def parser_mismatches(
    cases: tuple[dict[str, Any], ...], classified: list[dict[str, str]]
) -> dict[str, int]:
    return {
        "context": sum(
            actual["context"] != case["expected_context"]
            for case, actual in zip(cases, classified, strict=True)
        ),
        "s3_action": sum(
            actual["s3_action"] != case["expected_s3_action"]
            for case, actual in zip(cases, classified, strict=True)
        ),
        "scheme_group": sum(
            actual["scheme_group"] != case["expected_scheme_group"]
            for case, actual in zip(cases, classified, strict=True)
        ),
    }


def prepare_materializations(
    cases: tuple[dict[str, Any], ...], authority: str
) -> tuple[dict[str, bytes], dict[str, Any]]:
    payloads: dict[str, bytes] = {}
    entry_counts: list[int] = []
    expanded_sizes: list[int] = []
    deterministic = True
    for case in cases:
        first = materialize_epub(case, authority)
        second = materialize_epub(case, authority)
        deterministic = deterministic and first == second
        payloads[case["case_id"]] = first
        inspected = inspect_materialized_epub(first)
        entry_counts.append(int(inspected["entry_count"]))
        expanded_sizes.append(int(inspected["expanded_bytes"]))
    digest_input = [sha256_bytes(payloads[case_id]) for case_id in SELECTED_CASES]
    return payloads, {
        "aggregate_sha256": sha256_bytes(canonical_bytes(digest_input)),
        "archive_entries_max": max(entry_counts),
        "deterministic": deterministic,
        "expanded_bytes_max": max(expanded_sizes),
        "max_bytes": max(len(value) for value in payloads.values()),
        "total_unique_bytes": sum(len(value) for value in payloads.values()),
    }


def _provider_projection(result: Any, snapshot: Snapshot) -> dict[str, Any]:
    codes = Counter(finding.code for finding in result.findings)
    if any(not PROVIDER_CODE.fullmatch(code) for code in codes):
        raise ExperimentError("provider code cannot be aggregated safely")
    if result.snapshot_sha256 != snapshot.sha256:
        raise ExperimentError("provider result snapshot binding differs")
    raw_size = len(result.raw_report) if result.raw_report is not None else 0
    return {
        "assessment": result.assessment,
        "cleanup_complete": result.effects.cleanup_complete,
        "codes": dict(sorted(codes.items())),
        "execution_state": result.execution_state,
        "input_unchanged": sha256_bytes(snapshot.data) == snapshot.sha256,
        "isolation_verified": "isolation.verified" in result.observations,
        "original_modified": result.effects.original_modified,
        "process_started": result.effects.process_started,
        "raw_report_bytes": raw_size,
    }


def run_provider_repetition(
    *,
    cases: tuple[dict[str, Any], ...],
    classified: list[dict[str, str]],
    authority: str,
    baseline_payloads: dict[str, bytes],
    provider: Any,
) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    for case, parser_result in zip(cases, classified, strict=True):
        payload = materialize_epub(case, authority)
        if payload != baseline_payloads[case["case_id"]]:
            raise ExperimentError("materialized EPUB changed between repetitions")
        snapshot = Snapshot(
            data=payload,
            size_bytes=len(payload),
            sha256=sha256_bytes(payload),
            suffix=".epub",
        )
        projection = _provider_projection(provider.inspect(snapshot), snapshot)
        outcomes.append(
            {
                "case_id": case["case_id"],
                "parser": {
                    "context": parser_result["context"],
                    "s3_action": parser_result["s3_action"],
                    "scheme_group": parser_result["scheme_group"],
                },
                "provider": projection,
            }
        )
    return outcomes


def summarize_repetition(index: int, outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    states: Counter[str] = Counter()
    assessments: Counter[str] = Counter()
    codes: Counter[str] = Counter()
    report_sizes: list[int] = []
    process_started = 0
    isolation_verified = 0
    cleanup_complete = 0
    for outcome in outcomes:
        provider = outcome["provider"]
        states[provider["execution_state"]] += 1
        assessments[provider["assessment"]] += 1
        codes.update(provider["codes"])
        report_sizes.append(provider["raw_report_bytes"])
        process_started += provider["process_started"] is True
        isolation_verified += provider["isolation_verified"] is True
        cleanup_complete += provider["cleanup_complete"] is True
    return {
        "assessments": dict(sorted(assessments.items())),
        "cleanup_complete": cleanup_complete,
        "execution_states": dict(sorted(states.items())),
        "isolation_verified": isolation_verified,
        "process_started": process_started,
        "provider_codes": dict(sorted(codes.items())),
        "raw_report_max_bytes": max(report_sizes, default=0),
        "raw_report_total_bytes": sum(report_sizes),
        "repetition": index,
    }


def semantic_repetition(outcomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove report-size noise while retaining parser and provider semantics."""

    return [
        {
            "case_id": outcome["case_id"],
            "parser": outcome["parser"],
            "provider": {
                key: value
                for key, value in outcome["provider"].items()
                if key != "raw_report_bytes"
            },
        }
        for outcome in outcomes
    ]


def _isolation_exact(isolation: dict[str, Any], deep: DeepRuntimeProfile) -> bool:
    expected_cap_drop = {
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_NET_BIND_SERVICE",
        "CAP_SETFCAP",
        "CAP_SETGID",
        "CAP_SETPCAP",
        "CAP_SETUID",
        "CAP_SYS_CHROOT",
    }
    return (
        set(isolation["cap_drop"]) == expected_cap_drop
        and isolation["command_exact"] is True
        and isolation["container_removed"] is True
        and isolation["cpu_nanos"] == 1_000_000_000
        and isolation["environment_exact"] is True
        and isolation["input_read_only"] is True
        and isolation["memory_bytes"] == deep.execution["memory_bytes"]
        and isolation["memory_swap_bytes"]
        == deep.execution["memory_swap_bytes"]
        and isolation["network"] == "none"
        and isolation["no_new_privileges"] is True
        and isolation["pids_limit"] == deep.execution["pids_limit"]
        and isolation["privileged"] is False
        and isolation["read_only_root"] is True
        and isolation["task_root_empty"] is True
        and isolation["tmpfs_exact"] is True
        and isolation["ulimits_exact"] is True
        and isolation["verified_by_executor"] is True
    )


def _result_bindings() -> dict[str, str]:
    return {
        "case_manifest_sha256": sha256_file(CASE_MANIFEST_PATH),
        "deep_profile_sha256": sha256_file(DEEP_PROFILE_PATH),
        "execution_profile_sha256": sha256_file(PROFILE_PATH),
        "exp0016_manifest_sha256": sha256_file(run_exp_0016.CASE_MANIFEST_PATH),
        "exp0016_runner_sha256": sha256_file(Path(run_exp_0016.__file__)),
        "product_tree_sha256": _product_tree_sha256(),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "runtime_bindings_sha256": _bindings_sha256(RUNTIME_LOCATORS),
    }


def _public_result_safe(result: dict[str, Any]) -> bool:
    payload = canonical_bytes(result)
    lowered = payload.lower()
    if len(payload) > MAX_RESULT_BYTES:
        return False
    if any(literal.lower() in lowered for literal in PRIVATE_OR_RAW_LITERALS):
        return False
    forbidden_keys = {
        "container_name",
        "host",
        "message",
        "payload",
        "port",
        "raw_report",
        "stderr",
        "stdout",
        "task_name",
        "url",
    }
    pending: list[Any] = [result]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if forbidden_keys.intersection(value):
                return False
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    return True


def build_result(
    *,
    preimage_commit: str,
    profile: dict[str, Any],
    cases: tuple[dict[str, Any], ...],
    mismatches: dict[str, int],
    repetitions: list[list[dict[str, Any]]],
    materialization: dict[str, Any],
    runtime: dict[str, Any],
    isolation: dict[str, Any],
    canary_control: int,
    canary_deep: int,
    timeout: dict[str, Any],
    output: dict[str, Any],
    cleanup: dict[str, bool],
    inputs_unchanged: bool,
    bound_files_unchanged: bool,
    green_preimage_ci_confirmed: bool,
) -> dict[str, Any]:
    deep = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
    summaries = [
        summarize_repetition(index, outcomes)
        for index, outcomes in enumerate(repetitions, start=1)
    ]
    identical = len(repetitions) == EXPECTED_REPETITIONS and all(
        canonical_bytes(semantic_repetition(value))
        == canonical_bytes(semantic_repetition(repetitions[0]))
        for value in repetitions[1:]
    )
    provider_complete = all(
        outcome["provider"]["execution_state"] == "completed"
        and outcome["provider"]["process_started"] is True
        and outcome["provider"]["isolation_verified"] is True
        and outcome["provider"]["cleanup_complete"] is True
        and outcome["provider"]["raw_report_bytes"] > 0
        for outcomes in repetitions
        for outcome in outcomes
    )
    group_counts = dict(sorted(Counter(case["group"] for case in cases).items()))
    effects = {
        "collection_modified": False,
        "deep_tool_execution": True,
        "domain_system_writes": False,
        "external_network_access": canary_deep > 0,
        "local_loopback_measurement": True,
        "persistence": False,
        "private_inputs": False,
        "product_code_modified": not bound_files_unchanged,
        "wi0004_gate_modified": False,
    }
    timeout_expected = {
        "assessment": "not_assessed",
        "container_removed": True,
        "process_started": True,
        "state": "timeout",
        "task_root_empty": True,
    }
    output_expected = {
        "attempted_bytes": 4 * 1024 * 1024,
        "bounded_bytes": deep.execution["tmpfs"]["/output"],
        "container_removed": True,
        "write_rejected": True,
    }
    acceptance = {
        "preimage_and_green_ci_bound": green_preimage_ci_confirmed
        and bool(preimage_commit),
        "runtime_and_dependencies_exact": runtime
        == {
            "client_version": "6.1.0",
            "deep_profile_id": deep.profile_id,
            "image_id_exact": True,
            "provider_id": "epubcheck",
            "provider_version": "5.3.0",
            "server_os_arch": "linux/amd64",
            "server_version": "6.1.0",
        },
        "exact_case_matrix": len(cases) == EXPECTED_CASE_COUNT
        and group_counts == {key: 4 for key in sorted(GROUP_CASES)},
        "deterministic_bounded_epubs": materialization["deterministic"] is True
        and materialization["archive_entries_max"] <= MAX_ARCHIVE_ENTRIES
        and materialization["expanded_bytes_max"] <= MAX_EXPANDED_BYTES
        and materialization["max_bytes"] <= MAX_EPUB_BYTES,
        "exp0016_oracles_match": all(value == 0 for value in mismatches.values()),
        "exact_repetitions_and_provider_runs": len(repetitions)
        == EXPECTED_REPETITIONS
        and sum(len(value) for value in repetitions) == EXPECTED_PROVIDER_RUNS,
        "provider_runs_complete_and_isolated": provider_complete,
        "repetitions_semantically_identical": identical,
        "parser_and_provider_evidence_separate": set(mismatches)
        == {"context", "s3_action", "scheme_group"}
        and all("provider_codes" in value for value in summaries),
        "canary_control_sensitive": canary_control == 1,
        "deep_path_canary_quiet": canary_deep == 0,
        "effective_isolation_exact": _isolation_exact(isolation, deep),
        "timeout_fails_closed_and_cleans": timeout == timeout_expected,
        "output_limit_rejects_and_cleans": output == output_expected,
        "inputs_unchanged_and_tasks_clean": inputs_unchanged
        and all(cleanup.values()),
        "result_private_raw_url_path_free": True,
        "forbidden_effects_absent": all(
            effects[key] is False
            for key in (
                "collection_modified",
                "domain_system_writes",
                "external_network_access",
                "persistence",
                "private_inputs",
                "product_code_modified",
                "wi0004_gate_modified",
            )
        ),
        "separate_result_gate_required": True,
    }
    result = {
        "acceptance": acceptance,
        "artifact": "EXP-0017",
        "bindings": _result_bindings(),
        "boundary_probes": {"output": output, "timeout": timeout},
        "canary": {
            "control_connections": canary_control,
            "deep_path_connections": canary_deep,
        },
        "case_count": len(cases),
        "cleanup": cleanup,
        "effects": effects,
        "group_counts": group_counts,
        "isolation": isolation,
        "materialization": materialization,
        "parser_oracle_mismatches": mismatches,
        "path_free": True,
        "preimage_commit": preimage_commit,
        "provider_repetitions": summaries,
        "provider_runs": sum(len(value) for value in repetitions),
        "repetitions": len(repetitions),
        "runs_semantically_identical": identical,
        "runtime": runtime,
        "schema": RESULT_SCHEMA,
        "status": "inconclusive",
    }
    if not _public_result_safe(result):
        raise ExperimentError("result violates its private path-free boundary")
    result["status"] = "pass" if all(acceptance.values()) else "inconclusive"
    return result


def validate_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    if set(result) != RESULT_FIELDS:
        raise ExperimentError("result fields differ")
    if result["schema"] != RESULT_SCHEMA or result["artifact"] != "EXP-0017":
        raise ExperimentError("result identity differs")
    if not re.fullmatch(r"[0-9a-f]{40}", result["preimage_commit"]):
        raise ExperimentError("result preimage differs")
    if (
        result["case_count"] != EXPECTED_CASE_COUNT
        or result["repetitions"] != EXPECTED_REPETITIONS
        or result["provider_runs"] != EXPECTED_PROVIDER_RUNS
    ):
        raise ExperimentError("result execution counts differ")
    if result["group_counts"] != {key: 4 for key in sorted(GROUP_CASES)}:
        raise ExperimentError("result group counts differ")
    if result["bindings"] != _result_bindings():
        raise ExperimentError("result bindings differ")
    expected_runtime = {
        "client_version": "6.1.0",
        "deep_profile_id": DeepRuntimeProfile.load(DEEP_PROFILE_PATH).profile_id,
        "image_id_exact": True,
        "provider_id": "epubcheck",
        "provider_version": "5.3.0",
        "server_os_arch": "linux/amd64",
        "server_version": "6.1.0",
    }
    if result["runtime"] != expected_runtime:
        raise ExperimentError("result runtime evidence differs")
    acceptance = result["acceptance"]
    if set(acceptance) != set(ACCEPTANCE_KEYS) or any(
        type(value) is not bool for value in acceptance.values()
    ):
        raise ExperimentError("result acceptance differs")
    expected_status = "pass" if all(acceptance.values()) else "inconclusive"
    if result["status"] != expected_status:
        raise ExperimentError("result status differs")
    if result["path_free"] is not True or not _public_result_safe(result):
        raise ExperimentError("result is not path-free and bounded")
    if result["runs_semantically_identical"] is not acceptance[
        "repetitions_semantically_identical"
    ]:
        raise ExperimentError("result repetition evidence differs")
    if set(result["parser_oracle_mismatches"]) != {
        "context",
        "s3_action",
        "scheme_group",
    } or any(
        type(value) is not int or value < 0 or value > EXPECTED_CASE_COUNT
        for value in result["parser_oracle_mismatches"].values()
    ):
        raise ExperimentError("result parser evidence differs")
    if not isinstance(result["provider_repetitions"], list) or len(
        result["provider_repetitions"]
    ) != EXPECTED_REPETITIONS:
        raise ExperimentError("result repetition aggregates differ")
    repetition_fields = {
        "assessments",
        "cleanup_complete",
        "execution_states",
        "isolation_verified",
        "process_started",
        "provider_codes",
        "raw_report_max_bytes",
        "raw_report_total_bytes",
        "repetition",
    }
    for index, repetition in enumerate(result["provider_repetitions"], start=1):
        if not isinstance(repetition, dict) or set(repetition) != repetition_fields:
            raise ExperimentError("result provider aggregate fields differ")
        if repetition["repetition"] != index:
            raise ExperimentError("result repetition index differs")
        for field in ("assessments", "execution_states", "provider_codes"):
            values = repetition[field]
            if not isinstance(values, dict) or any(
                not isinstance(key, str)
                or not PROVIDER_CODE.fullmatch(key)
                or type(value) is not int
                or value < 0
                for key, value in values.items()
            ):
                raise ExperimentError("result provider aggregate differs")
        if sum(repetition["execution_states"].values()) != EXPECTED_CASE_COUNT:
            raise ExperimentError("result provider state count differs")
        if sum(repetition["assessments"].values()) != EXPECTED_CASE_COUNT:
            raise ExperimentError("result provider assessment count differs")
        for field in ("cleanup_complete", "isolation_verified", "process_started"):
            if (
                type(repetition[field]) is not int
                or not 0 <= repetition[field] <= EXPECTED_CASE_COUNT
            ):
                raise ExperimentError("result provider boolean count differs")
        for field in ("raw_report_max_bytes", "raw_report_total_bytes"):
            if type(repetition[field]) is not int or repetition[field] < 0:
                raise ExperimentError("result provider report size differs")
    if set(result["canary"]) != {
        "control_connections",
        "deep_path_connections",
    } or any(type(value) is not int or value < 0 for value in result["canary"].values()):
        raise ExperimentError("result canary aggregate differs")
    if set(result["effects"]) != {
        "collection_modified",
        "deep_tool_execution",
        "domain_system_writes",
        "external_network_access",
        "local_loopback_measurement",
        "persistence",
        "private_inputs",
        "product_code_modified",
        "wi0004_gate_modified",
    } or any(
        type(value) is not bool for value in result["effects"].values()
    ):
        raise ExperimentError("result effects differ")
    if (
        result["effects"]["deep_tool_execution"] is not True
        or result["effects"]["local_loopback_measurement"] is not True
    ):
        raise ExperimentError("result permitted execution effects differ")
    if set(result["cleanup"]) != {
        "canary_closed",
        "containers_empty_after",
        "containers_empty_before",
        "isolation_container_removed",
        "isolation_task_root_empty",
        "outer_task_removed",
        "output_container_removed",
        "provider_task_root_empty",
        "timeout_container_removed",
        "timeout_task_root_empty",
    } or any(
        type(value) is not bool for value in result["cleanup"].values()
    ):
        raise ExperimentError("result cleanup aggregate differs")
    if set(result["materialization"]) != {
        "aggregate_sha256",
        "archive_entries_max",
        "deterministic",
        "expanded_bytes_max",
        "max_bytes",
        "total_unique_bytes",
    }:
        raise ExperimentError("result materialization fields differ")
    materialization = result["materialization"]
    if not re.fullmatch(r"[0-9a-f]{64}", materialization["aggregate_sha256"]):
        raise ExperimentError("result materialization binding differs")
    if materialization["deterministic"] is not True or any(
        type(materialization[field]) is not int or materialization[field] <= 0
        for field in (
            "archive_entries_max",
            "expanded_bytes_max",
            "max_bytes",
            "total_unique_bytes",
        )
    ):
        raise ExperimentError("result materialization aggregate differs")
    if set(result["boundary_probes"]) != {"output", "timeout"}:
        raise ExperimentError("result boundary probes differ")
    if set(result["boundary_probes"]["output"]) != {
        "attempted_bytes",
        "bounded_bytes",
        "container_removed",
        "write_rejected",
    } or set(result["boundary_probes"]["timeout"]) != {
        "assessment",
        "container_removed",
        "process_started",
        "state",
        "task_root_empty",
    }:
        raise ExperimentError("result boundary probe fields differ")
    if set(result["isolation"]) != {
        "cap_drop",
        "command_exact",
        "container_removed",
        "cpu_nanos",
        "environment_exact",
        "input_read_only",
        "memory_bytes",
        "memory_swap_bytes",
        "network",
        "no_new_privileges",
        "pids_limit",
        "privileged",
        "read_only_root",
        "task_root_empty",
        "tmpfs_exact",
        "ulimits_exact",
        "verified_by_executor",
    }:
        raise ExperimentError("result isolation fields differ")
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    return validate_result_dict(load_json(path))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _prepare_execution_paths(temp_root: Path, result_path: Path) -> tuple[Path, Path]:
    if os.name == "nt":
        resolved_temp = temp_root.resolve()
        resolved_result = result_path.resolve()
        allowed_temp = WINDOWS_TEMP_BASE.resolve()
        allowed_result = WINDOWS_ARTIFACT_BASE.resolve()
        if resolved_temp != allowed_temp and not _is_within(
            resolved_temp, allowed_temp
        ):
            raise ExperimentError("temp root is outside the EXP-0017 boundary")
        if not _is_within(resolved_result, allowed_result):
            raise ExperimentError("result is outside the EXP-0017 boundary")
    if result_path.exists():
        raise ExperimentError("result target already exists")
    temp_root.mkdir(parents=True, exist_ok=True)
    if list(temp_root.iterdir()):
        raise ExperimentError("EXP-0017 temp root is not empty")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    task_root = temp_root / f"task-{secrets.token_hex(12)}"
    task_root.mkdir(mode=0o700)
    return task_root, result_path


def _cleanup_owned_task(task_root: Path, temp_root: Path) -> bool:
    if (
        task_root.resolve().parent != temp_root.resolve()
        or not task_root.name.startswith("task-")
    ):
        raise ExperimentError("refusing to clean an unowned task root")

    def make_writable(function: Any, path: str, exc_info: Any) -> None:
        del exc_info
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        function(path)

    shutil.rmtree(task_root, onerror=make_writable)
    return not task_root.exists()


def _write_result_once(path: Path, result: dict[str, Any]) -> None:
    payload = canonical_bytes(result)
    if len(payload) > MAX_RESULT_BYTES:
        raise ExperimentError("result exceeds its output bound")
    with path.open("xb") as stream:
        stream.write(payload)


def execute(
    *,
    temp_root: Path,
    result_path: Path,
    green_preimage_ci_confirmed: bool,
    preimage_commit: str | None = None,
) -> dict[str, Any]:
    if not green_preimage_ci_confirmed:
        raise ExperimentError("green preimage CI confirmation is required")
    profile, cases = load_contract()
    commit = preimage_commit or require_committed_preimage()
    deep = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
    before_bindings = _bindings(RUNTIME_LOCATORS)
    runtime = runtime_preflight(deep)
    containers_before = _container_names()
    if containers_before:
        raise ExperimentError("pre-existing WI-0005 containers make cleanup ambiguous")
    task_root, output_path = _prepare_execution_paths(temp_root, result_path)

    canary: LoopbackCanary | None = None
    canary_closed = False
    outer_task_removed = False
    repetitions: list[list[dict[str, Any]]] = []
    try:
        canary = LoopbackCanary()
        control_connections = canary.prove_and_reset()
        classified = classify_cases(cases)
        mismatches = parser_mismatches(cases, classified)
        baseline_payloads, materialization = prepare_materializations(
            cases, canary.authority
        )
        first_payload = baseline_payloads[SELECTED_CASES[0]]
        first_snapshot = Snapshot(
            data=first_payload,
            size_bytes=len(first_payload),
            sha256=sha256_bytes(first_payload),
            suffix=".epub",
        )
        isolation_root = task_root / "isolation"
        isolation = isolation_prestart(deep, isolation_root, first_snapshot)
        isolation = _finalize_isolation_probe(isolation, isolation_root)

        provider_root = task_root / "provider"
        provider = EpubCheckProvider(profile=deep, temp_root=provider_root)
        repetitions = [
            run_provider_repetition(
                cases=cases,
                classified=classified,
                authority=canary.authority,
                baseline_payloads=baseline_payloads,
                provider=provider,
            )
            for _ in range(profile["repetitions"])
        ]
        provider_root_empty = provider_root.is_dir() and not list(
            provider_root.iterdir()
        )
        timed = timeout_probe(deep, task_root / "timeout", first_snapshot)
        output = output_limit_probe(deep)
        time.sleep(0.2)
        deep_connections = canary.count
        canary_closed = canary.close()
        canary = None
        inputs_unchanged = all(
            outcome["provider"]["input_unchanged"] is True
            and outcome["provider"]["original_modified"] is False
            for values in repetitions
            for outcome in values
        )
    finally:
        if canary is not None:
            canary_closed = canary.close()
        outer_task_removed = _cleanup_owned_task(task_root, temp_root)

    containers_after = _container_names()
    if containers_after:
        raise ExperimentError("EXP-0017 container cleanup is incomplete")
    after_bindings = _bindings(RUNTIME_LOCATORS)
    cleanup = {
        "canary_closed": canary_closed,
        "containers_empty_after": not containers_after,
        "containers_empty_before": not containers_before,
        "isolation_container_removed": isolation["container_removed"],
        "isolation_task_root_empty": isolation["task_root_empty"],
        "outer_task_removed": outer_task_removed,
        "output_container_removed": output["container_removed"],
        "provider_task_root_empty": provider_root_empty,
        "timeout_container_removed": timed["container_removed"],
        "timeout_task_root_empty": timed["task_root_empty"],
    }
    result = build_result(
        preimage_commit=commit,
        profile=profile,
        cases=cases,
        mismatches=mismatches,
        repetitions=repetitions,
        materialization=materialization,
        runtime=runtime,
        isolation=isolation,
        canary_control=control_connections,
        canary_deep=deep_connections,
        timeout=timed,
        output=output,
        cleanup=cleanup,
        inputs_unchanged=inputs_unchanged,
        bound_files_unchanged=before_bindings == after_bindings,
        green_preimage_ci_confirmed=green_preimage_ci_confirmed,
    )
    validate_result_dict(result)
    _write_result_once(output_path, result)
    return result


def parser() -> SafeArgumentParser:
    result = SafeArgumentParser(description=__doc__)
    mode = result.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-profile", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--validate-result", action="store_true")
    result.add_argument("--temp-root", type=Path)
    result.add_argument("--result", type=Path, default=RESULT_PATH)
    result.add_argument("--confirm-green-preimage-ci", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        if args.validate_profile:
            profile, cases = load_contract()
            commit = require_committed_preimage()
            print(
                "EXP-0017 profile valid: "
                f"preimage={commit} cases={len(cases)} "
                f"repetitions={profile['repetitions']}"
            )
            return 0
        if args.validate_result:
            result = validate_result(args.result)
            print(
                "EXP-0017 result valid: "
                f"preimage={result['preimage_commit']} "
                f"provider_runs={result['provider_runs']} status={result['status']}"
            )
            return 0
        if args.temp_root is None:
            raise ExperimentError("EXP-0017 execution requires --temp-root")
        result = execute(
            temp_root=args.temp_root,
            result_path=args.result,
            green_preimage_ci_confirmed=args.confirm_green_preimage_ci,
        )
        print(
            "EXP-0017 executed: "
            f"cases={result['case_count']} repetitions={result['repetitions']} "
            f"provider_runs={result['provider_runs']} status={result['status']}"
        )
        return 0 if result["status"] == "pass" else 4
    except KeyboardInterrupt:
        return 130
    except (ExperimentError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"EXP-0017 failed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
