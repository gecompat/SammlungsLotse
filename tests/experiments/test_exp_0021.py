from __future__ import annotations

import importlib.util
import json
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
        container = {"Image": "sha256:abc", "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            exp.inspect_isolation("synthetic", PROFILE)
        container["HostConfig"]["NetworkMode"] = "default"
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_isolation("synthetic", PROFILE)

    def test_container_inspection_rejects_missing_cap_drop_and_extra_mount(self) -> None:
        container = {"Image": "sha256:abc", "Config": {"User": "65532:65532", "Entrypoint": ["/entry"]}, "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True, "Privileged": False, "CapAdd": [], "CapDrop": [], "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64, "Memory": 1024, "MemorySwap": 1024, "NanoCpus": 1_000_000_000, "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=67108864,mode=1777", "/config": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}, "LogConfig": {"Type": "none"}}, "Mounts": [{"Destination": "/library", "RW": True}, {"Destination": "/output", "RW": True}]}
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_isolation("synthetic", PROFILE)
        container["HostConfig"]["CapDrop"] = ["ALL"]
        container["Mounts"].append({"Destination": "/unexpected", "RW": False})
        with patch.object(exp, "execute", return_value=json.dumps([container])):
            with self.assertRaises(exp.DockerPreflightError):
                exp.inspect_isolation("synthetic", PROFILE)


if __name__ == "__main__":
    unittest.main()
