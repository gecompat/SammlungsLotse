"""Contract tests for the EXP-0013 private noncompletion diagnostic."""

from __future__ import annotations

import ast
import copy
import inspect
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tools.experiments import run_exp_0013


def test_temp_base() -> Path:
    if os.name == "nt":
        value = Path(r"C:\rep\tmp\SammlungsLotse\exp-0013-tests")
    else:
        value = Path(tempfile.gettempdir()) / "SammlungsLotse-exp-0013-tests"
    value.mkdir(parents=True, exist_ok=True)
    return value


def completed_report() -> dict[str, object]:
    return {"assessment": "completed", "handoff_reason_codes": []}


class Exp0013Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.records = run_exp_0013.validate_contract()

    def make_inputs(self, root: Path, count: int = 4) -> list[Path]:
        result = []
        for index in range(count):
            value = root / f"input-{index + 1}.epub"
            value.write_bytes(f"synthetic-{index + 1}".encode("ascii"))
            result.append(value)
        return result

    def test_profile_binds_exact_private_and_product_free_boundary(self) -> None:
        self.assertEqual("EXP-0013", self.profile["artifact"])
        self.assertEqual(3, self.profile["input_contract"]["count"])
        self.assertEqual(4 * 1024 * 1024, self.profile["input_contract"]["max_file_bytes"])
        self.assertEqual(12 * 1024 * 1024, self.profile["input_contract"]["max_total_bytes"])
        self.assertEqual(
            "--confirm-same-exp-0012-inputs",
            self.profile["input_contract"]["confirmation_flag"],
        )
        self.assertTrue(all(value is False for value in self.profile["implementation"].values()))
        self.assertEqual(["V1", "V2"], self.profile["commands"]["search_variants"])
        self.assertEqual(4, self.profile["limits"]["private_search_runs"])
        self.assertEqual([1, 4, 9], self.profile["synthetic_controls"]["actual_wi0011_record_ids"])
        self.assertEqual([1, 4, 9], [record["expected_id"] for record in self.records])
        self.assertEqual(
            "sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5",
            self.profile["runtime_bindings"]["calibre"]["image_id"],
        )

    def test_runner_has_no_discovery_network_database_or_product_import(self) -> None:
        source = Path(run_exp_0013.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue(imports.isdisjoint({"requests", "socket", "sqlite3", "urllib"}))
        self.assertNotIn("metadata.db", source)
        input_source = inspect.getsource(run_exp_0013.validate_private_inputs)
        self.assertNotIn("os.walk", input_source)
        self.assertNotIn("glob(", input_source)
        self.assertNotIn("rglob(", input_source)
        self.assertNotIn("iterdir(", input_source)
        self.assertIn('action="append"', inspect.getsource(run_exp_0013.parser))

    def test_aggregation_matrix_is_deterministic_and_unknown_stays_visible(self) -> None:
        matrix = self.profile["synthetic_controls"]["aggregation_matrix"]
        first = run_exp_0013.aggregate_diagnostics(matrix["reports"])
        second = run_exp_0013.aggregate_diagnostics(
            json.loads(run_exp_0013.canonical_json(matrix["reports"]))
        )
        self.assertEqual(matrix["expected"], first)
        self.assertEqual(run_exp_0013.canonical_json(first), run_exp_0013.canonical_json(second))
        self.assertEqual(1, first["reason_code_counts"]["future.unknown"])
        self.assertEqual(1, first["entry_stage_counts"]["unclassified"])
        self.assertEqual("inconclusive", first["status"])

    def test_result_contract_rejects_partial_cleanup_and_private_fields(self) -> None:
        aggregate = run_exp_0013.aggregate_diagnostics(
            [
                completed_report(),
                {"assessment": "not_assessed", "handoff_reason_codes": ["executor.timeout"]},
                {"assessment": "not_assessed", "handoff_reason_codes": ["identity.not_assessed"]},
            ]
        )
        result = run_exp_0013.build_private_result(
            aggregate,
            input_count=3,
            search_runs=4,
            wi0011_runs=3,
            execution_complete=True,
            source_unchanged=True,
            cleanup_complete=True,
        )
        self.assertEqual("not_qualified", result["status"])
        self.assertEqual(
            {
                "artifact",
                "assessment_counts",
                "cleanup_complete",
                "entry_stage_counts",
                "input_count",
                "path_free",
                "reason_code_counts",
                "schema",
                "search_runs",
                "source_unchanged",
                "status",
                "wi0011_runs",
            },
            set(result),
        )
        for key, value in (
            ("execution_complete", False),
            ("source_unchanged", False),
            ("cleanup_complete", False),
        ):
            arguments = {
                "execution_complete": True,
                "source_unchanged": True,
                "cleanup_complete": True,
            }
            arguments[key] = value
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.build_private_result(
                    aggregate,
                    input_count=3,
                    search_runs=4,
                    wi0011_runs=3,
                    **arguments,
                )
        private = copy.deepcopy(result)
        private["title"] = "private"
        with self.assertRaises(run_exp_0013.ExperimentError):
            run_exp_0013.validate_private_result_dict(private)
        path_like = copy.deepcopy(result)
        path_like["reason_code_counts"] = {"C:\\private\\book.epub": 2}
        with self.assertRaises(run_exp_0013.ExperimentError):
            run_exp_0013.validate_private_result_dict(path_like)

    def test_input_validation_requires_three_direct_bounded_regular_epubs(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_inputs(root)
            validated = run_exp_0013.validate_private_inputs(inputs[:3])
            self.assertEqual(3, len(validated))
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.validate_private_inputs(inputs[:2])
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.validate_private_inputs(inputs)
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.validate_private_inputs([inputs[0], inputs[0], inputs[1]])
            directory_input = root / "directory.epub"
            directory_input.mkdir()
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.validate_private_inputs([inputs[0], inputs[1], directory_input])
            link = root / "link.epub"
            link.symlink_to(inputs[0])
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.validate_private_inputs([inputs[0], inputs[1], link])
            oversized = root / "oversized.epub"
            with oversized.open("wb") as stream:
                stream.truncate(4 * 1024 * 1024 + 1)
            with self.assertRaises(run_exp_0013.ExperimentError):
                run_exp_0013.validate_private_inputs([inputs[0], inputs[1], oversized])

    def test_wi0011_projection_keeps_only_assessment_and_reason_code(self) -> None:
        report = {
            "assessment": "not_assessed",
            "calibre_record": {
                "external_record_id": 7,
                "library_snapshot_sha256": "a" * 64,
            },
            "effects": {
                "cleanup_complete": True,
                "container_started": False,
                "domain_system_writes": False,
                "network_access": False,
                "persistence": False,
                "source_modified": False,
                "task_materialized": False,
                "writer": False,
            },
            "handoff_reason_codes": ["ingress.preflight_gate_not_open"],
            "identity": None,
            "schema": "sammlungslotse/ebook-calibre-identity-candidate-report/v1",
        }
        bounded = SimpleNamespace(
            returncode=4,
            timed_out=False,
            stdout=json.dumps(report).encode("utf-8"),
            stderr=b"",
            stdout_truncated=False,
            stderr_truncated=False,
        )
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            with mock.patch.object(run_exp_0013, "run_bounded", return_value=bounded):
                value = run_exp_0013.run_identity_diagnostic(
                    root / "input.epub",
                    root / "library",
                    7,
                    root / "identity",
                )
        self.assertEqual(
            {
                "assessment": "not_assessed",
                "handoff_reason_codes": ["ingress.preflight_gate_not_open"],
            },
            value,
        )

    def test_private_workflow_runs_each_identity_once_and_writes_only_aggregate(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_inputs(root)[:3]
            temp_root = root / "runtime"
            result_path = root / "result.json"
            projection = [
                {
                    "authors": ["SENSITIVE_AUTHOR_VALUE"],
                    "external_record_id": index,
                    "formats": ["epub"],
                    "identifiers": {},
                    "languages": [],
                    "title": "SENSITIVE_TITLE_VALUE",
                }
                for index in (1, 2, 3)
            ]
            reports = [
                {"assessment": "not_assessed", "handoff_reason_codes": ["ingress.preflight_gate_not_open"]},
                {"assessment": "not_assessed", "handoff_reason_codes": ["executor.timeout"]},
                {"assessment": "not_assessed", "handoff_reason_codes": ["identity.not_assessed"]},
            ]
            with (
                mock.patch.object(run_exp_0013, "ALLOWED_TEMP_ROOT", temp_root),
                mock.patch.object(run_exp_0013, "require_committed_preimage", return_value="a" * 40),
                mock.patch.object(run_exp_0013, "_image_matches", return_value=True),
                mock.patch.object(run_exp_0013, "run_synthetic_controls", return_value={"status": "pass"}),
                mock.patch.object(run_exp_0013, "_container_names", side_effect=[[], []]),
                mock.patch.object(run_exp_0013, "materialize_private_library", return_value=projection),
                mock.patch.object(run_exp_0013, "run_self_searches", side_effect=[2, 1, 1]),
                mock.patch.object(run_exp_0013, "run_identity_diagnostic", side_effect=reports) as identity,
            ):
                result = run_exp_0013.execute_private_diagnostic(
                    inputs,
                    confirmed_same_inputs=True,
                    temp_root=temp_root,
                    result_path=result_path,
                )
            self.assertEqual(3, identity.call_count)
            self.assertEqual(3, result["wi0011_runs"])
            self.assertEqual(4, result["search_runs"])
            self.assertEqual("not_qualified", result["status"])
            self.assertEqual(result, json.loads(result_path.read_text(encoding="utf-8")))
            encoded = run_exp_0013.canonical_json(result)
            self.assertNotIn("SENSITIVE_AUTHOR_VALUE", encoded)
            self.assertNotIn("SENSITIVE_TITLE_VALUE", encoded)
            self.assertNotIn("external_record_id", encoded)
            self.assertNotIn("library_snapshot_sha256", encoded)


if __name__ == "__main__":
    unittest.main()
