from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_identity import IdentityCandidateService  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0010.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0010_guardrail", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("EXP-0010 runner cannot be loaded")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

MANIFEST = RUNNER.validate_manifest(
    json.loads(
        (ROOT / "experiments" / "ebook" / "exp-0010" / "case-manifest.json").read_text(
            encoding="utf-8"
        )
    )
)
CASES = {case["case_key"]: case for case in MANIFEST["cases"]}
FALSE_SAME_CASES = (
    "same-primary-strong-content-conflict",
    "shared-typed-additional-different-primary",
    "shared-untyped-additional-different-primary",
)


def stage(report, name: str):
    return next(item for item in report.stages if item.stage == name)


class EbookIdentityFalseSameGuardrailTests(unittest.TestCase):
    def compare_case(self, case_key: str):
        temporary = tempfile.TemporaryDirectory(prefix=f"wi-0012-{case_key}-")
        self.addCleanup(temporary.cleanup)
        paths = RUNNER.materialize_pair(
            MANIFEST,
            CASES[case_key],
            Path(temporary.name) / "pair",
        )
        return IdentityCandidateService().compare(
            LocalFileSnapshotReader(paths[0]),
            LocalFileSnapshotReader(paths[1]),
        )

    def test_identifier_overlap_cannot_override_different_representation(self) -> None:
        for case_key in FALSE_SAME_CASES:
            with self.subTest(case=case_key):
                report = self.compare_case(case_key)

                self.assertEqual("different", stage(report, "representation").decision)
                self.assertNotEqual("candidate_same", stage(report, "edition").decision)
                self.assertNotEqual("candidate_same", stage(report, "work").decision)
                self.assertIn(
                    "metadata.identifiers_overlap",
                    stage(report, "edition").positive_evidence,
                )

    def test_same_representation_keeps_qualified_edition_and_work_candidate(self) -> None:
        report = self.compare_case("same-primary-minor-revision")

        self.assertEqual("candidate_same", stage(report, "representation").decision)
        self.assertEqual("candidate_same", stage(report, "edition").decision)
        self.assertEqual(
            "identity.edition.identifier_representation_metadata",
            stage(report, "edition").rule_id,
        )
        self.assertEqual("candidate_same", stage(report, "work").decision)


if __name__ == "__main__":
    unittest.main()
