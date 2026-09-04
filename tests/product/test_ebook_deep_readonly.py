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

from sammlungslotse.ebook_intake.application import TriageService  # noqa: E402
from sammlungslotse.ebook_intake.deep_application import (  # noqa: E402
    DeepReadOnlyService,
)
from sammlungslotse.ebook_intake.deep_model import DeepToolResult  # noqa: E402
from sammlungslotse.ebook_intake.deep_ports import ProcessExecution  # noqa: E402
from sammlungslotse.ebook_intake.deep_profile import DeepRuntimeProfile  # noqa: E402
from sammlungslotse.ebook_intake.deep_workspace import (  # noqa: E402
    MARKER_NAME,
    TaskWorkspaceManager,
)
from sammlungslotse.ebook_intake.epubcheck_provider import (  # noqa: E402
    EpubCheckProvider,
)
from sammlungslotse.ebook_intake.model import Snapshot  # noqa: E402
from sammlungslotse.ebook_intake.podman_executor import (  # noqa: E402
    PodmanExecutor,
    run_bounded,
)
from sammlungslotse.ebook_intake.snapshot import (  # noqa: E402
    LocalFileSnapshotReader,
)


PROFILE_PATH = ROOT / "runtime" / "ebook-deep-readonly" / "profile.json"
QUALIFICATION_PATH = (
    ROOT / "runtime" / "ebook-deep-readonly" / "qualification.json"
)
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"
STABLE = CASES / "ingress-stable-minimal" / "stable.epub"
ACTIVE = CASES / "epub-active-or-remote" / "active-remote.epub"


def snapshot_for(data: bytes = b"synthetic snapshot") -> Snapshot:
    return Snapshot(
        data=data,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        suffix=".epub",
    )


def synthetic_report(*, locations: list[dict[str, object]] | None = None) -> bytes:
    return json.dumps(
        {
            "checker": {"checkerVersion": "5.3.0"},
            "messages": [
                {
                    "ID": "FUTURE-999",
                    "locations": locations
                    if locations is not None
                    else [{"column": 7, "line": 4, "path": "EPUB/chapter.xhtml"}],
                    "message": "Synthetic unknown provider finding",
                    "severity": "WARNING",
                }
            ],
        },
        separators=(",", ":"),
    ).encode("utf-8")


class FakeExecutor:
    def __init__(self, result: ProcessExecution, *, mutate_input: bool = False) -> None:
        self.result = result
        self.mutate_input = mutate_input
        self.calls = 0
        self.materialized = b""

    def execute(self, workspace):
        self.calls += 1
        self.materialized = workspace.input_file.read_bytes()
        if self.mutate_input:
            workspace.input_file.chmod(0o600)
            workspace.input_file.write_bytes(b"changed")
        return self.result


class FakeTool:
    def __init__(self) -> None:
        self.snapshots: list[Snapshot] = []

    def inspect(self, snapshot: Snapshot) -> DeepToolResult:
        self.snapshots.append(snapshot)
        return DeepToolResult.not_assessed(
            execution_state="unavailable",
            reason_code="synthetic",
            snapshot_sha256=snapshot.sha256,
        )


class CleanupFailingWorkspace:
    def __init__(self, delegate: TaskWorkspaceManager) -> None:
        self.delegate = delegate

    def recover(self):
        return self.delegate.recover()

    def create(self, snapshot):
        return self.delegate.create(snapshot)

    def cleanup(self, workspace):
        self.delegate.cleanup(workspace)
        raise RuntimeError("synthetic cleanup failure")


class DeepReadOnlyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = DeepRuntimeProfile.load(PROFILE_PATH)
        configured = os.environ.get("SAMMLUNGSLOTSE_TEST_TEMP_ROOT")
        if configured:
            parent = Path(configured)
        elif os.name == "nt" and Path("C:/rep").is_dir():
            parent = Path("C:/rep/tmp/SammlungsLotse/unit-tests")
        else:
            parent = Path(tempfile.gettempdir()) / "sammlungslotse-unit-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.temp_root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_gate_passes_only_the_approved_snapshot_to_the_port(self) -> None:
        triage = TriageService().triage(LocalFileSnapshotReader(STABLE))
        tool = FakeTool()

        DeepReadOnlyService().inspect(triage, tool)

        self.assertEqual([triage.snapshot], tool.snapshots)
        self.assertNotIn(str(STABLE), repr(tool.snapshots))

    def test_closed_gate_never_calls_the_tool(self) -> None:
        triage = TriageService().triage(LocalFileSnapshotReader(ACTIVE))
        tool = FakeTool()

        result = DeepReadOnlyService().inspect(triage, tool)

        self.assertEqual([], tool.snapshots)
        self.assertEqual("not_assessed", result.assessment)
        self.assertEqual(("gate.not_open",), result.reason_codes)

    def test_profile_rejects_mutated_provider_and_isolation_values(self) -> None:
        original = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        for area, key, value in (
            ("provider", "version", "future"),
            ("image", "id", "sha256:" + "x" * 64),
            ("execution", "network", "host"),
            ("execution", "memory_swap_bytes", 999999999),
        ):
            with self.subTest(area=area, key=key):
                changed = json.loads(json.dumps(original))
                changed[area][key] = value
                path = self.temp_root / f"{area}-{key}.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaises(ValueError):
                    DeepRuntimeProfile.load(path)

    def test_podman_version_contract_is_strictly_parseable(self) -> None:
        self.assertEqual((6, 1, 0), PodmanExecutor._version_tuple("6.1.0"))
        for value in ("6.1", "6.1.0-dev", "latest"):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                PodmanExecutor._version_tuple(value)

    def test_tasks_use_random_private_names_and_exact_snapshot_bytes(self) -> None:
        manager = TaskWorkspaceManager(self.temp_root / "tasks", self.profile)
        snapshot = snapshot_for()
        first = manager.create(snapshot)
        second = manager.create(snapshot)

        self.assertNotEqual(first.task_id, second.task_id)
        self.assertNotEqual(first.input_file.name, second.input_file.name)
        self.assertEqual(snapshot.data, first.input_file.read_bytes())
        self.assertEqual(snapshot.sha256, hashlib.sha256(first.input_file.read_bytes()).hexdigest())
        self.assertTrue((first.root / MARKER_NAME).is_file())

        manager.cleanup(first)
        manager.cleanup(second)
        self.assertEqual([], list(manager.root.iterdir()))

    def test_task_cleanup_bound_covers_inputs_larger_than_four_mebibytes(self) -> None:
        manager = TaskWorkspaceManager(self.temp_root / "large-task", self.profile)
        workspace = manager.create(snapshot_for(b"x" * (4 * 1024 * 1024 + 1)))

        manager.cleanup(workspace)

        self.assertEqual([], list(manager.root.iterdir()))

    def test_failed_materialization_removes_its_partial_task(self) -> None:
        manager = TaskWorkspaceManager(self.temp_root / "partial-task", self.profile)
        invalid = Snapshot(
            data=b"synthetic",
            size_bytes=999,
            sha256=hashlib.sha256(b"synthetic").hexdigest(),
            suffix=".epub",
        )

        with self.assertRaises(RuntimeError):
            manager.create(invalid)

        self.assertEqual([], list(manager.root.iterdir()))

    def test_checked_in_qualification_is_bound_to_the_active_profile(self) -> None:
        qualification = json.loads(QUALIFICATION_PATH.read_text(encoding="utf-8"))

        self.assertEqual("PASS", qualification["status"])
        self.assertTrue(all(qualification["acceptance"].values()))
        self.assertEqual(self.profile.profile_id, qualification["profile_id"])
        self.assertEqual(self.profile.image["id"], qualification["image"]["id"])

    def test_qualification_binds_the_complete_intake_runtime(self) -> None:
        qualification = json.loads(QUALIFICATION_PATH.read_text(encoding="utf-8"))
        bound = set(qualification["preimage_sha256"])
        evidence_commit = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(QUALIFICATION_PATH)],
            cwd=ROOT,
            capture_output=True,
            check=True,
            encoding="utf-8",
        ).stdout.strip()
        files = subprocess.run(
            [
                "git",
                "ls-tree",
                "-r",
                "--name-only",
                evidence_commit,
                "src/sammlungslotse/ebook_intake",
            ],
            cwd=ROOT,
            capture_output=True,
            check=True,
            encoding="utf-8",
        ).stdout.splitlines()
        expected = {
            f"ebook_intake/{Path(path).name}" for path in files if path.endswith(".py")
        }
        expected.update({"runner", "sammlungslotse/__init__.py"})
        self.assertTrue(expected.issubset(bound), sorted(expected - bound))

    def test_recovery_removes_only_owned_expired_tasks(self) -> None:
        manager = TaskWorkspaceManager(self.temp_root / "recovery", self.profile)
        workspace = manager.create(snapshot_for())
        marker_path = workspace.root / MARKER_NAME
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        marker["created_epoch"] = 1
        marker_path.chmod(0o600)
        marker_path.write_text(json.dumps(marker), encoding="utf-8")

        result = manager.recover(now=100000)

        self.assertTrue(result.safe_to_continue)
        self.assertEqual(("recovery.expired_task_removed",), result.observations)
        self.assertFalse(workspace.root.exists())

    def test_recovery_preserves_unknown_and_oversized_entries_for_review(self) -> None:
        manager = TaskWorkspaceManager(self.temp_root / "review", self.profile)
        manager.prepare()
        (manager.root / "unknown.txt").write_text("review", encoding="utf-8")

        result = manager.recover(now=100000)

        self.assertFalse(result.safe_to_continue)
        self.assertEqual(("recovery.unknown_entry",), result.observations)
        self.assertTrue((manager.root / "unknown.txt").exists())

    def test_provider_preserves_raw_report_and_unknown_code(self) -> None:
        raw = synthetic_report(
            locations=[
                {"column": 7, "line": 4, "path": "EPUB/chapter.xhtml"},
                {"column": 1, "line": 1, "path": "../private/location"},
            ]
        )
        executor = FakeExecutor(
            ProcessExecution(True, 1, True, ("synthetic",), True, raw, "completed")
        )
        provider = EpubCheckProvider(
            profile=self.profile,
            temp_root=self.temp_root / "provider",
            executor=executor,
        )
        snapshot = snapshot_for()

        result = provider.inspect(snapshot)

        self.assertEqual("epubcheck_conformance_findings", result.assessment)
        self.assertEqual("FUTURE-999", result.findings[0].code)
        self.assertEqual("WARNING", result.findings[0].severity)
        self.assertEqual(
            ("EPUB/chapter.xhtml",),
            tuple(item.path for item in result.findings[0].locations),
        )
        self.assertEqual(raw, result.raw_report)
        self.assertEqual(snapshot.data, executor.materialized)
        self.assertEqual([], list((self.temp_root / "provider").iterdir()))

    def test_executor_failures_and_invalid_reports_fail_closed(self) -> None:
        cases = (
            ("timeout", None, "executor.timeout"),
            ("invalid_report", b"{}", "executor.invalid_report"),
            ("failed", None, "executor.failed"),
        )
        for state, raw, reason in cases:
            with self.subTest(state=state):
                executor = FakeExecutor(
                    ProcessExecution(True, None, True, (), True, raw, state)
                )
                provider = EpubCheckProvider(
                    profile=self.profile,
                    temp_root=self.temp_root / f"failure-{state}",
                    executor=executor,
                )
                result = provider.inspect(snapshot_for(state.encode("ascii")))
                self.assertEqual("not_assessed", result.assessment)
                self.assertEqual((reason,), result.reason_codes)

    def test_unverified_or_impossible_executor_completion_fails_closed(self) -> None:
        cases = (
            (False, True, 0, "executor.isolation_not_verified"),
            (True, False, 0, "executor.invalid_completion_state"),
            (True, True, 99, "executor.invalid_completion_state"),
        )
        for isolation, started, exit_code, reason in cases:
            with self.subTest(reason=reason, exit_code=exit_code):
                executor = FakeExecutor(
                    ProcessExecution(
                        True,
                        exit_code,
                        isolation,
                        (),
                        started,
                        synthetic_report(),
                        "completed",
                    )
                )
                result = EpubCheckProvider(
                    profile=self.profile,
                    temp_root=self.temp_root
                    / f"invalid-completion-{isolation}-{started}-{exit_code}",
                    executor=executor,
                ).inspect(snapshot_for(reason.encode("ascii")))
                self.assertEqual("not_assessed", result.assessment)
                self.assertEqual((reason,), result.reason_codes)

    def test_pre_and_post_run_hash_mismatches_never_become_findings(self) -> None:
        snapshot = snapshot_for()
        invalid = Snapshot(
            data=snapshot.data,
            size_bytes=snapshot.size_bytes,
            sha256="0" * 64,
            suffix=".epub",
        )
        executor = FakeExecutor(
            ProcessExecution(True, 0, True, (), True, synthetic_report(), "completed")
        )
        provider = EpubCheckProvider(
            profile=self.profile,
            temp_root=self.temp_root / "hashes",
            executor=executor,
        )

        before = provider.inspect(invalid)
        self.assertEqual("hash_mismatch", before.execution_state)
        self.assertEqual(0, executor.calls)

        mutating = FakeExecutor(executor.result, mutate_input=True)
        after = EpubCheckProvider(
            profile=self.profile,
            temp_root=self.temp_root / "hash-after",
            executor=mutating,
        ).inspect(snapshot)
        self.assertEqual("hash_mismatch", after.execution_state)
        self.assertEqual("not_assessed", after.assessment)
        self.assertEqual((), after.findings)

    def test_cleanup_failure_is_visible_and_fail_closed(self) -> None:
        executor = FakeExecutor(
            ProcessExecution(True, 0, True, (), True, synthetic_report(), "completed")
        )
        provider = EpubCheckProvider(
            profile=self.profile,
            temp_root=self.temp_root / "cleanup",
            executor=executor,
        )
        provider._workspace = CleanupFailingWorkspace(provider._workspace)

        result = provider.inspect(snapshot_for())

        self.assertEqual("cleanup_failed", result.execution_state)
        self.assertEqual("not_assessed", result.assessment)
        self.assertFalse(result.effects.cleanup_complete)
        self.assertEqual(("workspace.cleanup_failed",), result.reason_codes)

    def test_bounded_process_capture_and_timeout_are_enforced(self) -> None:
        captured = run_bounded(
            [
                sys.executable,
                "-c",
                "import sys;sys.stdout.write('x'*4096);sys.stderr.write('y'*4096)",
            ],
            timeout=5,
            stdout_limit=128,
            stderr_limit=64,
        )
        self.assertEqual(128, len(captured.stdout))
        self.assertEqual(64, len(captured.stderr))
        self.assertTrue(captured.stdout_truncated)
        self.assertTrue(captured.stderr_truncated)

        timed = run_bounded(
            [sys.executable, "-c", "import time;time.sleep(30)"],
            timeout=0.1,
            stdout_limit=128,
            stderr_limit=128,
        )
        self.assertTrue(timed.timed_out)
        self.assertNotEqual(0, timed.returncode)


if __name__ == "__main__":
    unittest.main()
