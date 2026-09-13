#!/usr/bin/env python3
"""Execute or validate the product-code-free synthetic EXP-0019 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "experiments" / "ebook" / "exp-0019" / "cases.json"
RESULT_PATH = ROOT / "experiments" / "ebook" / "exp-0019" / "result.json"
CASE_SCHEMA = "sammlungslotse/ebook-inbox-calibre-review-plan-experiment-cases/v1"
RESULT_SCHEMA = "sammlungslotse/ebook-inbox-calibre-review-plan-experiment-result/v1"
MAX_LIBRARIES, MAX_CANDIDATES_PER_EPUB, MAX_CANDIDATES_PER_FOLDER = 3, 5, 12


class ExperimentError(ValueError):
    """Raised when the immutable synthetic experiment contract is invalid."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _validate_case(case: dict[str, Any]) -> None:
    required = {"case_id", "ingress", "format", "title", "authors", "languages", "snapshots", "expected_class", "expected_candidates"}
    if set(case) != required or case["ingress"] not in {"clear", "review"} or case["format"] not in {"EPUB", "PDF"}:
        raise ExperimentError("case boundary is invalid")
    if not isinstance(case["snapshots"], list) or len(case["snapshots"]) > MAX_LIBRARIES:
        raise ExperimentError("snapshot count is outside the bound")
    for snapshot in case["snapshots"]:
        allowed = {"library_position", "snapshot_id", "profile_id", "provider_id", "records", "integrity"}
        if not set(snapshot).issubset(allowed) or not {"library_position", "snapshot_id", "profile_id", "provider_id", "records"}.issubset(snapshot):
            raise ExperimentError("snapshot fields exceed the projection contract")
        if snapshot["library_position"] not in range(1, MAX_LIBRARIES + 1) or snapshot.get("integrity", "valid") not in {"valid", "inconsistent"}:
            raise ExperimentError("snapshot boundary is invalid")
        for record in snapshot["records"]:
            if set(record) != {"id", "title", "authors", "languages", "formats"} or not isinstance(record["id"], int):
                raise ExperimentError("record is not a minimal Calibre projection")


def load_cases() -> list[dict[str, Any]]:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if payload.get("schema") != CASE_SCHEMA or not isinstance(cases, list) or len(cases) != 10:
        raise ExperimentError("EXP-0019 requires exactly ten bound cases")
    if [case.get("case_id") for case in cases] != [f"C{number:02d}" for number in range(1, 11)]:
        raise ExperimentError("case identifiers are not the bound matrix")
    for case in cases:
        _validate_case(case)
    return cases


def _candidate_reason(case: dict[str, Any], record: dict[str, Any]) -> str | None:
    if case["title"] != record["title"]:
        return None
    return "title_author" if case["authors"] == record["authors"] else "title"


def _snapshot_digest(snapshot: dict[str, Any]) -> str:
    return sha256({key: snapshot[key] for key in ("snapshot_id", "profile_id", "provider_id", "records")})


def _outcome(case_id: str, review_class: str, candidate_total: int, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {"case_id": case_id, "review_class": review_class, "candidate_total": candidate_total, "candidates": candidates}


def enforce_folder_candidate_bound(outcomes: list[dict[str, Any]]) -> None:
    """Reject a review-plan folder whose discovered candidates exceed its bound."""

    if sum(item["candidate_total"] for item in outcomes) > MAX_CANDIDATES_PER_FOLDER:
        raise ExperimentError("folder candidate limit did not fail closed")


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    snapshots = case["snapshots"]
    positions = [snapshot["library_position"] for snapshot in snapshots]
    if any(snapshot.get("integrity", "valid") != "valid" for snapshot in snapshots) or len(set(positions)) != len(positions):
        return _outcome(case["case_id"], "not_assessed", 0, [])
    if case["ingress"] != "clear":
        return _outcome(case["case_id"], "review_ingress_blocked", 0, [])
    if case["format"] != "EPUB":
        return _outcome(case["case_id"], "unsupported", 0, [])
    candidates = []
    for snapshot in snapshots:
        digest = _snapshot_digest(snapshot)
        for record in snapshot["records"]:
            reason = _candidate_reason(case, record)
            if reason:
                candidates.append({"library_position": snapshot["library_position"], "external_record_id": record["id"], "reason": reason, "snapshot_digest": digest})
    candidates.sort(key=lambda item: (item["library_position"], item["external_record_id"]))
    total = len(candidates)
    if total > MAX_CANDIDATES_PER_EPUB:
        return _outcome(case["case_id"], "review_scope_incomplete", total, candidates[:MAX_CANDIDATES_PER_EPUB])
    if not candidates:
        return _outcome(case["case_id"], "review_new_candidate", 0, [])
    if len({candidate["library_position"] for candidate in candidates}) > 1:
        return _outcome(case["case_id"], "review_cross_library", total, candidates)
    return _outcome(case["case_id"], "review_candidate_present", total, candidates)


def _public_result_safe(value: Any) -> bool:
    forbidden_keys = {"title", "authors", "languages", "formats", "path", "raw_report", "url"}
    if isinstance(value, dict):
        return all(key not in forbidden_keys and _public_result_safe(item) for key, item in value.items())
    if isinstance(value, list):
        return all(_public_result_safe(item) for item in value)
    return not isinstance(value, str) or "\\" not in value and "://" not in value


def validate_result_dict(payload: dict[str, Any]) -> dict[str, Any]:
    cases = load_cases()
    if payload.get("schema") != RESULT_SCHEMA or payload.get("artifact") != "EXP-0019" or payload.get("status") != "pass":
        raise ExperimentError("result identity is invalid")
    if payload.get("case_count") != 10 or payload.get("repetitions") != 2 or payload.get("runs_semantically_identical") is not True:
        raise ExperimentError("result repetition contract is invalid")
    if payload.get("case_manifest_sha256") != hashlib.sha256(CASES_PATH.read_bytes()).hexdigest():
        raise ExperimentError("result is not bound to the current synthetic matrix")
    if payload.get("effects") != {"calibre_execution": False, "collection_modified": False, "external_network_access": False, "persistence": False, "product_code_modified": False, "writer_effects": False}:
        raise ExperimentError("forbidden effect boundary is invalid")
    if payload.get("limits") != {"libraries_max": 3, "candidates_per_epub_max": 5, "candidates_per_folder_max": 12}:
        raise ExperimentError("result limits are invalid")
    outcomes = payload.get("outcomes")
    if not isinstance(outcomes, list) or len(outcomes) != 10:
        raise ExperimentError("result outcomes are invalid")
    for case, outcome in zip(cases, outcomes, strict=True):
        if outcome != evaluate(case) or outcome["review_class"] != case["expected_class"]:
            raise ExperimentError("result outcome does not match the bound oracle")
    if not _public_result_safe(payload):
        raise ExperimentError("result contains a path, URL, or source metadata")
    return payload


def execute(temp_root: Path) -> dict[str, Any]:
    if temp_root.exists():
        raise ExperimentError("temporary experiment root must not exist")
    cases = load_cases()
    source_digest_before = hashlib.sha256(CASES_PATH.read_bytes()).hexdigest()
    try:
        temp_root.parent.mkdir(parents=True, exist_ok=True)
        temp_root.mkdir()
        repetitions = [[evaluate(case) for case in cases] for _ in range(2)]
        if repetitions[0] != repetitions[1]:
            raise ExperimentError("synthetic repetitions differ")
        enforce_folder_candidate_bound(repetitions[0])
        for case, outcome in zip(cases, repetitions[0], strict=True):
            if outcome["review_class"] != case["expected_class"] or outcome["candidate_total"] != case["expected_candidates"]:
                raise ExperimentError("bound case oracle differs")
        if any(item["candidate_total"] > MAX_CANDIDATES_PER_EPUB and item["review_class"] != "review_scope_incomplete" for item in repetitions[0]):
            raise ExperimentError("candidate limit did not fail closed")
        if source_digest_before != hashlib.sha256(CASES_PATH.read_bytes()).hexdigest():
            raise ExperimentError("case source changed during execution")
        return validate_result_dict({
            "schema": RESULT_SCHEMA, "artifact": "EXP-0019", "status": "pass", "case_count": len(cases), "repetitions": 2,
            "runs_semantically_identical": True, "case_manifest_sha256": source_digest_before, "outcomes": repetitions[0],
            "effects": {"calibre_execution": False, "collection_modified": False, "external_network_access": False, "persistence": False, "product_code_modified": False, "writer_effects": False},
            "limits": {"libraries_max": MAX_LIBRARIES, "candidates_per_epub_max": MAX_CANDIDATES_PER_EPUB, "candidates_per_folder_max": MAX_CANDIDATES_PER_FOLDER},
        })
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        if temp_root.exists():
            raise ExperimentError("temporary experiment root was not removed")


def validate_result(path: Path = RESULT_PATH) -> None:
    validate_result_dict(json.loads(path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temp-root", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    if args.validate_result:
        validate_result(); print("[OK] EXP-0019 result contract"); return 0
    temporary = args.temp_root or Path(tempfile.mkdtemp(prefix="sammlungslotse-exp-0019-"))
    if args.temp_root is None:
        shutil.rmtree(temporary)
    result = execute(temporary)
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.result:
        args.result.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
