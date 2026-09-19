from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.calibre_inventory.model import CalibreBook, CalibreEffects, CalibreInventoryReport
from sammlungslotse.ebook_review_plan.application import ReviewPlanService
from sammlungslotse.ebook_review_plan.cli import render_json


CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases"
CLI = ROOT / "tools" / "run_ebook_review_plan.py"


class FakeProjection:
    def __init__(self, report: CalibreInventoryReport) -> None:
        self.report = report
        self.calls = 0

    def project(self) -> CalibreInventoryReport:
        self.calls += 1
        return self.report


def projection(*books: CalibreBook, assessed: bool = True) -> CalibreInventoryReport:
    if not assessed:
        return CalibreInventoryReport.not_assessed(state="failed", reason="executor.failed")
    return CalibreInventoryReport(
        books=books,
        effects=CalibreEffects(True, False, False, True, True),
        execution_state="completed",
        library_snapshot_sha256=hashlib.sha256(b"synthetic-projection").hexdigest(),
        profile_id="synthetic-profile",
        provider_version="9.13.0",
        raw_output_sha256=hashlib.sha256(b"synthetic-output").hexdigest(),
        raw_output_size_bytes=16,
    )


class EbookReviewPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT)
        self.inbox = Path(self.temporary.name) / "private-inbox"
        self.inbox.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def add(self, source: str, name: str) -> Path:
        target = self.inbox / name
        shutil.copyfile(CASES / source, target)
        return target

    def test_review_plan_is_deterministic_path_free_and_candidate_bounded(self) -> None:
        source = self.add("ingress-stable-minimal/stable.epub", "private-stable.epub")
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        matching = tuple(
            CalibreBook(index, "Stabiler Eingang", ("Alex Beispiel",), ("de",), ("epub",))
            for index in range(1, 8)
        )
        provider = FakeProjection(projection(*matching))

        first = ReviewPlanService().build(self.inbox, provider)
        second = ReviewPlanService().build(self.inbox, provider)
        payload = render_json(first)

        self.assertEqual("completed", first.state)
        self.assertEqual(payload, render_json(second))
        self.assertEqual("review_candidate_present", first.items[0].review_class)
        self.assertEqual(5, len(first.items[0].candidates))
        self.assertEqual([1, 2, 3, 4, 5], [item.external_record_id for item in first.items[0].candidates])
        self.assertEqual(("metadata.author_equal", "metadata.language_equal", "metadata.title_equal"), first.items[0].candidates[0].reason_strategies)
        self.assertNotIn(str(self.inbox), payload)
        self.assertNotIn(source.name, payload)
        self.assertNotIn("Stabiler Eingang", payload)
        self.assertEqual(before, hashlib.sha256(source.read_bytes()).hexdigest())

    def test_blocked_and_non_epub_entries_never_receive_candidates(self) -> None:
        self.add("epub-active-or-remote/active-remote.epub", "blocked.epub")
        self.add("format-unknown/unknown.epub", "not-an-epub.pdf")
        provider = FakeProjection(projection(CalibreBook(1, "Any", (), (), ("epub",))))

        report = ReviewPlanService().build(self.inbox, provider)

        self.assertEqual(["review_ingress_blocked", "unsupported"], [item.review_class for item in report.items])
        self.assertTrue(all(not item.candidates for item in report.items))

    def test_unassessed_projection_returns_no_partial_plan(self) -> None:
        self.add("ingress-stable-minimal/stable.epub", "stable.epub")

        report = ReviewPlanService().build(self.inbox, FakeProjection(projection(assessed=False)))

        self.assertEqual("not_assessed", report.state)
        self.assertEqual((), report.items)
        self.assertEqual(("projection.not_safely_assessed",), report.reason_codes)

    def test_incomplete_inbox_does_not_start_library_projection(self) -> None:
        for index in range(33):
            (self.inbox / f"candidate-{index:02d}.epub").write_bytes(b"synthetic")
        provider = FakeProjection(projection())

        report = ReviewPlanService().build(self.inbox, provider)

        self.assertEqual("not_assessed", report.state)
        self.assertEqual(("inbox.inventory_incomplete",), report.reason_codes)
        self.assertEqual(0, provider.calls)

    def test_cli_missing_task_root_is_path_free_and_not_assessed(self) -> None:
        environment = dict(os.environ)
        environment.pop("SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT", None)
        result = subprocess.run(
            [sys.executable, str(CLI), str(self.inbox), "private-library", "--json"],
            cwd=ROOT, env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", check=False,
        )

        self.assertEqual(4, result.returncode)
        self.assertEqual("not_assessed", json.loads(result.stdout)["state"])
        self.assertIn("configuration.temp_root_missing", result.stdout)
        self.assertNotIn(str(self.inbox), result.stdout + result.stderr)
        self.assertNotIn("private-library", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
