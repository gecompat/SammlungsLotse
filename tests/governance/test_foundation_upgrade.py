"""Keep the complete semantic upgrade delta and historical scope reviewable."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FoundationUpgradeTests(unittest.TestCase):
    def test_assessment_covers_exact_material_feature_delta(self):
        catalog = json.loads((ROOT / ".ai/foundation/feature_catalog.json").read_text(encoding="utf-8"))
        for release in ("1_20", "1_21"):
            with self.subTest(release=release):
                assessment = json.loads(
                    (ROOT / f"docs/governance/FOUNDATION_UPGRADE_{release}.json").read_text(encoding="utf-8")
                )
                self.assert_complete_assessment(catalog, assessment)

        current = json.loads((ROOT / "docs/governance/FOUNDATION_UPGRADE_1_21.json").read_text(encoding="utf-8"))
        provenance = json.loads((ROOT / ".ai/foundation/installation-provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(current["source_ref"], provenance["source_commit"])
        self.assertEqual(current["source_version"], catalog["ruleset_version"])
        self.assertEqual(provenance["selection"]["capabilities"], ["artifact-registry-github", "rule-context-cache"])

    def assert_complete_assessment(self, catalog, assessment):
        version = lambda value: tuple(map(int, value.split(".")))
        installed, source = version(assessment["installed_version"]), version(assessment["source_version"])
        expected = {}
        for feature_id, feature in catalog["features"].items():
            reasons = []
            if installed < version(feature["introduced_in"]) <= source:
                reasons.append(f"introduced_in:{feature['introduced_in']}")
            for change in feature["change_history"]:
                if change["impact"] == "MATERIAL" and installed < version(change["version"]) <= source:
                    reasons.append(f"material_change:{change['version']}")
            if reasons:
                expected[feature_id] = reasons
        actual = assessment["assessments"]
        self.assertEqual(len(actual), len(expected))
        self.assertEqual({a["feature_id"]: a["candidate_reasons"] for a in actual}, expected)
        for item in actual:
            self.assertIn(item["classification"], catalog["assessment_classifications"])
            self.assertTrue(item["rationale"])
            self.assertTrue(item["evidence"])
            for relative in item["evidence"]:
                self.assertTrue((ROOT / relative).is_file(), relative)
            if item["classification"] in {"RECOMMENDED", "DECISION_REQUIRED", "CONFLICT"}:
                self.assertTrue(item.get("recommendation") or item.get("decision_required"))


if __name__ == "__main__":
    unittest.main()
