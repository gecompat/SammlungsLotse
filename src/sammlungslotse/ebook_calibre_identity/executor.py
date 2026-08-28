"""Exact bounded Calibre single-record export executor for WI-0011."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import uuid
from pathlib import Path
from typing import Any

from sammlungslotse.calibre_inventory.workspace import LibraryWorkspace
from sammlungslotse.ebook_intake.podman_executor import run_bounded

from .ports import RecordExecution
from .profile import CalibreIdentityProfile


CONTAINER_PREFIX = "sammlungslotse-wi0011-"


def _is_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        info = path.stat(follow_symlinks=False)
    except OSError:
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(info, "st_file_attributes", 0) & flag)


class CalibreRecordPodmanExecutor:
    def __init__(self, profile: CalibreIdentityProfile) -> None:
        self.profile = profile

    def execute(self, workspace: LibraryWorkspace, external_record_id: int) -> RecordExecution:
        self.profile.validate_external_record_id(str(external_record_id))
        name = f"{CONTAINER_PREFIX}{uuid.uuid4().hex[:16]}"
        created = False
        process_started = False
        isolated = False
        cleanup = True
        state = "failed"
        exit_code: int | None = None
        data: bytes | None = None
        output_sha256: str | None = None
        output_size: int | None = None
        try:
            self._runtime_and_image()
            if list(workspace.output.iterdir()):
                state = "invalid_report"
            else:
                create = run_bounded(
                    self._create_arguments(name, workspace, external_record_id),
                    timeout=15,
                    stdout_limit=4096,
                    stderr_limit=self.profile.runtime.execution["stderr_max_bytes"],
                )
                if create.timed_out or create.returncode != 0:
                    state = "failed"
                else:
                    created = True
                    isolated = self._isolation_matches(self._inspect_container(name))
                    if not isolated:
                        state = "failed"
                    else:
                        process_started = True
                        completed = run_bounded(
                            ["podman", "start", "--attach", name],
                            timeout=float(self.profile.runtime.execution["timeout_seconds"]),
                            stdout_limit=self.profile.runtime.execution["stdout_max_bytes"],
                            stderr_limit=self.profile.runtime.execution["stderr_max_bytes"],
                        )
                        exit_code = completed.returncode
                        if completed.timed_out:
                            state = "timeout"
                        elif completed.stdout_truncated or completed.stderr_truncated:
                            state = "invalid_report"
                        else:
                            inspected = self._read_output(workspace.output, external_record_id)
                            data = inspected["data"]
                            output_sha256 = inspected["sha256"]
                            output_size = inspected["size_bytes"]
                            if completed.returncode == 0 and data is not None:
                                state = "completed"
                            elif completed.returncode == 0 and inspected["empty"]:
                                state = "selection_unavailable"
                            elif completed.returncode != 0:
                                state = "failed"
                            else:
                                state = "invalid_report"
        except FileNotFoundError:
            state = "unavailable"
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
            state = "unavailable" if not created else "failed"
        finally:
            if created:
                try:
                    removed = run_bounded(
                        ["podman", "rm", "--force", name],
                        timeout=15,
                        stdout_limit=4096,
                        stderr_limit=4096,
                    )
                    cleanup = removed.returncode == 0 and not removed.timed_out
                except (OSError, RuntimeError):
                    cleanup = False
                if not cleanup:
                    state = "cleanup_failed"
                    data = None
                    output_sha256 = None
                    output_size = None
        return RecordExecution(
            cleanup_complete=cleanup,
            data=data if state == "completed" else None,
            exit_code=exit_code,
            isolation_verified=isolated,
            output_sha256=output_sha256 if state == "completed" else None,
            output_size_bytes=output_size if state == "completed" else None,
            process_started=process_started,
            state=state,
        )

    def _runtime_and_image(self) -> None:
        execution = self.profile.runtime.execution
        version = run_bounded(
            ["podman", "version", "--format", "json"],
            timeout=15,
            stdout_limit=65536,
            stderr_limit=65536,
        )
        if version.timed_out or version.returncode != 0:
            raise RuntimeError("runtime unavailable")
        value = json.loads(version.stdout)
        minimum = tuple(int(part) for part in execution["podman_minimum_version"].split("."))
        for area in ("Client", "Server"):
            actual = tuple(int(part) for part in str(value.get(area, {}).get("Version", "")).split("."))
            if len(actual) != 3 or actual < minimum:
                raise RuntimeError("runtime version differs")
        if value.get("Server", {}).get("OsArch") != "linux/amd64":
            raise RuntimeError("runtime platform differs")
        image = run_bounded(
            ["podman", "image", "inspect", self.profile.runtime.image["id"], "--format", "json"],
            timeout=15,
            stdout_limit=131072,
            stderr_limit=65536,
        )
        if image.timed_out or image.returncode != 0:
            raise RuntimeError("image unavailable")
        inspected = json.loads(image.stdout)[0]
        image_id = str(inspected.get("Id", ""))
        if not image_id.startswith("sha256:"):
            image_id = f"sha256:{image_id}"
        if (
            image_id != self.profile.runtime.image["id"]
            or inspected.get("Os") != "linux"
            or inspected.get("Architecture") != "amd64"
            or inspected.get("Config", {}).get("Entrypoint")
            != self.profile.runtime.image["entrypoint"]
        ):
            raise RuntimeError("image differs")

    def _create_arguments(
        self,
        name: str,
        workspace: LibraryWorkspace,
        external_record_id: int,
    ) -> list[str]:
        execution = self.profile.runtime.execution
        maximum = self.profile.limits["max_input_bytes"]
        arguments = [
            "podman",
            "create",
            "--name",
            name,
            "--pull=never",
            "--network",
            "none",
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
            "core=0:0",
            "--ulimit",
            "nofile=256:256",
            "--ulimit",
            f"fsize={maximum}:{maximum}",
            "--log-driver",
            "none",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,noexec,size=67108864,mode=1777",
            "--tmpfs",
            "/config:rw,nosuid,nodev,noexec,size=16777216,mode=1777",
            "--mount",
            f"type=bind,source={workspace.library},target=/library,rw=true",
            "--mount",
            f"type=bind,source={workspace.output},target=/output,rw=true",
            "--entrypoint",
            "/usr/bin/env",
            self.profile.runtime.image["id"],
            "-i",
        ]
        for key, value in execution["environment"].items():
            arguments.append(f"{key}={value}")
        arguments.extend(
            (
                self.profile.command["program"],
                self.profile.command["subcommand"],
                "--with-library",
                "/library",
                "--to-dir",
                "/output",
                *self.profile.command["fixed_flags"],
                str(external_record_id),
            )
        )
        return arguments

    def _inspect_container(self, name: str) -> dict[str, Any]:
        result = run_bounded(
            ["podman", "inspect", name, "--format", "json"],
            timeout=15,
            stdout_limit=262144,
            stderr_limit=65536,
        )
        if result.timed_out or result.returncode != 0:
            raise RuntimeError("container inspection failed")
        return json.loads(result.stdout)[0]

    def _isolation_matches(self, value: dict[str, Any]) -> bool:
        host = value.get("HostConfig", {})
        config = value.get("Config", {})
        mounts = {item.get("Destination"): item for item in value.get("Mounts", [])}
        image = str(value.get("Image", ""))
        if image and not image.startswith("sha256:"):
            image = f"sha256:{image}"
        execution = self.profile.runtime.execution
        return (
            image == self.profile.runtime.image["id"]
            and host.get("NetworkMode") == "none"
            and host.get("ReadonlyRootfs") is True
            and config.get("User") == execution["user"]
            and host.get("Privileged") is False
            and host.get("CapAdd") in (None, [])
            and bool(host.get("CapDrop"))
            and set(host.get("SecurityOpt") or []) == {"no-new-privileges"}
            and host.get("PidsLimit") == execution["pids_limit"]
            and host.get("Memory") == execution["memory_bytes"]
            and host.get("MemorySwap") == execution["memory_swap_bytes"]
            and host.get("NanoCpus") == 1_000_000_000
            and host.get("LogConfig", {}).get("Type") == "none"
            and set((host.get("Tmpfs") or {}).keys()) == {"/config", "/tmp"}
            and mounts.get("/library", {}).get("RW") is True
            and mounts.get("/output", {}).get("RW") is True
            and config.get("Entrypoint") == ["/usr/bin/env"]
        )

    def _read_output(self, output: Path, external_record_id: int) -> dict[str, Any]:
        entries = sorted(output.iterdir(), key=lambda item: item.name)
        if not entries:
            return {"data": None, "empty": True, "sha256": None, "size_bytes": None}
        if len(entries) != 1:
            return {"data": None, "empty": False, "sha256": None, "size_bytes": None}
        path = entries[0]
        if _is_reparse(path) or not path.is_file() or path.name != f"{external_record_id}.epub":
            return {"data": None, "empty": False, "sha256": None, "size_bytes": None}
        before = path.stat(follow_symlinks=False)
        if before.st_size <= 0 or before.st_size > self.profile.limits["max_input_bytes"]:
            return {"data": None, "empty": False, "sha256": None, "size_bytes": None}
        with path.open("rb") as stream:
            data = stream.read(self.profile.limits["max_input_bytes"] + 1)
        after = path.stat(follow_symlinks=False)
        if (
            len(data) > self.profile.limits["max_input_bytes"]
            or len(data) != before.st_size
            or (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns)
        ):
            return {"data": None, "empty": False, "sha256": None, "size_bytes": None}
        digest = hashlib.sha256(data).hexdigest()
        return {"data": bytes(data), "empty": False, "sha256": digest, "size_bytes": len(data)}
