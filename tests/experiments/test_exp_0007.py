from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0007"
PROFILE = EXPERIMENT / "execution-profile.json"
PROBE = EXPERIMENT / "probe.py"
RESULT = EXPERIMENT / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0007.py"


def load_runner():
    specification = importlib.util.spec_from_file_location("run_exp_0007", RUNNER_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class Exp0007ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_profile_is_frozen_narrow_and_synthetic(self) -> None:
        self.runner.validate_profile(self.profile)
        self.assertEqual(
            ["stream", "materialized", "original_locator"],
            self.profile["rules"]["variants"],
        )
        self.assertEqual(2, self.profile["rules"]["repetitions"])
        self.assertEqual(2, len(self.profile["cases"]))
        self.assertEqual("none", self.profile["container_runtime"]["network"])
        self.assertTrue(self.profile["container_runtime"]["read_only_root"])

    def test_probe_has_no_network_capability(self) -> None:
        source = PROBE.read_text(encoding="utf-8")
        for forbidden in ("import socket", "import urllib", "import requests"):
            self.assertNotIn(forbidden, source)

    def test_driver_controls_bind_and_clean_the_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            workspace = Path(directory) / "workspace"
            result = self.runner.DRIVER.run_profile(
                self.profile,
                probe=PROBE,
                corpus_root=self.runner.CORPUS_ROOT,
                workspace=workspace,
                platform_profile="windows",
            )
        self.assertEqual(12, len(result["positive_runs"]))
        self.assertTrue(self.runner.all_positive_bound(result))
        self.assertTrue(self.runner.prestart_blocked(result))
        self.assertTrue(self.runner.limits_effective(result, self.profile))
        self.assertTrue(self.runner.timeout_cleanup(result))
        self.assertTrue(self.runner.v2_cleanup_complete(result))
        self.assertTrue(self.runner.v3_rejected(result))
        self.assertTrue(result["originals_unchanged"])
        self.assertTrue(result["semantic_repetitions_identical"])

    def test_private_host_path_detection_does_not_self_trigger(self) -> None:
        windows_private = "C:\\" + "Us" + "ers\\person\\item"
        posix_private = "/ho" + "me/person/item"
        self.assertIsNotNone(self.runner.PRIVATE_PATH_PATTERN.search(windows_private))
        self.assertIsNotNone(self.runner.PRIVATE_PATH_PATTERN.search(posix_private))
        self.assertIsNone(
            self.runner.PRIVATE_PATH_PATTERN.search("fixture://TEST-0001/0.2.0/case")
        )

    def test_empirical_result_is_complete(self) -> None:
        if not RESULT.exists():
            self.skipTest("result.json is created by the explicit empirical run")
        frozen = json.loads(RESULT.read_text(encoding="utf-8"))
        if frozen.get("status") == "pending_completion":
            self.skipTest("empirical result is inside its completion gate")
        result = self.runner.validate_result(RESULT)
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))
        classifications = {
            item["variant"]: item["classification"]
            for item in result["profiles"]["windows"]["variant_classifications"]
        }
        self.assertEqual("QUALIFIED", classifications["stream"])
        self.assertEqual("QUALIFIED", classifications["materialized"])
        self.assertEqual("REJECTED", classifications["original_locator"])


if __name__ == "__main__":
    unittest.main()
