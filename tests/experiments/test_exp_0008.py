from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0008"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0008.py"


def load_runner():
    specification = importlib.util.spec_from_file_location("run_exp_0008", RUNNER_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class Exp0008ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        cls.runtime_profile = cls.runner.CalibreRuntimeProfile.load(
            cls.runner.RUNTIME_PROFILE_PATH
        )

    def test_profile_is_exact_narrow_and_synthetic(self) -> None:
        self.runner.validate_profile(self.profile)
        self.assertEqual("EXP-0008", self.profile["artifact"])
        self.assertEqual(2, self.profile["repetitions"])
        self.assertTrue(self.profile["qualification_library"]["synthetic_only"])
        self.assertEqual(["EPUB"], self.profile["selection"]["formats"])
        self.assertFalse(self.profile["selection"]["direct_database_access"])
        self.assertFalse(self.profile["selection"]["source_writes"])

    def test_external_id_validation_rejects_ambiguity_and_overflow(self) -> None:
        self.assertEqual("1", self.runner.validate_external_id("1"))
        for value in ("", "0", "01", "1,3", "-1", "not-an-id", "1000000000"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.runner.validate_external_id(value)

    def test_command_is_shell_free_single_record_epub_export(self) -> None:
        workspace = SimpleNamespace(
            library=ROOT / "synthetic-library",
            output=ROOT / "synthetic-output",
        )
        arguments = self.runner.create_arguments(
            "sammlungslotse-exp0008-test",
            workspace,
            "1",
            self.profile,
            self.runtime_profile,
            self.profile["limits"]["max_export_file_bytes"],
        )
        self.assertNotIn("sh", arguments)
        self.assertNotIn("cmd", arguments)
        self.assertIn("--dont-update-metadata", arguments)
        self.assertIn("--dont-write-opf", arguments)
        self.assertIn("--dont-save-cover", arguments)
        self.assertIn("--dont-save-extra-files", arguments)
        self.assertEqual("1", arguments[-1])
        self.assertEqual(1, arguments.count("EPUB"))

    def test_output_contract_accepts_only_exact_regular_epub(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory)
            payload = b"synthetic-epub"
            (output / "1.epub").write_bytes(payload)
            inspected = self.runner.inspect_export_output(output, "1", 1024)
            self.assertEqual("valid", inspected["classification"])
            self.assertEqual("epub_only", inspected["kind"])
            self.assertEqual(self.runner.sha256_bytes(payload), inspected["sha256"])
            (output / "unexpected.opf").write_bytes(b"not-allowed")
            rejected = self.runner.inspect_export_output(output, "1", 1024)
            self.assertEqual("unexpected", rejected["classification"])

    def test_output_contract_rejects_wrong_name_and_size(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory)
            (output / "2.epub").write_bytes(b"wrong-id")
            wrong = self.runner.inspect_export_output(output, "1", 1024)
            self.assertEqual("unexpected", wrong["classification"])
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory)
            (output / "1.epub").write_bytes(b"x" * 1025)
            oversized = self.runner.inspect_export_output(output, "1", 1024)
            self.assertEqual("limit_exceeded", oversized["classification"])

    def test_preimage_binds_runner_profile_runtime_and_fixtures(self) -> None:
        preimage = self.runner.current_preimage()
        self.assertEqual(set(self.runner.PREIMAGE_FILES), set(preimage))
        self.assertEqual(64, len(next(iter(preimage.values()))))

    def test_runner_does_not_import_database_or_network_clients(self) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "import sqlite3",
            "import socket",
            "import urllib",
            "import requests",
            "import http.client",
        ):
            self.assertNotIn(forbidden, source)

    def test_empirical_result_is_complete(self) -> None:
        if not RESULT_PATH.exists():
            self.skipTest("result.json is created by the explicit empirical run")
        result = self.runner.validate_result(RESULT_PATH)
        self.assertEqual("qualified", result["status"])
        self.assertEqual(16, len(result["acceptance"]))
        self.assertTrue(all(result["acceptance"].values()))


if __name__ == "__main__":
    unittest.main()
