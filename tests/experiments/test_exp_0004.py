import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0004.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0004", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class Exp0004Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = RUNNER.load_profile()
        cls.result = RUNNER.validate_result(RUNNER.DEFAULT_RESULT)

    def first_cases(self):
        return {
            case["case_key"]: case
            for case in self.result["repetitions"][0]["cases"]
        }

    def test_result_contract_and_metrics(self):
        self.assertEqual("pass", self.result["status"])
        self.assertEqual(15, len(self.result["acceptance"]))
        self.assertTrue(all(self.result["acceptance"].values()))
        for stage in RUNNER.STAGES:
            metrics = self.result["metrics"][stage]
            self.assertEqual(1.0, metrics["precision"]["value"])
            self.assertEqual(1.0, metrics["recall"]["value"])
            self.assertEqual(0, metrics["false_positive_count"])

    def test_stage_decisions_remain_layered(self):
        cases = self.first_cases()
        repackaged = RUNNER.stage_map(cases["identity-repackaged"])
        self.assertEqual("different", repackaged["byte"]["decision"])
        self.assertEqual("candidate_same", repackaged["package"]["decision"])
        multiformat = RUNNER.stage_map(cases["identity-multiformat-edition"])
        self.assertEqual("different", multiformat["representation"]["decision"])
        self.assertEqual("candidate_same", multiformat["edition"]["decision"])
        translation = RUNNER.stage_map(cases["identity-edition-vs-translation"])
        self.assertEqual("different", translation["edition"]["decision"])
        self.assertEqual("candidate_related", translation["work"]["decision"])

    def test_candidates_expose_positive_negative_and_missing_channels(self):
        all_stages = [
            stage for case in self.first_cases().values() for stage in case["stages"]
        ]
        candidates = [stage for stage in all_stages if stage["decision"].startswith("candidate_")]
        self.assertTrue(candidates)
        self.assertTrue(all(stage["positive_evidence"] for stage in candidates))
        self.assertTrue(all(stage["negative_evidence"] for stage in candidates))
        self.assertTrue(any(stage["missing_evidence"] for stage in all_stages))
        for stage in all_stages:
            negative_codes = {item["code"] for item in stage["negative_evidence"]}
            self.assertTrue(negative_codes.isdisjoint(stage["missing_evidence"]))

    def test_classifier_does_not_read_relationship_oracle_for_decisions(self):
        cases = RUNNER.load_cases(self.profile)
        original = cases["edition-sample-vs-full"]
        original_result = RUNNER.evaluate_case(original["case_key"], original, self.profile)
        altered = copy.deepcopy(original)
        altered["oracle"]["expected_relationship"] = {
            "file": "different",
            "representation": "different",
            "edition": "different",
            "work": "different",
        }
        altered_result = RUNNER.evaluate_case(altered["case_key"], altered, self.profile)
        self.assertEqual(
            [stage["decision"] for stage in original_result["stages"]],
            [stage["decision"] for stage in altered_result["stages"]],
        )
        self.assertNotEqual(
            [stage["matches_oracle"] for stage in original_result["stages"]],
            [stage["matches_oracle"] for stage in altered_result["stages"]],
        )

    def test_run_is_read_only_and_reproducible(self):
        self.assertTrue(self.result["input_integrity"]["unchanged"])
        self.assertEqual(
            self.result["repetitions"][0]["semantic_sha256"],
            self.result["repetitions"][1]["semantic_sha256"],
        )
        self.assertTrue(
            all(
                case["effects_observed"] == []
                for repetition in self.result["repetitions"]
                for case in repetition["cases"]
            )
        )


if __name__ == "__main__":
    unittest.main()
