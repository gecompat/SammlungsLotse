from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import BinaryIO


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def read_bounded(stream: BinaryIO, limit: int) -> bytes:
    payload = stream.read(limit + 1)
    if len(payload) > limit:
        raise RuntimeError("input_limit_exceeded")
    return payload


def inspect_payload(payload: bytes) -> dict[str, object]:
    return {
        "schema_version": 1,
        "received_sha256": hashlib.sha256(payload).hexdigest(),
        "received_size_bytes": len(payload),
    }


def wait_for_file(path: Path, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            return
        time.sleep(0.01)
    raise RuntimeError("coordination_timeout")


def load_payload(args: argparse.Namespace) -> bytes:
    if args.stdin:
        return read_bounded(sys.stdin.buffer, args.max_input_bytes)
    if args.input is None:
        raise RuntimeError("input_required")
    with args.input.open("rb") as stream:
        return read_bounded(stream, args.max_input_bytes)


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--stdin", action="store_true")
    source.add_argument("--input", type=Path)
    parser.add_argument("--max-input-bytes", type=int, required=True)
    parser.add_argument(
        "--mode",
        choices=(
            "inspect",
            "fail",
            "stdout-overflow",
            "stderr-overflow",
            "child-timeout",
            "coordinated-inspect",
        ),
        default="inspect",
    )
    parser.add_argument("--pid-file", type=Path)
    parser.add_argument("--ready-file", type=Path)
    parser.add_argument("--continue-file", type=Path)
    parser.add_argument("--overflow-bytes", type=int, default=0)
    args = parser.parse_args()

    if args.mode == "coordinated-inspect":
        if args.ready_file is None or args.continue_file is None:
            raise RuntimeError("coordination_files_required")
        args.ready_file.write_text("ready\n", encoding="ascii")
        wait_for_file(args.continue_file, 5.0)

    payload = load_payload(args)

    if args.mode == "fail":
        sys.stderr.write("synthetic_provider_failure\n")
        return 17
    if args.mode == "stdout-overflow":
        sys.stdout.write("X" * args.overflow_bytes)
        return 0
    if args.mode == "stderr-overflow":
        sys.stderr.write("X" * args.overflow_bytes)
        return 0
    if args.mode == "child-timeout":
        if args.pid_file is None:
            raise RuntimeError("pid_file_required")
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        args.pid_file.write_text(f"{child.pid}\n", encoding="ascii")
        time.sleep(60)
        return 0

    sys.stdout.write(canonical_json(inspect_payload(payload)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
