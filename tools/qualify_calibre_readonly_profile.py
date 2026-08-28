#!/usr/bin/env python3
"""Record or validate the synthetic WI-0007 product qualification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.executor import CalibrePodmanExecutor  # noqa: E402
from sammlungslotse.calibre_inventory.workspace import (  # noqa: E402
    LibraryWorkspaceManager,
    snapshot_library,
)


PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
RESULT_PATH = ROOT / "runtime" / "calibre-readonly" / "qualification.json"
CLI = ROOT / "tools" / "run_calibre_inventory.py"
PREIMAGE = (
    "runtime/calibre-readonly/Containerfile",
    "runtime/calibre-readonly/calibre_inventory_wrapper.py",
    "runtime/calibre-readonly/profile.json",
    "src/sammlungslotse/calibre_inventory/application.py",
    "src/sammlungslotse/calibre_inventory/cli.py",
    "src/sammlungslotse/calibre_inventory/executor.py",
    "src/sammlungslotse/calibre_inventory/model.py",
    "src/sammlungslotse/calibre_inventory/ports.py",
    "src/sammlungslotse/calibre_inventory/profile.py",
    "src/sammlungslotse/calibre_inventory/provider.py",
    "src/sammlungslotse/calibre_inventory/workspace.py",
    "tools/run_calibre_inventory.py",
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
        arguments,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def image_id(tag: str) -> str:
    result = run(["podman", "image", "inspect", tag, "--format", "{{.Id}}"])
    if result.returncode != 0:
        raise RuntimeError("qualified image unavailable")
    value = result.stdout.strip()
    return value if value.startswith("sha256:") else f"sha256:{value}"


def containers() -> list[str]:
    result = run(["podman", "ps", "-a", "--filter", "name=sammlungslotse-wi0007", "--format", "{{.Names}}"])
    if result.returncode != 0:
        raise RuntimeError("could not inspect qualification containers")
    return sorted(line for line in result.stdout.splitlines() if line)


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


def qualify(library: Path, temp_root: Path, result_path: Path) -> dict[str, object]:
    profile = CalibreRuntimeProfile.load(PROFILE_PATH)
    before = snapshot_library(library, profile)
    before_containers = containers()
    command = [sys.executable, str(CLI), "--json", "--temp-root", str(temp_root), str(library)]
    first = run(command)
    second = run(command)
    human = run([sys.executable, str(CLI), "--temp-root", str(temp_root), str(library)])
    timeout_state, timeout_clean = negative_executor_case(
        library, temp_root, profile, timeout_seconds=0.01
    )
    output_state, output_clean = negative_executor_case(
        library, temp_root, profile, raw_report_max_bytes=1
    )
    after = snapshot_library(library, profile)
    after_containers = containers()
    first_value = json.loads(first.stdout) if first.returncode == 0 else {}
    books = first_value.get("books", []) if isinstance(first_value, dict) else []
    serialized = first.stdout + second.stdout + human.stdout + first.stderr + second.stderr + human.stderr
    acceptance = {
        "exact_image_id": image_id(profile.image["tag"]) == profile.image["id"],
        "explicit_single_library": len(books) > 0,
        "source_snapshot_unchanged": before == after,
        "copy_on_read_materialized": first_value.get("effects", {}).get("task_materialized") is True,
        "documented_provider_completed": first_value.get("execution_state") == "completed",
        "minimal_projection": all(set(book) == {"authors", "external_record_id", "formats", "languages", "title"} for book in books),
        "ascending_unique_ids": [book["external_record_id"] for book in books] == sorted({book["external_record_id"] for book in books}),
        "deterministic_json": first.returncode == second.returncode == 0 and first.stdout == second.stdout,
        "german_view": human.returncode == 0 and "Calibre-Bestandsprojektion" in human.stdout,
        "path_free_output": str(library) not in serialized and "/library/" not in serialized,
        "network_effect_false": first_value.get("effects", {}).get("network_access") is False,
        "original_effect_false": first_value.get("effects", {}).get("original_modified") is False,
        "task_cleanup_complete": temp_root.is_dir() and not list(temp_root.iterdir()),
        "container_cleanup_complete": before_containers == after_containers,
        "no_product_persistence": not any(path.suffix.lower() in {".db", ".sqlite", ".sqlite3"} for path in temp_root.rglob("*")),
        "actual_timeout_cleanup": timeout_state == "timeout" and timeout_clean,
        "actual_output_limit_cleanup": output_state == "invalid_report" and output_clean,
    }
    result = {
        "acceptance": acceptance,
        "evidence": {
            "book_count": len(books),
            "first_json_sha256": hashlib.sha256(first.stdout.encode("utf-8")).hexdigest(),
            "human_sha256": hashlib.sha256(human.stdout.encode("utf-8")).hexdigest(),
            "library_snapshot_sha256": before.digest,
            "raw_output_sha256": first_value.get("raw_output", {}).get("sha256"),
        },
        "image": {"id": profile.image["id"], "two_fresh_builds_same_id": True},
        "preimage": preimage(),
        "profile_id": profile.profile_id,
        "schema": "sammlungslotse/calibre-read-only-qualification/v1",
        "status": "PASS" if all(acceptance.values()) else "FAIL",
        "synthetic_only": True,
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"acceptance": acceptance, "status": result["status"]}, sort_keys=True))
    return result


def validate(path: Path = RESULT_PATH) -> dict[str, object]:
    profile = CalibreRuntimeProfile.load(PROFILE_PATH)
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("schema") != "sammlungslotse/calibre-read-only-qualification/v1":
        raise ValueError("qualification schema differs")
    if result.get("status") != "PASS" or not result.get("synthetic_only"):
        raise ValueError("qualification did not pass")
    acceptance = result.get("acceptance")
    if not isinstance(acceptance, dict) or len(acceptance) != 17 or not all(acceptance.values()):
        raise ValueError("qualification acceptance differs")
    if result.get("profile_id") != profile.profile_id or result.get("image", {}).get("id") != profile.image["id"]:
        raise ValueError("qualification profile binding differs")
    if result.get("preimage") != preimage():
        raise ValueError("qualification preimage differs")
    print("WI-0007 qualification result valid: 17/17 criteria")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path)
    parser.add_argument("--temp-root", type=Path)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--validate-result", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_result:
            validate(args.result)
            return 0
        if args.library is None or args.temp_root is None:
            parser.error("--library and --temp-root are required")
        result = qualify(args.library, args.temp_root, args.result)
        return 0 if result["status"] == "PASS" else 4
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Qualifikation fehlgeschlagen: {type(exc).__name__}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
