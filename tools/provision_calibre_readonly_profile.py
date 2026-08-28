#!/usr/bin/env python3
"""Explicitly provision the exact local WI-0007 Calibre image."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "calibre-readonly"
PROFILE_PATH = RUNTIME / "profile.json"


def run(arguments: list[str], timeout: float = 1200) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
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
    if result.returncode != 0:
        raise RuntimeError(f"provisioning command failed: {arguments[:2]}\n{result.stdout[-4000:]}")
    return result


def sha512_file(path: Path) -> str:
    digest = hashlib.sha512()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_image_id(value: str) -> str:
    return value if value.startswith("sha256:") else f"sha256:{value}"


def image(reference: str) -> dict[str, object]:
    return json.loads(run(["podman", "image", "inspect", reference, "--format", "json"]).stdout)[0]


def download(profile: dict[str, object], cache_root: Path) -> Path:
    provider = profile["provider"]
    assert isinstance(provider, dict)
    target = cache_root / "calibre-9.13.0-x86_64.txz"
    expected_size = int(provider["artifact_bytes"])
    expected_digest = str(provider["artifact_sha512"])
    if target.exists():
        if not target.is_file() or target.stat().st_size != expected_size or sha512_file(target) != expected_digest:
            raise RuntimeError("cached Calibre artifact differs from the profile")
        return target
    partial = cache_root / ".calibre-9.13.0-x86_64.txz.part"
    if partial.exists():
        raise RuntimeError("partial Calibre download requires review")
    digest = hashlib.sha512()
    written = 0
    request = urllib.request.Request(str(provider["artifact_url"]), headers={"User-Agent": "SammlungsLotse-WI-0007"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response, partial.open("xb") as output:
            while chunk := response.read(1024 * 1024):
                written += len(chunk)
                if written > expected_size:
                    raise RuntimeError("Calibre download exceeded its bound")
                digest.update(chunk)
                output.write(chunk)
        if written != expected_size or digest.hexdigest() != expected_digest:
            raise RuntimeError("downloaded Calibre artifact differs from the profile")
        partial.replace(target)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return target


def provision(cache_root: Path) -> dict[str, object]:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    cache_root.mkdir(parents=True, exist_ok=True)
    if cache_root.is_symlink() or not cache_root.is_dir():
        raise RuntimeError("cache root must be a real directory")
    archive = download(profile, cache_root)
    base = profile["base_image"]
    run(["podman", "pull", "--platform", "linux/amd64", base["reference"]])
    base_image = image(base["reference"])
    if normalized_image_id(str(base_image["Id"])) != base["config_id"]:
        raise RuntimeError("base image differs from the profile")
    with tempfile.TemporaryDirectory(prefix="wi-0007-build-", dir=cache_root) as name:
        context = Path(name)
        calibre = context / "calibre"
        calibre.mkdir()
        with tarfile.open(archive, "r:xz") as source:
            for member in source.getmembers():
                if member.name.startswith(("/", "\\")) or ".." in Path(member.name).parts or member.isdev() or member.isfifo():
                    raise RuntimeError("Calibre archive contains an unsafe member")
            source.extractall(calibre, filter="data")
        if not (calibre / "calibredb").is_file():
            raise RuntimeError("Calibre archive layout differs")
        shutil.copy2(RUNTIME / "Containerfile", context / "Containerfile")
        shutil.copy2(RUNTIME / "calibre_inventory_wrapper.py", context / "calibre_inventory_wrapper.py")
        run(
            [
                "podman", "build", "--pull=never", "--no-cache", "--timestamp", "0",
                "--tag", profile["image"]["tag"], "--file", str(context / "Containerfile"), str(context),
            ]
        )
    built = image(profile["image"]["tag"])
    actual_id = normalized_image_id(str(built["Id"]))
    result = {
        "actual_image_id": actual_id,
        "artifact_sha512": sha512_file(archive),
        "base_config_id": normalized_image_id(str(base_image["Id"])),
        "expected_image_id": profile["image"]["id"],
        "image_id_matches_profile": actual_id == profile["image"]["id"],
        "profile_id": profile["profile_id"],
    }
    print(json.dumps(result, sort_keys=True))
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
