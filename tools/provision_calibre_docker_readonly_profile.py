#!/usr/bin/env python3
"""Explicitly build an unbound WI-0020 Docker image candidate from a local archive.

This tool is deliberately outside every product path.  It never downloads the
Calibre archive, runs, creates, or starts a container, and it never changes
profile.json.  Its build explicitly disables base-image pulls; an unavailable
base must therefore fail the provision attempt.
It imports only its own task-private OCI exporter archive into the local image
store so that the resulting candidate can be inspected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "calibre-docker-readonly"
PROFILE_PATH = RUNTIME / "profile.json"


class ProvisionError(RuntimeError):
    """Raised when a candidate cannot be built without relaxing the preimage."""


def run(
    arguments: list[str], timeout: float = 1200, *, capture: bool = True, environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.STDOUT if capture else subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        raise ProvisionError("docker_candidate_command_failed")
    return result


def sha512_file(path: Path) -> str:
    digest = hashlib.sha512()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_preimage() -> dict[str, Any]:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if (
        profile.get("profile_state") != "preimage_unbound"
        or profile.get("base_image", {}).get("config_id") is not None
        or profile.get("image", {}).get("id") is not None
        or profile.get("image", {}).get("container_environment") is not None
    ):
        raise ProvisionError("docker_profile_is_not_an_unbound_preimage")
    return profile


def safe_extract_archive(archive: Path, destination: Path) -> str:
    with tarfile.open(archive, "r:xz") as source:
        members = source.getmembers()
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.isdev() or member.isfifo() or member.issym() or member.islnk():
                raise ProvisionError("calibre_archive_has_unsafe_member")
        source.extractall(destination, members=members, filter="data")
    executable = destination / "calibredb"
    if not executable.is_file():
        raise ProvisionError("calibre_archive_layout_differs")
    return sha512_file(archive)


def inspect_image(reference: str) -> dict[str, Any]:
    output = run(["docker", "image", "inspect", reference, "--format", "{{json .}}"]).stdout.strip()
    try:
        value = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ProvisionError("docker_inspect_is_not_json") from exc
    if not isinstance(value, dict):
        raise ProvisionError("docker_inspect_shape_differs")
    return value


def verify_base(base: dict[str, Any], reference: str) -> None:
    if base.get("Os") != "linux" or base.get("Architecture") != "amd64":
        raise ProvisionError("docker_base_platform_differs")
    if not str(base.get("Id", "")).startswith("sha256:"):
        raise ProvisionError("docker_base_id_differs")
    expected_repository, expected_digest = reference.split("@", maxsplit=1)
    aliases = {expected_repository}
    if expected_repository == "docker.io/library/python":
        aliases.update({"library/python", "python"})
    observed = {
        item for item in base.get("RepoDigests", [])
        if isinstance(item, str) and "@" in item
    }
    if not any(item.split("@", maxsplit=1)[0] in aliases and item.split("@", maxsplit=1)[1] == expected_digest for item in observed):
        raise ProvisionError("docker_base_digest_differs")


def verify_containerfile_reference(profile: dict[str, Any]) -> bytes:
    containerfile = (RUNTIME / "Containerfile").read_bytes()
    try:
        decoded = containerfile.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProvisionError("containerfile_is_not_utf8") from exc
    references = re.findall(r"^FROM (docker\.io/library/python@sha256:[0-9a-f]{64})$", decoded, re.MULTILINE)
    if references != [profile["base_image"]["reference"]]:
        raise ProvisionError("containerfile_base_reference_differs")
    return containerfile


def verify_candidate(candidate: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    image = profile["image"]
    config = candidate.get("Config", {})
    environment = config.get("Env")
    command = config.get("Cmd", [])
    if (
        candidate.get("Os") != "linux"
        or candidate.get("Architecture") != "amd64"
        or config.get("User") != "65532:65532"
        or config.get("Entrypoint") != image["entrypoint"]
        or not isinstance(command, list)
        or command != image["command"]
        or not isinstance(environment, list)
        or not all(isinstance(item, str) and "=" in item for item in environment)
        or len(environment) != len(set(environment))
    ):
        raise ProvisionError("docker_candidate_inspect_differs")
    return environment


def canonicalize_context_timestamps(context: Path) -> None:
    """Make every task-private context entry use the BuildKit epoch input."""
    try:
        files: list[Path] = []
        directories: list[Path] = []
        for entry in [context, *context.rglob("*")]:
            metadata = entry.stat(follow_symlinks=False)
            if (
                entry.is_symlink()
                or getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
                or not (stat.S_ISREG(metadata.st_mode) or stat.S_ISDIR(metadata.st_mode))
            ):
                raise ProvisionError("docker_context_has_symlink")
            (files if stat.S_ISREG(metadata.st_mode) else directories).append(entry)
        for entry in [*sorted(files), *sorted(directories, key=lambda value: (len(value.parts), str(value)), reverse=True)]:
            # Symlink and reparse-point entries were rejected above.  Do not
            # pass ``follow_symlinks`` here: Windows' utime implementation
            # does not expose that optional keyword for ordinary paths.
            os.utime(entry, ns=(0, 0))
            if entry.stat(follow_symlinks=False).st_mtime_ns != 0:
                raise ProvisionError("docker_context_timestamp_normalization_failed")
    except ProvisionError:
        raise
    except OSError as exc:
        raise ProvisionError("docker_context_timestamp_normalization_failed") from exc


def verify_exported_image(path: Path) -> None:
    """Require BuildKit's task-private exporter archive before importing it."""
    if not path.is_file() or path.stat().st_size == 0:
        raise ProvisionError("docker_candidate_export_missing")


def provision(archive: Path, cache_root: Path, candidate_tag: str) -> dict[str, Any]:
    profile = load_preimage()
    provider = profile["provider"]
    if not archive.is_file() or archive.is_symlink():
        raise ProvisionError("calibre_archive_is_not_a_regular_file")
    if archive.stat().st_size != provider["artifact_bytes"] or sha512_file(archive) != provider["artifact_sha512"]:
        raise ProvisionError("calibre_archive_differs_from_profile")
    if cache_root.is_symlink() or (cache_root.exists() and not cache_root.is_dir()):
        raise ProvisionError("cache_root_is_not_a_real_directory")
    cache_root.mkdir(parents=True, exist_ok=True)
    containerfile = verify_containerfile_reference(profile)
    wrapper = (RUNTIME / "calibre_inventory_wrapper.py").read_bytes()
    base_reference = profile["base_image"]["reference"]
    base = inspect_image(base_reference)
    verify_base(base, base_reference)
    with tempfile.TemporaryDirectory(prefix="wi-0020-candidate-", dir=cache_root) as temporary:
        context = Path(temporary)
        calibre = context / "calibre"
        calibre.mkdir()
        archive_digest = safe_extract_archive(archive, calibre)
        (context / "Containerfile").write_bytes(containerfile)
        (context / "calibre_inventory_wrapper.py").write_bytes(wrapper)
        canonicalize_context_timestamps(context)
        build_environment = dict(os.environ)
        build_environment["SOURCE_DATE_EPOCH"] = "0"
        exported_image = context / "candidate-image.tar"
        run([
            "docker", "buildx", "build", "--builder", "desktop-linux", "--provenance=false", "--sbom=false",
            "--build-arg", "BUILDKIT_MULTI_PLATFORM=1", "--build-arg", "SOURCE_DATE_EPOCH=0",
            "--no-cache", "--pull=false", "--network=none", "--platform", "linux/amd64",
            "--output", f"type=oci,name={candidate_tag},dest={exported_image},rewrite-timestamp=true",
            "--tag", candidate_tag, "--file", str(context / "Containerfile"), str(context),
        ], capture=False, environment=build_environment)
        verify_exported_image(exported_image)
        run(["docker", "load", "--input", str(exported_image)], capture=False)
    candidate = inspect_image(candidate_tag)
    environment = verify_candidate(candidate, profile)
    candidate_command = candidate["Config"].get("Cmd", [])
    image_id = str(candidate.get("Id", ""))
    if not image_id.startswith("sha256:"):
        raise ProvisionError("docker_candidate_id_differs")
    return {
        "artifact_sha512": archive_digest,
        "candidate_image_id": image_id,
        "candidate_profile_state": "unbound_observation",
        "containerfile_sha256": sha256_bytes(containerfile),
        "context_timestamp_epoch": 0,
        "config_environment_sha256": sha256_json(environment),
        "observed_base_image_id": str(base.get("Id", "")),
        "observed_image": {
            "command": candidate_command,
            "container_environment": environment,
            "entrypoint": candidate["Config"]["Entrypoint"],
            "user": candidate["Config"]["User"],
        },
        "platform": "linux/amd64",
        "profile_id": profile["profile_id"],
        "wrapper_sha256": sha256_bytes(wrapper),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True, help="Explicit local Calibre 9.13.0 archive")
    parser.add_argument("--cache-root", type=Path, required=True, help="Task-private local build directory")
    parser.add_argument("--candidate-tag", required=True, help="Explicit local Docker tag for the unbound candidate")
    arguments = parser.parse_args()
    try:
        print(json.dumps(provision(arguments.archive, arguments.cache_root, arguments.candidate_tag), sort_keys=True))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Provisionierung fehlgeschlagen: {type(exc).__name__}")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
