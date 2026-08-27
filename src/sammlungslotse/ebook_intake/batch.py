"""Bounded, path-free orchestration for explicit multi-file intake."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .application import TriageService
from .deep_model import CombinedIntakeReport, DeepToolResult
from .model import NEXT_ACTIONS, TriageReport
from .ports import SnapshotReader


BATCH_REPORT_SCHEMA = "sammlungslotse/ebook-intake-batch-report/v1"
BATCH_ITEM_STATUSES = frozenset({"completed", "internal_error", "not_processed"})
BATCH_STATUSES = frozenset({"completed", "partial", "limit_exceeded"})


@dataclass(frozen=True, slots=True)
class BatchLimits:
    """Fixed WI-0006 limits for one explicit batch."""

    max_inputs: int = 32
    max_total_input_bytes: int = 256 * 1024 * 1024
    max_report_bytes: int = 48 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.max_inputs < 2:
            raise ValueError("batch input limit must allow at least two inputs")
        if self.max_total_input_bytes <= 0 or self.max_report_bytes <= 0:
            raise ValueError("batch byte limits must be positive")

    def to_dict(self) -> dict[str, int]:
        return {
            "max_inputs": self.max_inputs,
            "max_report_bytes": self.max_report_bytes,
            "max_total_input_bytes": self.max_total_input_bytes,
        }


@dataclass(frozen=True, slots=True)
class BatchItemReport:
    """One locator-free result identified only by its input position."""

    input_index: int
    status: str
    triage: TriageReport | None = None
    deep_read_only: DeepToolResult | None = None
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.input_index < 0:
            raise ValueError("input index must not be negative")
        if self.status not in BATCH_ITEM_STATUSES:
            raise ValueError("invalid batch item status")
        if self.status == "completed" and self.triage is None:
            raise ValueError("completed batch item needs a triage report")
        if self.status != "completed" and self.deep_read_only is not None:
            raise ValueError("incomplete batch item may not have a deep report")
        if self.deep_read_only is not None and self.triage is None:
            raise ValueError("deep report needs a triage report")

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] | None = None
        if self.triage is not None:
            if self.deep_read_only is None:
                result = self.triage.to_dict()
            else:
                result = CombinedIntakeReport(
                    self.triage, self.deep_read_only
                ).to_dict()
        return {
            "input_index": self.input_index,
            "reason_codes": list(self.reason_codes),
            "result": result,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class BatchReport:
    """Stable aggregate of independently processed explicit inputs."""

    batch_status: str
    deep_read_only_requested: bool
    input_count: int
    items: tuple[BatchItemReport, ...]
    limits: BatchLimits
    total_snapshot_bytes: int

    def __post_init__(self) -> None:
        if self.batch_status not in BATCH_STATUSES:
            raise ValueError("invalid batch status")
        if self.input_count < 2 or self.input_count > self.limits.max_inputs:
            raise ValueError("batch input count outside its contract")
        if len(self.items) != self.input_count:
            raise ValueError("batch item count differs from input count")
        if tuple(item.input_index for item in self.items) != tuple(
            range(self.input_count)
        ):
            raise ValueError("batch item positions are incomplete or unordered")
        if self.total_snapshot_bytes < 0:
            raise ValueError("total snapshot size must not be negative")

    @property
    def has_internal_error(self) -> bool:
        return any(item.status != "completed" for item in self.items)

    @property
    def has_unassessed_deep_result(self) -> bool:
        return any(
            item.deep_read_only is not None
            and item.deep_read_only.assessment == "not_assessed"
            for item in self.items
        )

    def to_dict(self) -> dict[str, object]:
        actions = {action: 0 for action in sorted(NEXT_ACTIONS)}
        assessments = {
            "epubcheck_conformance_findings": 0,
            "no_epubcheck_conformance_errors_reported": 0,
            "not_assessed": 0,
        }
        item_statuses = {status: 0 for status in sorted(BATCH_ITEM_STATUSES)}
        for item in self.items:
            item_statuses[item.status] += 1
            if item.triage is not None:
                actions[item.triage.next_action] += 1
            if item.deep_read_only is not None:
                assessments[item.deep_read_only.assessment] += 1
        return {
            "batch_status": self.batch_status,
            "deep_read_only_requested": self.deep_read_only_requested,
            "input_count": self.input_count,
            "items": [item.to_dict() for item in self.items],
            "limits": self.limits.to_dict(),
            "schema": BATCH_REPORT_SCHEMA,
            "summary": {
                "deep_assessments": assessments,
                "item_statuses": item_statuses,
                "next_actions": actions,
                "total_snapshot_bytes": self.total_snapshot_bytes,
            },
        }


class BatchIntakeService:
    """Processes explicit readers sequentially without exposing locators."""

    def __init__(self, triage: TriageService | None = None) -> None:
        self._triage = triage or TriageService()

    def inspect(
        self,
        readers: Sequence[SnapshotReader],
        *,
        limits: BatchLimits | None = None,
        deep_inspector: Callable[[TriageReport], DeepToolResult] | None = None,
    ) -> BatchReport:
        applied_limits = limits or BatchLimits()
        input_count = len(readers)
        if input_count < 2 or input_count > applied_limits.max_inputs:
            raise ValueError("batch input count outside its contract")

        items: list[BatchItemReport] = []
        total_snapshot_bytes = 0
        limit_exceeded = False

        for input_index, reader in enumerate(readers):
            if limit_exceeded:
                items.append(
                    BatchItemReport(
                        input_index=input_index,
                        status="not_processed",
                        reason_codes=("batch.aggregate_input_limit_exceeded",),
                    )
                )
                continue
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
                continue

            snapshot_bytes = report.snapshot.size_bytes if report.snapshot else 0
            total_snapshot_bytes += snapshot_bytes
            if total_snapshot_bytes > applied_limits.max_total_input_bytes:
                limit_exceeded = True
                items.append(
                    BatchItemReport(
                        input_index=input_index,
                        status="not_processed",
                        reason_codes=("batch.aggregate_input_limit_exceeded",),
                    )
                )
            else:
                items.append(
                    BatchItemReport(
                        input_index=input_index,
                        status="completed",
                        triage=report,
                    )
                )

        if not limit_exceeded and deep_inspector is not None:
            deep_items: list[BatchItemReport] = []
            for item in items:
                if item.status != "completed" or item.triage is None:
                    deep_items.append(item)
                    continue
                try:
                    deep = deep_inspector(item.triage)
                except KeyboardInterrupt:
                    raise
                except Exception:
                    deep_items.append(
                        BatchItemReport(
                            input_index=item.input_index,
                            status="internal_error",
                            triage=item.triage,
                            reason_codes=("processing.internal_error",),
                        )
                    )
                else:
                    deep_items.append(
                        BatchItemReport(
                            input_index=item.input_index,
                            status="completed",
                            triage=item.triage,
                            deep_read_only=deep,
                        )
                    )
            items = deep_items

        if limit_exceeded:
            batch_status = "limit_exceeded"
        elif any(item.status != "completed" for item in items):
            batch_status = "partial"
        else:
            batch_status = "completed"

        return BatchReport(
            batch_status=batch_status,
            deep_read_only_requested=deep_inspector is not None,
            input_count=input_count,
            items=tuple(items),
            limits=applied_limits,
            total_snapshot_bytes=total_snapshot_bytes,
        )
