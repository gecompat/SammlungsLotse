#!/usr/bin/env python3
"""Offline-only Docker preflight for the separate EXP-0021 evidence wave."""

from __future__ import annotations

import json
import subprocess
from typing import Any


class DockerPreflightError(RuntimeError):
    """The local Docker runtime cannot establish the bound experiment shape."""


def execute(arguments: list[str]) -> str:
    """Run a bounded read-only Docker query; never provision or start anything."""

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
    if completed.returncode != 0:
        raise DockerPreflightError("docker_query_unavailable")
    return completed.stdout


def _image_id(value: dict[str, Any]) -> str:
    image_id = str(value.get("Id", ""))
    return image_id if image_id.startswith("sha256:") else f"sha256:{image_id}"


def inspect_image(profile: dict[str, Any]) -> dict[str, Any]:
    """Require an already-local exact image; this intentionally has no fallback."""

    image = profile["image"]
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


def inspect_isolation(container_name: str, profile: dict[str, Any]) -> dict[str, Any]:
    """Validate a previously-created experiment container before it may start."""

    values = json.loads(execute(["docker", "container", "inspect", container_name]))
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        raise DockerPreflightError("docker_container_inspect_invalid")
    value = values[0]
    execution = profile["execution"]
    host = value.get("HostConfig", {})
    config = value.get("Config", {})
    mounts = {item.get("Destination"): item for item in value.get("Mounts", [])}
    tmpfs = host.get("Tmpfs") or {}
    expected_image = profile["image"]["id"]
    actual_image = str(value.get("Image", ""))
    if actual_image and not actual_image.startswith("sha256:"):
        actual_image = f"sha256:{actual_image}"
    expected_tmpfs = {
        "/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777",
        "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777",
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
        and mounts.get("/library", {}).get("RW") is True
        and mounts.get("/output", {}).get("RW") is True
        and set(mounts) == {"/library", "/output"}
        and tmpfs == expected_tmpfs
        and config.get("Entrypoint") == profile["image"]["entrypoint"]
        and (host.get("LogConfig") or {}).get("Type") == "none"
    ):
        raise DockerPreflightError("docker_isolation_contract_differs")
    return value
