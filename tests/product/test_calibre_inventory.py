from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.calibre_inventory.cli import render_human, render_json  # noqa: E402
from sammlungslotse.calibre_inventory.model import (  # noqa: E402
    CalibreEffects,
    CalibreInventoryReport,
)
from sammlungslotse.calibre_inventory.ports import InventoryExecution  # noqa: E402
from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402
from sammlungslotse.calibre_inventory.provider import (  # noqa: E402
    CalibreCliProvider,
    parse_calibre_output,
)
from sammlungslotse.calibre_inventory.workspace import (  # noqa: E402
    MARKER_NAME,
    LibraryWorkspaceManager,
    snapshot_library,
)


PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
CLI = ROOT / "tools" / "run_calibre_inventory.py"


def raw_report() -> bytes:
    return json.dumps(
        [
            {
                "id": 2,
                "title": "Zweiter Titel",
                "authors": "Bea Beispiel, Cid Beispiel",
                "languages": ["de"],
                "formats": ["/library/Bea/Zweiter Titel (2)/book.PDF", "/library/Bea/Zweiter Titel (2)/book.EPUB"],
            },
            {
                "id": 1,
                "title": "Erster Titel",
                "authors": ["Ada Beispiel"],
                "languages": "de,en",
                "formats": [],
            },
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


class FakeExecutor:
    def __init__(self, result: InventoryExecution, mutate_source: Path | None = None) -> None:
        self.result = result
        self.mutate_source = mutate_source
        self.calls = 0
        self.library_seen: Path | None = None

    def execute(self, workspace):
        self.calls += 1
        self.library_seen = workspace.library
        if self.mutate_source is not None:
            self.mutate_source.write_bytes(b"changed")
        return self.result


class CleanupFailingWorkspace:
    def __init__(self, delegate) -> None:
        self.delegate = delegate

    def recover(self):
        return self.delegate.recover()

    def create(self):
        return self.delegate.create()

    def source_unchanged(self, workspace):
        return self.delegate.source_unchanged(workspace)

    def cleanup(self, workspace):
        self.delegate.cleanup(workspace)
        raise RuntimeError("synthetic cleanup failure")


class CalibreInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = CalibreRuntimeProfile.load(PROFILE_PATH)
        configured = os.environ.get("SAMMLUNGSLOTSE_TEST_TEMP_ROOT")
        parent = Path(configured) if configured else Path("C:/rep/tmp/SammlungsLotse/unit-tests") if os.name == "nt" and Path("C:/rep").is_dir() else Path(tempfile.gettempdir()) / "sammlungslotse-unit-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.temporary.name)
        self.library = self.root / "library"
        self.library.mkdir()
        (self.library / "metadata.db").write_bytes(b"synthetic metadata")
        book = self.library / "Ada Beispiel" / "Erster Titel (1)"
        book.mkdir(parents=True)
        (book / "book.epub").write_bytes(b"synthetic epub")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_profile_is_exact_and_digest_bound(self) -> None:
        self.assertEqual("9.13.0", self.profile.provider["version"])
        self.assertTrue(self.profile.image["id"].startswith("sha256:"))
        changed = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        changed["execution"]["network"] = "host"
        path = self.root / "changed.json"
        path.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaises(ValueError):
            CalibreRuntimeProfile.load(path)

    def test_snapshot_is_deterministic_and_path_relative(self) -> None:
        first = snapshot_library(self.library, self.profile)
        second = snapshot_library(self.library, self.profile)
        self.assertEqual(first, second)
        self.assertEqual(["Ada Beispiel/Erster Titel (1)/book.epub", "metadata.db"], [item.relative_path for item in first.files])
        self.assertNotIn(str(self.library), repr(first))

    def test_snapshot_requires_metadata_database(self) -> None:
        (self.library / "metadata.db").unlink()
        with self.assertRaisesRegex(ValueError, "metadata_missing"):
            snapshot_library(self.library, self.profile)

    def test_snapshot_enforces_file_count_and_total_size_limits(self) -> None:
        for key, value, reason in (
            ("max_files", 1, "file_count_exceeded"),
            ("max_total_bytes", 1, "total_limit_exceeded"),
        ):
            with self.subTest(key=key):
                changed = json.loads(json.dumps(self.profile.data))
                changed["workspace"][key] = value
                limited = CalibreRuntimeProfile(changed)
                with self.assertRaisesRegex(ValueError, reason):
                    snapshot_library(self.library, limited)

    def test_snapshot_enforces_relative_path_limit(self) -> None:
        changed = json.loads(json.dumps(self.profile.data))
        changed["workspace"]["max_relative_path_bytes"] = 5
        limited = CalibreRuntimeProfile(changed)
        with self.assertRaisesRegex(ValueError, "path_limit_exceeded"):
            snapshot_library(self.library, limited)

    @unittest.skipIf(not hasattr(os, "symlink"), "symlink unavailable")
    def test_snapshot_rejects_links_when_supported(self) -> None:
        link = self.library / "linked.epub"
        try:
            link.symlink_to(self.library / "metadata.db")
        except OSError:
            self.skipTest("symlink privilege unavailable")
        with self.assertRaisesRegex(ValueError, "link_not_allowed"):
            snapshot_library(self.library, self.profile)

    def test_workspace_copies_source_and_cleans_only_owned_task(self) -> None:
        manager = LibraryWorkspaceManager(self.library, self.root / "tasks", self.profile)
        workspace = manager.create()
        self.assertNotEqual(self.library, workspace.library)
        self.assertEqual(snapshot_library(self.library, self.profile), snapshot_library(workspace.library, self.profile))
        self.assertTrue((workspace.root / MARKER_NAME).is_file())
        manager.cleanup(workspace)
        self.assertEqual([], list(manager.root.iterdir()))

    def test_recovery_preserves_unknown_entries(self) -> None:
        manager = LibraryWorkspaceManager(self.library, self.root / "recovery", self.profile)
        manager.prepare_root()
        (manager.root / "unknown").write_text("review", encoding="utf-8")
        self.assertFalse(manager.recover(now=100000))
        self.assertTrue((manager.root / "unknown").exists())

    def test_parser_projects_only_whitelisted_fields_and_strips_paths(self) -> None:
        books = parse_calibre_output(raw_report())
        self.assertEqual([1, 2], [item.external_record_id for item in books])
        self.assertEqual(("epub", "pdf"), books[1].formats)
        self.assertNotIn("/library", repr(books))

    def test_parser_splits_calibredb_machine_author_separator(self) -> None:
        raw = json.dumps(
            [{"id": 1, "title": "Atlas", "authors": "Ada Beispiel & Bea مثال"}],
            ensure_ascii=False,
        ).encode("utf-8")
        books = parse_calibre_output(raw)
        self.assertEqual(("Ada Beispiel", "Bea مثال"), books[0].authors)

    def test_parser_rejects_unknown_fields_and_invalid_ids(self) -> None:
        for value in ([{"id": 1, "title": "x", "tags": []}], [{"id": "1", "title": "x"}]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_calibre_output(json.dumps(value).encode("utf-8"))

    def test_provider_uses_copy_and_returns_deterministic_projection(self) -> None:
        executor = FakeExecutor(InventoryExecution(True, 0, True, True, raw_report(), "completed"))
        provider = CalibreCliProvider(source=self.library, temp_root=self.root / "provider", profile=self.profile, executor=executor)
        result = provider.project()
        self.assertTrue(result.assessed)
        self.assertEqual([1, 2], [item.external_record_id for item in result.books])
        self.assertNotEqual(self.library, executor.library_seen)
        self.assertEqual([], list((self.root / "provider").iterdir()))
        self.assertNotIn(str(self.library), render_json(result))

    def test_provider_rejects_changed_source(self) -> None:
        executor = FakeExecutor(
            InventoryExecution(True, 0, True, True, raw_report(), "completed"),
            mutate_source=self.library / "metadata.db",
        )
        result = CalibreCliProvider(source=self.library, temp_root=self.root / "changed", profile=self.profile, executor=executor).project()
        self.assertEqual("source_changed", result.execution_state)
        self.assertTrue(result.effects.original_modified)
        self.assertFalse(result.assessed)

    def test_provider_rejects_invalid_or_unverified_completion(self) -> None:
        cases = (
            (InventoryExecution(True, 0, True, True, b"{}", "completed"), "provider.output_contract_invalid"),
            (InventoryExecution(True, 0, False, True, raw_report(), "completed"), "executor.failed"),
            (InventoryExecution(True, 7, True, True, raw_report(), "completed"), "executor.failed"),
        )
        for execution, reason in cases:
            with self.subTest(reason=reason, exit_code=execution.exit_code):
                result = CalibreCliProvider(
                    source=self.library,
                    temp_root=self.root / f"invalid-{execution.exit_code}-{execution.isolation_verified}",
                    profile=self.profile,
                    executor=FakeExecutor(execution),
                ).project()
                self.assertEqual((reason,), result.reason_codes)
                self.assertFalse(result.assessed)

    def test_cleanup_failure_is_visible_and_fail_closed(self) -> None:
        provider = CalibreCliProvider(
            source=self.library,
            temp_root=self.root / "cleanup-failure",
            profile=self.profile,
            executor=FakeExecutor(InventoryExecution(True, 0, True, True, raw_report(), "completed")),
        )
        provider.workspace = CleanupFailingWorkspace(provider.workspace)
        result = provider.project()
        self.assertEqual("cleanup_failed", result.execution_state)
        self.assertEqual(("workspace.cleanup_failed",), result.reason_codes)
        self.assertFalse(result.effects.cleanup_complete)

    def test_executor_states_fail_closed(self) -> None:
        for state, reason in (
            ("unavailable", "executor.unavailable_or_changed"),
            ("timeout", "executor.timeout"),
            ("invalid_report", "executor.invalid_report"),
            ("failed", "executor.failed"),
        ):
            with self.subTest(state=state):
                result = CalibreCliProvider(
                    source=self.library,
                    temp_root=self.root / f"state-{state}",
                    profile=self.profile,
                    executor=FakeExecutor(InventoryExecution(True, None, state != "unavailable", state != "unavailable", None, state)),
                ).project()
                self.assertEqual((reason,), result.reason_codes)
                self.assertFalse(result.assessed)

    def test_human_and_json_views_are_path_free(self) -> None:
        raw = raw_report()
        report = CalibreInventoryReport(
            books=parse_calibre_output(raw),
            effects=CalibreEffects(True, False, False, True, True),
            execution_state="completed",
            library_snapshot_sha256=hashlib.sha256(b"snapshot").hexdigest(),
            profile_id=self.profile.profile_id,
            provider_version="9.13.0",
            raw_output_sha256=hashlib.sha256(raw).hexdigest(),
            raw_output_size_bytes=len(raw),
        )
        first = render_json(report)
        self.assertEqual(first, render_json(report))
        self.assertNotIn("/library", first)
        self.assertIn("Calibre-ID 1", render_human(report))

    def test_cli_missing_temp_root_is_visible_and_path_free(self) -> None:
        environment = dict(os.environ)
        environment.pop("SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT", None)
        completed = subprocess.run(
            [sys.executable, str(CLI), "private-library", "--json"],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(4, completed.returncode)
        self.assertIn("configuration.temp_root_missing", completed.stdout)
        self.assertNotIn("private-library", completed.stdout + completed.stderr)

    def test_cli_rejects_multiple_libraries_without_echoing_them(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CLI), "first-private", "second-private"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, completed.returncode)
        self.assertNotIn("first-private", completed.stderr)
        self.assertNotIn("second-private", completed.stderr)


if __name__ == "__main__":
    unittest.main()
