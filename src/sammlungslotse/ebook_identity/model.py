"""Path-free application contract for WI-0009."""

from __future__ import annotations

from dataclasses import dataclass


REPORT_SCHEMA_V1 = "sammlungslotse/ebook-identity-candidate-report/v1"
REPORT_SCHEMA_V2 = "sammlungslotse/ebook-identity-candidate-report/v2"
REPORT_SCHEMA = REPORT_SCHEMA_V1
STAGES = ("byte", "package", "representation", "edition", "work")
DECISIONS = frozenset(
    {"candidate_same", "candidate_related", "different", "abstain", "not_applicable"}
)
OVERALL = frozenset(
    {
        "exact_byte_match",
        "representation_candidate",
        "edition_candidate",
        "related_work_candidate",
        "no_candidate",
        "abstain",
        "not_assessed",
    }
)


@dataclass(frozen=True, slots=True)
class IdentityLimits:
    max_input_bytes: int = 32 * 1024 * 1024
    max_total_input_bytes: int = 64 * 1024 * 1024
    max_archive_entries: int = 512
    max_expanded_bytes: int = 128 * 1024 * 1024
    max_report_bytes: int = 256 * 1024

    def to_dict(self) -> dict[str, int]:
        return {
            "max_archive_entries": self.max_archive_entries,
            "max_expanded_bytes": self.max_expanded_bytes,
            "max_input_bytes": self.max_input_bytes,
            "max_report_bytes": self.max_report_bytes,
            "max_total_input_bytes": self.max_total_input_bytes,
        }


@dataclass(frozen=True, slots=True)
class Identifier:
    id: str | None
    value: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "value": self.value}


@dataclass(frozen=True, slots=True)
class AdditionalIdentifier:
    id: str | None
    identifier_type: str | None
    scheme: str | None
    value: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "identifier_type": self.identifier_type,
            "scheme": self.scheme,
            "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class CollectionMembership:
    id: str | None
    identifier: str | None
    name: str
    position: str | None
    type: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "identifier": self.identifier,
            "name": self.name,
            "position": self.position,
            "type": self.type,
        }


def _leaf_provenance(
    value: object, prefix: str, source: str
) -> dict[str, dict[str, str]]:
    if value is None or value == []:
        return {prefix: {"source": source, "status": "missing"}}
    if isinstance(value, dict):
        result: dict[str, dict[str, str]] = {}
        for key in sorted(value):
            result.update(_leaf_provenance(value[key], f"{prefix}.{key}", source))
        return result
    if isinstance(value, list):
        result = {}
        for index, item in enumerate(value):
            result.update(_leaf_provenance(item, f"{prefix}[{index}]", source))
        return result
    return {prefix: {"source": source, "status": "observed"}}


@dataclass(frozen=True, slots=True)
class EmbeddedMetadata:
    titles: tuple[str, ...]
    creators: tuple[str, ...]
    languages: tuple[str, ...]
    identifiers: tuple[str, ...]
    work_references: tuple[str, ...]
    primary_identifier: Identifier | None
    primary_identifier_element_ref: str | None
    additional_identifiers: tuple[AdditionalIdentifier, ...]
    modified: str | None
    collection_memberships: tuple[CollectionMembership, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "creators": list(self.creators),
            "identifiers": list(self.identifiers),
            "languages": list(self.languages),
            "titles": list(self.titles),
            "work_references": list(self.work_references),
        }

    def to_dict_v2(self) -> dict[str, object]:
        role_values: dict[str, object] = {
            "primary_identifier": (
                None
                if self.primary_identifier is None
                else self.primary_identifier.to_dict()
            ),
            "primary_identifier_element_ref": self.primary_identifier_element_ref,
            "additional_identifiers": [
                item.to_dict() for item in self.additional_identifiers
            ],
            "modified": self.modified,
            "collection_memberships": [
                item.to_dict() for item in self.collection_memberships
            ],
        }
        sources = {
            "primary_identifier": "package@unique-identifier and dc:identifier",
            "primary_identifier_element_ref": "package@unique-identifier",
            "additional_identifiers": (
                "dc:identifier and identifier-type refinements"
            ),
            "modified": "meta[property=dcterms:modified]",
            "collection_memberships": "belongs-to-collection refinements",
        }
        provenance: dict[str, dict[str, str]] = {}
        for key, source in sources.items():
            provenance.update(_leaf_provenance(role_values[key], key, source))
        return {
            "additional_identifiers": role_values["additional_identifiers"],
            "collection_memberships": role_values["collection_memberships"],
            "creators": list(self.creators),
            "languages": list(self.languages),
            "modified": role_values["modified"],
            "primary_identifier": role_values["primary_identifier"],
            "primary_identifier_element_ref": role_values[
                "primary_identifier_element_ref"
            ],
            "provenance": provenance,
            "titles": list(self.titles),
        }


@dataclass(frozen=True, slots=True)
class InputObservation:
    input_index: int
    sha256: str
    size_bytes: int
    package_sha256: str
    representation_sha256: str
    content_sha256: str
    entry_count: int
    expanded_bytes: int
    metadata: EmbeddedMetadata

    def to_dict(self) -> dict[str, object]:
        return {
            "content_sha256": self.content_sha256,
            "entry_count": self.entry_count,
            "expanded_bytes": self.expanded_bytes,
            "input_index": self.input_index,
            "metadata": self.metadata.to_dict(),
            "package_sha256": self.package_sha256,
            "representation_sha256": self.representation_sha256,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }

    def to_dict_v2(self) -> dict[str, object]:
        value = self.to_dict()
        value["metadata"] = self.metadata.to_dict_v2()
        return value


@dataclass(frozen=True, slots=True)
class StageResult:
    stage: str
    decision: str
    rule_id: str
    positive_evidence: tuple[str, ...] = ()
    negative_evidence: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.stage not in STAGES or self.decision not in DECISIONS:
            raise ValueError("invalid identity stage result")

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision,
            "missing_evidence": list(self.missing_evidence),
            "negative_evidence": list(self.negative_evidence),
            "positive_evidence": list(self.positive_evidence),
            "rule_id": self.rule_id,
            "stage": self.stage,
        }


@dataclass(frozen=True, slots=True)
class IdentityReport:
    assessment: str
    overall: str
    inputs: tuple[InputObservation, ...]
    stages: tuple[StageResult, ...]
    reason_codes: tuple[str, ...]
    limits: IdentityLimits

    def __post_init__(self) -> None:
        if self.assessment not in {"completed", "not_assessed"}:
            raise ValueError("invalid identity assessment")
        if self.overall not in OVERALL:
            raise ValueError("invalid overall identity result")
        if self.assessment == "completed":
            if len(self.inputs) != 2 or tuple(item.stage for item in self.stages) != STAGES:
                raise ValueError("completed identity report is incomplete")
            if self.reason_codes:
                raise ValueError("completed identity report has reasons")
        elif self.inputs or self.stages or not self.reason_codes or self.overall != "not_assessed":
            raise ValueError("not-assessed identity report differs")

    @classmethod
    def not_assessed(cls, reasons: tuple[str, ...], limits: IdentityLimits) -> "IdentityReport":
        return cls("not_assessed", "not_assessed", (), (), tuple(sorted(set(reasons))), limits)

    def to_dict(self) -> dict[str, object]:
        return {
            "assessment": self.assessment,
            "effects": {
                "domain_system_writes": False,
                "filesystem_writes": False,
                "network_access": False,
                "original_modified": False,
            },
            "inputs": [item.to_dict() for item in self.inputs],
            "limits": self.limits.to_dict(),
            "overall": self.overall,
            "reason_codes": list(self.reason_codes),
            "schema": REPORT_SCHEMA_V1,
            "stages": [item.to_dict() for item in self.stages],
        }

    def to_dict_v2(self) -> dict[str, object]:
        value = self.to_dict()
        value["inputs"] = [item.to_dict_v2() for item in self.inputs]
        value["schema"] = REPORT_SCHEMA_V2
        return value
