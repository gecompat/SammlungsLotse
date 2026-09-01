"""Focused contract tests for the EXP-0016 synthetic safety matrix."""

from __future__ import annotations

import ast
import copy
import inspect
import unittest
from pathlib import Path

from tools.experiments import run_exp_0016


RUNNER_PATH = Path(run_exp_0016.__file__)


class Exp0016Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile, cls.cases = run_exp_0016.load_contract()
        cls.by_id = {case["case_id"]: case for case in cls.cases}

    def test_profile_binds_exact_synthetic_product_free_boundary(self) -> None:
        self.assertEqual("EXP-0016", self.profile["artifact"])
        self.assertEqual(48, self.profile["case_manifest"]["case_count"])
        self.assertEqual(2, self.profile["repetitions"])
        self.assertEqual(
            list(run_exp_0016.STRATEGIES), self.profile["strategies"]
        )
        self.assertEqual(3, len(self.profile["standards"]))
        implementation = self.profile["implementation"]
        self.assertTrue(implementation["git_preimage_read_only_process"])
        self.assertTrue(
            all(
                value is False
                for key, value in implementation.items()
                if key != "git_preimage_read_only_process"
            )
        )
        self.assertFalse(
            self.profile["parser"]["oracle_fields_used_for_classification"]
        )
        self.assertNotIn(
            "experiments/ebook/exp-0016/result.json",
            run_exp_0016.PREIMAGE_FILES,
        )

    def test_manifest_has_exact_distribution_unique_oracles_and_surfaces(self) -> None:
        self.assertEqual(48, len(self.cases))
        self.assertEqual(48, len(self.by_id))
        counts: dict[str, int] = {}
        for case in self.cases:
            context = case["expected_context"]
            counts[context] = counts.get(context, 0) + 1
            self.assertEqual(
                set(run_exp_0016.STRATEGIES), set(case["expected_actions"])
            )
            for strategy in run_exp_0016.STRATEGIES:
                self.assertEqual(
                    run_exp_0016.strategy_action(
                        strategy,
                        case["expected_context"],
                        case["expected_scheme_group"],
                    ),
                    case["expected_actions"][strategy],
                )
        self.assertEqual(run_exp_0016.EXPECTED_DISTRIBUTION, counts)
        self.assertEqual(
            set(run_exp_0016.DOCUMENT_TYPES),
            {case["document_type"] for case in self.cases},
        )
        self.assertEqual(
            set(run_exp_0016.SCHEME_GROUPS) - {"none"},
            {case["expected_scheme_group"] for case in self.cases},
        )

    def test_representative_context_scheme_and_deception_controls(self) -> None:
        selected = (
            "usr-001",
            "usr-006",
            "pkg-001",
            "res-001",
            "res-009",
            "act-001",
            "non-003",
            "amb-001",
            "amb-003",
            "amb-008",
            "amb-010",
        )
        for case_id in selected:
            case = self.by_id[case_id]
            with self.subTest(case_id=case_id):
                actual = run_exp_0016.classify_snippet(
                    case["document_type"], case["snippet"]
                )
                self.assertEqual(case["expected_context"], actual["context"])
                self.assertEqual(
                    case["expected_scheme_group"], actual["scheme_group"]
                )

    def test_representative_repetition_is_semantically_identical(self) -> None:
        selected = tuple(
            self.by_id[case_id]
            for case_id in (
                "usr-001",
                "pkg-001",
                "res-002",
                "act-002",
                "non-001",
                "non-005",
                "amb-002",
                "amb-004",
            )
        )
        first = run_exp_0016._run_repetition(selected)
        second = run_exp_0016._run_repetition(selected)
        self.assertEqual(
            run_exp_0016.canonical_bytes(first),
            run_exp_0016.canonical_bytes(second),
        )

    def test_classifier_has_no_oracle_network_database_or_product_input(self) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(
            imports.isdisjoint(
                {"http", "requests", "socket", "sqlite3", "urllib"}
            )
        )
        classifier_source = inspect.getsource(run_exp_0016.classify_snippet)
        self.assertNotIn("expected_", classifier_source)
        repetition_source = inspect.getsource(run_exp_0016._run_repetition)
        self.assertNotIn("expected_context", repetition_source)
        self.assertNotIn("expected_scheme", repetition_source)
        self.assertEqual(1, source.count("subprocess.run("))
        self.assertIn(
            '["git", *arguments]', inspect.getsource(run_exp_0016.git_output)
        )

    def test_strict_strategy_never_continues_non_navigation_or_ambiguity(self) -> None:
        self.assertEqual(
            "candidate_continue_deep_read_only",
            run_exp_0016.strategy_action(
                "strict_navigation_candidate",
                "content.user_activated_hyperlink",
                "https",
            ),
        )
        for context, scheme in (
            ("package.optional_linked_resource", "https"),
            ("publication.automatic_remote_resource", "http"),
            ("content.active_or_submission", "https"),
            ("reference.local_or_other_scheme", "data_or_file"),
        ):
            with self.subTest(context=context, scheme=scheme):
                self.assertEqual(
                    "review",
                    run_exp_0016.strategy_action(
                        "strict_navigation_candidate", context, scheme
                    ),
                )
        self.assertEqual(
            "abstain",
            run_exp_0016.strategy_action(
                "strict_navigation_candidate", "ambiguous_or_deceptive", "https"
            ),
        )

    def test_one_critical_false_continue_disqualifies_strategy(self) -> None:
        metrics = {
            "abstention": 0,
            "conservative_review": 0,
            "context_false_negative": 0,
            "context_mismatch": 0,
            "critical_false_continue": 1,
        }
        self.assertEqual(
            "not_qualified",
            run_exp_0016._strategy_result(metrics)["classification"],
        )
        metrics["critical_false_continue"] = 0
        self.assertEqual(
            "eligible_with_tradeoffs",
            run_exp_0016._strategy_result(metrics)["classification"],
        )

    def test_manifest_mutations_fail_closed(self) -> None:
        manifest = run_exp_0016.load_json(run_exp_0016.CASE_MANIFEST_PATH)
        mutations = []
        duplicate = copy.deepcopy(manifest)
        duplicate["cases"][1]["case_id"] = duplicate["cases"][0]["case_id"]
        mutations.append(duplicate)
        action_change = copy.deepcopy(manifest)
        action_change["cases"][0]["expected_actions"][
            "strict_navigation_candidate"
        ] = "review"
        mutations.append(action_change)
        missing = copy.deepcopy(manifest)
        missing["cases"].pop()
        mutations.append(missing)
        for mutation in mutations:
            with self.subTest():
                with self.assertRaises(run_exp_0016.ExperimentError):
                    run_exp_0016.validate_manifest(mutation)

    def test_runtime_bindings_match_every_bound_file(self) -> None:
        bindings = self.profile["runtime_bindings"]["files"]
        self.assertEqual(len(run_exp_0016.RUNTIME_LOCATORS), len(bindings))
        for binding, locator in zip(
            bindings, run_exp_0016.RUNTIME_LOCATORS, strict=True
        ):
            self.assertEqual(locator, binding["locator"])
            self.assertEqual(
                run_exp_0016.sha256_file(run_exp_0016.ROOT / locator),
                binding["sha256"],
            )

    def test_result_contract_when_present(self) -> None:
        if not run_exp_0016.RESULT_PATH.is_file():
            self.skipTest("result.json is created only after green preimage CI")
        result = run_exp_0016.validate_result()
        self.assertEqual("pass", result["status"])
        self.assertTrue(all(result["acceptance"].values()))


if __name__ == "__main__":
    unittest.main()
