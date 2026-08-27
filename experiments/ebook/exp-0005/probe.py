#!/usr/bin/env python3
"""Container-internal probes for the disposable EXP-0005 qualification."""

from __future__ import annotations

import json
import multiprocessing
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


OUTPUT = Path("/output")


def write_json(name: str, value: object) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def epubcheck() -> int:
    completed = subprocess.run(
        [
            "/opt/java/bin/java",
            "-Djava.io.tmpdir=/tmp",
            "-Xms16m",
            "-Xmx256m",
            "-jar",
            "/opt/epubcheck/epubcheck.jar",
            "/input/input.epub",
            "--json",
            "/output/report.json",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    write_json("control.json", {"command": "epubcheck", "exit_code": completed.returncode})
    return completed.returncode


def tool_version() -> int:
    completed = subprocess.run(
        ["/opt/java/bin/java", "-jar", "/opt/epubcheck/epubcheck.jar", "--version"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=10,
        check=False,
    )
    write_json(
        "tool-version.json",
        {"exit_code": completed.returncode, "output": completed.stdout.strip()[:512]},
    )
    return completed.returncode


def input_write() -> int:
    try:
        with Path("/input/input.epub").open("ab") as stream:
            stream.write(b"forbidden")
    except OSError as error:
        write_json("input-write.json", {"write_succeeded": False, "errno": error.errno})
        return 0
    write_json("input-write.json", {"write_succeeded": True, "errno": None})
    return 17


def network() -> int:
    connection_succeeded = False
    error_type = None
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=0.5):
            connection_succeeded = True
    except OSError as error:
        error_type = type(error).__name__
    write_json(
        "network.json",
        {"connection_succeeded": connection_succeeded, "error_type": error_type},
    )
    return 19 if connection_succeeded else 0


def output_limit() -> int:
    target = OUTPUT / "limit.bin"
    written = 0
    error_number = None
    try:
        with target.open("wb", buffering=0) as stream:
            for _ in range(64):
                stream.write(b"x" * 65536)
                written += 65536
    except OSError as error:
        error_number = error.errno
    finally:
        target.unlink(missing_ok=True)
    write_json(
        "output-limit.json",
        {"attempted_bytes": 4194304, "written_before_limit": written, "errno": error_number},
    )
    return 0 if error_number is not None and written < 4194304 else 23


def memory_limit() -> int:
    allocations: list[bytearray] = []
    try:
        while True:
            block = bytearray(16 * 1024 * 1024)
            block[0] = 1
            allocations.append(block)
    except MemoryError:
        write_json("memory-limit.json", {"memory_error": True, "allocated_blocks": len(allocations)})
        return 42


def _cpu_worker(queue: multiprocessing.Queue) -> None:
    deadline = time.monotonic() + 2.0
    started = time.process_time()
    value = 1
    while time.monotonic() < deadline:
        value = (value * 1103515245 + 12345) & 0x7FFFFFFF
    queue.put(time.process_time() - started)


def cpu_limit() -> int:
    queue: multiprocessing.Queue = multiprocessing.Queue()
    workers = [multiprocessing.Process(target=_cpu_worker, args=(queue,)) for _ in range(4)]
    wall_started = time.monotonic()
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    wall_seconds = time.monotonic() - wall_started
    total_cpu_seconds = sum(queue.get() for _ in workers)
    write_json(
        "cpu-limit.json",
        {
            "workers": len(workers),
            "wall_seconds": round(wall_seconds, 6),
            "total_cpu_seconds": round(total_cpu_seconds, 6),
        },
    )
    return 0 if total_cpu_seconds <= wall_seconds * 1.5 else 29


def environment() -> int:
    allowlist = {"HOME", "JAVA_HOME", "LANG", "PATH"}
    names = sorted(os.environ)
    denied = [name for name in ("EXP0005_HOST_SENTINEL", "GH_TOKEN", "GITHUB_TOKEN") if name in os.environ]
    unexpected = [name for name in names if name not in allowlist]
    write_json(
        "environment.json",
        {"names": names, "denied_present": denied, "unexpected_names": unexpected},
    )
    return 0 if not denied else 31


def timeout_child() -> int:
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(300)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    write_json("timeout-child.json", {"child_started": True, "child_pid": child.pid})
    time.sleep(300)
    return 37


COMMANDS = {
    "epubcheck": epubcheck,
    "tool-version": tool_version,
    "input-write": input_write,
    "network": network,
    "output-limit": output_limit,
    "memory-limit": memory_limit,
    "cpu-limit": cpu_limit,
    "environment": environment,
    "timeout-child": timeout_child,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print("usage: probe.py " + "|".join(sorted(COMMANDS)), file=sys.stderr)
        return 2
    exit_code = COMMANDS[sys.argv[1]]()
    write_json("probe-complete.json", {"exit_code": exit_code})
    # Keep the container alive so the host can copy the bounded tmpfs evidence.
    # The runner terminates this wrapper after observing the completion marker.
    time.sleep(300)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
