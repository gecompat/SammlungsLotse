#!/usr/bin/env python3
"""Fetch and verify the pinned EXP-0005 tool artifacts during image build."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def download(url: str, expected_sha256: str, destination: Path) -> None:
    digest = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=120) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            output.write(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise RuntimeError(f"digest mismatch for {url}: expected {expected_sha256}, got {actual}")


def safe_zip_extract(archive: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            target = (destination / member.filename).resolve()
            if root != target and root not in target.parents:
                raise RuntimeError(f"unsafe ZIP member: {member.filename}")
        source.extractall(destination)


def install(args: argparse.Namespace) -> None:
    destination = Path(args.destination)
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="exp-0005-bootstrap-") as temp_name:
        temp = Path(temp_name)
        jre_archive = temp / "jre.tar.gz"
        epubcheck_archive = temp / "epubcheck.zip"
        download(args.jre_url, args.jre_sha256, jre_archive)
        download(args.epubcheck_url, args.epubcheck_sha256, epubcheck_archive)

        jre_extract = temp / "jre"
        jre_extract.mkdir()
        with tarfile.open(jre_archive, "r:gz") as source:
            source.extractall(jre_extract, filter="data")
        roots = [path for path in jre_extract.iterdir() if path.is_dir()]
        if len(roots) != 1:
            raise RuntimeError("Temurin archive did not contain exactly one root directory")
        shutil.copytree(roots[0], destination / "java", symlinks=True)

        epubcheck_extract = temp / "epubcheck"
        epubcheck_extract.mkdir()
        safe_zip_extract(epubcheck_archive, epubcheck_extract)
        roots = [path for path in epubcheck_extract.iterdir() if path.is_dir()]
        if len(roots) != 1 or not (roots[0] / "epubcheck.jar").is_file():
            raise RuntimeError("EPUBCheck archive layout is not the pinned distribution layout")
        shutil.copytree(roots[0], destination / "epubcheck")

        licenses = destination / "licenses"
        licenses.mkdir()
        epub_license = next((path for path in (destination / "epubcheck").glob("LICENSE*") if path.is_file()), None)
        if epub_license is None:
            raise RuntimeError("EPUBCheck license was not found in the distribution")
        shutil.copy2(epub_license, licenses / "EPUBCheck-LICENSE.md")
        legal = destination / "java" / "legal"
        if not legal.is_dir():
            raise RuntimeError("Temurin legal notices were not found in the distribution")
        shutil.copytree(legal, licenses / "Temurin-legal")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True)
    parser.add_argument("--jre-url", required=True)
    parser.add_argument("--jre-sha256", required=True)
    parser.add_argument("--epubcheck-url", required=True)
    parser.add_argument("--epubcheck-sha256", required=True)
    install(parser.parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
