#!/usr/bin/env python3
"""Run or validate the frozen, product-code-free EXP-0011 comparison."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "src"
for import_root in (ROOT, SOURCE_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from sammlungslotse.ebook_identity.application import IdentityCandidateService
from sammlungslotse.ebook_identity.model import IdentityLimits
from sammlungslotse.ebook_intake.model import Snapshot, TriageLimits


PROFILE_PATH = ROOT / "experiments" / "ebook" / "exp-0011" / "execution-profile.json"
CONTRACTS_PATH = ROOT / "experiments" / "ebook" / "exp-0011" / "variant-contracts.json"
RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0011" / "result.json"
EXP_0010_MANIFEST_PATH = ROOT / "experiments" / "ebook" / "exp-0010" / "case-manifest.json"
QUALIFICATION_PATH = ROOT / "runtime" / "ebook-identity" / "qualification.json"
TEST_MANIFEST_PATH = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "manifest.json"
TEST_CASES = TEST_MANIFEST_PATH.parent / "cases"
EXP_0010_RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0010.py"
PRODUCT_STAGES = ("byte", "package", "representation", "edition", "work")
VARIANTS = ("V1", "V2", "V3")
RESIDUAL_CASES = {
    "same-primary-strong-content-conflict",
    "shared-untyped-additional-different-primary",
}
TEST_PAIRS = {
    "byte_equal": (
        "identity-byte-equal/source-a/same.epub",
        "identity-byte-equal/source-b/renamed.epub",
    ),
    "repackaged": (
        "identity-repackaged/package-a.epub",
        "identity-repackaged/package-b.epub",
    ),
    "sample_full": (
        "edition-sample-vs-full/sample.epub",
        "edition-sample-vs-full/full.epub",
    ),
    "title_collision": (
        "identity-title-collision/work-a.epub",
        "identity-title-collision/work-b.epub",
    ),
    "translation": (
        "identity-edition-vs-translation/source-en.epub",
        "identity-edition-vs-translation/translation-de.epub",
    ),
}
TEST_FIXTURE_LOCATORS = tuple(
    f"tests/fixtures/ebook/test-0001/v0.3/cases/{relative}"
    for pair in TEST_PAIRS.values()
    for relative in pair
)
PREIMAGE_FILES = (
    "docs/planning/EBOOK_IDENTITY_METADATA_CONTRACT_EXPERIMENT.md",
    "experiments/ebook/exp-0011/README.md",
    "experiments/ebook/exp-0011/execution-profile.json",
    "experiments/ebook/exp-0011/variant-contracts.json",
    "tests/experiments/test_exp_0011.py",
    "tests/governance/test_ebook_next_decision.py",
    "tools/experiments/run_exp_0011.py",
    "experiments/ebook/exp-0010/case-manifest.json",
    "experiments/ebook/exp-0010/result.json",
    "runtime/ebook-identity/qualification.json",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    *TEST_FIXTURE_LOCATORS,
    "src/sammlungslotse/ebook_identity/__init__.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/cli.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/application.py",
    "src/sammlungslotse/ebook_intake/model.py",
    "src/sammlungslotse/ebook_intake/ports.py",
    "src/sammlungslotse/ebook_intake/preflight.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tools/experiments/run_exp_0010.py",
    "tools/experiments/validate_exp_0010_result.py",
    "tools/qualify_ebook_identity.py",
    "tools/run_ebook_identity.py",
)
ALLOWED_PREIMAGE_CHANGES = {
    "docs/planning/EBOOK_IDENTITY_METADATA_CONTRACT_EXPERIMENT.md",
    "experiments/ebook/exp-0011/README.md",
    "experiments/ebook/exp-0011/execution-profile.json",
    "experiments/ebook/exp-0011/variant-contracts.json",
    "tests/experiments/test_exp_0011.py",
    "tests/governance/test_ebook_next_decision.py",
    "tools/experiments/run_exp_0011.py",
}
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


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load bound module {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXP_0010 = load_module(EXP_0010_RUNNER_PATH, "exp_0010_for_exp_0011")


def load_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    profile = load_json(PROFILE_PATH)
    contracts = load_json(CONTRACTS_PATH)
    if profile.get("schema") != "sammlungslotse/exp-0011-execution-profile/v1":
        raise RuntimeError("EXP-0011 profile schema differs")
    if profile.get("artifact") != "EXP-0011" or profile.get("repetitions") != 2:
        raise RuntimeError("EXP-0011 profile identity differs")
    if profile.get("case_sources") != {
        "exp_0010_control": 2,
        "exp_0010_quality": 8,
        "test_0001": 5,
        "total": 15,
    }:
        raise RuntimeError("EXP-0011 case matrix differs")
    if profile.get("variants") != list(VARIANTS):
        raise RuntimeError("EXP-0011 variants differ")
    implementation = profile.get("implementation", {})
    if implementation.get("synthetic_only") is not True or any(
        implementation.get(key) is not False
        for key in (
            "container_access",
            "network_access",
            "product_code_changes",
            "versioned_media_writes",
        )
    ):
        raise RuntimeError("EXP-0011 implementation boundary differs")
    if contracts.get("schema") != "sammlungslotse/exp-0011-variant-contracts/v1":
        raise RuntimeError("EXP-0011 variant contract schema differs")
    if set(contracts.get("variants", {})) != set(VARIANTS):
        raise RuntimeError("EXP-0011 variant contract set differs")
    for name in VARIANTS:
        contract = contracts["variants"][name]
        if (
            contract.get("classification_rule") not in profile["result_classifications"]
            or not contract.get("field_mapping")
            or not contract.get("migration_surface")
        ):
            raise RuntimeError(f"EXP-0011 {name} contract is incomplete")
    return profile, contracts


class BytesSnapshotReader:
    """Supply an immutable in-memory synthetic snapshot without a locator."""

    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def capture(self, limits: TriageLimits) -> Snapshot:
        if len(self.payload) > limits.max_input_bytes:
            raise RuntimeError("EXP-0011 synthetic input exceeds the bound")
        return Snapshot(
            data=self.payload,
            size_bytes=len(self.payload),
            sha256=sha256_bytes(self.payload),
            suffix=".epub",
        )


def current_report(payloads: tuple[bytes, bytes]) -> dict[str, Any]:
    report = IdentityCandidateService().compare(
        BytesSnapshotReader(payloads[0]),
        BytesSnapshotReader(payloads[1]),
        IdentityLimits(),
    ).to_dict()
    if report["effects"] != {
        "domain_system_writes": False,
        "filesystem_writes": False,
        "network_access": False,
        "original_modified": False,
    }:
        raise RuntimeError("EXP-0011 product effects differ")
    return report


def empty_standard_projection() -> dict[str, Any]:
    return {
        "additional_identifiers": [],
        "collections": [],
        "modified": None,
        "primary_identifier": None,
        "unique_identifier_ref": None,
    }


def _leaf_provenance(value: Any, prefix: str, source: str) -> dict[str, dict[str, str]]:
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


def structured_metadata(projection: dict[str, Any], input_index: int) -> dict[str, Any]:
    value = {
        "input_index": input_index,
        "primary_identifier": copy.deepcopy(projection["primary_identifier"]),
        "primary_identifier_element_ref": projection["unique_identifier_ref"],
        "additional_identifiers": copy.deepcopy(projection["additional_identifiers"]),
        "modified": projection["modified"],
        "collection_memberships": copy.deepcopy(projection["collections"]),
    }
    sources = {
        "primary_identifier": "package@unique-identifier and dc:identifier",
        "primary_identifier_element_ref": "package@unique-identifier",
        "additional_identifiers": "dc:identifier and identifier-type refinements",
        "modified": "meta[property=dcterms:modified]",
        "collection_memberships": "belongs-to-collection refinements",
    }
    provenance: dict[str, dict[str, str]] = {}
    for key, source in sources.items():
        provenance.update(_leaf_provenance(value[key], key, source))
    value["provenance"] = provenance
    return value


def _role_aware_report(
    report: dict[str, Any],
    standards: list[dict[str, Any]],
    schema: str,
    *,
    publication_stage: bool,
) -> dict[str, Any]:
    candidate = copy.deepcopy(report)
    candidate["schema"] = schema
    for item in candidate["inputs"]:
        index = item["input_index"]
        legacy = item["metadata"]
        structured = structured_metadata(standards[index - 1], index)
        item["metadata"] = {
            "titles": legacy["titles"],
            "creators": legacy["creators"],
            "languages": legacy["languages"],
            "primary_identifier": structured["primary_identifier"],
            "primary_identifier_element_ref": structured["primary_identifier_element_ref"],
            "additional_identifiers": structured["additional_identifiers"],
            "modified": structured["modified"],
            "collection_memberships": structured["collection_memberships"],
            "provenance": structured["provenance"],
        }
    if publication_stage and candidate["assessment"] == "completed":
        stage = {
            "assessment": "not_assessed",
            "missing_evidence": ["experiment.publication.product_rule_absent"],
            "negative_evidence": [],
            "positive_evidence": [],
            "reason_codes": ["experiment.publication.no_product_rule"],
            "stage": "publication",
        }
        position = next(
            index + 1
            for index, item in enumerate(candidate["stages"])
            if item["stage"] == "representation"
        )
        candidate["stages"].insert(position, stage)
    return candidate


def project_variants(
    report: dict[str, Any], standards: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    evidence = [structured_metadata(item, index) for index, item in enumerate(standards, 1)]
    return {
        "V1": {
            "schema": "sammlungslotse/experiment/exp-0011/v1-plus-evidence-companion",
            "variant": "V1",
            "report_v1": copy.deepcopy(report),
            "evidence_companion": {"inputs": evidence},
            "publication_expression": {"assessment": "gap", "separate_stage": False},
            "legacy_semantic_debt": {
                "preserved_field": "report_v1.inputs[].metadata.work_references",
                "experiment_owned_collection_label": "collection_memberships",
            },
        },
        "V2": {
            "schema": "sammlungslotse/experiment/exp-0011/role-aware-five-stage-v2",
            "variant": "V2",
            "report": _role_aware_report(
                report,
                standards,
                "sammlungslotse/experiment/exp-0011/role-aware-five-stage-v2",
                publication_stage=False,
            ),
            "source_evidence": evidence,
            "publication_expression": {"assessment": "gap", "separate_stage": False},
        },
        "V3": {
            "schema": "sammlungslotse/experiment/exp-0011/role-aware-publication-stage-v2",
            "variant": "V3",
            "report": _role_aware_report(
                report,
                standards,
                "sammlungslotse/experiment/exp-0011/role-aware-publication-stage-v2",
                publication_stage=True,
            ),
            "source_evidence": evidence,
            "publication_expression": {
                "assessment": "not_assessed",
                "separate_stage": True,
            },
        },
    }


def _report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "overall": report["overall"],
        "stages": {
            item["stage"]: {"decision": item["decision"], "rule_id": item["rule_id"]}
            for item in report["stages"]
        },
    }


def _assert_qualification(
    source: str,
    case_key: str,
    report: dict[str, Any],
    qualification: dict[str, Any],
) -> None:
    if source == "test_0001":
        expected = qualification["test_0001_case_results"][case_key]
        actual = {
            "edition": next(item["decision"] for item in report["stages"] if item["stage"] == "edition"),
            "overall": report["overall"],
            "work": next(item["decision"] for item in report["stages"] if item["stage"] == "work"),
        }
    else:
        expected = qualification["guardrail_case_results"][case_key]
        actual = _report_summary(report)
    if actual != expected:
        raise RuntimeError(f"EXP-0011 {source} {case_key} differs from WI-0012 qualification")


def _standard_projections(payloads: tuple[bytes, bytes]) -> list[dict[str, Any]]:
    return [EXP_0010.standard_metadata_projection(payload) for payload in payloads]


def evaluate_cases() -> tuple[list[dict[str, Any]], dict[str, str]]:
    qualification = load_json(QUALIFICATION_PATH)
    manifest = load_json(EXP_0010_MANIFEST_PATH)
    EXP_0010.validate_manifest(manifest)
    cases: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {}

    for case_key, relative_paths in TEST_PAIRS.items():
        payloads = tuple((TEST_CASES / relative).read_bytes() for relative in relative_paths)
        for relative, payload in zip(relative_paths, payloads, strict=True):
            locator = f"test-0001:{relative}"
            digest = sha256_bytes(payload)
            if qualification["test_0001_fixture_hashes"][relative] != digest:
                raise RuntimeError(f"EXP-0011 TEST-0001 input hash differs: {relative}")
            input_hashes[locator] = digest
        report = current_report(payloads)
        _assert_qualification("test_0001", case_key, report, qualification)
        standards = _standard_projections(payloads)
        cases.append(
            {
                "case_key": case_key,
                "oracle_scope": "qualified_product_observation",
                "source": "test_0001",
                "standard_metadata_projection": standards,
                "product_report_v1": report,
                "variants": project_variants(report, standards),
            }
        )

    for source_case in manifest["cases"]:
        case_key = source_case["case_key"]
        payloads = tuple(
            EXP_0010.generate_epub(EXP_0010.merged_spec(manifest, source_case, side))
            for side in ("left", "right")
        )
        for side, payload in zip(("left", "right"), payloads, strict=True):
            digest = sha256_bytes(payload)
            input_hashes[f"exp-0010:{case_key}:{side}"] = digest
            expected_hash = qualification.get("guardrail_input_hashes", {}).get(case_key, {}).get(side)
            if source_case["oracle_scope"] == "quality" and expected_hash != digest:
                raise RuntimeError(f"EXP-0011 EXP-0010 input hash differs: {case_key} {side}")
        report = current_report(payloads)
        if source_case["oracle_scope"] == "quality":
            _assert_qualification("exp_0010", case_key, report, qualification)
        elif report["assessment"] != "not_assessed":
            raise RuntimeError(f"EXP-0011 invalid control was assessed: {case_key}")
        standards = _standard_projections(payloads)
        cases.append(
            {
                "case_key": case_key,
                "oracle_scope": source_case["oracle_scope"],
                "publication_oracle": source_case.get("publication_oracle"),
                "source": "exp_0010",
                "standard_metadata_projection": standards,
                "product_report_v1": report,
                "variants": project_variants(report, standards),
            }
        )
    return cases, dict(sorted(input_hashes.items()))


def _product_stage_signature(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [copy.deepcopy(item) for item in report["stages"] if item["stage"] in PRODUCT_STAGES]


def _variant_structured_inputs(case: dict[str, Any], name: str) -> list[dict[str, Any]]:
    variant = case["variants"][name]
    if name == "V1":
        return variant["evidence_companion"]["inputs"]
    report_inputs = variant["report"]["inputs"]
    if report_inputs:
        return [
            {
                "input_index": item["input_index"],
                **{
                    key: item["metadata"][key]
                    for key in (
                        "primary_identifier",
                        "primary_identifier_element_ref",
                        "additional_identifiers",
                        "modified",
                        "collection_memberships",
                        "provenance",
                    )
                },
            }
            for item in report_inputs
        ]
    return variant["source_evidence"]


def _contains_key(value: Any, forbidden: str) -> bool:
    if isinstance(value, dict):
        return forbidden in value or any(_contains_key(item, forbidden) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, forbidden) for item in value)
    return False


def measure_variants(
    cases: list[dict[str, Any]], contracts: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for name in VARIANTS:
        losses: list[str] = []
        provenance_total = 0
        provenance_covered = 0
        decision_equal = True
        v1_byte_equal = True
        semantic_violations: list[str] = []
        residual_visible: list[str] = []
        for case in cases:
            variant = case["variants"][name]
            projected = _variant_structured_inputs(case, name)
            if case["source"] == "exp_0010" and case["oracle_scope"] == "quality":
                for input_index, (expected, actual) in enumerate(
                    zip(case["standard_metadata_projection"], projected, strict=True), 1
                ):
                    expected_fields = {
                        "primary_identifier": expected["primary_identifier"],
                        "primary_identifier_element_ref": expected["unique_identifier_ref"],
                        "additional_identifiers": expected["additional_identifiers"],
                        "modified": expected["modified"],
                        "collection_memberships": expected["collections"],
                    }
                    for field, expected_value in expected_fields.items():
                        if actual[field] != expected_value:
                            losses.append(f"{case['case_key']}:{input_index}:{field}")
                    for evidence in actual["provenance"].values():
                        provenance_total += 1
                        if evidence.get("source") and evidence.get("status") in {
                            "observed",
                            "derived",
                            "missing",
                        }:
                            provenance_covered += 1
            candidate_report = variant["report_v1"] if name == "V1" else variant["report"]
            if _product_stage_signature(candidate_report) != _product_stage_signature(
                case["product_report_v1"]
            ):
                decision_equal = False
            if case["product_report_v1"]["assessment"] == "completed" and name == "V1":
                if canonical_json(candidate_report) != canonical_json(case["product_report_v1"]):
                    v1_byte_equal = False
            semantic_surface = (
                {key: value for key, value in variant.items() if key != "report_v1"}
                if name == "V1"
                else variant
            )
            if _contains_key(semantic_surface, "work_references"):
                semantic_violations.append(case["case_key"])
            if case["case_key"] in RESIDUAL_CASES:
                work = next(
                    item
                    for item in _product_stage_signature(candidate_report)
                    if item["stage"] == "work"
                )
                if (
                    work["decision"] == "candidate_related"
                    and work["rule_id"] == "identity.work.title_creator"
                ):
                    residual_visible.append(case["case_key"])
        publication = contracts["variants"][name]["publication_expression"]
        metrics[name] = {
            "classification": contracts["variants"][name]["classification_rule"],
            "decision_fidelity": decision_equal,
            "field_mapping": contracts["variants"][name]["field_mapping"],
            "legacy_v1_semantic_debt_visible": name == "V1",
            "migration_surface": contracts["variants"][name]["migration_surface"],
            "provenance_coverage": {
                "covered": provenance_covered,
                "ratio": 1 if provenance_total and provenance_covered == provenance_total else 0,
                "total": provenance_total,
            },
            "publication_expression": publication,
            "residual_cases_visible": sorted(residual_visible),
            "role_loss": {"count": len(losses), "fields": losses},
            "semantic_naming_violations": sorted(set(semantic_violations)),
            "v1_report_byte_equal": v1_byte_equal if name == "V1" else False,
        }
    return metrics


def current_preimage() -> dict[str, str]:
    result: dict[str, str] = {}
    for locator in PREIMAGE_FILES:
        path = ROOT / locator
        if not path.is_file():
            raise RuntimeError(f"EXP-0011 preimage file missing: {locator}")
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
        raise RuntimeError("EXP-0011 empirical run requires a clean preimage commit")
    head = git_output("rev-parse", "HEAD")
    origin_main = git_output("rev-parse", "origin/main")
    merge_base = git_output("merge-base", "HEAD", "origin/main")
    if merge_base != origin_main:
        raise RuntimeError("EXP-0011 preimage does not descend from exact origin/main")
    registry = json.loads(git_output("show", "origin/main:.ai/artifact_registry.json"))["artifacts"]
    if registry["GATE-0011"]["status"] != "done" or registry["EXP-0011"]["status"] != "accepted":
        raise RuntimeError("EXP-0011 accepted plan is not canonical on origin/main")
    changed = set(filter(None, git_output("diff", "--name-only", "origin/main...HEAD").splitlines()))
    if changed != ALLOWED_PREIMAGE_CHANGES:
        raise RuntimeError("EXP-0011 preimage change set differs from the frozen experiment")
    product_changes = git_output(
        "diff",
        "--name-only",
        "origin/main...HEAD",
        "--",
        "src",
        "runtime/ebook-identity",
        "tests/fixtures",
        "tools/run_ebook_identity.py",
        "tools/qualify_ebook_identity.py",
        "experiments/ebook/exp-0010",
    )
    if product_changes:
        raise RuntimeError("EXP-0011 preimage changes product or bound source evidence")
    return {
        "allowed_change_set": True,
        "exp_0011_accepted_on_origin_main": True,
        "gate_0011_done_on_origin_main": True,
        "merge_base": merge_base,
        "origin_main": origin_main,
        "preimage_commit": head,
        "product_and_bound_sources_unchanged": True,
    }


def result_path_free(result: dict[str, Any]) -> bool:
    redacted = dict(result)
    redacted.pop("result_content_sha256", None)
    return PRIVATE_PATH_PATTERN.search(canonical_json(redacted)) is None


def result_payload_digest(result: dict[str, Any]) -> str:
    return canonical_digest(
        {key: value for key, value in result.items() if key != "result_content_sha256"}
    )


def acceptance_from_result(
    result: dict[str, Any], profile: dict[str, Any], contracts: dict[str, Any]
) -> dict[str, bool]:
    cases = result.get("cases", [])
    metrics = measure_variants(cases, contracts) if len(cases) == 15 else {}
    qualified = [case for case in cases if case.get("oracle_scope") != "control"]
    counts = {
        "test_0001": sum(case.get("source") == "test_0001" for case in cases),
        "exp_0010_quality": sum(case.get("oracle_scope") == "quality" for case in cases),
        "exp_0010_control": sum(case.get("oracle_scope") == "control" for case in cases),
        "total": len(cases),
    }
    projections_complete = len(cases) == 15 and all(
        set(case.get("variants", {})) == set(VARIANTS) for case in cases
    )
    roles_preserved = bool(metrics) and all(
        value["role_loss"]["count"] == 0 and value["provenance_coverage"]["ratio"] == 1
        for value in metrics.values()
    )
    publication = bool(metrics) and (
        metrics["V1"]["publication_expression"] == "gap"
        and metrics["V2"]["publication_expression"] == "gap"
        and metrics["V3"]["publication_expression"] == "separate_not_assessed_stage"
    )
    residual = bool(metrics) and all(
        set(value["residual_cases_visible"]) == RESIDUAL_CASES for value in metrics.values()
    )
    authority = result.get("authority", {})
    effects = result.get("effects", {})
    return {
        "01_complete_git_and_sha_preimage_binding": (
            set(result.get("preimage", {})) == set(PREIMAGE_FILES)
            and result.get("preimage") == current_preimage()
            and bool(re.fullmatch(r"[0-9a-f]{40}", result.get("preimage_commit", "")))
        ),
        "02_exactly_fifteen_synthetic_pairs": counts == profile["case_sources"],
        "03_three_complete_variant_projections": projections_complete,
        "04_v1_reports_byte_identical_for_thirteen_qualified_cases": (
            len(qualified) == 13 and metrics.get("V1", {}).get("v1_report_byte_equal") is True
        ),
        "05_roles_and_provenance_lossless_for_quality_matrix": roles_preserved,
        "06_no_experiment_collection_field_named_work_reference": bool(metrics)
        and all(not value["semantic_naming_violations"] for value in metrics.values()),
        "07_five_product_stage_contracts_unchanged": bool(metrics)
        and all(value["decision_fidelity"] for value in metrics.values()),
        "08_publication_gap_and_separate_v3_stage_visible": publication,
        "09_residual_candidate_related_cases_visible": residual,
        "10_field_mappings_and_migration_surfaces_complete": bool(metrics)
        and all(value["field_mapping"] and value["migration_surface"] for value in metrics.values()),
        "11_two_semantic_repetitions_identical": (
            len(result.get("repetition_semantic_sha256", [])) == 2
            and len(set(result["repetition_semantic_sha256"])) == 1
        ),
        "12_inputs_unchanged_path_free_and_zero_effect": (
            result.get("source_input_hashes_before") == result.get("source_input_hashes_after")
            and result_path_free(result)
            and effects
            == {
                "container_access": False,
                "domain_system_writes": False,
                "filesystem_writes_except_result": False,
                "network_access": False,
                "original_modified": False,
                "persistence_access": False,
                "versioned_media_writes": False,
            }
        ),
        "13_product_schema_fixtures_and_prior_evidence_unchanged": (
            authority.get("product_and_bound_sources_unchanged") is True
            and authority.get("allowed_change_set") is True
        ),
        "14_result_metrics_recomputed_without_experiment_rerun": (
            result.get("metrics") == metrics and result.get("validator_contract") == "recalculate/v1"
        ),
    }


def run_experiment() -> dict[str, Any]:
    profile, contracts = load_contract()
    authority = authority_evidence()
    preimage = current_preimage()
    first_cases, first_hashes = evaluate_cases()
    second_cases, second_hashes = evaluate_cases()
    first_digest = canonical_digest(first_cases)
    second_digest = canonical_digest(second_cases)
    result: dict[str, Any] = {
        "artifact": "EXP-0011",
        "authority": authority,
        "cases": first_cases,
        "effects": {
            "container_access": False,
            "domain_system_writes": False,
            "filesystem_writes_except_result": False,
            "network_access": False,
            "original_modified": False,
            "persistence_access": False,
            "versioned_media_writes": False,
        },
        "metrics": measure_variants(first_cases, contracts),
        "preimage": preimage,
        "preimage_commit": authority["preimage_commit"],
        "profile": profile["profile_id"],
        "repetition_semantic_sha256": [first_digest, second_digest],
        "schema": "sammlungslotse/exp-0011-result/v1",
        "source_input_hashes_after": second_hashes,
        "source_input_hashes_before": first_hashes,
        "validator_contract": "recalculate/v1",
    }
    result["acceptance"] = acceptance_from_result(result, profile, contracts)
    result["status"] = "pass" if all(result["acceptance"].values()) else "fail"
    result["result_content_sha256"] = result_payload_digest(result)
    if result["status"] != "pass" or first_hashes != second_hashes or first_digest != second_digest:
        raise RuntimeError("EXP-0011 acceptance or determinism failed")
    RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    profile, contracts = load_contract()
    result = load_json(path)
    if result.get("schema") != "sammlungslotse/exp-0011-result/v1" or result.get("artifact") != "EXP-0011":
        raise RuntimeError("EXP-0011 result identity differs")
    if result.get("result_content_sha256") != result_payload_digest(result):
        raise RuntimeError("EXP-0011 result content digest differs")
    acceptance = acceptance_from_result(result, profile, contracts)
    if result.get("acceptance") != acceptance or not all(acceptance.values()):
        raise RuntimeError("EXP-0011 acceptance evidence differs")
    if result.get("status") != "pass":
        raise RuntimeError("EXP-0011 result status differs")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--validate-profile", action="store_true")
    group.add_argument("--validate-result", action="store_true")
    arguments = parser.parse_args()
    if arguments.validate_profile:
        load_contract()
        current_preimage()
        print("EXP-0011 profile validation: pass")
        return 0
    if arguments.validate_result:
        result = validate_result()
        print(f"EXP-0011 result validation: {result['status']}")
        return 0
    result = run_experiment()
    print(
        "EXP-0011 execution: "
        f"{result['status']}; cases={len(result['cases'])}; "
        f"semantic_sha256={result['repetition_semantic_sha256'][0]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
