#!/usr/bin/env python3
"""Qualify the public WI-0019 CLI with one synthetic Calibre library only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import materialize_calibre_qualification_library as materializer  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.workspace import snapshot_library  # noqa: E402


SCHEMA = "sammlungslotse/ebook-review-plan-qualification/v1"
FIXTURES = (
    "identity-multiformat-edition/edition.epub",
    "metadata-multilingual-rtl/multilingual-rtl.epub",
    "epub-active-or-remote/active-remote.epub",
    "format-unknown/unknown.epub",
)
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases"
PROFILE = ROOT / "runtime" / "calibre-readonly" / "profile.json"
CLI = ROOT / "tools" / "run_ebook_review_plan.py"
ALLOWED_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")


class QualificationError(RuntimeError):
    """The bounded synthetic qualification cannot establish its evidence."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _new_child(path: Path, allowed_root: Path = ALLOWED_ROOT) -> Path:
    """Validate a new disposable child; production keeps its fixed root."""

    root = allowed_root.resolve(strict=True)
    candidate = path.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise QualificationError("qualification root is outside the allowed root") from exc
    if candidate == root or candidate.exists():
        raise QualificationError("qualification root must be a new child")
    return candidate


def _safe(value: object) -> bool:
    forbidden = {"title", "authors", "languages", "formats", "path", "raw_output"}
    if isinstance(value, dict):
        return all(key not in forbidden and _safe(item) for key, item in value.items())
    if isinstance(value, list):
        return all(_safe(item) for item in value)
    return not isinstance(value, str) or ("\\" not in value and "://" not in value)


def _run(inbox: Path, library: Path, tasks: Path) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT"] = str(tasks)
    return subprocess.run(
        [sys.executable, str(CLI), str(inbox), str(library), "--json"],
        cwd=ROOT, env=environment, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace", check=False, timeout=120,
    )


def qualify(root: Path) -> dict[str, Any]:
    task_root = _new_child(root)
    profile = CalibreRuntimeProfile.load(PROFILE)
    fixtures = {str(item): sha256_file(CASES / item) for item in FIXTURES}
    task_root.mkdir(parents=True)
    try:
        library = task_root / "library"
        inbox = task_root / "inbox"
        tasks = task_root / "tasks"
        inbox.mkdir()
        tasks.mkdir()
        materialized = materializer.materialize(library)
        library_before = snapshot_library(library, profile)
        for index, source in enumerate(FIXTURES):
            shutil.copyfile(CASES / source, inbox / f"input-{index}{Path(source).suffix}")
        # Six equal synthetic EPUBs exercise a populated bounded candidate path.
        for index in range(6):
            shutil.copyfile(CASES / FIXTURES[0], inbox / f"candidate-{index}.epub")
        first, second = _run(inbox, library, tasks), _run(inbox, library, tasks)
        first_value, second_value = json.loads(first.stdout), json.loads(second.stdout)
        serialized = first.stdout + first.stderr + second.stdout + second.stderr
        classes = Counter(item["review_class"] for item in first_value.get("items", []))
        candidates = [candidate for item in first_value.get("items", []) for candidate in item.get("candidates", [])]
        library_after = snapshot_library(library, profile)
        acceptance = {
            "public_cli_completed": first.returncode == second.returncode == 0,
            "two_runs_identical": first.stdout == second.stdout and bool(first.stdout),
            "one_library_and_bounded_candidates": all(len(item.get("candidates", [])) <= 5 for item in first_value.get("items", [])),
            "positive_blocked_and_non_epub_visible": classes["review_candidate_present"] >= 1 and classes["review_ingress_blocked"] >= 1 and classes["unsupported"] >= 1,
            "path_title_and_content_free": all(value not in serialized for value in (str(ROOT), str(task_root), "Atlas Δ", "private", "input-0.epub")),
            "sources_and_library_unchanged": fixtures == {str(item): sha256_file(CASES / item) for item in FIXTURES} and library_before == library_after,
            "task_cleanup_complete": not list(tasks.iterdir()),
            "no_forbidden_effects": first_value.get("effects") == {"filesystem_writes": False, "import": False, "network_access": False, "persistence": False},
            "public_evidence_is_safe": _safe(first_value) and _safe(second_value),
        }
        result = {
            "acceptance": dict(sorted(acceptance.items())),
            "artifact": "EXP-0020",
            "case_count": len(first_value.get("items", [])),
            "effects": {"external_network_access": False, "import": False, "persistence": False, "writer_effects": False},
            "first_json_sha256": hashlib.sha256(first.stdout.encode("utf-8")).hexdigest(),
            "materialization": materialized,
            "repetitions": 2,
            "schema": SCHEMA,
            "status": "pass" if all(acceptance.values()) else "fail",
            "synthetic_only": True,
        }
        if not _safe(result):
            raise QualificationError("result leaks source metadata")
        return result
    finally:
        shutil.rmtree(task_root, ignore_errors=True)
        if task_root.exists():
            raise QualificationError("qualification cleanup failed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualification-root", required=True, type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    try:
        result = qualify(args.qualification_root)
        encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.result is None:
            print(encoded, end="")
        else:
            args.result.write_text(encoded, encoding="utf-8", newline="\n")
        return 0 if result["status"] == "pass" else 4
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"EXP-0020 qualification failed: {type(exc).__name__}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
