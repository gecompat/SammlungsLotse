#!/usr/bin/env python3
"""Run or validate the bounded synthetic EXP-0018 inbox explanation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools" / "run_ebook_intake.py"
CASES = ROOT / "experiments" / "ebook" / "exp-0018" / "cases.json"
RESULT = ROOT / "experiments" / "ebook" / "exp-0018" / "result.json"
STABLE = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases" / "ingress-stable-minimal" / "stable.epub"
REMOTE = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases" / "epub-active-or-remote" / "active-remote.epub"
SCHEMA = "sammlungslotse/ebook-inbox-aggregate-experiment-result/v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases() -> list[dict[str, str]]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    if payload.get("schema") != "sammlungslotse/ebook-inbox-aggregate-experiment-cases/v1":
        raise ValueError("unexpected EXP-0018 case schema")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise ValueError("EXP-0018 requires exactly six cases")
    return cases


def classify(report: dict[str, Any]) -> str:
    if report.get("status") == "unavailable":
        return "inventory_unavailable"
    if report.get("status") == "limit_exceeded" or not report.get("inventory_complete", False):
        return "inventory_incomplete"
    if report.get("candidate_counts", {}).get("epub") == 0:
        return "no_supported_epub"
    actions = [item.get("result", {}).get("next_action") for item in report.get("items", [])]
    if "review" in actions:
        return "manual_review_required"
    if actions and all(action == "continue_deep_read_only" for action in actions):
        return "review_deep_read_only"
    return "manual_review_required"


def materialize(root: Path, key: str) -> Path:
    inbox = root / key
    if key == "unavailable":
        return inbox
    inbox.mkdir()
    if key in {"continue_only", "mixed"}:
        shutil.copyfile(STABLE, inbox / "stable.epub")
    if key in {"review_only", "mixed"}:
        shutil.copyfile(REMOTE, inbox / "remote.epub")
    if key in {"unsupported_only", "mixed"}:
        (inbox / "document.pdf").write_bytes(b"%PDF-1.7\nsynthetic\n")
    if key == "candidate_limit":
        for index in range(33):
            (inbox / f"candidate-{index:02d}.epub").write_bytes(b"synthetic")
    return inbox


def run_case(root: Path, key: str) -> dict[str, Any]:
    directory = materialize(root, key)
    outputs: list[str] = []
    codes: list[int] = []
    for _ in range(2):
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--json", "--input-directory", str(directory)],
            cwd=ROOT, capture_output=True, encoding="utf-8", check=False,
        )
        if completed.stderr:
            raise RuntimeError(f"unexpected stderr for {key}")
        outputs.append(completed.stdout)
        codes.append(completed.returncode)
    if outputs[0] != outputs[1] or codes[0] != codes[1]:
        raise RuntimeError(f"non-deterministic directory report for {key}")
    for private in (str(directory), "stable.epub", "remote.epub", "document.pdf", "candidate-"):
        if private in outputs[0]:
            raise RuntimeError(f"path or local label leaked for {key}")
    report = json.loads(outputs[0])
    return {"key": key, "exit_code": codes[0], "priority_class": classify(report), "report_sha256": hashlib.sha256(outputs[0].encode("utf-8")).hexdigest()}


def execute(temp_root: Path) -> dict[str, Any]:
    if temp_root.exists():
        raise ValueError("temp root must not exist")
    temp_root.parent.mkdir(parents=True, exist_ok=True)
    before = {"stable": sha256(STABLE), "remote": sha256(REMOTE)}
    try:
        temp_root.mkdir()
        cases = load_cases()
        outcomes = [run_case(temp_root, entry["key"]) for entry in cases]
        for expected, outcome in zip(cases, outcomes, strict=True):
            if expected["expected_class"] != outcome["priority_class"]:
                raise RuntimeError(f"unexpected priority class for {outcome['key']}")
        if before != {"stable": sha256(STABLE), "remote": sha256(REMOTE)}:
            raise RuntimeError("fixture source changed")
        return {"schema": SCHEMA, "case_count": len(outcomes), "cases": outcomes, "fixture_hashes": before, "network": "not_used", "product_code_changed": False}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        if temp_root.exists():
            raise RuntimeError("temporary experiment root was not removed")


def validate_result(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = load_cases()
    if payload.get("schema") != SCHEMA or payload.get("case_count") != 6:
        raise ValueError("invalid EXP-0018 result contract")
    actual = payload.get("cases")
    if not isinstance(actual, list) or len(actual) != 6:
        raise ValueError("invalid EXP-0018 result cases")
    for expected_case, actual_case in zip(expected, actual, strict=True):
        if actual_case.get("key") != expected_case["key"] or actual_case.get("priority_class") != expected_case["expected_class"]:
            raise ValueError("EXP-0018 result does not match bound case matrix")
    if payload.get("network") != "not_used" or payload.get("product_code_changed") is not False:
        raise ValueError("EXP-0018 forbidden effect claimed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temp-root", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    if args.validate_result:
        validate_result(RESULT)
        print("[OK] EXP-0018 result contract")
        return 0
    root = args.temp_root or Path(tempfile.mkdtemp(prefix="sammlungslotse-exp-0018-"))
    if args.temp_root is None:
        shutil.rmtree(root)
    result = execute(root)
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.result:
        args.result.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
