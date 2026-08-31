#!/usr/bin/env python3
"""Record or validate the synthetic WI-0012 identity guardrail qualification."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases"
CLI = ROOT / "tools" / "run_ebook_identity.py"
RESULT = ROOT / "runtime" / "ebook-identity" / "qualification.json"
EXP_MANIFEST = ROOT / "experiments" / "ebook" / "exp-0010" / "case-manifest.json"
EXP_RUNNER = ROOT / "tools" / "experiments" / "run_exp_0010.py"
SCHEMA = "sammlungslotse/ebook-identity-qualification/v2"
PROFILE = "wi-0012-ebook-identity-false-same-guardrail/v1"
PREIMAGE = (
    "experiments/ebook/exp-0010/case-manifest.json",
    "experiments/ebook/exp-0010/result.json",
    "src/sammlungslotse/ebook_identity/__init__.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/cli.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    "tools/experiments/run_exp_0010.py",
    "tools/experiments/validate_exp_0010_result.py",
    "tools/qualify_ebook_identity.py",
    "tools/run_ebook_identity.py",
)
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
TEST_EXPECTED = {
    "byte_equal": ("exact_byte_match", "candidate_same", "candidate_same"),
    "repackaged": ("representation_candidate", "candidate_same", "candidate_same"),
    "sample_full": ("abstain", "different", "abstain"),
    "title_collision": ("abstain", "abstain", "different"),
    "translation": ("related_work_candidate", "different", "candidate_related"),
}


def _expected_guardrail_case(
    *,
    overall: str,
    representation: str,
    edition: str,
    edition_rule: str,
    work: str,
    work_rule: str,
) -> dict[str, object]:
    return {
        "overall": overall,
        "stages": {
            "byte": {"decision": "different", "rule_id": "identity.byte.sha256"},
            "edition": {"decision": edition, "rule_id": edition_rule},
            "package": {
                "decision": "different",
                "rule_id": "identity.package.canonical_entries",
            },
            "representation": {
                "decision": representation,
                "rule_id": "identity.representation.spine_text",
            },
            "work": {"decision": work, "rule_id": work_rule},
        },
    }


GUARDRAIL_EXPECTED = {
    "different-collections-same-work": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.title_creator",
    ),
    "multiple-collections-partial-overlap": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.explicit_reference",
    ),
    "same-primary-minor-revision": _expected_guardrail_case(
        overall="representation_candidate",
        representation="candidate_same",
        edition="candidate_same",
        edition_rule="identity.edition.identifier_representation_metadata",
        work="candidate_same",
        work_rule="identity.work.same_edition",
    ),
    "same-primary-strong-content-conflict": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.title_creator",
    ),
    "series-overlap-distinct-works": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.explicit_reference",
    ),
    "set-overlap-distinct-members": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.explicit_reference",
    ),
    "shared-typed-additional-different-primary": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.title_creator",
    ),
    "shared-untyped-additional-different-primary": _expected_guardrail_case(
        overall="related_work_candidate",
        representation="different",
        edition="abstain",
        edition_rule="identity.edition.insufficient_evidence",
        work="candidate_related",
        work_rule="identity.work.title_creator",
    ),
}
RESIDUAL_ORACLE_MISMATCHES = [
    {
        "actual": "candidate_related",
        "allowed": ["different", "abstain"],
        "case_key": "same-primary-strong-content-conflict",
        "stage": "work",
    },
    {
        "actual": "candidate_related",
        "allowed": ["different", "abstain"],
        "case_key": "shared-untyped-additional-different-primary",
        "stage": "work",
    },
]
ACCEPTANCE_NAMES = frozenset(
    {
        "actual_cli_completed",
        "critical_false_same_eliminated",
        "deterministic_json",
        "explicit_two_input_boundary",
        "fixture_inputs_unchanged",
        "generated_inputs_unchanged",
        "german_view",
        "identity_levels_separate",
        "network_effect_false",
        "original_effect_false",
        "path_free_output",
        "positive_negative_missing_separate",
        "public_schema_unchanged",
        "residual_model_gaps_visible",
        "same_representation_candidate_preserved",
        "task_cleanup_complete",
        "test_0001_contract_preserved",
        "work_same_requires_qualified_edition",
        "write_effect_false",
    }
)


def _load_exp_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_exp_0010_qualification",
        EXP_RUNNER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("EXP-0010 runner cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXP = _load_exp_runner()
MANIFEST = EXP.validate_manifest(json.loads(EXP_MANIFEST.read_text(encoding="utf-8")))
QUALITY_CASES = {
    case["case_key"]: case
    for case in MANIFEST["cases"]
    if case["oracle_scope"] == "quality"
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def preimage() -> dict[str, str]:
    return {name: sha256_file(ROOT / name) for name in PREIMAGE}


def git_bytes(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "Git preimage query failed")
    return completed.stdout


def git_preimage(commit: str) -> dict[str, str]:
    return {
        name: hashlib.sha256(git_bytes("show", f"{commit}:{name}")).hexdigest()
        for name in PREIMAGE
    }


def committed_preimage() -> tuple[str, dict[str, str]]:
    commit = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    changed = git_bytes("diff", "--name-only", "HEAD", "--", *PREIMAGE).decode(
        "utf-8", errors="replace"
    )
    if changed.strip():
        raise RuntimeError("WI-0012 qualification preimage is not committed")
    current = preimage()
    if git_preimage(commit) != current:
        raise RuntimeError("WI-0012 committed preimage differs from working tree")
    return commit, current


def fixture_hashes() -> dict[str, str]:
    names = sorted({name for pair in TEST_PAIRS.values() for name in pair})
    return {name: sha256_file(CASES / name) for name in names}


def guardrail_input_hashes() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for case_key, case in sorted(QUALITY_CASES.items()):
        result[case_key] = {
            side: hashlib.sha256(
                EXP.generate_epub(EXP.merged_spec(MANIFEST, case, side))
            ).hexdigest()
            for side in ("left", "right")
        }
    return result


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


def guardrail_projection(value: dict[str, Any]) -> dict[str, object]:
    return {
        "overall": value.get("overall"),
        "stages": {
            name: {
                "decision": stage(value, name).get("decision"),
                "rule_id": stage(value, name).get("rule_id"),
            }
            for name in EXP.STAGES
        },
    }


def oracle_mismatches(results: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    mismatches: list[dict[str, object]] = []
    for case_key, case in sorted(QUALITY_CASES.items()):
        stages = results[case_key]["stages"]
        for name in EXP.STAGES:
            actual = stages[name]["decision"]
            allowed = case["oracle"][name]
            if actual not in allowed:
                mismatches.append(
                    {
                        "actual": actual,
                        "allowed": allowed,
                        "case_key": case_key,
                        "stage": name,
                    }
                )
    return mismatches


def critical_false_same_count(results: dict[str, dict[str, object]]) -> int:
    return sum(
        results[case_key]["stages"][name]["decision"] == "candidate_same"
        and "candidate_same" not in case["oracle"][name]
        for case_key, case in QUALITY_CASES.items()
        for name in ("edition", "work")
    )


def qualify(temp_root: Path) -> dict[str, object]:
    preimage_commit, current_preimage = committed_preimage()
    before_fixtures = fixture_hashes()
    expected_generated_hashes = guardrail_input_hashes()
    test_results: dict[str, Any] = {}
    guardrail_results: dict[str, Any] = {}
    serialized = ""
    deterministic = True
    completed = True
    generated_unchanged = True
    generated_paths: list[Path] = []

    for name, pair in sorted(TEST_PAIRS.items()):
        paths = tuple(CASES / relative for relative in pair)
        arguments = ("--json", str(paths[0]), str(paths[1]))
        first = run(*arguments)
        second = run(*arguments)
        serialized += first.stdout + first.stderr + second.stdout + second.stderr
        deterministic = deterministic and first.returncode == second.returncode == 0
        deterministic = deterministic and first.stdout == second.stdout
        completed = completed and first.returncode == 0 and not first.stderr
        test_results[name] = json.loads(first.stdout) if first.returncode == 0 else {}

    task_path: Path | None = None
    with tempfile.TemporaryDirectory(prefix="wi-0012-run-", dir=temp_root) as task:
        task_path = Path(task)
        for case_key, case in sorted(QUALITY_CASES.items()):
            paths = EXP.materialize_pair(MANIFEST, case, task_path / case_key)
            generated_paths.extend(paths)
            before = {
                side: sha256_file(path)
                for side, path in zip(("left", "right"), paths, strict=True)
            }
            generated_unchanged = generated_unchanged and before == expected_generated_hashes[case_key]
            arguments = ("--json", str(paths[0]), str(paths[1]))
            first = run(*arguments)
            second = run(*arguments)
            serialized += first.stdout + first.stderr + second.stdout + second.stderr
            deterministic = deterministic and first.returncode == second.returncode == 0
            deterministic = deterministic and first.stdout == second.stdout
            completed = completed and first.returncode == 0 and not first.stderr
            guardrail_results[case_key] = json.loads(first.stdout) if first.returncode == 0 else {}
            after = {
                side: sha256_file(path)
                for side, path in zip(("left", "right"), paths, strict=True)
            }
            generated_unchanged = generated_unchanged and before == after
    cleanup_complete = task_path is not None and not task_path.exists()

    human_pair = tuple(CASES / item for item in TEST_PAIRS["byte_equal"])
    human = run(str(human_pair[0]), str(human_pair[1]))
    serialized += human.stdout + human.stderr
    forbidden = [str(ROOT), str(temp_root)]
    forbidden.extend(str(CASES / item) for pair in TEST_PAIRS.values() for item in pair)
    forbidden.extend(Path(item).name for pair in TEST_PAIRS.values() for item in pair)
    forbidden.extend(str(path) for path in generated_paths)
    forbidden.extend(path.name for path in generated_paths)

    actual_test = {
        name: (
            value.get("overall"),
            stage(value, "edition").get("decision") if value else None,
            stage(value, "work").get("decision") if value else None,
        )
        for name, value in test_results.items()
    }
    projected_guardrail = {
        name: guardrail_projection(value)
        for name, value in sorted(guardrail_results.items())
        if value
    }
    residual = oracle_mismatches(projected_guardrail) if len(projected_guardrail) == 8 else []
    false_same = critical_false_same_count(projected_guardrail) if len(projected_guardrail) == 8 else -1
    all_reports = [*test_results.values(), *guardrail_results.values()]
    effects = [value.get("effects", {}) for value in all_reports]
    stages_separate = all(
        [item.get("stage") for item in value.get("stages", [])] == list(EXP.STAGES)
        for value in all_reports
    )
    work_same_qualified = all(
        stage(value, "work").get("decision") != "candidate_same"
        or (
            stage(value, "edition").get("decision") == "candidate_same"
            and stage(value, "representation").get("decision") == "candidate_same"
        )
        for value in all_reports
    )
    acceptance = {
        "actual_cli_completed": completed and len(test_results) == 5 and len(guardrail_results) == 8,
        "critical_false_same_eliminated": false_same == 0,
        "deterministic_json": deterministic,
        "explicit_two_input_boundary": all(len(value.get("inputs", [])) == 2 for value in all_reports),
        "fixture_inputs_unchanged": before_fixtures == fixture_hashes(),
        "generated_inputs_unchanged": generated_unchanged,
        "german_view": human.returncode == 0 and "EPUB-Identitätskandidatenbericht" in human.stdout,
        "identity_levels_separate": stages_separate,
        "network_effect_false": all(item.get("network_access") is False for item in effects),
        "original_effect_false": all(item.get("original_modified") is False for item in effects),
        "path_free_output": not any(value in serialized for value in forbidden),
        "positive_negative_missing_separate": all(
            all(
                {"positive_evidence", "negative_evidence", "missing_evidence"} <= set(item)
                for item in value.get("stages", [])
            )
            for value in all_reports
        ),
        "public_schema_unchanged": all(
            value.get("schema") == "sammlungslotse/ebook-identity-candidate-report/v1"
            for value in all_reports
        ),
        "residual_model_gaps_visible": residual == RESIDUAL_ORACLE_MISMATCHES,
        "same_representation_candidate_preserved": projected_guardrail.get(
            "same-primary-minor-revision"
        )
        == GUARDRAIL_EXPECTED["same-primary-minor-revision"],
        "task_cleanup_complete": cleanup_complete,
        "test_0001_contract_preserved": actual_test == TEST_EXPECTED,
        "work_same_requires_qualified_edition": work_same_qualified,
        "write_effect_false": all(
            item.get("filesystem_writes") is False and item.get("domain_system_writes") is False
            for item in effects
        ),
    }
    return {
        "acceptance": dict(sorted(acceptance.items())),
        "case_counts": {"exp_0010_quality": 8, "test_0001": 5, "total": 13},
        "critical_false_same_count": false_same,
        "guardrail_case_results": projected_guardrail,
        "guardrail_input_hashes": expected_generated_hashes,
        "preimage": current_preimage,
        "preimage_commit": preimage_commit,
        "profile": PROFILE,
        "repetitions_per_case": 2,
        "residual_oracle_mismatches": residual,
        "schema": SCHEMA,
        "scope_verdict": "guardrail_qualified_with_residual_related_mismatches",
        "status": "pass" if all(acceptance.values()) else "fail",
        "test_0001_case_results": {
            name: {"edition": values[1], "overall": values[0], "work": values[2]}
            for name, values in sorted(actual_test.items())
        },
        "test_0001_fixture_hashes": before_fixtures,
    }


def validate(value: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if value.get("schema") != SCHEMA:
        problems.append("schema differs")
    if value.get("profile") != PROFILE:
        problems.append("profile differs")
    if value.get("status") != "pass":
        problems.append("qualification status is not pass")
    if value.get("scope_verdict") != "guardrail_qualified_with_residual_related_mismatches":
        problems.append("scope verdict differs")
    acceptance = value.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != ACCEPTANCE_NAMES:
        problems.append("acceptance set differs")
    elif not all(item is True for item in acceptance.values()):
        problems.append("acceptance is incomplete")
    if value.get("case_counts") != {"exp_0010_quality": 8, "test_0001": 5, "total": 13}:
        problems.append("case counts differ")
    if value.get("repetitions_per_case") != 2:
        problems.append("repetition count differs")
    if value.get("preimage") != preimage():
        problems.append("product preimage differs")
    commit = value.get("preimage_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        problems.append("preimage commit differs")
    else:
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if ancestor.returncode != 0 or value.get("preimage") != git_preimage(commit):
            problems.append("committed preimage binding differs")
    if value.get("test_0001_fixture_hashes") != fixture_hashes():
        problems.append("TEST-0001 fixture hashes differ")
    if value.get("guardrail_input_hashes") != guardrail_input_hashes():
        problems.append("guardrail input hashes differ")
    expected_test_cases = {
        name: {"edition": values[1], "overall": values[0], "work": values[2]}
        for name, values in sorted(TEST_EXPECTED.items())
    }
    if value.get("test_0001_case_results") != expected_test_cases:
        problems.append("TEST-0001 case results differ")
    if value.get("guardrail_case_results") != GUARDRAIL_EXPECTED:
        problems.append("guardrail case results differ")
    if value.get("critical_false_same_count") != 0:
        problems.append("critical false-same count differs")
    if value.get("residual_oracle_mismatches") != RESIDUAL_ORACLE_MISMATCHES:
        problems.append("residual oracle mismatches differ")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--temp-root", type=Path)
    args = parser.parse_args(argv)
    if args.validate_result:
        try:
            value = json.loads(args.result.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print("WI-0012 qualification result cannot be read.", file=sys.stderr)
            return 1
        problems = validate(value)
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            return 1
        print(
            f"WI-0012 qualification valid: {len(ACCEPTANCE_NAMES)}/"
            f"{len(ACCEPTANCE_NAMES)} critical_false_same=0 residual_related=2"
        )
        return 0

    if args.temp_root is None:
        parser.error("--temp-root is required for the synthetic qualification")
    args.temp_root.mkdir(parents=True, exist_ok=True)
    if not args.temp_root.is_dir():
        parser.error("--temp-root must be a directory")
    value = qualify(args.temp_root)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"WI-0012 qualification: {sum(value['acceptance'].values())}/"
        f"{len(ACCEPTANCE_NAMES)} critical_false_same={value['critical_false_same_count']} "
        f"residual_related={len(value['residual_oracle_mismatches'])}"
    )
    return 0 if value["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
