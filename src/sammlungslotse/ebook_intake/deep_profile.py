"""Strict loader for the checked-in WI-0005 process preimage."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROFILE_SCHEMA = "sammlungslotse/deep-read-only-runtime-profile/v1"
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class DeepRuntimeProfile:
    """Validated immutable values used by materializer, executor and provider."""

    data: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> "DeepRuntimeProfile":
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
    def execution(self) -> dict[str, Any]:
        return self.data["execution"]

    @property
    def image(self) -> dict[str, Any]:
        return self.data["image"]

    @property
    def provider(self) -> dict[str, Any]:
        return self.data["provider"]

    @property
    def workspace(self) -> dict[str, Any]:
        return self.data["workspace"]

    def validate(self) -> None:
        data = self.data
        if data.get("schema") != PROFILE_SCHEMA:
            raise ValueError("unsupported profile schema")
        if data.get("provider", {}).get("id") != "epubcheck":
            raise ValueError("unexpected provider")
        if data["provider"].get("version") != "5.3.0":
            raise ValueError("unexpected EPUBCheck version")
        if data["provider"].get("license_spdx") != "BSD-3-Clause":
            raise ValueError("unexpected EPUBCheck license")
        for area in ("provider", "runtime", "build_runtime"):
            digest = data.get(area, {}).get("artifact_sha256", "")
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"invalid {area} artifact digest")
            if not str(data[area].get("artifact_url", "")).startswith("https://"):
                raise ValueError(f"invalid {area} artifact URL")

        image = data.get("image", {})
        if not SHA256.fullmatch(str(image.get("id", ""))):
            raise ValueError("image is not digest-bound")
        if image.get("platform") != "linux/amd64":
            raise ValueError("unsupported image platform")
        if image.get("entrypoint") != [
            "/opt/java/bin/java",
            "-cp",
            "/opt/adapter",
            "EpubCheckWrapper",
        ]:
            raise ValueError("unexpected image entrypoint")

        base = data.get("base_image", {})
        reference = str(base.get("reference", ""))
        if "@sha256:" not in reference or ":latest" in reference:
            raise ValueError("base image is not digest-bound")
        if not SHA256.fullmatch(str(base.get("config_id", ""))):
            raise ValueError("base image config is not bound")

        execution = data.get("execution", {})
        exact = {
            "cap_drop": ["all"],
            "cli_json_max_bytes": 3 * 1024 * 1024,
            "cpus": "1.0",
            "input_max_bytes": 32 * 1024 * 1024,
            "http_proxy": False,
            "log_driver": "none",
            "memory_bytes": 384 * 1024 * 1024,
            "memory_swap_bytes": 384 * 1024 * 1024,
            "network": "none",
            "no_new_privileges": True,
            "pids_limit": 32,
            "podman_minimum_version": "6.1.0",
            "provider_arguments": [
                "/input/input.epub",
                "--json",
                "/output/report.json",
            ],
            "raw_report_max_bytes": 1024 * 1024,
            "read_only_root": True,
            "read_only_tmpfs": False,
            "security_opt": ["no-new-privileges"],
            "stderr_max_bytes": 128 * 1024,
            "stdout_max_bytes": 128 * 1024,
            "timeout_seconds": 30,
            "tmpfs": {"/output": 2 * 1024 * 1024, "/tmp": 16 * 1024 * 1024},
            "ulimit_core": "0:0",
            "ulimit_nofile": "256:256",
            "user": "65532:65532",
        }
        for key, expected in exact.items():
            if execution.get(key) != expected:
                raise ValueError(f"unsafe execution value: {key}")
        if execution.get("environment") != {
            "HOME": "/tmp",
            "JAVA_HOME": "/opt/java",
            "LANG": "C.UTF-8",
            "PATH": "/opt/java/bin:/usr/bin:/bin",
            "container": "podman",
        }:
            raise ValueError("unexpected container environment")
        if int(execution["cli_json_max_bytes"]) < int(
            execution["raw_report_max_bytes"]
        ) * 2:
            raise ValueError("CLI output cannot retain the bounded raw report")

        workspace = data.get("workspace", {})
        if workspace != {
            "marker_schema": "sammlungslotse/deep-read-only-task/v1",
            "max_children": 128,
            "max_task_age_seconds": 86400,
            "max_task_bytes": 36 * 1024 * 1024,
        }:
            raise ValueError("unexpected recovery contract")
