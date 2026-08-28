from __future__ import annotations

import hashlib
import io
import json
import stat
import sys
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_intake import (  # noqa: E402
    LocalFileSnapshotReader,
    TriageLimits,
    TriageService,
)
from sammlungslotse.ebook_intake.cli import render_json  # noqa: E402
from sammlungslotse.ebook_intake.model import Snapshot  # noqa: E402
from sammlungslotse.ebook_intake.ports import SnapshotIssue  # noqa: E402
from sammlungslotse.ebook_intake.preflight import EpubPreflight  # noqa: E402


CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"


def case(relative: str) -> Path:
    return CASES / relative


def triage(relative: str, limits: TriageLimits | None = None):
    return TriageService().triage(
        LocalFileSnapshotReader(case(relative)), limits or TriageLimits()
    )


def codes(items) -> set[str]:
    return {item.code for item in items}


def snapshot_for(data: bytes) -> Snapshot:
    return Snapshot(
        data=data,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        suffix=".epub",
    )


class UnstableReader:
    def capture(self, limits: TriageLimits) -> Snapshot:
        raise SnapshotIssue(
            observation_code="snapshot.changed",
            finding_code="ingress.unstable",
            next_action="defer",
        )


class SymlinkLikePath:
    def lstat(self):
        return type("Stat", (), {"st_mode": stat.S_IFLNK})()


class ReparseLikePath:
    def lstat(self):
        return type(
            "Stat",
            (),
            {"st_mode": stat.S_IFREG, "st_file_attributes": 0x400},
        )()


class EbookIntakeDecisionTests(unittest.TestCase):
    def test_stable_epub_opens_only_the_deep_read_only_gate(self) -> None:
        report = triage("ingress-stable-minimal/stable.epub")

        self.assertEqual("supported", report.format_capability)
        self.assertEqual("continue_deep_read_only", report.next_action)
        self.assertTrue(report.deep_read_only_allowed)
        self.assertEqual({"format.epub"}, codes(report.findings))
        effects = report.to_dict()["effects"]
        self.assertTrue(all(value is False for value in effects.values()))

    def test_unknown_signature_abstains(self) -> None:
        report = triage("format-unknown/unknown.epub")

        self.assertEqual("unknown", report.format_capability)
        self.assertEqual("abstain", report.next_action)
        self.assertIn("format.extension_mismatch", codes(report.findings))

    def test_pdf_stops_as_unsupported_for_the_epub_path(self) -> None:
        report = triage("identity-multiformat-edition/edition.pdf")

        self.assertEqual("unsupported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn(
            "format.pdf_unsupported_for_deep_epub", codes(report.findings)
        )

    def test_corrupt_container_stops(self) -> None:
        report = triage("container-corrupt/corrupt.epub")

        self.assertEqual("unsupported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("container.corrupt", codes(report.findings))

    def test_parent_traversal_stops_without_extraction(self) -> None:
        report = triage("container-path-traversal/traversal.epub")

        self.assertEqual("supported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("security.path_traversal", codes(report.findings))

    def test_declared_expansion_over_custom_limit_stops(self) -> None:
        limits = replace(TriageLimits(), max_expanded_bytes=1024)
        report = triage("container-expansion-limit/expansion.epub", limits)

        self.assertEqual("supported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("resource.expansion_limit_exceeded", codes(report.findings))

    def test_protection_marker_stops(self) -> None:
        report = triage("protected-or-encrypted/protected.epub")

        self.assertEqual("unsupported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("container.encryption_xml", codes(report.observations))
        self.assertIn("protection.present", codes(report.findings))

    def test_script_and_remote_reference_require_review(self) -> None:
        report = triage("epub-active-or-remote/active-remote.epub")
        serialized = render_json(report)

        self.assertEqual("supported", report.format_capability)
        self.assertEqual("review", report.next_action)
        self.assertEqual(
            {"format.epub", "security.active_content", "security.remote_resource"},
            codes(report.findings),
        )
        self.assertNotIn("example.invalid", serialized)
        self.assertNotIn("https://", serialized)

    def test_changed_snapshot_defers_without_format_release(self) -> None:
        report = TriageService().triage(UnstableReader())

        self.assertIsNone(report.snapshot)
        self.assertEqual("unknown", report.format_capability)
        self.assertEqual("defer", report.next_action)
        self.assertFalse(report.deep_read_only_allowed)
        self.assertEqual({"ingress.unstable"}, codes(report.findings))

    def test_symlink_is_rejected_before_open(self) -> None:
        report = TriageService().triage(LocalFileSnapshotReader(SymlinkLikePath()))

        self.assertEqual("stop", report.next_action)
        self.assertIn("input.symlink_not_allowed", codes(report.findings))

    def test_windows_reparse_point_is_rejected_before_open(self) -> None:
        report = TriageService().triage(LocalFileSnapshotReader(ReparseLikePath()))

        self.assertEqual("stop", report.next_action)
        self.assertIn("input.reparse_not_allowed", codes(report.findings))

    def test_input_limit_stops_before_full_read(self) -> None:
        limits = replace(TriageLimits(), max_input_bytes=8)
        report = triage("ingress-stable-minimal/stable.epub", limits)

        self.assertEqual("stop", report.next_action)
        self.assertIn("resource.input_limit_exceeded", codes(report.findings))

    def test_archive_entry_limit_stops(self) -> None:
        limits = replace(TriageLimits(), max_archive_entries=1)
        report = triage("ingress-stable-minimal/stable.epub", limits)

        self.assertEqual("unknown", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("resource.entry_limit_exceeded", codes(report.findings))

    def test_markup_read_limits_stop(self) -> None:
        limits = replace(
            TriageLimits(),
            max_markup_entry_bytes=512,
            max_markup_total_bytes=512,
        )
        report = triage("ingress-stable-minimal/stable.epub", limits)

        self.assertEqual("supported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("resource.markup_limit_exceeded", codes(report.findings))

    def test_duplicate_mimetype_is_ambiguous_and_stops(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("mimetype", "application/epub+zip")
            archive.writestr("MIMETYPE", "application/epub+zip")
        data = buffer.getvalue()
        report = EpubPreflight().inspect(snapshot_for(data), TriageLimits())

        self.assertEqual("unknown", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("security.duplicate_entry", codes(report.findings))

    def test_zip_encryption_flag_stops_before_payload_read(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("mimetype", "application/epub+zip")
        data = bytearray(buffer.getvalue())
        local = data.index(b"PK\x03\x04")
        central = data.index(b"PK\x01\x02")
        data[local + 6] |= 0x01
        data[central + 8] |= 0x01

        report = EpubPreflight().inspect(snapshot_for(bytes(data)), TriageLimits())

        self.assertEqual("unsupported", report.format_capability)
        self.assertEqual("stop", report.next_action)
        self.assertIn("container.zip_encrypted", codes(report.observations))
        self.assertIn("protection.present", codes(report.findings))

    def test_json_is_deterministic_bounded_and_path_free(self) -> None:
        source = case("ingress-stable-minimal/stable.epub")
        first = render_json(TriageService().triage(LocalFileSnapshotReader(source)))
        second = render_json(TriageService().triage(LocalFileSnapshotReader(source)))
        payload = json.loads(first)

        self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))
        self.assertLessEqual(
            len(first.encode("utf-8")), TriageLimits().max_report_bytes
        )
        self.assertEqual("sammlungslotse/ebook-intake-report/v1", payload["schema"])
        self.assertNotIn(str(source), first)
        self.assertNotIn(source.name, first)
        self.assertNotIn("EPUB/package.opf", first)
        self.assertNotIn("Stabiler Eingang", first)

    def test_too_small_report_limit_fails_closed(self) -> None:
        limits = replace(TriageLimits(), max_report_bytes=1)
        report = triage("ingress-stable-minimal/stable.epub", limits)

        with self.assertRaises(RuntimeError):
            render_json(report)

    def test_end_to_end_read_preserves_original_hash(self) -> None:
        paths = [
            case("ingress-stable-minimal/stable.epub"),
            case("epub-active-or-remote/active-remote.epub"),
            case("container-corrupt/corrupt.epub"),
            case("format-unknown/unknown.epub"),
        ]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}

        for path in paths:
            TriageService().triage(LocalFileSnapshotReader(path))

        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)
