from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "experiments" / "ebook" / "exp-0002" / "execution-profile.json"
RESULT = ROOT / "experiments" / "ebook" / "exp-0002" / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0002.py"


def load_runner():
    specification = importlib.util.spec_from_file_location("run_exp_0002", RUNNER_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class Exp0002ContractTests(unittest.TestCase):
    def test_profile_is_narrow_and_pinned(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        load_runner().validate_profile(profile)
        self.assertFalse(profile["projection"]["direct_database_access_allowed"])
        self.assertEqual("none", profile["container_runtime"]["network"])

    def test_version_compatibility_fails_closed(self) -> None:
        runner = load_runner()
        self.assertEqual("supported", runner.classify_tool_version("9.13.0", "9.13.0"))
        self.assertEqual("supported", runner.classify_tool_version("9.13", "9.13.0"))
        self.assertEqual("unsupported", runner.classify_tool_version("9.14.0", "9.13.0"))
        self.assertEqual("unsupported", runner.classify_tool_version("calibre 9.13", "9.13.0"))

    def test_empirical_result_is_complete(self) -> None:
        if not RESULT.exists():
            self.skipTest("result.json is created by the explicit empirical run")
        result = load_runner().validate_result(RESULT)
        self.assertEqual(2, len(result["targets"]))


if __name__ == "__main__":
    unittest.main()
