#!/usr/bin/env python3
"""Materialize the bounded synthetic WI-0008 Calibre qualification library."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.provider import parse_calibre_output  # noqa: E402
from sammlungslotse.ebook_intake.podman_executor import run_bounded  # noqa: E402


PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
MANIFEST_PATH = ROOT / "runtime" / "calibre-readonly" / "qualification-library.json"
ALLOWED_TEMP_ROOT = Path(r"C:\rep\tmp\SammlungsLotse")
CONTAINER_PREFIX = "sammlungslotse-wi0008-materialize-"


class MaterializationError(RuntimeError):
    """Raised when the synthetic library cannot be materialized safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_child(path: Path, allowed_root: Path = ALLOWED_TEMP_ROOT) -> Path:
    root = allowed_root.resolve(strict=True)
    candidate = path.resolve(strict=False)
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise MaterializationError("target is outside the protected temp root") from exc
    if not relative.parts:
        raise MaterializationError("target must be a child of the protected temp root")
    current = root
    for part in relative.parts[:-1]:
        current /= part
        if current.exists() and _is_link_or_reparse(current):
            raise MaterializationError("target parent contains a link or reparse point")
    if "," in str(candidate):
        raise MaterializationError("target path contains an unsupported comma")
    return candidate


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = path.stat(follow_symlinks=False).st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attributes & 0x400)


def validate_new_target(path: Path, allowed_root: Path = ALLOWED_TEMP_ROOT) -> Path:
    target = _strict_child(path, allowed_root)
    if target.exists():
        raise MaterializationError("target already exists")
    if not target.parent.is_dir() or _is_link_or_reparse(target.parent):
        raise MaterializationError("target parent is unavailable or unsafe")
    return target


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "sammlungslotse/calibre-qualification-library/v1":
        raise MaterializationError("qualification manifest schema differs")
    if value.get("synthetic_only") is not True:
        raise MaterializationError("qualification manifest is not synthetic-only")
    records = value.get("records")
    if not isinstance(records, list) or len(records) < 3:
        raise MaterializationError("qualification manifest requires at least three records")
    expected_ids = list(range(1, len(records) + 1))
    if [record.get("expected_id") for record in records] != expected_ids:
        raise MaterializationError("qualification record IDs must be consecutive")
    for record in records:
        if set(record) != {"authors", "expected_id", "formats", "languages", "title"}:
            raise MaterializationError("qualification record fields differ")
        if not isinstance(record["title"], str) or not record["title"]:
            raise MaterializationError("qualification title differs")
        for field in ("authors", "languages", "formats"):
            if not isinstance(record[field], list):
                raise MaterializationError(f"qualification {field} differs")
        if not record["authors"] or not all(isinstance(item, str) and item for item in record["authors"]):
            raise MaterializationError("qualification authors differ")
        if not all(isinstance(item, str) and item for item in record["languages"]):
            raise MaterializationError("qualification languages differ")
        for item in record["formats"]:
            if set(item) != {"fixture", "sha256"}:
                raise MaterializationError("qualification format fields differ")
            fixture = Path(item["fixture"])
            if fixture.is_absolute() or ".." in fixture.parts or "\\" in item["fixture"]:
                raise MaterializationError("qualification fixture locator differs")
            source = ROOT / fixture
            if not source.is_file() or _is_link_or_reparse(source):
                raise MaterializationError("qualification fixture is unavailable or unsafe")
            if sha256_file(source) != item["sha256"]:
                raise MaterializationError("qualification fixture hash differs")
    return value


def expected_projection(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for record in manifest["records"]:
        result.append(
            {
                "authors": record["authors"],
                "external_record_id": record["expected_id"],
                "formats": sorted(Path(item["fixture"]).suffix.lower().removeprefix(".") for item in record["formats"]),
                "languages": record["languages"],
                "title": record["title"],
            }
        )
    return result


def projection_digest(projection: list[dict[str, Any]]) -> str:
    encoded = json.dumps(projection, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _image_matches(profile: CalibreRuntimeProfile) -> bool:
    result = run_bounded(
        ["podman", "image", "inspect", profile.image["tag"], "--format", "json"],
        timeout=15,
        stdout_limit=131072,
        stderr_limit=65536,
    )
    if result.returncode != 0 or result.timed_out:
        return False
    value = json.loads(result.stdout)[0]
    actual_id = str(value.get("Id", ""))
    if not actual_id.startswith("sha256:"):
        actual_id = f"sha256:{actual_id}"
    return (
        actual_id == profile.image["id"]
        and value.get("Architecture") == "amd64"
        and value.get("Os") == "linux"
        and value.get("Config", {}).get("Entrypoint") == profile.image["entrypoint"]
    )


def _create_arguments(
    name: str,
    library: Path,
    profile: CalibreRuntimeProfile,
    calibre_arguments: list[str],
    fixture: Path | None,
) -> list[str]:
    execution = profile.execution
    arguments = [
        "podman", "create", "--name", name, "--pull=never", "--network", "none", "--http-proxy=false",
        "--read-only", "--read-only-tmpfs=false", "--cap-drop", "all", "--security-opt", "no-new-privileges",
        "--user", execution["user"], "--pids-limit", str(execution["pids_limit"]), "--cpus", execution["cpus"],
        "--memory", str(execution["memory_bytes"]), "--memory-swap", str(execution["memory_swap_bytes"]),
        "--ulimit", "core=0:0", "--ulimit", "nofile=256:256", "--log-driver", "none",
        "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=67108864,mode=1777",
        "--tmpfs", "/config:rw,nosuid,nodev,noexec,size=16777216,mode=1777",
        "--mount", f"type=bind,source={library},target=/library,rw=true",
    ]
    if fixture is not None:
        arguments.extend(("--mount", f"type=bind,source={fixture},target=/input/book{fixture.suffix.lower()},ro=true"))
    arguments.extend(("--entrypoint", "/usr/bin/env", profile.image["id"], "-i"))
    for key, value in profile.execution["environment"].items():
        arguments.append(f"{key}={value}")
    arguments.extend(("calibredb", *calibre_arguments))
    return arguments


def _isolation_matches(value: dict[str, Any], profile: CalibreRuntimeProfile, has_fixture: bool) -> bool:
    host = value.get("HostConfig", {})
    config = value.get("Config", {})
    mounts = {item.get("Destination"): item for item in value.get("Mounts", [])}
    input_mounts = [item for destination, item in mounts.items() if str(destination).startswith("/input/book")]
    image = str(value.get("Image", ""))
    if image and not image.startswith("sha256:"):
        image = f"sha256:{image}"
    return (
        image == profile.image["id"]
        and host.get("NetworkMode") == "none"
        and host.get("ReadonlyRootfs") is True
        and config.get("User") == profile.execution["user"]
        and host.get("Privileged") is False
        and host.get("CapAdd") in (None, [])
        and set(host.get("SecurityOpt") or []) == {"no-new-privileges"}
        and host.get("PidsLimit") == profile.execution["pids_limit"]
        and host.get("Memory") == profile.execution["memory_bytes"]
        and host.get("MemorySwap") == profile.execution["memory_swap_bytes"]
        and mounts.get("/library", {}).get("RW") is True
        and ((has_fixture and len(input_mounts) == 1 and input_mounts[0].get("RW") is False) or (not has_fixture and not input_mounts))
        and config.get("Entrypoint") == ["/usr/bin/env"]
    )


def run_calibre(
    library: Path,
    profile: CalibreRuntimeProfile,
    arguments: list[str],
    fixture: Path | None = None,
) -> bytes:
    name = f"{CONTAINER_PREFIX}{uuid.uuid4().hex[:16]}"
    created = False
    try:
        result = run_bounded(
            _create_arguments(name, library, profile, arguments, fixture),
            timeout=15,
            stdout_limit=4096,
            stderr_limit=131072,
        )
        if result.returncode != 0 or result.timed_out:
            raise MaterializationError("qualification container could not be created")
        created = True
        inspection = run_bounded(
            ["podman", "inspect", name, "--format", "json"],
            timeout=15,
            stdout_limit=262144,
            stderr_limit=65536,
        )
        if inspection.returncode != 0 or inspection.timed_out:
            raise MaterializationError("qualification container inspection failed")
        if not _isolation_matches(json.loads(inspection.stdout)[0], profile, fixture is not None):
            raise MaterializationError("qualification container isolation differs")
        completed = run_bounded(
            ["podman", "start", "--attach", name],
            timeout=60,
            stdout_limit=4 * 1024 * 1024,
            stderr_limit=256 * 1024,
        )
        if completed.returncode != 0 or completed.timed_out or completed.stdout_truncated or completed.stderr_truncated:
            raise MaterializationError("qualification Calibre command failed")
        return completed.stdout if isinstance(completed.stdout, bytes) else completed.stdout.encode("utf-8")
    finally:
        if created:
            removed = run_bounded(
                ["podman", "rm", "--force", name], timeout=15, stdout_limit=4096, stderr_limit=4096
            )
            if removed.returncode != 0 or removed.timed_out:
                raise MaterializationError("qualification container cleanup failed")


def _authors_argument(authors: list[str]) -> str:
    if any("&" in author for author in authors):
        raise MaterializationError("qualification author contains the Calibre separator")
    return " & ".join(authors)


def materialize(
    target: Path,
    *,
    manifest_path: Path = MANIFEST_PATH,
    allowed_root: Path = ALLOWED_TEMP_ROOT,
) -> dict[str, Any]:
    library = validate_new_target(target, allowed_root)
    manifest = load_manifest(manifest_path)
    profile = CalibreRuntimeProfile.load(PROFILE_PATH)
    if manifest["profile_id"] != profile.profile_id or not _image_matches(profile):
        raise MaterializationError("qualification profile or image differs")
    library.mkdir()
    try:
        for record in manifest["records"]:
            formats = record["formats"]
            add = [
                "add", "--with-library", "/library", "--title", record["title"],
                "--authors", _authors_argument(record["authors"]),
            ]
            if record["languages"]:
                add.extend(("--languages", ",".join(record["languages"])))
            if formats:
                fixture = ROOT / formats[0]["fixture"]
                run_calibre(library, profile, [*add, f"/input/book{fixture.suffix.lower()}"], fixture)
                for item in formats[1:]:
                    fixture = ROOT / item["fixture"]
                    run_calibre(
                        library,
                        profile,
                        ["add_format", "--with-library", "/library", str(record["expected_id"]), f"/input/book{fixture.suffix.lower()}"],
                        fixture,
                    )
            else:
                run_calibre(library, profile, [*add, "--empty"])
        raw = run_calibre(
            library,
            profile,
            ["list", "--with-library", "/library", "--for-machine", "--fields", "title,authors,languages,formats", "--sort-by", "id", "--ascending"],
        )
        actual = [book.to_dict() for book in parse_calibre_output(raw)]
        expected = expected_projection(manifest)
        if actual != expected:
            raise MaterializationError("materialized qualification projection differs from its oracle")
        return {
            "book_count": len(actual),
            "image_id": profile.image["id"],
            "manifest_sha256": sha256_file(manifest_path),
            "profile_id": profile.profile_id,
            "projection_sha256": projection_digest(actual),
            "schema": "sammlungslotse/calibre-qualification-materialization/v1",
            "synthetic_only": True,
        }
    except BaseException:
        shutil.rmtree(library, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()
    try:
        print(json.dumps(materialize(args.library, manifest_path=args.manifest), sort_keys=True))
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Materialisierung fehlgeschlagen: {type(exc).__name__}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
