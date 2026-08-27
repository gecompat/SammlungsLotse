"""Bounded Podman process executor for the WI-0005 adapter."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from .deep_ports import ProcessExecution
from .deep_profile import DeepRuntimeProfile
from .deep_workspace import TaskWorkspace


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stderr: bytes
    stderr_truncated: bool
    stdout: bytes
    stdout_truncated: bool
    timed_out: bool


def _read_limited(pipe: BinaryIO, limit: int, result: dict[str, object]) -> None:
    retained = bytearray()
    truncated = False
    while chunk := pipe.read(8192):
        remaining = limit - len(retained)
        if remaining > 0:
            retained.extend(chunk[:remaining])
        if len(chunk) > max(remaining, 0):
            truncated = True
    result["content"] = bytes(retained)
    result["truncated"] = truncated


def run_bounded(
    arguments: list[str],
    *,
    timeout: float,
    stdout_limit: int,
    stderr_limit: int,
) -> CommandResult:
    process = subprocess.Popen(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None or process.stderr is None:
        process.kill()
        raise RuntimeError("bounded process pipes unavailable")
    stdout: dict[str, object] = {}
    stderr: dict[str, object] = {}
    threads = [
        threading.Thread(
            target=_read_limited,
            args=(process.stdout, stdout_limit, stdout),
            daemon=True,
        ),
        threading.Thread(
            target=_read_limited,
            args=(process.stderr, stderr_limit, stderr),
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=5)
    except BaseException:
        process.kill()
        process.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
        process.stdout.close()
        process.stderr.close()
        raise
    for thread in threads:
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError("bounded output reader did not finish")
    process.stdout.close()
    process.stderr.close()
    return CommandResult(
        returncode=process.returncode,
        stderr=stderr.get("content", b""),
        stderr_truncated=bool(stderr.get("truncated", False)),
        stdout=stdout.get("content", b""),
        stdout_truncated=bool(stdout.get("truncated", False)),
        timed_out=timed_out,
    )


class PodmanExecutor:
    """Runs exactly one digest-bound container without a shell."""

    def __init__(self, profile: DeepRuntimeProfile) -> None:
        self._profile = profile

    def execute(self, workspace: TaskWorkspace) -> ProcessExecution:
        execution = self._profile.execution
        observations: list[str] = []
        process_started = False
        isolation_verified = False
        container_name = f"sammlungslotse-wi0005-{uuid.uuid4().hex[:16]}"
        created = False
        cleanup_complete = True
        result_state = "failed"
        exit_code: int | None = None
        report: bytes | None = None
        try:
            try:
                self._inspect_runtime()
                image = self._inspect_image()
            except FileNotFoundError:
                return ProcessExecution(
                    cleanup_complete=True,
                    exit_code=None,
                    isolation_verified=False,
                    observations=("executor.podman_unavailable",),
                    process_started=False,
                    report=None,
                    state="unavailable",
                )
            except RuntimeError:
                return ProcessExecution(
                    cleanup_complete=True,
                    exit_code=None,
                    isolation_verified=False,
                    observations=("executor.image_unavailable_or_changed",),
                    process_started=False,
                    report=None,
                    state="unavailable",
                )

            create = run_bounded(
                self._create_arguments(container_name, workspace),
                timeout=15,
                stdout_limit=execution["stdout_max_bytes"],
                stderr_limit=execution["stderr_max_bytes"],
            )
            observations.extend(self._output_observations("create", create))
            if create.timed_out or create.returncode != 0:
                result_state = "failed"
            else:
                created = True
                inspection = self._inspect_container(container_name)
                isolation_verified = self._isolation_matches(inspection, image)
                if not isolation_verified:
                    observations.append("executor.isolation_mismatch")
                    result_state = "failed"
                else:
                    start = run_bounded(
                        ["podman", "start", container_name],
                        timeout=15,
                        stdout_limit=execution["stdout_max_bytes"],
                        stderr_limit=execution["stderr_max_bytes"],
                    )
                    process_started = True
                    if start.timed_out:
                        result_state = "timeout"
                    elif start.returncode != 0:
                        observations.extend(self._output_observations("start", start))
                        result_state = "failed"
                    else:
                        completion = self._wait_for_completion(container_name)
                        if completion == "timeout":
                            result_state = "timeout"
                        elif completion != "ready":
                            result_state = "failed"
                        else:
                            copied = self._copy_outputs(container_name, workspace)
                            observations.extend(copied["observations"])
                            exit_code = copied["exit_code"]
                            report = copied["report"]
                            result_state = (
                                "completed"
                                if copied["valid"] and exit_code in {0, 1}
                                else "invalid_report"
                            )
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
            observations.append("executor.internal_failure")
            result_state = "failed"
        finally:
            if created:
                try:
                    removed = run_bounded(
                        ["podman", "rm", "--force", container_name],
                        timeout=15,
                        stdout_limit=execution["stdout_max_bytes"],
                        stderr_limit=execution["stderr_max_bytes"],
                    )
                    cleanup_complete = removed.returncode == 0 and not removed.timed_out
                except (OSError, RuntimeError):
                    cleanup_complete = False
                if not cleanup_complete:
                    result_state = "cleanup_failed"
                    observations.append("executor.container_cleanup_failed")
        return ProcessExecution(
            cleanup_complete=cleanup_complete,
            exit_code=exit_code,
            isolation_verified=isolation_verified,
            observations=tuple(observations),
            process_started=process_started,
            report=report,
            state=result_state,
        )

    def _inspect_runtime(self) -> None:
        execution = self._profile.execution
        result = run_bounded(
            ["podman", "version", "--format", "json"],
            timeout=15,
            stdout_limit=execution["stdout_max_bytes"],
            stderr_limit=execution["stderr_max_bytes"],
        )
        if result.timed_out or result.returncode != 0:
            raise RuntimeError("Podman runtime unavailable")
        value = json.loads(result.stdout)
        if not isinstance(value, dict):
            raise RuntimeError("invalid Podman version result")
        minimum = self._version_tuple(execution["podman_minimum_version"])
        client = value.get("Client", {})
        server = value.get("Server", {})
        if (
            self._version_tuple(str(client.get("Version", ""))) < minimum
            or self._version_tuple(str(server.get("Version", ""))) < minimum
            or server.get("OsArch") != "linux/amd64"
        ):
            raise RuntimeError("Podman runtime differs from the profile")

    @staticmethod
    def _version_tuple(value: str) -> tuple[int, int, int]:
        parts = value.split(".")
        if len(parts) != 3 or any(not part.isdigit() for part in parts):
            raise RuntimeError("unsupported Podman version format")
        return int(parts[0]), int(parts[1]), int(parts[2])

    def _wait_for_completion(self, name: str) -> str:
        execution = self._profile.execution
        deadline = time.monotonic() + float(execution["timeout_seconds"])
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            marker = run_bounded(
                ["podman", "exec", name, "/usr/bin/test", "-f", "/output/complete.json"],
                timeout=max(0.05, min(2.0, remaining)),
                stdout_limit=4096,
                stderr_limit=4096,
            )
            if marker.timed_out:
                if time.monotonic() >= deadline:
                    return "timeout"
                time.sleep(0.1)
                continue
            if marker.returncode == 0:
                return "ready"
            if marker.returncode != 1:
                state = run_bounded(
                    ["podman", "inspect", name, "--format", "{{json .State.Running}}"],
                    timeout=max(0.05, min(2.0, deadline - time.monotonic())),
                    stdout_limit=64,
                    stderr_limit=4096,
                )
                if state.timed_out:
                    if time.monotonic() >= deadline:
                        return "timeout"
                    time.sleep(0.1)
                    continue
                if state.returncode != 0 or state.stdout.strip() != b"true":
                    return "failed"
            time.sleep(0.1)
        return "timeout"

    def _copy_outputs(
        self, name: str, workspace: TaskWorkspace
    ) -> dict[str, object]:
        execution = self._profile.execution
        output_directory = workspace.output_file.parent
        targets = {
            "report": workspace.output_file,
            "stdout": output_directory / "stdout.bin",
            "stderr": output_directory / "stderr.bin",
            "marker": output_directory / "complete.json",
        }
        for key, target in targets.items():
            copied = run_bounded(
                ["podman", "cp", f"{name}:/output/{target.name}", str(target)],
                timeout=15,
                stdout_limit=4096,
                stderr_limit=4096,
            )
            if copied.returncode != 0 or copied.timed_out:
                return {
                    "exit_code": None,
                    "observations": (f"copy.{key}_failed",),
                    "report": None,
                    "valid": False,
                }
        try:
            stdout = self._read_bounded(
                targets["stdout"], int(execution["stdout_max_bytes"]), allow_empty=True
            )
            stderr = self._read_bounded(
                targets["stderr"], int(execution["stderr_max_bytes"]), allow_empty=True
            )
            marker_bytes = self._read_bounded(targets["marker"], 4096)
            marker = json.loads(marker_bytes)
            report = self._read_report(workspace.output_file)
            if (
                set(marker) != {"exit_code", "stdout_truncated", "stderr_truncated"}
                or not isinstance(marker["exit_code"], int)
                or not isinstance(marker["stdout_truncated"], bool)
                or not isinstance(marker["stderr_truncated"], bool)
                or stdout is None
                or stderr is None
                or report is None
            ):
                raise ValueError("invalid completion evidence")
            observations = [
                f"provider.stdout_sha256.{hashlib.sha256(stdout).hexdigest()}",
                f"provider.stderr_sha256.{hashlib.sha256(stderr).hexdigest()}",
            ]
            if marker["stdout_truncated"]:
                observations.append("provider.stdout_truncated")
            if marker["stderr_truncated"]:
                observations.append("provider.stderr_truncated")
            return {
                "exit_code": marker["exit_code"],
                "observations": tuple(observations),
                "report": report,
                "valid": True,
            }
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
            return {
                "exit_code": None,
                "observations": ("copy.invalid_completion_evidence",),
                "report": None,
                "valid": False,
            }

    def _inspect_image(self) -> dict[str, object]:
        execution = self._profile.execution
        result = run_bounded(
            ["podman", "image", "inspect", self._profile.image["tag"], "--format", "json"],
            timeout=15,
            stdout_limit=execution["stdout_max_bytes"],
            stderr_limit=execution["stderr_max_bytes"],
        )
        if result.timed_out or result.returncode != 0:
            raise RuntimeError("image unavailable")
        values = json.loads(result.stdout)
        if not isinstance(values, list) or len(values) != 1:
            raise RuntimeError("ambiguous image inspection")
        image = values[0]
        actual_id = str(image.get("Id", ""))
        if not actual_id.startswith("sha256:"):
            actual_id = f"sha256:{actual_id}"
        if actual_id != self._profile.image["id"]:
            raise RuntimeError("image ID changed")
        config = image.get("Config", {})
        if config.get("Entrypoint") != self._profile.image["entrypoint"]:
            raise RuntimeError("image entrypoint changed")
        if config.get("User") != self._profile.execution["user"]:
            raise RuntimeError("image user changed")
        expected_image_environment = {
            f"{key}={value}"
            for key, value in self._profile.execution["environment"].items()
            if key != "container"
        }
        if set(config.get("Env") or []) != expected_image_environment:
            raise RuntimeError("image environment changed")
        if image.get("Architecture") != "amd64" or image.get("Os") != "linux":
            raise RuntimeError("image platform changed")
        return image

    def _create_arguments(
        self, container_name: str, workspace: TaskWorkspace
    ) -> list[str]:
        execution = self._profile.execution
        arguments = [
            "podman",
            "create",
            "--name",
            container_name,
            "--pull=never",
            "--network",
            execution["network"],
            "--http-proxy=false",
            "--read-only",
            "--read-only-tmpfs=false",
            "--cap-drop",
            "all",
            "--security-opt",
            "no-new-privileges",
            "--user",
            execution["user"],
            "--pids-limit",
            str(execution["pids_limit"]),
            "--cpus",
            execution["cpus"],
            "--memory",
            str(execution["memory_bytes"]),
            "--memory-swap",
            str(execution["memory_swap_bytes"]),
            "--ulimit",
            f"core={execution['ulimit_core']}",
            "--ulimit",
            f"nofile={execution['ulimit_nofile']}",
            "--tmpfs",
            f"/tmp:rw,nosuid,nodev,noexec,size={execution['tmpfs']['/tmp']},mode=1777",
            "--tmpfs",
            f"/output:rw,nosuid,nodev,noexec,size={execution['tmpfs']['/output']},mode=1777",
            "--log-driver",
            execution["log_driver"],
            "--mount",
            f"type=bind,source={workspace.input_file},target=/input/input.epub,ro=true",
        ]
        for name, value in sorted(execution["environment"].items()):
            arguments.extend(["--env", f"{name}={value}"])
        arguments.append(self._profile.image["id"])
        arguments.extend(execution["provider_arguments"])
        return arguments

    def _inspect_container(self, name: str) -> dict[str, object]:
        execution = self._profile.execution
        result = run_bounded(
            ["podman", "inspect", name, "--format", "json"],
            timeout=15,
            stdout_limit=execution["stdout_max_bytes"],
            stderr_limit=execution["stderr_max_bytes"],
        )
        if result.timed_out or result.returncode != 0:
            raise RuntimeError("container inspection failed")
        values = json.loads(result.stdout)
        if not isinstance(values, list) or len(values) != 1:
            raise RuntimeError("ambiguous container inspection")
        return values[0]

    def _isolation_matches(
        self, inspection: dict[str, object], image: dict[str, object]
    ) -> bool:
        execution = self._profile.execution
        host = inspection.get("HostConfig", {})
        config = inspection.get("Config", {})
        cap_drop = host.get("CapDrop") or []
        mounts = inspection.get("Mounts", [])
        input_mounts = [
            item
            for item in mounts
            if item.get("Destination") == "/input/input.epub"
        ]
        tmpfs = host.get("Tmpfs") or {}
        expected_cap_drop = {
            "CAP_CHOWN",
            "CAP_DAC_OVERRIDE",
            "CAP_FOWNER",
            "CAP_FSETID",
            "CAP_KILL",
            "CAP_NET_BIND_SERVICE",
            "CAP_SETFCAP",
            "CAP_SETGID",
            "CAP_SETPCAP",
            "CAP_SETUID",
            "CAP_SYS_CHROOT",
        }
        expected_tmpfs = {
            "/output": "rw,nosuid,nodev,noexec,size=2097152,mode=1777,rprivate,tmpcopyup",
            "/tmp": "rw,nosuid,nodev,noexec,size=16777216,mode=1777,rprivate,tmpcopyup",
        }
        expected_ulimits = {
            ("RLIMIT_CORE", 0, 0),
            ("RLIMIT_NOFILE", 256, 256),
        }
        actual_ulimits = {
            (item.get("Name"), item.get("Soft"), item.get("Hard"))
            for item in (host.get("Ulimits") or [])
        }
        expected_env = {f"{key}={value}" for key, value in execution["environment"].items()}
        actual_image = str(inspection.get("Image", ""))
        if actual_image and not actual_image.startswith("sha256:"):
            actual_image = f"sha256:{actual_image}"
        return (
            actual_image == self._profile.image["id"]
            and host.get("NetworkMode") == "none"
            and host.get("ReadonlyRootfs") is True
            and config.get("User") == execution["user"]
            and host.get("CapAdd") in (None, [])
            and set(cap_drop) == expected_cap_drop
            and set(host.get("SecurityOpt") or []) == {"no-new-privileges"}
            and host.get("Privileged") is False
            and host.get("PidsLimit") == execution["pids_limit"]
            and host.get("Memory") == execution["memory_bytes"]
            and host.get("MemorySwap") == execution["memory_swap_bytes"]
            and host.get("NanoCpus") == 1_000_000_000
            and host.get("LogConfig", {}).get("Type") == "none"
            and len(input_mounts) == 1
            and input_mounts[0].get("RW") is False
            and tmpfs == expected_tmpfs
            and actual_ulimits == expected_ulimits
            and set(config.get("Env") or []) == expected_env
            and config.get("Entrypoint") == self._profile.image["entrypoint"]
            and config.get("Cmd") == execution["provider_arguments"]
            and image.get("Id", "").removeprefix("sha256:")
            == self._profile.image["id"].removeprefix("sha256:")
        )

    def _read_report(self, path: Path) -> bytes | None:
        return self._read_bounded(
            path, int(self._profile.execution["raw_report_max_bytes"])
        )

    @staticmethod
    def _read_bounded(
        path: Path, maximum: int, *, allow_empty: bool = False
    ) -> bytes | None:
        try:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                return None
            minimum = 0 if allow_empty else 1
            if not (minimum <= info.st_size <= maximum):
                return None
            content = path.read_bytes()
            if len(content) != info.st_size:
                return None
            return content
        except OSError:
            return None

    @staticmethod
    def _output_observations(prefix: str, result: CommandResult) -> list[str]:
        observations = [
            f"{prefix}.stdout_sha256.{hashlib.sha256(result.stdout).hexdigest()}",
            f"{prefix}.stderr_sha256.{hashlib.sha256(result.stderr).hexdigest()}",
        ]
        if result.stdout_truncated:
            observations.append(f"{prefix}.stdout_truncated")
        if result.stderr_truncated:
            observations.append(f"{prefix}.stderr_truncated")
        return observations
