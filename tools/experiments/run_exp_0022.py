#!/usr/bin/env python3
"""Product-code-free synthetic Docker/Podman Calibre projection comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "experiments"))
import run_exp_0021 as docker  # noqa: E402

DOCKER_PROFILE = ROOT / "experiments" / "ebook" / "exp-0021" / "profile.json"
PODMAN_PROFILE = ROOT / "runtime" / "calibre-readonly" / "profile.json"
SCHEMA = "sammlungslotse/exp-0022-docker-podman-equivalence-result/v1"
PODMAN_CAP_DROP_ALL = {
    "CAP_CHOWN", "CAP_DAC_OVERRIDE", "CAP_FOWNER", "CAP_FSETID", "CAP_KILL", "CAP_NET_BIND_SERVICE",
    "CAP_SETFCAP", "CAP_SETGID", "CAP_SETPCAP", "CAP_SETUID", "CAP_SYS_CHROOT",
}
PODMAN_TMPFS_BASE = {
    "/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777",
    "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777",
}
PODMAN_TMPFS_SUFFIX = ",rprivate,tmpcopyup"


class EquivalenceError(RuntimeError):
    """A runtime cannot establish the bounded comparison contract."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_projection_digest(payload: bytes) -> str:
    """Hash only the documented minimal projection, never a path or raw report."""

    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, list):
        raise EquivalenceError("projection_root_invalid")
    normalized = []
    for item in value:
        if not isinstance(item, dict) or not set(item).issubset({"id", "_source_id", "title", "authors", "languages", "formats"}):
            raise EquivalenceError("projection_fields_invalid")
        identifier = item.get("id", item.get("_source_id"))
        if isinstance(identifier, bool) or not isinstance(identifier, int):
            raise EquivalenceError("projection_identifier_invalid")
        normalized.append({
            "id": identifier,
            "title": item.get("title", ""),
            "authors": item.get("authors", []),
            "languages": item.get("languages", []),
            "formats": item.get("formats", []),
        })
    encoded = json.dumps(sorted(normalized, key=lambda item: item["id"]), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _podman(arguments: list[str], *, timeout: int = 30, stdout_limit: int = 4 * 1024 * 1024) -> bytes:
    try:
        completed = subprocess.run(arguments, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EquivalenceError("podman_runtime_unavailable") from exc
    if completed.returncode != 0 or len(completed.stdout) > stdout_limit or len(completed.stderr) > 128 * 1024:
        raise EquivalenceError("podman_command_failed")
    return completed.stdout


def _podman_image(profile: dict[str, Any]) -> None:
    value = json.loads(_podman(["podman", "image", "inspect", profile["image"]["tag"], "--format", "json"], timeout=15))[0]
    identifier = str(value.get("Id", ""))
    identifier = identifier if identifier.startswith("sha256:") else f"sha256:{identifier}"
    if not (identifier == profile["image"]["id"] and value.get("Os") == "linux" and value.get("Architecture") == "amd64" and value.get("Config", {}).get("Entrypoint") == profile["image"]["entrypoint"]):
        raise EquivalenceError("podman_image_contract_differs")


def _podman_capdrop_matches(value: object) -> bool:
    return isinstance(value, list) and set(value) == PODMAN_CAP_DROP_ALL and len(value) == len(PODMAN_CAP_DROP_ALL)


def _podman_ulimits_match(value: object) -> bool:
    if not isinstance(value, list) or len(value) != 2:
        return False
    expected = {"core": ("core", "RLIMIT_CORE", 0, 0), "nofile": ("nofile", "RLIMIT_NOFILE", 256, 256)}
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            return False
        for key, (short, observed, soft, hard) in expected.items():
            if item.get("Name") in (short, observed):
                if key in seen or item.get("Soft") != soft or item.get("Hard") != hard:
                    return False
                seen.add(key)
                break
        else:
            return False
    return seen == set(expected)


def _podman_tmpfs_matches(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != set(PODMAN_TMPFS_BASE):
        return False
    return all(value[key] == f"{base}{PODMAN_TMPFS_SUFFIX}" for key, base in PODMAN_TMPFS_BASE.items())


def _podman_projection(library: Path, output: Path, profile: dict[str, Any]) -> str:
    _podman_image(profile)
    name = f"sammlungslotse-exp0022-podman-{uuid.uuid4().hex[:12]}"
    execution = profile["execution"]
    create = [
        "podman", "create", "--name", name, "--pull=never", "--network", "none", "--http-proxy=false", "--read-only", "--read-only-tmpfs=false", "--cap-drop", "all", "--security-opt", "no-new-privileges", "--user", execution["user"], "--pids-limit", str(execution["pids_limit"]), "--cpus", execution["cpus"], "--memory", str(execution["memory_bytes"]), "--memory-swap", str(execution["memory_swap_bytes"]), "--ulimit", "core=0:0", "--ulimit", "nofile=256:256", "--log-driver", "none", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=67108864,mode=1777", "--tmpfs", "/config:rw,nosuid,nodev,noexec,size=16777216,mode=1777", "--mount", f"type=bind,source={library},target=/library,rw=true", "--mount", f"type=bind,source={output},target=/output,rw=true", profile["image"]["id"],
    ]
    created = False
    try:
        _podman(create, timeout=15, stdout_limit=4096)
        created = True
        inspected = json.loads(_podman(["podman", "inspect", name, "--format", "json"], timeout=15, stdout_limit=262144))[0]
        host, config = inspected.get("HostConfig", {}), inspected.get("Config", {})
        mounts = {item.get("Destination"): item for item in inspected.get("Mounts", [])}
        image = str(inspected.get("Image", ""))
        image = image if image.startswith("sha256:") else f"sha256:{image}"
        if not (image == profile["image"]["id"] and host.get("NetworkMode") == "none" and host.get("ReadonlyRootfs") is True and config.get("User") == execution["user"] and host.get("Privileged") is False and host.get("CapAdd") in (None, []) and _podman_capdrop_matches(host.get("CapDrop")) and set(host.get("SecurityOpt") or []) == {"no-new-privileges"} and host.get("PidsLimit") == execution["pids_limit"] and host.get("Memory") == execution["memory_bytes"] and host.get("MemorySwap") == execution["memory_swap_bytes"] and host.get("NanoCpus") == 1_000_000_000 and _podman_ulimits_match(host.get("Ulimits")) and _podman_tmpfs_matches(host.get("Tmpfs")) and (host.get("LogConfig") or {}).get("Type") == "none" and mounts.get("/library", {}).get("RW") is True and mounts.get("/output", {}).get("RW") is True and set(mounts) == {"/library", "/output"} and config.get("Entrypoint") == profile["image"]["entrypoint"]):
            raise EquivalenceError("podman_isolation_contract_differs")
        _podman(["podman", "start", "--attach", name], timeout=int(execution["timeout_seconds"]))
        report = output / "report.json"
        if not report.is_file() or report.stat().st_size > int(execution["raw_report_max_bytes"]):
            raise EquivalenceError("podman_projection_contract_invalid")
        return normalized_projection_digest(report.read_bytes())
    finally:
        if created:
            _podman(["podman", "rm", "--force", name], timeout=15, stdout_limit=4096)


def compare(
    materialize: Callable[[Path, Path, dict[str, Any]], None], docker_project: Callable[[Path, Path, dict[str, Any]], str], podman_project: Callable[[Path, Path, dict[str, Any]], str], docker_profile: dict[str, Any], podman_profile: dict[str, Any], *, root: Path | None = None
) -> dict[str, Any]:
    """Compare two repetitions per runtime over precisely one shared task library."""

    task = Path(tempfile.mkdtemp(prefix="sammlungslotse-exp0022-")) if root is None else root
    if root is not None:
        task.mkdir(parents=True, exist_ok=False)
    library, materialized = task / "library", task / "materialize"
    library.mkdir(); materialized.mkdir()
    try:
        materialize(library, materialized, docker_profile)
        before = docker.sha256_tree(library)
        projections: dict[str, list[str]] = {"docker": [], "podman": []}
        for runtime, project, profile in (("docker", docker_project, docker_profile), ("podman", podman_project, podman_profile)):
            for repetition in range(2):
                output = task / f"{runtime}-{repetition}"
                output.mkdir()
                projections[runtime].append(project(library, output, profile))
                shutil.rmtree(output)
        unchanged = before == docker.sha256_tree(library)
        passed = unchanged and len(set(projections["docker"])) == 1 and len(set(projections["podman"])) == 1 and projections["docker"][0] == projections["podman"][0]
        return {"artifact": "EXP-0022", "schema": SCHEMA, "status": "pass" if passed else "not_qualified", "repetitions_per_runtime": 2, "projection_sha256": projections, "library_snapshot_unchanged": unchanged, "cleanup": {"containers_removed_by_runtime": True, "task_root_removed_on_return": True}, "synthetic_only": True, "runtime_bindings": {"docker_image_id": docker_profile["docker_image"]["id"], "podman_image_id": podman_profile["image"]["id"], "docker_platform": "linux/amd64", "podman_platform": podman_profile["image"]["platform"]}, "effects": {"external_network_access": False, "persistence": False, "import": False, "writer_effects": False, "product_code_modified": False}}
    except (EquivalenceError, docker.DockerPreflightError):
        return {"artifact": "EXP-0022", "schema": SCHEMA, "status": "not_qualified", "repetitions_per_runtime": 0, "synthetic_only": True, "effects": {"external_network_access": False, "persistence": False, "import": False, "writer_effects": False, "product_code_modified": False}}
    finally:
        shutil.rmtree(task, ignore_errors=True)


def run() -> dict[str, Any]:
    docker_profile, podman_profile = load_json(DOCKER_PROFILE), load_json(PODMAN_PROFILE)
    return compare(docker._materialize_empty_library, docker._project, _podman_projection, docker_profile, podman_profile)


def main() -> int:
    result = run()
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "pass" else 4


if __name__ == "__main__":
    raise SystemExit(main())
