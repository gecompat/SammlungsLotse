"""Application service for one bounded E-book intake decision."""

from __future__ import annotations

from .model import TriageLimits, TriageReport, evidence
from .ports import SnapshotIssue, SnapshotReader
from .preflight import EpubPreflight


class TriageService:
    """Orchestrates snapshot capture and path-free preflight analysis."""

    def __init__(self, preflight: EpubPreflight | None = None) -> None:
        self._preflight = preflight or EpubPreflight()

    def triage(
        self,
        reader: SnapshotReader,
        limits: TriageLimits | None = None,
    ) -> TriageReport:
        applied_limits = limits or TriageLimits()
        try:
            snapshot = reader.capture(applied_limits)
        except SnapshotIssue as issue:
            item_values = dict(issue.values)
            return TriageReport(
                snapshot=None,
                observations=(evidence(issue.observation_code, **item_values),),
                findings=(evidence(issue.finding_code, **item_values),),
                format_capability="unknown",
                next_action=issue.next_action,
                deep_read_only_allowed=False,
                limits=applied_limits,
            )
        return self._preflight.inspect(snapshot, applied_limits)
