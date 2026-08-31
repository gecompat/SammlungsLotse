"""Current repository tests for historically frozen experiment evidence."""

from __future__ import annotations

import unittest

from tools.experiments import validate_exp_0009_result
from tools.experiments import validate_exp_0010_result
from tools.experiments import validate_exp_0011_result
from tools.experiments import validate_exp_0012_result


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


if __name__ == "__main__":
    unittest.main()
