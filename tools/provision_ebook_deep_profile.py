#!/usr/bin/env python3
"""Explicitly provision the digest-bound local WI-0005 runtime image."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "ebook-deep-readonly"
PROFILE_PATH = RUNTIME / "profile.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def run(arguments: list[str], *, timeout: float = 900) -> subprocess.CompletedProcess[str]:
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
    if completed.returncode != 0:
        raise RuntimeError(
            f"provisioning command failed with exit {completed.returncode}: "
            f"{arguments[0]} {arguments[1]}\n{completed.stdout[-4000:]}"
        )
    return completed


def load_profile() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def download_cached(source: dict[str, Any], cache_root: Path, filename: str) -> Path:
    target = cache_root / filename
    expected = source["artifact_sha256"]
    expected_bytes = source["artifact_bytes"]
    if target.exists():
        if not target.is_file():
            raise RuntimeError(f"cache target is not a regular file: {filename}")
        if target.stat().st_size != expected_bytes or sha256_file(target) != expected:
            raise RuntimeError(f"cached artifact does not match its preimage: {filename}")
        return target

    partial = cache_root / f".{filename}.part"
    if partial.exists():
        raise RuntimeError(f"partial cache artifact requires review: {partial.name}")
    digest = hashlib.sha256()
    written = 0
    request = urllib.request.Request(
        source["artifact_url"], headers={"User-Agent": "SammlungsLotse-WI-0005"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, partial.open(
            "xb"
        ) as output:
            while chunk := response.read(1024 * 1024):
                written += len(chunk)
                if written > expected_bytes:
                    raise RuntimeError(f"download exceeded bound: {filename}")
                digest.update(chunk)
                output.write(chunk)
        if written != expected_bytes or digest.hexdigest() != expected:
            raise RuntimeError(f"downloaded artifact does not match preimage: {filename}")
        partial.replace(target)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return target


def _safe_parts(name: str) -> tuple[str, ...]:
    logical = PurePosixPath(name.replace("\\", "/"))
    if logical.is_absolute() or ".." in logical.parts or not logical.parts:
        raise RuntimeError("archive contains an unsafe member")
    if logical.parts[0].endswith(":"):
        raise RuntimeError("archive contains an unsafe member")
    return logical.parts


def extract_temurin(archive: Path, destination: Path, target_name: str) -> None:
    unpack = destination / f"{target_name}-unpack"
    unpack.mkdir()
    with tarfile.open(archive, "r:gz") as source:
        for member in source.getmembers():
            _safe_parts(member.name)
            if member.isdev() or member.isfifo():
                raise RuntimeError("Temurin archive contains a special file")
        source.extractall(unpack, filter="data")
    roots = [item for item in unpack.iterdir() if item.is_dir()]
    if len(roots) != 1 or not (roots[0] / "bin" / "java").is_file():
        raise RuntimeError("Temurin archive layout differs from the bound preimage")
    if not (roots[0] / "legal").is_dir():
        raise RuntimeError("Temurin legal notices are missing")
    shutil.copytree(roots[0], destination / target_name, symlinks=True)
    shutil.rmtree(unpack)


def extract_epubcheck(archive: Path, destination: Path) -> None:
    unpack = destination / "epubcheck-unpack"
    unpack.mkdir()
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            parts = _safe_parts(member.filename)
            member_mode = member.external_attr >> 16
            if stat.S_IFMT(member_mode) == stat.S_IFLNK:
                raise RuntimeError("EPUBCheck archive contains a symbolic link")
            target = unpack.joinpath(*parts)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open(member) as incoming, target.open("xb") as output:
                shutil.copyfileobj(incoming, output, length=1024 * 1024)
    roots = [item for item in unpack.iterdir() if item.is_dir()]
    if len(roots) != 1 or not (roots[0] / "epubcheck.jar").is_file():
        raise RuntimeError("EPUBCheck archive layout differs from the bound preimage")
    if not any(item.is_file() for item in roots[0].glob("LICENSE*")):
        raise RuntimeError("EPUBCheck license is missing")
    shutil.copytree(roots[0], destination / "epubcheck")
    shutil.rmtree(unpack)


def image_inspection(reference: str) -> dict[str, Any]:
    return json.loads(run(["podman", "image", "inspect", reference, "--format", "json"]).stdout)[0]


def normalized_image_id(value: str) -> str:
    return value if value.startswith("sha256:") else f"sha256:{value}"


def provision(cache_root: Path) -> dict[str, Any]:
    profile = load_profile()
    cache_root.mkdir(parents=True, exist_ok=True)
    if cache_root.is_symlink() or not cache_root.is_dir():
        raise RuntimeError("cache root must be a real directory")

    jre = download_cached(
        profile["runtime"],
        cache_root,
        "OpenJDK21U-jre_x64_linux_hotspot_21.0.12.1_1.tar.gz",
    )
    jdk = download_cached(
        profile["build_runtime"],
        cache_root,
        "OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz",
    )
    epubcheck = download_cached(
        profile["provider"], cache_root, "epubcheck-5.3.0.zip"
    )

    base = profile["base_image"]
    run(["podman", "pull", "--platform", "linux/amd64", base["reference"]])
    base_inspection = image_inspection(base["reference"])
    if normalized_image_id(base_inspection["Id"]) != base["config_id"]:
        raise RuntimeError("base image config differs from the bound preimage")
    if base_inspection["Architecture"] != "amd64" or base_inspection["Os"] != "linux":
        raise RuntimeError("base image platform differs from the bound preimage")

    with tempfile.TemporaryDirectory(prefix="wi-0005-build-", dir=cache_root) as name:
        context = Path(name)
        extract_temurin(jre, context, "java")
        extract_temurin(jdk, context, "build-java")
        extract_epubcheck(epubcheck, context)
        shutil.copy2(RUNTIME / "Containerfile", context / "Containerfile")
        shutil.copy2(
            RUNTIME / "EpubCheckWrapper.java", context / "EpubCheckWrapper.java"
        )
        run(
            [
                "podman",
                "build",
                "--pull=never",
                "--no-cache",
                "--timestamp",
                "0",
                "--tag",
                profile["image"]["tag"],
                "--file",
                str(context / "Containerfile"),
                str(context),
            ]
        )

    image = image_inspection(profile["image"]["tag"])
    actual_id = normalized_image_id(image["Id"])
    expected_id = profile["image"]["id"]
    entrypoint = image["Config"].get("Entrypoint") or []
    if entrypoint != profile["image"]["entrypoint"]:
        raise RuntimeError("built image entrypoint differs from the profile")
    if image["Config"].get("User") != profile["execution"]["user"]:
        raise RuntimeError("built image user differs from the profile")
    result = {
        "actual_image_id": actual_id,
        "architecture": image["Architecture"],
        "base_config_id": normalized_image_id(base_inspection["Id"]),
        "expected_image_id": expected_id,
        "image_id_matches_profile": actual_id == expected_id,
        "os": image["Os"],
        "profile_id": profile["profile_id"],
        "provider_sha256": sha256_file(epubcheck),
        "build_runtime_sha256": sha256_file(jdk),
        "runtime_sha256": sha256_file(jre),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = provision(args.cache_root)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Provisionierung fehlgeschlagen: {type(exc).__name__}")
        return 3
    return 0 if result["image_id_matches_profile"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
