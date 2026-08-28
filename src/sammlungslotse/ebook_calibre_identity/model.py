"""Path-free WI-0011 application and provider contracts."""

from __future__ import annotations

from dataclasses import dataclass

from sammlungslotse.ebook_identity.model import IdentityReport
from sammlungslotse.ebook_intake.model import Snapshot


REPORT_SCHEMA = "sammlungslotse/ebook-calibre-identity-candidate-report/v1"
ASSESSMENTS = frozenset({"completed", "not_assessed"})
HANDOFF_STATES = frozenset(
    {
        "completed",
        "unavailable",
        "failed",
        "timeout",
        "invalid_report",
        "selection_unavailable",
        "source_changed",
        "cleanup_failed",
    }
)


@dataclass(frozen=True, slots=True)
class RecordHandoffEffects:
    cleanup_complete: bool
    network_access: bool
    process_started: bool
    source_modified: bool
    task_materialized: bool

    def to_dict(self) -> dict[str, bool]:
        return {
            "cleanup_complete": self.cleanup_complete,
            "network_access": self.network_access,
            "process_started": self.process_started,
            "source_modified": self.source_modified,
            "task_materialized": self.task_materialized,
        }


@dataclass(frozen=True, slots=True)
class RecordSnapshotHandoff:
    effects: RecordHandoffEffects
    external_record_id: int
    library_snapshot_sha256: str | None
    profile_id: str
    provider_version: str
    reason_codes: tuple[str, ...]
    snapshot: Snapshot | None
    state: str

    def __post_init__(self) -> None:
        if self.state not in HANDOFF_STATES:
            raise ValueError("invalid record handoff state")
        if self.external_record_id <= 0:
            raise ValueError("invalid external record ID")
        if self.state == "completed":
            if self.snapshot is None or self.reason_codes:
                raise ValueError("completed handoff is incomplete")
            if self.snapshot.suffix != ".epub":
                raise ValueError("completed handoff is not EPUB")
        elif self.snapshot is not None or not self.reason_codes:
            raise ValueError("incomplete handoff carries snapshot or no reason")


@dataclass(frozen=True, slots=True)
class ComparisonEffects:
    cleanup_complete: bool
    container_started: bool
    network_access: bool
    source_modified: bool
    task_materialized: bool

    @classmethod
    def from_handoff(cls, effects: RecordHandoffEffects) -> "ComparisonEffects":
        return cls(
            cleanup_complete=effects.cleanup_complete,
            container_started=effects.process_started,
            network_access=effects.network_access,
            source_modified=effects.source_modified,
            task_materialized=effects.task_materialized,
        )

    def to_dict(self) -> dict[str, bool]:
        return {
            "cleanup_complete": self.cleanup_complete,
            "container_started": self.container_started,
            "domain_system_writes": False,
            "network_access": self.network_access,
            "persistence": False,
            "source_modified": self.source_modified,
            "task_materialized": self.task_materialized,
            "writer": False,
        }


@dataclass(frozen=True, slots=True)
class EbookCalibreIdentityReport:
    assessment: str
    effects: ComparisonEffects
    external_record_id: int
    handoff_reason_codes: tuple[str, ...]
    identity: IdentityReport | None
    library_snapshot_sha256: str | None
    profile_id: str
    provider_version: str

    def __post_init__(self) -> None:
        if self.assessment not in ASSESSMENTS:
            raise ValueError("invalid comparison assessment")
        if self.assessment == "completed":
            if self.identity is None or self.identity.assessment != "completed" or self.handoff_reason_codes:
                raise ValueError("completed comparison is incomplete")
        elif self.identity is not None or not self.handoff_reason_codes:
            raise ValueError("not-assessed comparison differs")

    def to_dict(self) -> dict[str, object]:
        return {
            "assessment": self.assessment,
            "calibre_record": {
                "external_record_id": self.external_record_id,
                "library_snapshot_sha256": self.library_snapshot_sha256,
                "profile_id": self.profile_id,
                "provider": {"id": "calibre", "version": self.provider_version},
            },
            "effects": self.effects.to_dict(),
            "handoff_reason_codes": list(self.handoff_reason_codes),
            "identity": None if self.identity is None else self.identity.to_dict(),
            "schema": REPORT_SCHEMA,
            "source_roles": {
                "1": "ingress_epub",
                "2": "calibre_record_epub",
            },
        }
