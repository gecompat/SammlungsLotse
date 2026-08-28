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

from sammlungslotse.ebook_calibre_identity import (  # noqa: E402
    CalibreIdentityProfile,
    EbookCalibreIdentityService,
)
from sammlungslotse.ebook_calibre_identity.cli import (  # noqa: E402
    render_human,
    render_json,
)
from sammlungslotse.ebook_calibre_identity.executor import (  # noqa: E402
    CalibreRecordPodmanExecutor,
)
from sammlungslotse.ebook_calibre_identity.model import (  # noqa: E402
    RecordHandoffEffects,
    RecordSnapshotHandoff,
)
from sammlungslotse.ebook_calibre_identity.ports import RecordExecution  # noqa: E402
from sammlungslotse.ebook_calibre_identity.provider import (  # noqa: E402
    CalibreRecordSnapshotProvider,
)
from sammlungslotse.ebook_intake.model import Snapshot  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


PROFILE_PATH = ROOT / "runtime" / "ebook-calibre-identity" / "profile.json"
RUNTIME_PROFILE_PATH = ROOT / "runtime" / "calibre-readonly" / "profile.json"
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases"
SAFE_EPUB = CASES / "identity-byte-equal" / "source-a" / "same.epub"
UNSAFE_EPUB = CASES / "container-path-traversal" / "traversal.epub"
CLI = ROOT / "tools" / "run_ebook_calibre_identity.py"


def snapshot(data: bytes) -> Snapshot:
    return Snapshot(
        data=data,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        suffix=".epub",
    )


class FakeRecordPort:
    def __init__(self, handoff: RecordSnapshotHandoff) -> None:
        self.handoff = handoff
        self.calls = 0

    @property
    def external_record_id(self) -> int:
        return self.handoff.external_record_id

    @property
    def profile_id(self) -> str:
        return self.handoff.profile_id

    def capture(self, maximum_bytes: int) -> RecordSnapshotHandoff:
        self.calls += 1
        if maximum_bytes < 1:
            raise AssertionError("unexpected input limit")
        return self.handoff


class FakeExecutor:
    def __init__(
        self, result: RecordExecution, *, mutate_source: Path | None = None
    ) -> None:
        self.result = result
        self.mutate_source = mutate_source
        self.calls = 0
        self.library_seen: Path | None = None
        self.record_id_seen: int | None = None

    def execute(self, workspace, external_record_id: int) -> RecordExecution:
        self.calls += 1
        self.library_seen = workspace.library
        self.record_id_seen = external_record_id
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


class EbookCalibreIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = CalibreIdentityProfile.load(PROFILE_PATH, RUNTIME_PROFILE_PATH)
        configured = os.environ.get("SAMMLUNGSLOTSE_TEST_TEMP_ROOT")
        if configured:
            parent = Path(configured)
        elif os.name == "nt" and Path("C:/rep").is_dir():
            parent = Path("C:/rep/tmp/SammlungsLotse/unit-tests")
        else:
            parent = Path(tempfile.gettempdir()) / "sammlungslotse-unit-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.temporary.name)
        self.library = self.root / "library"
        self.library.mkdir()
        (self.library / "metadata.db").write_bytes(b"synthetic metadata")
        book = self.library / "Synthetic Author" / "Synthetic Book (1)"
        book.mkdir(parents=True)
        (book / "book.epub").write_bytes(SAFE_EPUB.read_bytes())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def completed_handoff(self, data: bytes | None = None) -> RecordSnapshotHandoff:
        content = SAFE_EPUB.read_bytes() if data is None else data
        return RecordSnapshotHandoff(
            effects=RecordHandoffEffects(True, False, True, False, True),
            external_record_id=1,
            library_snapshot_sha256=hashlib.sha256(b"library").hexdigest(),
            profile_id=self.profile.profile_id,
            provider_version=self.profile.runtime.provider["version"],
            reason_codes=(),
            snapshot=snapshot(content),
            state="completed",
        )

    def execution(self, data: bytes, state: str = "completed") -> RecordExecution:
        completed = state == "completed"
        return RecordExecution(
            cleanup_complete=True,
            data=data if completed else None,
            exit_code=0 if completed else None,
            isolation_verified=completed,
            output_sha256=hashlib.sha256(data).hexdigest() if completed else None,
            output_size_bytes=len(data) if completed else None,
            process_started=state != "unavailable",
            state=state,
        )

    def test_profile_binds_exact_runtime_command_and_limits(self) -> None:
        self.assertEqual("wi-0011-calibre-identity-handoff/v1", self.profile.profile_id)
        self.assertEqual("calibredb", self.profile.command["program"])
        self.assertEqual(4 * 1024 * 1024, self.profile.limits["max_input_bytes"])
        self.assertEqual(
            self.profile.runtime.image["id"], self.profile.data["calibre_runtime"]["image_id"]
        )
        changed = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        changed["command"]["fixed_flags"].append("--cover")
        path = self.root / "changed-profile.json"
        path.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaises(ValueError):
            CalibreIdentityProfile.load(path, RUNTIME_PROFILE_PATH)

    def test_external_record_id_is_narrow_and_single(self) -> None:
        for value in ("0", "01", "-1", "+1", "1,2", "abc", "1000000000", "١"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.profile.validate_external_record_id(value)
        self.assertEqual(1, self.profile.validate_external_record_id("1"))
        self.assertEqual(999999999, self.profile.validate_external_record_id("999999999"))

    def test_application_compares_two_immutable_snapshots_with_fixed_roles(self) -> None:
        port = FakeRecordPort(self.completed_handoff())
        report = EbookCalibreIdentityService(self.profile).compare(
            LocalFileSnapshotReader(SAFE_EPUB), port
        )

        self.assertEqual(1, port.calls)
        self.assertEqual("completed", report.assessment)
        self.assertIsNotNone(report.identity)
        assert report.identity is not None
        self.assertEqual("exact_byte_match", report.identity.overall)
        value = report.to_dict()
        self.assertEqual({"1": "ingress_epub", "2": "calibre_record_epub"}, value["source_roles"])
        self.assertFalse(value["effects"]["network_access"])
        self.assertFalse(value["effects"]["writer"])

    def test_ingress_gate_failure_prevents_provider_call_and_partial_identity(self) -> None:
        port = FakeRecordPort(self.completed_handoff())
        report = EbookCalibreIdentityService(self.profile).compare(
            LocalFileSnapshotReader(UNSAFE_EPUB), port
        )

        self.assertEqual(0, port.calls)
        self.assertEqual("not_assessed", report.assessment)
        self.assertIsNone(report.identity)
        self.assertEqual(("ingress.preflight_gate_not_open",), report.handoff_reason_codes)
        self.assertFalse(report.effects.container_started)

    def test_provider_uses_task_copy_verifies_bytes_and_cleans(self) -> None:
        data = SAFE_EPUB.read_bytes()
        executor = FakeExecutor(self.execution(data))
        provider = CalibreRecordSnapshotProvider(
            source=self.library,
            temp_root=self.root / "provider-tasks",
            external_record_id="1",
            profile=self.profile,
            executor=executor,
        )

        handoff = provider.capture(self.profile.limits["max_input_bytes"])

        self.assertEqual("completed", handoff.state)
        self.assertEqual(1, executor.calls)
        self.assertEqual(1, executor.record_id_seen)
        self.assertNotEqual(self.library, executor.library_seen)
        self.assertEqual(hashlib.sha256(data).hexdigest(), handoff.snapshot.sha256)
        self.assertEqual([], list((self.root / "provider-tasks").iterdir()))

    def test_provider_fails_closed_on_source_change(self) -> None:
        data = SAFE_EPUB.read_bytes()
        executor = FakeExecutor(
            self.execution(data), mutate_source=self.library / "metadata.db"
        )
        provider = CalibreRecordSnapshotProvider(
            source=self.library,
            temp_root=self.root / "changed-tasks",
            external_record_id="1",
            profile=self.profile,
            executor=executor,
        )

        handoff = provider.capture(self.profile.limits["max_input_bytes"])

        self.assertEqual("source_changed", handoff.state)
        self.assertIsNone(handoff.snapshot)
        self.assertTrue(handoff.effects.source_modified)
        self.assertEqual(("library.source_changed",), handoff.reason_codes)

    def test_provider_maps_executor_states_without_partial_snapshot(self) -> None:
        for state, reason in (
            ("unavailable", "executor.unavailable_or_changed"),
            ("failed", "executor.failed"),
            ("timeout", "executor.timeout"),
            ("invalid_report", "provider.output_contract_invalid"),
            ("selection_unavailable", "provider.selection_unavailable"),
            ("cleanup_failed", "executor.cleanup_failed"),
        ):
            with self.subTest(state=state):
                provider = CalibreRecordSnapshotProvider(
                    source=self.library,
                    temp_root=self.root / f"state-{state}",
                    external_record_id="1",
                    profile=self.profile,
                    executor=FakeExecutor(self.execution(b"ignored", state)),
                )
                handoff = provider.capture(self.profile.limits["max_input_bytes"])
                self.assertEqual(state, handoff.state)
                self.assertEqual((reason,), handoff.reason_codes)
                self.assertIsNone(handoff.snapshot)

    def test_provider_cleanup_failure_overrides_success(self) -> None:
        data = SAFE_EPUB.read_bytes()
        provider = CalibreRecordSnapshotProvider(
            source=self.library,
            temp_root=self.root / "cleanup-tasks",
            external_record_id="1",
            profile=self.profile,
            executor=FakeExecutor(self.execution(data)),
        )
        provider.workspace = CleanupFailingWorkspace(provider.workspace)

        handoff = provider.capture(self.profile.limits["max_input_bytes"])

        self.assertEqual("cleanup_failed", handoff.state)
        self.assertFalse(handoff.effects.cleanup_complete)
        self.assertIsNone(handoff.snapshot)

    def test_executor_command_is_shell_free_digest_bound_and_single_record(self) -> None:
        manager = CalibreRecordSnapshotProvider(
            source=self.library,
            temp_root=self.root / "command-tasks",
            external_record_id="1",
            profile=self.profile,
            executor=FakeExecutor(self.execution(SAFE_EPUB.read_bytes())),
        ).workspace
        workspace = manager.create()
        try:
            arguments = CalibreRecordPodmanExecutor(self.profile)._create_arguments(
                "sammlungslotse-wi0011-fixed", workspace, 1
            )
        finally:
            manager.cleanup(workspace)

        self.assertEqual("podman", arguments[0])
        self.assertIn(self.profile.runtime.image["id"], arguments)
        self.assertIn("none", arguments)
        self.assertIn("/usr/bin/env", arguments)
        self.assertEqual("1", arguments[-1])
        self.assertEqual(1, arguments.count("calibredb"))
        self.assertNotIn("shell", arguments)
        self.assertNotIn("metadata.db", " ".join(arguments))

    def test_executor_output_requires_exact_id_epub_and_stable_limit(self) -> None:
        output = self.root / "output"
        output.mkdir()
        data = SAFE_EPUB.read_bytes()
        (output / "1.epub").write_bytes(data)
        executor = CalibreRecordPodmanExecutor(self.profile)

        result = executor._read_output(output, 1)

        self.assertEqual(data, result["data"])
        self.assertEqual(hashlib.sha256(data).hexdigest(), result["sha256"])
        (output / "unexpected.opf").write_text("unexpected", encoding="utf-8")
        self.assertIsNone(executor._read_output(output, 1)["data"])

    def test_json_and_human_views_are_deterministic_path_free_and_role_explicit(self) -> None:
        report = EbookCalibreIdentityService(self.profile).compare(
            LocalFileSnapshotReader(SAFE_EPUB), FakeRecordPort(self.completed_handoff())
        )
        first = render_json(report)
        human = render_human(report)

        self.assertEqual(first, render_json(report))
        self.assertEqual(
            "sammlungslotse/ebook-calibre-identity-candidate-report/v1",
            json.loads(first)["schema"],
        )
        self.assertIn("1=ingress_epub", human)
        self.assertIn("2=calibre_record_epub", human)
        for forbidden in (str(ROOT), SAFE_EPUB.name, str(self.library), "metadata.db"):
            self.assertNotIn(forbidden, first + human)
        with self.assertRaises(RuntimeError):
            render_json(report, maximum=1)


class EbookCalibreIdentityCliTests(unittest.TestCase):
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

    def test_missing_temp_root_is_path_free_not_assessed(self) -> None:
        completed = self.run_cli("private-input.epub", "private-library", "1", "--json")

        self.assertEqual(4, completed.returncode)
        value = json.loads(completed.stdout)
        self.assertEqual("not_assessed", value["assessment"])
        self.assertEqual(["configuration.temp_root_missing"], value["handoff_reason_codes"])
        for forbidden in ("private-input.epub", "private-library"):
            self.assertNotIn(forbidden, completed.stdout + completed.stderr)

    def test_invalid_and_multiple_ids_are_rejected_before_execution_without_echo(self) -> None:
        cases = (
            ("private.epub", "private-library", "0"),
            ("private.epub", "private-library", "1,2"),
            ("private.epub", "private-library", "1", "2"),
        )
        for arguments in cases:
            with self.subTest(arguments=arguments):
                completed = self.run_cli(*arguments)
                self.assertEqual(2, completed.returncode)
                for forbidden in arguments[:2]:
                    self.assertNotIn(forbidden, completed.stdout + completed.stderr)

    def test_invalid_profile_is_path_free_not_assessed(self) -> None:
        completed = self.run_cli(
            "private.epub",
            "private-library",
            "1",
            "--json",
            "--profile",
            "private-profile.json",
        )

        self.assertEqual(4, completed.returncode)
        self.assertEqual(
            ["configuration.profile_invalid"],
            json.loads(completed.stdout)["handoff_reason_codes"],
        )
        self.assertNotIn("private-profile.json", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
