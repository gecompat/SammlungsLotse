from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "sammlungslotse_rule_context_tests", ROOT / "tools/governance/validate_rule_context.py"
)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
CACHE = GATE.load_cache_tool(ROOT)


class RuleContextTests(unittest.TestCase):
    def repository(self, root: Path) -> None:
        subprocess.run(["git", "init", "--quiet", str(root)], check=True, capture_output=True)
        for relative in GATE.REQUIRED_SOURCES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic rule.\n", encoding="utf-8")
        registry = {"artifacts": {}}
        (root / ".ai/artifact_registry.json").write_text(json.dumps(registry), encoding="utf-8")
        (root / "AGENTS.md").write_text(
            "Read [project rules](docs/governance/PROJECT_RULES.md).\n", encoding="utf-8"
        )
        links = []
        for relative in sorted(GATE.REQUIRED_SOURCES - {"docs/governance/PROJECT_RULES.md"}):
            links.append(f"[rule](../../{relative})")
        (root / "docs/governance/PROJECT_RULES.md").write_text(
            "\n".join(links) + "\n", encoding="utf-8"
        )

    def test_transitive_project_governance_is_covered(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            self.assertEqual(GATE.discovery_problems(root, CACHE), [])

    def test_unformatted_entrypoint_cannot_silently_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            (root / "AGENTS.md").write_text("Read docs/governance/PROJECT_RULES.md.\n", encoding="utf-8")
            problems = GATE.discovery_problems(root, CACHE)
            self.assertTrue(any("outside rule-context discovery: docs/governance/PROJECT_RULES.md" in p for p in problems))

    def test_existing_but_unlinked_validation_rule_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            router = root / "docs/governance/PROJECT_RULES.md"
            text = router.read_text(encoding="utf-8").replace("[rule](../../docs/governance/VALIDATION.md)\n", "")
            router.write_text(text, encoding="utf-8")
            self.assertTrue(any("outside rule-context discovery: docs/governance/VALIDATION.md" in p for p in GATE.discovery_problems(root, CACHE)))

    def test_new_accepted_decision_requires_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            locator = "docs/decisions/DEC-0001-SYNTHETIC.md"
            (root / locator).write_text("Synthetic accepted decision.\n", encoding="utf-8")
            registry = {"artifacts": {"DEC-0001": {"status": "accepted", "locator": locator}}}
            (root / ".ai/artifact_registry.json").write_text(json.dumps(registry), encoding="utf-8")
            self.assertTrue(any(locator in p for p in GATE.discovery_problems(root, CACHE)))
            index = root / "docs/decisions/README.md"
            index.write_text("[decision](DEC-0001-SYNTHETIC.md)\n", encoding="utf-8")
            self.assertEqual(GATE.discovery_problems(root, CACHE), [])

    def test_missing_referenced_rule_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            (root / "docs/governance/VALIDATION.md").unlink()
            self.assertTrue(any("UNRESOLVED_REFERENCE" in p for p in GATE.discovery_problems(root, CACHE)))

    def test_new_declared_authority_cannot_be_hidden_by_omitting_its_link(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            locator = "docs/governance/NEW_RULE.md"
            (root / locator).write_text("Status: AUTHORITATIVE\n", encoding="utf-8")
            self.assertTrue(any(locator in p for p in GATE.discovery_problems(root, CACHE)))

    def test_inventory_is_reachability_not_a_semantic_read_plan(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            inventory = GATE.discovery_inventory(root, CACHE)
            self.assertEqual(inventory["problems"], [])
            self.assertIn("docs/decisions/README.md", inventory["discovered_sources"])
            self.assertNotIn("analysis_keys", inventory)
            self.assertNotIn("reanalyze", inventory)

    def test_project_rule_change_invalidates_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.repository(root)
            options = CACHE.make_options(root, root, include_global=False, fallback_filenames=(), project_doc_max_bytes=32768)
            before = CACHE._capture_once(options)
            rule = root / "docs/governance/VALIDATION.md"
            rule.write_text("Changed synthetic validation contract.\n", encoding="utf-8")
            after = CACHE._capture_once(options)
            self.assertTrue(before.complete and after.complete)
            plan = CACHE.compare_records(before.record, after)
            self.assertEqual(plan["status"], "PARTIAL_INVALIDATION")
            self.assertIn("docs/governance/VALIDATION.md", plan["reanalyze"])
            self.assertIn("docs/governance/PROJECT_RULES.md", plan["reanalyze"])
            self.assertNotEqual(before.record["sources"]["docs/governance/PROJECT_RULES.md"]["analysis_key"], after.record["sources"]["docs/governance/PROJECT_RULES.md"]["analysis_key"])


if __name__ == "__main__":
    unittest.main()
