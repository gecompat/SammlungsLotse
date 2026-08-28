"""Exact bounded Podman executor for the WI-0007 Calibre profile."""

from __future__ import annotations

import json
import subprocess
import uuid

from sammlungslotse.ebook_intake.podman_executor import run_bounded

from .ports import InventoryExecution
from .profile import CalibreRuntimeProfile
from .workspace import LibraryWorkspace


class CalibrePodmanExecutor:
    def __init__(self, profile: CalibreRuntimeProfile) -> None:
        self.profile = profile

    def execute(self, workspace: LibraryWorkspace) -> InventoryExecution:
        name = f"sammlungslotse-wi0007-{uuid.uuid4().hex[:16]}"
        created = False
        started = False
        isolated = False
        cleanup = True
        state = "failed"
        exit_code = None
        raw = None
        try:
            self._runtime_and_image()
            created_result = run_bounded(
                self._create_arguments(name, workspace), timeout=15, stdout_limit=4096, stderr_limit=131072
            )
            if created_result.timed_out or created_result.returncode != 0:
                return InventoryExecution(True, None, False, False, None, "failed")
            created = True
            inspection = self._inspect_container(name)
            isolated = self._isolation_matches(inspection)
            if not isolated:
                state = "failed"
            else:
                started = True
                result = run_bounded(
                    ["podman", "start", "--attach", name],
                    timeout=float(self.profile.execution["timeout_seconds"]),
                    stdout_limit=int(self.profile.execution["stdout_max_bytes"]),
                    stderr_limit=int(self.profile.execution["stderr_max_bytes"]),
                )
                if result.timed_out:
                    state = "timeout"
                elif result.stdout_truncated or result.stderr_truncated:
                    state = "invalid_report"
                else:
                    exit_code = result.returncode
                    report = workspace.output / "report.json"
                    if exit_code == 0 and report.is_file() and 0 < report.stat().st_size <= int(self.profile.execution["raw_report_max_bytes"]):
                        raw = report.read_bytes()
                        state = "completed"
                    else:
                        state = "invalid_report" if exit_code == 0 else "failed"
        except (FileNotFoundError, OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.SubprocessError):
            state = "unavailable" if not created else "failed"
        finally:
            if created:
                try:
                    removed = run_bounded(["podman", "rm", "--force", name], timeout=15, stdout_limit=4096, stderr_limit=4096)
                    cleanup = removed.returncode == 0 and not removed.timed_out
                except (OSError, RuntimeError):
                    cleanup = False
                if not cleanup:
                    state = "cleanup_failed"
        return InventoryExecution(cleanup, exit_code, isolated, started, raw, state)

    def _runtime_and_image(self) -> None:
        version = run_bounded(["podman", "version", "--format", "json"], timeout=15, stdout_limit=65536, stderr_limit=65536)
        if version.timed_out or version.returncode != 0:
            raise RuntimeError("runtime unavailable")
        data = json.loads(version.stdout)
        minimum = tuple(int(value) for value in self.profile.execution["podman_minimum_version"].split("."))
        for area in ("Client", "Server"):
            actual = str(data.get(area, {}).get("Version", "")).split(".")
            if len(actual) != 3 or tuple(int(value) for value in actual) < minimum:
                raise RuntimeError("runtime version differs")
        if data.get("Server", {}).get("OsArch") != "linux/amd64":
            raise RuntimeError("runtime platform differs")
        image = run_bounded(["podman", "image", "inspect", self.profile.image["tag"], "--format", "json"], timeout=15, stdout_limit=131072, stderr_limit=65536)
        if image.returncode != 0 or image.timed_out:
            raise RuntimeError("image unavailable")
        value = json.loads(image.stdout)[0]
        actual_id = str(value.get("Id", ""))
        if not actual_id.startswith("sha256:"):
            actual_id = f"sha256:{actual_id}"
        if actual_id != self.profile.image["id"] or value.get("Architecture") != "amd64" or value.get("Os") != "linux":
            raise RuntimeError("image differs")
        if value.get("Config", {}).get("Entrypoint") != self.profile.image["entrypoint"]:
            raise RuntimeError("entrypoint differs")

    def _create_arguments(self, name: str, workspace: LibraryWorkspace) -> list[str]:
        e = self.profile.execution
        args = [
            "podman", "create", "--name", name, "--pull=never", "--network", "none", "--http-proxy=false",
            "--read-only", "--read-only-tmpfs=false", "--cap-drop", "all", "--security-opt", "no-new-privileges",
            "--user", e["user"], "--pids-limit", str(e["pids_limit"]), "--cpus", e["cpus"],
            "--memory", str(e["memory_bytes"]), "--memory-swap", str(e["memory_swap_bytes"]),
            "--ulimit", "core=0:0", "--ulimit", "nofile=256:256", "--log-driver", "none",
            "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=67108864,mode=1777",
            "--tmpfs", "/config:rw,nosuid,nodev,noexec,size=16777216,mode=1777",
            "--mount", f"type=bind,source={workspace.library},target=/library,rw=true",
            "--mount", f"type=bind,source={workspace.output},target=/output,rw=true",
        ]
        args.append(self.profile.image["id"])
        return args

    def _inspect_container(self, name: str) -> dict[str, object]:
        result = run_bounded(["podman", "inspect", name, "--format", "json"], timeout=15, stdout_limit=262144, stderr_limit=65536)
        if result.returncode != 0 or result.timed_out:
            raise RuntimeError("container inspection failed")
        return json.loads(result.stdout)[0]

    def _isolation_matches(self, value: dict[str, object]) -> bool:
        host = value.get("HostConfig", {})
        config = value.get("Config", {})
        mounts = value.get("Mounts", [])
        by_destination = {item.get("Destination"): item for item in mounts}
        image = str(value.get("Image", ""))
        if image and not image.startswith("sha256:"):
            image = f"sha256:{image}"
        return (
            image == self.profile.image["id"]
            and host.get("NetworkMode") == "none"
            and host.get("ReadonlyRootfs") is True
            and config.get("User") == self.profile.execution["user"]
            and host.get("Privileged") is False
            and host.get("CapAdd") in (None, [])
            and set(host.get("SecurityOpt") or []) == {"no-new-privileges"}
            and host.get("PidsLimit") == self.profile.execution["pids_limit"]
            and host.get("Memory") == self.profile.execution["memory_bytes"]
            and host.get("MemorySwap") == self.profile.execution["memory_swap_bytes"]
            and host.get("NanoCpus") == 1_000_000_000
            and by_destination.get("/library", {}).get("RW") is True
            and by_destination.get("/output", {}).get("RW") is True
            and config.get("Entrypoint") == self.profile.image["entrypoint"]
        )
