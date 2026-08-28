"""Application orchestration for two explicit EPUB snapshots."""

from __future__ import annotations

from sammlungslotse.ebook_intake.application import TriageService
from sammlungslotse.ebook_intake.model import TriageLimits
from sammlungslotse.ebook_intake.ports import SnapshotReader

from .analyzer import analyze_pair
from .model import IdentityLimits, IdentityReport


class IdentityCandidateService:
    def compare(
        self,
        first: SnapshotReader,
        second: SnapshotReader,
        limits: IdentityLimits | None = None,
    ) -> IdentityReport:
        applied = limits or IdentityLimits()
        triage_limits = TriageLimits(
            max_input_bytes=applied.max_input_bytes,
            max_archive_entries=applied.max_archive_entries,
            max_expanded_bytes=applied.max_expanded_bytes,
            max_report_bytes=applied.max_report_bytes,
        )
        reports = (
            TriageService().triage(first, triage_limits),
            TriageService().triage(second, triage_limits),
        )
        reasons = []
        snapshots = []
        for index, report in enumerate(reports, start=1):
            if not report.deep_read_only_allowed or report.snapshot is None:
                reasons.append(f"input_{index}.preflight_gate_not_open")
            else:
                snapshots.append(report.snapshot)
        if reasons:
            return IdentityReport.not_assessed(tuple(reasons), applied)
        observations, stages, overall = analyze_pair(snapshots[0], snapshots[1], applied)
        return IdentityReport("completed", overall, observations, stages, (), applied)
