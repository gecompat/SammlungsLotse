#!/usr/bin/env python3
"""Run repository tests with explicit historical-experiment replacements."""

from __future__ import annotations

import sys
import unittest
from collections.abc import Iterator
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = ROOT / "tests"
OBSOLETE_CURRENT_PREIMAGE_TESTS = frozenset(
    {
        "experiments.test_exp_0009.Exp0009Tests.test_empirical_result_contract_when_present",
        "experiments.test_exp_0010.Exp0010Tests.test_empirical_result_contract_when_present",
        "experiments.test_exp_0011.Exp0011Tests.test_empirical_result_contract_when_present",
        "experiments.test_exp_0012.Exp0012Tests.test_empirical_result_contract_when_present",
    }
)
FROZEN_PREIMAGE_TEST_PREFIX_COUNTS = {
    "experiments.test_exp_0014.Exp0014Tests.": 11,
}
HISTORICAL_REPLACEMENT_TESTS = frozenset(
    {
        "governance.test_historical_experiment_results.HistoricalExperimentResultTests."
        "test_exp_0009_result_against_historical_preimage",
        "governance.test_historical_experiment_results.HistoricalExperimentResultTests."
        "test_exp_0010_result_against_historical_preimage",
        "governance.test_historical_experiment_results.HistoricalExperimentResultTests."
        "test_exp_0011_result_against_historical_preimage",
        "governance.test_historical_experiment_results.HistoricalExperimentResultTests."
        "test_exp_0012_result_against_historical_preimage",
        "governance.test_historical_experiment_results.HistoricalExperimentResultTests."
        "test_exp_0014_result_against_historical_preimage",
    }
)


def iter_tests(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_tests(item)
        else:
            yield item


def build_suite() -> tuple[unittest.TestSuite, int, int, int]:
    discovered = unittest.defaultTestLoader.discover(
        str(TEST_ROOT),
        pattern="test_*.py",
        top_level_dir=str(TEST_ROOT),
    )
    tests = list(iter_tests(discovered))
    by_id: dict[str, list[unittest.TestCase]] = {}
    for test in tests:
        by_id.setdefault(test.id(), []).append(test)

    missing_obsolete = sorted(
        test_id
        for test_id in OBSOLETE_CURRENT_PREIMAGE_TESTS
        if len(by_id.get(test_id, [])) != 1
    )
    missing_replacements = sorted(
        test_id
        for test_id in HISTORICAL_REPLACEMENT_TESTS
        if len(by_id.get(test_id, [])) != 1
    )
    prefix_mismatches = {
        prefix: len(
            [test for test in tests if test.id().startswith(prefix)]
        )
        for prefix, expected_count in FROZEN_PREIMAGE_TEST_PREFIX_COUNTS.items()
        if len([test for test in tests if test.id().startswith(prefix)])
        != expected_count
    }
    if missing_obsolete or missing_replacements or prefix_mismatches:
        details = []
        if missing_obsolete:
            details.append(
                "obsolete test IDs not found exactly once: "
                + ", ".join(missing_obsolete)
            )
        if missing_replacements:
            details.append(
                "replacement test IDs not found exactly once: "
                + ", ".join(missing_replacements)
            )
        if prefix_mismatches:
            details.append(
                "frozen module test counts differ: "
                + ", ".join(
                    f"{prefix}={count}"
                    for prefix, count in sorted(prefix_mismatches.items())
                )
            )
        raise RuntimeError("; ".join(details))

    retained = [
        test
        for test in tests
        if test.id() not in OBSOLETE_CURRENT_PREIMAGE_TESTS
        and not any(
            test.id().startswith(prefix)
            for prefix in FROZEN_PREIMAGE_TEST_PREFIX_COUNTS
        )
    ]
    excluded_count = len(tests) - len(retained)
    return (
        unittest.TestSuite(retained),
        len(tests),
        excluded_count,
        len(HISTORICAL_REPLACEMENT_TESTS),
    )


def main() -> int:
    sys.path.insert(0, str(ROOT))
    try:
        suite, discovered_count, excluded_count, replacement_count = build_suite()
    except (ImportError, RuntimeError) as exc:
        print(f"Repository test selection failed: {exc}", file=sys.stderr)
        return 2
    print(
        "Repository tests: "
        f"discovered={discovered_count} excluded_current={excluded_count} "
        f"historical_replacements={replacement_count} "
        f"executed={suite.countTestCases()}",
        flush=True,
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
