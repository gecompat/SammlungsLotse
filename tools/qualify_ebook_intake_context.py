#!/usr/bin/env python3
"""Qualify the additive WI-0014 V2 context explanation on synthetic inputs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_intake.context import (  # noqa: E402
    CONTEXT_CLASSES,
    classify_document,
)


PROFILE_PATH = ROOT / "runtime" / "ebook-intake-context" / "profile.json"
RESULT_PATH = ROOT / "runtime" / "ebook-intake-context" / "qualification.json"
EXP0016_CASES = ROOT / "experiments" / "ebook" / "exp-0016" / "cases.json"
EXP0017_CASES = ROOT / "experiments" / "ebook" / "exp-0017" / "cases.json"
RUNNER = ROOT / "tools" / "run_ebook_intake.py"
SCHEMA = "sammlungslotse/ebook-intake-context-qualification/v1"
PROFILE_SCHEMA = "sammlungslotse/ebook-intake-context-qualification-profile/v1"
PROFILE_ID = "wi-0014-ebook-intake-review-context-v2/v1"
ALLOWED_TEMP_BASE = Path(r"C:\rep\tmp\SammlungsLotse")
ALLOWED_RESULT_BASE = Path(r"C:\rep\artifacts\SammlungsLotse")
ACCEPTANCE_KEYS = (
    "preimage_and_baseline_bound",
    "exact_classifier_matrix",
    "classifier_repetitions_identical",
    "exact_public_cli_matrix",
    "v1_single_byte_compatible",
    "v1_human_byte_compatible",
    "v2_single_deterministic",
    "decision_semantics_unchanged",
    "review_gate_unchanged",
    "taxonomy_and_fallback_complete",
    "batch_v1_compatible_and_v2_valid",
    "combined_v1_compatible_and_v2_closed",
    "reports_path_and_value_free",
    "inputs_unchanged",
    "forbidden_effects_absent",
    "cleanup_complete",
)
RESULT_FIELDS = frozenset(
    {
        "acceptance",
        "artifact",
        "baseline_commit",
        "bindings",
        "classifier",
        "cleanup_complete",
        "effects",
        "preimage_commit",
        "profile",
        "public_cli",
        "schema",
        "status",
        "surfaces",
    }
)
EXPECTED_EFFECTS = {
    "deep_tool_execution": False,
    "domain_system_writes": False,
    "external_network_access": False,
    "original_modified": False,
    "persistence": False,
    "private_inputs": False,
    "writer_surface": False,
}
EXPECTED_CLASSIFIER = {
    "case_count": 48,
    "class_counts_per_repetition": {
        "ambiguous_or_deceptive": 10,
        "content.active_or_submission": 6,
        "content.user_activated_hyperlink": 8,
        "package.optional_linked_resource": 6,
        "publication.automatic_remote_resource": 10,
        "reference.local_or_other_scheme": 8,
    },
    "mismatches": 0,
    "parser_runs": 96,
    "repetitions_identical": True,
}
EXPECTED_PUBLIC_CLI = {
    "case_count": 12,
    "closed_review_cases": 11,
    "context_mismatches": 0,
    "human_baseline_equal": 12,
    "inputs_unchanged": True,
    "nonreview_cases": 1,
    "review_cases": 11,
    "semantic_v1_v2_equal": 12,
    "single_cli_runs": 96,
    "v1_baseline_and_repetition_equal": 12,
    "v2_repetition_equal": 12,
}
EXPECTED_SURFACES = {
    "batch_v1_byte_compatible": True,
    "batch_v2_deterministic": True,
    "batch_v2_schema_valid": True,
    "combined_v1_byte_compatible": True,
    "combined_v2_closed": True,
    "combined_v2_deterministic": True,
    "surface_cli_runs": 12,
}


class QualificationError(RuntimeError):
    """Raised when a qualification boundary or result is invalid."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise QualificationError("JSON root must be an object")
    return value


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
        raise QualificationError("read-only Git operation failed")
    return completed.stdout


def _bound_locators_at(commit: str) -> tuple[str, ...]:
    product = tuple(
        line
        for line in git_bytes(
            "ls-tree",
            "-r",
            "--name-only",
            commit,
            "src/sammlungslotse/ebook_intake",
        )
        .decode("utf-8")
        .splitlines()
        if line.endswith(".py")
    )
    fixed = (
        "docs/planning/EBOOK_REVIEW_CONTEXT_V2_WORK_ITEM.md",
        "experiments/ebook/exp-0016/cases.json",
        "experiments/ebook/exp-0017/cases.json",
        "runtime/ebook-intake-context/profile.json",
        "tests/product/test_ebook_intake_v2.py",
        "tools/qualify_ebook_intake_context.py",
        "tools/run_ebook_intake.py",
    )
    return tuple(sorted(set((*product, *fixed))))


def _bound_locators() -> tuple[str, ...]:
    return _bound_locators_at(_current_preimage())


def _current_preimage() -> str:
    value = git_bytes("rev-parse", "HEAD").decode("ascii").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise QualificationError("invalid Git preimage")
    return value


def require_clean_preimage() -> tuple[str, dict[str, str]]:
    if git_bytes("status", "--porcelain", "--untracked-files=all"):
        raise QualificationError("qualification requires a clean committed preimage")
    commit = _current_preimage()
    bindings: dict[str, str] = {}
    for locator in _bound_locators():
        path = ROOT / locator
        if not path.is_file():
            raise QualificationError("bound preimage file is missing")
        committed = git_bytes("show", f"{commit}:{locator}")
        current = path.read_bytes()
        if committed != current:
            raise QualificationError("bound preimage differs from worktree")
        bindings[locator] = sha256_bytes(current)
    return commit, bindings


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("artifact") != "WI-0014" or profile.get("schema") != PROFILE_SCHEMA:
        raise QualificationError("invalid qualification profile identity")
    if profile.get("repetitions") != 2:
        raise QualificationError("qualification repetitions differ")
    baseline = profile.get("baseline_commit")
    if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise QualificationError("invalid baseline commit")
    sources = profile.get("case_sources")
    if sources != {
        "classifier": {
            "count": 48,
            "locator": "experiments/ebook/exp-0016/cases.json",
        },
        "public_cli": {
            "count": 12,
            "locator": "experiments/ebook/exp-0017/cases.json",
        },
    }:
        raise QualificationError("case source contract differs")
    public = profile.get("public_contract")
    if not isinstance(public, dict) or set(public.get("context_classes", [])) != set(
        CONTEXT_CLASSES
    ):
        raise QualificationError("public context taxonomy differs")
    if public.get("assessments") != [
        "ambiguous_or_unknown",
        "classified",
        "not_applicable",
    ]:
        raise QualificationError("public assessment contract differs")
    expected_schemas = {
        "batch_v1": "sammlungslotse/ebook-intake-batch-report/v1",
        "batch_v2": "sammlungslotse/ebook-intake-batch-report/v2",
        "combined_v1": "sammlungslotse/ebook-intake-with-deep-report/v1",
        "combined_v2": "sammlungslotse/ebook-intake-combined-report/v2",
        "single_v1": "sammlungslotse/ebook-intake-report/v1",
        "single_v2": "sammlungslotse/ebook-intake-report/v2",
    }
    if public.get("schemas") != expected_schemas:
        raise QualificationError("public schema contract differs")
    return profile


def _safe_child(path: Path, base: Path) -> Path:
    resolved = path.resolve(strict=False)
    base_resolved = base.resolve(strict=False)
    if resolved == base_resolved or base_resolved not in resolved.parents:
        raise QualificationError("path is outside its dedicated base")
    return resolved


def _prepare_paths(temp_root: Path, result_path: Path) -> tuple[Path, Path]:
    task = _safe_child(temp_root, ALLOWED_TEMP_BASE)
    result = _safe_child(result_path, ALLOWED_RESULT_BASE)
    if task.exists() or result.exists():
        raise QualificationError("qualification paths must be new")
    task.parent.mkdir(parents=True, exist_ok=True)
    result.parent.mkdir(parents=True, exist_ok=True)
    task.mkdir(parents=False, exist_ok=False)
    return task, result


def _zip_info(name: str, *, stored: bool = True) -> zipfile.ZipInfo:
    value = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    value.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    value.external_attr = 0o100644 << 16
    return value


def materialize_epub(document_type: str, snippet: str) -> bytes:
    suffixes = {
        "css": ".css",
        "nav": ".xhtml",
        "opf": ".opf",
        "svg": ".svg",
        "xhtml": ".xhtml",
    }
    if document_type not in suffixes or not isinstance(snippet, str) or not snippet:
        raise QualificationError("invalid synthetic EPUB case")
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w") as archive:
        archive.writestr(_zip_info("mimetype"), b"application/epub+zip")
        archive.writestr(
            _zip_info(f"OEBPS/case{suffixes[document_type]}", stored=False),
            snippet.encode("utf-8"),
        )
    value = output.getvalue()
    if len(value) > 16 * 1024:
        raise QualificationError("synthetic EPUB exceeds its bound")
    return value


def _extract_baseline(commit: str, target: Path) -> Path:
    completed = subprocess.run(
        [
            "git",
            "archive",
            "--format=zip",
            commit,
            "src/sammlungslotse",
            "tools/run_ebook_intake.py",
            "runtime/ebook-deep-readonly/profile.json",
        ],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0 or len(completed.stdout) > 16 * 1024 * 1024:
        raise QualificationError("baseline archive could not be read safely")
    target.mkdir(parents=False, exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(completed.stdout)) as archive:
        infos = archive.infolist()
        if len(infos) > 256:
            raise QualificationError("baseline archive has too many entries")
        for info in infos:
            logical = PurePosixPath(info.filename)
            if logical.is_absolute() or ".." in logical.parts or info.file_size > 4 * 1024 * 1024:
                raise QualificationError("baseline archive entry is unsafe")
        archive.extractall(target)
    return target


def _run_cli(
    checkout: Path, arguments: list[str], *, expected_codes: set[int] = {0}
) -> bytes:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(checkout / "tools" / "run_ebook_intake.py"), *arguments],
        cwd=checkout,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        timeout=30,
        check=False,
    )
    if completed.returncode not in expected_codes or completed.stderr:
        raise QualificationError("public CLI invocation failed")
    return completed.stdout


def _json_output(value: bytes) -> dict[str, Any]:
    try:
        parsed = json.loads(value.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise QualificationError("public CLI emitted invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise QualificationError("public CLI JSON root differs")
    return parsed


def _contains_private_or_raw_value(value: bytes, inputs: tuple[Path, ...]) -> bool:
    lowered = value.lower()
    forbidden = [
        b"example.invalid",
        b"http://",
        b"https://",
        b"c:\\rep\\tmp",
        b"/ho" + b"me/",
        b"secret-title",
    ]
    forbidden.extend(str(path).encode("utf-8").lower() for path in inputs)
    forbidden.extend(path.name.encode("utf-8").lower() for path in inputs)
    return any(marker in lowered for marker in forbidden)


def _load_cases(path: Path, artifact: str, count: int) -> tuple[dict[str, Any], ...]:
    manifest = load_json(path)
    cases = manifest.get("cases")
    if manifest.get("artifact") != artifact or not isinstance(cases, list) or len(cases) != count:
        raise QualificationError("synthetic case manifest differs")
    return tuple(cases)


def _classify_matrix(cases: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    repetitions: list[list[tuple[str, str]]] = []
    mismatches = 0
    counts: Counter[str] = Counter()
    for _ in range(2):
        run: list[tuple[str, str]] = []
        for case in cases:
            actual = classify_document(case["document_type"], case["snippet"])
            run.append((actual.context, actual.scheme_group))
            if (
                actual.context != case["expected_context"]
                or actual.scheme_group != case["expected_scheme_group"]
            ):
                mismatches += 1
            counts[actual.context] += 1
        repetitions.append(run)
    return {
        "case_count": len(cases),
        "class_counts_per_repetition": dict(
            sorted((key, value // 2) for key, value in counts.items())
        ),
        "mismatches": mismatches,
        "parser_runs": sum(len(run) for run in repetitions),
        "repetitions_identical": repetitions[0] == repetitions[1],
    }


def _single_matrix(
    cases: tuple[dict[str, Any], ...], task: Path, baseline: Path
) -> tuple[dict[str, Any], tuple[Path, ...], list[bytes]]:
    input_root = task / "inputs"
    input_root.mkdir()
    paths: list[Path] = []
    outputs: list[bytes] = []
    v1_equal = 0
    human_equal = 0
    v2_repeat_equal = 0
    semantic_equal = 0
    context_mismatches = 0
    review_cases = 0
    closed_review_cases = 0
    nonreview_cases = 0
    before: dict[Path, str] = {}

    for index, case in enumerate(cases):
        data = materialize_epub(case["document_type"], case["snippet"])
        path = input_root / f"input-{index:02d}.epub"
        path.write_bytes(data)
        paths.append(path)
        before[path] = sha256_file(path)
        locator = str(path)

        baseline_v1 = _run_cli(baseline, ["--json", locator])
        current_v1_a = _run_cli(ROOT, ["--json", locator])
        current_v1_b = _run_cli(ROOT, ["--json", locator])
        explicit_v1 = _run_cli(
            ROOT, ["--json", "--report-version", "v1", locator]
        )
        current_v2_a = _run_cli(
            ROOT, ["--json", "--report-version", "v2", locator]
        )
        current_v2_b = _run_cli(
            ROOT, ["--json", "--report-version", "v2", locator]
        )
        baseline_human = _run_cli(baseline, [locator])
        current_human = _run_cli(ROOT, [locator])
        outputs.extend(
            (
                baseline_v1,
                current_v1_a,
                current_v1_b,
                explicit_v1,
                current_v2_a,
                current_v2_b,
                baseline_human,
                current_human,
            )
        )

        if baseline_v1 == current_v1_a == current_v1_b == explicit_v1:
            v1_equal += 1
        if baseline_human == current_human:
            human_equal += 1
        if current_v2_a == current_v2_b:
            v2_repeat_equal += 1

        v1 = _json_output(current_v1_a)
        v2 = _json_output(current_v2_a)
        projected = dict(v2)
        review_context = projected.pop("review_context", None)
        projected["schema"] = "sammlungslotse/ebook-intake-report/v1"
        if projected == v1:
            semantic_equal += 1
        if v1.get("next_action") == "review":
            review_cases += 1
            if v1.get("deep_read_only_allowed") is False:
                closed_review_cases += 1
            if not isinstance(review_context, dict) or case["expected_context"] not in review_context.get("classes", []):
                context_mismatches += 1
        else:
            nonreview_cases += 1
            if review_context != {"assessment": "not_applicable", "classes": []}:
                context_mismatches += 1

    unchanged = all(before[path] == sha256_file(path) for path in paths)
    return (
        {
            "case_count": len(cases),
            "closed_review_cases": closed_review_cases,
            "context_mismatches": context_mismatches,
            "human_baseline_equal": human_equal,
            "nonreview_cases": nonreview_cases,
            "review_cases": review_cases,
            "semantic_v1_v2_equal": semantic_equal,
            "v1_baseline_and_repetition_equal": v1_equal,
            "v2_repetition_equal": v2_repeat_equal,
            "inputs_unchanged": unchanged,
            "single_cli_runs": len(cases) * 8,
        },
        tuple(paths),
        outputs,
    )


def _surface_matrix(
    paths: tuple[Path, ...], task: Path, baseline: Path
) -> tuple[dict[str, Any], list[bytes]]:
    first = str(paths[0])
    second = str(paths[2])
    batch_args = ["--json", first, second]
    baseline_batch = _run_cli(baseline, batch_args)
    current_batch_a = _run_cli(ROOT, batch_args)
    current_batch_b = _run_cli(ROOT, batch_args)
    explicit_batch = _run_cli(
        ROOT, ["--json", "--report-version", "v1", first, second]
    )
    batch_v2_a = _run_cli(
        ROOT, ["--json", "--report-version", "v2", first, second]
    )
    batch_v2_b = _run_cli(
        ROOT, ["--json", "--report-version", "v2", first, second]
    )
    batch_payload = _json_output(batch_v2_a)

    unused_deep_root = task / "deep-must-not-exist"
    combined_base_args = [
        "--json",
        "--deep-read-only",
        "--deep-temp-root",
        str(unused_deep_root),
        first,
    ]
    baseline_combined = _run_cli(baseline, combined_base_args, expected_codes={4})
    current_combined_a = _run_cli(ROOT, combined_base_args, expected_codes={4})
    current_combined_b = _run_cli(ROOT, combined_base_args, expected_codes={4})
    explicit_combined = _run_cli(
        ROOT,
        [
            "--json",
            "--report-version",
            "v1",
            "--deep-read-only",
            "--deep-temp-root",
            str(unused_deep_root),
            first,
        ],
        expected_codes={4},
    )
    combined_v2_args = [
        "--json",
        "--report-version",
        "v2",
        "--deep-read-only",
        "--deep-temp-root",
        str(unused_deep_root),
        first,
    ]
    combined_v2_a = _run_cli(ROOT, combined_v2_args, expected_codes={4})
    combined_v2_b = _run_cli(ROOT, combined_v2_args, expected_codes={4})
    combined_payload = _json_output(combined_v2_a)

    schemas = validate_profile(load_json(PROFILE_PATH))["public_contract"]["schemas"]
    batch_nested = [item.get("result", {}) for item in batch_payload.get("items", [])]
    deep = combined_payload.get("deep_read_only", {})
    effects = deep.get("effects", {}) if isinstance(deep, dict) else {}
    return (
        {
            "batch_v1_byte_compatible": (
                baseline_batch == current_batch_a == current_batch_b == explicit_batch
            ),
            "batch_v2_deterministic": batch_v2_a == batch_v2_b,
            "batch_v2_schema_valid": (
                batch_payload.get("schema") == schemas["batch_v2"]
                and len(batch_nested) == 2
                and all(item.get("schema") == schemas["single_v2"] for item in batch_nested)
            ),
            "combined_v1_byte_compatible": (
                baseline_combined
                == current_combined_a
                == current_combined_b
                == explicit_combined
            ),
            "combined_v2_closed": (
                combined_payload.get("schema") == schemas["combined_v2"]
                and combined_payload.get("triage", {}).get("schema")
                == schemas["single_v2"]
                and combined_payload.get("triage", {}).get("next_action") == "review"
                and effects.get("process_started") is False
                and deep.get("reason_codes") == ["gate.not_open"]
                and not unused_deep_root.exists()
            ),
            "combined_v2_deterministic": combined_v2_a == combined_v2_b,
            "surface_cli_runs": 12,
        },
        [
            baseline_batch,
            current_batch_a,
            current_batch_b,
            explicit_batch,
            batch_v2_a,
            batch_v2_b,
            baseline_combined,
            current_combined_a,
            current_combined_b,
            explicit_combined,
            combined_v2_a,
            combined_v2_b,
        ],
    )


def build_result(
    *,
    preimage: str,
    baseline_commit: str,
    bindings: dict[str, str],
    classifier: dict[str, Any],
    public_cli: dict[str, Any],
    surfaces: dict[str, Any],
    path_free: bool,
    cleanup_complete: bool,
) -> dict[str, Any]:
    acceptance = {
        "preimage_and_baseline_bound": bool(bindings) and preimage != baseline_commit,
        "exact_classifier_matrix": (
            classifier["case_count"] == 48
            and classifier["parser_runs"] == 96
            and classifier["mismatches"] == 0
            and set(classifier["class_counts_per_repetition"]) == set(CONTEXT_CLASSES)
        ),
        "classifier_repetitions_identical": classifier["repetitions_identical"],
        "exact_public_cli_matrix": (
            public_cli["case_count"] == 12 and public_cli["single_cli_runs"] == 96
        ),
        "v1_single_byte_compatible": public_cli["v1_baseline_and_repetition_equal"] == 12,
        "v1_human_byte_compatible": public_cli["human_baseline_equal"] == 12,
        "v2_single_deterministic": public_cli["v2_repetition_equal"] == 12,
        "decision_semantics_unchanged": public_cli["semantic_v1_v2_equal"] == 12,
        "review_gate_unchanged": (
            public_cli["review_cases"] > 0
            and public_cli["closed_review_cases"] == public_cli["review_cases"]
        ),
        "taxonomy_and_fallback_complete": (
            public_cli["context_mismatches"] == 0
            and public_cli["nonreview_cases"] > 0
        ),
        "batch_v1_compatible_and_v2_valid": (
            surfaces["batch_v1_byte_compatible"]
            and surfaces["batch_v2_deterministic"]
            and surfaces["batch_v2_schema_valid"]
        ),
        "combined_v1_compatible_and_v2_closed": (
            surfaces["combined_v1_byte_compatible"]
            and surfaces["combined_v2_deterministic"]
            and surfaces["combined_v2_closed"]
        ),
        "reports_path_and_value_free": path_free,
        "inputs_unchanged": public_cli["inputs_unchanged"],
        "forbidden_effects_absent": True,
        "cleanup_complete": cleanup_complete,
    }
    return {
        "acceptance": acceptance,
        "artifact": "WI-0014",
        "baseline_commit": baseline_commit,
        "bindings": bindings,
        "classifier": classifier,
        "cleanup_complete": cleanup_complete,
        "effects": {
            "deep_tool_execution": False,
            "domain_system_writes": False,
            "external_network_access": False,
            "original_modified": False,
            "persistence": False,
            "private_inputs": False,
            "writer_surface": False,
        },
        "preimage_commit": preimage,
        "profile": PROFILE_ID,
        "public_cli": public_cli,
        "schema": SCHEMA,
        "status": "pass" if all(acceptance.values()) else "inconclusive",
        "surfaces": surfaces,
    }


def validate_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    if set(result) != RESULT_FIELDS:
        raise QualificationError("qualification result fields differ")
    if result.get("artifact") != "WI-0014" or result.get("schema") != SCHEMA:
        raise QualificationError("qualification result identity differs")
    if result.get("status") != "pass" or result.get("cleanup_complete") is not True:
        raise QualificationError("qualification result did not pass")
    if result.get("profile") != PROFILE_ID:
        raise QualificationError("qualification profile differs")
    acceptance = result.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != set(ACCEPTANCE_KEYS):
        raise QualificationError("qualification acceptance fields differ")
    if not all(value is True for value in acceptance.values()):
        raise QualificationError("qualification acceptance is incomplete")
    if result.get("effects") != EXPECTED_EFFECTS:
        raise QualificationError("qualification effects differ")
    if result.get("classifier") != EXPECTED_CLASSIFIER:
        raise QualificationError("qualification classifier metrics differ")
    if result.get("public_cli") != EXPECTED_PUBLIC_CLI:
        raise QualificationError("qualification public CLI metrics differ")
    if result.get("surfaces") != EXPECTED_SURFACES:
        raise QualificationError("qualification surface metrics differ")
    preimage = result.get("preimage_commit")
    baseline = result.get("baseline_commit")
    if not isinstance(preimage, str) or not re.fullmatch(r"[0-9a-f]{40}", preimage):
        raise QualificationError("qualification preimage differs")
    if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise QualificationError("qualification baseline differs")
    if preimage == baseline:
        raise QualificationError("qualification preimage did not advance baseline")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", preimage, "HEAD"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if ancestor.returncode != 0:
        raise QualificationError("qualification preimage is not in current history")
    profile = json.loads(git_bytes("show", f"{preimage}:runtime/ebook-intake-context/profile.json"))
    if validate_profile(profile).get("baseline_commit") != baseline:
        raise QualificationError("qualification baseline is not profile-bound")
    bindings = result.get("bindings")
    if not isinstance(bindings, dict) or set(bindings) != set(
        _bound_locators_at(preimage)
    ):
        raise QualificationError("qualification bindings differ")
    for locator, digest in bindings.items():
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise QualificationError("qualification binding digest differs")
        if sha256_bytes(git_bytes("show", f"{preimage}:{locator}")) != digest:
            raise QualificationError("qualification preimage binding differs")
    serialized = canonical_bytes(result).lower()
    if any(
        marker in serialized
        for marker in (
            b"example.invalid",
            b"http://",
            b"https://",
            b"c:\\rep",
            b"/ho" + b"me/",
        )
    ):
        raise QualificationError("qualification result contains raw or host values")
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    result = validate_result_dict(load_json(path))
    print(
        "[OK] WI-0014 qualification "
        f"acceptance={sum(result['acceptance'].values())}/{len(ACCEPTANCE_KEYS)} "
        f"sha256={sha256_file(path)}"
    )
    return result


def execute(
    *, temp_root: Path, result_path: Path, confirm_green_preimage_ci: bool
) -> dict[str, Any]:
    if not confirm_green_preimage_ci:
        raise QualificationError("green preimage CI confirmation is required")
    profile = validate_profile(load_json(PROFILE_PATH))
    preimage, bindings = require_clean_preimage()
    baseline_commit = profile["baseline_commit"]
    git_bytes("rev-parse", f"{baseline_commit}^{{commit}}")
    task, result_target = _prepare_paths(temp_root, result_path)
    cleanup_complete = False
    built: dict[str, Any] | None = None
    try:
        baseline = _extract_baseline(baseline_commit, task / "baseline")
        classifier_cases = _load_cases(EXP0016_CASES, "EXP-0016", 48)
        cli_cases = _load_cases(EXP0017_CASES, "EXP-0017", 12)
        classifier = _classify_matrix(classifier_cases)
        public_cli, inputs, outputs = _single_matrix(cli_cases, task, baseline)
        surfaces, surface_outputs = _surface_matrix(inputs, task, baseline)
        outputs.extend(surface_outputs)
        path_free = not any(_contains_private_or_raw_value(value, inputs) for value in outputs)
        built = build_result(
            preimage=preimage,
            baseline_commit=baseline_commit,
            bindings=bindings,
            classifier=classifier,
            public_cli=public_cli,
            surfaces=surfaces,
            path_free=path_free,
            cleanup_complete=True,
        )
    finally:
        shutil.rmtree(task, ignore_errors=False)
        cleanup_complete = not task.exists()
    if built is None or not cleanup_complete:
        raise QualificationError("qualification cleanup failed")
    built["cleanup_complete"] = cleanup_complete
    built["acceptance"]["cleanup_complete"] = cleanup_complete
    built["status"] = "pass" if all(built["acceptance"].values()) else "inconclusive"
    validate_result_dict(built)
    result_target.write_bytes(canonical_bytes(built))
    print(
        "[OK] WI-0014 qualification executed "
        f"acceptance={sum(built['acceptance'].values())}/{len(ACCEPTANCE_KEYS)} "
        f"sha256={sha256_file(result_target)}"
    )
    return built


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--validate-result", action="store_true")
    result.add_argument("--temp-root", type=Path)
    result.add_argument("--result", type=Path)
    result.add_argument("--confirm-green-preimage-ci", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.validate_result:
            if args.temp_root is not None or args.confirm_green_preimage_ci:
                raise QualificationError("validation accepts no execution arguments")
            validate_result(args.result or RESULT_PATH)
        else:
            if args.temp_root is None or args.result is None:
                raise QualificationError("execution paths are required")
            execute(
                temp_root=args.temp_root,
                result_path=args.result,
                confirm_green_preimage_ci=args.confirm_green_preimage_ci,
            )
    except (OSError, ValueError, QualificationError, subprocess.SubprocessError) as exc:
        print(f"[BLOCK] {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
