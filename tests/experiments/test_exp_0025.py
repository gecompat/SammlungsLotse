from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Exp0025Tests(unittest.TestCase):
    def test_result_is_anonymous_deterministic_and_bound_to_wi0020(self) -> None:
        result = json.loads((ROOT / "experiments" / "ebook" / "exp-0025" / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(("EXP-0025", "pass", True), (result["artifact"], result["status"], result["synthetic_only"]))
        self.assertEqual(2, len(result["libraries"]))
        self.assertEqual([1, 2], [item["library_position"] for item in result["libraries"]])
        for item in result["libraries"]:
            self.assertEqual(2, len(item["projection_sha256"]))
            self.assertEqual(1, len(set(item["projection_sha256"])))
        self.assertFalse(any("\\" in json.dumps(result) for _ in [0]))
        qualification = ROOT / "runtime" / "calibre-docker-readonly" / "qualification.json"
        self.assertEqual(hashlib.sha256(qualification.read_bytes()).hexdigest(), result["bindings"]["qualification_sha256"])


if __name__ == "__main__":
    unittest.main()
