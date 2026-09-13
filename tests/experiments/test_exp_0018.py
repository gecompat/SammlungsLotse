from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "experiments" / "run_exp_0018.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0018", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
EXP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EXP
SPEC.loader.exec_module(EXP)


class Exp0018Tests(unittest.TestCase):
    def test_case_matrix_is_complete_and_bound(self) -> None:
        self.assertEqual(
            [
                "continue_only",
                "review_only",
                "unsupported_only",
                "mixed",
                "candidate_limit",
                "unavailable",
            ],
            [entry["key"] for entry in EXP.load_cases()],
        )

    def test_runner_is_deterministic_and_cleans_its_root(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            root = Path(temporary) / "task"
            first = EXP.execute(root)
            second = EXP.execute(root)
            self.assertFalse(root.exists())
        self.assertEqual(first, second)
        self.assertEqual(6, first["case_count"])
        self.assertEqual("not_used", first["network"])
        self.assertFalse(first["product_code_changed"])

    def test_result_validator_rejects_unbound_case(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            path = Path(temporary) / "result.json"
            path.write_text(json.dumps({"schema": EXP.SCHEMA, "case_count": 6, "cases": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                EXP.validate_result(path)


if __name__ == "__main__":
    unittest.main()
