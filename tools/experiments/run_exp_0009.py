#!/usr/bin/env python3
"""Run and validate the synthetic EXP-0009 identity evidence matrix."""

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
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.ebook_identity.application import IdentityCandidateService  # noqa: E402
from sammlungslotse.ebook_identity.model import IdentityLimits  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0009"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
MANIFEST_PATH = EXPERIMENT / "case-manifest.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNNER_PATH = Path(__file__).resolve()
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")
STAGES = ("byte", "package", "representation", "edition", "work")
DECISIONS = frozenset(
    {"candidate_same", "candidate_related", "different", "abstain", "not_applicable"}
)
SPEC_KEYS = frozenset(
    {
        "body",
        "creators",
        "fault",
        "identifiers",
        "languages",
        "opf_style",
        "titles",
        "work_references",
        "zip_style",
    }
)
FAULTS = frozenset({"none", "corrupt_zip", "unsafe_path", "duplicate_logical_entry"})
ZIP_STYLES = frozenset({"stored_normal", "deflated_reverse"})
OPF_STYLES = frozenset({"compact", "spaced"})
EXPECTED_CASE_KEYS = frozenset(
    {
        "byte-identical-renamed",
        "case-whitespace-normalization",
        "collection-versus-constituent",
        "corrupt-zip-not-assessed",
        "duplicate-logical-entry-not-assessed",
        "metadata-collision-work-conflict",
        "missing-all-bibliographic-metadata",
        "missing-identifier-and-creator-one-side",
        "opf-whitespace-only",
        "reused-identifier-title-conflict",
        "revised-edition-shared-work",
        "same-identifier-edition",
        "sample-versus-full",
        "title-collision-different-creators",
        "translation-shared-work",
        "unicode-composition",
        "unsafe-package-path-not-assessed",
        "zip-repackaged",
    }
)
PREIMAGE_FILES = (
    "experiments/ebook/exp-0009/case-manifest.json",
    "experiments/ebook/exp-0009/execution-profile.json",
    "tests/experiments/test_exp_0009.py",
    "tools/experiments/run_exp_0009.py",
    "src/sammlungslotse/__init__.py",
    "src/sammlungslotse/ebook_identity/__init__.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/cli.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/__init__.py",
    "src/sammlungslotse/ebook_intake/application.py",
    "src/sammlungslotse/ebook_intake/model.py",
    "src/sammlungslotse/ebook_intake/ports.py",
    "src/sammlungslotse/ebook_intake/preflight.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tools/run_ebook_identity.py",
)
ACCEPTANCE_NAMES = frozenset(
    {
        "case_matrix_complete",
        "critical_findings_visible",
        "explanation_channels_complete",
        "inputs_unchanged_and_cleanup_complete",
        "metrics_recomputable",
        "oracle_evaluated",
        "ordered_stages",
        "path_free_result",
        "preimage_bound",
        "result_contract_self_bound",
        "semantic_repetitions_identical",
        "zero_external_or_domain_effects",
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


def _validate_string_list(value: Any, field: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise RuntimeError(f"EXP-0009 {field} must be a string list")


def merged_spec(manifest: dict[str, Any], case: dict[str, Any], side: str) -> dict[str, Any]:
    value = dict(manifest["defaults"])
    value.update(case.get("base", {}))
    value.update(case.get(side, {}))
    if set(value) != SPEC_KEYS:
        raise RuntimeError(f"EXP-0009 {case.get('case_key')} {side} fields differ")
    for field in ("creators", "identifiers", "languages", "titles", "work_references"):
        _validate_string_list(value[field], field)
    if not isinstance(value["body"], str):
        raise RuntimeError("EXP-0009 body must be text")
    if value["fault"] not in FAULTS or value["zip_style"] not in ZIP_STYLES:
        raise RuntimeError("EXP-0009 generator variant differs")
    if value["opf_style"] not in OPF_STYLES:
        raise RuntimeError("EXP-0009 OPF style differs")
    return value


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != "sammlungslotse/exp-0009-case-manifest/v1":
        raise RuntimeError("unexpected EXP-0009 case manifest schema")
    if manifest.get("artifact") != "EXP-0009" or set(manifest.get("defaults", {})) != SPEC_KEYS:
        raise RuntimeError("unexpected EXP-0009 case manifest identity")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != 18:
        raise RuntimeError("EXP-0009 requires exactly 18 cases")
    case_keys = [case.get("case_key") for case in cases]
    if len(set(case_keys)) != 18 or set(case_keys) != EXPECTED_CASE_KEYS:
        raise RuntimeError("EXP-0009 case keys differ")
    assessments = [case.get("expected_assessment") for case in cases]
    if assessments.count("completed") != 15 or assessments.count("not_assessed") != 3:
        raise RuntimeError("EXP-0009 assessment totals differ")
    for case in cases:
        if set(case) != {"base", "case_key", "expected_assessment", "left", "oracle", "right"}:
            raise RuntimeError(f"EXP-0009 {case.get('case_key')} contract fields differ")
        if not all(isinstance(case[item], dict) for item in ("base", "left", "right")):
            raise RuntimeError("EXP-0009 generator overrides differ")
        for value in (case["base"], case["left"], case["right"]):
            if not set(value).issubset(SPEC_KEYS):
                raise RuntimeError("EXP-0009 generator override field differs")
        merged_spec(manifest, case, "left")
        merged_spec(manifest, case, "right")
        oracle = case.get("oracle")
        if not isinstance(oracle, dict) or tuple(sorted(oracle)) != tuple(sorted(STAGES)):
            raise RuntimeError("EXP-0009 stage oracle differs")
        for stage in STAGES:
            allowed = oracle[stage]
            if not isinstance(allowed, list) or not allowed or not set(allowed) <= DECISIONS:
                raise RuntimeError("EXP-0009 allowed decision differs")
            if len(allowed) != len(set(allowed)):
                raise RuntimeError("EXP-0009 duplicate allowed decision")
        if case["expected_assessment"] == "not_assessed" and any(
            case["oracle"][stage] != ["not_applicable"] for stage in STAGES
        ):
            raise RuntimeError("EXP-0009 not-assessed oracle differs")
    serialized = canonical_json(manifest)
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise RuntimeError("EXP-0009 manifest contains a private absolute path")
    return manifest


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("schema") != "sammlungslotse/exp-0009-execution-profile/v1":
        raise RuntimeError("unexpected EXP-0009 profile schema")
    if profile.get("artifact") != "EXP-0009" or profile.get("profile_id") != "exp-0009-identity-evidence-hardening/v1":
        raise RuntimeError("unexpected EXP-0009 profile identity")
    if profile.get("case_manifest") != "experiments/ebook/exp-0009/case-manifest.json":
        raise RuntimeError("EXP-0009 manifest locator differs")
    if profile.get("case_totals") != {"completed": 15, "not_assessed": 3, "total": 18}:
        raise RuntimeError("EXP-0009 profile case totals differ")
    if tuple(profile.get("stages", ())) != STAGES or set(profile.get("decisions", ())) != DECISIONS:
        raise RuntimeError("EXP-0009 identity levels differ")
    if profile.get("repetitions") != 2:
        raise RuntimeError("EXP-0009 repetition count differs")
    implementation = profile.get("implementation", {})
    if implementation != {
        "external_dependencies": [],
        "network": "not_used",
        "product_code_changes": False,
        "runtime": "Python 3.12 standard library",
        "synthetic_only": True,
    }:
        raise RuntimeError("EXP-0009 implementation boundary differs")
    expected_limits = IdentityLimits().to_dict()
    if profile.get("limits") != expected_limits:
        raise RuntimeError("EXP-0009 limits differ from the product contract")
    labels = profile.get("measurement", {}).get("labels", {})
    if labels != {
        "byte": ["candidate_same"],
        "edition": ["candidate_same"],
        "package": ["candidate_same"],
        "representation": ["candidate_same"],
        "work": ["candidate_same", "candidate_related"],
    }:
        raise RuntimeError("EXP-0009 measured labels differ")
    if profile["measurement"].get("critical_same_stages") != list(STAGES):
        raise RuntimeError("EXP-0009 critical stage list differs")
    if profile["measurement"].get("metrics") != [
        "precision",
        "recall",
        "selective_accuracy",
        "coverage",
        "abstention_rate",
        "correct_abstention",
        "unexpected_abstention",
    ]:
        raise RuntimeError("EXP-0009 metric set differs")
    return profile


def load_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    return validate_profile(load_json(PROFILE_PATH)), validate_manifest(load_json(MANIFEST_PATH))


def _xml_items(tag: str, values: list[str]) -> str:
    return "".join(f"<dc:{tag}>{html.escape(value)}</dc:{tag}>" for value in values)


def _opf(spec: dict[str, Any]) -> bytes:
    metadata = "".join(
        (
            _xml_items("title", spec["titles"]),
            _xml_items("creator", spec["creators"]),
            _xml_items("language", spec["languages"]),
            _xml_items("identifier", spec["identifiers"]),
            "".join(
                f'<meta property="belongs-to-collection">{html.escape(value)}</meta>'
                for value in spec["work_references"]
            ),
        )
    )
    if spec["opf_style"] == "compact":
        value = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">'
            f"<metadata>{metadata}</metadata>"
            '<manifest><item id="chapter" href="chapter.xhtml" '
            'media-type="application/xhtml+xml"/></manifest>'
            '<spine><itemref idref="chapter"/></spine></package>'
        )
    else:
        value = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">\n'
            f"  <metadata>\n    {metadata}\n  </metadata>\n"
            '  <manifest>\n    <item id="chapter" href="chapter.xhtml" '
            'media-type="application/xhtml+xml"/>\n  </manifest>\n'
            '  <spine>\n    <itemref idref="chapter"/>\n  </spine>\n</package>\n'
        )
    return value.encode("utf-8")


def _zip_info(name: str, compression: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = compression
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def generate_epub(spec: dict[str, Any]) -> bytes:
    if spec["fault"] == "corrupt_zip":
        return b"PK\x03\x04synthetic-corrupt-archive"
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
        '<rootfiles><rootfile full-path="OPS/package.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles></container>'
    ).encode("utf-8")
    chapter = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Synthetic</title></head>'
        f"<body><p>{html.escape(spec['body'])}</p></body></html>"
    ).encode("utf-8")
    entries: list[tuple[str, bytes]] = [
        ("mimetype", b"application/epub+zip"),
        ("META-INF/container.xml", container),
        ("OPS/package.opf", _opf(spec)),
        ("OPS/chapter.xhtml", chapter),
    ]
    if spec["fault"] == "unsafe_path":
        entries.append(("../synthetic-escape.txt", b"blocked"))
    elif spec["fault"] == "duplicate_logical_entry":
        entries.append(("ops/CHAPTER.XHTML", chapter))
    reverse = spec["zip_style"] == "deflated_reverse"
    compression = zipfile.ZIP_DEFLATED if reverse else zipfile.ZIP_STORED
    ordered = list(reversed(entries)) if reverse else entries
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, mode="w") as archive:
        archive.comment = b"exp-0009-repacked" if reverse else b""
        for name, value in ordered:
            item_compression = zipfile.ZIP_STORED if name == "mimetype" else compression
            archive.writestr(_zip_info(name, item_compression), value)
    return payload.getvalue()


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


def evaluate_case(
    manifest: dict[str, Any], case: dict[str, Any], case_root: Path, limits: IdentityLimits
) -> dict[str, Any]:
    paths = materialize_pair(manifest, case, case_root)
    before = [sha256_file(path) for path in paths]
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
                "stage": stage,
            }
        )
    return {
        "assessment": report["assessment"],
        "case_key": case["case_key"],
        "duration_ms": duration_ms,
        "expected_assessment": case["expected_assessment"],
        "input_sha256_after": after,
        "input_sha256_before": before,
        "inputs_unchanged": before == after,
        "oracle_evaluation": evaluations,
        "report": report,
    }


def semantic_case(case: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in case.items() if key != "duration_ms"}


def semantic_repetition(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {"cases": [semantic_case(case) for case in cases]}


def _fraction(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "denominator": denominator,
        "numerator": numerator,
        "value": round(numerator / denominator, 6) if denominator else "not_applicable",
    }


def calculate_metrics(cases: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    completed = [case for case in cases if case["assessment"] == "completed"]
    for stage in STAGES:
        rows = [
            next(item for item in case["oracle_evaluation"] if item["stage"] == stage)
            for case in completed
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
        correct_selected = sum(row["matches_oracle"] for row in selected)
        abstentions = [row for row in rows if row["decision"] == "abstain"]
        result[stage] = {
            "abstention_rate": _fraction(len(abstentions), len(rows)),
            "confusion": confusion,
            "correct_abstention": sum(row["matches_oracle"] for row in abstentions),
            "coverage": _fraction(len(selected), len(rows)),
            "labels": label_metrics,
            "oracle_match_count": sum(row["matches_oracle"] for row in rows),
            "row_count": len(rows),
            "selective_accuracy": _fraction(correct_selected, len(selected)),
            "unexpected_abstention": sum(not row["matches_oracle"] for row in abstentions),
        }
    return result


def calculate_findings(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for case in cases:
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
            if row["decision"] == "candidate_same":
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


def explanation_complete(case: dict[str, Any]) -> bool:
    report = case["report"]
    if report["assessment"] == "not_assessed":
        return bool(report.get("reason_codes")) and not report.get("stages")
    if [item.get("stage") for item in report.get("stages", [])] != list(STAGES):
        return False
    for stage in report["stages"]:
        if not isinstance(stage.get("rule_id"), str) or not stage["rule_id"]:
            return False
        channels = ("positive_evidence", "negative_evidence", "missing_evidence")
        if not all(isinstance(stage.get(channel), list) for channel in channels):
            return False
        if not any(stage[channel] for channel in channels):
            return False
    return True


def effects_zero(case: dict[str, Any]) -> bool:
    return case["report"].get("effects") == {
        "domain_system_writes": False,
        "filesystem_writes": False,
        "network_access": False,
        "original_modified": False,
    }


def result_payload_digest(result: dict[str, Any]) -> str:
    return canonical_digest({key: value for key, value in result.items() if key != "result_content_sha256"})


def result_path_free(result: dict[str, Any]) -> bool:
    redacted = dict(result)
    redacted.pop("result_content_sha256", None)
    return PRIVATE_PATH_PATTERN.search(canonical_json(redacted)) is None


def acceptance_from_result(result: dict[str, Any], profile: dict[str, Any]) -> dict[str, bool]:
    repetitions = result.get("repetitions", [])
    first_cases = repetitions[0].get("cases", []) if len(repetitions) == 2 else []
    second_cases = repetitions[1].get("cases", []) if len(repetitions) == 2 else []
    findings = calculate_findings(first_cases) if first_cases else []
    critical = [item for item in findings if item["kind"] == "critical_false_same"]
    expected_assessments = {"completed": 15, "not_assessed": 3}
    actual_assessments = {
        name: sum(case.get("assessment") == name for case in first_cases)
        for name in expected_assessments
    }
    self_bound = result.get("result_content_sha256") == result_payload_digest(result)
    return {
        "case_matrix_complete": len(first_cases) == len(second_cases) == 18
        and {case.get("case_key") for case in first_cases} == EXPECTED_CASE_KEYS
        and actual_assessments == expected_assessments,
        "critical_findings_visible": result.get("critical_false_same_count") == len(critical)
        and all(item in result.get("quality_findings", []) for item in critical),
        "explanation_channels_complete": bool(first_cases)
        and all(explanation_complete(case) for case in first_cases),
        "inputs_unchanged_and_cleanup_complete": bool(first_cases)
        and all(case.get("inputs_unchanged") is True for repetition in repetitions for case in repetition.get("cases", []))
        and result.get("cleanup_complete") is True,
        "metrics_recomputable": bool(first_cases)
        and result.get("metrics") == calculate_metrics(first_cases, profile),
        "oracle_evaluated": bool(first_cases)
        and all(
            len(case.get("oracle_evaluation", [])) == 5
            and all(isinstance(item.get("matches_oracle"), bool) for item in case["oracle_evaluation"])
            for case in first_cases
        ),
        "ordered_stages": bool(first_cases)
        and all(
            case["assessment"] == "not_assessed"
            or [item.get("stage") for item in case["report"].get("stages", [])] == list(STAGES)
            for case in first_cases
        ),
        "path_free_result": result_path_free(result),
        "preimage_bound": result.get("preimage", {}).get("sha256_by_locator") == current_preimage(),
        "result_contract_self_bound": self_bound,
        "semantic_repetitions_identical": len(repetitions) == 2
        and repetitions[0].get("semantic_sha256") == repetitions[1].get("semantic_sha256")
        and semantic_repetition(first_cases) == semantic_repetition(second_cases),
        "zero_external_or_domain_effects": bool(first_cases)
        and all(effects_zero(case) for repetition in repetitions for case in repetition.get("cases", [])),
    }


def quality_verdict(findings: list[dict[str, Any]]) -> str:
    if any(item["kind"] == "critical_false_same" for item in findings):
        return "not_qualified"
    return "qualified_with_findings" if findings else "qualified"


def current_preimage() -> dict[str, str]:
    result: dict[str, str] = {}
    for locator in PREIMAGE_FILES:
        path = ROOT / locator
        if not path.is_file():
            raise RuntimeError(f"EXP-0009 preimage file missing: {locator}")
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
        raise RuntimeError("EXP-0009 empirical run requires a clean preimage commit")
    head = git_output("rev-parse", "HEAD")
    origin_main = git_output("rev-parse", "origin/main")
    merge_base = git_output("merge-base", "HEAD", "origin/main")
    if merge_base != origin_main:
        raise RuntimeError("EXP-0009 preimage does not descend from exact origin/main")
    registry = json.loads(git_output("show", "origin/main:.ai/artifact_registry.json"))["artifacts"]
    if registry["GATE-0008"]["status"] != "done" or registry["EXP-0009"]["status"] != "accepted":
        raise RuntimeError("EXP-0009 plan is not canonical on origin/main")
    changed = set(filter(None, git_output("diff", "--name-only", "origin/main...HEAD").splitlines()))
    allowed = {
        "experiments/ebook/exp-0009/README.md",
        "experiments/ebook/exp-0009/case-manifest.json",
        "experiments/ebook/exp-0009/execution-profile.json",
        "tests/experiments/test_exp_0009.py",
        "tools/experiments/run_exp_0009.py",
    }
    if not changed or not changed.issubset(allowed):
        raise RuntimeError("EXP-0009 preimage change set is broader than the experiment")
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
    )
    if product_changes:
        raise RuntimeError("EXP-0009 preimage changes product code or qualification")
    return {
        "allowed_change_set": True,
        "exp_0009_accepted_on_origin_main": True,
        "gate_0008_done_on_origin_main": True,
        "merge_base": merge_base,
        "origin_main": origin_main,
        "preimage_commit": head,
        "product_code_unchanged": True,
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
        raise RuntimeError("EXP-0009 temp root escapes C:\\rep\\tmp authority") from exc
    if not relative.parts or any(value in str(candidate) for value in ("\x00", "\r", "\n")):
        raise RuntimeError("EXP-0009 temp root is not a strict task subpath")
    authority.mkdir(parents=True, exist_ok=True)
    current = authority
    for part in relative.parts:
        current /= part
        if current.exists() and _is_reparse(current):
            raise RuntimeError("EXP-0009 temp root contains a link or reparse point")
    candidate.mkdir(parents=True, exist_ok=True)
    if _is_reparse(candidate) or candidate.resolve(strict=True) != candidate:
        raise RuntimeError("EXP-0009 temp root is unsafe")
    return candidate


def cleanup_run_root(run_root: Path, temp_base: Path) -> bool:
    if run_root.parent != temp_base or not run_root.name.startswith("run-") or _is_reparse(run_root):
        raise RuntimeError("EXP-0009 cleanup target is outside the owned run root")
    shutil.rmtree(run_root)
    return not run_root.exists()


def execute(temp_root: Path) -> dict[str, Any]:
    profile, manifest = load_contract()
    authority = authority_evidence()
    preimage = current_preimage()
    temp_base = prepare_temp_base(temp_root)
    run_root = temp_base / f"run-{uuid.uuid4().hex}"
    run_root.mkdir(mode=0o700)
    repetitions: list[dict[str, Any]] = []
    cleanup_complete = False
    try:
        limits = IdentityLimits(**profile["limits"])
        for repetition_index in range(1, profile["repetitions"] + 1):
            repetition_root = run_root / f"repetition-{repetition_index}"
            repetition_root.mkdir(mode=0o700)
            cases = []
            for case in manifest["cases"]:
                cases.append(
                    evaluate_case(
                        manifest,
                        case,
                        repetition_root / case["case_key"],
                        limits,
                    )
                )
            semantic = semantic_repetition(cases)
            repetitions.append(
                {
                    "cases": cases,
                    "duration_ms": round(sum(case["duration_ms"] for case in cases), 3),
                    "repetition": repetition_index,
                    "semantic_sha256": canonical_digest(semantic),
                }
            )
    finally:
        cleanup_complete = cleanup_run_root(run_root, temp_base)

    first_cases = repetitions[0]["cases"]
    metrics = calculate_metrics(first_cases, profile)
    findings = calculate_findings(first_cases)
    result: dict[str, Any] = {
        "acceptance": {},
        "artifact": "EXP-0009",
        "cleanup_complete": cleanup_complete,
        "critical_false_same_count": sum(item["kind"] == "critical_false_same" for item in findings),
        "executed_on": date.today().isoformat(),
        "manifest": {"locator": profile["case_manifest"], "sha256": sha256_file(MANIFEST_PATH)},
        "metrics": metrics,
        "preimage": {"authority": authority, "sha256_by_locator": preimage},
        "profile": {"id": profile["profile_id"], "sha256": sha256_file(PROFILE_PATH)},
        "quality_findings": findings,
        "quality_verdict": quality_verdict(findings),
        "repetitions": repetitions,
        "schema": "sammlungslotse/exp-0009-result/v1",
        "status": "pending",
    }
    result["acceptance"] = {
        name: True for name in sorted(ACCEPTANCE_NAMES)
    }
    result["result_content_sha256"] = result_payload_digest(result)
    result["acceptance"] = acceptance_from_result(result, profile)
    result["status"] = "pass" if all(result["acceptance"].values()) else "fail"
    result["result_content_sha256"] = result_payload_digest(result)
    result["acceptance"] = acceptance_from_result(result, profile)
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    profile, manifest = load_contract()
    result = load_json(path)
    problems: list[str] = []
    if result.get("schema") != "sammlungslotse/exp-0009-result/v1" or result.get("artifact") != "EXP-0009":
        problems.append("EXP-0009 result identity differs")
    if result.get("profile") != {"id": profile["profile_id"], "sha256": sha256_file(PROFILE_PATH)}:
        problems.append("EXP-0009 profile binding differs")
    if result.get("manifest") != {"locator": profile["case_manifest"], "sha256": sha256_file(MANIFEST_PATH)}:
        problems.append("EXP-0009 manifest binding differs")
    acceptance = acceptance_from_result(result, profile)
    if set(result.get("acceptance", {})) != ACCEPTANCE_NAMES or result.get("acceptance") != acceptance:
        problems.append("EXP-0009 acceptance differs")
    if not all(acceptance.values()) or result.get("status") != "pass":
        problems.append("EXP-0009 method is not fully accepted")
    repetitions = result.get("repetitions", [])
    first_cases = repetitions[0].get("cases", []) if len(repetitions) == 2 else []
    expected_findings = calculate_findings(first_cases) if first_cases else []
    if result.get("quality_findings") != expected_findings:
        problems.append("EXP-0009 findings differ")
    if result.get("quality_verdict") != quality_verdict(expected_findings):
        problems.append("EXP-0009 quality verdict differs")
    if result.get("critical_false_same_count") != sum(
        item["kind"] == "critical_false_same" for item in expected_findings
    ):
        problems.append("EXP-0009 critical finding count differs")
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
                f"EXP-0009 profile valid: cases={len(manifest['cases'])} "
                f"repetitions={profile['repetitions']}"
            )
            return 0
        if args.validate_result:
            result = validate_result(args.result)
            print(
                f"EXP-0009 result valid: {sum(result['acceptance'].values())}/"
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
            f"EXP-0009 method: {sum(result['acceptance'].values())}/"
            f"{len(ACCEPTANCE_NAMES)} quality={result['quality_verdict']}"
        )
        return 0 if result["status"] == "pass" else 1
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
