from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "experiments" / "ebook" / "exp-0006" / "execution-profile.json"
RESULT = ROOT / "experiments" / "ebook" / "exp-0006" / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0006.py"


def load_runner():
    specification = importlib.util.spec_from_file_location("run_exp_0006", RUNNER_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class Exp0006ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        cls.manifest, cls.manifest_cases = cls.runner.load_manifest_cases()

    def test_profile_is_narrow_pinned_and_synthetic(self) -> None:
        self.runner.validate_profile(self.profile)
        runtime = self.profile["container_runtime"]
        self.assertEqual("none", runtime["network"])
        self.assertTrue(runtime["read_only_root"])
        self.assertEqual(runtime["memory_bytes"], runtime["memory_swap_bytes"])
        self.assertEqual(2, self.profile["rules"]["repetitions"])
        self.assertEqual(11, len(self.profile["cases"]))

    def test_private_host_path_detection_does_not_self_trigger(self) -> None:
        windows_private = "C:\\" + "Us" + "ers\\person\\item"
        posix_private = "/ho" + "me/person/item"
        self.assertIsNotNone(self.runner.PRIVATE_PATH_PATTERN.search(windows_private))
        self.assertIsNotNone(self.runner.PRIVATE_PATH_PATTERN.search(posix_private))
        self.assertIsNone(
            self.runner.PRIVATE_PATH_PATTERN.search(
                "fixture://TEST-0001/0.2.0/format-unknown/unknown.epub"
            )
        )

    def test_probe_matrix_matches_without_using_expected_as_an_oracle(self) -> None:
        repetition = self.runner.PROBE.run_profile(
            self.profile,
            self.manifest,
            self.runner.CORPUS_ROOT,
        )
        self.assertEqual(11, len(repetition["case_results"]))
        self.assertTrue(
            all(
                case["evaluation"]["matches_expected"]
                for case in repetition["case_results"]
            )
        )
        self.assertTrue(
            all(
                case["resources"]["input_bytes"]
                <= case["resources"]["max_input_bytes"]
                for case in repetition["case_results"]
            )
        )
        self.assertEqual(
            0,
            sum(
                case["deep_tool"]["started"]
                for case in repetition["case_results"]
                if not case["deep_tool_allowed"]
            ),
        )

        row = next(
            item for item in self.profile["cases"] if item["row_key"] == "format-unknown"
        )
        fixture_case = self.manifest_cases[row["source_case_key"]]
        baseline = self.runner.PROBE.evaluate_row(
            row,
            fixture_case,
            self.runner.CORPUS_ROOT,
        )
        altered_row = copy.deepcopy(row)
        altered_row["expected"] = {
            "format_capability": "supported",
            "next_action": "continue_deep_read_only",
            "deep_tool_allowed": True,
            "required_observations": [],
            "required_findings": [],
        }
        altered = self.runner.PROBE.evaluate_row(
            altered_row,
            fixture_case,
            self.runner.CORPUS_ROOT,
        )
        self.assertEqual(
            self.runner.PROBE.semantic_projection([baseline]),
            self.runner.PROBE.semantic_projection([altered]),
        )

    def test_stop_review_and_defer_rows_never_start_deep_tool(self) -> None:
        repetition = self.runner.PROBE.run_profile(
            self.profile,
            self.manifest,
            self.runner.CORPUS_ROOT,
        )
        for case in repetition["case_results"]:
            if not case["deep_tool_allowed"]:
                self.assertFalse(case["deep_tool"]["started"])
        timeout_case = next(
            case
            for case in repetition["case_results"]
            if case["row_key"] == "run-tool-timeout"
        )
        self.assertTrue(timeout_case["deep_tool_allowed"])
        self.assertTrue(timeout_case["deep_tool"]["started"])
        self.assertTrue(timeout_case["deep_tool"]["timed_out"])
        self.assertTrue(timeout_case["deep_tool"]["cleaned"])

    def test_empirical_result_is_complete(self) -> None:
        if not RESULT.exists():
            self.skipTest("result.json is created by the explicit empirical run")
        result = self.runner.validate_result(RESULT)
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))
        self.assertTrue(
            all(
                repetition["environment"] == self.profile["environment_allowlist"]
                for repetition in result["repetitions"]
            )
        )


if __name__ == "__main__":
    unittest.main()
