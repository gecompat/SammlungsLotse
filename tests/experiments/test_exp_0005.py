from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "experiments" / "ebook" / "exp-0005" / "execution-profile.json"
RESULT = ROOT / "experiments" / "ebook" / "exp-0005" / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0005.py"


def load_runner():
    specification = importlib.util.spec_from_file_location("run_exp_0005", RUNNER_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class Exp0005ContractTests(unittest.TestCase):
    def test_profile_is_narrow_and_pinned(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        load_runner().validate_profile(profile)
        runtime = profile["container_runtime"]
        self.assertEqual("none", runtime["network"])
        self.assertTrue(runtime["read_only_root"])
        self.assertEqual(runtime["memory_bytes"], runtime["memory_swap_bytes"])

    def test_empirical_result_is_complete(self) -> None:
        if not RESULT.exists():
            self.skipTest("result.json is created by the explicit empirical run")
        result = load_runner().validate_result(RESULT)
        self.assertEqual("pass", result["status"])
        self.assertTrue(result["acceptance"]["repeatable_findings"])


if __name__ == "__main__":
    unittest.main()
