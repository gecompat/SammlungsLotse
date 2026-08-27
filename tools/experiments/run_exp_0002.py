#!/usr/bin/env python3
"""Run and validate the disposable synthetic EXP-0002 calibre experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[2]
EXPERIMENT = REPOSITORY / "experiments" / "ebook" / "exp-0002"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
DEFAULT_RESULT = EXPERIMENT / "result.json"
FIXTURES = REPOSITORY / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"


def execute(arguments: list[str], *, timeout: float | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(arguments[:4])}\n{completed.stdout[-4000:]}")
    return completed


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def snapshot_tree(root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {"file_count": len(files), "digest": canonical_digest(files), "files": files}


def load_profile() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def classify_tool_version(actual: str, expected: str) -> str:
    def normalized(value: str) -> tuple[int, int, int] | None:
        match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?", value)
        if not match:
            return None
        return int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)

    return "supported" if normalized(actual) is not None and normalized(actual) == normalized(expected) else "unsupported"


def validate_profile(profile: dict[str, Any]) -> None:
    runtime = profile["container_runtime"]
    if runtime["network"] != "none" or not runtime["read_only_root"]:
        raise RuntimeError("EXP-0002 runtime must be networkless and read-only")
    if runtime["user"] != "65532:65532" or runtime["capabilities"] != []:
        raise RuntimeError("EXP-0002 runtime must be unprivileged and capability-free")
    if runtime["memory_bytes"] != runtime["memory_swap_bytes"]:
        raise RuntimeError("EXP-0002 runtime may not add swap beyond its memory limit")
    projection = profile["projection"]
    if projection["direct_database_access_allowed"] or projection["absolute_paths_allowed"]:
        raise RuntimeError("EXP-0002 projection boundary is too broad")
    if projection.get("local_access_strategy") != "disposable-copy-on-read":
        raise RuntimeError("EXP-0002 must isolate local calibre access through a disposable copy")
    if projection.get("direct_read_only_mount") != "expected-unsupported-calibre-9.13.0":
        raise RuntimeError("EXP-0002 must retain the direct read-only mount finding")
    containerfile = (EXPERIMENT / "Containerfile").read_text(encoding="utf-8")
    if "@sha256:" not in containerfile or ":latest" in containerfile:
        raise RuntimeError("EXP-0002 base image must be digest-pinned")
    if 'ENTRYPOINT ["/usr/bin/env", "-i"' not in containerfile:
        raise RuntimeError("EXP-0002 container process environment is not minimized")


def build_image(profile: dict[str, Any]) -> dict[str, Any]:
    execute(
        [
            "podman",
            "build",
            "--pull=never",
            "--tag",
            profile["image_tag"],
            "--file",
            str(EXPERIMENT / "Containerfile"),
            str(EXPERIMENT),
        ],
        timeout=900,
    )
    inspection = json.loads(execute(["podman", "image", "inspect", profile["image_tag"]]).stdout)[0]
    return {
        "id": inspection["Id"].removeprefix("sha256:"),
        "digest": inspection.get("Digest", "").removeprefix("sha256:") or None,
        "os": inspection["Os"],
        "architecture": inspection["Architecture"],
    }


def security_projection(inspection: dict[str, Any]) -> dict[str, Any]:
    host = inspection["HostConfig"]
    config = inspection["Config"]
    return {
        "network_mode": host.get("NetworkMode"),
        "read_only_root": host.get("ReadonlyRootfs"),
        "user": config.get("User"),
        "cap_add": host.get("CapAdd") or [],
        "cap_drop": host.get("CapDrop") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "pids_limit": host.get("PidsLimit"),
        "memory": host.get("Memory"),
        "memory_swap": host.get("MemorySwap"),
        "cpu_quota": host.get("CpuQuota"),
        "cpu_period": host.get("CpuPeriod"),
        "mounts": [
            {"destination": mount.get("Destination"), "rw": mount.get("RW"), "type": mount.get("Type")}
            for mount in inspection.get("Mounts", [])
        ],
    }


def container_arguments(
    profile: dict[str, Any],
    name: str,
    library: Path,
    output: Path,
    command: list[str],
    *,
    library_read_only: bool,
    fixtures: Path | None = None,
) -> list[str]:
    runtime = profile["container_runtime"]
    arguments = [
        "podman",
        "create",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "all",
        "--security-opt",
        "no-new-privileges",
        "--user",
        runtime["user"],
        "--pids-limit",
        str(runtime["pids_limit"]),
        "--cpus",
        str(runtime["cpus"]),
        "--memory",
        str(runtime["memory_bytes"]),
        "--memory-swap",
        str(runtime["memory_swap_bytes"]),
        "--tmpfs",
        f"/tmp:rw,nosuid,nodev,noexec,size={runtime['tmpfs_bytes']},mode=1777",
        "--tmpfs",
        f"/config:rw,nosuid,nodev,noexec,size={runtime['tmpfs_bytes']},mode=1777",
        "--ulimit",
        f"fsize={runtime['max_output_file_bytes']}:{runtime['max_output_file_bytes']}",
        "--log-driver",
        "none",
        "--mount",
        f"type=bind,source={library},target=/library,ro={'true' if library_read_only else 'false'}",
        "--mount",
        f"type=bind,source={output},target=/output,ro=false",
    ]
    if fixtures is not None:
        arguments.extend(["--mount", f"type=bind,source={fixtures},target=/fixtures,ro=true"])
    return [*arguments, profile["image_tag"], *command]


def run_container(
    profile: dict[str, Any],
    library: Path,
    output: Path,
    command: list[str],
    *,
    library_read_only: bool,
    fixtures: Path | None = None,
    expected_exit_codes: set[int] | None = None,
) -> dict[str, Any]:
    name = f"sammlungslotse-exp0002-{uuid.uuid4().hex[:12]}"
    started = time.monotonic()
    try:
        execute(container_arguments(profile, name, library, output, command, library_read_only=library_read_only, fixtures=fixtures))
        attached = execute(
            ["podman", "start", "--attach", name],
            timeout=profile["container_runtime"]["timeout_seconds"],
            check=False,
        )
        inspection = json.loads(execute(["podman", "inspect", name]).stdout)[0]
        exit_code = int(inspection["State"]["ExitCode"])
        allowed_exit_codes = expected_exit_codes or {0}
        if exit_code not in allowed_exit_codes:
            raise RuntimeError(
                f"EXP-0002 container {command[0]} failed with exit {exit_code}:\n{attached.stdout[-4000:]}"
            )
        diagnostic_class = None
        if "calibre_test_case_sensitivity" in attached.stdout and "Read-only file system" in attached.stdout:
            diagnostic_class = "calibre-library-open-requires-write-probe"
        return {
            "exit_code": exit_code,
            "duration_seconds": round(time.monotonic() - started, 6),
            "diagnostic_class": diagnostic_class,
            "security": security_projection(inspection),
        }
    finally:
        execute(["podman", "rm", "--force", name], check=False)


def records_from_raw(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        records = []
        for source_id, value in raw.items():
            if not isinstance(value, dict):
                raise RuntimeError("unexpected calibre machine record")
            records.append({"_source_id": source_id, **value})
        return records
    if isinstance(raw, list) and all(isinstance(value, dict) for value in raw):
        return list(raw)
    raise RuntimeError("unexpected calibre machine output shape")


def value(record: dict[str, Any], *names: str) -> Any:
    lowered = {str(key).lower(): child for key, child in record.items()}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def normalize_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if isinstance(raw, str):
        return [item.strip() for item in raw.split(",") if item.strip()]
    return [str(raw)]


def normalize_identifiers(raw: Any) -> dict[str, str]:
    if isinstance(raw, dict):
        return {str(key): str(child) for key, child in sorted(raw.items())}
    result = {}
    for item in normalize_list(raw):
        if ":" in item:
            key, child = item.split(":", 1)
            result[key] = child
    return dict(sorted(result.items()))


def normalize_formats(raw: Any) -> list[str]:
    formats = []
    for item in normalize_list(raw):
        suffix = Path(item).suffix.lower().removeprefix(".")
        formats.append(suffix or item.lower())
    return sorted(set(formats))


def normalize_projection(raw_path: Path, target: str, custom_field: str, profile: dict[str, Any]) -> dict[str, Any]:
    raw_text = raw_path.read_text(encoding="utf-8")
    records = records_from_raw(json.loads(raw_text))
    books = []
    for record in records:
        source_id = value(record, "id", "_source_id")
        custom = value(record, f"#{custom_field}", f"*{custom_field}", custom_field)
        books.append(
            {
                "source_record_id": int(source_id) if str(source_id).isdigit() else str(source_id),
                "title": value(record, "title"),
                "authors": normalize_list(value(record, "authors")),
                "languages": normalize_list(value(record, "languages")),
                "tags": normalize_list(value(record, "tags")),
                "identifiers": normalize_identifiers(value(record, "identifiers")),
                "formats": normalize_formats(value(record, "formats")),
                "custom": {custom_field: custom},
            }
        )
    books.sort(key=lambda book: str(book["source_record_id"]))
    projection = {
        "schema_id": profile["projection"]["schema_id"],
        "target_key": target,
        "source": {
            "tool": "calibre",
            "tool_version": profile["tool"]["version"],
            "command_profile": "calibredb-list-minimal/v1",
            "raw_sha256": sha256_file(raw_path),
        },
        "books": books,
    }
    serialized = json.dumps(projection, sort_keys=True)
    if re.search(r"(?:[A-Za-z]:\\\\|/library(?:/|\\\\))", serialized):
        raise RuntimeError("normalized projection contains an absolute library path")
    return projection


def stage_fixtures(raw_root: Path) -> tuple[Path, dict[str, str]]:
    staging = raw_root / "fixture-inputs"
    staging.mkdir()
    sources = {
        "edition.epub": FIXTURES / "identity-multiformat-edition" / "edition.epub",
        "edition.pdf": FIXTURES / "identity-multiformat-edition" / "edition.pdf",
        "contributor-roles.epub": FIXTURES / "metadata-contributor-roles" / "contributor-roles.epub",
        "sample.epub": FIXTURES / "edition-sample-vs-full" / "sample.epub",
        "full.epub": FIXTURES / "edition-sample-vs-full" / "full.epub",
    }
    hashes = {}
    for name, source in sources.items():
        shutil.copy2(source, staging / name)
        hashes[name] = sha256_file(source)
    return staging, hashes


def run(profile: dict[str, Any], result_path: Path, artifact_root: Path) -> dict[str, Any]:
    raw_root = artifact_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_root.mkdir(parents=True, exist_ok=False)
    image = build_image(profile)
    fixture_staging, fixture_hashes = stage_fixtures(raw_root)
    target_results = []
    tool_version = None
    custom_by_target = {
        target: values["custom_fields"][0]
        for target, values in profile["projection"]["target_profiles"].items()
    }
    for index, (target, custom_field) in enumerate(custom_by_target.items()):
        library = raw_root / "libraries" / target
        library.mkdir(parents=True)
        provision_output = raw_root / "provision" / target
        provision_output.mkdir(parents=True)
        provision_run = run_container(
            profile,
            library,
            provision_output,
            ["provision", target],
            library_read_only=False,
            fixtures=fixture_staging,
        )
        before = snapshot_tree(library)
        direct_probe_output = raw_root / "direct-read-only-probe" / target
        direct_probe_output.mkdir(parents=True)
        direct_read_only_probe = run_container(
            profile,
            library,
            direct_probe_output,
            ["project", target, custom_field],
            library_read_only=True,
            expected_exit_codes={1},
        )
        direct_read_only_probe["classification"] = (
            "expected-unsupported"
            if direct_read_only_probe["diagnostic_class"] == "calibre-library-open-requires-write-probe"
            else "unexpected-failure"
        )
        direct_read_only_probe["source_library_unchanged"] = before["digest"] == snapshot_tree(library)["digest"]
        repeats = []
        for repeat in (1, 2):
            working_library = raw_root / "disposable-read-copies" / target / f"run-{repeat}"
            shutil.copytree(library, working_library, copy_function=shutil.copy2)
            working_before = snapshot_tree(working_library)
            output = raw_root / "projection" / target / f"run-{repeat}"
            output.mkdir(parents=True)
            runtime = run_container(
                profile,
                working_library,
                output,
                ["project", target, custom_field],
                library_read_only=False,
            )
            working_after = snapshot_tree(working_library)
            source_after_repeat = snapshot_tree(library)
            projection = normalize_projection(output / "raw-minimal.json", target, custom_field, profile)
            limited = normalize_projection(output / "raw-limited.json", target, custom_field, profile)
            broad_text = (output / "raw-broad.json").read_text(encoding="utf-8")
            control = json.loads((output / "control.json").read_text(encoding="utf-8"))
            repeats.append(
                {
                    "run": repeat,
                    "runtime": runtime,
                    "raw_minimal_sha256": sha256_file(output / "raw-minimal.json"),
                    "raw_broad_sha256": sha256_file(output / "raw-broad.json"),
                    "raw_broad_has_internal_library_path": "/library/" in broad_text,
                    "projection": projection,
                    "projection_sha256": canonical_digest(projection),
                    "limited_source_record_ids": [book["source_record_id"] for book in limited["books"]],
                    "unknown_field": control["unknown_field"],
                    "working_copy_unchanged_after_projection": working_before["digest"] == working_after["digest"],
                    "source_library_unchanged": before["digest"] == source_after_repeat["digest"],
                }
            )
        after = snapshot_tree(library)
        if index == 0:
            version_output = raw_root / "tool-version"
            version_output.mkdir()
            version_run = run_container(
                profile,
                library,
                version_output,
                ["tool-version"],
                library_read_only=True,
            )
            version_value = json.loads((version_output / "tool-version.json").read_text(encoding="utf-8"))
            match = re.search(r"([0-9]+\.[0-9]+(?:\.[0-9]+)?)", version_value["output"])
            reported_version = match.group(1) if match else version_value["output"]
            version_parts = reported_version.split(".")
            normalized_version = reported_version + ".0" if len(version_parts) == 2 else reported_version
            tool_version = {
                "reported": reported_version,
                "normalized": normalized_version,
                "classification": classify_tool_version(reported_version, profile["tool"]["version"]),
                "runtime": version_run,
            }
        target_results.append(
            {
                "target_key": target,
                "custom_field": custom_field,
                "provision": json.loads((provision_output / "provision.json").read_text(encoding="utf-8")),
                "provision_runtime": provision_run,
                "direct_read_only_probe": direct_read_only_probe,
                "snapshot_before": before,
                "snapshot_after": after,
                "library_unchanged_during_read_phase": before["digest"] == after["digest"],
                "repeats": repeats,
            }
        )
    assert tool_version is not None
    acceptance = {
        "tool_version_supported": tool_version["classification"] == "supported",
        "two_targets_separate": {item["target_key"] for item in target_results}
        == {"technical-library", "young-readers-library"},
        "minimal_field_whitelist": all(
            len(repeat["projection"]["books"]) == 2
            for target in target_results
            for repeat in target["repeats"]
        ),
        "standard_projection_path_free": all(
            "/library/" not in json.dumps(repeat["projection"])
            for target in target_results
            for repeat in target["repeats"]
        ),
        "unknown_field_visible": all(
            repeat["unknown_field"]["classification"] in {"unsupported", "bounded_projection"}
            for target in target_results
            for repeat in target["repeats"]
        ),
        "custom_and_missing_values_preserved": all(
            any(book["custom"][target["custom_field"]] not in {None, ""} for book in target["repeats"][0]["projection"]["books"])
            and any(book["custom"][target["custom_field"]] in {None, ""} for book in target["repeats"][0]["projection"]["books"])
            for target in target_results
        ),
        "pagination_bounded": all(
            len(repeat["limited_source_record_ids"]) == 1
            for target in target_results
            for repeat in target["repeats"]
        ),
        "repeatable_projection": all(
            target["repeats"][0]["projection_sha256"] == target["repeats"][1]["projection_sha256"]
            for target in target_results
        ),
        "libraries_unchanged": all(target["library_unchanged_during_read_phase"] for target in target_results),
        "direct_read_only_probe_fail_closed": all(
            target["direct_read_only_probe"]["classification"] == "expected-unsupported"
            and target["direct_read_only_probe"]["source_library_unchanged"]
            for target in target_results
        ),
        "source_isolated_by_disposable_copy": all(
            repeat["working_copy_unchanged_after_projection"]
            and repeat["source_library_unchanged"]
            and any(mount["destination"] == "/library" and mount["rw"] is True for mount in repeat["runtime"]["security"]["mounts"])
            for target in target_results
            for repeat in target["repeats"]
        ),
        "network_and_privilege_boundary": all(
            repeat["runtime"]["security"]["network_mode"] == "none"
            and repeat["runtime"]["security"]["read_only_root"] is True
            and repeat["runtime"]["security"]["user"] == profile["container_runtime"]["user"]
            and repeat["runtime"]["security"]["cap_add"] == []
            for target in target_results
            for repeat in target["repeats"]
        ),
        "no_direct_database_contract": profile["projection"]["direct_database_access_allowed"] is False,
    }
    result = {
        "schema_version": 1,
        "experiment": "EXP-0002",
        "status": "pass" if all(acceptance.values()) else "fail",
        "executed_on": date.today().isoformat(),
        "profile_id": profile["profile_id"],
        "profile_sha256": sha256_file(PROFILE_PATH),
        "fixture_ref": profile["fixture_ref"],
        "fixture_version": profile["fixture_version"],
        "fixture_input_sha256": fixture_hashes,
        "runtime": {
            "provider": "podman",
            "client_version": execute(["podman", "version", "--format", "{{.Client.Version}}"], check=False).stdout.strip(),
            "server_version": execute(["podman", "version", "--format", "{{.Server.Version}}"], check=False).stdout.strip(),
            "host_os": platform.system(),
            "container_os": image["os"],
            "architecture": image["architecture"],
        },
        "image": image,
        "tool": profile["tool"],
        "tool_version": tool_version,
        "acceptance": acceptance,
        "targets": target_results,
        "raw_evidence": {
            "retention": "local artifact outside Git",
            "content_sha256": canonical_digest(
                [
                    {
                        "target": target["target_key"],
                        "before": target["snapshot_before"]["digest"],
                        "after": target["snapshot_after"]["digest"],
                        "repeats": [repeat["raw_minimal_sha256"] for repeat in target["repeats"]],
                    }
                    for target in target_results
                ]
            ),
        },
        "limitations": [
            "The two calibre libraries are synthetic materialized experiment inputs, not product fixtures or private collections.",
            "The content-server variant was not run; only the documented local calibredb interface was qualified.",
            "Calibre 9.13.0 probes library filesystem case sensitivity during local open, so a direct read-only mount fails closed; successful local projections used independent disposable copies while the source snapshots remained unmounted and byte-identical.",
            "The result qualifies calibre 9.13.0 exactly and classifies other versions as unsupported pending a new profile.",
            "Absolute /library paths occur in retained raw format fields and are removed from the standard projection.",
        ],
    }
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def validate_result(path: Path) -> dict[str, Any]:
    profile = load_profile()
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("experiment") != "EXP-0002" or result.get("status") != "pass":
        raise RuntimeError("EXP-0002 result is not a pass")
    if not all(result.get("acceptance", {}).values()) or len(result["acceptance"]) != 13:
        raise RuntimeError("EXP-0002 acceptance set is incomplete")
    if result.get("profile_sha256") != sha256_file(PROFILE_PATH) or result.get("profile_id") != profile["profile_id"]:
        raise RuntimeError("EXP-0002 result does not match the active profile")
    if result.get("fixture_version") != profile["fixture_version"] or len(result.get("targets", [])) != 2:
        raise RuntimeError("EXP-0002 fixture or target set is incomplete")
    if any(not target["library_unchanged_during_read_phase"] for target in result["targets"]):
        raise RuntimeError("an EXP-0002 library changed during the read phase")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--artifact-root", type=Path, default=Path("C:/rep/artifacts/SammlungsLotse/exp-0002"))
    args = parser.parse_args()
    profile = load_profile()
    validate_profile(profile)
    if args.validate_profile and not args.validate_result:
        print(f"EXP-0002 profile valid: {profile['profile_id']}")
        return 0
    result = validate_result(args.result) if args.validate_result else run(profile, args.result, args.artifact_root)
    print(f"EXP-0002 {result['status']}: {sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
