#!/usr/bin/env python3
"""Record or validate the synthetic WI-0011 product qualification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import stat
import subprocess
import sys
import time
import uuid
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import materialize_calibre_qualification_library as materializer  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.workspace import (  # noqa: E402
    MARKER_NAME,
    LibraryWorkspaceManager,
    snapshot_library,
)
from sammlungslotse.ebook_calibre_identity import (  # noqa: E402
    CalibreIdentityProfile,
    EbookCalibreIdentityService,
)
from sammlungslotse.ebook_calibre_identity.executor import (  # noqa: E402
    CONTAINER_PREFIX,
    CalibreRecordPodmanExecutor,
)
from sammlungslotse.ebook_calibre_identity.provider import (  # noqa: E402
    CalibreRecordSnapshotProvider,
)
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


PROFILE_PATH = ROOT / "runtime" / "ebook-calibre-identity" / "profile.json"
RUNTIME_PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
LIBRARY_MANIFEST_PATH = ROOT / "runtime" / "calibre-readonly" / "qualification-library.json"
FIXTURE_MANIFEST_PATH = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "manifest.json"
CASES = FIXTURE_MANIFEST_PATH.parent / "cases"
EXACT_INPUT = CASES / "identity-multiformat-edition" / "edition.epub"
NEGATIVE_INPUT = CASES / "identity-title-collision" / "work-b.epub"
CLI = ROOT / "tools" / "run_ebook_calibre_identity.py"
RESULT_PATH = ROOT / "runtime" / "ebook-calibre-identity" / "qualification.json"
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")
ALLOWED_EVIDENCE_ROOT = Path(r"C:\rep\artifacts\SammlungsLotse")
SCHEMA = "sammlungslotse/ebook-calibre-identity-qualification/v1"
PREIMAGE = (
    ".gitignore",
    "runtime/calibre-readonly/profile.json",
    "runtime/calibre-readonly/qualification-library.json",
    "runtime/ebook-calibre-identity/README.md",
    "runtime/ebook-calibre-identity/profile.json",
    "src/sammlungslotse/calibre_inventory/profile.py",
    "src/sammlungslotse/calibre_inventory/workspace.py",
    "src/sammlungslotse/ebook_calibre_identity/__init__.py",
    "src/sammlungslotse/ebook_calibre_identity/application.py",
    "src/sammlungslotse/ebook_calibre_identity/cli.py",
    "src/sammlungslotse/ebook_calibre_identity/executor.py",
    "src/sammlungslotse/ebook_calibre_identity/memory.py",
    "src/sammlungslotse/ebook_calibre_identity/model.py",
    "src/sammlungslotse/ebook_calibre_identity/ports.py",
    "src/sammlungslotse/ebook_calibre_identity/profile.py",
    "src/sammlungslotse/ebook_calibre_identity/provider.py",
    "src/sammlungslotse/ebook_identity/analyzer.py",
    "src/sammlungslotse/ebook_identity/application.py",
    "src/sammlungslotse/ebook_identity/model.py",
    "src/sammlungslotse/ebook_intake/application.py",
    "src/sammlungslotse/ebook_intake/model.py",
    "src/sammlungslotse/ebook_intake/podman_executor.py",
    "src/sammlungslotse/ebook_intake/ports.py",
    "src/sammlungslotse/ebook_intake/snapshot.py",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    "tests/product/test_ebook_calibre_identity.py",
    "tools/materialize_calibre_qualification_library.py",
    "tools/qualify_ebook_calibre_identity.py",
    "tools/run_ebook_calibre_identity.py",
)
ACCEPTANCE_NAMES = frozenset(
    {
        "actual_positive_cli_completed",
        "copy_on_read_and_container_visible",
        "deterministic_json",
        "exact_image_profile_and_preimage",
        "exact_record_epub_byte_match",
        "five_identity_levels_preserved",
        "german_view_matches",
        "input_source_and_fixtures_unchanged",
        "invalid_and_multiple_ids_pre_container",
        "missing_id_and_no_epub_fail_closed",
        "negative_case_has_no_false_same",
        "network_persistence_and_writer_false",
        "output_limit_fail_closed_and_clean",
        "oversize_input_pre_container",
        "path_free_views",
        "recovery_complete",
        "repackaged_representation_detected",
        "simulated_interrupt_cleanup_complete",
        "single_explicit_record_and_roles",
        "synthetic_inputs_only",
        "task_and_container_cleanup_complete",
        "timeout_fail_closed_and_clean",
        "unexpected_output_pre_container",
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


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        info = path.stat(follow_symlinks=False)
    except OSError:
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(info, "st_file_attributes", 0) & flag)


def new_child(path: Path, allowed_root: Path) -> Path:
    root = allowed_root.resolve(strict=True)
    target = path.resolve(strict=False)
    try:
        relative = target.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("qualification target outside controlled root") from exc
    if not relative.parts or target.exists() or not target.parent.is_dir():
        raise RuntimeError("qualification target is not a new strict child")
    current = root
    for part in relative.parts[:-1]:
        current /= part
        if current.exists() and _is_link_or_reparse(current):
            raise RuntimeError("qualification target parent is unsafe")
    if "," in str(target):
        raise RuntimeError("qualification target contains unsupported delimiter")
    return target


def fixture_hashes() -> dict[str, str]:
    manifest = materializer.load_manifest(LIBRARY_MANIFEST_PATH)
    locators = {
        item["fixture"]
        for record in manifest["records"]
        for item in record["formats"]
    }
    locators.add(EXACT_INPUT.relative_to(ROOT).as_posix())
    locators.add(NEGATIVE_INPUT.relative_to(ROOT).as_posix())
    return {name: sha256_file(ROOT / name) for name in sorted(locators)}


def containers() -> list[str]:
    completed = subprocess.run(
        ["podman", "ps", "-a", "--format", "{{.Names}}"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError("container inventory unavailable")
    prefixes = (CONTAINER_PREFIX, materializer.CONTAINER_PREFIX)
    return sorted(name for name in completed.stdout.splitlines() if name.startswith(prefixes))


def run_cli(
    label: str,
    evidence_root: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=90,
    )
    (evidence_root / f"{label}.stdout.txt").write_text(
        completed.stdout, encoding="utf-8", newline="\n"
    )
    (evidence_root / f"{label}.stderr.txt").write_text(
        completed.stderr, encoding="utf-8", newline="\n"
    )
    return completed


def load_json(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def repackage_epub(source: Path, target: Path) -> None:
    with zipfile.ZipFile(source, "r") as incoming, zipfile.ZipFile(
        target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as outgoing:
        names = [item.filename for item in incoming.infolist() if not item.is_dir()]
        if "mimetype" in names:
            outgoing.writestr(
                zipfile.ZipInfo("mimetype", date_time=(2020, 1, 1, 0, 0, 0)),
                incoming.read("mimetype"),
                compress_type=zipfile.ZIP_STORED,
            )
        for name in sorted((item for item in names if item != "mimetype"), reverse=True):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            outgoing.writestr(info, incoming.read(name), compress_type=zipfile.ZIP_DEFLATED)


def stage(report: dict[str, Any], name: str) -> dict[str, Any]:
    identity = report.get("identity") or {}
    return next(
        (item for item in identity.get("stages", []) if item.get("stage") == name),
        {},
    )


def direct_negative_case(
    library: Path,
    task_root: Path,
    input_path: Path,
    profile: CalibreIdentityProfile,
    executor: CalibreRecordPodmanExecutor,
) -> tuple[dict[str, Any], bool]:
    before = snapshot_library(library, profile.runtime)
    provider = CalibreRecordSnapshotProvider(
        source=library,
        temp_root=task_root,
        external_record_id="1",
        profile=profile,
        executor=executor,
    )
    report = EbookCalibreIdentityService(profile).compare(
        LocalFileSnapshotReader(input_path), provider
    )
    clean = before == snapshot_library(library, profile.runtime) and not list(task_root.iterdir())
    return report.to_dict(), clean


class InterruptingExecutor:
    def execute(self, _workspace: object, _external_record_id: int) -> object:
        raise KeyboardInterrupt


class UnexpectedOutputExecutor:
    def __init__(self, delegate: CalibreRecordPodmanExecutor) -> None:
        self.delegate = delegate

    def execute(self, workspace: Any, external_record_id: int) -> object:
        (workspace.output / "unexpected.opf").write_bytes(b"synthetic-control")
        return self.delegate.execute(workspace, external_record_id)


def interrupt_case(
    library: Path, task_root: Path, input_path: Path, profile: CalibreIdentityProfile
) -> bool:
    before = snapshot_library(library, profile.runtime)
    provider = CalibreRecordSnapshotProvider(
        source=library,
        temp_root=task_root,
        external_record_id="1",
        profile=profile,
        executor=InterruptingExecutor(),
    )
    try:
        EbookCalibreIdentityService(profile).compare(
            LocalFileSnapshotReader(input_path), provider
        )
    except KeyboardInterrupt:
        return before == snapshot_library(library, profile.runtime) and not list(task_root.iterdir())
    return False


def seed_stale_task(task_root: Path, profile: CalibreIdentityProfile) -> str:
    task_id = f"stale{uuid.uuid4().hex[:12]}"
    task = task_root / f"task-{task_id}"
    task.mkdir(mode=0o700)
    marker = {
        "created_epoch": time.time() - int(profile.runtime.workspace["max_task_age_seconds"]) - 1,
        "profile_id": profile.runtime.profile_id,
        "schema": profile.runtime.workspace["marker_schema"],
        "task_id": task_id,
    }
    (task / MARKER_NAME).write_text(
        json.dumps(marker, separators=(",", ":"), sort_keys=True), encoding="utf-8"
    )
    (task / "synthetic-leftover.bin").write_bytes(b"WI-0011")
    return task_id


def evidence_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.iterdir())
        if path.is_file()
    }


def qualify(
    qualification_root: Path, evidence_root: Path, result_path: Path
) -> dict[str, Any]:
    root = new_child(qualification_root, ALLOWED_TEMP_ROOT)
    raw_root = new_child(evidence_root, ALLOWED_EVIDENCE_ROOT)
    result = result_path.resolve(strict=False)
    try:
        result.relative_to(root)
    except ValueError:
        pass
    else:
        raise RuntimeError("qualification result must stay outside disposable root")

    profile = CalibreIdentityProfile.load(PROFILE_PATH, RUNTIME_PROFILE_PATH)
    fixtures_before = fixture_hashes()
    containers_before = containers()
    root.mkdir()
    raw_root.mkdir()
    acceptance: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    root_removed = False
    try:
        library = root / "library"
        task_root = root / "tasks"
        task_root.mkdir()
        materialized = materializer.materialize(library)
        source_before = snapshot_library(library, profile.runtime)
        exact_before = sha256_file(EXACT_INPUT)
        repackaged = root / "synthetic-repackaged.epub"
        oversized = root / "synthetic-oversized.epub"
        repackage_epub(EXACT_INPUT, repackaged)
        oversized.write_bytes(b"x" * (profile.limits["max_input_bytes"] + 1))

        common = ("--temp-root", str(task_root), str(EXACT_INPUT), str(library), "1")
        first = run_cli("positive-1", raw_root, "--json", *common)
        second = run_cli("positive-2", raw_root, "--json", *common)
        human = run_cli("positive-human", raw_root, *common)
        repacked = run_cli(
            "repackaged", raw_root, "--json", "--temp-root", str(task_root),
            str(repackaged), str(library), "1"
        )
        negative = run_cli(
            "negative", raw_root, "--json", "--temp-root", str(task_root),
            str(NEGATIVE_INPUT), str(library), "1"
        )
        missing = run_cli(
            "missing-id", raw_root, "--json", "--temp-root", str(task_root),
            str(EXACT_INPUT), str(library), "999"
        )
        no_epub = run_cli(
            "no-epub", raw_root, "--json", "--temp-root", str(task_root),
            str(EXACT_INPUT), str(library), "2"
        )

        selection_containers = containers()
        invalid = run_cli(
            "invalid-id", raw_root, "--json", "--temp-root", str(task_root),
            str(EXACT_INPUT), str(library), "not-an-id"
        )
        multiple = run_cli(
            "multiple-id", raw_root, "--json", "--temp-root", str(task_root),
            str(EXACT_INPUT), str(library), "1", "3"
        )
        selection_unchanged = selection_containers == containers()

        oversized_containers = containers()
        oversized_run = run_cli(
            "oversized-input", raw_root, "--json", "--temp-root", str(task_root),
            str(oversized), str(library), "1"
        )
        oversized_pre_container = oversized_containers == containers()

        limited_data = copy.deepcopy(profile.data)
        limited_data["limits"]["max_input_bytes"] = 1
        limited_profile = CalibreIdentityProfile(limited_data, profile.runtime)
        output_report, output_clean = direct_negative_case(
            library, task_root, EXACT_INPUT, profile,
            CalibreRecordPodmanExecutor(limited_profile)
        )

        timeout_runtime_data = copy.deepcopy(profile.runtime.data)
        timeout_runtime_data["execution"]["timeout_seconds"] = 0.01
        timeout_runtime = CalibreRuntimeProfile(timeout_runtime_data)
        timeout_profile = CalibreIdentityProfile(profile.data, timeout_runtime)
        timeout_report, timeout_clean = direct_negative_case(
            library, task_root, EXACT_INPUT, profile,
            CalibreRecordPodmanExecutor(timeout_profile)
        )

        unexpected_containers = containers()
        unexpected_report, unexpected_clean = direct_negative_case(
            library, task_root, EXACT_INPUT, profile,
            UnexpectedOutputExecutor(CalibreRecordPodmanExecutor(profile)),
        )
        unexpected_pre_container = unexpected_containers == containers()
        interrupted_clean = interrupt_case(library, task_root, EXACT_INPUT, profile)

        stale_id = seed_stale_task(task_root, profile)
        recovery = run_cli("recovery", raw_root, "--json", *common)
        stale_removed = not (task_root / f"task-{stale_id}").exists()

        first_value = load_json(first)
        repacked_value = load_json(repacked)
        negative_value = load_json(negative)
        missing_value = load_json(missing)
        no_epub_value = load_json(no_epub)
        oversized_value = load_json(oversized_run)
        recovery_value = load_json(recovery)
        source_after = snapshot_library(library, profile.runtime)
        serialized = "".join(
            item.stdout + item.stderr
            for item in (
                first, second, human, repacked, negative, missing, no_epub,
                invalid, multiple, oversized_run, recovery,
            )
        )
        forbidden = (
            str(ROOT), str(root), str(raw_root), str(EXACT_INPUT), str(NEGATIVE_INPUT),
            EXACT_INPUT.name, NEGATIVE_INPUT.name, repackaged.name, oversized.name,
        )
        first_identity = first_value.get("identity") or {}
        first_inputs = first_identity.get("inputs", [])
        first_effects = first_value.get("effects") or {}
        nested_effects = first_identity.get("effects") or {}
        output_reasons = output_report.get("handoff_reason_codes", [])
        timeout_reasons = timeout_report.get("handoff_reason_codes", [])
        unexpected_reasons = unexpected_report.get("handoff_reason_codes", [])
        acceptance.update(
            {
                "actual_positive_cli_completed": first.returncode == second.returncode == human.returncode == 0,
                "copy_on_read_and_container_visible": first_effects.get("task_materialized") is True and first_effects.get("container_started") is True,
                "deterministic_json": first.stdout == second.stdout and bool(first.stdout),
                "exact_image_profile_and_preimage": first_value.get("calibre_record", {}).get("profile_id") == profile.profile_id and profile.runtime.image["id"] == profile.data["calibre_runtime"]["image_id"],
                "exact_record_epub_byte_match": first_identity.get("overall") == "exact_byte_match" and len(first_inputs) == 2 and first_inputs[1].get("sha256") == exact_before,
                "five_identity_levels_preserved": [item.get("stage") for item in first_identity.get("stages", [])] == ["byte", "package", "representation", "edition", "work"],
                "german_view_matches": "EPUB-Calibre-Identitätskandidatenbericht" in human.stdout and "exact_byte_match" in human.stdout,
                "input_source_and_fixtures_unchanged": exact_before == sha256_file(EXACT_INPUT) and source_before == source_after and fixtures_before == fixture_hashes(),
                "invalid_and_multiple_ids_pre_container": invalid.returncode == multiple.returncode == 2 and selection_unchanged,
                "missing_id_and_no_epub_fail_closed": missing.returncode == no_epub.returncode == 4 and missing_value.get("identity") is None and no_epub_value.get("identity") is None,
                "negative_case_has_no_false_same": negative.returncode == 0 and negative_value.get("identity", {}).get("overall") != "exact_byte_match" and all(stage(negative_value, name).get("decision") != "candidate_same" for name in ("byte", "package", "representation", "edition", "work")),
                "network_persistence_and_writer_false": all(first_effects.get(key) is False for key in ("network_access", "persistence", "writer", "domain_system_writes")) and all(value is False for value in nested_effects.values()),
                "output_limit_fail_closed_and_clean": output_report.get("assessment") == "not_assessed" and output_report.get("identity") is None and output_clean and any(reason in {"executor.failed", "provider.output_contract_invalid"} for reason in output_reasons),
                "oversize_input_pre_container": oversized_run.returncode == 4 and oversized_value.get("identity") is None and oversized_pre_container,
                "path_free_views": not any(value in serialized for value in forbidden),
                "recovery_complete": recovery.returncode == 0 and recovery_value.get("assessment") == "completed" and stale_removed,
                "repackaged_representation_detected": repacked.returncode == 0 and repacked_value.get("identity", {}).get("overall") == "representation_candidate",
                "simulated_interrupt_cleanup_complete": interrupted_clean,
                "single_explicit_record_and_roles": first_value.get("source_roles") == {"1": "ingress_epub", "2": "calibre_record_epub"} and first_value.get("calibre_record", {}).get("external_record_id") == 1,
                "synthetic_inputs_only": materializer.load_manifest(LIBRARY_MANIFEST_PATH).get("synthetic_only") is True,
                "task_and_container_cleanup_complete": not list(task_root.iterdir()),
                "timeout_fail_closed_and_clean": timeout_report.get("assessment") == "not_assessed" and timeout_report.get("identity") is None and timeout_clean and "executor.timeout" in timeout_reasons,
                "unexpected_output_pre_container": unexpected_report.get("assessment") == "not_assessed" and "provider.output_contract_invalid" in unexpected_reasons and unexpected_clean and unexpected_pre_container,
            }
        )
        evidence.update(
            {
                "exact_input_sha256": exact_before,
                "first_json_sha256": hashlib.sha256(first.stdout.encode("utf-8")).hexdigest(),
                "human_sha256": hashlib.sha256(human.stdout.encode("utf-8")).hexdigest(),
                "library_snapshot_sha256": source_before.digest,
                "materialization_manifest_sha256": materialized["manifest_sha256"],
                "negative_overall": negative_value.get("identity", {}).get("overall"),
                "output_limit_reasons": output_reasons,
                "repackaged_overall": repacked_value.get("identity", {}).get("overall"),
                "timeout_reasons": timeout_reasons,
            }
        )
    finally:
        shutil.rmtree(root)
        root_removed = not root.exists()

    containers_after = containers()
    acceptance["task_and_container_cleanup_complete"] = (
        acceptance.get("task_and_container_cleanup_complete") is True
        and root_removed
        and containers_before == containers_after
    )
    result_value: dict[str, Any] = {
        "acceptance": dict(sorted(acceptance.items())),
        "evidence": evidence,
        "fixture_hashes": fixtures_before,
        "image_id": profile.runtime.image["id"],
        "preimage": preimage(),
        "preimage_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", check=True
        ).stdout.strip(),
        "profile_id": profile.profile_id,
        "raw_evidence_sha256": evidence_hashes(raw_root),
        "repetitions": 2,
        "schema": SCHEMA,
        "status": "PASS" if set(acceptance) == ACCEPTANCE_NAMES and all(acceptance.values()) else "FAIL",
        "synthetic_only": True,
        "work_item": "WI-0011",
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(result_value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"WI-0011 qualification: {sum(acceptance.values())}/{len(ACCEPTANCE_NAMES)}"
    )
    return result_value


def validate(path: Path = RESULT_PATH) -> dict[str, Any]:
    profile = CalibreIdentityProfile.load(PROFILE_PATH, RUNTIME_PROFILE_PATH)
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != SCHEMA or value.get("work_item") != "WI-0011":
        raise ValueError("qualification identity differs")
    if value.get("status") != "PASS" or value.get("synthetic_only") is not True:
        raise ValueError("qualification did not pass")
    acceptance = value.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != ACCEPTANCE_NAMES:
        raise ValueError("qualification acceptance set differs")
    if not all(item is True for item in acceptance.values()):
        raise ValueError("qualification acceptance is incomplete")
    if value.get("preimage") != preimage() or value.get("fixture_hashes") != fixture_hashes():
        raise ValueError("qualification preimage differs")
    if value.get("profile_id") != profile.profile_id or value.get("image_id") != profile.runtime.image["id"]:
        raise ValueError("qualification profile binding differs")
    if value.get("repetitions") != 2 or len(value.get("raw_evidence_sha256", {})) != 22:
        raise ValueError("qualification repetition or raw evidence count differs")
    commit = value.get("preimage_commit", "")
    if not isinstance(commit, str) or len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise ValueError("qualification preimage commit differs")
    print(f"WI-0011 qualification valid: {len(ACCEPTANCE_NAMES)}/{len(ACCEPTANCE_NAMES)}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualification-root", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_result:
            validate(args.result)
            return 0
        if args.qualification_root is None or args.evidence_root is None:
            parser.error("--qualification-root and --evidence-root are required")
        result = qualify(args.qualification_root, args.evidence_root, args.result)
        return 0 if result["status"] == "PASS" else 4
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"WI-0011 qualification failed: {type(exc).__name__}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
