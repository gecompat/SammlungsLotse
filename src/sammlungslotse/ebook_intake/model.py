"""Application contract for the bounded E-book intake prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias


Scalar: TypeAlias = str | int | bool
FORMAT_CAPABILITIES = frozenset({"supported", "unsupported", "unknown"})
NEXT_ACTIONS = frozenset(
    {"continue_deep_read_only", "defer", "stop", "review", "abstain"}
)
REPORT_SCHEMA = "sammlungslotse/ebook-intake-report/v1"


@dataclass(frozen=True, slots=True)
class Evidence:
    """One path-free observation or derived finding."""

    code: str
    values: tuple[tuple[str, Scalar], ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "values": dict(self.values)}


def evidence(code: str, **values: Scalar) -> Evidence:
    return Evidence(code=code, values=tuple(sorted(values.items())))


@dataclass(frozen=True, slots=True)
class TriageLimits:
    """Versioned, non-configurable CLI defaults for WI-0004."""

    max_input_bytes: int = 32 * 1024 * 1024
    max_archive_entries: int = 512
    max_expanded_bytes: int = 128 * 1024 * 1024
    max_markup_entry_bytes: int = 2 * 1024 * 1024
    max_markup_total_bytes: int = 16 * 1024 * 1024
    max_report_bytes: int = 128 * 1024

    def __post_init__(self) -> None:
        if any(value <= 0 for value in self.to_dict().values()):
            raise ValueError("triage limits must be positive")
        if self.max_markup_entry_bytes > self.max_markup_total_bytes:
            raise ValueError("markup entry limit exceeds total markup limit")

    def to_dict(self) -> dict[str, int]:
        return {
            "max_archive_entries": self.max_archive_entries,
            "max_expanded_bytes": self.max_expanded_bytes,
            "max_input_bytes": self.max_input_bytes,
            "max_markup_entry_bytes": self.max_markup_entry_bytes,
            "max_markup_total_bytes": self.max_markup_total_bytes,
            "max_report_bytes": self.max_report_bytes,
        }


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Immutable local input snapshot; bytes never enter the public report."""

    data: bytes = field(repr=False)
    size_bytes: int
    sha256: str
    suffix: str


@dataclass(frozen=True, slots=True)
class TriageReport:
    """Path-free result shared by human and JSON CLI projections."""

    snapshot: Snapshot | None
    observations: tuple[Evidence, ...]
    findings: tuple[Evidence, ...]
    format_capability: str
    next_action: str
    deep_read_only_allowed: bool
    limits: TriageLimits

    def __post_init__(self) -> None:
        if self.format_capability not in FORMAT_CAPABILITIES:
            raise ValueError("invalid format capability")
        if self.next_action not in NEXT_ACTIONS:
            raise ValueError("invalid next action")
        if self.deep_read_only_allowed != (
            self.next_action == "continue_deep_read_only"
        ):
            raise ValueError("deep read-only gate differs from next action")

    def to_dict(self) -> dict[str, object]:
        snapshot = None
        if self.snapshot is not None:
            snapshot = {
                "sha256": self.snapshot.sha256,
                "size_bytes": self.snapshot.size_bytes,
            }
        return {
            "deep_read_only_allowed": self.deep_read_only_allowed,
            "effects": {
                "deep_tool_started": False,
                "domain_system_writes": False,
                "filesystem_writes": False,
                "network_access": False,
                "original_modified": False,
            },
            "findings": [item.to_dict() for item in self.findings],
            "format_capability": self.format_capability,
            "limits": self.limits.to_dict(),
            "next_action": self.next_action,
            "observations": [item.to_dict() for item in self.observations],
            "schema": REPORT_SCHEMA,
            "snapshot": snapshot,
        }
