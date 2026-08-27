from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class EbookNextDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        registry = json.loads(
            (ROOT / ".ai" / "artifact_registry.json").read_text(encoding="utf-8")
        )
        cls.artifacts = registry["artifacts"]
        cls.gate_plan = (
            ROOT / "docs" / "planning" / "EBOOK_GATE_0002_AFTER_PROTOTYPE.md"
        ).read_text(encoding="utf-8")
        cls.experiment_plan = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_DEEP_READONLY_HANDOFF_EXPERIMENT.md"
        ).read_text(encoding="utf-8")

    def relation_targets(self, reference: str, relation_type: str) -> set[str]:
        return {
            relation["target"]
            for relation in self.artifacts[reference]["relations"]
            if relation["type"] == relation_type
        }

    def test_registry_keeps_experiment_and_release_gate_separate(self) -> None:
        self.assertEqual(self.artifacts["GATE-0002"]["status"], "done")
        self.assertEqual(self.artifacts["EXP-0007"]["status"], "accepted")
        self.assertEqual(self.artifacts["GATE-0003"]["status"], "proposed")
        self.assertIn(
            "GATE-0002", self.relation_targets("EXP-0007", "depends_on")
        )
        self.assertIn(
            "EXP-0007", self.relation_targets("GATE-0003", "depends_on")
        )

    def test_gate_selects_evidence_without_authorizing_product_code(self) -> None:
        self.assertIn("genau eine reversible", self.gate_plan)
        self.assertIn("EXP-0007", self.gate_plan)
        self.assertIn("Produktadapter bleibt", self.gate_plan)
        self.assertIn("Änderungen unter `src/sammlungslotse/`", self.gate_plan)

    def test_experiment_compares_three_handoffs_before_gate_evaluation(self) -> None:
        for heading in (
            "### V1 — Byte-Stream",
            "### V2 — task-private Materialisierung",
            "### V3 — Original-Locator erneut öffnen",
        ):
            self.assertIn(heading, self.experiment_plan)
        self.assertIn("GATE-0003 bleibt `proposed`", self.experiment_plan)
        self.assertIn("Produktcode bleibt", self.experiment_plan)


if __name__ == "__main__":
    unittest.main()
