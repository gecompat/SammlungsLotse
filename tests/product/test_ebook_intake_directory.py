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

from sammlungslotse.ebook_intake.batch import BatchLimits  # noqa: E402
from sammlungslotse.ebook_intake.directory import (  # noqa: E402
    DIRECTORY_REPORT_SCHEMA,
    DirectoryIntakeService,
)


RUNNER = ROOT / "tools" / "run_ebook_intake.py"
STABLE = (
    ROOT
    / "tests"
    / "fixtures"
    / "ebook"
    / "test-0001"
    / "v0.2"
    / "cases"
    / "ingress-stable-minimal"
    / "stable.epub"
)


def run_directory(
    directory: Path, *, as_json: bool = True, extra: list[str] | None = None
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RUNNER)]
    if as_json:
        command.append("--json")
    command.extend(extra or [])
    command.extend(["--input-directory", str(directory)])
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


class EbookIntakeDirectoryTests(unittest.TestCase):
    def _tree(self, base: Path) -> Path:
        inbox = base / "inbox"
        nested = inbox / "nested"
        nested.mkdir(parents=True)
        shutil.copyfile(STABLE, nested / "stable.epub")
        (inbox / "unsupported.pdf").write_bytes(b"%PDF-1.7\nsynthetic\n")
        (inbox / "ignored.txt").write_text("synthetic", encoding="utf-8")
        return inbox

    def test_recursive_inventory_is_path_free_and_preserves_sources(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = self._tree(Path(temp))
            sources = [inbox / "nested" / "stable.epub", inbox / "unsupported.pdf"]
            before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}

            result = run_directory(inbox)

            after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
            payload = json.loads(result.stdout)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(DIRECTORY_REPORT_SCHEMA, payload["schema"])
            self.assertEqual("completed", payload["status"])
            self.assertEqual({"epub": 1, "pdf": 1}, payload["candidate_counts"])
            self.assertEqual([0, 1], [item["input_index"] for item in payload["items"]])
            self.assertEqual(
                ["continue_deep_read_only", "stop"],
                [item["result"]["next_action"] for item in payload["items"]],
            )
            self.assertFalse(payload["deep_read_only_requested"])
            self.assertEqual(before, after)
            for private in (str(inbox), "stable.epub", "unsupported.pdf", "nested"):
                self.assertNotIn(private, result.stdout)

    def test_local_labels_require_explicit_human_opt_in(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = self._tree(Path(temp))

            default = run_directory(inbox, as_json=False)
            opted_in = run_directory(inbox, as_json=False, extra=["--show-local-labels"])
            rejected = run_directory(inbox, extra=["--show-local-labels"])

            self.assertEqual(0, default.returncode, default.stderr)
            self.assertNotIn("stable.epub", default.stdout)
            self.assertNotIn("unsupported.pdf", default.stdout)
            self.assertEqual(0, opted_in.returncode, opted_in.stderr)
            self.assertIn("nested/stable.epub", opted_in.stdout)
            self.assertIn("unsupported.pdf", opted_in.stdout)
            self.assertNotIn(str(inbox), opted_in.stdout)
            self.assertEqual(2, rejected.returncode)
            self.assertEqual("", rejected.stdout)
            self.assertEqual("Eingabeparameter sind ungültig.\n", rejected.stderr)

    def test_candidate_limit_fails_closed_without_partial_selection(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = Path(temp) / "inbox"
            inbox.mkdir()
            for index in range(33):
                (inbox / f"candidate-{index:02d}.epub").write_bytes(b"synthetic")

            result = run_directory(inbox)

            payload = json.loads(result.stdout)
            self.assertEqual(3, result.returncode, result.stderr)
            self.assertEqual("limit_exceeded", payload["status"])
            self.assertFalse(payload["inventory_complete"])
            self.assertEqual(
                ["directory.candidate_limit_exceeded"], payload["reason_codes"]
            )
            self.assertEqual(33, payload["candidate_count"])
            self.assertEqual([], payload["items"])
            self.assertEqual(0, payload["summary"]["total_snapshot_bytes"])
            self.assertNotIn("candidate-", result.stdout)
            self.assertNotIn(str(inbox), result.stdout)

    def test_declared_byte_limit_prevents_any_triage(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = self._tree(Path(temp))

            report, labels = DirectoryIntakeService().inspect(
                inbox, limits=BatchLimits(max_total_input_bytes=1)
            )

            self.assertEqual("limit_exceeded", report.status)
            self.assertEqual((), report.items)
            self.assertEqual((), labels)
            self.assertEqual(0, report.total_snapshot_bytes)

    def test_links_are_skipped_without_following_them(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = self._tree(Path(temp))
            link = inbox / "linked.epub"
            try:
                os.symlink(inbox / "nested" / "stable.epub", link)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            report, labels = DirectoryIntakeService().inspect(inbox)

            self.assertEqual("completed", report.status)
            self.assertEqual(1, report.skipped_link_or_reparse_points)
            self.assertNotIn("linked.epub", labels)
            self.assertEqual(2, len(report.items))

    def test_linked_root_is_rejected_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = self._tree(Path(temp))
            root_link = Path(temp) / "linked-root"
            try:
                os.symlink(inbox, root_link, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            report, labels = DirectoryIntakeService().inspect(root_link)

            self.assertEqual("unavailable", report.status)
            self.assertEqual(("input.symlink_not_allowed",), report.reason_codes)
            self.assertEqual((), labels)
            self.assertEqual((), report.items)

    def test_unavailable_directory_stays_path_free_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            missing = Path(temp) / "private-directory"

            result = run_directory(missing)

            payload = json.loads(result.stdout)
            self.assertEqual(3, result.returncode, result.stderr)
            self.assertEqual("unavailable", payload["status"])
            self.assertEqual(["input.unavailable"], payload["reason_codes"])
            self.assertEqual([], payload["items"])
            self.assertNotIn(str(missing), result.stdout)
            self.assertNotIn("private-directory", result.stdout)

    def test_directory_mode_never_starts_deep_read_only_without_new_opt_in_contract(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            inbox = self._tree(Path(temp))
            result = run_directory(inbox, extra=["--deep-read-only"])

            self.assertEqual(2, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertEqual("Eingabeparameter sind ungültig.\n", result.stderr)


if __name__ == "__main__":
    unittest.main()
