from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from sammlungslotse.calibre_inventory.docker_profile import DockerCalibreRuntimeProfile


RUNTIME = ROOT / "runtime" / "calibre-docker-readonly"


class DockerPreimageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = json.loads((RUNTIME / "profile.json").read_text(encoding="utf-8"))

    def test_preimage_is_explicitly_unbound_and_runtime_loader_rejects_it(self) -> None:
        self.assertEqual("preimage_unbound", self.profile["profile_state"])
        self.assertIsNone(self.profile["base_image"]["config_id"])
        self.assertIsNone(self.profile["image"]["id"])
        self.assertIsNone(self.profile["image"]["container_environment"])
        with self.assertRaises(ValueError):
            DockerCalibreRuntimeProfile(self.profile).validate()

    def test_preimage_separates_unbound_image_environment_from_fixed_process_environment(self) -> None:
        self.assertIsNone(self.profile["image"]["container_environment"])
        self.assertEqual(
            {
                "CALIBRE_CONFIG_DIRECTORY": "/config",
                "HOME": "/tmp/home",
                "LANG": "C.UTF-8",
                "PATH": "/opt/calibre:/usr/local/bin:/usr/bin:/bin",
                "QT_QPA_PLATFORM": "offscreen",
            },
            self.profile["execution"]["environment"],
        )

    def test_containerfile_has_fixed_noninteractive_docker_shape(self) -> None:
        containerfile = (RUNTIME / "Containerfile").read_text(encoding="utf-8")
        from_references = re.findall(r"^FROM (docker\.io/library/python@sha256:[0-9a-f]{64})$", containerfile, re.MULTILINE)
        self.assertEqual([self.profile["base_image"]["reference"]], from_references)
        self.assertIn("USER 65532:65532", containerfile)
        self.assertIn('ENTRYPOINT ["/usr/bin/env", "-i"', containerfile)
        self.assertIn("CMD []", containerfile)
        self.assertNotIn("podman", containerfile.lower())

    def test_source_assessment_is_bound_to_the_preimage_reference(self) -> None:
        assessment = (RUNTIME / "SOURCE_ASSESSMENT.md").read_text(encoding="utf-8")
        self.assertIn("Status: OBSERVED_PREIMAGE — NICHT QUALIFIZIEREND", assessment)
        self.assertIn(self.profile["base_image"]["reference"].removeprefix("docker.io/library/python@"), assessment)
        self.assertEqual(4, len(re.findall(r"sha256:[0-9a-f]{64}", assessment)))
        self.assertIn("Linux/amd64", assessment)

    def test_wrapper_is_fixed_to_minimal_calibredb_list_contract(self) -> None:
        wrapper = (RUNTIME / "calibre_inventory_wrapper.py").read_text(encoding="utf-8")
        self.assertIn('"list",', wrapper)
        self.assertIn('"title,authors,languages,formats",', wrapper)
        self.assertIn('"--with-library",', wrapper)
        self.assertIn('"/library",', wrapper)
        self.assertNotIn("shell=True", wrapper)

    def test_readme_has_no_provisioning_or_runtime_command(self) -> None:
        readme = (RUNTIME / "README.md").read_text(encoding="utf-8")
        self.assertIn("NICHT AUSFÜHRBAR", readme)
        self.assertNotIn("docker build", readme.lower())
        self.assertNotIn("docker run", readme.lower())


if __name__ == "__main__":
    unittest.main()
