from __future__ import annotations

import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("docker_provision", ROOT / "tools" / "provision_calibre_docker_readonly_profile.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DockerProvisionerTests(unittest.TestCase):
    def profile(self, *, artifact_bytes: int = 1) -> dict[str, object]:
        return {
            "profile_state": "preimage_unbound",
            "profile_id": "wi-0020-calibre-9.13.0-docker-linux-amd64/v1",
            "provider": {"artifact_bytes": artifact_bytes, "artifact_sha512": "a" * 128},
            "base_image": {"reference": "docker.io/library/python@sha256:" + "b" * 64, "config_id": None},
            "image": {"id": None, "container_environment": None, "entrypoint": ["entry"], "command": []},
        }

    def base(self, profile: dict[str, object]) -> dict[str, object]:
        return {"Id": "sha256:" + "c" * 64, "Os": "linux", "Architecture": "amd64", "RepoDigests": [profile["base_image"]["reference"]]}

    @staticmethod
    def candidate() -> dict[str, object]:
        return {"Id": "sha256:" + "d" * 64, "Os": "linux", "Architecture": "amd64", "Config": {"User": "65532:65532", "Entrypoint": ["entry"], "Cmd": [], "Env": ["A=1"]}}

    def test_preimage_rejects_any_bound_runtime_field(self) -> None:
        with patch.object(MODULE, "PROFILE_PATH") as profile_path:
            profile_path.read_text.return_value = json.dumps({"profile_state": "preimage_unbound", "base_image": {"config_id": "sha256:x"}, "image": {"id": None, "container_environment": None}})
            with self.assertRaises(MODULE.ProvisionError):
                MODULE.load_preimage()

    def test_candidate_inspect_rejects_environment_drift(self) -> None:
        profile = {"image": {"entrypoint": ["entry"], "command": []}}
        candidate = {"Os": "linux", "Architecture": "amd64", "Config": {"User": "65532:65532", "Entrypoint": ["entry"], "Cmd": [], "Env": ["A=1", "A=1"]}}
        with self.assertRaises(MODULE.ProvisionError):
            MODULE.verify_candidate(candidate, profile)

    def test_base_requires_exact_digest_and_linux_amd64(self) -> None:
        with self.assertRaises(MODULE.ProvisionError):
            MODULE.verify_base({"Os": "linux", "Architecture": "amd64", "RepoDigests": []}, "docker.io/library/python@sha256:" + "a" * 64)

    def test_base_accepts_the_equivalent_docker_official_short_name(self) -> None:
        digest = "sha256:" + "a" * 64
        MODULE.verify_base(
            {"Id": "sha256:" + "b" * 64, "Os": "linux", "Architecture": "amd64", "RepoDigests": ["python@" + digest]},
            "docker.io/library/python@" + digest,
        )

    def test_containerfile_reference_must_equal_the_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            (runtime / "Containerfile").write_text("FROM docker.io/library/python@sha256:" + "a" * 64 + "\n", encoding="utf-8")
            profile = self.profile()
            with patch.object(MODULE, "RUNTIME", runtime):
                with self.assertRaises(MODULE.ProvisionError):
                    MODULE.verify_containerfile_reference(profile)

    def test_source_has_no_automatic_network_or_runtime_start(self) -> None:
        source = (ROOT / "tools" / "provision_calibre_docker_readonly_profile.py").read_text(encoding="utf-8")
        self.assertNotIn("urllib", source)
        self.assertNotIn('"pull"', source)
        self.assertNotIn('"run"', source)
        self.assertNotIn('"create"', source)
        self.assertNotIn('"start"', source)
        self.assertIn('"--pull=false"', source)
        self.assertIn('"--network=none"', source)

    def test_wrong_archive_stops_before_docker_inspect_or_build(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "calibre.txz"
            archive.write_bytes(b"x")
            profile = self.profile(artifact_bytes=2)
            with patch.object(MODULE, "load_preimage", return_value=profile), patch.object(MODULE, "inspect_image") as inspect:
                with self.assertRaises(MODULE.ProvisionError):
                    MODULE.provision(archive, Path(temporary) / "cache", "candidate:bound")
            inspect.assert_not_called()

    def test_candidate_build_is_networkless_and_reports_bindable_observation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "calibre.txz"
            archive.write_bytes(b"x")
            profile = self.profile()
            with patch.object(MODULE, "load_preimage", return_value=profile), patch.object(MODULE, "sha512_file", return_value="a" * 128), patch.object(MODULE, "safe_extract_archive", return_value="a" * 128), patch.object(MODULE, "verify_containerfile_reference", return_value=b"FROM docker.io/library/python@sha256:" + b"b" * 64 + b"\n"), patch.object(MODULE, "inspect_image", side_effect=[self.base(profile), self.candidate()]), patch.object(MODULE, "run") as run:
                result = MODULE.provision(archive, Path(temporary) / "cache", "candidate:bound")
            build = run.call_args.args[0]
            self.assertEqual("docker", build[0])
            self.assertEqual("build", build[1])
            self.assertIn("--pull=false", build)
            self.assertIn("--network=none", build)
            self.assertIn("--platform", build)
            self.assertEqual("linux/amd64", build[build.index("--platform") + 1])
            self.assertFalse(run.call_args.kwargs["capture"])
            self.assertEqual("unbound_observation", result["candidate_profile_state"])
            self.assertEqual(["A=1"], result["observed_image"]["container_environment"])
            self.assertEqual(MODULE.sha256_bytes(b"FROM docker.io/library/python@sha256:" + b"b" * 64 + b"\n"), result["containerfile_sha256"])
            self.assertNotIn(str(archive), json.dumps(result))

    def test_unsafe_archive_member_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "unsafe.txz"
            with tarfile.open(archive, "w:xz") as target:
                item = tarfile.TarInfo("../escape")
                item.size = 1
                target.addfile(item, io.BytesIO(b"x"))
            with self.assertRaises(MODULE.ProvisionError):
                MODULE.safe_extract_archive(archive, Path(temporary) / "out")

    def test_archive_requires_calibredb_at_the_bound_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "calibre.txz"
            with tarfile.open(archive, "w:xz") as target:
                item = tarfile.TarInfo("calibredb")
                item.size = 1
                target.addfile(item, io.BytesIO(b"x"))
            destination = Path(temporary) / "calibre"
            destination.mkdir()
            digest = MODULE.safe_extract_archive(archive, destination)
            self.assertEqual(MODULE.sha512_file(archive), digest)
            self.assertTrue((destination / "calibredb").is_file())


if __name__ == "__main__":
    unittest.main()
