"""Path-free application contract for one explicit Calibre library."""

from __future__ import annotations

from dataclasses import dataclass


REPORT_SCHEMA = "sammlungslotse/calibre-read-only-projection/v1"
STATES = frozenset(
    {"completed", "unavailable", "failed", "timeout", "invalid_report", "source_changed", "cleanup_failed"}
)


@dataclass(frozen=True, slots=True)
class CalibreBook:
    external_record_id: int
    title: str
    authors: tuple[str, ...]
    languages: tuple[str, ...]
    formats: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "authors": list(self.authors),
            "external_record_id": self.external_record_id,
            "formats": list(self.formats),
            "languages": list(self.languages),
            "title": self.title,
        }


@dataclass(frozen=True, slots=True)
class CalibreEffects:
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
class CalibreInventoryReport:
    books: tuple[CalibreBook, ...]
    effects: CalibreEffects
    execution_state: str
    library_snapshot_sha256: str | None
    profile_id: str
    provider_version: str
    raw_output_sha256: str | None
    raw_output_size_bytes: int | None
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.execution_state not in STATES:
            raise ValueError("invalid inventory execution state")
        if self.execution_state == "completed" and self.reason_codes:
            raise ValueError("completed projection cannot carry failure reasons")
        if self.execution_state != "completed" and self.books:
            raise ValueError("incomplete projection cannot carry books")
        ids = [item.external_record_id for item in self.books]
        if ids != sorted(ids) or len(ids) != len(set(ids)):
            raise ValueError("book IDs must be unique and ascending")

    @property
    def assessed(self) -> bool:
        return self.execution_state == "completed"

    @classmethod
    def not_assessed(
        cls,
        *,
        state: str,
        reason: str,
        profile_id: str = "",
        provider_version: str = "9.13.0",
        snapshot_sha256: str | None = None,
        process_started: bool = False,
        task_materialized: bool = False,
        cleanup_complete: bool = True,
        original_modified: bool = False,
    ) -> "CalibreInventoryReport":
        return cls(
            books=(),
            effects=CalibreEffects(
                cleanup_complete=cleanup_complete,
                network_access=False,
                original_modified=original_modified,
                process_started=process_started,
                task_materialized=task_materialized,
            ),
            execution_state=state,
            library_snapshot_sha256=snapshot_sha256,
            profile_id=profile_id,
            provider_version=provider_version,
            raw_output_sha256=None,
            raw_output_size_bytes=None,
            reason_codes=(reason,),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "books": [item.to_dict() for item in self.books],
            "effects": self.effects.to_dict(),
            "execution_state": self.execution_state,
            "library_snapshot_sha256": self.library_snapshot_sha256,
            "profile_id": self.profile_id,
            "provider": {"id": "calibre", "version": self.provider_version},
            "raw_output": (
                None
                if self.raw_output_sha256 is None
                else {
                    "sha256": self.raw_output_sha256,
                    "size_bytes": self.raw_output_size_bytes,
                }
            ),
            "reason_codes": list(self.reason_codes),
            "schema": REPORT_SCHEMA,
        }
