from __future__ import annotations

import copy
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0009.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0009", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_temp_base() -> Path:
    if os.name == "nt":
        value = Path(r"C:\rep\tmp\SammlungsLotse\exp-0009-tests")
    else:
        value = Path(tempfile.gettempdir()) / "SammlungsLotse-exp-0009-tests"
    value.mkdir(parents=True, exist_ok=True)
    return value


class Exp0009Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.manifest = RUNNER.load_contract()
        cls.cases = {item["case_key"]: item for item in cls.manifest["cases"]}

    def evaluate(self, case_key: str, case: dict | None = None) -> dict:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            return RUNNER.evaluate_case(
                self.manifest,
                case or self.cases[case_key],
                Path(directory) / case_key,
                RUNNER.IdentityLimits(**self.profile["limits"]),
            )

    def test_profile_and_manifest_are_narrow_and_complete(self) -> None:
        self.assertEqual(18, len(self.manifest["cases"]))
        self.assertEqual(15, sum(item["expected_assessment"] == "completed" for item in self.manifest["cases"]))
        self.assertEqual(3, sum(item["expected_assessment"] == "not_assessed" for item in self.manifest["cases"]))
        self.assertEqual(2, self.profile["repetitions"])
        self.assertTrue(self.profile["implementation"]["synthetic_only"])
        self.assertFalse(self.profile["implementation"]["product_code_changes"])
        self.assertEqual([], self.profile["implementation"]["external_dependencies"])

    def test_generator_and_product_keep_identity_levels_separate(self) -> None:
        exact = self.evaluate("byte-identical-renamed")
        repackaged = self.evaluate("zip-repackaged")
        opf = self.evaluate("opf-whitespace-only")
        exact_stages = RUNNER.stage_map(exact["report"])
        repackaged_stages = RUNNER.stage_map(repackaged["report"])
        opf_stages = RUNNER.stage_map(opf["report"])
        self.assertEqual("candidate_same", exact_stages["byte"]["decision"])
        self.assertEqual("different", repackaged_stages["byte"]["decision"])
        self.assertEqual("candidate_same", repackaged_stages["package"]["decision"])
        self.assertEqual("different", opf_stages["package"]["decision"])
        self.assertEqual("candidate_same", opf_stages["representation"]["decision"])

    def test_invalid_packages_fail_closed_without_paths(self) -> None:
        for case_key in (
            "corrupt-zip-not-assessed",
            "unsafe-package-path-not-assessed",
            "duplicate-logical-entry-not-assessed",
        ):
            result = self.evaluate(case_key)
            self.assertEqual("not_assessed", result["assessment"])
            self.assertTrue(result["report"]["reason_codes"])
            self.assertFalse(RUNNER.PRIVATE_PATH_PATTERN.search(RUNNER.canonical_json(result)))

    def test_oracle_is_not_an_input_to_product_decisions(self) -> None:
        original = self.cases["metadata-collision-work-conflict"]
        first = self.evaluate(original["case_key"], original)
        altered = copy.deepcopy(original)
        altered["oracle"] = {stage: ["candidate_same"] for stage in RUNNER.STAGES}
        second = self.evaluate(altered["case_key"], altered)
        self.assertEqual(first["report"], second["report"])
        self.assertNotEqual(first["oracle_evaluation"], second["oracle_evaluation"])

    def test_experiment_runner_has_no_network_client(self) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        for forbidden in ("import socket", "import urllib", "import requests", "http.client"):
            self.assertNotIn(forbidden, source)

    def test_empirical_result_contract_when_present(self) -> None:
        if not RUNNER.RESULT_PATH.is_file():
            self.skipTest("result.json is created only after the frozen preimage commit")
        result = RUNNER.validate_result()
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))
        self.assertIn(
            result["quality_verdict"],
            {"qualified", "qualified_with_findings", "not_qualified"},
        )


if __name__ == "__main__":
    unittest.main()
