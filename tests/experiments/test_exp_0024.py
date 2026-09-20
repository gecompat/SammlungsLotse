from __future__ import annotations

import copy
import contextlib
import io
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from tools.experiments import run_exp_0024 as exp


class Exp0024Tests(unittest.TestCase):
    def test_bound_matrix_reaches_only_registered_classes(self) -> None:
        cases = exp.load_cases()
        self.assertEqual([f"M{number:02d}" for number in range(1, 11)], [case["case_id"] for case in cases])
        self.assertEqual([case["expected_class"] for case in cases], [exp.evaluate(case)["review_class"] for case in cases])
        self.assertIn("review_cross_library", [exp.evaluate(case)["review_class"] for case in cases])
        self.assertIn("review_scope_incomplete", [exp.evaluate(case)["review_class"] for case in cases])
        self.assertIn("not_assessed", [exp.evaluate(case)["review_class"] for case in cases])
        self.assertTrue(all(len(exp.evaluate(case)["candidates"]) <= exp.MAX_CANDIDATES for case in cases))

    def test_two_runs_are_deterministic_and_cleaned_up(self) -> None:
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            root = Path(directory) / "task"
            first, second = exp.execute(root), exp.execute(root)
            self.assertFalse(root.exists())
        self.assertEqual(first, second)
        self.assertTrue(first["runs_semantically_identical"])
        self.assertTrue(all(value is False for value in first["effects"].values()))

    def test_target_candidate_is_only_a_manual_hint_and_bounds_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            candidate = next(item for item in exp.execute(Path(directory) / "task")["outcomes"] if item["case_id"] == "M01")
        self.assertEqual("review_target_candidate", candidate["review_class"])
        self.assertEqual({"candidate_reason", "library_position"}, set(candidate["candidates"][0]))
        altered = copy.deepcopy(exp.load_cases()[0])
        altered["snapshots"] *= 4
        with self.assertRaises(exp.ExperimentError):
            exp._validate_case(altered)

    def test_result_validator_rejects_target_and_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            result = exp.execute(Path(directory) / "task")
        polluted = copy.deepcopy(result)
        polluted["outcomes"][0]["target_library"] = 1
        with self.assertRaises(exp.ExperimentError):
            exp.validate_result_dict(polluted)
        changed = copy.deepcopy(result)
        changed["outcomes"][3]["review_class"] = "review_target_candidate"
        with self.assertRaises(exp.ExperimentError):
            exp.validate_result_dict(changed)

    def test_runner_has_no_output_writer_contract(self) -> None:
        source = Path(exp.__file__).read_text(encoding="utf-8")
        self.assertNotIn("--result", source)
        self.assertNotIn("write_text", source)
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output), mock.patch.object(
                sys, "argv", ["run_exp_0024.py", "--temp-root", str(Path(directory) / "task")]
            ):
                self.assertEqual(0, exp.main())
        self.assertIn('"artifact": "EXP-0024"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
