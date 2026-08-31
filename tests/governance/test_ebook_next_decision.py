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
        cls.gate_decision = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0003_HANDOFF_DECISION.md"
        ).read_text(encoding="utf-8")
        cls.work_item_plan = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_DEEP_READONLY_ADAPTER_WORK_ITEM.md"
        ).read_text(encoding="utf-8")
        cls.post_wi0012_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0011_AFTER_WI0012.md"
        ).read_text(encoding="utf-8")

    def relation_targets(self, reference: str, relation_type: str) -> set[str]:
        return {
            relation["target"]
            for relation in self.artifacts[reference]["relations"]
            if relation["type"] == relation_type
        }

    def test_registry_keeps_evidence_gate_and_completed_work_item_separate(self) -> None:
        self.assertEqual(self.artifacts["GATE-0002"]["status"], "done")
        self.assertEqual(self.artifacts["EXP-0007"]["status"], "done")
        self.assertEqual(self.artifacts["GATE-0003"]["status"], "done")
        self.assertEqual(self.artifacts["WI-0005"]["status"], "done")
        self.assertIn(
            "GATE-0002", self.relation_targets("EXP-0007", "depends_on")
        )
        self.assertIn(
            "EXP-0007", self.relation_targets("GATE-0003", "depends_on")
        )
        self.assertIn(
            "GATE-0003", self.relation_targets("WI-0005", "depends_on")
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
        self.assertIn("GATE-0003 ist getrennt ausgewertet", self.experiment_plan)
        self.assertIn("Produktcode bleibt", self.experiment_plan)

    def test_gate_history_and_completed_work_item_remain_separate(self) -> None:
        self.assertIn("ausschließlich V2", self.gate_decision)
        self.assertIn("V3, das erneute Öffnen", self.gate_decision)
        self.assertIn("ist abgelehnt", self.gate_decision)
        self.assertIn("WI-0005 NUR VORGESCHLAGEN", self.gate_decision)
        self.assertIn(
            "DONE — IMPLEMENTIERT UND SYNTHETISCH PRODUKTQUALIFIZIERT",
            self.work_item_plan,
        )
        self.assertIn("## Implementierung und Abnahme", self.work_item_plan)
        self.assertIn("Der Kern übergibt nur Snapshot-Bytes", self.work_item_plan)
        self.assertIn("providerneutralen Ergebnisumschlag", self.work_item_plan)

    def test_post_wi0012_gate_is_open_without_follow_up_artifact(self) -> None:
        self.assertEqual(self.artifacts["GATE-0011"]["status"], "in_progress")
        self.assertIn(
            "GATE-0010", self.relation_targets("GATE-0011", "depends_on")
        )
        self.assertIn(
            "WI-0012", self.relation_targets("GATE-0011", "depends_on")
        )
        self.assertNotIn("EXP-0011", self.artifacts)
        self.assertNotIn("WI-0013", self.artifacts)
        self.assertIn("ENTSCHEIDUNGSBEREIT — AUSWAHL OFFEN", self.post_wi0012_gate)
        self.assertIn(
            "### A — Produktcodefreie Vertrags- und Evidenzwave",
            self.post_wi0012_gate,
        )
        self.assertIn("noch nicht ausgewählt", self.post_wi0012_gate)
        self.assertIn("### K — Pausieren", self.post_wi0012_gate)


if __name__ == "__main__":
    unittest.main()
