from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("exp0021", ROOT / "tools" / "experiments" / "run_exp_0021.py")
assert SPEC is not None and SPEC.loader is not None
exp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exp)

PROFILE = {
    "image": {"tag": "local/test", "id": "sha256:abc", "entrypoint": ["/entry"]},
    "execution": {"user": "65532:65532", "pids_limit": 64, "memory_bytes": 1024, "memory_swap_bytes": 1024},
}


class Exp0021Tests(unittest.TestCase):
    def test_image_requires_local_exact_linux_amd64_contract(self) -> None:
        image = {"Id": "sha256:abc", "Os": "linux", "Architecture": "amd64", "Config": {"Entrypoint": ["/entry"]}}
        with patch.object(exp, "execute", return_value=json.dumps([image])):
            self.assertEqual(image, exp.inspect_image(PROFILE))
        image["Architecture"] = "arm64"
        with patch.object(exp, "execute", return_value=json.dumps([image])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_image(PROFILE)

    def test_container_inspection_rejects_network_or_mount_drift(self) -> None:
        container = {"Image": "sha256:abc", "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}, {"Name": "nofile", "Soft": 256, "Hard": 256}], "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            exp.inspect_isolation("synthetic", PROFILE)
        container["HostConfig"]["NetworkMode"] = "default"
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_isolation("synthetic", PROFILE)
        container["HostConfig"]["CapDrop"] = ["ALL"]
        container["Mounts"].append({"Destination": "/unexpected", "RW": False})
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_isolation("synthetic", PROFILE)

    def test_container_inspection_rejects_missing_cap_drop_and_extra_mount(self) -> None:
        container = {"Image": "sha256:abc", "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": [], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}, {"Name": "nofile", "Soft": 256, "Hard": 256}], "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_isolation("synthetic", PROFILE)

    def test_materializer_uses_a_separate_entrypoint_override_and_cleans_up(self) -> None:
        container = {
            "Image": "sha256:abc", "Config": {"User": "65532:65532", "Entrypoint": ["/usr/bin/env"]},
            "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [],
                "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024,
                "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}, {"Name": "nofile", "Soft": 256, "Hard": 256}], "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}},
            "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}],
        }
        with tempfile.TemporaryDirectory() as directory:
            library, output = Path(directory) / "library", Path(directory) / "output"
            library.mkdir(); output.mkdir()
            commands: list[list[str]] = []
            replies = iter(["created", json.dumps([container]), "", "removed"])
            def mocked_execute(arguments: list[str]) -> str:
                commands.append(arguments)
                return next(replies)
            with patch.object(exp, "execute", side_effect=mocked_execute), patch.object(exp, "execute_attached", return_value=b""):
                exp._materialize_empty_library(library, output, PROFILE)
        create = commands[0]
        self.assertEqual(["docker", "create"], create[:2])
        self.assertIn("--entrypoint", create)
        self.assertEqual("/usr/bin/env", create[create.index("--entrypoint") + 1])
        self.assertIn("calibredb", create)
        mounts = [create[index + 1] for index, value in enumerate(create) if value == "--mount"]
        self.assertEqual(
            [f"type=bind,source={library},target=/library", f"type=bind,source={output},target=/output"], mounts
        )
        self.assertTrue(all("rw=true" not in mount for mount in mounts))
        self.assertEqual(["docker", "rm", "--force"], commands[2][:3])

    def test_ulimit_drift_is_rejected(self) -> None:
        container = {"Image": "sha256:abc", "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}, {"Name": "nofile", "Soft": 512, "Hard": 512}], "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaisesRegex(exp.DockerPreflightError, "isolation_contract"):
                exp.inspect_isolation("synthetic", PROFILE)

    def test_attached_timeout_fails_closed(self) -> None:
        with patch.object(exp.subprocess, "run", side_effect=subprocess.TimeoutExpired(["docker"], 30)):
            with self.assertRaisesRegex(exp.DockerPreflightError, "container_timeout"):
                exp.execute_attached(["docker", "start", "--attach", "synthetic"])

    def test_attached_timeout_removes_the_created_container(self) -> None:
        commands: list[list[str]] = []
        def mocked_execute(arguments: list[str]) -> str:
            commands.append(arguments)
            return "created"
        with patch.object(exp, "execute", side_effect=mocked_execute), patch.object(exp, "inspect_isolation"), patch.object(
            exp, "execute_attached", side_effect=exp.DockerPreflightError("docker_container_timeout")
        ):
            with self.assertRaisesRegex(exp.DockerPreflightError, "container_timeout"):
                exp._run_container("synthetic", ["docker", "create"], PROFILE, entrypoint=["/entry"])
        self.assertEqual(["docker", "rm", "--force", "synthetic"], commands[-1])

    def test_evidence_bindings_are_path_free_and_bind_profile_image_and_runner(self) -> None:
        bindings = exp.evidence_bindings(PROFILE)
        self.assertEqual("sha256:abc", bindings["docker_image_id"])
        self.assertEqual("linux/amd64", bindings["docker_platform"])
        self.assertEqual("docker-synthetic-empty-library-two-exact-entrypoint-projections/v1", bindings["method"])
        self.assertEqual(exp.sha256_file(exp.PROFILE_PATH), bindings["profile_sha256"])
        self.assertEqual(exp.sha256_file(Path(exp.__file__)), bindings["runner_sha256"])
        self.assertTrue(all("\\" not in value for value in bindings.values()))


if __name__ == "__main__":
    unittest.main()
