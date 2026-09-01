from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_intake.application import TriageService  # noqa: E402
from sammlungslotse.ebook_intake.batch import BATCH_REPORT_SCHEMA_V2  # noqa: E402
from sammlungslotse.ebook_intake.context import classify_document  # noqa: E402
from sammlungslotse.ebook_intake.deep_model import (  # noqa: E402
    COMBINED_REPORT_SCHEMA_V2,
)
from sammlungslotse.ebook_intake.model import (  # noqa: E402
    REPORT_SCHEMA_V2,
    ReviewContext,
    Snapshot,
)


RUNNER = ROOT / "tools" / "run_ebook_intake.py"
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"
EXP0016_CASES = ROOT / "experiments" / "ebook" / "exp-0016" / "cases.json"


class StaticReader:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def capture(self, limits):
        import hashlib

        del limits
        return Snapshot(
            data=self._data,
            size_bytes=len(self._data),
            sha256=hashlib.sha256(self._data).hexdigest(),
            suffix=".epub",
        )


def minimal_epub(document_type: str, snippet: str) -> bytes:
    suffix = {
        "css": ".css",
        "nav": ".xhtml",
        "opf": ".opf",
        "svg": ".svg",
        "xhtml": ".xhtml",
        "xml": ".xml",
    }[document_type]
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w") as archive:
        mimetype = zipfile.ZipInfo("mimetype")
        mimetype.compress_type = zipfile.ZIP_STORED
        archive.writestr(mimetype, b"application/epub+zip")
        archive.writestr(f"OEBPS/case{suffix}", snippet.encode("utf-8"))
    return output.getvalue()


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *arguments],
        cwd=ROOT,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


class EbookIntakeV2Tests(unittest.TestCase):
    def test_product_classifier_matches_all_48_exp0016_oracles_twice(self) -> None:
        manifest = json.loads(EXP0016_CASES.read_text(encoding="utf-8"))
        for repetition in range(2):
            for case in manifest["cases"]:
                with self.subTest(repetition=repetition, case=case["case_id"]):
                    actual = classify_document(case["document_type"], case["snippet"])
                    self.assertEqual(case["expected_context"], actual.context)
                    self.assertEqual(case["expected_scheme_group"], actual.scheme_group)

    def test_review_context_model_fails_closed_for_empty_or_unknown_classes(self) -> None:
        empty = ReviewContext.for_review(set())
        unknown = ReviewContext.for_review({"future.context"})

        self.assertEqual("ambiguous_or_unknown", empty.assessment)
        self.assertEqual(("ambiguous_or_deceptive",), empty.classes)
        self.assertEqual(empty, unknown)
        with self.assertRaises(ValueError):
            ReviewContext("classified", ("future.context",))

    def test_default_and_explicit_v1_are_byte_identical_and_v2_is_opt_in(self) -> None:
        path = CASES / "epub-active-or-remote" / "active-remote.epub"
        default = run_cli("--json", str(path))
        explicit = run_cli("--json", "--report-version", "v1", str(path))
        v2 = run_cli("--json", "--report-version", "v2", str(path))

        self.assertEqual(0, default.returncode, default.stderr)
        self.assertEqual(default.stdout.encode("utf-8"), explicit.stdout.encode("utf-8"))
        payload = json.loads(v2.stdout)
        self.assertEqual(REPORT_SCHEMA_V2, payload["schema"])
        self.assertEqual("review", payload["next_action"])
        self.assertFalse(payload["deep_read_only_allowed"])
        self.assertEqual(
            {
                "assessment": "classified",
                "classes": [
                    "content.active_or_submission",
                    "publication.automatic_remote_resource",
                ],
            },
            payload["review_context"],
        )

    def test_report_version_requires_json_and_unknown_version_is_path_free(self) -> None:
        private = "C:/private-library/secret-title.epub"
        missing_json = run_cli("--report-version", "v2", private)
        unknown = run_cli("--json", "--report-version", "v9", private)

        for result in (missing_json, unknown):
            self.assertEqual(2, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertEqual("Eingabeparameter sind ungültig.\n", result.stderr)
            self.assertNotIn(private, result.stderr)

    def test_all_six_public_classes_have_review_preserving_product_controls(self) -> None:
        controls = {
            "content.user_activated_hyperlink": (
                "xhtml",
                '<html><body><a href="https://example.invalid/read">x</a></body></html>',
            ),
            "package.optional_linked_resource": (
                "opf",
                '<package><metadata><link rel="record" href="https://example.invalid/r"/></metadata></package>',
            ),
            "publication.automatic_remote_resource": (
                "xhtml",
                '<html><body><img src="https://example.invalid/i"/></body></html>',
            ),
            "content.active_or_submission": (
                "xhtml",
                '<html><body><script src="https://example.invalid/s"></script></body></html>',
            ),
            "reference.local_or_other_scheme": (
                "xhtml",
                '<html><body><script src="mailto:local@example.invalid"></script></body></html>',
            ),
            "ambiguous_or_deceptive": (
                "xhtml",
                '<html><head><link rel="next stylesheet" href="https://example.invalid/m"/></head></html>',
            ),
        }

        for expected, (document_type, snippet) in controls.items():
            with self.subTest(expected=expected):
                report = TriageService().triage(
                    StaticReader(minimal_epub(document_type, snippet))
                )
                payload = report.to_dict_v2()
                self.assertEqual("review", report.next_action)
                self.assertFalse(report.deep_read_only_allowed)
                self.assertIn(expected, payload["review_context"]["classes"])
                if expected == "ambiguous_or_deceptive":
                    self.assertEqual(
                        "ambiguous_or_unknown",
                        payload["review_context"]["assessment"],
                    )

    def test_unknown_surface_falls_back_and_nonreview_is_not_applicable(self) -> None:
        unknown = TriageService().triage(
            StaticReader(
                minimal_epub(
                    "xml", '<root href="https://example.invalid/unknown"/>'
                )
            )
        )
        stable = CASES / "ingress-stable-minimal" / "stable.epub"
        stable_payload = json.loads(
            run_cli("--json", "--report-version", "v2", str(stable)).stdout
        )

        self.assertEqual("review", unknown.next_action)
        self.assertEqual(
            {
                "assessment": "ambiguous_or_unknown",
                "classes": ["ambiguous_or_deceptive"],
            },
            unknown.to_dict_v2()["review_context"],
        )
        self.assertEqual(
            {"assessment": "not_applicable", "classes": []},
            stable_payload["review_context"],
        )

    def test_batch_and_combined_v2_keep_nested_triage_contract(self) -> None:
        review = CASES / "epub-active-or-remote" / "active-remote.epub"
        stable = CASES / "ingress-stable-minimal" / "stable.epub"
        batch = run_cli(
            "--json", "--report-version", "v2", str(review), str(stable)
        )
        combined = run_cli(
            "--json",
            "--report-version",
            "v2",
            "--deep-read-only",
            "--deep-temp-root",
            "C:/rep/tmp/SammlungsLotse/wi-0014-test-must-not-exist",
            str(review),
        )

        batch_payload = json.loads(batch.stdout)
        combined_payload = json.loads(combined.stdout)
        self.assertEqual(0, batch.returncode, batch.stderr)
        self.assertEqual(BATCH_REPORT_SCHEMA_V2, batch_payload["schema"])
        self.assertEqual(
            [REPORT_SCHEMA_V2, REPORT_SCHEMA_V2],
            [item["result"]["schema"] for item in batch_payload["items"]],
        )
        self.assertEqual(4, combined.returncode, combined.stderr)
        self.assertEqual(COMBINED_REPORT_SCHEMA_V2, combined_payload["schema"])
        self.assertEqual(REPORT_SCHEMA_V2, combined_payload["triage"]["schema"])
        self.assertEqual("review", combined_payload["triage"]["next_action"])
        self.assertFalse(
            combined_payload["deep_read_only"]["effects"]["process_started"]
        )
        self.assertEqual(
            ["gate.not_open"], combined_payload["deep_read_only"]["reason_codes"]
        )


if __name__ == "__main__":
    unittest.main()
