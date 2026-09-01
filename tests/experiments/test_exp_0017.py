"""Focused, container-free contract tests for EXP-0017."""

from __future__ import annotations

import copy
import inspect
import io
import unittest
import zipfile
from pathlib import Path

from tools.experiments import run_exp_0017

from sammlungslotse.ebook_intake.deep_model import (
    DeepEffects,
    DeepFinding,
    DeepToolResult,
)
from sammlungslotse.ebook_intake.deep_profile import DeepRuntimeProfile


class _FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    def inspect(self, snapshot):
        self.calls += 1
        return DeepToolResult(
            assessment="epubcheck_conformance_findings",
            effects=DeepEffects(
                cleanup_complete=True,
                network_access=False,
                original_modified=False,
                process_started=True,
                task_materialized=True,
            ),
            execution_state="completed",
            findings=(
                DeepFinding(
                    code="TST-001",
                    message="synthetic",
                    severity="WARNING",
                ),
            ),
            observations=("isolation.verified",),
            profile_id="synthetic",
            provider_id="epubcheck",
            provider_version="5.3.0",
            reason_codes=(),
            snapshot_sha256=snapshot.sha256,
            raw_report=b"{}",
        )


class Exp0017Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.cases = run_exp_0017.load_contract()
        cls.classified = run_exp_0017.classify_cases(cls.cases)
        cls.authority = "127.0.0.1:49152"

    def test_profile_binds_exact_execution_and_forbidden_effect_boundary(self) -> None:
        self.assertEqual("EXP-0017", self.profile["artifact"])
        self.assertEqual(12, self.profile["case_manifest"]["case_count"])
        self.assertEqual(2, self.profile["repetitions"])
        self.assertTrue(self.profile["implementation"]["deep_tool_execution"])
        self.assertTrue(
            self.profile["implementation"]["local_loopback_measurement"]
        )
        self.assertTrue(self.profile["implementation"]["product_code_imports"])
        for key in (
            "direct_database_access",
            "domain_system_writes",
            "downloads",
            "external_network_access",
            "image_build",
            "persistence",
            "private_input_access",
            "product_code_changes",
            "writer_surface",
        ):
            self.assertFalse(self.profile["implementation"][key])
        self.assertNotIn(
            "experiments/ebook/exp-0017/result.json",
            run_exp_0017.PREIMAGE_FILES,
        )

    def test_manifest_is_exact_exp0016_selection_with_four_cases_per_group(self) -> None:
        self.assertEqual(run_exp_0017.SELECTED_CASES, tuple(
            case["case_id"] for case in self.cases
        ))
        counts = {}
        for case in self.cases:
            counts[case["group"]] = counts.get(case["group"], 0) + 1
            self.assertEqual(case["case_id"], case["source_case_id"])
            self.assertEqual(
                list(run_exp_0017.FORBIDDEN_EFFECTS),
                case["forbidden_effects"],
            )
        self.assertEqual(
            {key: 4 for key in sorted(run_exp_0017.GROUP_CASES)}, counts
        )

    def test_exp0016_classifier_matches_all_context_scheme_and_s3_oracles(self) -> None:
        self.assertEqual(
            {"context": 0, "s3_action": 0, "scheme_group": 0},
            run_exp_0017.parser_mismatches(self.cases, self.classified),
        )
        classifier = inspect.getsource(run_exp_0017.classify_cases)
        self.assertNotIn("expected_context", classifier)
        self.assertNotIn("expected_scheme_group", classifier)
        self.assertNotIn("expected_s3_action", classifier)

    def test_materializer_is_deterministic_bounded_and_epub_shaped(self) -> None:
        payloads, summary = run_exp_0017.prepare_materializations(
            self.cases, self.authority
        )
        self.assertEqual(12, len(payloads))
        self.assertTrue(summary["deterministic"])
        self.assertLessEqual(
            summary["archive_entries_max"], run_exp_0017.MAX_ARCHIVE_ENTRIES
        )
        self.assertLessEqual(summary["max_bytes"], run_exp_0017.MAX_EPUB_BYTES)
        for case in self.cases:
            first = payloads[case["case_id"]]
            second = run_exp_0017.materialize_epub(case, self.authority)
            self.assertEqual(first, second)
            with zipfile.ZipFile(io.BytesIO(first), "r") as archive:
                entries = archive.infolist()
                self.assertEqual("mimetype", entries[0].filename)
                self.assertEqual(zipfile.ZIP_STORED, entries[0].compress_type)
                self.assertEqual(b"application/epub+zip", archive.read("mimetype"))
                self.assertIn("META-INF/container.xml", archive.namelist())
                self.assertIn("EPUB/package.opf", archive.namelist())

    def test_source_bindings_are_stable_across_checkout_line_endings(self) -> None:
        self.assertEqual(
            b"first\nsecond\nthird\n",
            run_exp_0017.canonical_source_bytes(
                b"first\r\nsecond\rthird\n"
            ),
        )

    def test_loopback_canary_has_one_control_hit_then_resets(self) -> None:
        canary = run_exp_0017.LoopbackCanary()
        try:
            self.assertEqual(1, canary.prove_and_reset())
            self.assertEqual(0, canary.count)
        finally:
            self.assertTrue(canary.close())

    def test_fake_matrix_makes_exactly_24_semantically_identical_calls(self) -> None:
        payloads, _ = run_exp_0017.prepare_materializations(
            self.cases, self.authority
        )
        provider = _FakeProvider()
        repetitions = [
            run_exp_0017.run_provider_repetition(
                cases=self.cases,
                classified=self.classified,
                authority=self.authority,
                baseline_payloads=payloads,
                provider=provider,
            )
            for _ in range(2)
        ]
        self.assertEqual(24, provider.calls)
        self.assertEqual(
            run_exp_0017.canonical_bytes(repetitions[0]),
            run_exp_0017.canonical_bytes(repetitions[1]),
        )
        summary = run_exp_0017.summarize_repetition(1, repetitions[0])
        self.assertEqual({"completed": 12}, summary["execution_states"])
        self.assertEqual({"TST-001": 12}, summary["provider_codes"])
        self.assertEqual(12, summary["process_started"])
        self.assertEqual(12, summary["isolation_verified"])

    def test_pure_fake_result_passes_all_18_method_criteria(self) -> None:
        payloads, materialization = run_exp_0017.prepare_materializations(
            self.cases, self.authority
        )
        provider = _FakeProvider()
        repetitions = [
            run_exp_0017.run_provider_repetition(
                cases=self.cases,
                classified=self.classified,
                authority=self.authority,
                baseline_payloads=payloads,
                provider=provider,
            )
            for _ in range(2)
        ]
        deep = DeepRuntimeProfile.load(run_exp_0017.DEEP_PROFILE_PATH)
        isolation = {
            "cap_drop": sorted(
                {
                    "CAP_CHOWN",
                    "CAP_DAC_OVERRIDE",
                    "CAP_FOWNER",
                    "CAP_FSETID",
                    "CAP_KILL",
                    "CAP_NET_BIND_SERVICE",
                    "CAP_SETFCAP",
                    "CAP_SETGID",
                    "CAP_SETPCAP",
                    "CAP_SETUID",
                    "CAP_SYS_CHROOT",
                }
            ),
            "command_exact": True,
            "container_removed": True,
            "cpu_nanos": 1_000_000_000,
            "environment_exact": True,
            "input_read_only": True,
            "memory_bytes": deep.execution["memory_bytes"],
            "memory_swap_bytes": deep.execution["memory_swap_bytes"],
            "network": "none",
            "no_new_privileges": True,
            "pids_limit": deep.execution["pids_limit"],
            "privileged": False,
            "read_only_root": True,
            "task_root_empty": True,
            "tmpfs_exact": True,
            "ulimits_exact": True,
            "verified_by_executor": True,
        }
        runtime = {
            "client_version": "6.1.0",
            "deep_profile_id": deep.profile_id,
            "image_id_exact": True,
            "provider_id": "epubcheck",
            "provider_version": "5.3.0",
            "server_os_arch": "linux/amd64",
            "server_version": "6.1.0",
        }
        timeout = {
            "assessment": "not_assessed",
            "container_removed": True,
            "process_started": True,
            "state": "timeout",
            "task_root_empty": True,
        }
        output = {
            "attempted_bytes": 4 * 1024 * 1024,
            "bounded_bytes": deep.execution["tmpfs"]["/output"],
            "container_removed": True,
            "write_rejected": True,
        }
        cleanup = {
            "canary_closed": True,
            "containers_empty_after": True,
            "containers_empty_before": True,
            "isolation_container_removed": True,
            "isolation_task_root_empty": True,
            "outer_task_removed": True,
            "output_container_removed": True,
            "provider_task_root_empty": True,
            "timeout_container_removed": True,
            "timeout_task_root_empty": True,
        }
        result = run_exp_0017.build_result(
            preimage_commit="a" * 40,
            profile=self.profile,
            cases=self.cases,
            mismatches={"context": 0, "s3_action": 0, "scheme_group": 0},
            repetitions=repetitions,
            materialization=materialization,
            runtime=runtime,
            isolation=isolation,
            canary_control=1,
            canary_deep=0,
            timeout=timeout,
            output=output,
            cleanup=cleanup,
            inputs_unchanged=True,
            bound_files_unchanged=True,
            green_preimage_ci_confirmed=True,
        )
        self.assertEqual(18, len(result["acceptance"]))
        self.assertTrue(all(result["acceptance"].values()))
        self.assertEqual("pass", result["status"])
        self.assertEqual(result, run_exp_0017.validate_result_dict(result))
        serialized = run_exp_0017.canonical_bytes(result)
        self.assertNotIn(b"127.0.0.1", serialized)
        self.assertNotIn(b"https://", serialized)

    def test_manifest_mutations_fail_closed(self) -> None:
        manifest = run_exp_0017.load_json(run_exp_0017.CASE_MANIFEST_PATH)
        mutations = []
        missing = copy.deepcopy(manifest)
        missing["cases"].pop()
        mutations.append(missing)
        changed = copy.deepcopy(manifest)
        changed["cases"][0]["expected_s3_action"] = "review"
        mutations.append(changed)
        private_effect = copy.deepcopy(manifest)
        private_effect["cases"][0]["forbidden_effects"].pop()
        mutations.append(private_effect)
        for mutation in mutations:
            with self.subTest():
                with self.assertRaises(run_exp_0017.ExperimentError):
                    run_exp_0017.validate_manifest(mutation)

    def test_execution_requires_explicit_green_preimage_confirmation(self) -> None:
        with self.assertRaises(run_exp_0017.ExperimentError):
            run_exp_0017.execute(
                temp_root=Path("unused"),
                result_path=Path("unused-result"),
                green_preimage_ci_confirmed=False,
                preimage_commit="a" * 40,
            )

    def test_result_privacy_guard_rejects_paths_urls_and_raw_fields(self) -> None:
        self.assertTrue(run_exp_0017._public_result_safe({"safe": True}))
        self.assertFalse(
            run_exp_0017._public_result_safe({"value": "https://example.invalid"})
        )
        self.assertFalse(
            run_exp_0017._public_result_safe({"value": r"C:\private\book.epub"})
        )
        self.assertFalse(run_exp_0017._public_result_safe({"raw_report": "x"}))

    def test_runner_uses_existing_provider_and_executor_without_product_gate(self) -> None:
        source = Path(run_exp_0017.__file__).read_text(encoding="utf-8")
        self.assertIn("EpubCheckProvider", source)
        self.assertIn("PodmanExecutor", source)
        self.assertIn("provider.inspect(snapshot)", source)
        self.assertNotIn("TriageService", source)
        self.assertNotIn("DeepReadOnlyService", source)

    def test_result_contract_when_present(self) -> None:
        if not run_exp_0017.RESULT_PATH.is_file():
            self.skipTest("result.json is created only after green preimage CI")
        result = run_exp_0017.validate_result()
        self.assertIn(result["status"], {"inconclusive", "pass"})


if __name__ == "__main__":
    unittest.main()
