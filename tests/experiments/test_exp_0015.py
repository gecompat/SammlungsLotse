"""Contract tests for the EXP-0015 private remote-context experiment."""

from __future__ import annotations

import ast
import copy
import inspect
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.experiments import run_exp_0015
from tools.experiments import validate_exp_0015_result


def test_temp_base() -> Path:
    if os.name == "nt":
        value = Path(r"C:\rep\tmp\SammlungsLotse\exp-0015-tests")
    else:
        value = Path(tempfile.gettempdir()) / "SammlungsLotse-exp-0015-tests"
    value.mkdir(parents=True, exist_ok=True)
    return value


def projection(
    *contexts: str,
    remote: bool = True,
    unclassified: bool = False,
) -> dict[str, object]:
    return {
        "contexts": sorted(contexts),
        "remote_reference_present": remote,
        "unclassified": unclassified,
    }


class Exp0015Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = run_exp_0015.load_json(run_exp_0015.PROFILE_PATH)
        cls.result = validate_exp_0015_result.validate(
            validate_exp_0015_result.RESULT_PATH
        )

    def make_epubs(self, root: Path, count: int = 4) -> list[Path]:
        result = []
        for index in range(count):
            value = root / f"private-title-{index + 1}.epub"
            run_exp_0015._write_synthetic_epub(
                value,
                run_exp_0015._context_entries("content.navigation"),
            )
            result.append(value)
        return result

    def test_profile_binds_exact_private_product_free_boundary(self) -> None:
        self.assertEqual("EXP-0015", self.profile["artifact"])
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
            "--confirm-same-exp-0014-inputs",
            self.profile["input_contract"]["confirmation_flag"],
        )
        implementation = self.profile["implementation"]
        self.assertTrue(implementation["git_preimage_read_only_process"])
        self.assertTrue(
            all(
                value is False
                for key, value in implementation.items()
                if key != "git_preimage_read_only_process"
            )
        )
        self.assertEqual(
            list(run_exp_0015.CONTEXT_CLASSES),
            self.profile["parser"]["context_classes"],
        )
        self.assertEqual(2, self.profile["limits"]["minimum_group_size"])
        self.assertNotIn(
            "experiments/ebook/exp-0015/result.json",
            run_exp_0015.PREIMAGE_FILES,
        )
        self.assertTrue(run_exp_0015.RESULT_PATH.exists())
        self.assertEqual("pass", self.result["status"])
        self.assertEqual(
            {"content.navigation": 3}, self.result["context_input_counts"]
        )

    def test_runtime_bindings_match_bound_files(self) -> None:
        bindings = self.profile["runtime_bindings"]["files"]
        historical = validate_exp_0015_result.historical_preimage()
        self.assertEqual(len(run_exp_0015.RUNTIME_LOCATORS), len(bindings))
        for binding, locator in zip(
            bindings, run_exp_0015.RUNTIME_LOCATORS, strict=True
        ):
            self.assertEqual(locator, binding["locator"])
            self.assertEqual(
                historical[locator],
                binding["sha256"],
            )

    def test_runner_has_no_network_database_discovery_or_product_import(self) -> None:
        source = Path(run_exp_0015.__file__).read_text(encoding="utf-8")
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
        self.assertNotIn("sammlungslotse", imports)
        self.assertNotIn("metadata.db", source)
        input_source = inspect.getsource(run_exp_0015.validate_private_inputs)
        for forbidden in ("os.walk", "glob(", "rglob(", "iterdir("):
            self.assertNotIn(forbidden, input_source)
        scan_source = inspect.getsource(run_exp_0015.scan_epub)
        self.assertNotIn("subprocess", scan_source)
        self.assertNotIn("extract", scan_source)
        self.assertIn('action="append"', inspect.getsource(run_exp_0015.parser))

    def test_git_process_is_read_only_and_receives_no_private_arguments(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"value\n", stderr=b""
        )
        with mock.patch.object(
            run_exp_0015.subprocess, "run", return_value=completed
        ) as invoked:
            self.assertEqual(b"value\n", run_exp_0015.git_output("rev-parse", "HEAD"))
        invoked.assert_called_once_with(
            ["git", "rev-parse", "HEAD"],
            cwd=run_exp_0015.ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_context_taxonomy_and_nonremote_controls(self) -> None:
        cases = {
            "package.metadata_or_link": (
                b"<package><link HREF=\"HTTPS://example.invalid/x\"/></package>",
                ".opf",
            ),
            "content.navigation": (
                b"<html><a href='https://example.invalid/x'>x</a></html>",
                ".xhtml",
            ),
            "content.embedded_resource": (
                b"<html><video poster=\"http://example.invalid/x\"/></html>",
                ".html",
            ),
            "stylesheet.resource": (
                b"@import URL('https://example.invalid/x');",
                ".css",
            ),
            "svg.resource": (
                b"<svg><use href='https://example.invalid/x'/></svg>",
                ".svg",
            ),
            "markup.other_attribute": (
                b"<html><custom src='https://example.invalid/x'/></html>",
                ".xhtml",
            ),
            "text_or_script.literal": (
                b"<html><script>const x=\"href='https://example.invalid/x'\";</script></html>",
                ".xhtml",
            ),
        }
        for expected, (payload, suffix) in cases.items():
            with self.subTest(expected=expected):
                actual = run_exp_0015.classify_markup(payload, suffix)
                self.assertEqual([expected], actual["contexts"])
                self.assertTrue(actual["remote_reference_present"])
                self.assertFalse(actual["unclassified"])
        nonremote = run_exp_0015.classify_markup(
            b"<a href='#x'><img src='data:image/png;base64,AA=='/></a>",
            ".xhtml",
        )
        self.assertEqual(projection(remote=False), nonremote)
        unknown = run_exp_0015.classify_markup(
            b"<!-- href='https://example.invalid/private' -->", ".xhtml"
        )
        self.assertEqual(projection(remote=True, unclassified=True), unknown)
        for inconsistent in (
            projection("content.navigation", remote=False),
            projection(remote=True),
        ):
            with self.assertRaises(run_exp_0015.ExperimentError):
                run_exp_0015.validate_projection(inconsistent)

    def test_group_aggregation_suppresses_rare_class_literal(self) -> None:
        aggregate = run_exp_0015.aggregate_projections(
            [
                projection("content.navigation", "svg.resource"),
                projection("content.navigation"),
                projection("markup.other_attribute"),
            ]
        )
        self.assertEqual(
            {"content.navigation": 2}, aggregate["context_input_counts"]
        )
        self.assertTrue(aggregate["suppressed_context_present"])
        encoded = run_exp_0015.canonical_json(aggregate)
        self.assertNotIn("svg.resource", encoded)
        self.assertNotIn("markup.other_attribute", encoded)
        self.assertEqual("shared_context_present", aggregate["qualification"])

    def test_result_contract_rejects_partial_private_and_inconsistent_values(self) -> None:
        aggregate = run_exp_0015.aggregate_projections(
            [
                projection("content.navigation"),
                projection("content.navigation"),
                projection("content.navigation"),
            ]
        )
        result = run_exp_0015.build_private_result(
            aggregate,
            input_count=3,
            parser_runs=3,
            execution_complete=True,
            source_unchanged=True,
            cleanup_complete=True,
        )
        self.assertEqual(run_exp_0015.RESULT_FIELDS, set(result))
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
            with self.assertRaises(run_exp_0015.ExperimentError):
                run_exp_0015.build_private_result(
                    aggregate, input_count=3, parser_runs=3, **arguments
                )
        for field, private_value in (
            ("url", "https://example.invalid/private"),
            ("path", r"C:\private\title.epub"),
            ("sha256", "a" * 64),
        ):
            unsafe = copy.deepcopy(result)
            unsafe[field] = private_value
            with self.assertRaises(run_exp_0015.ExperimentError):
                run_exp_0015.validate_private_result_dict(unsafe)
        inconsistent = copy.deepcopy(result)
        inconsistent["qualification"] = "no_shared_context"
        with self.assertRaises(run_exp_0015.ExperimentError):
            run_exp_0015.validate_private_result_dict(inconsistent)
        impossible_count = copy.deepcopy(result)
        impossible_count["remote_reference_input_count"] = 1
        impossible_count["qualification"] = "inconclusive"
        impossible_count["status"] = "inconclusive"
        with self.assertRaises(run_exp_0015.ExperimentError):
            run_exp_0015.validate_private_result_dict(impossible_count)

    def test_input_validation_requires_three_direct_bounded_regular_epubs(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_epubs(root)
            self.assertEqual(
                3, len(run_exp_0015.validate_private_inputs(inputs[:3]))
            )
            for invalid in (
                inputs[:2],
                inputs,
                [inputs[0], inputs[0], inputs[1]],
            ):
                with self.assertRaises(run_exp_0015.ExperimentError):
                    run_exp_0015.validate_private_inputs(invalid)
            directory = root / "directory.epub"
            directory.mkdir()
            with self.assertRaises(run_exp_0015.ExperimentError):
                run_exp_0015.validate_private_inputs(
                    [inputs[0], inputs[1], directory]
                )
            oversized = root / "oversized.epub"
            with oversized.open("wb") as stream:
                stream.truncate(4 * 1024 * 1024 + 1)
            with self.assertRaises(run_exp_0015.ExperimentError):
                run_exp_0015.validate_private_inputs(
                    [inputs[0], inputs[1], oversized]
                )

    def test_synthetic_controls_cover_all_boundaries_and_cleanup(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            temp_root = Path(directory) / "runtime"
            with mock.patch.object(run_exp_0015, "ALLOWED_TEMP_ROOT", temp_root):
                summary = run_exp_0015.run_synthetic_controls(
                    temp_root, self.profile
                )
        self.assertEqual("pass", summary["status"])
        self.assertEqual(len(run_exp_0015.CONTEXT_CLASSES), summary["context_classes"])
        self.assertEqual(len(run_exp_0015.NEGATIVE_CONTROLS), summary["negative_controls"])
        self.assertTrue(summary["repetitions_identical"])
        self.assertTrue(summary["cleanup_complete"])

    def test_private_workflow_uses_neutral_copies_once_and_writes_aggregate(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_epubs(root)[:3]
            temp_root = root / "runtime"
            result_path = root / "result.json"
            original = [path.read_bytes() for path in inputs]
            with (
                mock.patch.object(run_exp_0015, "ALLOWED_TEMP_ROOT", temp_root),
                mock.patch.object(
                    run_exp_0015, "require_committed_preimage", return_value="a" * 40
                ),
                mock.patch.object(
                    run_exp_0015, "validate_contract", return_value=self.profile
                ),
                mock.patch.object(
                    run_exp_0015,
                    "run_synthetic_controls",
                    return_value={"status": "pass"},
                ),
                mock.patch.object(
                    run_exp_0015,
                    "scan_epub",
                    wraps=run_exp_0015.scan_epub,
                ) as scanner,
            ):
                result = run_exp_0015.execute_private_diagnostic(
                    inputs,
                    confirmed_same_inputs=True,
                    temp_root=temp_root,
                    result_path=result_path,
                )
            self.assertEqual(3, scanner.call_count)
            self.assertEqual(
                ["input-1.epub", "input-2.epub", "input-3.epub"],
                [call.args[0].name for call in scanner.call_args_list],
            )
            self.assertEqual(
                result, json.loads(result_path.read_text(encoding="utf-8"))
            )
            self.assertEqual(original, [path.read_bytes() for path in inputs])
            self.assertFalse(any(temp_root.glob("private-*")))
            encoded = run_exp_0015.canonical_json(result)
            for forbidden in ("private-title", "https://", '"sha256"', '"path"'):
                self.assertNotIn(forbidden, encoded)

    def test_partial_failure_cleans_up_and_writes_no_result(self) -> None:
        with tempfile.TemporaryDirectory(dir=test_temp_base()) as directory:
            root = Path(directory)
            inputs = self.make_epubs(root)[:3]
            temp_root = root / "runtime"
            result_path = root / "result.json"
            with (
                mock.patch.object(run_exp_0015, "ALLOWED_TEMP_ROOT", temp_root),
                mock.patch.object(
                    run_exp_0015, "require_committed_preimage", return_value="a" * 40
                ),
                mock.patch.object(
                    run_exp_0015, "validate_contract", return_value=self.profile
                ),
                mock.patch.object(
                    run_exp_0015,
                    "run_synthetic_controls",
                    return_value={"status": "pass"},
                ),
                mock.patch.object(
                    run_exp_0015,
                    "scan_epub",
                    side_effect=[
                        projection("content.navigation"),
                        run_exp_0015.ExperimentError("synthetic partial failure"),
                    ],
                ),
            ):
                with self.assertRaises(run_exp_0015.ExperimentError):
                    run_exp_0015.execute_private_diagnostic(
                        inputs,
                        confirmed_same_inputs=True,
                        temp_root=temp_root,
                        result_path=result_path,
                    )
            self.assertFalse(result_path.exists())
            self.assertFalse(any(temp_root.glob("private-*")))


if __name__ == "__main__":
    unittest.main()
