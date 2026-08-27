#!/usr/bin/env python3
"""Run and validate the synthetic EXP-0007 snapshot handoff qualification."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0007"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
PROBE_PATH = EXPERIMENT / "probe.py"
DRIVER_PATH = EXPERIMENT / "driver.py"
CONTAINERFILE_PATH = EXPERIMENT / "Containerfile"
RESULT_PATH = EXPERIMENT / "result.json"
RUNNER_PATH = Path(__file__).resolve()
CORPUS_ROOT = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2"
MANIFEST_PATH = CORPUS_ROOT / "manifest.json"
EXP5_RUNNER = ROOT / "tools" / "experiments" / "run_exp_0005.py"
EXP5_PROFILE = ROOT / "experiments" / "ebook" / "exp-0005" / "execution-profile.json"
EXP5_RESULT = ROOT / "experiments" / "ebook" / "exp-0005" / "result.json"
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/](?:Us" + r"ers|home)[\\/]|/(?:ho" + r"me|Users)/)",
    re.IGNORECASE,
)


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load module: {name}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


DRIVER = load_module("sammlungslotse_exp_0007_driver", DRIVER_PATH)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def execute(
    command: list[str],
    *,
    check: bool = True,
    timeout: float = 60,
    cwd: Path = ROOT,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({command[0]} {command[1] if len(command) > 1 else ''}): "
            f"{result.stderr.strip()[:1000]}"
        )
    return result


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("experiment") != "EXP-0007" or profile.get("schema_version") != 1:
        raise RuntimeError("unexpected EXP-0007 profile identity")
    if profile.get("fixture_manifest_sha256") != sha256_file(MANIFEST_PATH):
        raise RuntimeError("EXP-0007 fixture manifest binding differs")
    if profile["rules"].get("variants") != [
        "stream",
        "materialized",
        "original_locator",
    ]:
        raise RuntimeError("EXP-0007 must freeze exactly three handoff variants")
    if profile["rules"].get("repetitions") != 2:
        raise RuntimeError("EXP-0007 requires exactly two positive repetitions")
    limits = profile["limits"]
    if not (
        0 < limits["stdout_bytes"] <= limits["retained_result_bytes"]
        and 0 < limits["stderr_bytes"] <= limits["retained_result_bytes"]
        and 0 < limits["input_bytes"] <= 2 * 1024 * 1024
        and 0 < limits["control_timeout_seconds"] < limits["normal_timeout_seconds"]
    ):
        raise RuntimeError("EXP-0007 limits are absent or broader than planned")
    runtime = profile["container_runtime"]
    if not (
        runtime["network"] == "none"
        and runtime["read_only_root"] is True
        and runtime["user"] == "65532:65532"
        and runtime["capabilities"] == []
        and runtime["no_new_privileges"] is True
        and runtime["memory_bytes"] == runtime["memory_swap_bytes"]
        and runtime["pids_limit"] <= 32
        and runtime["cpus"] <= 1.0
        and runtime["log_driver"] == "none"
    ):
        raise RuntimeError("EXP-0007 Linux isolation profile is incomplete")
    seen = set()
    for case in profile["cases"]:
        if case["case_key"] in seen:
            raise RuntimeError("EXP-0007 case keys must be unique")
        seen.add(case["case_key"])
        candidate = (CORPUS_ROOT / case["relative_path"]).resolve()
        if CORPUS_ROOT.resolve() not in candidate.parents or not candidate.is_file():
            raise RuntimeError("EXP-0007 fixture path escapes or is missing")
        if candidate.stat().st_size != case["size_bytes"] or sha256_file(candidate) != case["sha256"]:
            raise RuntimeError("EXP-0007 frozen case binding differs")
    if seen != {"ingress-stable-minimal", "epub33-valid-reflow"}:
        raise RuntimeError("EXP-0007 positive controls differ from the accepted plan")
    containerfile = CONTAINERFILE_PATH.read_text(encoding="utf-8")
    if "@sha256:" not in containerfile or ":latest" in containerfile:
        raise RuntimeError("EXP-0007 base image must be digest-pinned")
    if 'USER 65532:65532' not in containerfile or 'ENTRYPOINT ["/usr/bin/env", "-i"' not in containerfile:
        raise RuntimeError("EXP-0007 image must use an unprivileged user and empty environment")
    probe_source = PROBE_PATH.read_text(encoding="utf-8")
    forbidden_imports = ("socket", "urllib", "http.client", "requests", "ftplib")
    if any(re.search(rf"^\s*(?:from|import)\s+{re.escape(name)}\b", probe_source, re.MULTILINE) for name in forbidden_imports):
        raise RuntimeError("EXP-0007 Windows probe contains a network-capable import")
    return profile


def load_profile() -> dict[str, Any]:
    return validate_profile(load_json(PROFILE_PATH))


def git_value(*arguments: str) -> str:
    return execute(["git", *arguments]).stdout.strip()


def authority_evidence() -> dict[str, Any]:
    if git_value("status", "--porcelain"):
        raise RuntimeError("EXP-0007 empirical run requires a clean preimage commit")
    head = git_value("rev-parse", "HEAD")
    origin_main = git_value("rev-parse", "origin/main")
    merge_base = git_value("merge-base", "HEAD", "origin/main")
    if merge_base != origin_main:
        raise RuntimeError("EXP-0007 preimage does not descend from exact origin/main")
    registry_text = execute(
        ["git", "show", "origin/main:.ai/artifact_registry.json"]
    ).stdout
    artifacts = json.loads(registry_text)["artifacts"]
    if artifacts["GATE-0002"]["status"] != "done" or artifacts["EXP-0007"]["status"] != "accepted":
        raise RuntimeError("EXP-0007 plan and preceding gate are not canonical on origin/main")
    product_changes = git_value(
        "diff", "--name-only", "origin/main...HEAD", "--", "src", "tools/run_ebook_intake.py"
    )
    if product_changes:
        raise RuntimeError("EXP-0007 preimage changes product code")
    return {
        "origin_main": origin_main,
        "preimage_commit": head,
        "merge_base": merge_base,
        "gate_0002_on_origin_main": True,
        "exp_0007_accepted_on_origin_main": True,
        "product_code_unchanged": True,
    }


def unique_run_root(base: Path) -> Path:
    path = base / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:8]
    )
    path.mkdir(parents=True, exist_ok=False)
    return path


def run_windows(
    profile: dict[str, Any], artifact_root: Path, temp_base: Path
) -> dict[str, Any]:
    workspace = unique_run_root(temp_base)
    try:
        result = execute(
            [
                sys.executable,
                str(DRIVER_PATH),
                "--profile",
                str(PROFILE_PATH),
                "--probe",
                str(PROBE_PATH),
                "--corpus-root",
                str(CORPUS_ROOT),
                "--workspace",
                str(workspace),
                "--platform-profile",
                "windows",
            ],
            timeout=profile["container_runtime"]["timeout_seconds"],
        )
        if len(result.stdout.encode("utf-8")) > profile["limits"]["retained_result_bytes"]:
            raise RuntimeError("EXP-0007 Windows result exceeds retained limit")
        payload = json.loads(result.stdout)
        (artifact_root / "windows.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return payload
    finally:
        if workspace.exists():
            shutil.rmtree(workspace)


def build_image(profile: dict[str, Any]) -> dict[str, Any]:
    execute(
        [
            "podman",
            "build",
            "--pull=never",
            "--network=none",
            "--tag",
            profile["image_tag"],
            "--file",
            str(CONTAINERFILE_PATH),
            str(EXPERIMENT),
        ],
        timeout=600,
    )
    inspection = json.loads(
        execute(["podman", "image", "inspect", profile["image_tag"]]).stdout
    )[0]
    return {
        "id": inspection["Id"].removeprefix("sha256:"),
        "digest": inspection.get("Digest", "").removeprefix("sha256:") or None,
        "architecture": inspection["Architecture"],
        "os": inspection["Os"],
    }


def container_arguments(profile: dict[str, Any], name: str) -> list[str]:
    runtime = profile["container_runtime"]
    return [
        "podman",
        "create",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--user",
        runtime["user"],
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        str(runtime["pids_limit"]),
        "--cpus",
        str(runtime["cpus"]),
        "--memory",
        str(runtime["memory_bytes"]),
        "--memory-swap",
        str(runtime["memory_swap_bytes"]),
        "--tmpfs",
        f"/work:rw,noexec,nosuid,nodev,size={runtime['tmpfs']['/work']}",
        "--tmpfs",
        f"/tmp:rw,noexec,nosuid,nodev,size={runtime['tmpfs']['/tmp']}",
        "--log-driver",
        runtime["log_driver"],
        "--mount",
        f"type=bind,source={CORPUS_ROOT},target=/corpus,ro=true",
        profile["image_tag"],
    ]


def security_projection(inspection: dict[str, Any]) -> dict[str, Any]:
    host = inspection["HostConfig"]
    config = inspection["Config"]
    state = inspection["State"]
    return {
        "network_mode": host.get("NetworkMode"),
        "read_only_root": host.get("ReadonlyRootfs"),
        "user": config.get("User"),
        "cap_add": host.get("CapAdd") or [],
        "cap_drop": sorted(host.get("CapDrop") or []),
        "security_opt": sorted(host.get("SecurityOpt") or []),
        "pids_limit": host.get("PidsLimit"),
        "memory": host.get("Memory"),
        "memory_swap": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "log_driver": host.get("LogConfig", {}).get("Type"),
        "running": state.get("Running", False),
        "oom_killed": state.get("OOMKilled", False),
        "tmpfs": host.get("Tmpfs") or {},
        "mounts": [
            {
                "destination": mount.get("Destination"),
                "rw": mount.get("RW"),
                "type": mount.get("Type"),
            }
            for mount in inspection.get("Mounts", [])
        ],
    }


def linux_security_matches(profile: dict[str, Any], linux: dict[str, Any]) -> bool:
    security = linux["security"]
    runtime = profile["container_runtime"]
    corpus = next(
        (mount for mount in security["mounts"] if mount["destination"] == "/corpus"),
        None,
    )
    return (
        security["network_mode"] == "none"
        and security["read_only_root"] is True
        and security["user"] == runtime["user"]
        and security["cap_add"] == []
        and len(security["cap_drop"]) >= 10
        and all(value.upper().startswith("CAP_") for value in security["cap_drop"])
        and "no-new-privileges" in security["security_opt"]
        and security["pids_limit"] == runtime["pids_limit"]
        and security["memory"] == runtime["memory_bytes"]
        and security["memory_swap"] == runtime["memory_swap_bytes"]
        and security["nano_cpus"] <= 1_000_000_000
        and security["log_driver"] == "none"
        and security["running"] is False
        and security["oom_killed"] is False
        and "/work" in security["tmpfs"]
        and "/tmp" in security["tmpfs"]
        and corpus is not None
        and corpus["rw"] is False
        and linux["container_removed_after_run"] is True
        and linux["environment_minimized"] is True
    )


def run_linux(profile: dict[str, Any], artifact_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    image = build_image(profile)
    name = f"sammlungslotse-exp-0007-{uuid.uuid4().hex[:12]}"
    inspection: dict[str, Any] | None = None
    try:
        execute(container_arguments(profile, name))
        process = execute(
            ["podman", "start", "--attach", name],
            check=False,
            timeout=profile["container_runtime"]["timeout_seconds"],
        )
        inspection = json.loads(execute(["podman", "inspect", name]).stdout)[0]
        if process.returncode != 0:
            raise RuntimeError(f"EXP-0007 Linux driver failed: {process.stderr[:1000]}")
        if len(process.stdout.encode("utf-8")) > profile["limits"]["retained_result_bytes"]:
            raise RuntimeError("EXP-0007 Linux result exceeds retained limit")
        payload = json.loads(process.stdout)
        payload["security"] = security_projection(inspection)
    finally:
        execute(["podman", "rm", "--force", name], check=False)
    payload["container_removed_after_run"] = (
        execute(["podman", "container", "exists", name], check=False).returncode != 0
    )
    (artifact_root / "linux.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload, image


def optional_epubcheck_compatibility(
    profile: dict[str, Any], artifact_root: Path, temp_base: Path
) -> dict[str, Any]:
    try:
        exp5 = load_module("sammlungslotse_exp_0005_runner", EXP5_RUNNER)
        frozen = exp5.validate_result(EXP5_RESULT)
        exp5_profile = json.loads(EXP5_PROFILE.read_text(encoding="utf-8"))
        inspection = json.loads(
            execute(["podman", "image", "inspect", exp5_profile["image_tag"]]).stdout
        )[0]
        image_id = inspection["Id"].removeprefix("sha256:")
        if image_id != frozen["image"]["id"]:
            return {
                "status": "NOT_EXECUTED",
                "reason": "local_image_differs_from_frozen_exp_0005_evidence",
            }
    except Exception:
        return {
            "status": "NOT_EXECUTED",
            "reason": "frozen_hash_checked_exp_0005_prerequisite_unavailable",
        }

    compatibility_root = artifact_root / "epubcheck-compatibility"
    compatibility_root.mkdir(parents=True, exist_ok=False)
    temp_root = unique_run_root(temp_base)
    cases = []
    try:
        for case in profile["cases"]:
            source = CORPUS_ROOT / case["relative_path"]
            task = temp_root / uuid.uuid4().hex
            task.mkdir(mode=0o700)
            materialized = task / f"payload-{uuid.uuid4().hex}.bin"
            materialized.write_bytes(source.read_bytes())
            materialized.chmod(0o400)
            before = sha256_file(materialized)
            evidence = exp5.run_case(
                exp5_profile,
                compatibility_root,
                f"exp7-{case['case_key']}",
                materialized,
                "epubcheck",
                float(exp5_profile["container_runtime"]["timeout_seconds"]),
            )
            after = sha256_file(materialized)
            DRIVER.cleanup_directory(task)
            cases.append(
                {
                    "case_key": case["case_key"],
                    "snapshot_sha256": case["sha256"],
                    "materialized_sha256_before": before,
                    "materialized_sha256_after": after,
                    "input_unchanged": before == after == case["sha256"],
                    "started": evidence["exit_code"] is not None,
                    "timed_out": evidence["timed_out"],
                    "exit_code": evidence["exit_code"],
                    "semantic_report_sha256": evidence.get("semantic_report_sha256"),
                    "container_removed_after_run": evidence["container_removed_after_run"],
                    "temporary_cleanup": not task.exists(),
                }
            )
    finally:
        if temp_root.exists():
            DRIVER.cleanup_directory(temp_root)
    qualified = all(
        case["started"]
        and not case["timed_out"]
        and case["input_unchanged"]
        and case["container_removed_after_run"]
        and case["temporary_cleanup"]
        and case["semantic_report_sha256"]
        for case in cases
    )
    return {
        "status": "QUALIFIED" if qualified else "INCONCLUSIVE",
        "profile_id": frozen["profile_id"],
        "image_id": image_id,
        "tool": {"name": "EPUBCheck", "version": "5.3.0"},
        "network_during_measurement": "none",
        "cases": cases,
        "limitation": "Compatibility evidence only; no product adapter or quality normalization is qualified.",
    }


def raw_evidence(artifact_root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(candidate for candidate in artifact_root.rglob("*") if candidate.is_file()):
        files.append(
            {
                "artifact_key": path.relative_to(artifact_root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "retention": "local synthetic artifact outside Git",
        "files": files,
        "content_sha256": canonical_digest(files),
    }


def all_positive_bound(profile_result: dict[str, Any]) -> bool:
    return all(
        run["accepted"]
        and run["received_sha256"] == run["snapshot_sha256"]
        and run["received_size_bytes"] == run["snapshot_size_bytes"]
        for run in profile_result["positive_runs"]
    )


def prestart_blocked(profile_result: dict[str, Any]) -> bool:
    return all(
        not control["started"] and not control["allowed"]
        for control in profile_result["controls"]["prestart"]
    )


def limits_effective(profile_result: dict[str, Any], profile: dict[str, Any]) -> bool:
    controls = profile_result["controls"]["stream_and_output"]
    return (
        controls["incomplete_stream"]["started"]
        and controls["incomplete_stream"]["accepted"] is False
        and controls["stdout_overflow"]["stdout_overflow"] is True
        and controls["stdout_overflow"]["retained_stdout_bytes"] <= profile["limits"]["stdout_bytes"]
        and controls["stderr_overflow"]["stderr_overflow"] is True
        and controls["stderr_overflow"]["retained_stderr_bytes"] <= profile["limits"]["stderr_bytes"]
    )


def timeout_cleanup(profile_result: dict[str, Any]) -> bool:
    timeout = profile_result["controls"]["stream_and_output"]["timeout_child"]
    v2_timeout = profile_result["controls"]["materialized"]["timeout"]
    return (
        timeout["timed_out"]
        and timeout["process_cleaned"]
        and timeout["child_pid_recorded"]
        and timeout["child_process_cleaned"]
        and v2_timeout["process"]["timed_out"]
        and v2_timeout["child_process_cleaned"]
    )


def v2_cleanup_complete(profile_result: dict[str, Any]) -> bool:
    values = profile_result["controls"]["materialized"]
    return (
        all(values[key]["cleanup"] for key in ("success", "error", "timeout", "interruption"))
        and values["crash_residue"]["detected"]
        and values["crash_residue"]["bounded"]
        and values["crash_residue"]["recovery_cleanup"]
        and profile_result["workspace_empty_after_run"]
    )


def v3_rejected(profile_result: dict[str, Any]) -> bool:
    values = profile_result["controls"]["original_locator"]
    classification = next(
        item for item in profile_result["variant_classifications"] if item["variant"] == "original_locator"
    )
    return (
        not values["exchange"]["started"]
        and not values["exchange"]["allowed"]
        and not values["rename"]["started"]
        and not values["rename"]["allowed"]
        and values["concurrent_change"]["started"]
        and values["concurrent_change"]["accepted"] is False
        and values["concurrent_change"]["provider_received_original_locator"]
        and classification["classification"] == "REJECTED"
    )


def acceptance_contract(
    profile: dict[str, Any], result: dict[str, Any]
) -> dict[str, bool]:
    windows = result["profiles"]["windows"]
    linux = result["profiles"]["linux"]
    serialized = canonical_json(result)
    original_names = [Path(case["relative_path"]).name for case in profile["cases"]]
    classifications = windows["variant_classifications"]
    same_snapshot_matrix = all(
        {
            (run["case_key"], run["snapshot_sha256"], run["snapshot_size_bytes"])
            for run in value["positive_runs"]
        }
        == {
            (case["case_key"], case["sha256"], case["size_bytes"])
            for case in profile["cases"]
        }
        for value in (windows, linux)
    )
    return {
        "canonical_plan_precedes_experiment": result["authority"]["gate_0002_on_origin_main"]
        and result["authority"]["exp_0007_accepted_on_origin_main"],
        "experiment_only_and_product_unchanged": result["authority"]["product_code_unchanged"],
        "three_handoffs_share_frozen_snapshots": same_snapshot_matrix,
        "prestart_guards_fail_closed": prestart_blocked(windows) and prestart_blocked(linux),
        "process_edge_matches_snapshot": all_positive_bound(windows) and all_positive_bound(linux),
        "semantic_repetitions_identical": windows["semantic_repetitions_identical"]
        and linux["semantic_repetitions_identical"],
        "original_inputs_unchanged": windows["originals_unchanged"] and linux["originals_unchanged"],
        "result_path_name_and_content_minimized": PRIVATE_PATH_PATTERN.search(serialized) is None
        and all(name not in serialized for name in original_names),
        "input_and_output_limits_effective": limits_effective(windows, profile)
        and limits_effective(linux, profile),
        "timeout_and_child_cleanup_effective": timeout_cleanup(windows) and timeout_cleanup(linux),
        "materialized_cleanup_and_recovery_effective": v2_cleanup_complete(windows)
        and v2_cleanup_complete(linux),
        "original_locator_controls_fail_closed_and_rejected": v3_rejected(windows)
        and v3_rejected(linux),
        "linux_isolation_profile_effective": linux_security_matches(profile, linux),
        "windows_and_linux_evidence_separate": windows["platform_profile"] == "windows"
        and linux["platform_profile"] == "linux"
        and windows["environment_minimized"] is None
        and linux["environment_minimized"] is True,
        "variant_comparison_complete": {item["variant"] for item in classifications}
        == set(profile["rules"]["variants"])
        and all(
            item["classification"] in profile["rules"]["required_classifications"]
            and item["heaviest_residual_error"]
            for item in classifications
        ),
        "repository_completion_gate": result.get("completion_gate", {}).get("passed") is True,
    }


def run_completion_gate() -> dict[str, Any]:
    commands = [
        ("repository", [sys.executable, "tools/governance/validate_repository.py"]),
        (
            "registry",
            [
                sys.executable,
                ".ai/foundation/artifact_registry_github/registry_semantic.py",
                "validate",
                "--registry",
                ".ai/artifact_registry.json",
            ],
        ),
        ("fixture", [sys.executable, "tools/fixtures/validate_ebook_reference_corpus.py"]),
        ("exp-0002", [sys.executable, "tools/experiments/run_exp_0002.py", "--validate-result"]),
        ("exp-0003", [sys.executable, "tools/experiments/run_exp_0003.py", "--validate-result"]),
        ("exp-0004", [sys.executable, "tools/experiments/run_exp_0004.py", "--validate-result"]),
        ("exp-0005", [sys.executable, "tools/experiments/run_exp_0005.py", "--validate-result"]),
        ("exp-0006", [sys.executable, "tools/experiments/run_exp_0006.py", "--validate-result"]),
        ("exp-0007-profile", [sys.executable, str(RUNNER_PATH), "--validate-profile"]),
        ("unit", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        (
            "compileall",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "src/sammlungslotse",
                "tools/run_ebook_intake.py",
                ".ai/foundation/artifact_registry_github",
                "tools/governance",
                "tools/fixtures",
                "tools/experiments",
                "experiments/ebook/exp-0002",
                "experiments/ebook/exp-0003",
                "experiments/ebook/exp-0004",
                "experiments/ebook/exp-0005",
                "experiments/ebook/exp-0006",
                "experiments/ebook/exp-0007",
            ],
        ),
        ("diff-check", ["git", "diff", "--check"]),
    ]
    results = []
    for key, command in commands:
        completed = execute(command, check=False, timeout=120)
        results.append({"check": key, "passed": completed.returncode == 0})
        if completed.returncode != 0:
            break
    return {
        "executed": True,
        "passed": len(results) == len(commands) and all(item["passed"] for item in results),
        "checks": results,
    }


def result_hashes() -> dict[str, str]:
    return {
        "profile_sha256": sha256_file(PROFILE_PATH),
        "probe_sha256": sha256_file(PROBE_PATH),
        "driver_sha256": sha256_file(DRIVER_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "containerfile_sha256": sha256_file(CONTAINERFILE_PATH),
        "fixture_manifest_sha256": sha256_file(MANIFEST_PATH),
    }


def write_result(result: dict[str, Any], path: Path) -> None:
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if len(serialized.encode("utf-8")) > load_profile()["limits"]["retained_result_bytes"]:
        raise RuntimeError("EXP-0007 versioned result exceeds retained limit")
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise RuntimeError("EXP-0007 result contains an absolute private host path")
    for case in load_profile()["cases"]:
        if Path(case["relative_path"]).name in serialized:
            raise RuntimeError("EXP-0007 result contains an original input filename")
    path.write_text(serialized, encoding="utf-8")


def run(
    profile: dict[str, Any],
    result_path: Path,
    artifact_base: Path,
    temp_base: Path,
) -> dict[str, Any]:
    authority = authority_evidence()
    artifact_root = unique_run_root(artifact_base)
    temp_base.mkdir(parents=True, exist_ok=True)
    windows = run_windows(profile, artifact_root, temp_base)
    linux, image = run_linux(profile, artifact_root)
    compatibility = optional_epubcheck_compatibility(profile, artifact_root, temp_base)
    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment": "EXP-0007",
        "status": "pending_completion",
        "executed_on": date.today().isoformat(),
        "profile_id": profile["profile_id"],
        **result_hashes(),
        "authority": authority,
        "fixture_ref": profile["fixture_ref"],
        "fixture_version": profile["fixture_version"],
        "runtime": {
            "host_os": platform.system(),
            "host_python": platform.python_version(),
            "container_provider": "podman",
            "container_client_version": execute(
                ["podman", "version", "--format", "{{.Client.Version}}"], check=False
            ).stdout.strip(),
            "container_server_version": execute(
                ["podman", "version", "--format", "{{.Server.Version}}"], check=False
            ).stdout.strip(),
            "container_os": image["os"],
            "container_architecture": image["architecture"],
        },
        "image": image,
        "base_image": profile["base_image"],
        "tool": profile["tool"],
        "profiles": {"windows": windows, "linux": linux},
        "optional_epubcheck_compatibility": compatibility,
        "raw_evidence": raw_evidence(artifact_root),
        "completion_gate": {"executed": False, "passed": False, "checks": []},
        "acceptance": {},
        "limitations": [
            "The evidence covers two small synthetic EPUB snapshots and does not forecast private, large or adversarial collections.",
            "Windows proves local process semantics but not operating-system network isolation.",
            "Linux isolation evidence applies only to the fixed Podman/Linux amd64 profile.",
            "V1 is compatible only with stream-capable providers; V2 requires bounded temporary storage and recovery cleanup.",
            "V3 is rejected because the provider receives the original locator and concurrent replacement remains a TOCTOU exposure.",
            "Optional EPUBCheck evidence, when executed, proves only V2 handoff compatibility and not product quality or adapter readiness.",
            "No product adapter, persistence, UI, domain-system access, import, transformation or writer was implemented.",
        ],
    }
    result["acceptance"] = acceptance_contract(profile, result)
    write_result(result, result_path)
    result["completion_gate"] = run_completion_gate()
    result["acceptance"] = acceptance_contract(profile, result)
    result["status"] = "pass" if all(result["acceptance"].values()) else "fail"
    write_result(result, result_path)
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    profile = load_profile()
    result = load_json(path)
    if result.get("experiment") != "EXP-0007" or result.get("status") != "pass":
        raise RuntimeError("EXP-0007 result is not a pass")
    for key, expected in result_hashes().items():
        if result.get(key) != expected:
            raise RuntimeError(f"EXP-0007 result does not match current {key}")
    for key in ("windows", "linux"):
        value = result.get("profiles", {}).get(key, {})
        if len(value.get("positive_runs", [])) != 12:
            raise RuntimeError(f"EXP-0007 {key} positive matrix is incomplete")
    expected_acceptance = acceptance_contract(profile, result)
    if len(expected_acceptance) != 16 or not all(expected_acceptance.values()):
        raise RuntimeError("EXP-0007 recomputed acceptance is incomplete")
    if result.get("acceptance") != expected_acceptance:
        raise RuntimeError("EXP-0007 frozen acceptance differs from evidence")
    if result["profiles"]["windows"]["originals_before_sha256"] != result["profiles"]["windows"]["originals_after_sha256"]:
        raise RuntimeError("EXP-0007 Windows original integrity differs")
    if result["profiles"]["linux"]["originals_before_sha256"] != result["profiles"]["linux"]["originals_after_sha256"]:
        raise RuntimeError("EXP-0007 Linux original integrity differs")
    serialized = canonical_json(result)
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise RuntimeError("EXP-0007 result contains an absolute private host path")
    for case in profile["cases"]:
        if Path(case["relative_path"]).name in serialized:
            raise RuntimeError("EXP-0007 result contains an original input filename")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("C:/rep/artifacts/SammlungsLotse/exp-0007"),
    )
    parser.add_argument(
        "--temp-root",
        type=Path,
        default=Path("C:/rep/tmp/SammlungsLotse/exp-0007"),
    )
    args = parser.parse_args()
    profile = load_profile()
    if args.validate_profile and not args.validate_result:
        print(f"EXP-0007 profile valid: {profile['profile_id']}")
        return 0
    result = validate_result(args.result) if args.validate_result else run(
        profile, args.result, args.artifact_root, args.temp_root
    )
    print(
        f"EXP-0007 {result['status']}: "
        f"{sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
