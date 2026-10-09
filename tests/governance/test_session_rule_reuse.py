"""Project regression for the selected core and the retained persistent contract.

Native discovery evidence below is a controlled fixture, never an attestation
of the test runner's client. Actual callers must supply trusted current evidence.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.governance import test_rule_context as FIXTURES

CACHE, GATE, ROOT = FIXTURES.CACHE, FIXTURES.GATE, FIXTURES.ROOT

SPEC = importlib.util.spec_from_file_location(
    "sammlungslotse_processing_efficiency",
    ROOT / ".ai/foundation/runtime/processing_efficiency.py",
)
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)


class SessionRuleReuseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.dependencies = {"rule.md": [], "dependent.md": ["rule.md"],
                             "independent.md": []}
        for source, text in {"AGENTS.md": "Current native authority.\n",
                             "rule.md": "Require read-only input.\n",
                             "dependent.md": "Apply the input rule.\n",
                             "independent.md": "Preserve stable identifiers.\n"}.items():
            (self.root / source).write_text(text, encoding="utf-8")
        self.session = CORE.SessionContext()

    def capture(self, *, root=None, scope="governance-test", complete=True,
                configuration=None, dependencies=None):
        location = root or self.root
        # Trusted synthetic native-chain/config evidence, freshly bound each time.
        authority = CORE.digest({"chain": [("AGENTS.md", (location / "AGENTS.md").read_text())],
                                 "config": configuration or {"fallbacks": [], "limit": 32768}})
        return CORE.capture_context(
            location, dependencies or self.dependencies,
            repository_identity="synthetic-stable-repository", authority_key=authority,
            scope_key=scope, discovery_complete=complete,
        )

    def analyze(self, snapshot):
        # Actually read and interpret the synthetic obligations; retain no record.
        analyses = {source: {"obligation": (self.root / source).read_text().strip()}
                    for source in snapshot["analysis_keys"]}
        self.session.acknowledge(snapshot, analyses)

    def test_unchanged_reuses_actual_analysis_without_a_persistent_record(self):
        before = self.capture()
        self.assertEqual(self.session.check(before)["status"], "READ")
        self.analyze(before)
        after = self.capture()
        self.assertEqual(self.session.check(after)["status"], "REUSE")
        self.assertEqual(self.session.analysis_for(after, "rule.md"),
                         {"obligation": "Require read-only input."})
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ["AGENTS.md", "dependent.md", "independent.md", "rule.md"])

    def test_dirty_untracked_rule_invalidates_itself_and_transitive_dependent(self):
        before = self.capture()
        self.analyze(before)
        (self.root / "rule.md").write_text("Require new read-only boundary.\n", encoding="utf-8")
        after = self.capture()
        result = self.session.check(after)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["reread"], ["dependent.md", "rule.md"])
        self.assertEqual(result["reuse"], ["independent.md"])
        with self.assertRaises(KeyError):
            self.session.analysis_for(after, "dependent.md")

    def test_changed_native_instruction_or_configuration_invalidates_all(self):
        before = self.capture()
        self.analyze(before)
        configured = self.capture(configuration={"fallbacks": ["CUSTOM.md"], "limit": 32768})
        self.assertEqual(self.session.check(configured)["status"], "READ")
        (self.root / "AGENTS.md").write_text("New native override.\n", encoding="utf-8")
        self.assertEqual(self.session.check(self.capture())["status"], "READ")

    def test_scope_change_and_missing_analysis_cannot_invent_reuse(self):
        before = self.capture()
        self.analyze(before)
        self.assertEqual(self.session.check(self.capture(scope="product-test"))["status"], "READ")
        empty = CORE.SessionContext()
        self.assertEqual(empty.check(before)["status"], "READ")
        with self.assertRaises(KeyError):
            empty.analysis_for(before, "rule.md")

    def test_incomplete_discovery_blocks_existing_analysis(self):
        before = self.capture()
        self.analyze(before)
        unknown = self.capture(complete=False)
        self.assertEqual(self.session.check(unknown)["reason"], "DISCOVERY_INCOMPLETE")
        self.assertEqual(self.session.check(unknown)["reuse"], [])
        with self.assertRaises(ValueError):
            self.session.analysis_for(unknown, "rule.md")
        with self.assertRaises(ValueError):
            self.session.acknowledge(unknown, {"rule.md": "invented"})

    def test_changed_dependency_topology_rebinds_affected_analysis(self):
        before = self.capture()
        self.analyze(before)
        dependencies = dict(self.dependencies)
        dependencies["independent.md"] = ["rule.md"]
        after = self.capture(dependencies=dependencies)
        self.assertEqual(self.session.check(after)["reread"], ["independent.md"])

    def test_missing_dependency_or_removed_selected_source_fails_closed(self):
        with self.assertRaises(ValueError):
            self.capture(dependencies={"rule.md": ["absent.md"]})
        (self.root / "rule.md").unlink()
        with self.assertRaises(OSError):
            self.capture()

    def test_fresh_equivalent_locator_binding_can_reuse(self):
        before = self.capture()
        self.analyze(before)
        with tempfile.TemporaryDirectory() as raw:
            other = Path(raw)
            for source in ["AGENTS.md", *self.dependencies]:
                shutil.copyfile(self.root / source, other / source)
            # Caller has freshly established same repository, authority and scope.
            self.assertEqual(self.session.check(self.capture(root=other))["status"], "REUSE")
            (other / "AGENTS.md").write_text("Different checkout authority.\n", encoding="utf-8")
            self.assertEqual(self.session.check(self.capture(root=other))["status"], "READ")

    def test_commit_and_index_changes_require_fresh_binding_but_keep_equal_analysis(self):
        def git(*args):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        git("init", "--quiet")
        git("add", ".")
        git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
            "commit", "--quiet", "-m", "Synthetic rules")
        before = self.capture()
        self.analyze(before)
        (self.root / "unrelated.txt").write_text("Unrelated commit.\n", encoding="utf-8")
        git("add", "unrelated.txt")
        git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
            "commit", "--quiet", "-m", "Unrelated source")
        self.assertEqual(self.session.check(self.capture())["status"], "REUSE")
        (self.root / "rule.md").write_text("Staged changed authority.\n", encoding="utf-8")
        git("add", "rule.md")
        self.assertEqual(self.session.check(self.capture())["reread"], ["dependent.md", "rule.md"])

    def test_complete_discovery_does_not_force_unrelated_accepted_decision_read(self):
        FIXTURES.RuleContextTests().repository(self.root)
        locator = "docs/decisions/DEC-0001-SYNTHETIC.md"
        (self.root / locator).write_text("Accepted runtime decision.\n", encoding="utf-8")
        (self.root / ".ai/artifact_registry.json").write_text(json.dumps({"artifacts": {
            "DEC-0001": {"status": "accepted", "locator": locator}}}), encoding="utf-8")
        (self.root / "docs/decisions/README.md").write_text(
            "[decision](DEC-0001-SYNTHETIC.md)\n", encoding="utf-8")
        inventory = GATE.discovery_inventory(self.root, CACHE)
        self.assertEqual(inventory["problems"], [])
        self.assertIn(locator, inventory["required_sources"])
        selected = {"docs/governance/DOCUMENTATION_STYLE.md": []}
        current = self.capture(dependencies=selected)
        self.assertNotIn(locator, current["analysis_keys"])
        self.analyze(current)
        (self.root / locator).write_text("Changed unrelated runtime decision.\n", encoding="utf-8")
        self.assertEqual(GATE.discovery_problems(self.root, CACHE), [])
        self.assertEqual(self.session.check(self.capture(dependencies=selected))["status"], "REUSE")
        (self.root / locator).unlink()
        self.assertTrue(GATE.discovery_problems(self.root, CACHE))

    def test_persistent_contract_retains_miss_hit_and_partial_invalidation(self):
        FIXTURES.RuleContextTests().repository(self.root)
        options = CACHE.make_options(self.root, self.root, include_global=False,
                                     fallback_filenames=(), project_doc_max_bytes=32768)
        with tempfile.TemporaryDirectory() as raw:
            operator_cache = Path(raw)
            self.assertEqual(CACHE.check_cache(options, operator_cache)["status"], "CACHE_MISS")
            self.assertEqual(list(operator_cache.iterdir()), [])
            self.assertTrue(CACHE.record_cache(options, operator_cache)["recorded"])
            self.assertEqual(CACHE.check_cache(options, operator_cache)["status"], "CACHE_HIT")
            (self.root / "docs/governance/VALIDATION.md").write_text("New validation.\n", encoding="utf-8")
            plan = CACHE.check_cache(options, operator_cache)
            self.assertEqual(plan["status"], "PARTIAL_INVALIDATION")
            self.assertIn("docs/governance/PROJECT_RULES.md", plan["reanalyze"])
            (self.root / "AGENTS.md").write_text("New authority.\n", encoding="utf-8")
            self.assertEqual(CACHE.check_cache(options, operator_cache)["status"], "CACHE_MISS")


if __name__ == "__main__":
    unittest.main()
