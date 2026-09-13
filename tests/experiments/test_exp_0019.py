from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from tools.experiments import run_exp_0019 as exp


class Exp0019Tests(unittest.TestCase):
    def test_matrix_is_exact_and_bound(self) -> None:
        cases = exp.load_cases()
        self.assertEqual([f"C{number:02d}" for number in range(1, 11)], [case["case_id"] for case in cases])
        self.assertEqual([case["expected_class"] for case in cases], [exp.evaluate(case)["review_class"] for case in cases])

    def test_two_runs_are_deterministic_and_cleaned_up(self) -> None:
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            root = Path(directory) / "task"
            first, second = exp.execute(root), exp.execute(root)
            self.assertFalse(root.exists())
        self.assertEqual(first, second)
        self.assertTrue(first["runs_semantically_identical"])
        self.assertTrue(all(value is False for value in first["effects"].values()))

    def test_candidate_and_library_limits_fail_closed(self) -> None:
        case = copy.deepcopy(exp.load_cases()[1])
        case["snapshots"] *= 4
        with self.assertRaises(exp.ExperimentError):
            exp._validate_case(case)
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            result = exp.execute(Path(directory) / "task")
        limited = next(item for item in result["outcomes"] if item["case_id"] == "C06")
        self.assertEqual(("review_scope_incomplete", 6, 5), (limited["review_class"], limited["candidate_total"], len(limited["candidates"])))
        with self.assertRaises(exp.ExperimentError):
            exp.enforce_folder_candidate_bound([limited, limited, limited])

    def test_result_validator_rejects_private_metadata_and_oracle_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=exp.ROOT) as directory:
            result = exp.execute(Path(directory) / "task")
        polluted = copy.deepcopy(result)
        polluted["outcomes"][0]["title"] = "Synthetic one"
        with self.assertRaises(exp.ExperimentError):
            exp.validate_result_dict(polluted)
        changed = copy.deepcopy(result)
        changed["outcomes"][0]["review_class"] = "new"
        with self.assertRaises(exp.ExperimentError):
            exp.validate_result_dict(changed)


if __name__ == "__main__":
    unittest.main()
