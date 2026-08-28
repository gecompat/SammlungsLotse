"""Run and validate the synthetic EXP-0010 standards-bound evidence matrix."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import uuid
import zipfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.ebook_identity.application import IdentityCandidateService  # noqa: E402
from sammlungslotse.ebook_identity.model import IdentityLimits  # noqa: E402
from sammlungslotse.ebook_intake.deep_profile import DeepRuntimeProfile  # noqa: E402
from sammlungslotse.ebook_intake.epubcheck_provider import EpubCheckProvider  # noqa: E402
from sammlungslotse.ebook_intake.model import Snapshot  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0010"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
MANIFEST_PATH = EXPERIMENT / "case-manifest.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNNER_PATH = Path(__file__).resolve()
DEEP_PROFILE_PATH = ROOT / "runtime" / "ebook-deep-readonly" / "profile.json"
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")
STAGES = ("byte", "package", "representation", "edition", "work")
DECISIONS = frozenset(
    {"candidate_same", "candidate_related", "different", "abstain", "not_applicable"}
)
PUBLICATION_DECISIONS = frozenset({"same", "different", "abstain", "not_assessed"})
FAULTS = frozenset({"none", "missing_primary_binding", "missing_modified"})
SPEC_KEYS = frozenset(
    {
        "additional_identifiers",
        "body",
        "collections",
        "creator",
        "fault",
        "language",
        "modified",
        "primary_identifier",
        "title",
    }
)
EXPECTED_CASE_KEYS = frozenset(
    {
        "different-collections-same-work",
        "invalid-missing-modified",
        "invalid-missing-primary-binding",
        "multiple-collections-partial-overlap",
        "same-primary-minor-revision",
        "same-primary-strong-content-conflict",
        "series-overlap-distinct-works",
        "set-overlap-distinct-members",
        "shared-typed-additional-different-primary",
        "shared-untyped-additional-different-primary",
    }
)
PREIMAGE_FILES = (
    "experiments/ebook/exp-0010/README.md",
    "experiments/ebook/exp-0010/case-manifest.json",
    "experiments/ebook/exp-0010/execution-profile.json",
    "tests/experiments/test_exp_0010.py",
    "tools/experiments/run_exp_0010.py",
    "runtime/ebook-deep-readonly/profile.json",
    "src/sammlungslotse/__init__.py",
    "src/sammlungslotse/ebook_identity/__init__.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/cli.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/__init__.py",
    "src/sammlungslotse/ebook_intake/application.py",
    "src/sammlungslotse/ebook_intake/deep_model.py",
    "src/sammlungslotse/ebook_intake/deep_ports.py",
    "src/sammlungslotse/ebook_intake/deep_profile.py",
    "src/sammlungslotse/ebook_intake/deep_workspace.py",
    "src/sammlungslotse/ebook_intake/epubcheck_provider.py",
    "src/sammlungslotse/ebook_intake/model.py",
    "src/sammlungslotse/ebook_intake/podman_executor.py",
    "src/sammlungslotse/ebook_intake/ports.py",
    "src/sammlungslotse/ebook_intake/preflight.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tools/run_ebook_identity.py",
)
ACCEPTANCE_NAMES = frozenset(
    {
        "case_matrix_complete",
        "conformance_expectations_met",
        "conformance_profile_bound",
        "inputs_unchanged_and_cleanup_complete",
        "metrics_and_findings_recomputable",
        "oracle_layers_bound_and_evaluated",
        "path_free_and_preimage_bound",
        "result_contract_self_bound",
        "role_projections_reconstructable",
        "semantic_capability_gaps_visible",
        "semantic_product_repetitions_identical",
        "zero_network_domain_or_original_effects",
    }
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]|/(?:home|Users|tmp|private)(?:[\\/]|$))",
    re.IGNORECASE,
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_identifier(value: Any, field: str, *, typed: bool) -> None:
    expected = {"id", "identifier_type", "scheme", "value"} if typed else {"id", "value"}
    if not isinstance(value, dict) or set(value) != expected:
        raise RuntimeError(f"EXP-0010 {field} fields differ")
    if not all(isinstance(value[key], str) and value[key] for key in ("id", "value")):
        raise RuntimeError(f"EXP-0010 {field} identity differs")
    if typed:
        for key in ("identifier_type", "scheme"):
            if value[key] is not None and (not isinstance(value[key], str) or not value[key]):
                raise RuntimeError(f"EXP-0010 {field} refinement differs")
        if value["identifier_type"] is None and value["scheme"] is not None:
            raise RuntimeError(f"EXP-0010 {field} scheme lacks a type")


def _validate_collection(value: Any, field: str) -> None:
    if not isinstance(value, dict) or set(value) != {
        "id",
        "identifier",
        "name",
        "position",
        "type",
    }:
        raise RuntimeError(f"EXP-0010 {field} fields differ")
    if not all(isinstance(value[key], str) and value[key] for key in ("id", "identifier", "name")):
        raise RuntimeError(f"EXP-0010 {field} identity differs")
    if value["type"] not in {"series", "set"}:
        raise RuntimeError(f"EXP-0010 {field} type differs")
    if value["position"] is not None and (
        not isinstance(value["position"], str)
        or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value["position"])
    ):
        raise RuntimeError(f"EXP-0010 {field} position differs")


def merged_spec(manifest: dict[str, Any], case: dict[str, Any], side: str) -> dict[str, Any]:
    value = dict(manifest["defaults"])
    value.update(case.get("base", {}))
    value.update(case.get(side, {}))
    if set(value) != SPEC_KEYS:
        raise RuntimeError(f"EXP-0010 {case.get('case_key')} {side} fields differ")
    for field in ("body", "creator", "language", "modified", "title"):
        if not isinstance(value[field], str) or not value[field]:
            raise RuntimeError(f"EXP-0010 {field} must be text")
    if value["fault"] not in FAULTS:
        raise RuntimeError("EXP-0010 generator fault differs")
    _validate_identifier(value["primary_identifier"], "primary_identifier", typed=False)
    if not isinstance(value["additional_identifiers"], list):
        raise RuntimeError("EXP-0010 additional identifiers differ")
    for index, item in enumerate(value["additional_identifiers"]):
        _validate_identifier(item, f"additional_identifiers[{index}]", typed=True)
    if not isinstance(value["collections"], list):
        raise RuntimeError("EXP-0010 collections differ")
    for index, item in enumerate(value["collections"]):
        _validate_collection(item, f"collections[{index}]")
    identifiers = [value["primary_identifier"]["id"]] + [
        item["id"] for item in value["additional_identifiers"]
    ]
    collection_ids = [item["id"] for item in value["collections"]]
    if len(identifiers) != len(set(identifiers)) or len(collection_ids) != len(set(collection_ids)):
        raise RuntimeError("EXP-0010 metadata IDs differ")
    return value


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != "sammlungslotse/exp-0010-case-manifest/v1":
        raise RuntimeError("unexpected EXP-0010 case manifest schema")
    if manifest.get("artifact") != "EXP-0010" or set(manifest.get("defaults", {})) != SPEC_KEYS:
        raise RuntimeError("unexpected EXP-0010 case manifest identity")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != 10:
        raise RuntimeError("EXP-0010 requires exactly ten cases")
    case_keys = [case.get("case_key") for case in cases]
    if len(set(case_keys)) != 10 or set(case_keys) != EXPECTED_CASE_KEYS:
        raise RuntimeError("EXP-0010 case keys differ")
    if sum(case.get("oracle_scope") == "quality" for case in cases) != 8:
        raise RuntimeError("EXP-0010 quality case count differs")
    if sum(case.get("oracle_scope") == "control" for case in cases) != 2:
        raise RuntimeError("EXP-0010 control case count differs")
    required = {
        "base",
        "case_key",
        "conformance_expected",
        "expected_product_assessment",
        "left",
        "oracle",
        "oracle_rationale",
        "oracle_scope",
        "publication_oracle",
        "right",
    }
    for case in cases:
        if set(case) != required or not all(
            isinstance(case[item], dict) for item in ("base", "left", "right")
        ):
            raise RuntimeError(f"EXP-0010 {case.get('case_key')} contract fields differ")
        for value in (case["base"], case["left"], case["right"]):
            if not set(value).issubset(SPEC_KEYS):
                raise RuntimeError("EXP-0010 generator override differs")
        left = merged_spec(manifest, case, "left")
        right = merged_spec(manifest, case, "right")
        expected_conformance = case["conformance_expected"]
        if set(expected_conformance) != {"left", "right"} or not set(
            expected_conformance.values()
        ) <= {"pass", "error"}:
            raise RuntimeError("EXP-0010 conformance oracle differs")
        if case["oracle_scope"] == "quality" and (
            left["fault"] != "none"
            or right["fault"] != "none"
            or set(expected_conformance.values()) != {"pass"}
        ):
            raise RuntimeError("EXP-0010 quality case is not standard-bound")
        if case["oracle_scope"] == "control" and "error" not in expected_conformance.values():
            raise RuntimeError("EXP-0010 control lacks an error expectation")
        if case["expected_product_assessment"] != "completed":
            raise RuntimeError("EXP-0010 expected product assessment differs")
        if not isinstance(case["oracle_rationale"], str) or not case["oracle_rationale"]:
            raise RuntimeError("EXP-0010 oracle rationale missing")
        publication = case["publication_oracle"]
        if not isinstance(publication, list) or not publication or not set(publication) <= PUBLICATION_DECISIONS:
            raise RuntimeError("EXP-0010 publication oracle differs")
        oracle = case["oracle"]
        if not isinstance(oracle, dict) or tuple(sorted(oracle)) != tuple(sorted(STAGES)):
            raise RuntimeError("EXP-0010 stage oracle differs")
        for stage in STAGES:
            allowed = oracle[stage]
            if not isinstance(allowed, list) or not allowed or not set(allowed) <= DECISIONS:
                raise RuntimeError("EXP-0010 allowed decision differs")
            if len(allowed) != len(set(allowed)):
                raise RuntimeError("EXP-0010 duplicate allowed decision")
        if case["oracle_scope"] == "control" and any(
            oracle[stage] != ["not_applicable"] for stage in STAGES
        ):
            raise RuntimeError("EXP-0010 control oracle differs")
    if PRIVATE_PATH_PATTERN.search(canonical_json(manifest)):
        raise RuntimeError("EXP-0010 manifest contains a private absolute path")
    return manifest


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("schema") != "sammlungslotse/exp-0010-execution-profile/v1":
        raise RuntimeError("unexpected EXP-0010 profile schema")
    if profile.get("artifact") != "EXP-0010" or profile.get("profile_id") != "exp-0010-standards-bound-metadata-oracle/v1":
        raise RuntimeError("unexpected EXP-0010 profile identity")
    if profile.get("case_manifest") != "experiments/ebook/exp-0010/case-manifest.json":
        raise RuntimeError("EXP-0010 manifest locator differs")
    if profile.get("case_totals") != {"control": 2, "quality": 8, "total": 10}:
        raise RuntimeError("EXP-0010 case totals differ")
    if tuple(profile.get("stages", ())) != STAGES or set(profile.get("decisions", ())) != DECISIONS:
        raise RuntimeError("EXP-0010 identity levels differ")
    if profile.get("product_repetitions") != 2:
        raise RuntimeError("EXP-0010 repetition count differs")
    if profile.get("limits") != IdentityLimits().to_dict():
        raise RuntimeError("EXP-0010 limits differ from product contract")
    conformance = profile.get("conformance", {})
    deep = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
    if conformance != {
        "image_id": deep.image["id"],
        "profile_id": deep.profile_id,
        "profile_locator": "runtime/ebook-deep-readonly/profile.json",
        "provider_id": deep.provider["id"],
        "provider_version": deep.provider["version"],
        "runs_per_distinct_input": 1,
    }:
        raise RuntimeError("EXP-0010 conformance profile differs")
    implementation = profile.get("implementation", {})
    if implementation != {
        "external_dependencies": ["existing WI-0005 EPUBCheck 5.3.0 profile"],
        "network": "podman network=none",
        "product_code_changes": False,
        "runtime": "Python 3.12 standard library plus existing bounded EPUBCheck profile",
        "synthetic_only": True,
    }:
        raise RuntimeError("EXP-0010 implementation boundary differs")
    measurement = profile.get("measurement", {})
    if set(measurement.get("publication_oracle_decisions", ())) != PUBLICATION_DECISIONS:
        raise RuntimeError("EXP-0010 publication decisions differ")
    if measurement.get("critical_same_stages") != ["edition", "work"]:
        raise RuntimeError("EXP-0010 critical stage list differs")
    if set(measurement.get("labels", {})) != set(STAGES):
        raise RuntimeError("EXP-0010 metric labels differ")
    return profile


def load_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    return validate_profile(load_json(PROFILE_PATH)), validate_manifest(load_json(MANIFEST_PATH))


def _xml_attr(value: str) -> str:
    return html.escape(value, quote=True)


def _opf(spec: dict[str, Any]) -> bytes:
    primary = spec["primary_identifier"]
    unique_ref = "missing-id" if spec["fault"] == "missing_primary_binding" else primary["id"]
    metadata = [
        f'<dc:identifier id="{_xml_attr(primary["id"])}">{html.escape(primary["value"])}</dc:identifier>',
        f"<dc:title>{html.escape(spec['title'])}</dc:title>",
        f"<dc:language>{html.escape(spec['language'])}</dc:language>",
        f"<dc:creator>{html.escape(spec['creator'])}</dc:creator>",
    ]
    if spec["fault"] != "missing_modified":
        metadata.append(f'<meta property="dcterms:modified">{html.escape(spec["modified"])}</meta>')
    for item in spec["additional_identifiers"]:
        metadata.append(
            f'<dc:identifier id="{_xml_attr(item["id"])}">{html.escape(item["value"])}</dc:identifier>'
        )
        if item["identifier_type"] is not None:
            scheme = (
                f' scheme="{_xml_attr(item["scheme"])}"' if item["scheme"] is not None else ""
            )
            metadata.append(
                f'<meta refines="#{_xml_attr(item["id"])}" property="identifier-type"{scheme}>'
                f'{html.escape(item["identifier_type"])}</meta>'
            )
    for item in spec["collections"]:
        metadata.append(
            f'<meta property="belongs-to-collection" id="{_xml_attr(item["id"])}">'
            f'{html.escape(item["name"])}</meta>'
        )
        metadata.append(
            f'<meta refines="#{_xml_attr(item["id"])}" property="collection-type">'
            f'{html.escape(item["type"])}</meta>'
        )
        metadata.append(
            f'<meta refines="#{_xml_attr(item["id"])}" property="dcterms:identifier">'
            f'{html.escape(item["identifier"])}</meta>'
        )
        if item["position"] is not None:
            metadata.append(
                f'<meta refines="#{_xml_attr(item["id"])}" property="group-position">'
                f'{html.escape(item["position"])}</meta>'
            )
    value = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" '
        f'unique-identifier="{_xml_attr(unique_ref)}" version="3.0" xml:lang="{_xml_attr(spec["language"])}">'
        f'<metadata>{"".join(metadata)}</metadata>'
        '<manifest>'
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        '<item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>'
        '</manifest><spine><itemref idref="chapter"/></spine></package>'
    )
    return value.encode("utf-8")


def _zip_info(name: str, compression: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = compression
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def generate_epub(spec: dict[str, Any]) -> bytes:
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
        '<rootfiles><rootfile full-path="OPS/package.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles></container>'
    ).encode("utf-8")
    chapter = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{_xml_attr(spec["language"])}" '
        f'lang="{_xml_attr(spec["language"])}"><head><title>{html.escape(spec["title"])}</title></head>'
        f'<body><h1>{html.escape(spec["title"])}</h1><p>{html.escape(spec["body"])}</p></body></html>'
    ).encode("utf-8")
    nav = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
        f'xml:lang="{_xml_attr(spec["language"])}" lang="{_xml_attr(spec["language"])}">'
        '<head><title>Contents</title></head><body><nav epub:type="toc" id="toc">'
        '<h1>Contents</h1><ol><li><a href="chapter.xhtml">Chapter</a></li></ol>'
        '</nav></body></html>'
    ).encode("utf-8")
    entries = [
        ("mimetype", b"application/epub+zip", zipfile.ZIP_STORED),
        ("META-INF/container.xml", container, zipfile.ZIP_DEFLATED),
        ("OPS/package.opf", _opf(spec), zipfile.ZIP_DEFLATED),
        ("OPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED),
        ("OPS/chapter.xhtml", chapter, zipfile.ZIP_DEFLATED),
    ]
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, mode="w") as archive:
        for name, value, compression in entries:
            archive.writestr(_zip_info(name, compression), value)
    return payload.getvalue()


def _package_from_epub(payload: bytes) -> ElementTree.Element:
    with zipfile.ZipFile(io.BytesIO(payload), mode="r") as archive:
        container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise RuntimeError("EXP-0010 package locator missing")
        return ElementTree.fromstring(archive.read(rootfile.get("full-path", "")))


def standard_metadata_projection(payload: bytes) -> dict[str, Any]:
    package = _package_from_epub(payload)
    opf = "http://www.idpf.org/2007/opf"
    dc = "http://purl.org/dc/elements/1.1/"
    unique_ref = package.get("unique-identifier", "")
    identifiers = package.findall(f".//{{{opf}}}metadata/{{{dc}}}identifier")
    metas = package.findall(f".//{{{opf}}}metadata/{{{opf}}}meta")

    def text(element: ElementTree.Element) -> str:
        return " ".join("".join(element.itertext()).split())

    def refinement(item_id: str, property_name: str) -> ElementTree.Element | None:
        return next(
            (
                item
                for item in metas
                if item.get("refines") == f"#{item_id}" and item.get("property") == property_name
            ),
            None,
        )

    primary_element = next((item for item in identifiers if item.get("id") == unique_ref), None)
    primary = (
        {"id": primary_element.get("id"), "value": text(primary_element)}
        if primary_element is not None
        else None
    )
    additional = []
    for item in identifiers:
        if item is primary_element:
            continue
        item_id = item.get("id", "")
        typed = refinement(item_id, "identifier-type") if item_id else None
        additional.append(
            {
                "id": item_id or None,
                "identifier_type": text(typed) if typed is not None else None,
                "scheme": typed.get("scheme") if typed is not None else None,
                "value": text(item),
            }
        )
    modified_element = next(
        (item for item in metas if item.get("property") == "dcterms:modified" and not item.get("refines")),
        None,
    )
    collections = []
    for item in metas:
        if item.get("property") != "belongs-to-collection":
            continue
        item_id = item.get("id", "")
        collection_type = refinement(item_id, "collection-type") if item_id else None
        collection_id = refinement(item_id, "dcterms:identifier") if item_id else None
        position = refinement(item_id, "group-position") if item_id else None
        collections.append(
            {
                "id": item_id or None,
                "identifier": text(collection_id) if collection_id is not None else None,
                "name": text(item),
                "position": text(position) if position is not None else None,
                "type": text(collection_type) if collection_type is not None else None,
            }
        )
    return {
        "additional_identifiers": additional,
        "collections": collections,
        "modified": text(modified_element) if modified_element is not None else None,
        "primary_identifier": primary,
        "unique_identifier_ref": unique_ref or None,
    }


def expected_standard_projection(spec: dict[str, Any]) -> dict[str, Any]:
    if spec["fault"] == "missing_primary_binding":
        primary = None
        additional = [
            {
                "id": spec["primary_identifier"]["id"],
                "identifier_type": None,
                "scheme": None,
                "value": spec["primary_identifier"]["value"],
            },
            *spec["additional_identifiers"],
        ]
        unique_ref = "missing-id"
    else:
        primary = spec["primary_identifier"]
        additional = spec["additional_identifiers"]
        unique_ref = spec["primary_identifier"]["id"]
    return {
        "additional_identifiers": additional,
        "collections": spec["collections"],
        "modified": None if spec["fault"] == "missing_modified" else spec["modified"],
        "primary_identifier": primary,
        "unique_identifier_ref": unique_ref,
    }


def materialize_pair(
    manifest: dict[str, Any], case: dict[str, Any], case_root: Path
) -> tuple[Path, Path]:
    case_root.mkdir(mode=0o700)
    paths = (case_root / "input-1.epub", case_root / "input-2.epub")
    for side, path in zip(("left", "right"), paths, strict=True):
        path.write_bytes(generate_epub(merged_spec(manifest, case, side)))
    return paths


def stage_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["stage"]: item for item in report.get("stages", [])}


def evaluate_product_case(
    manifest: dict[str, Any], case: dict[str, Any], case_root: Path, limits: IdentityLimits
) -> dict[str, Any]:
    paths = materialize_pair(manifest, case, case_root)
    before = [sha256_file(path) for path in paths]
    projections = [standard_metadata_projection(path.read_bytes()) for path in paths]
    expected_projections = [
        expected_standard_projection(merged_spec(manifest, case, side))
        for side in ("left", "right")
    ]
    started = time.perf_counter_ns()
    report = IdentityCandidateService().compare(
        LocalFileSnapshotReader(paths[0]), LocalFileSnapshotReader(paths[1]), limits
    ).to_dict()
    duration_ms = round((time.perf_counter_ns() - started) / 1_000_000, 3)
    after = [sha256_file(path) for path in paths]
    stages = stage_map(report)
    evaluations = []
    for stage in STAGES:
        decision = stages[stage]["decision"] if report["assessment"] == "completed" else "not_applicable"
        allowed = case["oracle"][stage]
        evaluations.append(
            {
                "allowed": allowed,
                "decision": decision,
                "matches_oracle": decision in allowed,
                "quality_scope": case["oracle_scope"] == "quality",
                "stage": stage,
            }
        )
    return {
        "assessment": report["assessment"],
        "case_key": case["case_key"],
        "duration_ms": duration_ms,
        "expected_assessment": case["expected_product_assessment"],
        "input_sha256_after": after,
        "input_sha256_before": before,
        "inputs_unchanged": before == after,
        "oracle_evaluation": evaluations,
        "oracle_rationale": case["oracle_rationale"],
        "oracle_scope": case["oracle_scope"],
        "publication_oracle": case["publication_oracle"],
        "publication_product_stage_present": False,
        "report": report,
        "standard_metadata_projection": projections,
        "standard_projection_matches_manifest": projections == expected_projections,
    }


def conformance_summary(result: Any, expected: str) -> dict[str, Any]:
    findings = [
        {"code": item.code, "severity": item.severity}
        for item in result.findings
    ]
    if result.execution_state != "completed":
        classification = "not_assessed"
    elif not findings:
        classification = "pass"
    elif any(item["severity"].casefold() in {"error", "fatal"} for item in findings):
        classification = "error"
    else:
        classification = "finding"
    return {
        "actual": classification,
        "assessment": result.assessment,
        "effects": result.effects.to_dict(),
        "expected": expected,
        "findings": findings,
        "matches_expected": classification == expected,
        "profile_id": result.profile_id,
        "provider": {"id": result.provider_id, "version": result.provider_version},
        "reason_codes": list(result.reason_codes),
        "snapshot_sha256": result.snapshot_sha256,
    }


def evaluate_conformance(
    manifest: dict[str, Any], case: dict[str, Any], case_root: Path, provider: EpubCheckProvider
) -> dict[str, Any]:
    paths = materialize_pair(manifest, case, case_root)
    before = [sha256_file(path) for path in paths]
    sides: dict[str, Any] = {}
    for side, path in zip(("left", "right"), paths, strict=True):
        payload = path.read_bytes()
        snapshot = Snapshot(data=payload, size_bytes=len(payload), sha256=sha256_bytes(payload), suffix=".epub")
        result = provider.inspect(snapshot)
        sides[side] = conformance_summary(result, case["conformance_expected"][side])
    after = [sha256_file(path) for path in paths]
    return {
        "case_key": case["case_key"],
        "input_sha256_after": after,
        "input_sha256_before": before,
        "inputs_unchanged": before == after,
        "oracle_scope": case["oracle_scope"],
        "sides": sides,
    }


def semantic_case(case: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in case.items() if key != "duration_ms"}


def semantic_repetition(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {"cases": [semantic_case(case) for case in cases]}


def _fraction(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "denominator": denominator,
        "numerator": numerator,
        "value": "not_applicable" if denominator == 0 else round(numerator / denominator, 6),
    }


def calculate_metrics(cases: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    quality = [
        case
        for case in cases
        if case["oracle_scope"] == "quality" and case["assessment"] == "completed"
    ]
    result: dict[str, Any] = {}
    for stage in STAGES:
        rows = [
            next(item for item in case["oracle_evaluation"] if item["stage"] == stage)
            for case in quality
        ]
        confusion: dict[str, dict[str, int]] = {}
        for row in rows:
            oracle_key = "|".join(row["allowed"])
            confusion.setdefault(oracle_key, {})
            confusion[oracle_key][row["decision"]] = confusion[oracle_key].get(row["decision"], 0) + 1
        label_metrics: dict[str, Any] = {}
        for label in profile["measurement"]["labels"][stage]:
            true_positive = sum(row["decision"] == label and label in row["allowed"] for row in rows)
            false_positive = sum(row["decision"] == label and label not in row["allowed"] for row in rows)
            false_negative = sum(row["decision"] != label and label in row["allowed"] for row in rows)
            label_metrics[label] = {
                "false_negative": false_negative,
                "false_positive": false_positive,
                "precision": _fraction(true_positive, true_positive + false_positive),
                "recall": _fraction(true_positive, true_positive + false_negative),
                "true_positive": true_positive,
            }
        selected = [row for row in rows if row["decision"] != "abstain"]
        abstentions = [row for row in rows if row["decision"] == "abstain"]
        result[stage] = {
            "abstention_rate": _fraction(len(abstentions), len(rows)),
            "confusion": confusion,
            "correct_abstention": sum(row["matches_oracle"] for row in abstentions),
            "coverage": _fraction(len(selected), len(rows)),
            "labels": label_metrics,
            "oracle_match_count": sum(row["matches_oracle"] for row in rows),
            "row_count": len(rows),
            "selective_accuracy": _fraction(
                sum(row["matches_oracle"] for row in selected), len(selected)
            ),
            "unexpected_abstention": sum(not row["matches_oracle"] for row in abstentions),
        }
    return result


def calculate_findings(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for case in cases:
        if case["oracle_scope"] != "quality":
            continue
        if case["assessment"] != case["expected_assessment"]:
            findings.append(
                {
                    "actual": case["assessment"],
                    "case_key": case["case_key"],
                    "expected": case["expected_assessment"],
                    "kind": "assessment_mismatch",
                }
            )
        for row in case["oracle_evaluation"]:
            if row["matches_oracle"]:
                continue
            if row["decision"] == "candidate_same" and row["stage"] in {"edition", "work"}:
                kind = "critical_false_same"
            elif row["decision"] == "candidate_related":
                kind = "false_related"
            elif "candidate_same" in row["allowed"] or "candidate_related" in row["allowed"]:
                kind = "false_negative_or_abstention"
            else:
                kind = "unexpected_decision"
            findings.append(
                {
                    "allowed": row["allowed"],
                    "case_key": case["case_key"],
                    "decision": row["decision"],
                    "kind": kind,
                    "stage": row["stage"],
                }
            )
    return findings


def semantic_capability_gaps(cases: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    if cases and all(case["publication_product_stage_present"] is False for case in cases):
        gaps.append("identity.publication_stage_absent")
    identifier_role_loss = False
    collection_role_loss = False
    for case in cases:
        if case["assessment"] != "completed":
            continue
        for projection, observed in zip(
            case["standard_metadata_projection"], case["report"]["inputs"], strict=True
        ):
            metadata = observed["metadata"]
            if projection["additional_identifiers"] and set(metadata) == {
                "creators",
                "identifiers",
                "languages",
                "titles",
                "work_references",
            }:
                identifier_role_loss = True
            if projection["collections"] and metadata["work_references"] == [
                item["name"] for item in projection["collections"]
            ]:
                collection_role_loss = True
    if identifier_role_loss:
        gaps.append("metadata.identifier_roles_flattened")
    if collection_role_loss:
        gaps.append("metadata.collections_flattened_as_work_references")
    return gaps


def quality_verdict(findings: list[dict[str, Any]]) -> str:
    if any(item["kind"] == "critical_false_same" for item in findings):
        return "not_qualified"
    return "qualified_with_findings" if findings else "qualified"


def result_payload_digest(result: dict[str, Any]) -> str:
    return canonical_digest(
        {key: value for key, value in result.items() if key != "result_content_sha256"}
    )


def result_path_free(result: dict[str, Any]) -> bool:
    redacted = dict(result)
    redacted.pop("result_content_sha256", None)
    return PRIVATE_PATH_PATTERN.search(canonical_json(redacted)) is None


def current_preimage() -> dict[str, str]:
    result: dict[str, str] = {}
    for locator in PREIMAGE_FILES:
        path = ROOT / locator
        if not path.is_file():
            raise RuntimeError(f"EXP-0010 preimage file missing: {locator}")
        result[locator] = sha256_file(path)
    return result


def git_output(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git command failed: {' '.join(arguments[:2])}")
    return completed.stdout.strip()


def authority_evidence() -> dict[str, Any]:
    if git_output("status", "--porcelain"):
        raise RuntimeError("EXP-0010 empirical run requires a clean preimage commit")
    head = git_output("rev-parse", "HEAD")
    origin_main = git_output("rev-parse", "origin/main")
    merge_base = git_output("merge-base", "HEAD", "origin/main")
    if merge_base != origin_main:
        raise RuntimeError("EXP-0010 preimage does not descend from exact origin/main")
    registry = json.loads(git_output("show", "origin/main:.ai/artifact_registry.json"))["artifacts"]
    if registry["GATE-0009"]["status"] != "done" or registry["EXP-0010"]["status"] != "accepted":
        raise RuntimeError("EXP-0010 accepted plan is not canonical on origin/main")
    changed = set(filter(None, git_output("diff", "--name-only", "origin/main...HEAD").splitlines()))
    allowed = {
        "experiments/ebook/exp-0010/README.md",
        "experiments/ebook/exp-0010/case-manifest.json",
        "experiments/ebook/exp-0010/execution-profile.json",
        "tests/experiments/test_exp_0010.py",
        "tools/experiments/run_exp_0010.py",
    }
    if changed != allowed:
        raise RuntimeError("EXP-0010 preimage change set differs from the frozen experiment")
    product_changes = git_output(
        "diff",
        "--name-only",
        "origin/main...HEAD",
        "--",
        "src",
        "tools/run_ebook_identity.py",
        "tools/qualify_ebook_identity.py",
        "tests/product",
        "runtime/ebook-identity",
        "tests/fixtures",
    )
    if product_changes:
        raise RuntimeError("EXP-0010 preimage changes product code or fixtures")
    return {
        "allowed_change_set": True,
        "exp_0010_accepted_on_origin_main": True,
        "gate_0009_done_on_origin_main": True,
        "merge_base": merge_base,
        "origin_main": origin_main,
        "preimage_commit": head,
        "product_code_and_test_0001_unchanged": True,
    }


def _is_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        info = path.stat(follow_symlinks=False)
    except OSError:
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(info, "st_file_attributes", 0) & flag)


def prepare_temp_base(path: Path) -> Path:
    authority = Path(os.path.abspath(ALLOWED_TEMP_ROOT))
    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(authority)
    except ValueError as exc:
        raise RuntimeError("EXP-0010 temp root escapes C:\\rep\\tmp authority") from exc
    if not relative.parts or any(value in str(candidate) for value in ("\x00", "\r", "\n")):
        raise RuntimeError("EXP-0010 temp root is not a strict task subpath")
    authority.mkdir(parents=True, exist_ok=True)
    current = authority
    for part in relative.parts:
        current /= part
        if current.exists() and _is_reparse(current):
            raise RuntimeError("EXP-0010 temp root contains a link or reparse point")
    candidate.mkdir(parents=True, exist_ok=True)
    if _is_reparse(candidate) or candidate.resolve(strict=True) != candidate:
        raise RuntimeError("EXP-0010 temp root is unsafe")
    return candidate


def cleanup_run_root(run_root: Path, temp_base: Path) -> bool:
    if run_root.parent != temp_base or not run_root.name.startswith("run-") or _is_reparse(run_root):
        raise RuntimeError("EXP-0010 cleanup target is outside the owned run root")
    shutil.rmtree(run_root)
    return not run_root.exists()


def _conformance_expectations_met(evidence: list[dict[str, Any]]) -> bool:
    return len(evidence) == 10 and all(
        item["inputs_unchanged"]
        and all(side["matches_expected"] for side in item["sides"].values())
        for item in evidence
    )


def _zero_conformance_effects(evidence: list[dict[str, Any]]) -> bool:
    return bool(evidence) and all(
        side["effects"]["cleanup_complete"] is True
        and side["effects"]["network_access"] is False
        and side["effects"]["original_modified"] is False
        for item in evidence
        for side in item["sides"].values()
    )


def acceptance_from_result(result: dict[str, Any], profile: dict[str, Any]) -> dict[str, bool]:
    repetitions = result.get("product_repetitions", [])
    first_cases = repetitions[0].get("cases", []) if len(repetitions) == 2 else []
    second_cases = repetitions[1].get("cases", []) if len(repetitions) == 2 else []
    conformance = result.get("conformance_evidence", [])
    findings = calculate_findings(first_cases) if first_cases else []
    gaps = semantic_capability_gaps(first_cases) if first_cases else []
    deep = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
    role_projection = bool(first_cases) and all(
        case.get("standard_projection_matches_manifest") is True for case in first_cases
    )
    oracles = bool(first_cases) and all(
        case.get("publication_oracle")
        and case.get("oracle_rationale")
        and len(case.get("oracle_evaluation", [])) == 5
        for case in first_cases
    )
    critical = [item for item in findings if item["kind"] == "critical_false_same"]
    return {
        "case_matrix_complete": len(first_cases) == len(second_cases) == 10
        and {case.get("case_key") for case in first_cases} == EXPECTED_CASE_KEYS
        and sum(case.get("oracle_scope") == "quality" for case in first_cases) == 8
        and sum(case.get("oracle_scope") == "control" for case in first_cases) == 2,
        "conformance_expectations_met": _conformance_expectations_met(conformance),
        "conformance_profile_bound": result.get("conformance_profile")
        == {
            "id": deep.profile_id,
            "image_id": deep.image["id"],
            "provider_id": deep.provider["id"],
            "provider_version": deep.provider["version"],
            "sha256": sha256_file(DEEP_PROFILE_PATH),
        },
        "inputs_unchanged_and_cleanup_complete": bool(first_cases)
        and all(
            case.get("inputs_unchanged") is True
            for repetition in repetitions
            for case in repetition.get("cases", [])
        )
        and all(item.get("inputs_unchanged") is True for item in conformance)
        and result.get("cleanup_complete") is True,
        "metrics_and_findings_recomputable": bool(first_cases)
        and result.get("metrics") == calculate_metrics(first_cases, profile)
        and result.get("quality_findings") == findings
        and result.get("critical_false_same_count") == len(critical),
        "oracle_layers_bound_and_evaluated": oracles,
        "path_free_and_preimage_bound": result_path_free(result)
        and result.get("preimage", {}).get("sha256_by_locator") == current_preimage(),
        "result_contract_self_bound": result.get("result_content_sha256")
        == result_payload_digest(result),
        "role_projections_reconstructable": role_projection,
        "semantic_capability_gaps_visible": gaps
        == [
            "identity.publication_stage_absent",
            "metadata.identifier_roles_flattened",
            "metadata.collections_flattened_as_work_references",
        ]
        and result.get("semantic_capability_gaps") == gaps,
        "semantic_product_repetitions_identical": len(repetitions) == 2
        and repetitions[0].get("semantic_sha256") == repetitions[1].get("semantic_sha256")
        and semantic_repetition(first_cases) == semantic_repetition(second_cases),
        "zero_network_domain_or_original_effects": _zero_conformance_effects(conformance)
        and bool(first_cases)
        and all(
            case["report"].get("effects")
            == {
                "domain_system_writes": False,
                "filesystem_writes": False,
                "network_access": False,
                "original_modified": False,
            }
            for repetition in repetitions
            for case in repetition.get("cases", [])
        ),
    }


def execute(temp_root: Path) -> dict[str, Any]:
    profile, manifest = load_contract()
    authority = authority_evidence()
    preimage = current_preimage()
    temp_base = prepare_temp_base(temp_root)
    run_root = temp_base / f"run-{uuid.uuid4().hex}"
    run_root.mkdir(mode=0o700)
    repetitions: list[dict[str, Any]] = []
    conformance: list[dict[str, Any]] = []
    cleanup_complete = False
    try:
        limits = IdentityLimits(**profile["limits"])
        deep_profile = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
        provider = EpubCheckProvider(profile=deep_profile, temp_root=run_root / "epubcheck-tasks")
        conformance_root = run_root / "conformance"
        conformance_root.mkdir(mode=0o700)
        for case in manifest["cases"]:
            conformance.append(
                evaluate_conformance(
                    manifest,
                    case,
                    conformance_root / case["case_key"],
                    provider,
                )
            )
        for repetition_index in range(1, profile["product_repetitions"] + 1):
            repetition_root = run_root / f"product-repetition-{repetition_index}"
            repetition_root.mkdir(mode=0o700)
            cases = [
                evaluate_product_case(
                    manifest,
                    case,
                    repetition_root / case["case_key"],
                    limits,
                )
                for case in manifest["cases"]
            ]
            repetitions.append(
                {
                    "cases": cases,
                    "duration_ms": round(sum(case["duration_ms"] for case in cases), 3),
                    "repetition": repetition_index,
                    "semantic_sha256": canonical_digest(semantic_repetition(cases)),
                }
            )
    finally:
        cleanup_complete = cleanup_run_root(run_root, temp_base)

    first_cases = repetitions[0]["cases"]
    findings = calculate_findings(first_cases)
    deep_profile = DeepRuntimeProfile.load(DEEP_PROFILE_PATH)
    result: dict[str, Any] = {
        "acceptance": {name: True for name in sorted(ACCEPTANCE_NAMES)},
        "artifact": "EXP-0010",
        "cleanup_complete": cleanup_complete,
        "conformance_evidence": conformance,
        "conformance_profile": {
            "id": deep_profile.profile_id,
            "image_id": deep_profile.image["id"],
            "provider_id": deep_profile.provider["id"],
            "provider_version": deep_profile.provider["version"],
            "sha256": sha256_file(DEEP_PROFILE_PATH),
        },
        "critical_false_same_count": sum(
            item["kind"] == "critical_false_same" for item in findings
        ),
        "executed_on": date.today().isoformat(),
        "manifest": {"locator": profile["case_manifest"], "sha256": sha256_file(MANIFEST_PATH)},
        "metrics": calculate_metrics(first_cases, profile),
        "preimage": {"authority": authority, "sha256_by_locator": preimage},
        "product_repetitions": repetitions,
        "profile": {"id": profile["profile_id"], "sha256": sha256_file(PROFILE_PATH)},
        "quality_findings": findings,
        "quality_verdict": quality_verdict(findings),
        "schema": "sammlungslotse/exp-0010-result/v1",
        "semantic_capability_gaps": semantic_capability_gaps(first_cases),
        "status": "pending",
    }
    result["result_content_sha256"] = result_payload_digest(result)
    result["acceptance"] = acceptance_from_result(result, profile)
    result["status"] = "pass" if all(result["acceptance"].values()) else "fail"
    result["result_content_sha256"] = result_payload_digest(result)
    result["acceptance"] = acceptance_from_result(result, profile)
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    profile, _manifest = load_contract()
    result = load_json(path)
    problems: list[str] = []
    if result.get("schema") != "sammlungslotse/exp-0010-result/v1" or result.get("artifact") != "EXP-0010":
        problems.append("EXP-0010 result identity differs")
    if result.get("profile") != {"id": profile["profile_id"], "sha256": sha256_file(PROFILE_PATH)}:
        problems.append("EXP-0010 profile binding differs")
    if result.get("manifest") != {"locator": profile["case_manifest"], "sha256": sha256_file(MANIFEST_PATH)}:
        problems.append("EXP-0010 manifest binding differs")
    acceptance = acceptance_from_result(result, profile)
    if set(result.get("acceptance", {})) != ACCEPTANCE_NAMES or result.get("acceptance") != acceptance:
        problems.append("EXP-0010 acceptance differs")
    if not all(acceptance.values()) or result.get("status") != "pass":
        problems.append("EXP-0010 method is not fully accepted")
    repetitions = result.get("product_repetitions", [])
    first_cases = repetitions[0].get("cases", []) if len(repetitions) == 2 else []
    expected_findings = calculate_findings(first_cases) if first_cases else []
    if result.get("quality_findings") != expected_findings:
        problems.append("EXP-0010 findings differ")
    if result.get("quality_verdict") != quality_verdict(expected_findings):
        problems.append("EXP-0010 quality verdict differs")
    if result.get("semantic_capability_gaps") != semantic_capability_gaps(first_cases):
        problems.append("EXP-0010 capability gaps differ")
    if problems:
        raise RuntimeError("; ".join(problems))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--temp-root", type=Path)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    args = parser.parse_args(argv)
    try:
        if args.validate_profile:
            profile, manifest = load_contract()
            print(
                f"EXP-0010 profile valid: cases={len(manifest['cases'])} "
                f"product_repetitions={profile['product_repetitions']}"
            )
            return 0
        if args.validate_result:
            result = validate_result(args.result)
            print(
                f"EXP-0010 result valid: {sum(result['acceptance'].values())}/"
                f"{len(ACCEPTANCE_NAMES)} quality={result['quality_verdict']}"
            )
            return 0
        if args.temp_root is None:
            parser.error("--temp-root is required for the empirical run")
        result = execute(args.temp_root)
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"EXP-0010 method: {sum(result['acceptance'].values())}/"
            f"{len(ACCEPTANCE_NAMES)} quality={result['quality_verdict']}"
        )
        return 0 if result["status"] == "pass" else 1
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
