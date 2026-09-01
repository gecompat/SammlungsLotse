"""Contract tests for the EXP-0014 private preflight-cause experiment."""

from __future__ import annotations

import ast
import copy
import inspect
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.experiments import run_exp_0014


def test_temp_base() -> Path:
    if os.name == "nt":
        value = Path(r"C:\rep\tmp\SammlungsLotse\exp-0014-tests")
    else:
        value = Path(tempfile.gettempdir()) / "SammlungsLotse-exp-0014-tests"
    value.mkdir(parents=True, exist_ok=True)
    return value


def projection(
    action: str = "continue_deep_read_only",
    *,
    observation: str = "snapshot.stable",
    finding: str | None = "format.epub",
) -> dict[str, object]:
    return {
        "finding_codes": [] if finding is None else [finding],
        "next_action": action,
        "observation_codes": [observation],
        "unclassified_finding_count": 0,
        "unclassified_observation_count": 0,
    }


class Exp0014Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = run_exp_0014.validate_contract()

    def make_inputs(self, root: Path, count: int = 4) -> list[Path]:
        result = []
        for index in range(count):
            value = root / f"private-title-{index + 1}.epub"
            value.write_bytes(f"synthetic-{index + 1}".encode("ascii"))
            result.append(value)
        return result

    def valid_report(
        self,
        *,
        extra_observations: list[str] | None = None,
        extra_findings: list[str] | None = None,
        sensitive_value: str | None = None,
    ) -> dict[str, object]:
        return run_exp_0014._synthetic_report(
            observation_codes=extra_observations,
            finding_codes=extra_findings,
            sensitive_value=sensitive_value,
        )

    def test_profile_binds_exact_private_product_free_boundary(self) -> None:
        self.assertEqual("EXP-0014", self.profile["artifact"])
        self.assertEqual(3, self.profile["input_contract"]["count"])
        self.assertEqual(
            4 * 1024 * 1024,
            self.profile["input_contract"]["max_file_bytes"],
        )
        self.assertEqual(
            12 * 1024 * 1024,
            self.profile["input_contract"]["max_total_bytes"],
        )
        self.assertEqual(
            "--confirm-same-exp-0013-inputs",
            self.profile["input_contract"]["confirmation_flag"],
        )
        self.assertTrue(
            all(value is False for value in self.profile["implementation"].values())
        )
        self.assertEqual(
            ["tools/run_ebook_intake.py", "--json"],
            self.profile["commands"]["arguments"],
        )
        self.assertEqual(
            1, self.profile["commands"]["intake_runs_per_private_input"]
        )
        self.assertEqual(
            list(run_exp_0014.OBSERVATION_CODES),
            self.profile["public_contract"]["observation_codes"],
        )
        self.assertEqual(
            list(run_exp_0014.FINDING_CODES),
            self.profile["public_contract"]["finding_codes"],
        )
        self.assertNotIn(
            "experiments/ebook/exp-0014/result.json",
            run_exp_0014.PREIMAGE_FILES,
        )
        self.assertFalse(run_exp_0014.RESULT_PATH.exists())

    def test_runtime_bindings_match_every_bound_file(self) -> None:
        bindings = self.profile["runtime_bindings"]["files"]
        self.assertEqual(len(run_exp_0014.RUNTIME_LOCATORS), len(bindings))
        package_root = (
            run_exp_0014.ROOT / "src" / "sammlungslotse" / "ebook_intake"
        )
        package_locators = sorted(
            path.relative_to(run_exp_0014.ROOT).as_posix()
            for path in package_root.glob("*.py")
        )
        self.assertEqual(
            package_locators,
            sorted(
                locator
                for locator in run_exp_0014.RUNTIME_LOCATORS
                if locator.startswith("src/sammlungslotse/ebook_intake/")
            ),
        )
        for binding, locator in zip(
            bindings, run_exp_0014.RUNTIME_LOCATORS, strict=True
        ):
            self.assertEqual(locator, binding["locator"])
            self.assertEqual(
                run_exp_0014.sha256_file(run_exp_0014.ROOT / locator),
                binding["sha256"],
            )

    def test_runner_has_no_discovery_network_database_or_product_import(self) -> None:
        source = Path(run_exp_0014.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue(
            imports.isdisjoint({"requests", "socket", "sqlite3", "urllib"})
        )
        self.assertNotIn("metadata.db", source)
        input_source = inspect.getsource(run_exp_0014.validate_private_inputs)
        self.assertNotIn("os.walk", input_source)
        self.assertNotIn("glob(", input_source)
        self.assertNotIn("rglob(", input_source)
        self.assertNotIn("iterdir(", input_source)
        self.assertIn('action="append"', inspect.getsource(run_exp_0014.parser))
        self.assertNotIn("--deep-read-only", inspect.getsource(run_exp_0014.run_intake_projection))

    def test_projection_matrix_is_deterministic_and_covers_defer(self) -> None:
        matrix = self.profile["synthetic_controls"]["projection_matrix"]
        first = run_exp_0014.aggregate_projections(matrix["reports"])
        second = run_exp_0014.aggregate_projections(
            json.loads(run_exp_0014.canonical_json(matrix["reports"]))
        )
        self.assertEqual(matrix["expected"], first)
        self.assertEqual(
            run_exp_0014.canonical_json(first),
            run_exp_0014.canonical_json(second),
        )
        self.assertEqual(1, first["next_action_counts"]["defer"])
        self.assertEqual(1, first["unclassified_observation_count"])
        self.assertEqual(1, first["unclassified_finding_count"])
        self.assertEqual("inconclusive", first["status"])

    def test_projection_discards_values_snapshot_and_unknown_code_literals(self) -> None:
        report = self.valid_report(
            extra_observations=["future.unknown_observation"],
            extra_findings=["future.unknown_finding"],
            sensitive_value="SENSITIVE_EVIDENCE_VALUE",
        )
        validated = run_exp_0014.validate_intake_report_dict(
            report,
            expected_sha256="a" * 64,
            expected_size=1,
        )
        projected = run_exp_0014.project_intake_report(validated)
        encoded = run_exp_0014.canonical_json(projected)

        self.assertEqual(1, projected["unclassified_observation_count"])
        self.assertEqual(1, projected["unclassified_finding_count"])
        for forbidden in (
            "future.unknown_observation",
            "future.unknown_finding",
            "SENSITIVE_EVIDENCE_VALUE",
            '"values":',
            '"snapshot":',
            '"sha256":"',
            '"size_bytes":',
        ):
            self.assertNotIn(forbidden, encoded)

    def test_full_intake_contract_rejects_extra_fields_and_invalid_json(self) -> None:
        report = self.valid_report()
        extra = copy.deepcopy(report)
        extra["title"] = "private"
        with self.assertRaises(run_exp_0014.ExperimentError):
            run_exp_0014.validate_intake_report_dict(
                extra,
                expected_sha256="a" * 64,
                expected_size=1,
            )
        unsafe = copy.deepcopy(report)
        unsafe["effects"]["network_access"] = True
        with self.assertRaises(run_exp_0014.ExperimentError):
            run_exp_0014.validate_intake_report_dict(
                unsafe,
                expected_sha256="a" * 64,
                expected_size=1,
            )
        with self.assertRaises(run_exp_0014.ExperimentError):
            run_exp_0014.parse_intake_stdout(b"{")

    def test_intake_subprocess_is_exactly_one_bounded_json_run(self) -> None:
        report = self.valid_report()
        completed = run_exp_0014.BoundedProcess(
            returncode=0,
            stderr=b"",
            stderr_truncated=False,
            stdout=(run_exp_0014.canonical_json(report) + "\n").encode("utf-8"),
            stdout_truncated=False,
            timed_out=False,
        )
        neutral = Path("input-1.epub")
        with mock.patch.object(
            run_exp_0014, "run_bounded", return_value=completed
        ) as bounded:
            projected = run_exp_0014.run_intake_projection(
                neutral,
                expected_sha256="a" * 64,
                expected_size=1,
                profile=self.profile,
            )

        bounded.assert_called_once_with(
            [
                sys.executable,
                str(run_exp_0014.INTAKE_CLI_PATH),
                "--json",
                str(neutral),
            ],
            timeout=20,
            stdout_limit=131072,
            stderr_limit=8192,
        )
        self.assertEqual("continue_deep_read_only", projected["next_action"])

    def test_result_contract_rejects_partial_cleanup_and_private_fields(self) -> None:
        aggregate = run_exp_0014.aggregate_projections(
            [
                projection(),
                projection("review", observation="epub.script.present"),
                projection(
                    "stop",
                    observation="container.open_error",
                    finding="container.corrupt",
                ),
            ]
        )
        result = run_exp_0014.build_private_result(
            aggregate,
            input_count=3,
            intake_runs=3,
            execution_complete=True,
            source_unchanged=True,
            cleanup_complete=True,
        )
        self.assertEqual(run_exp_0014.RESULT_FIELDS, set(result))
        self.assertEqual("pass", result["status"])
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
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.build_private_result(
                    aggregate,
                    input_count=3,
                    intake_runs=3,
                    **arguments,
                )
        private = copy.deepcopy(result)
        private["title"] = "private"
        with self.assertRaises(run_exp_0014.ExperimentError):
            run_exp_0014.validate_private_result_dict(private)
        unknown_literal = copy.deepcopy(result)
        unknown_literal["observation_code_counts"] = {"future.unknown": 1}
        with self.assertRaises(run_exp_0014.ExperimentError):
            run_exp_0014.validate_private_result_dict(unknown_literal)

    def test_input_validation_requires_three_direct_bounded_regular_epubs(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_inputs(root)
            validated = run_exp_0014.validate_private_inputs(inputs[:3])
            self.assertEqual(3, len(validated))
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.validate_private_inputs(inputs[:2])
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.validate_private_inputs(inputs)
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.validate_private_inputs(
                    [inputs[0], inputs[0], inputs[1]]
                )
            directory_input = root / "directory.epub"
            directory_input.mkdir()
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.validate_private_inputs(
                    [inputs[0], inputs[1], directory_input]
                )
            link = root / "link.epub"
            try:
                link.symlink_to(inputs[0])
            except OSError as exc:
                self.skipTest(f"symlink control unavailable: {type(exc).__name__}")
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.validate_private_inputs([inputs[0], inputs[1], link])
            oversized = root / "oversized.epub"
            with oversized.open("wb") as stream:
                stream.truncate(4 * 1024 * 1024 + 1)
            with self.assertRaises(run_exp_0014.ExperimentError):
                run_exp_0014.validate_private_inputs(
                    [inputs[0], inputs[1], oversized]
                )

    def test_private_workflow_runs_each_neutral_copy_once_and_writes_only_aggregate(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_inputs(root)[:3]
            temp_root = root / "runtime"
            result_path = root / "result.json"
            projections = [
                projection(),
                projection("review", observation="epub.script.present"),
                projection(
                    "stop",
                    observation="container.open_error",
                    finding="container.corrupt",
                ),
            ]
            with (
                mock.patch.object(run_exp_0014, "ALLOWED_TEMP_ROOT", temp_root),
                mock.patch.object(
                    run_exp_0014, "require_committed_preimage", return_value="a" * 40
                ),
                mock.patch.object(
                    run_exp_0014,
                    "run_synthetic_controls",
                    return_value={"status": "pass"},
                ),
                mock.patch.object(
                    run_exp_0014,
                    "run_intake_projection",
                    side_effect=projections,
                ) as intake,
            ):
                result = run_exp_0014.execute_private_diagnostic(
                    inputs,
                    confirmed_same_inputs=True,
                    temp_root=temp_root,
                    result_path=result_path,
                )

            self.assertEqual(3, intake.call_count)
            self.assertEqual(
                ["input-1.epub", "input-2.epub", "input-3.epub"],
                [call.args[0].name for call in intake.call_args_list],
            )
            self.assertEqual(3, result["intake_runs"])
            self.assertEqual(
                result, json.loads(result_path.read_text(encoding="utf-8"))
            )
            encoded = run_exp_0014.canonical_json(result)
            for value in (
                "private-title",
                '"snapshot":',
                '"sha256":"',
                '"size_bytes":',
            ):
                self.assertNotIn(value, encoded)
            self.assertFalse(any(temp_root.glob("private-*")))

    def test_partial_private_failure_cleans_up_and_writes_no_result(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_inputs(root)[:3]
            temp_root = root / "runtime"
            result_path = root / "result.json"
            with (
                mock.patch.object(run_exp_0014, "ALLOWED_TEMP_ROOT", temp_root),
                mock.patch.object(
                    run_exp_0014, "require_committed_preimage", return_value="a" * 40
                ),
                mock.patch.object(
                    run_exp_0014,
                    "run_synthetic_controls",
                    return_value={"status": "pass"},
                ),
                mock.patch.object(
                    run_exp_0014,
                    "run_intake_projection",
                    side_effect=[
                        projection(),
                        run_exp_0014.ExperimentError("synthetic partial failure"),
                    ],
                ),
            ):
                with self.assertRaises(run_exp_0014.ExperimentError):
                    run_exp_0014.execute_private_diagnostic(
                        inputs,
                        confirmed_same_inputs=True,
                        temp_root=temp_root,
                        result_path=result_path,
                    )

            self.assertFalse(result_path.exists())
            self.assertFalse(any(temp_root.glob("private-*")))
            self.assertEqual(
                [f"synthetic-{index}".encode("ascii") for index in range(1, 4)],
                [path.read_bytes() for path in inputs],
            )


if __name__ == "__main__":
    unittest.main()
