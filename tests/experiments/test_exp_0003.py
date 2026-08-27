from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "experiments" / "ebook" / "exp-0003" / "execution-profile.json"
RESULT = ROOT / "experiments" / "ebook" / "exp-0003" / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0003.py"


def load_runner():
    specification = importlib.util.spec_from_file_location("run_exp_0003", RUNNER_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class Exp0003ContractTests(unittest.TestCase):
    def test_profile_is_narrow_pinned_and_explicit_about_ace_risk(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        load_runner().validate_profile(profile)
        self.assertEqual("none", profile["container_runtime"]["network"])
        self.assertFalse(profile["ace_runtime"]["browser_internal_sandbox"])
        self.assertFalse(profile["normalization"]["clean_automation_means_accessibility_conformant"])

    def test_unknown_epubcheck_code_remains_visible(self) -> None:
        runner = load_runner()
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        report = {
            "checker": {"checkerVersion": "5.3.0"},
            "messages": [{"ID": "ZZZ-999", "severity": "WARNING", "message": "synthetic", "locations": []}],
        }
        projection = runner.normalize_epubcheck(report, "synthetic", profile, "0" * 64)
        finding = projection["findings"][0]
        self.assertEqual("ZZZ-999", finding["tool_code"])
        self.assertEqual("unclassified", finding["quality_dimension"])
        self.assertTrue(finding["review_required"])

    def test_runtime_paths_are_cleaned_or_rejected(self) -> None:
        runner = load_runner()
        self.assertEqual("EPUB/chapter.xhtml", runner.clean_internal_path("/input/input.epub/EPUB/chapter.xhtml"))
        with self.assertRaises(RuntimeError):
            runner.clean_internal_path("../private/book.epub")

    def test_empirical_result_is_complete(self) -> None:
        if not RESULT.exists():
            self.skipTest("result.json is created by the explicit empirical run")
        result = load_runner().validate_result(RESULT)
        self.assertEqual(7, len(result["cases"]))


if __name__ == "__main__":
    unittest.main()
