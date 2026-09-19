from __future__ import annotations

import importlib.util
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("exp0020", ROOT / "tools" / "experiments" / "run_exp_0020.py")
assert SPEC is not None and SPEC.loader is not None
exp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exp)


class Exp0020Tests(unittest.TestCase):
    def test_fixture_set_is_synthetic_and_hashable(self) -> None:
        self.assertEqual(4, len(exp.FIXTURES))
        self.assertTrue(all((exp.CASES / item).is_file() for item in exp.FIXTURES))
        self.assertTrue(all(len(exp.sha256_file(exp.CASES / item)) == 64 for item in exp.FIXTURES))

    def test_qualification_target_requires_new_child_of_protected_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            allowed = Path(directory)
            self.assertEqual(
                (allowed / "new-task").resolve(),
                exp._new_child(allowed / "new-task", allowed),
            )
            with self.assertRaises(exp.QualificationError):
                exp._new_child(allowed, allowed)
            with self.assertRaises(exp.QualificationError):
                exp._new_child(allowed.parent / "outside", allowed)

    def test_public_result_guard_rejects_private_metadata_and_paths(self) -> None:
        self.assertTrue(exp._safe({"acceptance": {"clean": True}}))
        self.assertFalse(exp._safe({"title": "synthetic"}))
        self.assertFalse(exp._safe({"value": "C:\\private"}))

    def test_runtime_preflight_fails_before_any_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.object(
            exp.CalibrePodmanExecutor,
            "_runtime_and_image",
            side_effect=RuntimeError("synthetic unavailable"),
        ):
            with self.assertRaisesRegex(exp.QualificationError, "runtime_unavailable"):
                exp.qualify(Path(directory) / "new-task")


if __name__ == "__main__":
    unittest.main()
