"""Current repository tests for historically frozen experiment evidence."""

from __future__ import annotations

import unittest

from tools.experiments import validate_exp_0009_result
from tools.experiments import validate_exp_0010_result
from tools.experiments import validate_exp_0011_result
from tools.experiments import validate_exp_0012_result
from tools.experiments import validate_exp_0013_result
from tools.experiments import validate_exp_0014_result
from tools.experiments import validate_exp_0015_result
from tools.experiments import validate_exp_0016_result


class HistoricalExperimentResultTests(unittest.TestCase):
    def test_exp_0009_result_against_historical_preimage(self) -> None:
        result = validate_exp_0009_result.validate(
            validate_exp_0009_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))

    def test_exp_0010_result_against_historical_preimage(self) -> None:
        result = validate_exp_0010_result.validate(
            validate_exp_0010_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))

    def test_exp_0011_result_against_historical_preimage(self) -> None:
        result = validate_exp_0011_result.validate(
            validate_exp_0011_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))

    def test_exp_0012_result_against_historical_preimage(self) -> None:
        result = validate_exp_0012_result.validate(
            validate_exp_0012_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))

    def test_exp_0013_result_against_historical_preimage(self) -> None:
        result = validate_exp_0013_result.validate(
            validate_exp_0013_result.RESULT_PATH
        )
        self.assertEqual("not_qualified", result["status"])
        self.assertEqual(3, result["input_count"])
        self.assertEqual(3, result["entry_stage_counts"]["ingress_preflight"])
        self.assertTrue(result["path_free"])

    def test_exp_0014_result_against_historical_preimage(self) -> None:
        result = validate_exp_0014_result.validate(
            validate_exp_0014_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertEqual(3, result["input_count"])
        self.assertEqual(3, result["next_action_counts"]["review"])
        self.assertEqual(
            3, result["finding_code_counts"]["security.remote_resource"]
        )
        self.assertTrue(result["path_free"])

    def test_exp_0015_result_against_historical_preimage(self) -> None:
        result = validate_exp_0015_result.validate(
            validate_exp_0015_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertEqual(3, result["input_count"])
        self.assertEqual(
            3, result["context_input_counts"]["content.navigation"]
        )
        self.assertFalse(result["suppressed_context_present"])
        self.assertEqual(0, result["unclassified_input_count"])
        self.assertTrue(result["path_free"])

    def test_exp_0016_result_against_historical_preimage(self) -> None:
        result = validate_exp_0016_result.validate(
            validate_exp_0016_result.RESULT_PATH
        )
        self.assertEqual("pass", result["status"])
        self.assertEqual(48, result["case_count"])
        self.assertEqual(96, result["parser_runs"])
        self.assertEqual(
            0,
            result["strategies"]["strict_navigation_candidate"]["metrics"][
                "critical_false_continue"
            ],
        )
        self.assertTrue(result["path_free"])


if __name__ == "__main__":
    unittest.main()
