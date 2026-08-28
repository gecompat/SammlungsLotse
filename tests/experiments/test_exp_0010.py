from __future__ import annotations

import copy
import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0010.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0010", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_temp_base() -> Path:
    if os.name == "nt":
        value = Path(r"C:\rep\tmp\SammlungsLotse\exp-0010-tests")
    else:
        value = Path(tempfile.gettempdir()) / "SammlungsLotse-exp-0010-tests"
    value.mkdir(parents=True, exist_ok=True)
    return value


class Exp0010Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.manifest = RUNNER.load_contract()
        cls.cases = {item["case_key"]: item for item in cls.manifest["cases"]}

    def evaluate(self, case_key: str, case: dict | None = None) -> dict:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            return RUNNER.evaluate_product_case(
                self.manifest,
                case or self.cases[case_key],
                Path(directory) / case_key,
                RUNNER.IdentityLimits(**self.profile["limits"]),
            )

    def test_profile_and_manifest_are_narrow_and_complete(self) -> None:
        self.assertEqual(10, len(self.manifest["cases"]))
        self.assertEqual(8, sum(item["oracle_scope"] == "quality" for item in self.manifest["cases"]))
        self.assertEqual(2, sum(item["oracle_scope"] == "control" for item in self.manifest["cases"]))
        self.assertEqual(2, self.profile["product_repetitions"])
        self.assertTrue(self.profile["implementation"]["synthetic_only"])
        self.assertFalse(self.profile["implementation"]["product_code_changes"])
        self.assertEqual("podman network=none", self.profile["implementation"]["network"])

    def test_generator_binds_epub_container_and_primary_identifier(self) -> None:
        case = self.cases["same-primary-minor-revision"]
        spec = RUNNER.merged_spec(self.manifest, case, "left")
        payload = RUNNER.generate_epub(spec)
        with zipfile.ZipFile(RUNNER.io.BytesIO(payload), mode="r") as archive:
            first = archive.infolist()[0]
            self.assertEqual("mimetype", first.filename)
            self.assertEqual(zipfile.ZIP_STORED, first.compress_type)
            self.assertEqual(b"application/epub+zip", archive.read("mimetype"))
        projection = RUNNER.standard_metadata_projection(payload)
        self.assertEqual(spec["primary_identifier"], projection["primary_identifier"])
        self.assertEqual(spec["modified"], projection["modified"])
        self.assertEqual([], projection["additional_identifiers"])

    def test_identifier_and_collection_roles_are_reconstructable(self) -> None:
        typed = self.cases["shared-typed-additional-different-primary"]
        typed_spec = RUNNER.merged_spec(self.manifest, typed, "left")
        typed_projection = RUNNER.standard_metadata_projection(RUNNER.generate_epub(typed_spec))
        self.assertEqual(typed_spec["primary_identifier"], typed_projection["primary_identifier"])
        self.assertEqual(typed_spec["additional_identifiers"], typed_projection["additional_identifiers"])

        multiple = self.cases["multiple-collections-partial-overlap"]
        collection_spec = RUNNER.merged_spec(self.manifest, multiple, "left")
        collection_projection = RUNNER.standard_metadata_projection(
            RUNNER.generate_epub(collection_spec)
        )
        self.assertEqual(collection_spec["collections"], collection_projection["collections"])

    def test_invalid_controls_are_separate_from_quality_scope(self) -> None:
        binding = self.cases["invalid-missing-primary-binding"]
        binding_spec = RUNNER.merged_spec(self.manifest, binding, "left")
        projection = RUNNER.standard_metadata_projection(RUNNER.generate_epub(binding_spec))
        self.assertIsNone(projection["primary_identifier"])
        self.assertEqual("missing-id", projection["unique_identifier_ref"])
        self.assertEqual("control", binding["oracle_scope"])

        modified = self.cases["invalid-missing-modified"]
        modified_spec = RUNNER.merged_spec(self.manifest, modified, "left")
        projection = RUNNER.standard_metadata_projection(RUNNER.generate_epub(modified_spec))
        self.assertIsNone(projection["modified"])
        self.assertEqual("control", modified["oracle_scope"])

    def test_unmodified_product_flattens_identifier_and_collection_roles(self) -> None:
        typed = self.evaluate("shared-typed-additional-different-primary")
        first_projection = typed["standard_metadata_projection"][0]
        first_product = typed["report"]["inputs"][0]["metadata"]
        self.assertTrue(first_projection["additional_identifiers"])
        self.assertEqual(
            sorted(
                [first_projection["primary_identifier"]["value"]]
                + [item["value"] for item in first_projection["additional_identifiers"]]
            ),
            sorted(first_product["identifiers"]),
        )
        self.assertNotIn("primary_identifier", first_product)
        self.assertNotIn("additional_identifiers", first_product)

        series = self.evaluate("series-overlap-distinct-works")
        series_projection = series["standard_metadata_projection"][0]
        series_product = series["report"]["inputs"][0]["metadata"]
        self.assertEqual(
            [item["name"] for item in series_projection["collections"]],
            series_product["work_references"],
        )
        self.assertNotIn("collections", series_product)

    def test_oracle_is_not_an_input_to_product_decisions(self) -> None:
        original = self.cases["same-primary-strong-content-conflict"]
        first = self.evaluate(original["case_key"], original)
        altered = copy.deepcopy(original)
        altered["oracle"] = {stage: ["candidate_same"] for stage in RUNNER.STAGES}
        altered["publication_oracle"] = ["same"]
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
