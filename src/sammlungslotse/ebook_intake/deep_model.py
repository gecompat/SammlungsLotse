"""Provider-neutral result contract for one bounded deep read-only check."""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass

from .model import TriageReport


DEEP_REPORT_SCHEMA = "sammlungslotse/deep-read-only-report/v1"
COMBINED_REPORT_SCHEMA = "sammlungslotse/ebook-intake-with-deep-report/v1"
EXECUTION_STATES = frozenset(
    {
        "completed",
        "unavailable",
        "failed",
        "timeout",
        "invalid_report",
        "hash_mismatch",
        "cleanup_failed",
    }
)
ASSESSMENTS = frozenset(
    {
        "no_epubcheck_conformance_errors_reported",
        "epubcheck_conformance_findings",
        "not_assessed",
    }
)


@dataclass(frozen=True, slots=True)
class DeepLocation:
    """One publication-relative provider location."""

    path: str
    line: int | None = None
    column: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {"column": self.column, "line": self.line, "path": self.path}


@dataclass(frozen=True, slots=True)
class DeepFinding:
    """Lossless provider code with a small path-safe projection."""

    code: str
    severity: str
    message: str
    locations: tuple[DeepLocation, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "locations": [item.to_dict() for item in self.locations],
            "message": self.message,
            "severity": self.severity,
        }


@dataclass(frozen=True, slots=True)
class DeepEffects:
    """Bounded effects observed for the deep adapter call."""

    cleanup_complete: bool
    network_access: bool
    original_modified: bool
    process_started: bool
    task_materialized: bool

    def to_dict(self) -> dict[str, bool]:
        return {
            "cleanup_complete": self.cleanup_complete,
            "network_access": self.network_access,
            "original_modified": self.original_modified,
            "process_started": self.process_started,
            "task_materialized": self.task_materialized,
        }


@dataclass(frozen=True, slots=True)
class DeepToolResult:
    """Path-free result envelope shared by every future deep provider."""

    assessment: str
    effects: DeepEffects
    execution_state: str
    findings: tuple[DeepFinding, ...]
    observations: tuple[str, ...]
    profile_id: str
    provider_id: str
    provider_version: str
    reason_codes: tuple[str, ...]
    snapshot_sha256: str | None
    raw_report: bytes | None = None

    def __post_init__(self) -> None:
        if self.execution_state not in EXECUTION_STATES:
            raise ValueError("invalid deep execution state")
        if self.assessment not in ASSESSMENTS:
            raise ValueError("invalid deep assessment")
        if self.execution_state == "completed" and self.assessment == "not_assessed":
            raise ValueError("completed tool run may not be unassessed")
        if self.execution_state != "completed" and self.assessment != "not_assessed":
            raise ValueError("incomplete tool run may not carry an assessment")

    @classmethod
    def not_assessed(
        cls,
        *,
        execution_state: str,
        reason_code: str,
        snapshot_sha256: str | None,
        provider_id: str = "epubcheck",
        provider_version: str = "5.3.0",
        profile_id: str = "",
        observations: tuple[str, ...] = (),
        process_started: bool = False,
        task_materialized: bool = False,
        cleanup_complete: bool = True,
        raw_report: bytes | None = None,
    ) -> "DeepToolResult":
        return cls(
            assessment="not_assessed",
            effects=DeepEffects(
                cleanup_complete=cleanup_complete,
                network_access=False,
                original_modified=False,
                process_started=process_started,
                task_materialized=task_materialized,
            ),
            execution_state=execution_state,
            findings=(),
            observations=observations,
            profile_id=profile_id,
            provider_id=provider_id,
            provider_version=provider_version,
            reason_codes=(reason_code,),
            snapshot_sha256=snapshot_sha256,
            raw_report=raw_report,
        )

    def to_dict(self) -> dict[str, object]:
        raw: dict[str, object] | None = None
        if self.raw_report is not None:
            raw = {
                "data": base64.b64encode(self.raw_report).decode("ascii"),
                "encoding": "base64",
                "media_type": "application/json",
                "sha256": hashlib.sha256(self.raw_report).hexdigest(),
                "size_bytes": len(self.raw_report),
            }
        return {
            "assessment": self.assessment,
            "effects": self.effects.to_dict(),
            "execution_state": self.execution_state,
            "findings": [item.to_dict() for item in self.findings],
            "observations": list(self.observations),
            "profile_id": self.profile_id,
            "provider": {
                "id": self.provider_id,
                "version": self.provider_version,
            },
            "raw_report": raw,
            "reason_codes": list(self.reason_codes),
            "schema": DEEP_REPORT_SCHEMA,
            "snapshot_sha256": self.snapshot_sha256,
        }


@dataclass(frozen=True, slots=True)
class CombinedIntakeReport:
    """Opt-in aggregate; the unchanged WI-0004 report remains the default."""

    triage: TriageReport
    deep_read_only: DeepToolResult

    def to_dict(self) -> dict[str, object]:
        return {
            "deep_read_only": self.deep_read_only.to_dict(),
            "schema": COMBINED_REPORT_SCHEMA,
            "triage": self.triage.to_dict(),
        }
