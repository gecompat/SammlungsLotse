"""Strict loader for the checked-in WI-0007 runtime preimage."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROFILE_SCHEMA = "sammlungslotse/calibre-read-only-runtime-profile/v1"
HEX128 = re.compile(r"^[0-9a-f]{128}$")
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class CalibreRuntimeProfile:
    data: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> "CalibreRuntimeProfile":
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
            raise ValueError("unsupported profile schema")
        provider = data.get("provider", {})
        if provider.get("id") != "calibre" or provider.get("version") != "9.13.0":
            raise ValueError("unexpected Calibre provider")
        if provider.get("license_spdx") != "GPL-3.0-only":
            raise ValueError("unexpected Calibre license")
        if provider.get("artifact_bytes") != 192554776:
            raise ValueError("unexpected Calibre artifact size")
        if not HEX128.fullmatch(str(provider.get("artifact_sha512", ""))):
            raise ValueError("invalid Calibre artifact digest")
        if not str(provider.get("artifact_url", "")).startswith("https://download.calibre-ebook.com/"):
            raise ValueError("invalid Calibre artifact URL")
        image = data.get("image", {})
        if not IMAGE_ID.fullmatch(str(image.get("id", ""))):
            raise ValueError("image is not digest-bound")
        if image.get("platform") != "linux/amd64":
            raise ValueError("unsupported image platform")
        expected_entrypoint = [
            "/usr/bin/env",
            "-i",
            "CALIBRE_CONFIG_DIRECTORY=/config",
            "HOME=/tmp/home",
            "LANG=C.UTF-8",
            "PATH=/opt/calibre:/usr/local/bin:/usr/bin:/bin",
            "QT_QPA_PLATFORM=offscreen",
            "python",
            "/opt/adapter/calibre_inventory_wrapper.py",
        ]
        if image.get("entrypoint") != expected_entrypoint:
            raise ValueError("unexpected image entrypoint")
        base = data.get("base_image", {})
        if "@sha256:" not in str(base.get("reference", "")):
            raise ValueError("base image is not digest-bound")
        execution = data.get("execution", {})
        exact = {
            "network": "none",
            "user": "65532:65532",
            "read_only_root": True,
            "cap_drop": ["all"],
            "no_new_privileges": True,
            "pids_limit": 64,
            "cpus": "1.0",
            "memory_bytes": 1073741824,
            "memory_swap_bytes": 1073741824,
            "timeout_seconds": 30,
            "stdout_max_bytes": 4194304,
            "stderr_max_bytes": 131072,
            "raw_report_max_bytes": 4194304,
            "podman_minimum_version": "6.1.0",
            "provider_arguments": [],
        }
        for key, expected in exact.items():
            if execution.get(key) != expected:
                raise ValueError(f"unexpected execution value: {key}")
        expected_env = {
            "CALIBRE_CONFIG_DIRECTORY": "/config",
            "HOME": "/tmp/home",
            "LANG": "C.UTF-8",
            "PATH": "/opt/calibre:/usr/local/bin:/usr/bin:/bin",
            "QT_QPA_PLATFORM": "offscreen",
        }
        if execution.get("environment") != expected_env:
            raise ValueError("unexpected execution environment")
        workspace = data.get("workspace", {})
        for key in (
            "marker_schema",
            "max_children",
            "max_task_age_seconds",
            "max_files",
            "max_total_bytes",
            "max_file_bytes",
            "max_depth",
            "max_relative_path_bytes",
        ):
            if key not in workspace:
                raise ValueError(f"missing workspace value: {key}")
