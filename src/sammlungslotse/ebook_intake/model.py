"""Application contract for the bounded E-book intake prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias


Scalar: TypeAlias = str | int | bool
FORMAT_CAPABILITIES = frozenset({"supported", "unsupported", "unknown"})
NEXT_ACTIONS = frozenset(
    {"continue_deep_read_only", "defer", "stop", "review", "abstain"}
)
REPORT_SCHEMA_V1 = "sammlungslotse/ebook-intake-report/v1"
REPORT_SCHEMA_V2 = "sammlungslotse/ebook-intake-report/v2"
REPORT_SCHEMA = REPORT_SCHEMA_V1
REVIEW_CONTEXT_CLASSES = frozenset(
    {
        "ambiguous_or_deceptive",
        "content.active_or_submission",
        "content.user_activated_hyperlink",
        "package.optional_linked_resource",
        "publication.automatic_remote_resource",
        "reference.local_or_other_scheme",
    }
)
REVIEW_CONTEXT_ASSESSMENTS = frozenset(
    {"classified", "ambiguous_or_unknown", "not_applicable"}
)


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
class ReviewContext:
    """Coarse path-free explanation used only by the explicit V2 projection."""

    assessment: str
    classes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.assessment not in REVIEW_CONTEXT_ASSESSMENTS:
            raise ValueError("invalid review context assessment")
        if self.classes != tuple(sorted(set(self.classes))):
            raise ValueError("review context classes must be sorted and unique")
        if not set(self.classes) <= REVIEW_CONTEXT_CLASSES:
            raise ValueError("unknown review context class")
        if self.assessment == "not_applicable" and self.classes:
            raise ValueError("not-applicable review context has classes")
        if self.assessment == "classified" and (
            not self.classes or "ambiguous_or_deceptive" in self.classes
        ):
            raise ValueError("classified review context is incomplete")
        if self.assessment == "ambiguous_or_unknown" and (
            "ambiguous_or_deceptive" not in self.classes
        ):
            raise ValueError("ambiguous review context lacks its fallback class")

    @classmethod
    def not_applicable(cls) -> "ReviewContext":
        return cls("not_applicable", ())

    @classmethod
    def for_review(
        cls, classes: set[str], *, ambiguous: bool = False
    ) -> "ReviewContext":
        normalized = set(classes)
        if not normalized or not normalized <= REVIEW_CONTEXT_CLASSES:
            ambiguous = True
        normalized &= REVIEW_CONTEXT_CLASSES
        if ambiguous or "ambiguous_or_deceptive" in normalized:
            normalized.add("ambiguous_or_deceptive")
            assessment = "ambiguous_or_unknown"
        else:
            assessment = "classified"
        return cls(assessment, tuple(sorted(normalized)))

    def to_dict(self) -> dict[str, object]:
        return {"assessment": self.assessment, "classes": list(self.classes)}


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
    review_context: ReviewContext = field(default_factory=ReviewContext.not_applicable)

    def __post_init__(self) -> None:
        if self.format_capability not in FORMAT_CAPABILITIES:
            raise ValueError("invalid format capability")
        if self.next_action not in NEXT_ACTIONS:
            raise ValueError("invalid next action")
        if self.deep_read_only_allowed != (
            self.next_action == "continue_deep_read_only"
        ):
            raise ValueError("deep read-only gate differs from next action")
        if self.next_action == "review":
            if self.review_context.assessment == "not_applicable":
                raise ValueError("review action lacks a context explanation")
        elif self.review_context != ReviewContext.not_applicable():
            raise ValueError("non-review action carries a context explanation")

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
            "schema": REPORT_SCHEMA_V1,
            "snapshot": snapshot,
        }

    def to_dict_v2(self) -> dict[str, object]:
        value = self.to_dict()
        value["review_context"] = self.review_context.to_dict()
        value["schema"] = REPORT_SCHEMA_V2
        return value
