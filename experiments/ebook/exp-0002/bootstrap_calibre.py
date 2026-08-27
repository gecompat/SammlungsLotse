#!/usr/bin/env python3
"""Fetch and verify the pinned calibre distribution during image build."""

from __future__ import annotations

import argparse
import hashlib
import tarfile
import tempfile
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--sha512", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()
    destination = Path(args.destination)
    with tempfile.TemporaryDirectory(prefix="exp-0002-bootstrap-") as temp_name:
        archive = Path(temp_name) / "calibre.txz"
        digest = hashlib.sha512()
        with urllib.request.urlopen(args.url, timeout=180) as response, archive.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != args.sha512:
            raise RuntimeError("calibre distribution SHA-512 mismatch")
        destination.mkdir(parents=True, exist_ok=False)
        with tarfile.open(archive, "r:xz") as source:
            source.extractall(destination, filter="data")
    # The official binary archive does not carry a top-level license file.  Its
    # license is therefore recorded from the official project documentation in
    # the execution profile, while the archive itself remains hash-pinned.
    required = [destination / "calibredb", destination / "calibre"]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"calibre distribution is missing required files: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
