from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_identity import IdentityCandidateService  # noqa: E402
from sammlungslotse.ebook_identity.cli import render_json  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases"
CLI = ROOT / "tools" / "run_ebook_identity.py"


def fixture(relative: str) -> Path:
    return CASES / relative


def compare(first: str, second: str):
    return IdentityCandidateService().compare(
        LocalFileSnapshotReader(fixture(first)),
        LocalFileSnapshotReader(fixture(second)),
    )


def stages(report) -> dict[str, object]:
    return {stage.stage: stage for stage in report.stages}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EbookIdentityContractTests(unittest.TestCase):
    def test_byte_equal_pair_stays_distinct_and_exact(self) -> None:
        report = compare(
            "identity-byte-equal/source-a/same.epub",
            "identity-byte-equal/source-b/renamed.epub",
        )

        self.assertEqual("completed", report.assessment)
        self.assertEqual("exact_byte_match", report.overall)
        self.assertEqual((1, 2), tuple(item.input_index for item in report.inputs))
        self.assertEqual("candidate_same", stages(report)["byte"].decision)
        self.assertTrue(all(value is False for value in report.to_dict()["effects"].values()))

    def test_repackaged_pair_is_representation_candidate(self) -> None:
        report = compare(
            "identity-repackaged/package-a.epub",
            "identity-repackaged/package-b.epub",
        )
        by_stage = stages(report)

        self.assertEqual("representation_candidate", report.overall)
        self.assertEqual("different", by_stage["byte"].decision)
        self.assertEqual("candidate_same", by_stage["package"].decision)
        self.assertEqual("candidate_same", by_stage["representation"].decision)

    def test_title_collision_is_not_a_same_work_candidate(self) -> None:
        report = compare(
            "identity-title-collision/work-a.epub",
            "identity-title-collision/work-b.epub",
        )
        by_stage = stages(report)

        self.assertEqual("abstain", report.overall)
        self.assertEqual("abstain", by_stage["edition"].decision)
        self.assertEqual("different", by_stage["work"].decision)
        self.assertIn("metadata.creators_conflict", by_stage["work"].negative_evidence)

    def test_translation_is_related_but_not_the_same_edition(self) -> None:
        report = compare(
            "identity-edition-vs-translation/source-en.epub",
            "identity-edition-vs-translation/translation-de.epub",
        )
        by_stage = stages(report)

        self.assertEqual("related_work_candidate", report.overall)
        self.assertEqual("different", by_stage["edition"].decision)
        self.assertEqual("candidate_related", by_stage["work"].decision)
        self.assertIn("metadata.languages_conflict", by_stage["edition"].negative_evidence)
        self.assertIn("metadata.work_references_overlap", by_stage["work"].positive_evidence)

    def test_sample_and_full_are_not_the_same_edition(self) -> None:
        report = compare(
            "edition-sample-vs-full/sample.epub",
            "edition-sample-vs-full/full.epub",
        )
        by_stage = stages(report)

        self.assertEqual("different", by_stage["edition"].decision)
        self.assertIn("metadata.sample_full_conflict", by_stage["edition"].negative_evidence)
        self.assertEqual("abstain", by_stage["work"].decision)

    def test_preflight_failure_is_visible_without_partial_identity_data(self) -> None:
        report = compare(
            "container-path-traversal/traversal.epub",
            "identity-byte-equal/source-a/same.epub",
        )

        self.assertEqual("not_assessed", report.assessment)
        self.assertEqual("not_assessed", report.overall)
        self.assertEqual((), report.inputs)
        self.assertEqual((), report.stages)
        self.assertEqual(("input_1.preflight_gate_not_open",), report.reason_codes)

    def test_json_is_deterministic_and_evidence_channels_are_separate(self) -> None:
        report = compare(
            "identity-edition-vs-translation/source-en.epub",
            "identity-edition-vs-translation/translation-de.epub",
        )
        first = render_json(report)
        second = render_json(report)
        value = json.loads(first)

        self.assertEqual(first, second)
        self.assertEqual(
            "sammlungslotse/ebook-identity-candidate-report/v1", value["schema"]
        )
        for stage in value["stages"]:
            self.assertIn("positive_evidence", stage)
            self.assertIn("negative_evidence", stage)
            self.assertIn("missing_evidence", stage)
        missing_report = compare(
            "identity-repackaged/package-a.epub",
            "identity-repackaged/package-b.epub",
        )
        self.assertIn(
            "metadata.work_references_missing",
            stages(missing_report)["edition"].missing_evidence,
        )


class EbookIdentityCliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )

    def test_actual_json_cli_is_path_free_deterministic_and_read_only(self) -> None:
        left = fixture("identity-repackaged/package-a.epub")
        right = fixture("identity-repackaged/package-b.epub")
        before = (sha256(left), sha256(right))
        arguments = ("--json", str(left), str(right))

        first = self.run_cli(*arguments)
        second = self.run_cli(*arguments)

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual("representation_candidate", json.loads(first.stdout)["overall"])
        serialized = first.stdout + first.stderr + second.stdout + second.stderr
        for forbidden in (str(left), str(right), left.name, right.name, str(ROOT)):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(before, (sha256(left), sha256(right)))

    def test_actual_human_cli_is_path_free(self) -> None:
        left = fixture("identity-byte-equal/source-a/same.epub")
        right = fixture("identity-byte-equal/source-b/renamed.epub")

        completed = self.run_cli(str(left), str(right))

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("EPUB-Identitätskandidatenbericht", completed.stdout)
        self.assertIn("Eingang 1", completed.stdout)
        self.assertNotIn(left.name, completed.stdout + completed.stderr)
        self.assertNotIn(right.name, completed.stdout + completed.stderr)

    def test_same_locator_is_rejected_without_disclosure(self) -> None:
        source = fixture("identity-byte-equal/source-a/same.epub")

        completed = self.run_cli("--json", str(source), str(source))

        self.assertEqual(3, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertNotIn(str(source), completed.stderr)
        self.assertNotIn(source.name, completed.stderr)

    def test_closed_preflight_exits_not_assessed(self) -> None:
        unsafe = fixture("protected-or-encrypted/protected.epub")
        safe = fixture("identity-byte-equal/source-a/same.epub")

        completed = self.run_cli("--json", str(unsafe), str(safe))

        self.assertEqual(4, completed.returncode, completed.stderr)
        self.assertEqual("not_assessed", json.loads(completed.stdout)["assessment"])
        self.assertNotIn(unsafe.name, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
