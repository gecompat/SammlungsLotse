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
        cls.metadata_contract_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_IDENTITY_METADATA_CONTRACT_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0011_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0012_AFTER_EXP0011.md"
        ).read_text(encoding="utf-8")
        cls.v2_work_item = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_IDENTITY_ROLE_AWARE_V2_WORK_ITEM.md"
        ).read_text(encoding="utf-8")
        cls.post_wi0013_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0013_AFTER_WI0013.md"
        ).read_text(encoding="utf-8")
        cls.next_readonly_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0014_NEXT_READONLY_VALUE.md"
        ).read_text(encoding="utf-8")
        cls.exp0011_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0011"
                / "result.json"
            ).read_text(encoding="utf-8")
        )

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

    def test_post_exp0011_gate_selects_bounded_v2_work_item(self) -> None:
        self.assertEqual(self.artifacts["GATE-0011"]["status"], "done")
        self.assertIn(
            "GATE-0010", self.relation_targets("GATE-0011", "depends_on")
        )
        self.assertIn(
            "WI-0012", self.relation_targets("GATE-0011", "depends_on")
        )
        self.assertEqual(self.artifacts["EXP-0011"]["status"], "done")
        self.assertIn(
            "GATE-0011", self.relation_targets("EXP-0011", "depends_on")
        )
        self.assertIn(
            "EXP-0010", self.relation_targets("EXP-0011", "derived_from")
        )
        self.assertEqual(self.artifacts["GATE-0012"]["status"], "done")
        self.assertIn(
            "EXP-0011", self.relation_targets("GATE-0012", "depends_on")
        )
        self.assertEqual(self.artifacts["WI-0013"]["status"], "done")
        for dependency in ("GATE-0012", "EXP-0011", "WI-0012", "TEST-0001"):
            self.assertIn(
                dependency, self.relation_targets("WI-0013", "depends_on")
            )
        self.assertIn(
            "DONE — OPTION A / EXP-0011 AUSGEWÄHLT", self.post_wi0012_gate
        )
        self.assertIn(
            "### A — Produktcodefreie Vertrags- und Evidenzwave",
            self.post_wi0012_gate,
        )
        self.assertIn("als EXP-0011 ausgewählt", self.post_wi0012_gate)
        self.assertIn("### K — Pausieren", self.post_wi0012_gate)
        self.assertIn(
            "DONE — EXECUTED, 14/14 METHOD CRITERIA PASSED",
            self.metadata_contract_experiment,
        )
        for heading in (
            "### V1 — Unveränderter v1-Bericht plus Evidenzbegleiter",
            "### V2 — Rollenbewusster Bericht v2 mit fünf Stufen",
            "### V3 — Rollenbewusster Bericht v2 mit Publikationsstufe",
        ):
            self.assertIn(heading, self.metadata_contract_experiment)
        self.assertIn("genau 15 Paare", self.metadata_contract_experiment)
        self.assertIn("Alle 14 methodischen Kriterien", self.metadata_contract_experiment)
        self.assertTrue(
            (ROOT / "experiments" / "ebook" / "exp-0011" / "execution-profile.json").is_file()
        )
        self.assertTrue((ROOT / "tools" / "experiments" / "run_exp_0011.py").is_file())
        self.assertEqual("pass", self.exp0011_result["status"])
        self.assertTrue(all(self.exp0011_result["acceptance"].values()))
        self.assertIn(
            "DONE — OPTION A / WI-0013 AUSGEWÄHLT", self.post_exp0011_gate
        )
        for heading in (
            "### A — V2 als engen Zielvertrag auswählen",
            "### B — V1 als additive Kompatibilitätsoption auswählen",
            "### C — V3 erst durch ein Publikationsregel-Experiment vertiefen",
            "### D — V3 direkt als Zielvertrag auswählen",
            "### K — Pausieren",
        ):
            self.assertIn(heading, self.post_exp0011_gate)
        self.assertIn("ausdrücklich Option A ausgewählt", self.post_exp0011_gate)
        self.assertIn(
            "DONE — IMPLEMENTIERT UND SYNTHETISCH PRODUKTQUALIFIZIERT",
            self.v2_work_item,
        )
        self.assertIn("--json --report-version v2", self.v2_work_item)
        self.assertIn(
            "sammlungslotse/ebook-identity-candidate-report/v2",
            self.v2_work_item,
        )
        self.assertIn("genau die fünf Stufen", self.v2_work_item)
        self.assertIn("Es entsteht keine Stufe `publication`", self.v2_work_item)
        self.assertIn("keine V1-Deprecation", self.v2_work_item)
        self.assertIn("29/29 Kriterien", self.v2_work_item)
        self.assertIn("erneut 23/23 qualifiziert", self.v2_work_item)
        self.assertEqual(self.artifacts["GATE-0013"]["status"], "done")
        self.assertIn(
            "WI-0013", self.relation_targets("GATE-0013", "depends_on")
        )
        self.assertIn(
            "DONE — OPTION A / DUALEN VERTRAG STABIL HALTEN",
            self.post_wi0013_gate,
        )
        self.assertIn("V1 bleibt Standard; V2 bleibt Opt-in", self.post_wi0013_gate)
        self.assertIn("kein WI-0014", self.post_wi0013_gate)
        self.assertIn(
            "Kein neuer Produktarbeitsgegenstand ist registriert",
            self.post_wi0013_gate,
        )
        self.assertEqual(self.artifacts["GATE-0014"]["status"], "proposed")
        self.assertIn(
            "GATE-0013", self.relation_targets("GATE-0014", "depends_on")
        )
        for heading in (
            "### A — Begrenzte Kandidatensuche produktcodefrei evidenzieren",
            "### B — Read-only Bestandsqualitätsbefunde definieren",
            "### C — Bibliografische Konflikte read-only erklären",
            "### D — Mehrbibliotheks-Routing experimentieren",
            "### E — V2-Verbraucher- und Migrationsevidenz erheben",
            "### F — Nur Maintenance und Requalifikation fortsetzen",
            "### K — Pausieren",
        ):
            self.assertIn(heading, self.next_readonly_gate)
        self.assertIn("A ist empfohlen, aber nicht ausgewählt", self.next_readonly_gate)
        self.assertIn(
            "Kein Experiment und kein Produktarbeitsgegenstand ist registriert",
            self.next_readonly_gate,
        )


if __name__ == "__main__":
    unittest.main()
