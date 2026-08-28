"""Application composition for one ingress EPUB and one provider record EPUB."""

from __future__ import annotations

from sammlungslotse.ebook_identity import IdentityCandidateService
from sammlungslotse.ebook_identity.model import IdentityLimits
from sammlungslotse.ebook_intake.application import TriageService
from sammlungslotse.ebook_intake.model import TriageLimits
from sammlungslotse.ebook_intake.ports import SnapshotReader

from .memory import ImmutableSnapshotReader
from .model import (
    ComparisonEffects,
    EbookCalibreIdentityReport,
    RecordHandoffEffects,
)
from .ports import RecordSnapshotPort
from .profile import CalibreIdentityProfile


NO_HANDOFF_EFFECTS = RecordHandoffEffects(True, False, False, False, False)


class EbookCalibreIdentityService:
    def __init__(self, profile: CalibreIdentityProfile) -> None:
        self.profile = profile

    def compare(
        self,
        ingress: SnapshotReader,
        record: RecordSnapshotPort,
    ) -> EbookCalibreIdentityReport:
        limits = IdentityLimits(
            max_input_bytes=self.profile.limits["max_input_bytes"],
            max_total_input_bytes=self.profile.limits["max_total_input_bytes"],
            max_archive_entries=self.profile.limits["max_archive_entries"],
            max_expanded_bytes=self.profile.limits["max_expanded_bytes"],
            max_report_bytes=self.profile.limits["max_report_bytes"],
        )
        triage_limits = TriageLimits(
            max_input_bytes=limits.max_input_bytes,
            max_archive_entries=limits.max_archive_entries,
            max_expanded_bytes=limits.max_expanded_bytes,
            max_report_bytes=limits.max_report_bytes,
        )
        ingress_report = TriageService().triage(ingress, triage_limits)
        if not ingress_report.deep_read_only_allowed or ingress_report.snapshot is None:
            return EbookCalibreIdentityReport(
                assessment="not_assessed",
                effects=ComparisonEffects.from_handoff(NO_HANDOFF_EFFECTS),
                external_record_id=record.external_record_id,
                handoff_reason_codes=("ingress.preflight_gate_not_open",),
                identity=None,
                library_snapshot_sha256=None,
                profile_id=record.profile_id,
                provider_version=self.profile.runtime.provider["version"],
            )

        handoff = record.capture(limits.max_input_bytes)
        if handoff.state != "completed" or handoff.snapshot is None:
            return EbookCalibreIdentityReport(
                assessment="not_assessed",
                effects=ComparisonEffects.from_handoff(handoff.effects),
                external_record_id=handoff.external_record_id,
                handoff_reason_codes=handoff.reason_codes,
                identity=None,
                library_snapshot_sha256=handoff.library_snapshot_sha256,
                profile_id=handoff.profile_id,
                provider_version=handoff.provider_version,
            )

        identity = IdentityCandidateService().compare(
            ImmutableSnapshotReader(ingress_report.snapshot),
            ImmutableSnapshotReader(handoff.snapshot),
            limits,
        )
        if identity.assessment != "completed":
            return EbookCalibreIdentityReport(
                assessment="not_assessed",
                effects=ComparisonEffects.from_handoff(handoff.effects),
                external_record_id=handoff.external_record_id,
                handoff_reason_codes=("identity.not_assessed",),
                identity=None,
                library_snapshot_sha256=handoff.library_snapshot_sha256,
                profile_id=handoff.profile_id,
                provider_version=handoff.provider_version,
            )
        return EbookCalibreIdentityReport(
            assessment="completed",
            effects=ComparisonEffects.from_handoff(handoff.effects),
            external_record_id=handoff.external_record_id,
            handoff_reason_codes=(),
            identity=identity,
            library_snapshot_sha256=handoff.library_snapshot_sha256,
            profile_id=handoff.profile_id,
            provider_version=handoff.provider_version,
        )
