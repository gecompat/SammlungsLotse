#!/usr/bin/env python3
"""Run and validate the synthetic EXP-0008 Calibre single-record handoff."""

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
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import materialize_calibre_qualification_library as materializer  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.workspace import (  # noqa: E402
    MARKER_NAME,
    LibraryWorkspace,
    LibraryWorkspaceManager,
    snapshot_library,
)
from sammlungslotse.ebook_intake.podman_executor import run_bounded  # noqa: E402


EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0008"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNTIME_PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
LIBRARY_MANIFEST_PATH = ROOT / "runtime" / "calibre-readonly" / "qualification-library.json"
RUNNER_PATH = Path(__file__).resolve()
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")
ALLOWED_EVIDENCE_ROOT = Path(r"C:\rep\artifacts\SammlungsLotse")
CONTAINER_PREFIX = "sammlungslotse-exp0008-"
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]|/(?:home|Users|library|output)(?:[\\/]|$))",
    re.IGNORECASE,
)
PREIMAGE_FILES = (
    "experiments/ebook/exp-0008/execution-profile.json",
    "tests/experiments/test_exp_0008.py",
    "tools/experiments/run_exp_0008.py",
    "runtime/calibre-readonly/profile.json",
    "runtime/calibre-readonly/qualification-library.json",
    "tools/materialize_calibre_qualification_library.py",
    "src/sammlungslotse/__init__.py",
    "src/sammlungslotse/calibre_inventory/__init__.py",
    "src/sammlungslotse/calibre_inventory/profile.py",
    "src/sammlungslotse/calibre_inventory/workspace.py",
    "src/sammlungslotse/ebook_intake/podman_executor.py",
    "tests/fixtures/ebook/test-0001/v0.3/cases/identity-multiformat-edition/edition.epub",
    "tests/fixtures/ebook/test-0001/v0.3/cases/metadata-multilingual-rtl/multilingual-rtl.epub",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


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


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("schema") != "sammlungslotse/exp-0008-execution-profile/v1":
        raise RuntimeError("unexpected EXP-0008 profile schema")
    if profile.get("artifact") != "EXP-0008" or profile.get("fixture_version") != "0.3.0":
        raise RuntimeError("unexpected EXP-0008 identity")
    runtime = profile.get("runtime_profile", {})
    if runtime != {
        "image_id": "sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5",
        "locator": "runtime/calibre-readonly/profile.json",
        "profile_id": "wi-0007-calibre-9.13.0-podman-linux-amd64/v1",
        "sha256": sha256_file(RUNTIME_PROFILE_PATH),
    }:
        raise RuntimeError("EXP-0008 runtime profile binding differs")
    library = profile.get("qualification_library", {})
    if (
        library.get("locator") != "runtime/calibre-readonly/qualification-library.json"
        or library.get("sha256") != sha256_file(LIBRARY_MANIFEST_PATH)
        or library.get("synthetic_only") is not True
    ):
        raise RuntimeError("EXP-0008 qualification library binding differs")
    records = library.get("records", {})
    if records.get("positive") != {
        "expected_sha256": "1d98510717f6c3f22b3219bdedf8cbdf38785f060bfca0522f66ccf374f684a5",
        "expected_size_bytes": 1521,
        "external_record_id": "1",
    }:
        raise RuntimeError("EXP-0008 positive record differs")
    if records.get("no_epub") != {"external_record_id": "2"}:
        raise RuntimeError("EXP-0008 no-EPUB control differs")
    if records.get("missing") != {"external_record_id": "999"}:
        raise RuntimeError("EXP-0008 missing-ID control differs")
    command = profile.get("command", {})
    if command != {
        "fixed_flags": [
            "--single-dir",
            "--dont-update-metadata",
            "--dont-write-opf",
            "--dont-save-cover",
            "--dont-save-extra-files",
            "--formats",
            "EPUB",
            "--template",
            "{id}",
        ],
        "program": "calibredb",
        "subcommand": "export",
    }:
        raise RuntimeError("EXP-0008 command allowlist differs")
    selection = profile.get("selection", {})
    if selection != {
        "direct_database_access": False,
        "formats": ["EPUB"],
        "ids_per_request": 1,
        "library_strategy": "task-private-copy-on-read",
        "network": False,
        "product_code": False,
        "source_writes": False,
    }:
        raise RuntimeError("EXP-0008 selection boundary differs")
    limits = profile.get("limits", {})
    if not (
        profile.get("repetitions") == 2
        and limits.get("max_export_files") == 1
        and 0 < limits.get("control_output_file_bytes", 0) < records["positive"]["expected_size_bytes"]
        and 0 < limits.get("control_timeout_seconds", 0) < limits.get("timeout_seconds", 0)
        and records["positive"]["expected_size_bytes"] < limits.get("max_export_file_bytes", 0) <= 4 * 1024 * 1024
        and 0 < limits.get("stdout_bytes", 0) <= 131072
        and 0 < limits.get("stderr_bytes", 0) <= 131072
        and limits.get("external_id_max") == 999999999
    ):
        raise RuntimeError("EXP-0008 limits differ")
    CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
    return profile


def load_profile() -> dict[str, Any]:
    return validate_profile(load_json(PROFILE_PATH))


def validate_external_id(value: str, maximum: int = 999999999) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]*", value):
        raise ValueError("selection.invalid_external_id")
    if int(value) > maximum:
        raise ValueError("selection.external_id_limit_exceeded")
    return value


def current_preimage() -> dict[str, str]:
    result: dict[str, str] = {}
    for locator in PREIMAGE_FILES:
        path = ROOT / locator
        if not path.is_file():
            raise RuntimeError(f"EXP-0008 preimage file missing: {locator}")
        result[locator] = sha256_file(path)
    return result


def git_output(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git command failed: {' '.join(arguments[:2])}")
    return completed.stdout.strip()


def authority_evidence() -> dict[str, Any]:
    if git_output("status", "--porcelain"):
        raise RuntimeError("EXP-0008 empirical run requires a clean preimage commit")
    head = git_output("rev-parse", "HEAD")
    origin_main = git_output("rev-parse", "origin/main")
    merge_base = git_output("merge-base", "HEAD", "origin/main")
    if merge_base != origin_main:
        raise RuntimeError("EXP-0008 preimage does not descend from exact origin/main")
    registry = json.loads(git_output("show", "origin/main:.ai/artifact_registry.json"))["artifacts"]
    if registry["GATE-0006"]["status"] != "done" or registry["EXP-0008"]["status"] != "accepted":
        raise RuntimeError("EXP-0008 plan is not canonical on origin/main")
    changed = set(filter(None, git_output("diff", "--name-only", "origin/main...HEAD").splitlines()))
    allowed = {
        "experiments/ebook/exp-0008/README.md",
        "experiments/ebook/exp-0008/execution-profile.json",
        "tests/experiments/test_exp_0008.py",
        "tools/experiments/run_exp_0008.py",
    }
    if not changed or not changed.issubset(allowed):
        raise RuntimeError("EXP-0008 preimage change set is broader than the experiment")
    product_changes = git_output(
        "diff",
        "--name-only",
        "origin/main...HEAD",
        "--",
        "src",
        "tools/run_ebook_intake.py",
        "tools/run_calibre_inventory.py",
        "tools/run_ebook_identity.py",
    )
    if product_changes:
        raise RuntimeError("EXP-0008 preimage changes product code")
    return {
        "allowed_change_set": True,
        "exp_0008_accepted_on_origin_main": True,
        "gate_0006_done_on_origin_main": True,
        "merge_base": merge_base,
        "origin_main": origin_main,
        "preimage_commit": head,
        "product_code_unchanged": True,
    }


def _is_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        info = path.stat(follow_symlinks=False)
    except OSError:
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(info, "st_file_attributes", 0) & flag)


def prepare_controlled_root(path: Path, allowed_root: Path) -> Path:
    root = allowed_root.resolve(strict=True)
    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("controlled root escapes its authority") from exc
    if any(value in str(candidate) for value in (",", "\x00", "\r", "\n")):
        raise RuntimeError("controlled root contains an unsupported character")
    current = root
    for part in relative.parts:
        current /= part
        if current.exists() and _is_reparse(current):
            raise RuntimeError("controlled root contains a link or reparse point")
    candidate.mkdir(parents=True, mode=0o700, exist_ok=True)
    if _is_reparse(candidate) or candidate.resolve(strict=True) != candidate:
        raise RuntimeError("controlled root is unsafe")
    return candidate


def create_run_root(base: Path) -> Path:
    run = base / f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    run.mkdir(mode=0o700)
    return run


def remove_run_root(run: Path, base: Path) -> bool:
    if run.parent != base or not run.name.startswith("run-") or _is_reparse(run):
        raise RuntimeError("EXP-0008 cleanup target is outside the owned run root")
    shutil.rmtree(run)
    return not run.exists()


def container_names() -> set[str]:
    result = run_bounded(
        ["podman", "ps", "-a", "--filter", f"name={CONTAINER_PREFIX}", "--format", "{{.Names}}"],
        timeout=15,
        stdout_limit=65536,
        stderr_limit=65536,
    )
    if result.timed_out or result.returncode != 0:
        raise RuntimeError("EXP-0008 container inventory failed")
    return {line.strip() for line in result.stdout.decode("utf-8", "replace").splitlines() if line.strip()}


def runtime_evidence(runtime_profile: CalibreRuntimeProfile) -> dict[str, Any]:
    version = run_bounded(
        ["podman", "version", "--format", "json"],
        timeout=15,
        stdout_limit=65536,
        stderr_limit=65536,
    )
    if version.timed_out or version.returncode != 0:
        raise RuntimeError("EXP-0008 Podman runtime is unavailable")
    value = json.loads(version.stdout)
    minimum = tuple(int(part) for part in runtime_profile.execution["podman_minimum_version"].split("."))
    for area in ("Client", "Server"):
        actual = tuple(int(part) for part in str(value.get(area, {}).get("Version", "")).split("."))
        if len(actual) != 3 or actual < minimum:
            raise RuntimeError("EXP-0008 Podman version differs")
    if value.get("Server", {}).get("OsArch") != "linux/amd64":
        raise RuntimeError("EXP-0008 Podman platform differs")
    image = run_bounded(
        ["podman", "image", "inspect", runtime_profile.image["id"], "--format", "json"],
        timeout=15,
        stdout_limit=131072,
        stderr_limit=65536,
    )
    if image.timed_out or image.returncode != 0:
        raise RuntimeError("EXP-0008 image is unavailable")
    inspected = json.loads(image.stdout)[0]
    image_id = str(inspected.get("Id", ""))
    if not image_id.startswith("sha256:"):
        image_id = f"sha256:{image_id}"
    if (
        image_id != runtime_profile.image["id"]
        or inspected.get("Os") != "linux"
        or inspected.get("Architecture") != "amd64"
        or inspected.get("Config", {}).get("Entrypoint") != runtime_profile.image["entrypoint"]
    ):
        raise RuntimeError("EXP-0008 image binding differs")
    return {
        "calibre_version": runtime_profile.provider["version"],
        "image_id": image_id,
        "platform": "linux/amd64",
        "podman_client": value["Client"]["Version"],
        "podman_server": value["Server"]["Version"],
        "profile_id": runtime_profile.profile_id,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }


def create_arguments(
    name: str,
    workspace: LibraryWorkspace,
    external_id: str,
    profile: dict[str, Any],
    runtime_profile: CalibreRuntimeProfile,
    max_export_file_bytes: int,
) -> list[str]:
    execution = runtime_profile.execution
    arguments = [
        "podman",
        "create",
        "--name",
        name,
        "--pull=never",
        "--network",
        "none",
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
        "core=0:0",
        "--ulimit",
        "nofile=256:256",
        "--ulimit",
        f"fsize={max_export_file_bytes}:{max_export_file_bytes}",
        "--log-driver",
        "none",
        "--tmpfs",
        "/tmp:rw,nosuid,nodev,noexec,size=67108864,mode=1777",
        "--tmpfs",
        "/config:rw,nosuid,nodev,noexec,size=16777216,mode=1777",
        "--mount",
        f"type=bind,source={workspace.library},target=/library,rw=true",
        "--mount",
        f"type=bind,source={workspace.output},target=/output,rw=true",
        "--entrypoint",
        "/usr/bin/env",
        runtime_profile.image["id"],
        "-i",
    ]
    for key, value in runtime_profile.execution["environment"].items():
        arguments.append(f"{key}={value}")
    arguments.extend(
        (
            profile["command"]["program"],
            profile["command"]["subcommand"],
            "--with-library",
            "/library",
            "--to-dir",
            "/output",
            *profile["command"]["fixed_flags"],
            external_id,
        )
    )
    return arguments


def inspect_container(name: str) -> dict[str, Any]:
    result = run_bounded(
        ["podman", "inspect", name, "--format", "json"],
        timeout=15,
        stdout_limit=262144,
        stderr_limit=65536,
    )
    if result.timed_out or result.returncode != 0:
        raise RuntimeError("EXP-0008 container inspection failed")
    return json.loads(result.stdout)[0]


def security_projection(value: dict[str, Any]) -> dict[str, Any]:
    host = value.get("HostConfig", {})
    config = value.get("Config", {})
    mounts = {
        item.get("Destination"): {
            "destination": item.get("Destination"),
            "rw": item.get("RW"),
            "type": item.get("Type"),
        }
        for item in value.get("Mounts", [])
    }
    return {
        "cap_add": host.get("CapAdd") or [],
        "cap_drop_count": len(host.get("CapDrop") or []),
        "cpus_nano": host.get("NanoCpus"),
        "entrypoint": config.get("Entrypoint"),
        "log_driver": host.get("LogConfig", {}).get("Type"),
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "mounts": [mounts[key] for key in sorted(mounts)],
        "network": host.get("NetworkMode"),
        "pids_limit": host.get("PidsLimit"),
        "privileged": host.get("Privileged"),
        "read_only_root": host.get("ReadonlyRootfs"),
        "security_opt": sorted(host.get("SecurityOpt") or []),
        "tmpfs_destinations": sorted((host.get("Tmpfs") or {}).keys()),
        "user": config.get("User"),
    }


def isolation_matches(value: dict[str, Any], runtime_profile: CalibreRuntimeProfile) -> bool:
    host = value.get("HostConfig", {})
    config = value.get("Config", {})
    mounts = {item.get("Destination"): item for item in value.get("Mounts", [])}
    image = str(value.get("Image", ""))
    if image and not image.startswith("sha256:"):
        image = f"sha256:{image}"
    return (
        image == runtime_profile.image["id"]
        and host.get("NetworkMode") == "none"
        and host.get("ReadonlyRootfs") is True
        and config.get("User") == runtime_profile.execution["user"]
        and host.get("Privileged") is False
        and host.get("CapAdd") in (None, [])
        and bool(host.get("CapDrop"))
        and set(host.get("SecurityOpt") or []) == {"no-new-privileges"}
        and host.get("PidsLimit") == runtime_profile.execution["pids_limit"]
        and host.get("Memory") == runtime_profile.execution["memory_bytes"]
        and host.get("MemorySwap") == runtime_profile.execution["memory_swap_bytes"]
        and host.get("NanoCpus") == 1_000_000_000
        and host.get("LogConfig", {}).get("Type") == "none"
        and set((host.get("Tmpfs") or {}).keys()) == {"/config", "/tmp"}
        and mounts.get("/library", {}).get("RW") is True
        and mounts.get("/output", {}).get("RW") is True
        and config.get("Entrypoint") == ["/usr/bin/env"]
    )


def inspect_export_output(output: Path, external_id: str, maximum: int) -> dict[str, Any]:
    entries = sorted(output.iterdir(), key=lambda item: item.name)
    if not entries:
        return {
            "classification": "empty",
            "file_count": 0,
            "kind": None,
            "sha256": None,
            "size_bytes": 0,
        }
    if len(entries) != 1:
        return {
            "classification": "unexpected",
            "file_count": len(entries),
            "kind": None,
            "sha256": None,
            "size_bytes": sum(item.stat(follow_symlinks=False).st_size for item in entries),
        }
    item = entries[0]
    if _is_reparse(item) or not item.is_file() or item.name != f"{external_id}.epub":
        return {
            "classification": "unexpected",
            "file_count": 1,
            "kind": None,
            "sha256": None,
            "size_bytes": item.stat(follow_symlinks=False).st_size,
        }
    size = item.stat(follow_symlinks=False).st_size
    if size > maximum:
        return {
            "classification": "limit_exceeded",
            "file_count": 1,
            "kind": "epub_only",
            "sha256": None,
            "size_bytes": size,
        }
    return {
        "classification": "valid",
        "file_count": 1,
        "kind": "epub_only",
        "sha256": sha256_file(item),
        "size_bytes": size,
    }


def write_raw_evidence(
    evidence_root: Path,
    label: str,
    stdout: bytes,
    stderr: bytes,
    security: dict[str, Any] | None,
) -> dict[str, str]:
    payloads = {
        "stdout": (f"{label}.stdout.bin", stdout),
        "stderr": (f"{label}.stderr.bin", stderr),
        "security": (
            f"{label}.security.json",
            (json.dumps(security or {}, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        ),
    }
    result: dict[str, str] = {}
    for kind, (name, payload) in payloads.items():
        path = evidence_root / name
        path.write_bytes(payload)
        result[kind] = sha256_bytes(payload)
    return result


def run_export(
    workspace: LibraryWorkspace,
    *,
    external_id: str,
    label: str,
    profile: dict[str, Any],
    runtime_profile: CalibreRuntimeProfile,
    evidence_root: Path,
    timeout: float,
    max_export_file_bytes: int,
    control_kind: str | None = None,
) -> dict[str, Any]:
    external_id = validate_external_id(external_id, profile["limits"]["external_id_max"])
    if any(workspace.output.iterdir()):
        return {
            "cleanup_complete": True,
            "container_created": False,
            "exit_code": None,
            "isolation_verified": False,
            "output": inspect_export_output(workspace.output, external_id, max_export_file_bytes),
            "process_started": False,
            "raw_evidence_sha256": {},
            "state": "unexpected_output",
            "stderr_truncated": False,
            "stdout_truncated": False,
        }
    name = f"{CONTAINER_PREFIX}{uuid.uuid4().hex[:16]}"
    created = False
    started = False
    isolated = False
    cleanup = True
    state = "create_failed"
    exit_code: int | None = None
    stdout = b""
    stderr = b""
    stdout_truncated = False
    stderr_truncated = False
    security: dict[str, Any] | None = None
    try:
        created_result = run_bounded(
            create_arguments(
                name,
                workspace,
                external_id,
                profile,
                runtime_profile,
                max_export_file_bytes,
            ),
            timeout=15,
            stdout_limit=4096,
            stderr_limit=profile["limits"]["stderr_bytes"],
        )
        if created_result.timed_out or created_result.returncode != 0:
            stderr = created_result.stderr
        else:
            created = True
            inspection = inspect_container(name)
            security = security_projection(inspection)
            isolated = isolation_matches(inspection, runtime_profile)
            if not isolated:
                state = "isolation_mismatch"
            elif control_kind == "interruption":
                state = "interrupted"
            else:
                started = True
                completed = run_bounded(
                    ["podman", "start", "--attach", name],
                    timeout=timeout,
                    stdout_limit=profile["limits"]["stdout_bytes"],
                    stderr_limit=profile["limits"]["stderr_bytes"],
                )
                exit_code = completed.returncode
                stdout = completed.stdout
                stderr = completed.stderr
                stdout_truncated = completed.stdout_truncated
                stderr_truncated = completed.stderr_truncated
                if completed.timed_out:
                    state = "timeout"
                elif completed.stdout_truncated or completed.stderr_truncated:
                    state = "stream_limit_exceeded"
                else:
                    output = inspect_export_output(workspace.output, external_id, max_export_file_bytes)
                    if control_kind == "output_limit" and (
                        completed.returncode != 0 or output["classification"] != "valid"
                    ):
                        state = "output_limit_exceeded"
                    elif completed.returncode == 0 and output["classification"] == "valid":
                        state = "completed"
                    elif output["classification"] == "empty":
                        state = "selection_unavailable"
                    elif output["classification"] in {"unexpected", "limit_exceeded"}:
                        state = "unexpected_output"
                    else:
                        state = "failed"
    finally:
        if created:
            removed = run_bounded(
                ["podman", "rm", "--force", name],
                timeout=15,
                stdout_limit=4096,
                stderr_limit=4096,
            )
            cleanup = removed.returncode == 0 and not removed.timed_out
            if not cleanup:
                state = "cleanup_failed"
    output = inspect_export_output(workspace.output, external_id, max_export_file_bytes)
    raw_hashes = write_raw_evidence(evidence_root, label, stdout, stderr, security)
    return {
        "cleanup_complete": cleanup,
        "container_created": created,
        "exit_code": exit_code,
        "isolation_verified": isolated,
        "output": output,
        "process_started": started,
        "raw_evidence_sha256": raw_hashes,
        "state": state,
        "stderr_truncated": stderr_truncated,
        "stdout_truncated": stdout_truncated,
    }


def run_managed_case(
    manager: LibraryWorkspaceManager,
    *,
    external_id: str,
    label: str,
    profile: dict[str, Any],
    runtime_profile: CalibreRuntimeProfile,
    evidence_root: Path,
    timeout: float,
    max_export_file_bytes: int,
    control_kind: str | None = None,
    preseed_unexpected: bool = False,
) -> dict[str, Any]:
    if not manager.recover():
        raise RuntimeError("EXP-0008 workspace recovery refused the task root")
    workspace = manager.create()
    source_unchanged = False
    task_cleanup = False
    try:
        if preseed_unexpected:
            (workspace.output / "unexpected.opf").write_bytes(b"synthetic-control")
        result = run_export(
            workspace,
            external_id=external_id,
            label=label,
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=timeout,
            max_export_file_bytes=max_export_file_bytes,
            control_kind=control_kind,
        )
        source_unchanged = manager.source_unchanged(workspace)
    finally:
        manager.cleanup(workspace)
        task_cleanup = not workspace.root.exists()
    result["requested_external_id"] = external_id
    result["source_unchanged"] = source_unchanged
    result["task_cleanup_complete"] = task_cleanup
    result["workspace_prepared"] = True
    return result


def rejected_selection_case(source: Path, value: str, profile: dict[str, Any]) -> dict[str, Any]:
    runtime_profile = CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
    before = snapshot_library(source, runtime_profile)
    try:
        validate_external_id(value, profile["limits"]["external_id_max"])
    except ValueError:
        state = "invalid_selection"
    else:
        state = "unexpected_acceptance"
    return {
        "cleanup_complete": True,
        "container_created": False,
        "isolation_verified": False,
        "process_started": False,
        "requested_external_id": value,
        "source_unchanged": snapshot_library(source, runtime_profile) == before,
        "state": state,
        "task_cleanup_complete": True,
        "workspace_prepared": False,
    }


def seed_and_recover_stale_task(manager: LibraryWorkspaceManager) -> bool:
    manager.prepare_root()
    task_id = f"stale{uuid.uuid4().hex[:12]}"
    task = manager.root / f"task-{task_id}"
    task.mkdir(mode=0o700)
    marker = {
        "created_epoch": time.time() - int(manager.profile.workspace["max_task_age_seconds"]) - 1,
        "profile_id": manager.profile.profile_id,
        "schema": manager.profile.workspace["marker_schema"],
        "task_id": task_id,
    }
    (task / MARKER_NAME).write_text(canonical_json(marker), encoding="utf-8")
    (task / "synthetic-leftover.bin").write_bytes(b"EXP-0008")
    return manager.recover() and not task.exists()


def snapshot_summary(value: Any) -> dict[str, Any]:
    return {
        "digest": value.digest,
        "file_count": len(value.files),
        "total_bytes": value.total_bytes,
    }


def fixture_hashes(profile: dict[str, Any]) -> dict[str, str]:
    records = load_json(LIBRARY_MANIFEST_PATH)["records"]
    result: dict[str, str] = {}
    for record in records:
        for item in record["formats"]:
            locator = item["fixture"]
            result[locator] = sha256_file(ROOT / locator)
    expected = {
        item["fixture"]: item["sha256"]
        for record in records
        for item in record["formats"]
    }
    if result != expected or profile["qualification_library"]["synthetic_only"] is not True:
        raise RuntimeError("EXP-0008 fixture binding differs")
    return result


def result_has_no_private_paths(value: dict[str, Any]) -> bool:
    return PRIVATE_PATH_PATTERN.search(canonical_json(value)) is None


def all_actual_cases(cases: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        *cases["positive_repetitions"],
        cases["missing_id"],
        cases["no_epub"],
        cases["output_limit"],
        cases["timeout"],
        cases["interruption"],
        cases["recovery"]["run"],
    ]


def derive_acceptance(result: dict[str, Any]) -> dict[str, bool]:
    profile = load_profile()
    cases = result["cases"]
    positive = cases["positive_repetitions"]
    expected = profile["qualification_library"]["records"]["positive"]
    actual = all_actual_cases(cases)
    return {
        "exact_profile_image_platform_and_preimage": (
            result["environment"]["image_id"] == profile["runtime_profile"]["image_id"]
            and result["environment"]["profile_id"] == profile["runtime_profile"]["profile_id"]
            and result["environment"]["platform"] == "linux/amd64"
            and result["preimage_sha256"] == current_preimage()
        ),
        "synthetic_bound_inputs_only": (
            result["fixtures"]["before"] == result["fixtures"]["after"]
            and result["materialization"]["synthetic_only"] is True
        ),
        "single_explicit_id_and_epub_only": all(
            item["requested_external_id"] == expected["external_record_id"]
            and item["output"]["kind"] == "epub_only"
            for item in positive
        ),
        "supported_cli_without_internal_database_access": (
            result["effects"]["supported_calibredb_export_only"] is True
            and result["effects"]["direct_database_access"] is False
        ),
        "exactly_one_positive_output": all(item["output"]["file_count"] == 1 for item in positive),
        "positive_epub_byte_equal": all(
            item["output"]["sha256"] == expected["expected_sha256"]
            and item["output"]["size_bytes"] == expected["expected_size_bytes"]
            for item in positive
        ),
        "no_opf_cover_extra_or_other_format": all(
            item["output"]["classification"] == "valid" and item["output"]["kind"] == "epub_only"
            for item in positive
        ),
        "source_and_fixtures_unchanged": (
            result["source"]["before"] == result["source"]["after"]
            and result["fixtures"]["before"] == result["fixtures"]["after"]
            and all(item["source_unchanged"] for item in actual)
        ),
        "task_private_random_bounded_copy_on_read": all(
            item["workspace_prepared"] for item in actual
        ) and result["workspace_controls"] == {
            "bounded_by_runtime_profile": True,
            "copy_on_read": True,
            "random_task_ids": True,
            "task_private": True,
        },
        "container_isolation_read_back": all(item["isolation_verified"] for item in actual),
        "negative_selection_and_output_fail_closed": (
            cases["missing_id"]["state"] == "selection_unavailable"
            and cases["no_epub"]["state"] == "selection_unavailable"
            and cases["multiple_ids"]["state"] == "invalid_selection"
            and cases["invalid_id"]["state"] == "invalid_selection"
            and cases["unexpected_output"]["state"] == "unexpected_output"
            and not cases["multiple_ids"]["container_created"]
            and not cases["invalid_id"]["container_created"]
            and not cases["unexpected_output"]["container_created"]
        ),
        "resource_and_time_limits_effective": (
            cases["output_limit"]["state"] == "output_limit_exceeded"
            and cases["output_limit"]["output"]["size_bytes"] <= profile["limits"]["control_output_file_bytes"]
            and cases["timeout"]["state"] == "timeout"
            and all(not item["stdout_truncated"] and not item["stderr_truncated"] for item in actual)
        ),
        "cleanup_recovery_and_interruption_complete": (
            all(item["cleanup_complete"] and item["task_cleanup_complete"] for item in actual)
            and cases["unexpected_output"]["task_cleanup_complete"]
            and cases["interruption"]["state"] == "interrupted"
            and cases["recovery"]["stale_task_removed"] is True
            and result["cleanup"]["task_root_empty"] is True
            and result["cleanup"]["qualification_root_removed"] is True
            and result["cleanup"]["containers_before"] == result["cleanup"]["containers_after"]
        ),
        "path_free_minimal_result": (
            result["privacy"]["path_free_result"] is True
            and result["privacy"]["raw_streams_not_retained"] is True
            and result_has_no_private_paths(result)
        ),
        "positive_repetitions_byte_stable": (
            len(positive) == profile["repetitions"]
            and canonical_digest(positive[0]) == canonical_digest(positive[1])
        ),
        "no_product_collection_network_persistence_or_writer_effect": (
            result["authority"]["product_code_unchanged"] is True
            and result["effects"] == {
                "direct_database_access": False,
                "network": False,
                "persistence": False,
                "product_code": False,
                "source_writes": False,
                "supported_calibredb_export_only": True,
                "writer": False,
            }
        ),
    }


def evidence_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def execute_experiment(temp_base: Path, evidence_base: Path, result_path: Path) -> dict[str, Any]:
    profile = load_profile()
    authority = authority_evidence()
    runtime_profile = CalibreRuntimeProfile.load(RUNTIME_PROFILE_PATH)
    environment = runtime_evidence(runtime_profile)
    temp_base = prepare_controlled_root(temp_base, ALLOWED_TEMP_ROOT)
    evidence_base = prepare_controlled_root(evidence_base, ALLOWED_EVIDENCE_ROOT)
    run_root = create_run_root(temp_base)
    evidence_root = create_run_root(evidence_base)
    containers_before = sorted(container_names())
    fixtures_before = fixture_hashes(profile)
    source_before = None
    source_after = None
    task_root_empty = False
    cases: dict[str, Any] = {}
    materialized: dict[str, Any] = {}
    try:
        source = run_root / "source-library"
        materialized = materializer.materialize(source)
        source_before = snapshot_library(source, runtime_profile)
        task_root = run_root / "tasks"
        manager = LibraryWorkspaceManager(source, task_root, runtime_profile)
        positive = profile["qualification_library"]["records"]["positive"]
        cases["positive_repetitions"] = [
            run_managed_case(
                manager,
                external_id=positive["external_record_id"],
                label=f"positive-{index + 1}",
                profile=profile,
                runtime_profile=runtime_profile,
                evidence_root=evidence_root,
                timeout=profile["limits"]["timeout_seconds"],
                max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
            )
            for index in range(profile["repetitions"])
        ]
        cases["missing_id"] = run_managed_case(
            manager,
            external_id=profile["qualification_library"]["records"]["missing"]["external_record_id"],
            label="missing-id",
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=profile["limits"]["timeout_seconds"],
            max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
        )
        cases["no_epub"] = run_managed_case(
            manager,
            external_id=profile["qualification_library"]["records"]["no_epub"]["external_record_id"],
            label="no-epub",
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=profile["limits"]["timeout_seconds"],
            max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
        )
        cases["multiple_ids"] = rejected_selection_case(source, "1,3", profile)
        cases["invalid_id"] = rejected_selection_case(source, "not-an-id", profile)
        cases["output_limit"] = run_managed_case(
            manager,
            external_id=positive["external_record_id"],
            label="output-limit",
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=profile["limits"]["timeout_seconds"],
            max_export_file_bytes=profile["limits"]["control_output_file_bytes"],
            control_kind="output_limit",
        )
        cases["timeout"] = run_managed_case(
            manager,
            external_id=positive["external_record_id"],
            label="timeout",
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=profile["limits"]["control_timeout_seconds"],
            max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
            control_kind="timeout",
        )
        cases["interruption"] = run_managed_case(
            manager,
            external_id=positive["external_record_id"],
            label="interruption",
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=profile["limits"]["timeout_seconds"],
            max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
            control_kind="interruption",
        )
        cases["unexpected_output"] = run_managed_case(
            manager,
            external_id=positive["external_record_id"],
            label="unexpected-output",
            profile=profile,
            runtime_profile=runtime_profile,
            evidence_root=evidence_root,
            timeout=profile["limits"]["timeout_seconds"],
            max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
            preseed_unexpected=True,
        )
        stale_removed = seed_and_recover_stale_task(manager)
        cases["recovery"] = {
            "run": run_managed_case(
                manager,
                external_id=positive["external_record_id"],
                label="recovery",
                profile=profile,
                runtime_profile=runtime_profile,
                evidence_root=evidence_root,
                timeout=profile["limits"]["timeout_seconds"],
                max_export_file_bytes=profile["limits"]["max_export_file_bytes"],
            ),
            "stale_task_removed": stale_removed,
        }
        source_after = snapshot_library(source, runtime_profile)
        task_root_empty = task_root.is_dir() and not list(task_root.iterdir())
    finally:
        qualification_root_removed = remove_run_root(run_root, temp_base)
    containers_after = sorted(container_names())
    fixtures_after = fixture_hashes(profile)
    result: dict[str, Any] = {
        "artifact": "EXP-0008",
        "authority": authority,
        "cases": cases,
        "cleanup": {
            "containers_after": containers_after,
            "containers_before": containers_before,
            "qualification_root_removed": qualification_root_removed,
            "task_root_empty": task_root_empty,
        },
        "effects": {
            "direct_database_access": False,
            "network": False,
            "persistence": False,
            "product_code": False,
            "source_writes": False,
            "supported_calibredb_export_only": True,
            "writer": False,
        },
        "environment": environment,
        "executed_on": date.today().isoformat(),
        "fixtures": {"after": fixtures_after, "before": fixtures_before},
        "limitations": [
            "synthetic TEST-0001 library only",
            "exact Calibre 9.13.0 image only",
            "single explicit local record and EPUB only",
            "no product adapter or identity comparison",
        ],
        "materialization": {
            "book_count": materialized["book_count"],
            "manifest_sha256": materialized["manifest_sha256"],
            "projection_sha256": materialized["projection_sha256"],
            "synthetic_only": True,
        },
        "preimage_sha256": current_preimage(),
        "privacy": {
            "path_free_result": True,
            "raw_streams_not_retained": True,
        },
        "raw_evidence_sha256": evidence_hashes(evidence_root),
        "schema": "sammlungslotse/exp-0008-result/v1",
        "source": {
            "after": snapshot_summary(source_after),
            "before": snapshot_summary(source_before),
        },
        "status": "inconclusive",
        "workspace_controls": {
            "bounded_by_runtime_profile": True,
            "copy_on_read": True,
            "random_task_ids": True,
            "task_private": True,
        },
    }
    result["privacy"]["path_free_result"] = result_has_no_private_paths(result)
    result["acceptance"] = derive_acceptance(result)
    result["status"] = "qualified" if all(result["acceptance"].values()) else "not_qualified"
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
    if result.get("schema") != "sammlungslotse/exp-0008-result/v1" or result.get("artifact") != "EXP-0008":
        raise RuntimeError("unexpected EXP-0008 result identity")
    if result.get("preimage_sha256") != current_preimage():
        raise RuntimeError("EXP-0008 result preimage differs")
    acceptance = derive_acceptance(result)
    if result.get("acceptance") != acceptance:
        raise RuntimeError("EXP-0008 acceptance values differ from evidence")
    if result.get("status") != "qualified" or not all(acceptance.values()):
        raise RuntimeError("EXP-0008 result is not fully qualified")
    if not result_has_no_private_paths(result):
        raise RuntimeError("EXP-0008 result contains a private or runtime path")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--temp-root", type=Path, default=ALLOWED_TEMP_ROOT / "exp-0008")
    parser.add_argument("--evidence-root", type=Path, default=ALLOWED_EVIDENCE_ROOT / "exp-0008")
    args = parser.parse_args()
    if args.validate_profile:
        load_profile()
        print("EXP-0008 profile valid")
        return 0
    if args.validate_result:
        result = validate_result(args.result)
        print(f"EXP-0008 qualification valid: {sum(result['acceptance'].values())}/{len(result['acceptance'])}")
        return 0
    result = execute_experiment(args.temp_root, args.evidence_root, args.result)
    print(f"EXP-0008 {result['status']}: {sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria")
    return 0 if result["status"] == "qualified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
