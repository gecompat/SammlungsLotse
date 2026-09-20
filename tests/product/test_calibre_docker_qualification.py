from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "runtime" / "calibre-docker-readonly"


class DockerQualificationTests(unittest.TestCase):
    def test_evidence_is_path_free_and_binds_the_current_preimage(self) -> None:
        value = json.loads((RUNTIME / "qualification.json").read_text(encoding="utf-8"))
        self.assertEqual("WI-0020", value["artifact"])
        self.assertEqual("pass", value["status"])
        self.assertTrue(value["synthetic_only"])
        self.assertEqual(2, value["repetitions"])
        self.assertEqual(2, len(value["projection_sha256"]))
        self.assertEqual(1, len(set(value["projection_sha256"])))
        self.assertFalse(any("\\" in json.dumps(value) for _ in [0]))
        bindings = value["bindings"]
        for name, path in {
            "profile_sha256": RUNTIME / "profile.json",
            "executor_sha256": ROOT / "src" / "sammlungslotse" / "calibre_inventory" / "docker_executor.py",
            "provider_sha256": ROOT / "src" / "sammlungslotse" / "calibre_inventory" / "provider.py",
        }.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), bindings[name])


if __name__ == "__main__":
    unittest.main()
