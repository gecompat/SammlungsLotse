"""Strict contract for a future Docker-bound Calibre runtime.

This profile is deliberately separate from the historical WI-0007 Podman
profile.  Loading a Docker profile never changes the selected runtime of an
existing caller.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROFILE_SCHEMA = "sammlungslotse/calibre-docker-read-only-runtime-profile/v1"
HEX128 = re.compile(r"^[0-9a-f]{128}$")
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True, slots=True)
class DockerCalibreRuntimeProfile:
    """Validated Docker-only preimage; it is not a Podman compatibility shim."""

    data: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> "DockerCalibreRuntimeProfile":
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("profile root must be an object")
        result = cls(value)
        result.validate()
        return result

    @property
    def profile_id(self) -> str:
        return self.data["profile_id"]

    @property
    def provider(self) -> dict[str, Any]:
        return self.data["provider"]

    @property
    def image(self) -> dict[str, Any]:
        return self.data["image"]

    @property
    def execution(self) -> dict[str, Any]:
        return self.data["execution"]

    @property
    def workspace(self) -> dict[str, Any]:
        return self.data["workspace"]

    def validate(self) -> None:
        data = self.data
        if data.get("schema") != PROFILE_SCHEMA:
            raise ValueError("unsupported Docker profile schema")
        if not isinstance(data.get("profile_id"), str) or "docker" not in data["profile_id"]:
            raise ValueError("Docker profile identity differs")
        provider = self.provider
        if provider.get("id") != "calibre" or provider.get("version") != "9.13.0":
            raise ValueError("unexpected Calibre provider")
        if provider.get("license_spdx") != "GPL-3.0-only":
            raise ValueError("unexpected Calibre license")
        if provider.get("artifact_bytes") != 192554776 or not HEX128.fullmatch(str(provider.get("artifact_sha512", ""))):
            raise ValueError("invalid Calibre artifact binding")
        if not str(provider.get("artifact_url", "")).startswith("https://download.calibre-ebook.com/"):
            raise ValueError("invalid Calibre artifact URL")
        image = self.image
        if not IMAGE_ID.fullmatch(str(image.get("id", ""))) or image.get("platform") != "linux/amd64":
            raise ValueError("Docker image binding differs")
        entrypoint = image.get("entrypoint")
        if not isinstance(entrypoint, list) or not all(isinstance(item, str) for item in entrypoint):
            raise ValueError("Docker image entrypoint differs")
        if image.get("command") != [] or not isinstance(image.get("container_environment"), list) or not all(
            isinstance(item, str) for item in image["container_environment"]
        ):
            raise ValueError("Docker image command or environment differs")
        base = data.get("base_image", {})
        if "@sha256:" not in str(base.get("reference", "")) or not IMAGE_ID.fullmatch(str(base.get("config_id", ""))):
            raise ValueError("Docker base image is not digest-bound")
        execution = self.execution
        exact = {
            "network": "none", "user": "65532:65532", "read_only_root": True,
            "cap_drop": ["ALL"], "no_new_privileges": True, "pids_limit": 64,
            "cpus": "1.0", "memory_bytes": 1073741824,
            "memory_swap_bytes": 1073741824, "timeout_seconds": 30,
            "stdout_max_bytes": 4194304, "stderr_max_bytes": 131072,
            "raw_report_max_bytes": 4194304, "provider_arguments": [],
            "tmpfs": {
                "/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777",
                "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777",
            },
        }
        for key, expected in exact.items():
            if execution.get(key) != expected:
                raise ValueError(f"unexpected Docker execution value: {key}")
        if not VERSION.fullmatch(str(execution.get("docker_minimum_version", ""))):
            raise ValueError("invalid Docker minimum version")
        expected_env = {
            "CALIBRE_CONFIG_DIRECTORY": "/config", "HOME": "/tmp/home", "LANG": "C.UTF-8",
            "PATH": "/opt/calibre:/usr/local/bin:/usr/bin:/bin", "QT_QPA_PLATFORM": "offscreen",
        }
        if execution.get("environment") != expected_env:
            raise ValueError("unexpected Docker environment")
        if set(image["container_environment"]) != {
            f"{key}={value}" for key, value in expected_env.items()
        }:
            raise ValueError("unexpected Docker container environment")
        workspace = self.workspace
        for key in ("marker_schema", "max_children", "max_task_age_seconds", "max_files", "max_total_bytes", "max_file_bytes", "max_depth", "max_relative_path_bytes"):
            if key not in workspace:
                raise ValueError(f"missing workspace value: {key}")
