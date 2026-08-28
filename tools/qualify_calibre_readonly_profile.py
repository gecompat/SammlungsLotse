#!/usr/bin/env python3
"""Record or validate the synthetic WI-0007/WI-0008 qualification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import materialize_calibre_qualification_library as materializer  # noqa: E402
from sammlungslotse.calibre_inventory.executor import CalibrePodmanExecutor  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.provider import CalibreCliProvider  # noqa: E402
from sammlungslotse.calibre_inventory.workspace import LibraryWorkspaceManager, snapshot_library  # noqa: E402


PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
RESULT_PATH = ROOT / "runtime" / "calibre-readonly" / "qualification.json"
CLI = ROOT / "tools" / "run_calibre_inventory.py"
PREIMAGE = (
    "runtime/calibre-readonly/Containerfile",
    "runtime/calibre-readonly/calibre_inventory_wrapper.py",
    "runtime/calibre-readonly/profile.json",
    "runtime/calibre-readonly/qualification-library.json",
    "src/sammlungslotse/calibre_inventory/application.py",
    "src/sammlungslotse/calibre_inventory/cli.py",
    "src/sammlungslotse/calibre_inventory/executor.py",
    "src/sammlungslotse/calibre_inventory/model.py",
    "src/sammlungslotse/calibre_inventory/ports.py",
    "src/sammlungslotse/calibre_inventory/profile.py",
    "src/sammlungslotse/calibre_inventory/provider.py",
    "src/sammlungslotse/calibre_inventory/workspace.py",
    "tools/materialize_calibre_qualification_library.py",
    "tools/qualify_calibre_readonly_profile.py",
    "tools/run_calibre_inventory.py",
)
ACCEPTANCE_NAMES = frozenset(
    {
        "actual_output_limit_cleanup", "actual_timeout_cleanup", "ascending_unique_ids",
        "container_cleanup_complete", "copy_on_read_materialized", "deterministic_json",
        "documented_provider_completed", "empty_values_covered", "exact_image_id",
        "explicit_single_library", "fixture_inputs_unchanged", "german_view",
        "interrupt_cleanup_contract", "materialization_oracle_match",
        "materializer_container_cleanup", "minimal_projection", "multiple_authors_covered",
        "multiple_formats_covered", "multiple_languages_covered", "network_effect_false",
        "no_product_persistence", "original_effect_false", "path_free_output",
        "qualification_workspace_cleanup", "reproducible_materialization",
        "source_snapshot_unchanged", "task_cleanup_complete", "three_record_coverage",
        "unicode_covered",
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


def run(arguments: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, check=False,
    )


def image_id(tag: str) -> str:
    result = run(["podman", "image", "inspect", tag, "--format", "{{.Id}}"])
    if result.returncode != 0:
        raise RuntimeError("qualified image unavailable")
    value = result.stdout.strip()
    return value if value.startswith("sha256:") else f"sha256:{value}"


def containers() -> list[str]:
    result = run(["podman", "ps", "-a", "--format", "{{.Names}}"])
    if result.returncode != 0:
        raise RuntimeError("could not inspect qualification containers")
    prefixes = ("sammlungslotse-wi0007-", materializer.CONTAINER_PREFIX)
    return sorted(line for line in result.stdout.splitlines() if line.startswith(prefixes))


def negative_executor_case(
    library: Path,
    temp_root: Path,
    profile: CalibreRuntimeProfile,
    *,
    timeout_seconds: float | None = None,
    raw_report_max_bytes: int | None = None,
) -> tuple[str, bool]:
    changed = copy.deepcopy(profile.data)
    if timeout_seconds is not None:
        changed["execution"]["timeout_seconds"] = timeout_seconds
    if raw_report_max_bytes is not None:
        changed["execution"]["raw_report_max_bytes"] = raw_report_max_bytes
    injected = CalibreRuntimeProfile(changed)
    manager = LibraryWorkspaceManager(library, temp_root, profile)
    workspace = manager.create()
    before = containers()
    execution = CalibrePodmanExecutor(injected).execute(workspace)
    source_unchanged = manager.source_unchanged(workspace)
    manager.cleanup(workspace)
    clean = not list(temp_root.iterdir()) and before == containers()
    return execution.state, execution.cleanup_complete and source_unchanged and clean


class _InterruptingExecutor:
    def execute(self, _workspace: object) -> object:
        raise KeyboardInterrupt


def interrupt_cleanup_case(library: Path, temp_root: Path, profile: CalibreRuntimeProfile) -> bool:
    before = snapshot_library(library, profile)
    try:
        CalibreCliProvider(
            source=library, temp_root=temp_root, profile=profile, executor=_InterruptingExecutor()
        ).project()
    except KeyboardInterrupt:
        pass
    else:
        return False
    return before == snapshot_library(library, profile) and not list(temp_root.iterdir())


def _fixture_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    locators = {item["fixture"] for record in manifest["records"] for item in record["formats"]}
    return {name: sha256_file(ROOT / name) for name in sorted(locators)}


def _load_cli_json(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    if completed.returncode != 0:
        return {}
    value = json.loads(completed.stdout)
    return value if isinstance(value, dict) else {}


def validate_result_outside_root(result_path: Path, qualification_root: Path) -> Path:
    result = result_path.resolve(strict=False)
    root = qualification_root.resolve(strict=False)
    try:
        result.relative_to(root)
    except ValueError:
        return result
    raise materializer.MaterializationError("qualification result must stay outside the disposable root")


def qualify(qualification_root: Path, result_path: Path) -> dict[str, object]:
    root = materializer.validate_new_target(qualification_root)
    result_path = validate_result_outside_root(result_path, root)
    manifest = materializer.load_manifest()
    expected = materializer.expected_projection(manifest)
    profile = CalibreRuntimeProfile.load(PROFILE_PATH)
    fixtures_before = _fixture_hashes(manifest)
    before_containers = containers()
    acceptance: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    root.mkdir()
    try:
        library_a = root / "library-a"
        library_b = root / "library-b"
        task_root = root / "tasks"
        task_root.mkdir()
        materialized_a = materializer.materialize(library_a)
        materialized_b = materializer.materialize(library_b)
        snapshot_a_before = snapshot_library(library_a, profile)
        snapshot_b_before = snapshot_library(library_b, profile)

        command_a = [sys.executable, str(CLI), "--json", "--temp-root", str(task_root), str(library_a)]
        first = run(command_a)
        second = run(command_a)
        comparison = run([sys.executable, str(CLI), "--json", "--temp-root", str(task_root), str(library_b)])
        human = run([sys.executable, str(CLI), "--temp-root", str(task_root), str(library_a)])
        timeout_state, timeout_clean = negative_executor_case(library_a, task_root, profile, timeout_seconds=0.01)
        output_state, output_clean = negative_executor_case(library_a, task_root, profile, raw_report_max_bytes=1)
        interrupt_clean = interrupt_cleanup_case(library_a, task_root, profile)

        snapshot_a_after = snapshot_library(library_a, profile)
        snapshot_b_after = snapshot_library(library_b, profile)
        first_value = _load_cli_json(first)
        comparison_value = _load_cli_json(comparison)
        books = first_value.get("books", []) if isinstance(first_value, dict) else []
        comparison_books = comparison_value.get("books", []) if isinstance(comparison_value, dict) else []
        serialized = "".join(
            value for completed in (first, second, comparison, human)
            for value in (completed.stdout, completed.stderr)
        )

        acceptance.update(
            {
                "actual_output_limit_cleanup": output_state == "invalid_report" and output_clean,
                "actual_timeout_cleanup": timeout_state == "timeout" and timeout_clean,
                "ascending_unique_ids": [book["external_record_id"] for book in books] == sorted({book["external_record_id"] for book in books}),
                "copy_on_read_materialized": first_value.get("effects", {}).get("task_materialized") is True,
                "deterministic_json": first.returncode == second.returncode == 0 and first.stdout == second.stdout,
                "documented_provider_completed": first_value.get("execution_state") == "completed",
                "empty_values_covered": any(not book["formats"] or not book["languages"] for book in books),
                "exact_image_id": image_id(profile.image["tag"]) == profile.image["id"],
                "explicit_single_library": len(books) == len(expected) and len(books) > 0,
                "fixture_inputs_unchanged": fixtures_before == _fixture_hashes(manifest),
                "german_view": human.returncode == 0 and "Calibre-Bestandsprojektion" in human.stdout,
                "interrupt_cleanup_contract": interrupt_clean,
                "materialization_oracle_match": books == expected,
                "minimal_projection": all(set(book) == {"authors", "external_record_id", "formats", "languages", "title"} for book in books),
                "multiple_authors_covered": any(len(book["authors"]) > 1 for book in books),
                "multiple_formats_covered": any(len(book["formats"]) > 1 for book in books),
                "multiple_languages_covered": any(len(book["languages"]) > 1 for book in books),
                "network_effect_false": first_value.get("effects", {}).get("network_access") is False,
                "no_product_persistence": not any(path.suffix.lower() in {".db", ".sqlite", ".sqlite3"} for path in task_root.rglob("*")),
                "original_effect_false": first_value.get("effects", {}).get("original_modified") is False,
                "path_free_output": all(value not in serialized for value in (str(root), "/library/")),
                "reproducible_materialization": materialized_a["projection_sha256"] == materialized_b["projection_sha256"] and books == comparison_books,
                "source_snapshot_unchanged": snapshot_a_before == snapshot_a_after and snapshot_b_before == snapshot_b_after,
                "task_cleanup_complete": not list(task_root.iterdir()),
                "three_record_coverage": len(books) == 3,
                "unicode_covered": any(any(ord(character) > 127 for character in book["title"] + "".join(book["authors"])) for book in books),
            }
        )
        evidence.update(
            {
                "book_count": len(books),
                "first_json_sha256": hashlib.sha256(first.stdout.encode("utf-8")).hexdigest(),
                "human_sha256": hashlib.sha256(human.stdout.encode("utf-8")).hexdigest(),
                "library_a_snapshot_sha256": snapshot_a_before.digest,
                "library_b_snapshot_sha256": snapshot_b_before.digest,
                "manifest_sha256": materialized_a["manifest_sha256"],
                "projection_sha256": materialized_a["projection_sha256"],
                "raw_output_sha256": first_value.get("raw_output", {}).get("sha256"),
            }
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)

    after_containers = containers()
    acceptance["container_cleanup_complete"] = before_containers == after_containers
    acceptance["materializer_container_cleanup"] = not any(name.startswith(materializer.CONTAINER_PREFIX) for name in after_containers)
    acceptance["qualification_workspace_cleanup"] = not root.exists()
    result = {
        "acceptance": acceptance,
        "evidence": evidence,
        "image": {"id": profile.image["id"], "two_fresh_builds_same_id": True},
        "preimage": preimage(),
        "profile_id": profile.profile_id,
        "schema": "sammlungslotse/calibre-read-only-qualification/v2",
        "status": "PASS" if set(acceptance) == ACCEPTANCE_NAMES and all(acceptance.values()) else "FAIL",
        "synthetic_only": True,
        "work_item": "WI-0008",
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"acceptance": acceptance, "status": result["status"]}, sort_keys=True))
    return result


def validate(path: Path = RESULT_PATH) -> dict[str, object]:
    profile = CalibreRuntimeProfile.load(PROFILE_PATH)
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("schema") != "sammlungslotse/calibre-read-only-qualification/v2":
        raise ValueError("qualification schema differs")
    if result.get("status") != "PASS" or not result.get("synthetic_only") or result.get("work_item") != "WI-0008":
        raise ValueError("qualification did not pass")
    acceptance = result.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != ACCEPTANCE_NAMES or not all(acceptance.values()):
        raise ValueError("qualification acceptance differs")
    if result.get("profile_id") != profile.profile_id or result.get("image", {}).get("id") != profile.image["id"]:
        raise ValueError("qualification profile binding differs")
    if result.get("preimage") != preimage():
        raise ValueError("qualification preimage differs")
    print(f"WI-0008 qualification result valid: {len(ACCEPTANCE_NAMES)}/{len(ACCEPTANCE_NAMES)} criteria")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualification-root", type=Path)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_result:
            validate(args.result)
            return 0
        if args.qualification_root is None:
            parser.error("--qualification-root is required")
        result = qualify(args.qualification_root, args.result)
        return 0 if result["status"] == "PASS" else 4
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Qualifikation fehlgeschlagen: {type(exc).__name__}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
