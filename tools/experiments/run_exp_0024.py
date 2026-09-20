#!/usr/bin/env python3
"""Execute or validate the product-code-free synthetic EXP-0024 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "experiments" / "ebook" / "exp-0024" / "cases.json"
RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0024" / "result.json"
CASE_SCHEMA = "sammlungslotse/ebook-multi-library-routing-experiment-cases/v1"
RESULT_SCHEMA = "sammlungslotse/ebook-multi-library-routing-experiment-result/v1"
RULE_VERSION, EVIDENCE_VERSION = "routing-rules/v1", "test-0001/v0.3"
MAX_LIBRARIES, MAX_CANDIDATES = 3, 4


class ExperimentError(ValueError):
    """Raised when the immutable synthetic experiment contract is invalid."""


def _validate_case(case: dict[str, Any]) -> None:
    required = {"case_id", "ingress", "evidence_keys", "snapshots", "expected_class", "expected_state", "expected_candidates"}
    if set(case) != required or case["ingress"] not in {"clear", "review"} or not isinstance(case["evidence_keys"], list):
        raise ExperimentError("case boundary is invalid")
    snapshots = case["snapshots"]
    if not isinstance(snapshots, list) or len(snapshots) > MAX_LIBRARIES:
        raise ExperimentError("snapshot count is outside the bound")
    for snapshot in snapshots:
        if set(snapshot) != {"library_position", "integrity", "records"} or snapshot["library_position"] not in range(1, MAX_LIBRARIES + 1) or snapshot["integrity"] not in {"complete", "incomplete"}:
            raise ExperimentError("snapshot boundary is invalid")
        for record in snapshot["records"]:
            if set(record) != {"evidence_keys"} or not isinstance(record["evidence_keys"], list):
                raise ExperimentError("record is not a minimal synthetic projection")


def load_cases() -> list[dict[str, Any]]:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if payload.get("schema") != CASE_SCHEMA or not isinstance(cases, list) or len(cases) != 10:
        raise ExperimentError("EXP-0024 requires exactly ten bound cases")
    if [case.get("case_id") for case in cases] != [f"M{number:02d}" for number in range(1, 11)]:
        raise ExperimentError("case identifiers are not the bound matrix")
    for case in cases:
        _validate_case(case)
    return cases


def _outcome(case_id: str, review_class: str, state: str, candidates: list[dict[str, Any]], candidate_total: int | None = None) -> dict[str, Any]:
    return {"case_id": case_id, "review_class": review_class, "state": state, "candidate_total": len(candidates) if candidate_total is None else candidate_total, "candidates": candidates}


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    snapshots = case["snapshots"]
    if case["ingress"] != "clear":
        return _outcome(case["case_id"], "not_assessed", "ingress_not_clear", [])
    if not snapshots:
        return _outcome(case["case_id"], "not_assessed", "projection_absent", [])
    positions = [snapshot["library_position"] for snapshot in snapshots]
    if len(set(positions)) != len(positions):
        return _outcome(case["case_id"], "review_scope_incomplete", "library_position_ambiguous", [])
    if any(snapshot["integrity"] != "complete" for snapshot in snapshots):
        return _outcome(case["case_id"], "review_scope_incomplete", "inventory_incomplete", [])
    candidates = []
    for snapshot in snapshots:
        for record in snapshot["records"]:
            if set(case["evidence_keys"]).intersection(record["evidence_keys"]):
                candidates.append({"library_position": snapshot["library_position"], "candidate_reason": "bound_evidence_key"})
    candidates.sort(key=lambda item: item["library_position"])
    if len(candidates) > MAX_CANDIDATES:
        return _outcome(case["case_id"], "review_scope_incomplete", "candidate_bound_exceeded", candidates[:MAX_CANDIDATES], len(candidates))
    if not candidates:
        return _outcome(case["case_id"], "not_assessed", "no_bound_evidence", [])
    if len({candidate["library_position"] for candidate in candidates}) > 1:
        return _outcome(case["case_id"], "review_cross_library", "cross_library_conflict", candidates)
    return _outcome(case["case_id"], "review_target_candidate", "single_library_candidate", candidates)


def _public_result_safe(value: Any) -> bool:
    forbidden_keys = {"evidence_keys", "records", "snapshots", "path", "title", "authors", "formats", "url", "target_library", "rank"}
    if isinstance(value, dict):
        return all(key not in forbidden_keys and _public_result_safe(item) for key, item in value.items())
    if isinstance(value, list):
        return all(_public_result_safe(item) for item in value)
    return not isinstance(value, str) or ("\\" not in value and "://" not in value)


def validate_result_dict(payload: dict[str, Any]) -> dict[str, Any]:
    cases = load_cases()
    effects = {"calibre_execution": False, "container_execution": False, "discovery": False, "external_network_access": False, "persistence": False, "product_code_modified": False, "writer_effects": False}
    if payload.get("schema") != RESULT_SCHEMA or payload.get("artifact") != "EXP-0024" or payload.get("status") != "pass":
        raise ExperimentError("result identity is invalid")
    if payload.get("case_count") != 10 or payload.get("repetitions") != 2 or payload.get("runs_semantically_identical") is not True:
        raise ExperimentError("result repetition contract is invalid")
    if payload.get("rule_version") != RULE_VERSION or payload.get("evidence_version") != EVIDENCE_VERSION or payload.get("case_manifest_sha256") != hashlib.sha256(CASES_PATH.read_bytes()).hexdigest():
        raise ExperimentError("result provenance is invalid")
    if payload.get("effects") != effects or payload.get("limits") != {"libraries_max": MAX_LIBRARIES, "candidates_per_input_max": MAX_CANDIDATES}:
        raise ExperimentError("forbidden effect or bound is invalid")
    outcomes = payload.get("outcomes")
    if not isinstance(outcomes, list) or len(outcomes) != len(cases):
        raise ExperimentError("result outcomes are invalid")
    for case, outcome in zip(cases, outcomes, strict=True):
        if outcome != evaluate(case) or outcome["review_class"] != case["expected_class"] or outcome["state"] != case["expected_state"] or outcome["candidate_total"] != case["expected_candidates"]:
            raise ExperimentError("result outcome does not match the bound oracle")
    if not _public_result_safe(payload):
        raise ExperimentError("result contains forbidden source, path, or target data")
    return payload


def execute(temp_root: Path) -> dict[str, Any]:
    if temp_root.exists():
        raise ExperimentError("temporary experiment root must not exist")
    source_digest = hashlib.sha256(CASES_PATH.read_bytes()).hexdigest()
    try:
        temp_root.mkdir(parents=True)
        cases = load_cases()
        repetitions = [[evaluate(case) for case in cases] for _ in range(2)]
        if repetitions[0] != repetitions[1] or source_digest != hashlib.sha256(CASES_PATH.read_bytes()).hexdigest():
            raise ExperimentError("synthetic repetitions or source binding differ")
        result = {"schema": RESULT_SCHEMA, "artifact": "EXP-0024", "status": "pass", "case_count": 10, "repetitions": 2, "runs_semantically_identical": True, "rule_version": RULE_VERSION, "evidence_version": EVIDENCE_VERSION, "case_manifest_sha256": source_digest, "limits": {"libraries_max": MAX_LIBRARIES, "candidates_per_input_max": MAX_CANDIDATES}, "effects": {"calibre_execution": False, "container_execution": False, "discovery": False, "external_network_access": False, "persistence": False, "product_code_modified": False, "writer_effects": False}, "outcomes": repetitions[0]}
        return validate_result_dict(result)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        if temp_root.exists():
            raise ExperimentError("temporary experiment root was not removed")


def validate_result(path: Path = RESULT_PATH) -> None:
    validate_result_dict(json.loads(path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temp-root", type=Path)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    if args.validate_result:
        validate_result(); print("[OK] EXP-0024 result contract"); return 0
    temporary = args.temp_root or Path(tempfile.mkdtemp(prefix="sammlungslotse-exp-0024-"))
    if args.temp_root is None:
        shutil.rmtree(temporary)
    result = execute(temporary)
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
