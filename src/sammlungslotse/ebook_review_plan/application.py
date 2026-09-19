"""Application service that composes existing bounded read-only adapters."""

from __future__ import annotations

import unicodedata
from pathlib import Path

from sammlungslotse.calibre_inventory.model import (
    CalibreBook,
    CalibreInventoryReport,
)
from sammlungslotse.calibre_inventory.ports import CalibreInventoryPort
from sammlungslotse.ebook_identity.analyzer import observe_epub
from sammlungslotse.ebook_identity.model import IdentityLimits
from sammlungslotse.ebook_intake.directory import DirectoryIntakeService

from .model import ReviewCandidate, ReviewPlanItem, ReviewPlanReport


def _values(values: tuple[str, ...]) -> set[str]:
    return {
        " ".join(unicodedata.normalize("NFKC", value).casefold().split())
        for value in values
        if value.strip()
    }


def _strategies(
    titles: tuple[str, ...],
    creators: tuple[str, ...],
    languages: tuple[str, ...],
    book: CalibreBook,
) -> tuple[str, ...]:
    matches = []
    if _values(titles) & _values((book.title,)):
        matches.append("metadata.title_equal")
    if _values(creators) & _values(book.authors):
        matches.append("metadata.author_equal")
    if _values(languages) & _values(book.languages):
        matches.append("metadata.language_equal")
    return tuple(sorted(matches))


class ReviewPlanService:
    """Builds only ephemeral manual-review hints; it never selects a target."""

    def __init__(self, directory: DirectoryIntakeService | None = None) -> None:
        self._directory = directory or DirectoryIntakeService()

    def build(self, inbox: Path, projection: CalibreInventoryPort) -> ReviewPlanReport:
        directory, _labels = self._directory.inspect(inbox)
        if not directory.inventory_complete or directory.status != "completed":
            return ReviewPlanReport(
                "not_assessed", (), None, ("inbox.inventory_incomplete",)
            )
        inventory = projection.project()
        if not inventory.assessed or not inventory.effects.cleanup_complete or inventory.effects.original_modified:
            return ReviewPlanReport(
                "not_assessed", (), None, ("projection.not_safely_assessed",)
            )
        provenance = {
            "profile_id": inventory.profile_id,
            "provider": {"id": "calibre", "version": inventory.provider_version},
            "snapshot_sha256": inventory.library_snapshot_sha256,
        }
        items = tuple(
            self._item(
                item.input_index,
                item.status,
                item.triage,
                inventory,
                provenance["snapshot_sha256"],
            )
            for item in directory.items
        )
        return ReviewPlanReport("completed", items, provenance)

    def _item(self, index: int, status: str, triage, inventory: CalibreInventoryReport, digest: str | None) -> ReviewPlanItem:
        if status != "completed" or triage is None:
            return ReviewPlanItem(index, "not_assessed", reason_codes=("inbox.item_not_assessed",))
        if triage.snapshot is None or triage.snapshot.suffix.casefold() != ".epub":
            return ReviewPlanItem(index, "unsupported", reason_codes=("input.not_epub",))
        if not triage.deep_read_only_allowed:
            return ReviewPlanItem(index, "review_ingress_blocked", reason_codes=("ingress.preflight_gate_not_open",))
        try:
            observed = observe_epub(triage.snapshot, IdentityLimits())
        except (OSError, ValueError):
            return ReviewPlanItem(index, "not_assessed", reason_codes=("metadata.not_safely_observed",))
        candidates = []
        for position, book in enumerate(inventory.books):
            reasons = _strategies(
                observed.metadata.titles,
                observed.metadata.creators,
                observed.metadata.languages,
                book,
            )
            if reasons:
                candidates.append(ReviewCandidate(position, book.external_record_id, reasons, digest or ""))
            if len(candidates) == 5:
                break
        if candidates:
            return ReviewPlanItem(index, "review_candidate_present", tuple(candidates))
        return ReviewPlanItem(index, "review_no_candidate_found")
