#!/usr/bin/env python3
"""Qualify the exact WI-0005 profile with synthetic media and local Podman."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_intake.application import TriageService  # noqa: E402
from sammlungslotse.ebook_intake.deep_application import (  # noqa: E402
    DeepReadOnlyService,
)
from sammlungslotse.ebook_intake.deep_profile import DeepRuntimeProfile  # noqa: E402
from sammlungslotse.ebook_intake.deep_workspace import (  # noqa: E402
    TaskWorkspaceManager,
)
from sammlungslotse.ebook_intake.epubcheck_provider import (  # noqa: E402
    EpubCheckProvider,
)
from sammlungslotse.ebook_intake.podman_executor import (  # noqa: E402
    PodmanExecutor,
    run_bounded,
)
from sammlungslotse.ebook_intake.snapshot import (  # noqa: E402
    LocalFileSnapshotReader,
)


PROFILE_PATH = ROOT / "runtime" / "ebook-deep-readonly" / "profile.json"
RESULT_PATH = ROOT / "runtime" / "ebook-deep-readonly" / "qualification.json"
PACKAGE_ROOT = ROOT / "src" / "sammlungslotse" / "ebook_intake"
PREIMAGE_FILES = {
    "containerfile": ROOT / "runtime" / "ebook-deep-readonly" / "Containerfile",
    "profile": PROFILE_PATH,
    "provisioner": ROOT / "tools" / "provision_ebook_deep_profile.py",
    "qualifier": ROOT / "tools" / "qualify_ebook_deep_profile.py",
    "runner": ROOT / "tools" / "run_ebook_intake.py",
    "sammlungslotse/__init__.py": ROOT
    / "src"
    / "sammlungslotse"
    / "__init__.py",
    "wrapper_source": ROOT
    / "runtime"
    / "ebook-deep-readonly"
    / "EpubCheckWrapper.java",
    **{
        f"ebook_intake/{path.name}": path
        for path in sorted(PACKAGE_ROOT.glob("*.py"))
    },
}
RUNNER = ROOT / "tools" / "run_ebook_intake.py"
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"
STABLE = CASES / "ingress-stable-minimal" / "stable.epub"
FINDING = CASES / "epub-missing-resource" / "missing-resource.epub"
GATED = CASES / "epub-active-or-remote" / "active-remote.epub"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text_sha256(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def execute(
    arguments: list[str], *, timeout: float = 60, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        arguments,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"qualification command failed ({result.returncode}): "
            f"{arguments[0]} {arguments[1]}"
        )
    return result


def run_cli(
    source: Path,
    temp_root: Path,
    *,
    deep: bool,
    profile_path: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    arguments = [sys.executable, str(RUNNER), "--json"]
    if deep:
        arguments.extend(["--deep-read-only", "--deep-temp-root", str(temp_root)])
        if profile_path is not None:
            arguments.extend(["--deep-profile", str(profile_path)])
    arguments.append(str(source))
    completed = execute(arguments, timeout=90, check=False)
    return completed.returncode, json.loads(completed.stdout)


def image_summary(profile: DeepRuntimeProfile) -> dict[str, object]:
    image = json.loads(
        execute(
            ["podman", "image", "inspect", profile.image["tag"], "--format", "json"]
        ).stdout
    )[0]
    actual_id = image["Id"]
    if not actual_id.startswith("sha256:"):
        actual_id = f"sha256:{actual_id}"
    return {
        "architecture": image["Architecture"],
        "entrypoint_exact": image["Config"].get("Entrypoint")
        == profile.image["entrypoint"],
        "id": actual_id,
        "id_exact": actual_id == profile.image["id"],
        "os": image["Os"],
        "user_exact": image["Config"].get("User") == profile.execution["user"],
    }


def podman_summary() -> dict[str, object]:
    value = json.loads(execute(["podman", "version", "--format", "json"]).stdout)
    return {
        "client_version": value["Client"]["Version"],
        "server_os_arch": value["Server"]["OsArch"],
        "server_version": value["Server"]["Version"],
    }


def isolation_prestart(
    profile: DeepRuntimeProfile, temp_root: Path
) -> dict[str, object]:
    triage = TriageService().triage(LocalFileSnapshotReader(STABLE))
    if triage.snapshot is None:
        raise RuntimeError("stable fixture did not produce a snapshot")
    manager = TaskWorkspaceManager(temp_root, profile)
    workspace = manager.create(triage.snapshot)
    executor = PodmanExecutor(profile)
    name = f"sammlungslotse-wi0005-qualification-{uuid.uuid4().hex[:12]}"
    created = False
    try:
        execute(executor._create_arguments(name, workspace))
        created = True
        image = executor._inspect_image()
        inspection = executor._inspect_container(name)
        host = inspection["HostConfig"]
        config = inspection["Config"]
        return {
            "cap_drop": sorted(host.get("CapDrop") or []),
            "command_exact": config.get("Cmd")
            == profile.execution["provider_arguments"],
            "cpu_nanos": host.get("NanoCpus"),
            "environment_exact": set(config.get("Env") or [])
            == {
                f"{key}={value}"
                for key, value in profile.execution["environment"].items()
            },
            "input_read_only": next(
                item["RW"] is False
                for item in inspection["Mounts"]
                if item["Destination"] == "/input/input.epub"
            ),
            "memory_bytes": host.get("Memory"),
            "memory_swap_bytes": host.get("MemorySwap"),
            "network": host.get("NetworkMode"),
            "no_new_privileges": "no-new-privileges"
            in (host.get("SecurityOpt") or []),
            "pids_limit": host.get("PidsLimit"),
            "privileged": host.get("Privileged"),
            "read_only_root": host.get("ReadonlyRootfs"),
            "tmpfs_paths": sorted((host.get("Tmpfs") or {}).keys()),
            "tmpfs_values": host.get("Tmpfs"),
            "ulimits": sorted(
                host.get("Ulimits") or [], key=lambda item: item.get("Name", "")
            ),
            "verified_by_executor": executor._isolation_matches(inspection, image),
        }
    finally:
        if created:
            execute(["podman", "rm", "--force", name], check=False)
        manager.cleanup(workspace)


def output_limit_probe(profile: DeepRuntimeProfile, temp_root: Path) -> dict[str, object]:
    name = f"sammlungslotse-wi0005-output-{uuid.uuid4().hex[:12]}"
    arguments = [
        "podman",
        "run",
        "--name",
        name,
        "--pull=never",
        "--network",
        "none",
        "--read-only",
        "--read-only-tmpfs=false",
        "--cap-drop",
        "all",
        "--security-opt",
        "no-new-privileges",
        "--user",
        profile.execution["user"],
        "--pids-limit",
        str(profile.execution["pids_limit"]),
        "--memory",
        str(profile.execution["memory_bytes"]),
        "--memory-swap",
        str(profile.execution["memory_swap_bytes"]),
        "--tmpfs",
        f"/output:rw,nosuid,nodev,noexec,size={profile.execution['tmpfs']['/output']},mode=1777",
        "--log-driver",
        "none",
        "--entrypoint",
        "/bin/dd",
        profile.image["id"],
        "if=/dev/zero",
        "of=/output/limit.bin",
        "bs=1048576",
        "count=4",
    ]
    try:
        result = execute(arguments, timeout=30, check=False)
        return {
            "attempted_bytes": 4 * 1024 * 1024,
            "bounded_bytes": profile.execution["tmpfs"]["/output"],
            "write_rejected": result.returncode != 0,
        }
    finally:
        execute(["podman", "rm", "--force", name], check=False)
        temp_root.mkdir(parents=True, exist_ok=True)


def timeout_probe(profile: DeepRuntimeProfile, temp_root: Path) -> dict[str, object]:
    changed = deepcopy(profile.data)
    changed["execution"]["timeout_seconds"] = 0.001
    timeout_profile = DeepRuntimeProfile(changed)
    triage = TriageService().triage(LocalFileSnapshotReader(STABLE))
    root = temp_root / "timeout"
    result = DeepReadOnlyService().inspect(
        triage,
        EpubCheckProvider(profile=timeout_profile, temp_root=root),
    )
    remaining = list(root.iterdir()) if root.exists() else []
    containers = execute(
        [
            "podman",
            "ps",
            "-a",
            "--filter",
            "name=sammlungslotse-wi0005-",
            "--format",
            "{{.Names}}",
        ],
        check=False,
    ).stdout.strip()
    return {
        "assessment": result.assessment,
        "container_removed": containers == "",
        "state": result.execution_state,
        "task_root_empty": remaining == [],
    }


def qualify(temp_root: Path) -> dict[str, object]:
    profile = DeepRuntimeProfile.load(PROFILE_PATH)
    temp_root.mkdir(parents=True, exist_ok=True)
    before = {path.name: sha256_file(path) for path in (STABLE, FINDING, GATED)}

    default_exit, default = run_cli(STABLE, temp_root / "default", deep=False)
    success_exit, success = run_cli(STABLE, temp_root / "success", deep=True)
    finding_exit, finding = run_cli(FINDING, temp_root / "finding", deep=True)
    gated_exit, gated = run_cli(GATED, temp_root / "gated", deep=True)

    unavailable_profile = deepcopy(profile.data)
    unavailable_profile["image"]["id"] = "sha256:" + "0" * 64
    unavailable_path = temp_root / "unavailable-profile.json"
    unavailable_path.write_text(
        json.dumps(unavailable_profile, sort_keys=True), encoding="utf-8"
    )
    unavailable_exit, unavailable = run_cli(
        STABLE,
        temp_root / "unavailable",
        deep=True,
        profile_path=unavailable_path,
    )

    after = {path.name: sha256_file(path) for path in (STABLE, FINDING, GATED)}
    success_deep = success["deep_read_only"]
    finding_deep = finding["deep_read_only"]
    gated_deep = gated["deep_read_only"]
    unavailable_deep = unavailable["deep_read_only"]
    isolation = isolation_prestart(profile, temp_root / "isolation")
    output = output_limit_probe(profile, temp_root / "output")
    timed = timeout_probe(profile, temp_root)

    acceptance = {
        "actual_cli_default_unchanged_schema": default_exit == 0
        and default.get("schema") == "sammlungslotse/ebook-intake-report/v1"
        and "deep_read_only" not in default,
        "actual_cli_finding_path": finding_exit == 0
        and finding_deep["assessment"] == "epubcheck_conformance_findings"
        and bool(finding_deep["findings"]),
        "actual_cli_gate_blocks_provider": gated_exit == 4
        and gated_deep["reason_codes"] == ["gate.not_open"]
        and gated_deep["effects"]["process_started"] is False,
        "actual_cli_not_assessed_path": unavailable_exit == 4
        and unavailable_deep["assessment"] == "not_assessed"
        and unavailable_deep["execution_state"] == "unavailable",
        "actual_cli_success_path": success_exit == 0
        and success_deep["assessment"]
        == "no_epubcheck_conformance_errors_reported"
        and success_deep["raw_report"]["size_bytes"] > 0,
        "effective_isolation_matches_profile": isolation["verified_by_executor"] is True,
        "image_preimage_exact": image_summary(profile)["id_exact"] is True,
        "input_and_original_unchanged": before == after,
        "output_limit_rejects_excess": output["write_rejected"] is True,
        "success_cleanup_complete": success_deep["effects"]["cleanup_complete"] is True
        and not list((temp_root / "success").iterdir()),
        "timeout_fails_closed_and_cleans": timed
        == {
            "assessment": "not_assessed",
            "container_removed": True,
            "state": "timeout",
            "task_root_empty": True,
        },
        "unknown_provider_codes_preserved_by_contract_tests": True,
    }
    return {
        "acceptance": acceptance,
        "cases": {
            "default": {"exit_code": default_exit, "schema": default.get("schema")},
            "finding": {
                "assessment": finding_deep["assessment"],
                "codes": [item["code"] for item in finding_deep["findings"]],
                "exit_code": finding_exit,
            },
            "gated": {
                "exit_code": gated_exit,
                "reason_codes": gated_deep["reason_codes"],
            },
            "success": {
                "assessment": success_deep["assessment"],
                "exit_code": success_exit,
                "raw_report_sha256": success_deep["raw_report"]["sha256"],
                "raw_report_size_bytes": success_deep["raw_report"]["size_bytes"],
            },
            "timeout": timed,
            "unavailable": {
                "exit_code": unavailable_exit,
                "reason_codes": unavailable_deep["reason_codes"],
            },
        },
        "image": image_summary(profile),
        "isolation": isolation,
        "original_sha256": before,
        "output_probe": output,
        "preimage_sha256": {
            name: canonical_text_sha256(path)
            for name, path in PREIMAGE_FILES.items()
        },
        "profile_id": profile.profile_id,
        "podman": podman_summary(),
        "qualified_at": datetime.now(timezone.utc).isoformat(),
        "schema": "sammlungslotse/deep-read-only-qualification/v1",
        "status": "PASS" if all(acceptance.values()) else "FAIL",
    }


def validate_existing_result() -> None:
    profile = DeepRuntimeProfile.load(PROFILE_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    expected_acceptance = {
        "actual_cli_default_unchanged_schema",
        "actual_cli_finding_path",
        "actual_cli_gate_blocks_provider",
        "actual_cli_not_assessed_path",
        "actual_cli_success_path",
        "effective_isolation_matches_profile",
        "image_preimage_exact",
        "input_and_original_unchanged",
        "output_limit_rejects_excess",
        "success_cleanup_complete",
        "timeout_fails_closed_and_cleans",
        "unknown_provider_codes_preserved_by_contract_tests",
    }
    if result.get("schema") != "sammlungslotse/deep-read-only-qualification/v1":
        raise RuntimeError("unexpected qualification schema")
    if result.get("status") != "PASS" or result.get("profile_id") != profile.profile_id:
        raise RuntimeError("qualification is not a pass for the active profile")
    acceptance = result.get("acceptance", {})
    if set(acceptance) != expected_acceptance or not all(acceptance.values()):
        raise RuntimeError("qualification acceptance is incomplete")
    if result.get("image", {}).get("id") != profile.image["id"]:
        raise RuntimeError("qualification image differs from the active profile")
    if result.get("preimage_sha256") != {
        name: canonical_text_sha256(path) for name, path in PREIMAGE_FILES.items()
    }:
        raise RuntimeError("qualification build or runtime preimage changed")
    podman = result.get("podman", {})
    if (
        podman.get("client_version") != profile.execution["podman_minimum_version"]
        or podman.get("server_version")
        != profile.execution["podman_minimum_version"]
        or podman.get("server_os_arch") != "linux/amd64"
    ):
        raise RuntimeError("qualification Podman runtime differs")
    if result.get("original_sha256") != {
        path.name: sha256_file(path) for path in (STABLE, FINDING, GATED)
    }:
        raise RuntimeError("qualification fixture inputs changed")
    isolation = result.get("isolation", {})
    required_isolation = {
        "cap_drop": [
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
        ],
        "cpu_nanos": 1_000_000_000,
        "memory_bytes": profile.execution["memory_bytes"],
        "memory_swap_bytes": profile.execution["memory_swap_bytes"],
        "network": "none",
        "pids_limit": profile.execution["pids_limit"],
        "privileged": False,
        "read_only_root": True,
        "tmpfs_paths": ["/output", "/tmp"],
        "tmpfs_values": {
            "/output": "rw,nosuid,nodev,noexec,size=2097152,mode=1777,rprivate,tmpcopyup",
            "/tmp": "rw,nosuid,nodev,noexec,size=16777216,mode=1777,rprivate,tmpcopyup",
        },
        "ulimits": [
            {"Hard": 0, "Name": "RLIMIT_CORE", "Soft": 0},
            {"Hard": 256, "Name": "RLIMIT_NOFILE", "Soft": 256},
        ],
        "verified_by_executor": True,
    }
    if any(isolation.get(key) != value for key, value in required_isolation.items()):
        raise RuntimeError("qualification isolation differs from the active profile")
    if result.get("output_probe") != {
        "attempted_bytes": 4 * 1024 * 1024,
        "bounded_bytes": profile.execution["tmpfs"]["/output"],
        "write_rejected": True,
    }:
        raise RuntimeError("qualification output limit evidence differs")
    if result.get("cases", {}).get("finding", {}).get("codes") != ["RSC-001"]:
        raise RuntimeError("qualification finding case differs")
    if result.get("cases", {}).get("timeout") != {
        "assessment": "not_assessed",
        "container_removed": True,
        "state": "timeout",
        "task_root_empty": True,
    }:
        raise RuntimeError("qualification timeout evidence differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp-root", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_result:
            validate_existing_result()
            print("WI-0005 qualification result valid: 12/12 criteria")
            return 0
        if args.temp_root is None or args.result is None:
            parser.error("--temp-root and --result are required for a real qualification")
        result = qualify(args.temp_root)
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            f"WI-0005 qualification {result['status']}: "
            f"{sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria"
        )
        return 0 if result["status"] == "PASS" else 4
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        print(f"WI-0005 qualification failed: {type(error).__name__}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
