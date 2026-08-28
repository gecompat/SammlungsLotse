"""Exact product profile for the WI-0011 Calibre record handoff."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile


PROFILE_SCHEMA = "sammlungslotse/ebook-calibre-identity-profile/v1"
PROFILE_ID = "wi-0011-calibre-identity-handoff/v1"
EXPECTED_FLAGS = [
    "--single-dir",
    "--dont-update-metadata",
    "--dont-write-opf",
    "--dont-save-cover",
    "--dont-save-extra-files",
    "--formats",
    "EPUB",
    "--template",
    "{id}",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class CalibreIdentityProfile:
    data: dict[str, Any]
    runtime: CalibreRuntimeProfile

    @classmethod
    def load(
        cls,
        path: Path,
        runtime_path: Path,
    ) -> "CalibreIdentityProfile":
        value = json.loads(path.read_text(encoding="utf-8"))
        runtime = CalibreRuntimeProfile.load(runtime_path)
        result = cls(value, runtime)
        result.validate(runtime_path)
        return result

    @property
    def profile_id(self) -> str:
        return self.data["profile_id"]

    @property
    def command(self) -> dict[str, Any]:
        return self.data["command"]

    @property
    def limits(self) -> dict[str, int]:
        return self.data["limits"]

    def validate(self, runtime_path: Path) -> None:
        if self.data.get("schema") != PROFILE_SCHEMA or self.data.get("profile_id") != PROFILE_ID:
            raise ValueError("unexpected WI-0011 profile identity")
        binding = self.data.get("calibre_runtime", {})
        if binding != {
            "image_id": self.runtime.image["id"],
            "locator": "runtime/calibre-readonly/profile.json",
            "profile_id": self.runtime.profile_id,
            "sha256": _sha256(runtime_path),
        }:
            raise ValueError("WI-0011 Calibre runtime binding differs")
        if self.command != {
            "fixed_flags": EXPECTED_FLAGS,
            "program": "calibredb",
            "subcommand": "export",
        }:
            raise ValueError("WI-0011 command allowlist differs")
        limits = self.data.get("limits", {})
        if limits != {
            "external_record_id_max": 999999999,
            "max_archive_entries": 512,
            "max_expanded_bytes": 128 * 1024 * 1024,
            "max_input_bytes": 4 * 1024 * 1024,
            "max_report_bytes": 512 * 1024,
            "max_total_input_bytes": 8 * 1024 * 1024,
        }:
            raise ValueError("WI-0011 limits differ")

    def validate_external_record_id(self, value: str) -> int:
        if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]*", value):
            raise ValueError("selection.invalid_external_record_id")
        parsed = int(value)
        if parsed > self.limits["external_record_id_max"]:
            raise ValueError("selection.external_record_id_limit_exceeded")
        return parsed
