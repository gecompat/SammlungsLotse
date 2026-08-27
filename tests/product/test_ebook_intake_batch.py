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

from sammlungslotse.ebook_intake.batch import (  # noqa: E402
    BATCH_REPORT_SCHEMA,
    BatchIntakeService,
    BatchLimits,
)
from sammlungslotse.ebook_intake.cli import render_batch_json  # noqa: E402
from sammlungslotse.ebook_intake.deep_model import DeepToolResult  # noqa: E402
from sammlungslotse.ebook_intake.model import Snapshot  # noqa: E402
from sammlungslotse.ebook_intake.ports import SnapshotIssue  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import (  # noqa: E402
    LocalFileSnapshotReader,
)


RUNNER = ROOT / "tools" / "run_ebook_intake.py"
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"


def case(relative: str) -> Path:
    return CASES / relative


def run_batch(
    relatives: list[str], *, as_json: bool = True, extra: list[str] | None = None
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RUNNER)]
    if as_json:
        command.append("--json")
    command.extend(extra or [])
    command.extend(str(case(relative)) for relative in relatives)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


class StaticReader:
    def __init__(self, data: bytes, suffix: str = ".bin") -> None:
        self.data = data
        self.suffix = suffix

    def capture(self, limits):
        del limits
        return Snapshot(
            data=self.data,
            size_bytes=len(self.data),
            sha256=hashlib.sha256(self.data).hexdigest(),
            suffix=self.suffix,
        )


class ExplodingReader:
    def capture(self, limits):
        del limits
        raise RuntimeError("C:/private-library/secret-title.epub")


class DeferredReader:
    def capture(self, limits):
        del limits
        raise SnapshotIssue(
            observation_code="snapshot.changed",
            finding_code="ingress.unstable",
            next_action="defer",
        )


class EbookIntakeBatchContractTests(unittest.TestCase):
    def test_service_preserves_all_gate_outcomes_and_input_order(self) -> None:
        readers = (
            LocalFileSnapshotReader(case("ingress-stable-minimal/stable.epub")),
            LocalFileSnapshotReader(case("epub-active-or-remote/active-remote.epub")),
            LocalFileSnapshotReader(case("container-corrupt/corrupt.epub")),
            LocalFileSnapshotReader(case("format-unknown/unknown.epub")),
            DeferredReader(),
        )

        report = BatchIntakeService().inspect(readers)

        self.assertEqual("completed", report.batch_status)
        self.assertEqual(tuple(range(5)), tuple(item.input_index for item in report.items))
        self.assertEqual(
            (
                "continue_deep_read_only",
                "review",
                "stop",
                "abstain",
                "defer",
            ),
            tuple(item.triage.next_action for item in report.items if item.triage),
        )

    def test_unexpected_item_error_is_path_free_and_does_not_stop_batch(self) -> None:
        report = BatchIntakeService().inspect(
            (ExplodingReader(), StaticReader(b"unknown"))
        )
        payload = report.to_dict()

        self.assertEqual("partial", report.batch_status)
        self.assertEqual("internal_error", report.items[0].status)
        self.assertEqual("completed", report.items[1].status)
        self.assertNotIn("secret-title", json.dumps(payload))
        self.assertNotIn("private-library", json.dumps(payload))

    def test_aggregate_limit_stops_later_capture_and_is_explicit(self) -> None:
        report = BatchIntakeService().inspect(
            (StaticReader(b"aa"), StaticReader(b"bb"), ExplodingReader()),
            limits=BatchLimits(max_total_input_bytes=3),
        )

        self.assertEqual("limit_exceeded", report.batch_status)
        self.assertEqual("completed", report.items[0].status)
        self.assertEqual("not_processed", report.items[1].status)
        self.assertEqual("not_processed", report.items[2].status)
        self.assertEqual(
            ("batch.aggregate_input_limit_exceeded",),
            report.items[2].reason_codes,
        )

    def test_aggregate_limit_prevents_every_deep_call(self) -> None:
        calls = 0

        def inspect(triage):
            nonlocal calls
            calls += 1
            raise AssertionError(triage)

        report = BatchIntakeService().inspect(
            (StaticReader(b"aa"), StaticReader(b"bb")),
            limits=BatchLimits(max_total_input_bytes=3),
            deep_inspector=inspect,
        )

        self.assertEqual("limit_exceeded", report.batch_status)
        self.assertEqual(0, calls)

    def test_deep_inspector_runs_for_every_item_and_preserves_not_assessed(self) -> None:
        seen: list[str | None] = []

        def inspect(triage):
            seen.append(triage.snapshot.sha256 if triage.snapshot else None)
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="gate.not_open",
                snapshot_sha256=(triage.snapshot.sha256 if triage.snapshot else None),
            )

        report = BatchIntakeService().inspect(
            (StaticReader(b"first"), StaticReader(b"second")),
            deep_inspector=inspect,
        )

        self.assertEqual(2, len(seen))
        self.assertTrue(report.has_unassessed_deep_result)
        self.assertEqual(
            ["not_assessed", "not_assessed"],
            [item.deep_read_only.assessment for item in report.items],
        )

    def test_deep_internal_error_is_isolated_and_later_item_still_runs(self) -> None:
        calls = 0

        def inspect(triage):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("C:/private-library/secret-title.epub")
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="gate.not_open",
                snapshot_sha256=(triage.snapshot.sha256 if triage.snapshot else None),
            )

        report = BatchIntakeService().inspect(
            (StaticReader(b"first"), StaticReader(b"second")),
            deep_inspector=inspect,
        )
        payload = json.dumps(report.to_dict())

        self.assertEqual(2, calls)
        self.assertEqual("partial", report.batch_status)
        self.assertEqual("internal_error", report.items[0].status)
        self.assertEqual("completed", report.items[1].status)
        self.assertNotIn("secret-title", payload)

    def test_json_renderer_enforces_batch_output_limit(self) -> None:
        report = BatchIntakeService().inspect(
            (StaticReader(b"a"), StaticReader(b"b")),
            limits=BatchLimits(max_report_bytes=1),
        )

        with self.assertRaises(RuntimeError):
            render_batch_json(report)

    def test_service_rejects_more_than_32_inputs(self) -> None:
        with self.assertRaises(ValueError):
            BatchIntakeService().inspect(tuple(StaticReader(b"x") for _ in range(33)))


class EbookIntakeBatchCliTests(unittest.TestCase):
    def test_json_process_reports_all_inputs_without_locators(self) -> None:
        relatives = [
            "ingress-stable-minimal/stable.epub",
            "epub-active-or-remote/active-remote.epub",
            "container-corrupt/corrupt.epub",
            "format-unknown/unknown.epub",
        ]

        result = run_batch(relatives)
        payload = json.loads(result.stdout)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(BATCH_REPORT_SCHEMA, payload["schema"])
        self.assertEqual(4, payload["input_count"])
        self.assertEqual([0, 1, 2, 3], [item["input_index"] for item in payload["items"]])
        self.assertEqual(
            ["continue_deep_read_only", "review", "stop", "abstain"],
            [item["result"]["next_action"] for item in payload["items"]],
        )
        for relative in relatives:
            self.assertNotIn(str(case(relative)), result.stdout)
            self.assertNotIn(case(relative).name, result.stdout)

    def test_repeated_json_batches_are_byte_identical(self) -> None:
        relatives = [
            "ingress-stable-minimal/stable.epub",
            "format-unknown/unknown.epub",
        ]

        first = run_batch(relatives)
        second = run_batch(relatives)

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout.encode("utf-8"), second.stdout.encode("utf-8"))

    def test_input_order_changes_only_position_and_result_order(self) -> None:
        first = run_batch(
            ["ingress-stable-minimal/stable.epub", "format-unknown/unknown.epub"]
        )
        second = run_batch(
            ["format-unknown/unknown.epub", "ingress-stable-minimal/stable.epub"]
        )

        first_payload = json.loads(first.stdout)
        second_payload = json.loads(second.stdout)
        self.assertEqual(
            list(reversed([item["result"] for item in first_payload["items"]])),
            [item["result"] for item in second_payload["items"]],
        )

    def test_human_batch_is_german_and_path_free(self) -> None:
        relatives = [
            "ingress-stable-minimal/stable.epub",
            "format-unknown/unknown.epub",
        ]

        result = run_batch(relatives, as_json=False)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("SammlungsLotse E-Book-Mehrdatei-Eingangsbericht", result.stdout)
        self.assertIn("Eingang 1", result.stdout)
        self.assertIn("Eingang 2", result.stdout)
        self.assertNotIn("stable.epub", result.stdout)
        self.assertNotIn("unknown.epub", result.stdout)

    def test_missing_and_regular_input_both_produce_results(self) -> None:
        private = "C:/private-library/secret-title.epub"
        stable = str(case("ingress-stable-minimal/stable.epub"))
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--json", private, stable],
            cwd=ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )
        payload = json.loads(result.stdout)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("stop", payload["items"][0]["result"]["next_action"])
        self.assertEqual(
            "continue_deep_read_only", payload["items"][1]["result"]["next_action"]
        )
        self.assertNotIn(private, result.stdout)
        self.assertNotIn("secret-title", result.stdout)

    def test_explicit_directory_is_rejected_without_discovering_its_files(self) -> None:
        directory = case("ingress-stable-minimal")
        unknown = case("format-unknown/unknown.epub")
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--json", str(directory), str(unknown)],
            cwd=ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )
        payload = json.loads(result.stdout)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            ["input.not_regular_file"],
            [
                item["code"]
                for item in payload["items"][0]["result"]["findings"]
            ],
        )
        self.assertEqual("abstain", payload["items"][1]["result"]["next_action"])
        self.assertNotIn("stable.epub", result.stdout)
        self.assertNotIn(str(directory), result.stdout)

    def test_deep_opt_in_without_temp_root_finishes_every_input_then_returns_4(self) -> None:
        result = run_batch(
            ["ingress-stable-minimal/stable.epub", "format-unknown/unknown.epub"],
            extra=["--deep-read-only"],
        )
        payload = json.loads(result.stdout)

        self.assertEqual(4, result.returncode, result.stderr)
        self.assertEqual(2, len(payload["items"]))
        self.assertEqual(
            ["configuration.temp_root_missing"],
            payload["items"][0]["result"]["deep_read_only"]["reason_codes"],
        )
        self.assertEqual(
            ["gate.not_open"],
            payload["items"][1]["result"]["deep_read_only"]["reason_codes"],
        )

    def test_more_than_32_inputs_fails_without_echoing_locators(self) -> None:
        private = "C:/private-library/secret-title.epub"
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--json", *([private] * 33)],
            cwd=ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )

        self.assertEqual(3, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("Eingang konnte nicht sicher geprüft werden.\n", result.stderr)
        self.assertNotIn(private, result.stderr)

    def test_batch_cli_does_not_modify_processed_inputs(self) -> None:
        relatives = [
            "ingress-stable-minimal/stable.epub",
            "epub-active-or-remote/active-remote.epub",
            "container-corrupt/corrupt.epub",
            "format-unknown/unknown.epub",
        ]
        paths = [case(relative) for relative in relatives]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}

        result = run_batch(relatives)

        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
