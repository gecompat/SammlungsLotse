from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("exp0022", ROOT / "tools" / "experiments" / "run_exp_0022.py")
assert SPEC and SPEC.loader
exp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exp)

DOCKER = {"docker_image": {"id": "sha256:docker"}}
PODMAN = {"image": {"id": "sha256:podman", "platform": "linux/amd64"}}

class Exp0022Tests(unittest.TestCase):
    def test_normalized_projection_digest_ignores_field_order_but_rejects_paths(self) -> None:
        first = b'[{"id":1,"title":"Synthetic","authors":["Test"],"languages":[],"formats":[]}]'
        second = b'[{"formats":[],"languages":[],"authors":["Test"],"title":"Synthetic","id":1}]'
        self.assertEqual(exp.normalized_projection_digest(first), exp.normalized_projection_digest(second))
        with self.assertRaises(exp.EquivalenceError):
            exp.normalized_projection_digest(b'[{"id":1,"path":"C:/private"}]')

    def test_compare_uses_one_shared_library_and_two_repetitions_per_runtime(self) -> None:
        seen: list[tuple[str, Path]] = []
        def materialize(library: Path, output: Path, profile: dict) -> None:
            (library / "metadata.db").write_bytes(b"synthetic")
        def project(runtime: str):
            def inner(library: Path, output: Path, profile: dict) -> str:
                seen.append((runtime, library))
                return "a" * 64
            return inner
        with tempfile.TemporaryDirectory() as directory:
            result = exp.compare(materialize, project("docker"), project("podman"), DOCKER, PODMAN, root=Path(directory) / "task")
        self.assertEqual("pass", result["status"])
        self.assertEqual(["docker", "docker", "podman", "podman"], [item[0] for item in seen])
        self.assertEqual(1, len({item[1] for item in seen}))
        self.assertNotEqual(result["runtime_bindings"]["docker_image_id"], result["runtime_bindings"]["podman_image_id"])

    def test_missing_runtime_precondition_is_not_qualified(self) -> None:
        def unavailable(*args, **kwargs):
            raise exp.EquivalenceError("unavailable")
        with tempfile.TemporaryDirectory() as directory:
            result = exp.compare(unavailable, unavailable, unavailable, DOCKER, PODMAN, root=Path(directory) / "task")
        self.assertEqual("not_qualified", result["status"])
        self.assertEqual(0, result["repetitions_per_runtime"])

    def test_podman_projection_uses_inspected_container_and_removes_it(self) -> None:
        profile = {"image": {"tag": "local/podman", "id": "sha256:podman", "entrypoint": ["/entry"]}, "execution": {"user": "65532:65532", "pids_limit": 64, "cpus": "1.0", "memory_bytes": 1024, "memory_swap_bytes": 1024, "timeout_seconds": 30, "raw_report_max_bytes": 4096}}
        image = {"Id": "sha256:podman", "Os": "linux", "Architecture": "amd64", "Config": {"Entrypoint": ["/entry"]}}
        container = {"Image": "sha256:podman", "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": sorted(exp.PODMAN_CAP_DROP_ALL), "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Ulimits": [{"Name": "RLIMIT_CORE", "Soft": 0, "Hard": 0}, {"Name": "RLIMIT_NOFILE", "Soft": 256, "Hard": 256}], "Tmpfs": {key: value + exp.PODMAN_TMPFS_SUFFIX for key, value in exp.PODMAN_TMPFS_BASE.items()}, "LogConfig": {"Type": "none"}}, "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        commands: list[list[str]] = []
        with tempfile.TemporaryDirectory() as directory:
            library, output = Path(directory) / "library", Path(directory) / "output"
            library.mkdir(); output.mkdir()
            def mocked(arguments: list[str], **kwargs) -> bytes:
                commands.append(arguments)
                if arguments[1:3] == ["image", "inspect"]:
                    return json.dumps([image]).encode()
                if arguments[1] == "inspect":
                    return json.dumps([container]).encode()
                if arguments[1:3] == ["start", "--attach"]:
                    (output / "report.json").write_bytes(b'[{"id":1,"title":"Synthetic","authors":[],"languages":[],"formats":[]}]')
                return b""
            with patch.object(exp, "_podman", side_effect=mocked):
                digest = exp._podman_projection(library, output, profile)
        self.assertEqual(64, len(digest))
        create = next(command for command in commands if command[1] == "create")
        self.assertIn("type=bind,source=" + str(library) + ",target=/library,rw=true", create)
        self.assertEqual(["podman", "rm", "--force"], commands[-1][:3])

    def test_podman_projection_rejects_capability_or_ulimit_drift(self) -> None:
        profile = {"image": {"tag": "local/podman", "id": "sha256:podman", "entrypoint": ["/entry"]}, "execution": {"user": "65532:65532", "pids_limit": 64, "cpus": "1.0", "memory_bytes": 1024, "memory_swap_bytes": 1024, "timeout_seconds": 30, "raw_report_max_bytes": 4096}}
        image = {"Id": "sha256:podman", "Os": "linux", "Architecture": "amd64", "Config": {"Entrypoint": ["/entry"]}}
        container = {"Image": "sha256:podman", "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": [], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}, {"Name": "nofile", "Soft": 512, "Hard": 512}], "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}}, "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        with tempfile.TemporaryDirectory() as directory:
            library, output = Path(directory) / "library", Path(directory) / "output"
            library.mkdir(); output.mkdir()
            def mocked(arguments: list[str], **kwargs) -> bytes:
                if arguments[1:3] == ["image", "inspect"]:
                    return json.dumps([image]).encode()
                if arguments[1] == "inspect":
                    return json.dumps([container]).encode()
                return b""
            with patch.object(exp, "_podman", side_effect=mocked):
                with self.assertRaisesRegex(exp.EquivalenceError, "isolation_contract"):
                    exp._podman_projection(library, output, profile)

    def test_observed_podman_normalizers_reject_unsafe_additions_or_missing_flags(self) -> None:
        self.assertTrue(exp._podman_capdrop_matches(sorted(exp.PODMAN_CAP_DROP_ALL)))
        self.assertFalse(exp._podman_capdrop_matches([*sorted(exp.PODMAN_CAP_DROP_ALL), "CAP_SYS_ADMIN"]))
        self.assertTrue(exp._podman_ulimits_match([{"Name": "RLIMIT_CORE", "Soft": 0, "Hard": 0}, {"Name": "RLIMIT_NOFILE", "Soft": 256, "Hard": 256}]))
        self.assertFalse(exp._podman_ulimits_match([{"Name": "RLIMIT_CORE", "Soft": 0, "Hard": 0}]))
        observed_tmpfs = {key: value + exp.PODMAN_TMPFS_SUFFIX for key, value in exp.PODMAN_TMPFS_BASE.items()}
        self.assertTrue(exp._podman_tmpfs_matches(observed_tmpfs))
        observed_tmpfs["/tmp"] += ",unsafe"
        self.assertFalse(exp._podman_tmpfs_matches(observed_tmpfs))

if __name__ == "__main__":
    unittest.main()
