"""Bounded, read-only inventory for one explicitly selected local directory."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .application import TriageService
from .batch import BatchItemReport, BatchLimits
from .model import NEXT_ACTIONS, Snapshot, TriageLimits
from .ports import SnapshotIssue, SnapshotReader
from .snapshot import FILE_ATTRIBUTE_REPARSE_POINT, LocalFileSnapshotReader


DIRECTORY_REPORT_SCHEMA_V1 = "sammlungslotse/ebook-intake-directory-report/v1"
DIRECTORY_REPORT_SCHEMA_V2 = "sammlungslotse/ebook-intake-directory-report/v2"
DIRECTORY_REPORT_SCHEMA = DIRECTORY_REPORT_SCHEMA_V1
DIRECTORY_STATUSES = frozenset({"completed", "limit_exceeded", "unavailable", "partial"})


def _is_reparse_point(value: os.stat_result) -> bool:
    return bool(
        int(getattr(value, "st_file_attributes", 0)) & FILE_ATTRIBUTE_REPARSE_POINT
    )


@dataclass(frozen=True, slots=True)
class DirectoryCandidate:
    """A private locator retained only while a single local run is active."""

    path: Path
    relative_label: str
    declared_size_bytes: int
    suffix: str


@dataclass(frozen=True, slots=True)
class DirectoryDiscovery:
    """Private discovery result with no public locator projection."""

    candidates: tuple[DirectoryCandidate, ...]
    candidate_counts: tuple[tuple[str, int], ...]
    declared_candidate_bytes: int
    reason_codes: tuple[str, ...]
    skipped_link_or_reparse_points: int
    status: str


class DirectoryScanner:
    """Recursively discovers regular EPUB/PDF files without following links."""

    def discover(self, directory: Path, *, limits: BatchLimits) -> DirectoryDiscovery:
        candidate_counts = {"epub": 0, "pdf": 0}
        candidates: list[DirectoryCandidate] = []
        declared_candidate_bytes = 0
        skipped_link_or_reparse_points = 0

        try:
            root = directory.lstat()
        except OSError:
            return DirectoryDiscovery(
                (), tuple(candidate_counts.items()), 0, ("input.unavailable",), 0, "unavailable"
            )
        if stat.S_ISLNK(root.st_mode):
            return DirectoryDiscovery(
                (), tuple(candidate_counts.items()), 0, ("input.symlink_not_allowed",), 0, "unavailable"
            )
        if _is_reparse_point(root):
            return DirectoryDiscovery(
                (), tuple(candidate_counts.items()), 0, ("input.reparse_not_allowed",), 0, "unavailable"
            )
        if not stat.S_ISDIR(root.st_mode):
            return DirectoryDiscovery(
                (), tuple(candidate_counts.items()), 0, ("input.not_directory",), 0, "unavailable"
            )

        pending = [directory]
        while pending:
            current = pending.pop()
            try:
                entries = sorted(
                    os.scandir(current), key=lambda entry: (entry.name.casefold(), entry.name)
                )
            except OSError:
                return DirectoryDiscovery(
                    (),
                    tuple(candidate_counts.items()),
                    declared_candidate_bytes,
                    ("input.unavailable",),
                    skipped_link_or_reparse_points,
                    "unavailable",
                )

            child_directories: list[Path] = []
            for entry in entries:
                path = Path(entry.path)
                try:
                    entry_stat = entry.stat(follow_symlinks=False)
                except OSError:
                    return DirectoryDiscovery(
                        (),
                        tuple(candidate_counts.items()),
                        declared_candidate_bytes,
                        ("input.unavailable",),
                        skipped_link_or_reparse_points,
                        "unavailable",
                    )
                if stat.S_ISLNK(entry_stat.st_mode) or _is_reparse_point(entry_stat):
                    skipped_link_or_reparse_points += 1
                    continue
                if stat.S_ISDIR(entry_stat.st_mode):
                    child_directories.append(path)
                    continue
                if not stat.S_ISREG(entry_stat.st_mode):
                    continue

                suffix = path.suffix.casefold()
                if suffix not in {".epub", ".pdf"}:
                    continue
                format_name = suffix.removeprefix(".")
                candidate_counts[format_name] += 1
                declared_candidate_bytes += entry_stat.st_size
                candidates.append(
                    DirectoryCandidate(
                        path=path,
                        relative_label=path.relative_to(directory).as_posix(),
                        declared_size_bytes=entry_stat.st_size,
                        suffix=suffix,
                    )
                )
                if len(candidates) > limits.max_inputs:
                    return DirectoryDiscovery(
                        (),
                        tuple(candidate_counts.items()),
                        declared_candidate_bytes,
                        ("directory.candidate_limit_exceeded",),
                        skipped_link_or_reparse_points,
                        "limit_exceeded",
                    )

            pending.extend(reversed(child_directories))

        candidates.sort(key=lambda candidate: (candidate.relative_label.casefold(), candidate.relative_label))
        return DirectoryDiscovery(
            tuple(candidates),
            tuple(candidate_counts.items()),
            declared_candidate_bytes,
            (),
            skipped_link_or_reparse_points,
            "completed",
        )


@dataclass(frozen=True, slots=True)
class _CapturedSnapshotReader:
    snapshot: Snapshot | None = None
    issue: SnapshotIssue | None = None

    def capture(self, limits: TriageLimits) -> Snapshot:
        del limits
        if self.issue is not None:
            raise self.issue
        if self.snapshot is None:
            raise RuntimeError("captured reader is incomplete")
        return self.snapshot


@dataclass(frozen=True, slots=True)
class DirectoryIntakeReport:
    """Path-free report for one directory inventory and its local triage."""

    candidate_counts: tuple[tuple[str, int], ...]
    declared_candidate_bytes: int
    items: tuple[BatchItemReport, ...]
    inventory_complete: bool
    limits: BatchLimits
    reason_codes: tuple[str, ...]
    skipped_link_or_reparse_points: int
    status: str
    total_snapshot_bytes: int

    def __post_init__(self) -> None:
        if self.status not in DIRECTORY_STATUSES:
            raise ValueError("invalid directory intake status")
        if self.total_snapshot_bytes < 0 or self.declared_candidate_bytes < 0:
            raise ValueError("directory byte values must be non-negative")
        if len(self.items) > self.limits.max_inputs:
            raise ValueError("directory report exceeds candidate limit")
        if tuple(item.input_index for item in self.items) != tuple(range(len(self.items))):
            raise ValueError("directory item positions are incomplete or unordered")

    @property
    def candidate_count(self) -> int:
        return sum(value for _, value in self.candidate_counts)

    @property
    def has_internal_error(self) -> bool:
        return self.status in {"unavailable", "partial", "limit_exceeded"}

    def to_dict(self, report_version: str = "v1") -> dict[str, object]:
        if report_version not in {"v1", "v2"}:
            raise ValueError("unsupported directory report version")
        actions = {action: 0 for action in sorted(NEXT_ACTIONS)}
        item_statuses = {status: 0 for status in ("completed", "internal_error", "not_processed")}
        for item in self.items:
            item_statuses[item.status] += 1
            if item.triage is not None:
                actions[item.triage.next_action] += 1
        return {
            "candidate_counts": dict(self.candidate_counts),
            "candidate_count": self.candidate_count,
            "declared_candidate_bytes": self.declared_candidate_bytes,
            "deep_read_only_requested": False,
            "inventory_complete": self.inventory_complete,
            "items": [
                item.to_dict_v2() if report_version == "v2" else item.to_dict()
                for item in self.items
            ],
            "limits": self.limits.to_dict(),
            "reason_codes": list(self.reason_codes),
            "schema": (
                DIRECTORY_REPORT_SCHEMA_V2
                if report_version == "v2"
                else DIRECTORY_REPORT_SCHEMA_V1
            ),
            "skipped_link_or_reparse_points": self.skipped_link_or_reparse_points,
            "status": self.status,
            "summary": {
                "item_statuses": item_statuses,
                "next_actions": actions,
                "total_snapshot_bytes": self.total_snapshot_bytes,
            },
        }


class DirectoryIntakeService:
    """Inventories one directory before any bounded, sequential triage begins."""

    def __init__(
        self,
        *,
        scanner: DirectoryScanner | None = None,
        triage: TriageService | None = None,
    ) -> None:
        self._scanner = scanner or DirectoryScanner()
        self._triage = triage or TriageService()

    def inspect(
        self, directory: Path, *, limits: BatchLimits | None = None
    ) -> tuple[DirectoryIntakeReport, tuple[str, ...]]:
        applied_limits = limits or BatchLimits()
        discovery = self._scanner.discover(directory, limits=applied_limits)
        empty_report = lambda status: DirectoryIntakeReport(
            candidate_counts=discovery.candidate_counts,
            declared_candidate_bytes=discovery.declared_candidate_bytes,
            items=(),
            inventory_complete=discovery.status != "limit_exceeded",
            limits=applied_limits,
            reason_codes=discovery.reason_codes,
            skipped_link_or_reparse_points=discovery.skipped_link_or_reparse_points,
            status=status,
            total_snapshot_bytes=0,
        )
        if discovery.status != "completed":
            return empty_report(discovery.status), ()
        if discovery.declared_candidate_bytes > applied_limits.max_total_input_bytes:
            return (
                DirectoryIntakeReport(
                    candidate_counts=discovery.candidate_counts,
                    declared_candidate_bytes=discovery.declared_candidate_bytes,
                    items=(),
                    inventory_complete=True,
                    limits=applied_limits,
                    reason_codes=("directory.aggregate_input_limit_exceeded",),
                    skipped_link_or_reparse_points=discovery.skipped_link_or_reparse_points,
                    status="limit_exceeded",
                    total_snapshot_bytes=0,
                ),
                (),
            )

        captured_readers: list[SnapshotReader] = []
        total_snapshot_bytes = 0
        for candidate in discovery.candidates:
            try:
                snapshot = LocalFileSnapshotReader(candidate.path).capture(TriageLimits())
            except SnapshotIssue as issue:
                captured_readers.append(_CapturedSnapshotReader(issue=issue))
                continue
            total_snapshot_bytes += snapshot.size_bytes
            if total_snapshot_bytes > applied_limits.max_total_input_bytes:
                return (
                    DirectoryIntakeReport(
                        candidate_counts=discovery.candidate_counts,
                        declared_candidate_bytes=discovery.declared_candidate_bytes,
                        items=(),
                        inventory_complete=True,
                        limits=applied_limits,
                        reason_codes=("directory.aggregate_input_limit_exceeded",),
                        skipped_link_or_reparse_points=discovery.skipped_link_or_reparse_points,
                        status="limit_exceeded",
                        total_snapshot_bytes=0,
                    ),
                    (),
                )
            captured_readers.append(_CapturedSnapshotReader(snapshot=snapshot))

        items: list[BatchItemReport] = []
        for input_index, reader in enumerate(captured_readers):
            try:
                report = self._triage.triage(reader)
            except KeyboardInterrupt:
                raise
            except Exception:
                items.append(
                    BatchItemReport(
                        input_index=input_index,
                        status="internal_error",
                        reason_codes=("processing.internal_error",),
                    )
                )
            else:
                items.append(
                    BatchItemReport(
                        input_index=input_index, status="completed", triage=report
                    )
                )

        status = "partial" if any(item.status != "completed" for item in items) else "completed"
        return (
            DirectoryIntakeReport(
                candidate_counts=discovery.candidate_counts,
                declared_candidate_bytes=discovery.declared_candidate_bytes,
                items=tuple(items),
                inventory_complete=True,
                limits=applied_limits,
                reason_codes=(),
                skipped_link_or_reparse_points=discovery.skipped_link_or_reparse_points,
                status=status,
                total_snapshot_bytes=total_snapshot_bytes,
            ),
            tuple(candidate.relative_label for candidate in discovery.candidates),
        )
