#!/usr/bin/env python3
"""Offline-only Docker preflight for the separate EXP-0021 evidence wave."""

from __future__ import annotations

import argparse
import json
import hashlib
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any


class DockerPreflightError(RuntimeError):
    """The local Docker runtime cannot establish the bound experiment shape."""


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "experiments" / "ebook" / "exp-0021" / "profile.json"
TMPFS = {
    "/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777",
    "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777",
}
LIMITS = {"pids_limit": 64, "memory_bytes": 1073741824, "memory_swap_bytes": 1073741824}
STDOUT_LIMIT = 4 * 1024 * 1024
STDERR_LIMIT = 128 * 1024
START_TIMEOUT_SECONDS = 30


def execute(arguments: list[str]) -> str:
    """Run one bounded Docker command in the preflight or disposable task."""

    try:
        completed = subprocess.run(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=15,
        )
    except subprocess.TimeoutExpired as exc:
        raise DockerPreflightError("docker_query_timeout") from exc
    if completed.returncode != 0:
        raise DockerPreflightError("docker_query_unavailable")
    return completed.stdout


def execute_attached(arguments: list[str]) -> bytes:
    """Start one task container under its own bounded execution contract."""

    try:
        completed = subprocess.run(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=START_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise DockerPreflightError("docker_container_timeout") from exc
    if completed.returncode != 0:
        raise DockerPreflightError("docker_container_failed")
    if len(completed.stdout) > STDOUT_LIMIT or len(completed.stderr) > STDERR_LIMIT:
        raise DockerPreflightError("docker_container_output_limit")
    return completed.stdout


def _image_id(value: dict[str, Any]) -> str:
    image_id = str(value.get("Id", ""))
    return image_id if image_id.startswith("sha256:") else f"sha256:{image_id}"


def bound_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Accept the checked-in Docker profile and compact unit-test fixtures."""

    image = profile.get("image", profile.get("docker_image"))
    if not isinstance(image, dict):
        raise DockerPreflightError("docker_profile_image_missing")
    execution = dict(LIMITS)
    execution.update(profile.get("execution", {}))
    execution.setdefault("user", "65532:65532")
    execution.setdefault("stdout_max_bytes", STDOUT_LIMIT)
    execution.setdefault("stderr_max_bytes", STDERR_LIMIT)
    execution.setdefault("timeout_seconds", START_TIMEOUT_SECONDS)
    return {"image": image, "execution": execution}


def inspect_image(profile: dict[str, Any]) -> dict[str, Any]:
    """Require an already-local exact image; this intentionally has no fallback."""

    image = bound_profile(profile)["image"]
    values = json.loads(execute(["docker", "image", "inspect", image["tag"]]))
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        raise DockerPreflightError("docker_image_inspect_invalid")
    value = values[0]
    if (
        _image_id(value) != image["id"]
        or value.get("Os") != "linux"
        or value.get("Architecture") != "amd64"
        or value.get("Config", {}).get("Entrypoint") != image["entrypoint"]
    ):
        raise DockerPreflightError("docker_image_contract_differs")
    return value


def inspect_isolation(
    container_name: str, profile: dict[str, Any], *, expected_entrypoint: list[str] | None = None
) -> dict[str, Any]:
    """Validate a previously-created experiment container before it may start."""

    values = json.loads(execute(["docker", "container", "inspect", container_name]))
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        raise DockerPreflightError("docker_container_inspect_invalid")
    value = values[0]
    profile = bound_profile(profile)
    execution = profile["execution"]
    host = value.get("HostConfig", {})
    config = value.get("Config", {})
    mounts = {item.get("Destination"): item for item in value.get("Mounts", [])}
    tmpfs = host.get("Tmpfs") or {}
    expected_image = profile["image"]["id"]
    actual_image = str(value.get("Image", ""))
    if actual_image and not actual_image.startswith("sha256:"):
        actual_image = f"sha256:{actual_image}"
    expected_tmpfs = TMPFS
    expected_entrypoint = expected_entrypoint or profile["image"]["entrypoint"]
    ulimits = {
        (str(item.get("Name")), str(item.get("Soft")), str(item.get("Hard")))
        for item in host.get("Ulimits") or []
        if isinstance(item, dict)
    }
    if not (
        actual_image == expected_image
        and host.get("NetworkMode") == "none"
        and host.get("ReadonlyRootfs") is True
        and config.get("User") == execution["user"]
        and host.get("Privileged") is False
        and host.get("CapAdd") in (None, [])
        and set(host.get("CapDrop") or []) == {"ALL"}
        and set(host.get("SecurityOpt") or []) == {"no-new-privileges"}
        and host.get("PidsLimit") == execution["pids_limit"]
        and host.get("Memory") == execution["memory_bytes"]
        and host.get("MemorySwap") == execution["memory_swap_bytes"]
        and host.get("NanoCpus") == 1_000_000_000
        and ulimits == {("core", "0", "0"), ("nofile", "256", "256")}
        and mounts.get("/library", {}).get("RW") is True
        and mounts.get("/output", {}).get("RW") is True
        and set(mounts) == {"/library", "/output"}
        and tmpfs == expected_tmpfs
        and config.get("Entrypoint") == expected_entrypoint
        and (host.get("LogConfig") or {}).get("Type") == "none"
    ):
        raise DockerPreflightError("docker_isolation_contract_differs")
    return value


def sha256_tree(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_bindings(profile: dict[str, Any], profile_path: Path = PROFILE_PATH) -> dict[str, str]:
    """Return deterministic, public metadata for a later checked-in result."""

    image = bound_profile(profile)["image"]
    platform = f"{image.get('os', 'linux')}/{image.get('architecture', 'amd64')}"
    return {
        "docker_image_id": str(image["id"]),
        "docker_platform": platform,
        "method": "docker-synthetic-empty-library-two-exact-entrypoint-projections/v1",
        "profile_sha256": sha256_file(profile_path),
        "runner_sha256": sha256_file(Path(__file__)),
    }


def _create_command(
    name: str, library: Path, output: Path, profile: dict[str, Any], command: list[str], *, entrypoint: str | None = None
) -> list[str]:
    """The only container shape accepted by this evidence runner."""

    profile = bound_profile(profile)
    execution = profile["execution"]
    arguments = [
        "docker", "create", "--name", name, "--pull=never", "--network=none", "--read-only",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", execution["user"],
        "--pids-limit", str(execution["pids_limit"]), "--cpus", "1.0", "--memory", str(execution["memory_bytes"]),
        "--memory-swap", str(execution["memory_swap_bytes"]), "--ulimit", "core=0:0", "--ulimit", "nofile=256:256",
        "--log-driver", "none", "--tmpfs", f"/tmp:{TMPFS['/tmp']}", "--tmpfs", f"/config:{TMPFS['/config']}",
        # Docker bind mounts are read-write by default.  Unlike Podman, Docker
        # rejects the non-standard `rw=true` key, while inspect still proves RW.
        "--mount", f"type=bind,source={library},target=/library",
        "--mount", f"type=bind,source={output},target=/output",
    ]
    if entrypoint is not None:
        arguments.extend(("--entrypoint", entrypoint))
    return [*arguments, profile["image"]["tag"], *command]


def _run_container(name: str, create: list[str], profile: dict[str, Any], *, entrypoint: list[str]) -> bytes:
    """Create, inspect, start and remove one bounded container."""

    created = False
    try:
        execute(create)
        created = True
        inspect_isolation(name, profile, expected_entrypoint=entrypoint)
        return execute_attached(["docker", "start", "--attach", name])
    finally:
        if created:
            try:
                execute(["docker", "rm", "--force", name])
            except DockerPreflightError as exc:
                raise DockerPreflightError("docker_cleanup_failed") from exc


def _materialize_empty_library(library: Path, output: Path, profile: dict[str, Any]) -> None:
    """The one controlled write is confined to a new synthetic task library."""

    name = f"sammlungslotse-exp0021-materialize-{uuid.uuid4().hex[:12]}"
    command = ["-i", "CALIBRE_CONFIG_DIRECTORY=/config", "HOME=/tmp/home",
               "LANG=C.UTF-8", "PATH=/opt/calibre:/usr/local/bin:/usr/bin:/bin", "QT_QPA_PLATFORM=offscreen",
               "calibredb", "add", "--with-library", "/library", "--title", "Synthetic EXP-0021", "--authors", "Test", "--empty"]
    _run_container(
        name, _create_command(name, library, output, profile, command, entrypoint="/usr/bin/env"), profile,
        entrypoint=["/usr/bin/env"],
    )


def _project(library: Path, output: Path, profile: dict[str, Any]) -> str:
    name = f"sammlungslotse-exp0021-project-{uuid.uuid4().hex[:12]}"
    _run_container(name, _create_command(name, library, output, profile, []), profile, entrypoint=bound_profile(profile)["image"]["entrypoint"])
    report = output / "report.json"
    complete = output / "complete.json"
    if not report.is_file() or not complete.is_file() or json.loads(complete.read_text(encoding="utf-8")).get("exit_code") != 0:
        raise DockerPreflightError("docker_projection_contract_invalid")
    value = json.loads(report.read_text(encoding="utf-8"))
    if not isinstance(value, list) or len(value) != 1:
        raise DockerPreflightError("docker_projection_contract_invalid")
    return hashlib.sha256(report.read_bytes()).hexdigest()


def run_synthetic(profile: dict[str, Any], *, task_root: Path | None = None) -> dict[str, Any]:
    """Run the minimal two-repetition Docker evidence path; never touch a real library."""

    inspect_image(profile)
    parent = Path(tempfile.mkdtemp(prefix="sammlungslotse-exp0021-")) if task_root is None else task_root
    if task_root is not None:
        parent.mkdir(parents=True, exist_ok=False)
    library, materialize_output = parent / "library", parent / "materialize-output"
    library.mkdir()
    materialize_output.mkdir()
    try:
        _materialize_empty_library(library, materialize_output, profile)
        before = sha256_tree(library)
        hashes = []
        for _ in range(2):
            output = parent / f"projection-{len(hashes)}"
            output.mkdir()
            hashes.append(_project(library, output, profile))
            shutil.rmtree(output)
        after = sha256_tree(library)
        accepted = before == after and len(hashes) == 2 and hashes[0] == hashes[1]
        return {"artifact": "EXP-0021", "bindings": evidence_bindings(profile), "schema": "sammlungslotse/exp-0021-docker-result/v1", "status": "pass" if accepted else "not_qualified", "repetitions": 2, "projection_sha256": hashes, "library_snapshot_unchanged": before == after, "synthetic_only": True, "effects": {"external_network_access": False, "persistence": False, "import": False, "writer_effects": False, "product_code_modified": False}}
    except DockerPreflightError:
        return {"artifact": "EXP-0021", "bindings": evidence_bindings(profile), "schema": "sammlungslotse/exp-0021-docker-result/v1", "status": "not_qualified", "repetitions": 0, "synthetic_only": True, "effects": {"external_network_access": False, "persistence": False, "import": False, "writer_effects": False, "product_code_modified": False}}
    finally:
        shutil.rmtree(parent, ignore_errors=True)


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("artifact") != "EXP-0021" or value.get("synthetic_only") is not True:
        raise DockerPreflightError("docker_profile_contract_differs")
    bound_profile(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    result = run_synthetic(load_profile(), task_root=args.task_root)
    encoded = json.dumps(result, sort_keys=True) + "\n"
    if args.result is None:
        print(encoded, end="")
    else:
        args.result.write_text(encoded, encoding="utf-8", newline="\n")
    return 0 if result["status"] == "pass" else 4


if __name__ == "__main__":
    raise SystemExit(main())
