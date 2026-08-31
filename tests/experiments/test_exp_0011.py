from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0011.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0011", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class Exp0011Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.contracts = RUNNER.load_contract()

    def test_profile_binds_exactly_fifteen_pairs_and_three_variants(self) -> None:
        self.assertEqual(
            {"test_0001": 5, "exp_0010_quality": 8, "exp_0010_control": 2, "total": 15},
            self.profile["case_sources"],
        )
        self.assertEqual(["V1", "V2", "V3"], self.profile["variants"])
        self.assertEqual(2, self.profile["repetitions"])

    def test_execution_boundary_is_product_code_free_and_offline(self) -> None:
        implementation = self.profile["implementation"]
        self.assertTrue(implementation["synthetic_only"])
        for field in (
            "container_access",
            "network_access",
            "product_code_changes",
            "versioned_media_writes",
        ):
            self.assertFalse(implementation[field])
        source = RUNNER_PATH.read_text(encoding="utf-8")
        for forbidden in ("import socket", "import urllib", "import requests", "http.client"):
            self.assertNotIn(forbidden, source)

    def test_contracts_prebind_migration_and_no_target_selection(self) -> None:
        variants = self.contracts["variants"]
        self.assertEqual({"V1", "V2", "V3"}, set(variants))
        for contract in variants.values():
            self.assertTrue(contract["field_mapping"])
            self.assertTrue(contract["migration_surface"])
            self.assertEqual("eligible_with_tradeoffs", contract["classification_rule"])

    def test_structured_metadata_preserves_roles_and_provenance(self) -> None:
        projection = {
            "primary_identifier": {"id": "pub-id", "value": "urn:example:1"},
            "additional_identifiers": [
                {"id": "isbn", "identifier_type": "15", "scheme": "onix", "value": "9780"}
            ],
            "modified": "2026-08-31T00:00:00Z",
            "collections": [
                {"id": "series", "identifier": "s1", "name": "Series", "position": "2", "type": "series"}
            ],
            "unique_identifier_ref": "pub-id",
        }
        structured = RUNNER.structured_metadata(projection, 1)
        self.assertEqual(projection["primary_identifier"], structured["primary_identifier"])
        self.assertEqual(projection["collections"], structured["collection_memberships"])
        self.assertNotIn("work_references", structured)
        self.assertTrue(all(item["status"] in {"observed", "missing"} for item in structured["provenance"].values()))

    def test_projection_keeps_v1_bytes_and_five_product_stages(self) -> None:
        report = {
            "assessment": "completed",
            "effects": {"domain_system_writes": False, "filesystem_writes": False, "network_access": False, "original_modified": False},
            "inputs": [
                {
                    "input_index": index,
                    "metadata": {"creators": [], "identifiers": [], "languages": [], "titles": [], "work_references": []},
                }
                for index in (1, 2)
            ],
            "limits": {},
            "overall": "abstain",
            "reason_codes": [],
            "schema": "sammlungslotse/ebook-identity-candidate-report/v1",
            "stages": [
                {"stage": stage, "decision": "abstain", "rule_id": f"rule.{stage}", "positive_evidence": [], "negative_evidence": [], "missing_evidence": []}
                for stage in RUNNER.PRODUCT_STAGES
            ],
        }
        standard = [RUNNER.empty_standard_projection(), RUNNER.empty_standard_projection()]
        variants = RUNNER.project_variants(report, standard)
        self.assertEqual(RUNNER.canonical_json(report), RUNNER.canonical_json(variants["V1"]["report_v1"]))
        self.assertEqual(list(RUNNER.PRODUCT_STAGES), [item["stage"] for item in variants["V2"]["report"]["stages"]])
        publication = next(item for item in variants["V3"]["report"]["stages"] if item["stage"] == "publication")
        self.assertEqual("not_assessed", publication["assessment"])
        self.assertNotIn("decision", publication)

    def test_empirical_result_contract_when_present(self) -> None:
        if not RUNNER.RESULT_PATH.is_file():
            self.skipTest("result.json is created only after the frozen preimage commit")
        result = RUNNER.validate_result()
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))


if __name__ == "__main__":
    unittest.main()
