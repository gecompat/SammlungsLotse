"""Path-free contract for the WI-0019 manual review plan."""

from __future__ import annotations

from dataclasses import dataclass


REPORT_SCHEMA = "sammlungslotse/ebook-calibre-review-plan/v1"
PLAN_STATES = frozenset({"completed", "not_assessed"})
REVIEW_CLASSES = frozenset(
    {"not_assessed", "review_candidate_present", "review_ingress_blocked", "review_no_candidate_found", "unsupported"}
)


@dataclass(frozen=True, slots=True)
class ReviewCandidate:
    library_position: int
    external_record_id: int
    reason_strategies: tuple[str, ...]
    projection_snapshot_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {"external_record_id": self.external_record_id, "library_position": self.library_position, "projection_snapshot_sha256": self.projection_snapshot_sha256, "reason_strategies": list(self.reason_strategies)}


@dataclass(frozen=True, slots=True)
class ReviewPlanItem:
    input_index: int
    review_class: str
    candidates: tuple[ReviewCandidate, ...] = ()
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.input_index < 0 or self.review_class not in REVIEW_CLASSES:
            raise ValueError("invalid review plan item")
        if len(self.candidates) > 5:
            raise ValueError("candidate limit exceeded")
        if self.review_class != "review_candidate_present" and self.candidates:
            raise ValueError("only candidate reviews may contain candidates")

    def to_dict(self) -> dict[str, object]:
        return {"candidates": [item.to_dict() for item in self.candidates], "input_index": self.input_index, "reason_codes": list(self.reason_codes), "review_class": self.review_class}


@dataclass(frozen=True, slots=True)
class ReviewPlanReport:
    state: str
    items: tuple[ReviewPlanItem, ...]
    projection_provenance: dict[str, object] | None
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in PLAN_STATES:
            raise ValueError("invalid review plan state")
        if tuple(item.input_index for item in self.items) != tuple(range(len(self.items))):
            raise ValueError("review plan item positions are incomplete")
        if self.state == "completed" and (self.projection_provenance is None or self.reason_codes):
            raise ValueError("completed plan lacks provenance or carries reasons")
        if self.state == "not_assessed" and (self.items or not self.reason_codes):
            raise ValueError("not-assessed plan differs")

    def to_dict(self) -> dict[str, object]:
        return {"effects": {"filesystem_writes": False, "import": False, "network_access": False, "persistence": False}, "items": [item.to_dict() for item in self.items], "projection_provenance": self.projection_provenance, "reason_codes": list(self.reason_codes), "schema": REPORT_SCHEMA, "state": self.state}
