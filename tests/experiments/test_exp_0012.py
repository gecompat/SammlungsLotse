"""Contract tests for EXP-0012 candidate-search evidence."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from tools.experiments import run_exp_0012


ROOT = Path(__file__).resolve().parents[2]


class Exp0012Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.manifest = run_exp_0012.validate_contract()

    def test_profile_is_narrow_and_product_code_free(self) -> None:
        self.assertEqual("EXP-0012", self.profile["artifact"])
        self.assertEqual(["V1", "V2", "V3"], self.profile["strategies"])
        self.assertEqual(8, self.profile["limits"]["synthetic_tasks"])
        self.assertEqual(2, self.profile["limits"]["repetitions"])
        self.assertEqual(5, self.profile["limits"]["candidate_limit"])
        self.assertEqual(3, self.profile["limits"]["private_epub_limit"])
        self.assertTrue(all(value is False for value in self.profile["implementation"].values()))
        self.assertTrue(self.profile["private_smoke"]["anonymous_aggregate_only"])
        self.assertFalse(self.profile["private_smoke"]["acceptance_authority"])

    def test_manifest_binds_twelve_records_and_eight_oracle_tasks(self) -> None:
        self.assertTrue(self.manifest["synthetic_only"])
        self.assertEqual(list(range(1, 13)), [item["expected_id"] for item in self.manifest["records"]])
        self.assertEqual(8, len(self.manifest["tasks"]))
        self.assertEqual(8, len({item["case"] for item in self.manifest["tasks"]}))
        for task in self.manifest["tasks"]:
            self.assertEqual({"V1", "V2", "V3"}, set(task["oracle"]))

    def test_queries_are_field_bound_and_identifier_has_no_fallback(self) -> None:
        identifier_task = self.manifest["tasks"][0]
        self.assertEqual(
            "identifiers:=isbn:=9780000000008",
            run_exp_0012.query_for(identifier_task, "V1"),
        )
        no_identifier = self.manifest["tasks"][2]
        self.assertIsNone(run_exp_0012.query_for(no_identifier, "V1"))
        self.assertEqual(
            'title:"=Silent Harbor" and author:"=Nora Unique"',
            run_exp_0012.query_for(no_identifier, "V2"),
        )
        self.assertEqual(
            'title:"Silent Harbor" and author:"Nora Unique"',
            run_exp_0012.query_for(no_identifier, "V3"),
        )

    def test_runner_has_no_network_or_database_client(self) -> None:
        tree = ast.parse(Path(run_exp_0012.__file__).read_text(encoding="utf-8"))
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue(imports.isdisjoint({"requests", "socket", "sqlite3", "urllib"}))
        source = Path(run_exp_0012.__file__).read_text(encoding="utf-8")
        self.assertNotIn("metadata.db", source)
        self.assertNotIn("src/sammlungslotse", "\n".join(run_exp_0012.PREIMAGE_FILES[:6]))
        self.assertIn('arguments[0] == "search"', source)
        self.assertIn("not execution.stdout.strip()", source)
        self.assertIn("No books matching the search expression", source)
        self.assertIn('arguments[-1].encode("utf-8")', source)

    def test_private_smoke_retains_only_anonymous_counts(self) -> None:
        contract = self.profile["private_smoke"]
        self.assertTrue(contract["explicit_opt_in"])
        self.assertTrue(contract["source_read_only"])
        self.assertTrue(contract["cleanup_required"])
        source = Path(run_exp_0012.__file__).read_text(encoding="utf-8")
        self.assertIn('"private_values_retained": False', source)
        self.assertIn("select_private_epubs", source)

    def test_path_scanner_distinguishes_query_escapes_from_real_paths(self) -> None:
        escaped_query = run_exp_0012.canonical_json(
            {"query": 'title:"=Twin Edition" and author:"=Edition Author"'}
        )
        self.assertIsNone(run_exp_0012.PRIVATE_PATH_PATTERN.search(escaped_query))
        self.assertIsNotNone(
            run_exp_0012.PRIVATE_PATH_PATTERN.search(
                run_exp_0012.canonical_json({"path": "C:\\private\\book.epub"})
            )
        )

    @unittest.skipUnless(run_exp_0012.RESULT_PATH.is_file(), "empirical result not generated")
    def test_empirical_result_contract_when_present(self) -> None:
        result = run_exp_0012.validate_result(run_exp_0012.RESULT_PATH)
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))
        self.assertEqual(2, len(result["runs"]))
        self.assertEqual(
            json.dumps(result["runs"][0]["observations"], sort_keys=True),
            json.dumps(result["runs"][1]["observations"], sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
