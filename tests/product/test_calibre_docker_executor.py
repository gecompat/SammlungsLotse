from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.calibre_inventory.docker_executor import CalibreDockerExecutor
from sammlungslotse.calibre_inventory.docker_profile import DockerCalibreRuntimeProfile


def profile_data() -> dict[str, object]:
    return {
        "schema": "sammlungslotse/calibre-docker-read-only-runtime-profile/v1",
        "profile_id": "wi-0020-calibre-9.13.0-docker-linux-amd64/v1",
        "base_image": {"reference": "docker.io/library/python@sha256:" + "a" * 64, "config_id": "sha256:" + "b" * 64},
        "provider": {"id": "calibre", "version": "9.13.0", "license_spdx": "GPL-3.0-only", "artifact_bytes": 192554776, "artifact_sha512": "c" * 128, "artifact_url": "https://download.calibre-ebook.com/9.13.0/calibre.txz"},
        "image": {"tag": "sammlungslotse-calibre:wi-0020", "id": "sha256:" + "d" * 64, "platform": "linux/amd64", "entrypoint": ["/usr/bin/env", "-i", "CALIBRE_CONFIG_DIRECTORY=/config", "HOME=/tmp/home", "LANG=C.UTF-8", "PATH=/opt/calibre:/usr/local/bin:/usr/bin:/bin", "QT_QPA_PLATFORM=offscreen", "python", "/opt/adapter/calibre_inventory_wrapper.py"], "command": [], "container_environment": ["CALIBRE_CONFIG_DIRECTORY=/config", "HOME=/tmp/home", "LANG=C.UTF-8", "PATH=/opt/calibre:/usr/local/bin:/usr/bin:/bin", "QT_QPA_PLATFORM=offscreen", "GPG_KEY=upstream-bound", "PYTHON_VERSION=3.12.14", "PYTHON_SHA256=upstream-bound"]},
        "execution": {"network": "none", "user": "65532:65532", "read_only_root": True, "cap_drop": ["ALL"], "no_new_privileges": True, "pids_limit": 64, "cpus": "1.0", "memory_bytes": 1073741824, "memory_swap_bytes": 1073741824, "timeout_seconds": 30, "stdout_max_bytes": 4194304, "stderr_max_bytes": 131072, "raw_report_max_bytes": 4194304, "docker_minimum_version": "29.0.0", "provider_arguments": [], "tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "environment": {"CALIBRE_CONFIG_DIRECTORY": "/config", "HOME": "/tmp/home", "LANG": "C.UTF-8", "PATH": "/opt/calibre:/usr/local/bin:/usr/bin:/bin", "QT_QPA_PLATFORM": "offscreen"}},
        "workspace": {"marker_schema": "sammlungslotse/calibre-read-only-task/v1", "max_children": 64, "max_task_age_seconds": 86400, "max_files": 5000, "max_total_bytes": 2147483648, "max_file_bytes": 536870912, "max_depth": 16, "max_relative_path_bytes": 1024},
    }


class DockerProfileAndExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = DockerCalibreRuntimeProfile(profile_data())
        self.profile.validate()
        self.executor = CalibreDockerExecutor(self.profile)

    def test_profile_rejects_podman_identity_and_missing_docker_version(self) -> None:
        for mutate in (
            lambda value: value.update(profile_id="wi-0007-calibre-podman/v1"),
            lambda value: value["execution"].pop("docker_minimum_version"),
        ):
            value = profile_data()
            mutate(value)
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    DockerCalibreRuntimeProfile(value).validate()

    def test_profile_binds_full_image_environment_separately_from_process_environment(self) -> None:
        self.assertIn("GPG_KEY=upstream-bound", self.profile.image["container_environment"])
        self.assertEqual(
            {
                "CALIBRE_CONFIG_DIRECTORY": "/config",
                "HOME": "/tmp/home",
                "LANG": "C.UTF-8",
                "PATH": "/opt/calibre:/usr/local/bin:/usr/bin:/bin",
                "QT_QPA_PLATFORM": "offscreen",
            },
            self.profile.execution["environment"],
        )
        altered = profile_data()
        altered["image"]["container_environment"].append("UNEXPECTED=bound-only")
        DockerCalibreRuntimeProfile(altered).validate()

    def test_create_arguments_bind_docker_isolation(self) -> None:
        workspace = type("Workspace", (), {"library": Path("C:/task/library"), "output": Path("C:/task/output")})()
        arguments = self.executor._create_arguments("test", workspace)
        self.assertEqual(["docker", "create"], arguments[:2])
        for value in ("--pull=never", "--network=none", "--read-only", "ALL", "no-new-privileges", "--log-driver", "none", self.profile.image["id"]):
            self.assertIn(value, arguments)
        self.assertNotIn("rw=true", "\n".join(arguments))
        self.assertFalse(any(
            argument == "-e" or argument == "--env" or argument == "--env-file"
            or argument.startswith("--env=") or argument.startswith("--env-file=")
            for argument in arguments
        ))
        self.assertNotIn("podman", arguments)

    def test_runtime_preflight_accepts_only_bound_docker(self) -> None:
        version = {"Client": {"Version": "29.8.0"}, "Server": {"Version": "29.8.0", "Os": "linux", "Arch": "amd64"}}
        image = [{"Id": self.profile.image["id"], "Os": "linux", "Architecture": "amd64", "Config": {"Entrypoint": self.profile.image["entrypoint"], "Env": self.profile.image["container_environment"]}}]
        results = [type("Result", (), {"timed_out": False, "returncode": 0, "stdout": json.dumps(value), "stderr": b"", "stdout_truncated": False, "stderr_truncated": False})() for value in (version, image)]
        with patch("sammlungslotse.calibre_inventory.docker_executor.run_bounded", side_effect=results) as run:
            self.executor._runtime_and_image()
        self.assertEqual(["docker", "version", "--format", "json"], run.call_args_list[0].args[0])
        self.assertEqual("docker", run.call_args_list[1].args[0][0])

    def test_runtime_preflight_rejects_image_environment_drift_before_create(self) -> None:
        version = {"Client": {"Version": "29.8.0"}, "Server": {"Version": "29.8.0", "Os": "linux", "Arch": "amd64"}}
        base = {"Id": self.profile.image["id"], "Os": "linux", "Architecture": "amd64", "Config": {"Entrypoint": self.profile.image["entrypoint"], "Env": self.profile.image["container_environment"]}}
        variants = {
            "added": [*self.profile.image["container_environment"], "ADDED=value"],
            "removed": self.profile.image["container_environment"][1:],
            "reordered": list(reversed(self.profile.image["container_environment"])),
            "duplicate": [*self.profile.image["container_environment"], self.profile.image["container_environment"][0]],
        }
        for name, environment in variants.items():
            image = json.loads(json.dumps(base))
            image["Config"]["Env"] = environment
            results = [type("Result", (), {"timed_out": False, "returncode": 0, "stdout": json.dumps(value), "stderr": b"", "stdout_truncated": False, "stderr_truncated": False})() for value in (version, [image])]
            with self.subTest(name=name), patch("sammlungslotse.calibre_inventory.docker_executor.run_bounded", side_effect=results) as run:
                with self.assertRaisesRegex(RuntimeError, "image differs"):
                    self.executor._runtime_and_image()
            self.assertEqual(2, run.call_count)

    def test_runtime_preflight_rejects_an_unbound_image_command(self) -> None:
        version = {"Client": {"Version": "29.8.0"}, "Server": {"Version": "29.8.0", "Os": "linux", "Arch": "amd64"}}
        for command in (["unexpected"], None):
            image = {"Id": self.profile.image["id"], "Os": "linux", "Architecture": "amd64", "Config": {"Entrypoint": self.profile.image["entrypoint"], "Cmd": command, "Env": self.profile.image["container_environment"]}}
            results = [type("Result", (), {"timed_out": False, "returncode": 0, "stdout": json.dumps(value), "stderr": b"", "stdout_truncated": False, "stderr_truncated": False})() for value in (version, [image])]
            with self.subTest(command=command), patch("sammlungslotse.calibre_inventory.docker_executor.run_bounded", side_effect=results):
                with self.assertRaisesRegex(RuntimeError, "image differs"):
                    self.executor._runtime_and_image()

    def test_runtime_preflight_rejects_old_server_before_image(self) -> None:
        version = {"Client": {"Version": "29.8.0"}, "Server": {"Version": "28.9.0", "Os": "linux", "Arch": "amd64"}}
        result = type("Result", (), {"timed_out": False, "returncode": 0, "stdout": json.dumps(version), "stderr": b"", "stdout_truncated": False, "stderr_truncated": False})()
        with patch("sammlungslotse.calibre_inventory.docker_executor.run_bounded", return_value=result) as run:
            with self.assertRaisesRegex(RuntimeError, "version"):
                self.executor._runtime_and_image()
        self.assertEqual(1, run.call_count)

    def test_inspection_requires_all_security_boundaries(self) -> None:
        value = {"Image": self.profile.image["id"], "Config": {"User": "65532:65532", "Entrypoint": self.profile.image["entrypoint"], "Cmd": [], "Env": self.profile.image["container_environment"]}, "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1073741824, "MemorySwap": 1073741824, "NanoCpus": 1000000000, "LogConfig": {"Type": "none"}, "Tmpfs": self.profile.execution["tmpfs"], "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}, {"Name": "nofile", "Soft": 256, "Hard": 256}]}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        self.assertTrue(self.executor._isolation_matches(value))
        omitted_command = json.loads(json.dumps(value))
        del omitted_command["Config"]["Cmd"]
        self.assertTrue(self.executor._isolation_matches(omitted_command))
        for area, key, changed in (("HostConfig", "NetworkMode", "bridge"), ("HostConfig", "Tmpfs", {}), ("Config", "Cmd", ["unexpected"]), ("Config", "Env", [])):
            altered = json.loads(json.dumps(value))
            altered[area][key] = changed
            with self.subTest(key=key):
                self.assertFalse(self.executor._isolation_matches(altered))
        variants = {
            "added": [*self.profile.image["container_environment"], "ADDED=value"],
            "removed": self.profile.image["container_environment"][1:],
            "reordered": list(reversed(self.profile.image["container_environment"])),
            "duplicate": [*self.profile.image["container_environment"], self.profile.image["container_environment"][0]],
        }
        for name, environment in variants.items():
            altered = json.loads(json.dumps(value))
            altered["Config"]["Env"] = environment
            with self.subTest(name=name):
                self.assertFalse(self.executor._isolation_matches(altered))

    def test_execute_removes_untrusted_container_without_starting_it(self) -> None:
        result = type("Result", (), {"timed_out": False, "returncode": 0, "stdout": "", "stderr": b"", "stdout_truncated": False, "stderr_truncated": False})()
        inspection = {"Image": self.profile.image["id"], "HostConfig": {}, "Config": {}, "Mounts": []}
        created = result
        inspected = type("Result", (), {"timed_out": False, "returncode": 0, "stdout": json.dumps([inspection]), "stderr": b"", "stdout_truncated": False, "stderr_truncated": False})()
        removed = result
        workspace = type("Workspace", (), {"library": Path("C:/task/library"), "output": Path("C:/task/output")})()
        with patch.object(self.executor, "_runtime_and_image"), patch("sammlungslotse.calibre_inventory.docker_executor.run_bounded", side_effect=[created, inspected, removed]) as run:
            execution = self.executor.execute(workspace)
        self.assertEqual("failed", execution.state)
        self.assertFalse(execution.process_started)
        commands = [call.args[0][:3] for call in run.call_args_list]
        self.assertEqual(["docker", "create", "--name"], commands[0])
        self.assertEqual(["docker", "container", "inspect"], commands[1])
        self.assertEqual(["docker", "rm", "--force"], commands[2])


if __name__ == "__main__":
    unittest.main()
