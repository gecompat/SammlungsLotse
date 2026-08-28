#!/usr/bin/env python3
"""Record or validate the synthetic WI-0009 product qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases"
CLI = ROOT / "tools" / "run_ebook_identity.py"
RESULT = ROOT / "runtime" / "ebook-identity" / "qualification.json"
SCHEMA = "sammlungslotse/ebook-identity-qualification/v1"
PREIMAGE = (
    "src/sammlungslotse/ebook_identity/__init__.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/cli.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    "tools/qualify_ebook_identity.py",
    "tools/run_ebook_identity.py",
)
PAIRS = {
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
EXPECTED = {
    "byte_equal": ("exact_byte_match", "candidate_same", "candidate_same"),
    "repackaged": ("representation_candidate", "candidate_same", "candidate_same"),
    "sample_full": ("abstain", "different", "abstain"),
    "title_collision": ("abstain", "abstain", "different"),
    "translation": ("related_work_candidate", "different", "candidate_related"),
}
ACCEPTANCE_NAMES = frozenset(
    {
        "actual_cli_completed",
        "byte_equality_detected",
        "deterministic_json",
        "explicit_two_input_boundary",
        "fixture_inputs_unchanged",
        "german_view",
        "identity_levels_separate",
        "network_effect_false",
        "no_false_same_candidate",
        "original_effect_false",
        "path_free_output",
        "positive_negative_missing_separate",
        "repackaging_detected",
        "sample_full_separated",
        "translation_related_not_same_edition",
        "write_effect_false",
    }
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def preimage() -> dict[str, str]:
    return {name: sha256_file(ROOT / name) for name in PREIMAGE}


def fixture_hashes() -> dict[str, str]:
    names = sorted({name for pair in PAIRS.values() for name in pair})
    return {name: sha256_file(CASES / name) for name in names}


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=30,
    )


def stage(value: dict[str, Any], name: str) -> dict[str, Any]:
    return next(item for item in value["stages"] if item["stage"] == name)


def qualify() -> dict[str, object]:
    before = fixture_hashes()
    results: dict[str, Any] = {}
    serialized = ""
    deterministic = True
    completed = True
    for name, pair in sorted(PAIRS.items()):
        paths = tuple(CASES / relative for relative in pair)
        arguments = ("--json", str(paths[0]), str(paths[1]))
        first = run(*arguments)
        second = run(*arguments)
        serialized += first.stdout + first.stderr + second.stdout + second.stderr
        deterministic = deterministic and first.returncode == second.returncode == 0
        deterministic = deterministic and first.stdout == second.stdout
        completed = completed and first.returncode == 0 and not first.stderr
        results[name] = json.loads(first.stdout) if first.returncode == 0 else {}

    human_pair = tuple(CASES / item for item in PAIRS["byte_equal"])
    human = run(str(human_pair[0]), str(human_pair[1]))
    serialized += human.stdout + human.stderr
    forbidden = [str(ROOT)]
    forbidden.extend(str(CASES / item) for pair in PAIRS.values() for item in pair)
    forbidden.extend(Path(item).name for pair in PAIRS.values() for item in pair)

    actual = {
        name: (
            value.get("overall"),
            stage(value, "edition").get("decision") if value else None,
            stage(value, "work").get("decision") if value else None,
        )
        for name, value in results.items()
    }
    effects = [value.get("effects", {}) for value in results.values()]
    acceptance = {
        "actual_cli_completed": completed and len(results) == 5,
        "byte_equality_detected": actual.get("byte_equal") == EXPECTED["byte_equal"],
        "deterministic_json": deterministic,
        "explicit_two_input_boundary": all(len(value.get("inputs", [])) == 2 for value in results.values()),
        "fixture_inputs_unchanged": before == fixture_hashes(),
        "german_view": human.returncode == 0 and "EPUB-Identitätskandidatenbericht" in human.stdout,
        "identity_levels_separate": all(
            [item.get("stage") for item in value.get("stages", [])]
            == ["byte", "package", "representation", "edition", "work"]
            for value in results.values()
        ),
        "network_effect_false": all(item.get("network_access") is False for item in effects),
        "no_false_same_candidate": actual.get("title_collision") == EXPECTED["title_collision"],
        "original_effect_false": all(item.get("original_modified") is False for item in effects),
        "path_free_output": not any(value in serialized for value in forbidden),
        "positive_negative_missing_separate": all(
            all(
                {"positive_evidence", "negative_evidence", "missing_evidence"} <= set(item)
                for item in value.get("stages", [])
            )
            for value in results.values()
        ),
        "repackaging_detected": actual.get("repackaged") == EXPECTED["repackaged"],
        "sample_full_separated": actual.get("sample_full") == EXPECTED["sample_full"],
        "translation_related_not_same_edition": actual.get("translation") == EXPECTED["translation"],
        "write_effect_false": all(
            item.get("filesystem_writes") is False and item.get("domain_system_writes") is False
            for item in effects
        ),
    }
    return {
        "acceptance": dict(sorted(acceptance.items())),
        "case_results": {
            name: {"edition": values[1], "overall": values[0], "work": values[2]}
            for name, values in sorted(actual.items())
        },
        "fixture_hashes": before,
        "preimage": preimage(),
        "profile": "wi-0009-two-explicit-epub-readonly/v1",
        "repetitions_per_case": 2,
        "schema": SCHEMA,
        "status": "pass" if all(acceptance.values()) else "fail",
    }


def validate(value: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if value.get("schema") != SCHEMA:
        problems.append("schema differs")
    if value.get("profile") != "wi-0009-two-explicit-epub-readonly/v1":
        problems.append("profile differs")
    if value.get("status") != "pass":
        problems.append("qualification status is not pass")
    acceptance = value.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != ACCEPTANCE_NAMES:
        problems.append("acceptance set differs")
    elif not all(item is True for item in acceptance.values()):
        problems.append("acceptance is incomplete")
    if value.get("repetitions_per_case") != 2:
        problems.append("repetition count differs")
    if value.get("preimage") != preimage():
        problems.append("product preimage differs")
    if value.get("fixture_hashes") != fixture_hashes():
        problems.append("fixture hashes differ")
    expected_cases = {
        name: {"edition": values[1], "overall": values[0], "work": values[2]}
        for name, values in sorted(EXPECTED.items())
    }
    if value.get("case_results") != expected_cases:
        problems.append("case results differ")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=RESULT)
    args = parser.parse_args(argv)
    if args.validate_result:
        try:
            value = json.loads(args.result.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print("WI-0009 qualification result cannot be read.", file=sys.stderr)
            return 1
        problems = validate(value)
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            return 1
        print(f"WI-0009 qualification valid: {len(ACCEPTANCE_NAMES)}/{len(ACCEPTANCE_NAMES)}")
        return 0

    value = qualify()
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"WI-0009 qualification: {sum(value['acceptance'].values())}/{len(ACCEPTANCE_NAMES)}")
    return 0 if value["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
