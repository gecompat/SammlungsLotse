from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import re
import subprocess
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = ROOT / "experiments" / "ebook" / "exp-0006"
PROFILE_PATH = EXPERIMENT_ROOT / "execution-profile.json"
PROBE_PATH = EXPERIMENT_ROOT / "probe.py"
CONTAINERFILE_PATH = EXPERIMENT_ROOT / "Containerfile"
CORPUS_ROOT = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2"
MANIFEST_PATH = CORPUS_ROOT / "manifest.json"
DEFAULT_RESULT = EXPERIMENT_ROOT / "result.json"
PRIVATE_PATH_PATTERN = re.compile(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/|/home/[^/]+/)")


def load_probe() -> ModuleType:
    specification = importlib.util.spec_from_file_location("exp_0006_probe", PROBE_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load EXP-0006 probe")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


PROBE = load_probe()


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
    arguments: list[str], *, timeout: float | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
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
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(arguments[:4])}\n"
            f"{completed.stdout[-4000:]}"
        )
    return completed


def load_profile() -> dict[str, Any]:
    profile = load_json(PROFILE_PATH)
    validate_profile(profile)
    return profile


def validate_profile(profile: dict[str, Any]) -> None:
    PROBE.validate_profile(profile)
    if profile.get("fixture_version") != "0.2.0":
        raise RuntimeError("EXP-0006 requires TEST-0001 fixture version 0.2.0")
    if profile.get("fixture_manifest_sha256") != sha256_file(MANIFEST_PATH):
        raise RuntimeError("EXP-0006 profile does not match TEST-0001")
    if profile.get("implementation", {}).get("external_dependencies") != []:
        raise RuntimeError("EXP-0006 may not add Python dependencies")
    runtime = profile.get("container_runtime", {})
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
            raise RuntimeError(f"unsafe EXP-0006 profile value {key}: {runtime.get(key)!r}")
    if runtime.get("memory_bytes") != runtime.get("memory_swap_bytes"):
        raise RuntimeError("EXP-0006 memory and memory+swap limits must match")
    if runtime.get("memory_bytes", 0) > 268435456:
        raise RuntimeError("EXP-0006 memory limit is broader than the contract")
    if runtime.get("pids_limit", 0) > 16 or runtime.get("cpus", 0) > 1.0:
        raise RuntimeError("EXP-0006 process or CPU limit is broader than the contract")
    if runtime.get("timeout_seconds", 0) > 10:
        raise RuntimeError("EXP-0006 host timeout is broader than the contract")
    if profile.get("result_max_bytes") != runtime.get("tmpfs", {}).get("/output"):
        raise RuntimeError("EXP-0006 output limits are inconsistent")
    containerfile = CONTAINERFILE_PATH.read_text(encoding="utf-8")
    if profile["base_image"]["reference"] not in containerfile:
        raise RuntimeError("EXP-0006 Containerfile base differs from the profile")
    if ":latest" in containerfile or "@sha256:" not in containerfile:
        raise RuntimeError("EXP-0006 Containerfile base is not digest-pinned")
    if 'USER 65532:65532' not in containerfile or 'ENTRYPOINT ["/usr/bin/env", "-i"' not in containerfile:
        raise RuntimeError("EXP-0006 Containerfile does not bind user and environment")


def load_manifest_cases() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = load_json(MANIFEST_PATH)
    return manifest, {case["case_key"]: case for case in manifest["cases"]}


def selected_input_paths(profile: dict[str, Any]) -> list[Path]:
    _, cases = load_manifest_cases()
    selected: set[Path] = {MANIFEST_PATH.resolve()}
    root = CORPUS_ROOT.resolve()
    for row in profile["cases"]:
        case = cases[row["source_case_key"]]
        components = {
            PurePosixPath(item["path"]).name: item for item in case["components"]
        }
        for name in row["components"]:
            component = components[name]
            path = (root / component["path"]).resolve()
            if root not in path.parents or not path.is_file():
                raise RuntimeError("EXP-0006 selected input escapes TEST-0001")
            if path.stat().st_size != component["size_bytes"] or sha256_file(path) != component["sha256"]:
                raise RuntimeError("EXP-0006 selected input differs from TEST-0001")
            selected.add(path)
    return sorted(selected, key=lambda path: path.as_posix())


def input_hashes(paths: list[Path]) -> dict[str, str]:
    return {
        path.relative_to(CORPUS_ROOT).as_posix(): sha256_file(path)
        for path in paths
    }


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
            str(EXPERIMENT_ROOT),
        ],
        timeout=300,
    )
    inspection = load_json_from_command(["podman", "image", "inspect", profile["image_tag"]])[0]
    return {
        "id": inspection["Id"].removeprefix("sha256:"),
        "digest": (inspection.get("Digest") or "").removeprefix("sha256:") or None,
        "architecture": inspection["Architecture"],
        "os": inspection["Os"],
    }


def load_json_from_command(arguments: list[str]) -> Any:
    return json.loads(execute(arguments).stdout)


def create_arguments(profile: dict[str, Any], name: str) -> list[str]:
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
        f"type=bind,source={CORPUS_ROOT.resolve()},target=/corpus,ro=true",
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


def run_repetition(
    profile: dict[str, Any], artifact_root: Path, repetition: int
) -> dict[str, Any]:
    name = f"sammlungslotse-exp0006-{uuid.uuid4().hex[:12]}"
    output_path = artifact_root / f"repetition-{repetition}.json"
    started = time.monotonic()
    inspection: dict[str, Any] | None = None
    exit_code: int | None = None
    try:
        execute(create_arguments(profile, name))
        completed = execute(
            ["podman", "start", "--attach", name],
            timeout=float(profile["container_runtime"]["timeout_seconds"]),
            check=False,
        )
        inspection = load_json_from_command(["podman", "inspect", name])[0]
        exit_code = int(inspection["State"]["ExitCode"])
        if exit_code != 0:
            diagnostic = (completed.stderr or completed.stdout).strip()[-2000:]
            raise RuntimeError(
                f"EXP-0006 container exited with {exit_code}: {diagnostic}"
            )
        serialized = completed.stdout
        if not serialized.strip():
            raise RuntimeError("EXP-0006 container produced no bounded stdout result")
        if len(serialized.encode("utf-8")) > profile["result_max_bytes"]:
            raise RuntimeError("EXP-0006 repetition output exceeds the retained limit")
        output_path.write_text(serialized, encoding="utf-8")
    except subprocess.TimeoutExpired as exc:
        execute(["podman", "kill", name], check=False)
        execute(["podman", "wait", name], check=False)
        raise RuntimeError("EXP-0006 container exceeded its host timeout") from exc
    finally:
        execute(["podman", "rm", "--force", name], check=False)
    if not output_path.is_file():
        raise RuntimeError("EXP-0006 repetition output is missing")
    if output_path.stat().st_size > profile["result_max_bytes"]:
        raise RuntimeError("EXP-0006 repetition output exceeds the retained limit")
    payload = load_json(output_path)
    payload["repetition"] = repetition
    payload["duration_seconds"] = round(time.monotonic() - started, 6)
    payload["exit_code"] = exit_code
    payload["security"] = security_projection(inspection or {})
    payload["container_removed_after_run"] = (
        execute(["podman", "container", "exists", name], check=False).returncode != 0
    )
    return payload


def all_case_results(repetition: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case["row_key"]: case for case in repetition["case_results"]}


def security_matches(profile: dict[str, Any], repetition: dict[str, Any]) -> bool:
    security = repetition["security"]
    runtime = profile["container_runtime"]
    corpus_mount = next(
        (mount for mount in security["mounts"] if mount["destination"] == "/corpus"),
        None,
    )
    cap_drop = security["cap_drop"]
    return (
        security["network_mode"] == "none"
        and security["read_only_root"] is True
        and security["user"] == runtime["user"]
        and security["cap_add"] == []
        and len(cap_drop) >= 10
        and all(item.upper().startswith("CAP_") for item in cap_drop)
        and "no-new-privileges" in security["security_opt"]
        and security["pids_limit"] == runtime["pids_limit"]
        and security["memory"] == runtime["memory_bytes"]
        and security["memory_swap"] == runtime["memory_swap_bytes"]
        and security["nano_cpus"] <= 1_000_000_000
        and security["log_driver"] == "none"
        and security["running"] is False
        and security["oom_killed"] is False
        and corpus_mount is not None
        and corpus_mount["rw"] is False
        and "/output" in security["tmpfs"]
        and "/tmp" in security["tmpfs"]
        and repetition["container_removed_after_run"] is True
    )


def metrics_for(repetition: dict[str, Any]) -> dict[str, Any]:
    cases = repetition["case_results"]
    blocked = [case for case in cases if not case["deep_tool_allowed"]]
    return {
        "matrix_matches": sum(case["evaluation"]["matches_expected"] for case in cases),
        "matrix_rows": len(cases),
        "critical_false_release_count": sum(case["deep_tool"]["started"] for case in blocked),
        "deep_tool_allowed_count": sum(case["deep_tool_allowed"] for case in cases),
        "deep_tool_started_count": sum(case["deep_tool"]["started"] for case in cases),
        "blocked_count": len(blocked),
        "format_capabilities_observed": sorted({case["format_capability"] for case in cases}),
        "next_actions_observed": sorted({case["next_action"] for case in cases}),
    }


def acceptance_contract(
    profile: dict[str, Any],
    repetitions: list[dict[str, Any]],
    before: dict[str, str],
    after: dict[str, str],
) -> tuple[dict[str, bool], dict[str, Any]]:
    first = all_case_results(repetitions[0])
    cases = list(first.values())
    metrics = metrics_for(repetitions[0])
    timeout = first["run-tool-timeout"]
    unknown = first["format-unknown"]
    risk_codes = {
        item["code"]
        for case in cases
        for item in case["findings"]
    }
    forbidden = set(profile["rules"]["forbidden_effects"])
    all_effects = {
        effect
        for repetition in repetitions
        for case in repetition["case_results"]
        for effect in case["effects_observed"]
    }
    expected_environment = set(profile["environment_allowlist"])
    acceptance = {
        "profile_and_fixture_bound": profile["fixture_manifest_sha256"] == sha256_file(MANIFEST_PATH)
        and all(repetition["profile_id"] == profile["profile_id"] for repetition in repetitions),
        "eleven_matrix_rows_match": metrics["matrix_rows"] == 11
        and metrics["matrix_matches"] == 11
        and all(repetition["matrix_matches"] for repetition in repetitions),
        "safe_sequence_fixed": all(
            tuple(case["safe_sequence"]) == PROBE.SAFE_SEQUENCE for case in cases
        ),
        "critical_false_release_zero": metrics["critical_false_release_count"] == 0,
        "deep_tool_gate_effective": metrics["deep_tool_allowed_count"] == metrics["deep_tool_started_count"] == 3,
        "signature_overrides_extension": unknown["format_capability"] == "unknown"
        and unknown["next_action"] == "abstain"
        and "format.extension_mismatch" in {item["code"] for item in unknown["findings"]},
        "risk_findings_separate": {
            "security.path_traversal",
            "resource.expansion_limit_exceeded",
            "protection.present",
            "security.active_content",
            "security.remote_resource",
        }.issubset(risk_codes),
        "decision_states_separate": set(metrics["format_capabilities_observed"]) == PROBE.FORMAT_CAPABILITIES
        and set(metrics["next_actions_observed"]) == PROBE.NEXT_ACTIONS,
        "timeout_and_process_cleanup": timeout["deep_tool"]["timed_out"] is True
        and timeout["deep_tool"]["cleaned"] is True
        and timeout["deep_tool"]["child_processes_observed"] == 0,
        "semantic_repetitions_identical": len(repetitions) == 2
        and repetitions[0]["semantic_sha256"] == repetitions[1]["semantic_sha256"],
        "fixture_inputs_unchanged": before == after,
        "network_denied": all(repetition["security"]["network_mode"] == "none" for repetition in repetitions),
        "filesystem_and_output_confined": all(
            security_matches(profile, repetition) for repetition in repetitions
        ),
        "resource_profile_effective": all(
            repetition["security"]["memory"] == profile["container_runtime"]["memory_bytes"]
            and repetition["security"]["pids_limit"] == profile["container_runtime"]["pids_limit"]
            and repetition["security"]["nano_cpus"] <= 1_000_000_000
            for repetition in repetitions
        ),
        "environment_minimized": all(
            set(repetition["environment_names"]) == expected_environment
            for repetition in repetitions
        ),
        "no_forbidden_effect": not (all_effects & forbidden)
        and all_effects == set()
        and all(source.startswith("fixture://TEST-0001/0.2.0/") for case in cases for source in case["sources"]),
    }
    return acceptance, metrics


def run(profile: dict[str, Any], result_path: Path, artifact_base: Path) -> dict[str, Any]:
    artifact_root = artifact_base / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    )
    artifact_root.mkdir(parents=True, exist_ok=False)
    image = build_image(profile)
    paths = selected_input_paths(profile)
    before = input_hashes(paths)
    repetitions = [
        run_repetition(profile, artifact_root, repetition)
        for repetition in range(1, profile["rules"]["repetitions"] + 1)
    ]
    after = input_hashes(paths)
    acceptance, metrics = acceptance_contract(profile, repetitions, before, after)
    raw_outputs = sorted(artifact_root.glob("repetition-*.json"))
    result = {
        "schema_version": 1,
        "experiment": "EXP-0006",
        "status": "pass" if all(acceptance.values()) else "fail",
        "executed_on": date.today().isoformat(),
        "profile_id": profile["profile_id"],
        "profile_sha256": sha256_file(PROFILE_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "probe_sha256": sha256_file(PROBE_PATH),
        "containerfile_sha256": sha256_file(CONTAINERFILE_PATH),
        "fixture_ref": profile["fixture_ref"],
        "fixture_version": profile["fixture_version"],
        "fixture_manifest_sha256": profile["fixture_manifest_sha256"],
        "runtime": {
            "provider": "podman",
            "client_version": execute(["podman", "version", "--format", "{{.Client.Version}}"], check=False).stdout.strip(),
            "server_version": execute(["podman", "version", "--format", "{{.Server.Version}}"], check=False).stdout.strip(),
            "host_os": platform.system(),
            "container_os": image["os"],
            "architecture": image["architecture"],
            "python_version": repetitions[0]["python_version"],
            "external_dependencies": profile["implementation"]["external_dependencies"],
        },
        "image": image,
        "base_image": profile["base_image"],
        "tool": profile["tool"],
        "metrics": metrics,
        "acceptance": acceptance,
        "repetitions": repetitions,
        "input_integrity": {
            "before_sha256": before,
            "after_sha256": after,
            "unchanged": before == after,
        },
        "raw_evidence": {
            "retention": "local artifact outside Git",
            "files": [
                {
                    "name": path.name,
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
                for path in raw_outputs
            ],
            "content_sha256": canonical_digest(
                [load_json(path) for path in raw_outputs]
            ),
        },
        "limitations": [
            "The result covers eleven small synthetic rows and does not forecast private or large-collection behavior.",
            "PDF is unsupported only for this profile's deep EPUB path; the result is not a general PDF product decision.",
            "The bounded ZIP and XML inspection is an experiment probe, not a product parser or public contract.",
            "The result qualifies one Linux/amd64 Podman profile and does not select a product runtime.",
            "Network denial and filesystem/resource limits apply to the container run; the image build used pull=never and network=none.",
            "No product adapter, persistence, UI, domain-system access, import, quarantine action or writer was implemented.",
        ],
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise RuntimeError("EXP-0006 result contains an absolute private host path")
    result_path.write_text(serialized, encoding="utf-8")
    return result


def validate_result(path: Path) -> dict[str, Any]:
    profile = load_profile()
    result = load_json(path)
    if result.get("experiment") != "EXP-0006" or result.get("status") != "pass":
        raise RuntimeError("EXP-0006 result is not a pass")
    expected_hashes = {
        "profile_sha256": sha256_file(PROFILE_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "probe_sha256": sha256_file(PROBE_PATH),
        "containerfile_sha256": sha256_file(CONTAINERFILE_PATH),
        "fixture_manifest_sha256": sha256_file(MANIFEST_PATH),
    }
    for key, expected in expected_hashes.items():
        if result.get(key) != expected:
            raise RuntimeError(f"EXP-0006 result does not match current {key}")
    acceptance = result.get("acceptance", {})
    if len(acceptance) != 16 or not all(acceptance.values()):
        raise RuntimeError("EXP-0006 acceptance set is incomplete")
    repetitions = result.get("repetitions", [])
    if len(repetitions) != 2 or repetitions[0].get("semantic_sha256") != repetitions[1].get("semantic_sha256"):
        raise RuntimeError("EXP-0006 repetition evidence is incomplete")
    if any(len(repetition.get("case_results", [])) != 11 for repetition in repetitions):
        raise RuntimeError("EXP-0006 matrix evidence is incomplete")
    if result.get("input_integrity", {}).get("unchanged") is not True:
        raise RuntimeError("EXP-0006 fixture integrity evidence is incomplete")
    if result.get("metrics", {}).get("critical_false_release_count") != 0:
        raise RuntimeError("EXP-0006 has a safety-critical false release")
    if any(not security_matches(profile, repetition) for repetition in repetitions):
        raise RuntimeError("EXP-0006 frozen security evidence differs from the profile")
    serialized = canonical_json(result)
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise RuntimeError("EXP-0006 result contains an absolute private host path")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("C:/rep/artifacts/SammlungsLotse/exp-0006"),
    )
    args = parser.parse_args()
    profile = load_profile()
    if args.validate_profile and not args.validate_result:
        print(f"EXP-0006 profile valid: {profile['profile_id']}")
        return 0
    result = validate_result(args.result) if args.validate_result else run(
        profile, args.result, args.artifact_root
    )
    print(
        f"EXP-0006 {result['status']}: "
        f"{sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
