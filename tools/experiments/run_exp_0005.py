#!/usr/bin/env python3
"""Run the disposable, synthetic EXP-0005 Podman qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[2]
EXPERIMENT = REPOSITORY / "experiments" / "ebook" / "exp-0005"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
FIXTURES = REPOSITORY / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"
DEFAULT_RESULT = EXPERIMENT / "result.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    content = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def execute(arguments: list[str], *, timeout: float | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        tail = completed.stdout[-4000:]
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(arguments[:4])}\n{tail}")
    return completed


def load_profile() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def validate_profile(profile: dict[str, Any]) -> None:
    runtime = profile["container_runtime"]
    required = {
        "network": "none",
        "read_only_root": True,
        "user": "65532:65532",
        "capabilities": [],
        "no_new_privileges": True,
        "log_driver": "none",
    }
    for key, expected in required.items():
        if runtime.get(key) != expected:
            raise RuntimeError(f"unsafe profile value {key}: {runtime.get(key)!r}")
    if runtime["memory_bytes"] != runtime["memory_swap_bytes"]:
        raise RuntimeError("memory and memory+swap limits must be identical")
    if runtime["pids_limit"] > 64 or runtime["cpus"] > 1.0:
        raise RuntimeError("process or CPU profile is broader than the experiment contract")
    if profile["tool"]["artifact_sha256"] != "6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5":
        raise RuntimeError("unexpected EPUBCheck artifact digest")
    containerfile = (EXPERIMENT / "Containerfile").read_text(encoding="utf-8")
    if "@sha256:" not in containerfile or ":latest" in containerfile:
        raise RuntimeError("Containerfile base must be digest-pinned and may not use latest")
    if 'USER 65532:65532' not in containerfile or 'ENTRYPOINT ["/usr/bin/env", "-i"' not in containerfile:
        raise RuntimeError("Containerfile must use the unprivileged user and an empty process environment")


def build_image(profile: dict[str, Any]) -> dict[str, Any]:
    execute(
        [
            "podman",
            "build",
            "--pull=never",
            "--tag",
            profile["image_tag"],
            "--file",
            str(EXPERIMENT / "Containerfile"),
            str(EXPERIMENT),
        ],
        timeout=600,
    )
    inspection = json.loads(execute(["podman", "image", "inspect", profile["image_tag"]]).stdout)[0]
    return {
        "id": inspection["Id"].removeprefix("sha256:"),
        "digest": inspection.get("Digest", "").removeprefix("sha256:") or None,
        "architecture": inspection["Architecture"],
        "os": inspection["Os"],
    }


def directory_evidence(path: Path) -> dict[str, Any]:
    files = []
    total = 0
    if path.exists():
        for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
            size = item.stat().st_size
            total += size
            files.append({"name": item.relative_to(path).as_posix(), "size_bytes": size, "sha256": sha256_file(item)})
    return {"size_bytes": total, "files": files}


def normalize_epubcheck_report(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    volatile = {"checkDate", "elapsedTime", "time", "duration"}

    def normalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: normalize(child) for key, child in sorted(value.items()) if key not in volatile}
        if isinstance(value, list):
            return [normalize(child) for child in value]
        return value

    return normalize(report)


def create_arguments(profile: dict[str, Any], name: str, input_path: Path, command: str) -> list[str]:
    runtime = profile["container_runtime"]
    return [
        "podman",
        "create",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "all",
        "--security-opt",
        "no-new-privileges",
        "--user",
        runtime["user"],
        "--pids-limit",
        str(runtime["pids_limit"]),
        "--cpus",
        str(runtime["cpus"]),
        "--memory",
        str(runtime["memory_bytes"]),
        "--memory-swap",
        str(runtime["memory_swap_bytes"]),
        "--tmpfs",
        f"/tmp:rw,nosuid,nodev,noexec,size={runtime['tmpfs']['/tmp']},mode=1777",
        "--tmpfs",
        f"/output:rw,nosuid,nodev,noexec,size={runtime['tmpfs']['/output']},mode=1777",
        "--log-driver",
        runtime["log_driver"],
        "--mount",
        f"type=bind,source={input_path},target=/input/input.epub,ro=true",
        profile["image_tag"],
        command,
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
        "cap_drop": host.get("CapDrop") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "pids_limit": host.get("PidsLimit"),
        "nano_cpus": host.get("NanoCpus"),
        "cpu_quota": host.get("CpuQuota"),
        "cpu_period": host.get("CpuPeriod"),
        "memory": host.get("Memory"),
        "memory_swap": host.get("MemorySwap"),
        "oom_killed": state.get("OOMKilled", False),
        "running": state.get("Running", False),
        "log_driver": host.get("LogConfig", {}).get("Type"),
        "mounts": [
            {
                "destination": mount.get("Destination"),
                "rw": mount.get("RW"),
                "type": mount.get("Type"),
            }
            for mount in inspection.get("Mounts", [])
        ],
    }


def run_case(
    profile: dict[str, Any],
    raw_root: Path,
    case_key: str,
    input_path: Path,
    command: str,
    timeout: float,
) -> dict[str, Any]:
    if not input_path.is_file():
        raise RuntimeError(f"missing input fixture: {input_path}")
    name = f"sammlungslotse-exp0005-{uuid.uuid4().hex[:12]}"
    case_output = raw_root / case_key
    case_output.mkdir(parents=True, exist_ok=False)
    before = sha256_file(input_path)
    started = time.monotonic()
    timed_out = False
    exit_code: int | None = None
    process_tree_before_kill: list[str] = []
    inspection: dict[str, Any] | None = None
    try:
        execute(create_arguments(profile, name, input_path, command))
        execute(["podman", "start", name])
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = json.loads(
                execute(["podman", "inspect", name, "--format", "{{json .State}}"], check=False).stdout
            )
            if not state.get("Running", False):
                exit_code = int(state.get("ExitCode", 125))
                break
            marker = execute(
                ["podman", "exec", name, "/usr/bin/test", "-f", "/output/probe-complete.json"],
                check=False,
            )
            if marker.returncode == 0:
                execute(["podman", "cp", f"{name}:/output/.", str(case_output)])
                marker_value = json.loads((case_output / "probe-complete.json").read_text(encoding="utf-8"))
                exit_code = int(marker_value["exit_code"])
                execute(["podman", "kill", name])
                execute(["podman", "wait", name])
                break
            time.sleep(0.05)
        if exit_code is None:
            timed_out = True
            top = execute(["podman", "top", name, "pid,args"], check=False)
            process_tree_before_kill = [line.strip() for line in top.stdout.splitlines() if line.strip()]
            execute(["podman", "cp", f"{name}:/output/.", str(case_output)], check=False)
            execute(["podman", "kill", name])
            waited = execute(["podman", "wait", name])
            exit_code = int(waited.stdout.strip().splitlines()[-1])
        inspection = json.loads(execute(["podman", "inspect", name]).stdout)[0]
    finally:
        execute(["podman", "rm", "--force", name], check=False)
    after = sha256_file(input_path)
    output = directory_evidence(case_output)
    evidence: dict[str, Any] = {
        "case_key": case_key,
        "command": command,
        "duration_seconds": round(time.monotonic() - started, 6),
        "timed_out": timed_out,
        "exit_code": exit_code,
        "input_sha256_before": before,
        "input_sha256_after": after,
        "input_unchanged": before == after,
        "process_tree_entries_before_kill": len(process_tree_before_kill),
        "container_removed_after_run": execute(["podman", "container", "exists", name], check=False).returncode != 0,
        "output": output,
        "security": security_projection(inspection or {}),
    }
    report = case_output / "report.json"
    if report.is_file():
        normalized = normalize_epubcheck_report(report)
        evidence["semantic_report_sha256"] = canonical_digest(normalized)
    for candidate in sorted(case_output.glob("*.json")):
        if candidate.name != "report.json":
            evidence.setdefault("control", {})[candidate.name] = json.loads(candidate.read_text(encoding="utf-8"))
    return evidence


def assess(profile: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, bool]:
    by_key = {case["case_key"]: case for case in cases}
    epub_runs = [case for case in cases if case["case_key"].startswith("epubcheck-")]
    repeat_groups: dict[str, list[dict[str, Any]]] = {}
    for case in epub_runs:
        repeat_groups.setdefault(case["case_key"].rsplit("-run-", 1)[0], []).append(case)
    repeatable = all(
        len(group) == 2
        and len({item.get("semantic_report_sha256") for item in group}) == 1
        and len({item["exit_code"] for item in group}) == 1
        for group in repeat_groups.values()
    )
    all_inputs_unchanged = all(case["input_unchanged"] for case in cases)
    security_consistent = all(
        case["security"]["network_mode"] == "none"
        and case["security"]["read_only_root"] is True
        and case["security"]["user"] == profile["container_runtime"]["user"]
        and case["security"]["cap_add"] == []
        and len(case["security"]["cap_drop"]) >= 10
        and all(item.upper().startswith("CAP_") for item in case["security"]["cap_drop"])
        and "no-new-privileges" in case["security"]["security_opt"]
        for case in cases
    )
    environment_control = by_key["probe-environment-minimized"]["control"]["environment.json"]
    output_control = by_key["probe-output-limit"]["control"]["output-limit.json"]
    cpu_control = by_key["probe-cpu-limit"]["control"]["cpu-limit.json"]
    memory = by_key["probe-memory-limit"]
    return {
        "input_read_only": by_key["probe-input-read-only"]["control"]["input-write.json"]["write_succeeded"] is False,
        "all_inputs_unchanged": all_inputs_unchanged,
        "output_confined_and_limited": output_control["errno"] is not None
        and output_control["written_before_limit"] < output_control["attempted_bytes"]
        and all(case["output"]["size_bytes"] <= profile["retained_output_max_bytes"] for case in cases),
        "network_denied": by_key["probe-network-denied"]["control"]["network.json"]["connection_succeeded"] is False,
        "memory_limit_effective": memory["exit_code"] in {42, 137} or memory["security"]["oom_killed"] is True,
        "cpu_limit_effective": cpu_control["total_cpu_seconds"] <= cpu_control["wall_seconds"] * 1.5,
        "timeout_and_child_cleanup": by_key["run-tool-timeout"]["timed_out"] is True
        and by_key["run-tool-timeout"]["process_tree_entries_before_kill"] >= 2
        and by_key["run-tool-timeout"]["container_removed_after_run"] is True,
        "environment_minimized": environment_control["denied_present"] == []
        and set(environment_control["names"]) == set(profile["environment_allowlist"]),
        "security_profile_effective": security_consistent,
        "repeatable_findings": repeatable,
        "tool_provenance_pinned": bool(profile["tool"]["artifact_sha256"] and profile["base_image"]["reference"]),
    }


def run(profile: dict[str, Any], result_path: Path, artifact_root: Path) -> dict[str, Any]:
    raw_root = artifact_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_root.mkdir(parents=True, exist_ok=False)
    image = build_image(profile)
    version_input = FIXTURES / "epub33-valid-reflow" / "valid-reflow.epub"
    cases: list[dict[str, Any]] = []
    case_specs = [
        ("tool-version", version_input, "tool-version", 15.0),
        ("epubcheck-valid-run-1", version_input, "epubcheck", 15.0),
        ("epubcheck-valid-run-2", version_input, "epubcheck", 15.0),
        ("epubcheck-invalid-run-1", FIXTURES / "container-corrupt" / "corrupt.epub", "epubcheck", 15.0),
        ("epubcheck-invalid-run-2", FIXTURES / "container-corrupt" / "corrupt.epub", "epubcheck", 15.0),
        ("probe-input-read-only", version_input, "input-write", 5.0),
        ("probe-network-denied", version_input, "network", 5.0),
        ("probe-output-limit", version_input, "output-limit", 5.0),
        ("probe-memory-limit", version_input, "memory-limit", 10.0),
        ("probe-cpu-limit", version_input, "cpu-limit", 10.0),
        ("probe-environment-minimized", version_input, "environment", 5.0),
        (
            "run-tool-timeout",
            FIXTURES / "run-tool-timeout" / "input.epub",
            "timeout-child",
            profile["container_runtime"]["timeout_probe_seconds"],
        ),
    ]
    os.environ["EXP0005_HOST_SENTINEL"] = "present-on-host-only"
    for case_key, input_path, command, timeout in case_specs:
        cases.append(run_case(profile, raw_root, case_key, input_path, command, timeout))
    acceptance = assess(profile, cases)
    result = {
        "schema_version": 1,
        "experiment": "EXP-0005",
        "status": "pass" if all(acceptance.values()) else "fail",
        "executed_on": date.today().isoformat(),
        "profile_id": profile["profile_id"],
        "profile_sha256": sha256_file(PROFILE_PATH),
        "fixture_ref": profile["fixture_ref"],
        "fixture_version": profile["fixture_version"],
        "runtime": {
            "provider": "podman",
            "client_version": execute(["podman", "version", "--format", "{{.Client.Version}}"], check=False).stdout.strip(),
            "server_version": execute(["podman", "version", "--format", "{{.Server.Version}}"], check=False).stdout.strip(),
            "host_os": platform.system(),
            "container_os": image["os"],
            "architecture": image["architecture"],
        },
        "image": image,
        "tool": profile["tool"],
        "java_runtime": profile["java_runtime"],
        "acceptance": acceptance,
        "cases": cases,
        "raw_evidence": {
            "retention": "local artifact outside Git",
            "content_sha256": canonical_digest([case["output"] for case in cases]),
        },
        "limitations": [
            "The result qualifies one Linux/amd64 Podman profile and does not select a product runtime.",
            "Network denial is demonstrated for the container namespace; image provisioning used explicit network access.",
            "The synthetic fixtures do not establish behavior for private or large real collections.",
        ],
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def validate_result(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    profile = load_profile()
    if result.get("experiment") != "EXP-0005":
        raise RuntimeError("result does not belong to EXP-0005")
    if result.get("status") != "pass" or not all(result.get("acceptance", {}).values()):
        raise RuntimeError("EXP-0005 result is not a complete pass")
    if result.get("profile_id") != profile["profile_id"] or result.get("profile_sha256") != sha256_file(PROFILE_PATH):
        raise RuntimeError("EXP-0005 result does not match the current execution profile")
    if result.get("fixture_version") != profile["fixture_version"]:
        raise RuntimeError("EXP-0005 result does not match the active fixture version")
    if len(result.get("acceptance", {})) != 11 or len(result.get("cases", [])) != 12:
        raise RuntimeError("EXP-0005 result has an incomplete acceptance or case set")
    if any(case["input_sha256_before"] != case["input_sha256_after"] for case in result["cases"]):
        raise RuntimeError("an EXP-0005 input changed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("C:/rep/artifacts/SammlungsLotse/exp-0005"),
    )
    args = parser.parse_args()
    profile = load_profile()
    validate_profile(profile)
    if args.validate_profile and not args.validate_result:
        print(f"EXP-0005 profile valid: {profile['profile_id']}")
        return 0
    if args.validate_result:
        result = validate_result(args.result)
    else:
        result = run(profile, args.result, args.artifact_root)
    print(f"EXP-0005 {result['status']}: {sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
