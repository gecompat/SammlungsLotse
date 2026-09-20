"""Bounded Docker executor for the separate WI-0020 runtime contract."""

from __future__ import annotations

import json
import uuid

from sammlungslotse.ebook_intake.podman_executor import run_bounded

from .docker_profile import DockerCalibreRuntimeProfile
from .ports import InventoryExecution
from .workspace import LibraryWorkspace


class CalibreDockerExecutor:
    """Runs only a preflight-inspected Docker container; never falls back to Podman."""

    def __init__(self, profile: DockerCalibreRuntimeProfile) -> None:
        self.profile = profile

    def execute(self, workspace: LibraryWorkspace) -> InventoryExecution:
        name = f"sammlungslotse-wi0020-{uuid.uuid4().hex[:16]}"
        created = started = isolated = False
        cleanup = True
        state = "failed"
        exit_code = None
        raw = None
        try:
            self._runtime_and_image()
            created_result = run_bounded(self._create_arguments(name, workspace), timeout=15, stdout_limit=4096, stderr_limit=131072)
            if created_result.timed_out or created_result.returncode != 0:
                return InventoryExecution(True, None, False, False, None, "failed")
            created = True
            isolated = self._isolation_matches(self._inspect_container(name))
            if isolated:
                started = True
                result = run_bounded(["docker", "start", "--attach", name], timeout=float(self.profile.execution["timeout_seconds"]), stdout_limit=int(self.profile.execution["stdout_max_bytes"]), stderr_limit=int(self.profile.execution["stderr_max_bytes"]))
                if result.timed_out:
                    state = "timeout"
                elif result.stdout_truncated or result.stderr_truncated:
                    state = "invalid_report"
                else:
                    exit_code = result.returncode
                    report = workspace.output / "report.json"
                    if exit_code == 0 and report.is_file() and 0 < report.stat().st_size <= int(self.profile.execution["raw_report_max_bytes"]):
                        raw, state = report.read_bytes(), "completed"
                    else:
                        state = "invalid_report" if exit_code == 0 else "failed"
        except (FileNotFoundError, OSError, RuntimeError, ValueError, json.JSONDecodeError):
            state = "unavailable" if not created else "failed"
        finally:
            if created:
                try:
                    removed = run_bounded(["docker", "rm", "--force", name], timeout=15, stdout_limit=4096, stderr_limit=4096)
                    cleanup = removed.returncode == 0 and not removed.timed_out
                except (OSError, RuntimeError):
                    cleanup = False
                if not cleanup:
                    state = "cleanup_failed"
        return InventoryExecution(cleanup, exit_code, isolated, started, raw, state)

    def _runtime_and_image(self) -> None:
        result = run_bounded(["docker", "version", "--format", "json"], timeout=15, stdout_limit=65536, stderr_limit=65536)
        if result.timed_out or result.returncode != 0:
            raise RuntimeError("Docker runtime unavailable")
        value = json.loads(result.stdout)
        minimum = tuple(int(part) for part in self.profile.execution["docker_minimum_version"].split("."))
        for area in ("Client", "Server"):
            parts = str(value.get(area, {}).get("Version", "")).split(".")
            if len(parts) < 3 or not all(part.isdigit() for part in parts[:3]) or tuple(int(part) for part in parts[:3]) < minimum:
                raise RuntimeError("Docker runtime version differs")
        server = value.get("Server", {})
        if server.get("Os") != "linux" or server.get("Arch") != "amd64":
            raise RuntimeError("Docker runtime platform differs")
        image = run_bounded(["docker", "image", "inspect", self.profile.image["tag"], "--format", "json"], timeout=15, stdout_limit=131072, stderr_limit=65536)
        if image.timed_out or image.returncode != 0:
            raise RuntimeError("Docker image unavailable")
        values = json.loads(image.stdout)
        if not isinstance(values, list) or len(values) != 1:
            raise RuntimeError("Docker image inspection differs")
        actual = str(values[0].get("Id", ""))
        if not actual.startswith("sha256:"):
            actual = f"sha256:{actual}"
        if actual != self.profile.image["id"] or values[0].get("Os") != "linux" or values[0].get("Architecture") != "amd64" or values[0].get("Config", {}).get("Entrypoint") != self.profile.image["entrypoint"]:
            raise RuntimeError("Docker image differs")

    def _create_arguments(self, name: str, workspace: LibraryWorkspace) -> list[str]:
        e = self.profile.execution
        return [
            "docker", "create", "--name", name, "--pull=never", "--network=none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", e["user"],
            "--pids-limit", str(e["pids_limit"]), "--cpus", e["cpus"], "--memory", str(e["memory_bytes"]),
            "--memory-swap", str(e["memory_swap_bytes"]), "--ulimit", "core=0:0", "--ulimit", "nofile=256:256",
            "--log-driver", "none", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=67108864,mode=1777",
            "--tmpfs", "/config:rw,nosuid,nodev,noexec,size=16777216,mode=1777",
            "--mount", f"type=bind,source={workspace.library},target=/library",
            "--mount", f"type=bind,source={workspace.output},target=/output", self.profile.image["id"],
        ]

    def _inspect_container(self, name: str) -> dict[str, object]:
        result = run_bounded(["docker", "container", "inspect", name, "--format", "json"], timeout=15, stdout_limit=262144, stderr_limit=65536)
        if result.timed_out or result.returncode != 0:
            raise RuntimeError("Docker container inspection failed")
        values = json.loads(result.stdout)
        if not isinstance(values, list) or len(values) != 1:
            raise RuntimeError("Docker container inspection differs")
        return values[0]

    def _isolation_matches(self, value: dict[str, object]) -> bool:
        host, config = value.get("HostConfig", {}), value.get("Config", {})
        mount_values = value.get("Mounts", [])
        mounts = {item.get("Destination"): item for item in mount_values}
        actual = str(value.get("Image", ""))
        if actual and not actual.startswith("sha256:"):
            actual = f"sha256:{actual}"
        ulimits = {(item.get("Name"), item.get("Soft"), item.get("Hard")) for item in host.get("Ulimits", [])}
        return (
            actual == self.profile.image["id"] and host.get("NetworkMode") == "none" and host.get("ReadonlyRootfs") is True
            and config.get("User") == self.profile.execution["user"] and host.get("Privileged") is False
            and host.get("CapAdd") in (None, []) and set(host.get("CapDrop") or []) == {"ALL"}
            and set(host.get("SecurityOpt") or []) == {"no-new-privileges"} and host.get("PidsLimit") == self.profile.execution["pids_limit"]
            and host.get("Memory") == self.profile.execution["memory_bytes"] and host.get("MemorySwap") == self.profile.execution["memory_swap_bytes"]
            and host.get("NanoCpus") == 1_000_000_000 and host.get("LogConfig", {}).get("Type") == "none"
            and ulimits == {("core", 0, 0), ("nofile", 256, 256)} and set(mounts) == {"/library", "/output"}
            and len(mounts) == len(mount_values) == 2 and mounts.get("/library", {}).get("RW") is True
            and mounts.get("/output", {}).get("RW") is True and config.get("Entrypoint") == self.profile.image["entrypoint"]
            and host.get("Tmpfs") == self.profile.execution["tmpfs"] and config.get("Cmd") == self.profile.execution["provider_arguments"]
            and set(config.get("Env") or []) == set(self.profile.image["container_environment"])
        )
