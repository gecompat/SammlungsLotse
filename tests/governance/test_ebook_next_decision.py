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
        cls.candidate_search_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_CALIBRE_CANDIDATE_SEARCH_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0012_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0015_AFTER_EXP0012.md"
        ).read_text(encoding="utf-8")
        cls.private_noncompletion_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_PRIVATE_WI0011_NONCOMPLETION_DIAGNOSTIC_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0013_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0016_AFTER_EXP0013.md"
        ).read_text(encoding="utf-8")
        cls.private_ingress_cause_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_PRIVATE_INGRESS_PREFLIGHT_CAUSE_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0014_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0017_AFTER_EXP0014.md"
        ).read_text(encoding="utf-8")
        cls.private_remote_context_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_PRIVATE_REMOTE_REFERENCE_CONTEXT_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0015_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0018_AFTER_EXP0015.md"
        ).read_text(encoding="utf-8")
        cls.navigation_safety_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_SYNTHETIC_NAVIGATION_SAFETY_MATRIX_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0016_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0019_AFTER_EXP0016.md"
        ).read_text(encoding="utf-8")
        cls.downstream_isolation_experiment = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_SYNTHETIC_DOWNSTREAM_ISOLATION_EXPERIMENT.md"
        ).read_text(encoding="utf-8")
        cls.post_exp0017_gate = (
            ROOT
            / "docs"
            / "planning"
            / "EBOOK_GATE_0020_AFTER_EXP0017.md"
        ).read_text(encoding="utf-8")
        cls.exp0012_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0012"
                / "result.json"
            ).read_text(encoding="utf-8")
        )
        cls.exp0011_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0011"
                / "result.json"
            ).read_text(encoding="utf-8")
        )
        cls.exp0013_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0013"
                / "result.json"
            ).read_text(encoding="utf-8")
        )
        cls.exp0014_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0014"
                / "result.json"
            ).read_text(encoding="utf-8")
        )
        cls.exp0015_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0015"
                / "result.json"
            ).read_text(encoding="utf-8")
        )
        cls.exp0016_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0016"
                / "result.json"
            ).read_text(encoding="utf-8")
        )
        cls.exp0017_result = json.loads(
            (
                ROOT
                / "experiments"
                / "ebook"
                / "exp-0017"
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
        self.assertEqual(self.artifacts["GATE-0014"]["status"], "done")
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
        self.assertIn("Option A am 2026-08-31 ausdrücklich ausgewählt", self.next_readonly_gate)
        self.assertIn(
            "Kein Produktarbeitsgegenstand ist registriert",
            self.next_readonly_gate,
        )
        self.assertEqual(self.artifacts["EXP-0012"]["status"], "done")
        for dependency in (
            "GATE-0014",
            "WI-0013",
            "WI-0011",
            "WI-0007",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("EXP-0012", "depends_on")
            )
        for heading in (
            "### V1 — Exakter typisierter Identifier",
            "### V2 — Exakter Titel plus exakter Autor",
            "### V3 — Feldgebundener Titel- und Autor-Contains",
        ):
            self.assertIn(heading, self.candidate_search_experiment)
        self.assertIn("genau acht Aufgaben", self.candidate_search_experiment)
        self.assertIn("genau zwei", self.candidate_search_experiment)
        self.assertIn("höchstens fünf Kandidaten", self.candidate_search_experiment)
        self.assertIn(
            "DONE — EXECUTED, 16/16 METHOD CRITERIA PASSED",
            self.candidate_search_experiment,
        )
        self.assertIn(
            "keine Änderung unter `src/sammlungslotse/`",
            self.candidate_search_experiment,
        )
        self.assertIn("höchstens drei einzelnen EPUBs", self.candidate_search_experiment)
        self.assertIn("nicht eingecheckten", self.next_readonly_gate)
        self.assertEqual("pass", self.exp0012_result["status"])
        self.assertTrue(all(self.exp0012_result["acceptance"].values()))
        self.assertEqual(
            "eligible_with_tradeoffs",
            self.exp0012_result["metrics"]["variants"]["V1"]["classification"],
        )
        self.assertEqual(
            "not_qualified",
            self.exp0012_result["metrics"]["variants"]["V2"]["classification"],
        )
        self.assertEqual(
            "eligible_with_tradeoffs",
            self.exp0012_result["metrics"]["variants"]["V3"]["classification"],
        )
        self.assertEqual(self.artifacts["GATE-0015"]["status"], "done")
        self.assertIn(
            "EXP-0012", self.relation_targets("GATE-0015", "depends_on")
        )
        for heading in (
            "### A — Private Nichtabschlussgründe produktcodefrei diagnostizieren",
            "### B — V1 als optionale Identifier-Suche für einen Produktvertrag prüfen",
            "### C — V3 als begrenzte Titel-/Autor-Kandidatensuche prüfen",
            "### D — Einen mehrstufigen Suchvertrag weiter experimentieren",
            "### E — Nur die synthetische Evidenz konservieren",
            "### K — Pausieren",
        ):
            self.assertIn(heading, self.post_exp0012_gate)
        self.assertIn(
            "Option A am 2026-08-31 ausdrücklich ausgewählt",
            self.post_exp0012_gate,
        )
        self.assertIn("0/3 WI-0011-Vergleiche", self.post_exp0012_gate)
        self.assertEqual(self.artifacts["EXP-0013"]["status"], "done")
        for dependency in (
            "GATE-0015",
            "EXP-0012",
            "WI-0011",
            "WI-0007",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("EXP-0013", "depends_on")
            )
        self.assertIn(
            "DONE — EXECUTED, 16/16 METHOD CRITERIA PASSED; RESULT NOT_QUALIFIED",
            self.private_noncompletion_experiment,
        )
        self.assertIn(
            "genau drei wiederholte", self.private_noncompletion_experiment
        )
        self.assertIn(
            "keine Verzeichnis-, Glob-, Index- oder rekursive Suche",
            self.private_noncompletion_experiment,
        )
        self.assertIn(
            "alle drei Dateien zusammen höchstens 12 MiB",
            self.private_noncompletion_experiment,
        )
        self.assertIn(
            "reason_code_counts", self.private_noncompletion_experiment
        )
        self.assertIn(
            "entry_stage_counts", self.private_noncompletion_experiment
        )
        self.assertIn(
            "keine Änderung unter `src/sammlungslotse/`",
            self.private_noncompletion_experiment,
        )
        self.assertIn(
            "ein neues getrenntes Ergebnisgate",
            self.private_noncompletion_experiment,
        )
        self.assertEqual("not_qualified", self.exp0013_result["status"])
        self.assertEqual(3, self.exp0013_result["input_count"])
        self.assertEqual(
            {"ingress.preflight_gate_not_open": 3},
            self.exp0013_result["reason_code_counts"],
        )
        self.assertEqual(
            3, self.exp0013_result["entry_stage_counts"]["ingress_preflight"]
        )
        self.assertTrue(self.exp0013_result["path_free"])
        self.assertEqual(self.artifacts["GATE-0016"]["status"], "done")
        for dependency in (
            "EXP-0013",
            "GATE-0015",
            "WI-0011",
            "WI-0004",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("GATE-0016", "depends_on")
            )
        for heading in (
            "### A — Private Intake-Gate-Ursachen produktcodefrei qualifizieren",
            "### B — Ausschließlich synthetische Intake-Matrix vertiefen",
            "### C — Produktdiagnostik getrennt erwägen",
            "### K — Evidenz konservieren",
            "### P — E-Book-Identitätszweig pausieren",
        ):
            self.assertIn(heading, self.post_exp0013_gate)
        self.assertIn(
            "Option A am 2026-09-01 ausdrücklich ausgewählt",
            self.post_exp0013_gate,
        )
        self.assertIn(
            "**Ausgewählt als EXP-0014.**",
            self.post_exp0013_gate,
        )
        self.assertEqual(self.artifacts["EXP-0014"]["status"], "done")
        for dependency in (
            "GATE-0016",
            "EXP-0013",
            "WI-0004",
            "WI-0011",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("EXP-0014", "depends_on")
            )
        self.assertIn(
            "EXP-0013", self.relation_targets("EXP-0014", "derived_from")
        )
        self.assertIn(
            "DONE — EXECUTED, METHOD PASSED; RESULT REVIEW 3/3",
            self.private_ingress_cause_experiment,
        )
        self.assertIn(
            "genau drei wiederholte", self.private_ingress_cause_experiment
        )
        self.assertIn(
            "keine Verzeichnis-, Glob-, Index- oder rekursive Suche",
            self.private_ingress_cause_experiment,
        )
        self.assertIn(
            "tools/run_ebook_intake.py --json",
            self.private_ingress_cause_experiment,
        )
        self.assertIn(
            "observation_code_counts", self.private_ingress_cause_experiment
        )
        self.assertIn(
            "finding_code_counts", self.private_ingress_cause_experiment
        )
        self.assertIn(
            "`unclassified`-Zählwert", self.private_ingress_cause_experiment
        )
        self.assertIn(
            "keine Änderung unter `src/sammlungslotse/`",
            self.private_ingress_cause_experiment,
        )
        self.assertIn(
            "Ein methodischer `pass` ist keine Produktfreigabe",
            self.private_ingress_cause_experiment,
        )
        self.assertEqual("pass", self.exp0014_result["status"])
        self.assertEqual(3, self.exp0014_result["input_count"])
        self.assertEqual(3, self.exp0014_result["intake_runs"])
        self.assertEqual(
            3, self.exp0014_result["next_action_counts"]["review"]
        )
        self.assertEqual(
            3,
            self.exp0014_result["finding_code_counts"][
                "security.remote_resource"
            ],
        )
        self.assertEqual(
            0, self.exp0014_result["unclassified_observation_count"]
        )
        self.assertEqual(0, self.exp0014_result["unclassified_finding_count"])
        self.assertTrue(self.exp0014_result["source_unchanged"])
        self.assertTrue(self.exp0014_result["cleanup_complete"])
        self.assertTrue(self.exp0014_result["path_free"])
        self.assertEqual(self.artifacts["GATE-0017"]["status"], "done")
        for dependency in (
            "EXP-0014",
            "GATE-0016",
            "WI-0004",
            "WI-0011",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("GATE-0017", "depends_on")
            )
        for heading in (
            "### A — Private Referenzarten produktcodefrei und pfadfrei qualifizieren",
            "### B — Ausschließlich synthetische Remote-Referenzmatrix vertiefen",
            "### C — Produktarbeitsgegenstand getrennt erwägen",
            "### K — Evidenz konservieren und bestehendes Review beibehalten",
            "### P — E-Book-Identitätszweig pausieren",
        ):
            self.assertIn(heading, self.post_exp0014_gate)
        self.assertIn(
            "Option A am 2026-09-01 ausdrücklich ausgewählt",
            self.post_exp0014_gate,
        )
        self.assertIn(
            "**Ausgewählt als EXP-0015.**", self.post_exp0014_gate
        )
        self.assertIn(
            "B, C, K und P sind nicht ausgewählt", self.post_exp0014_gate
        )
        self.assertIn(
            "`security.remote_resource` ist ein Reviewgrund, kein Schadensnachweis",
            self.post_exp0014_gate,
        )
        self.assertEqual(self.artifacts["EXP-0015"]["status"], "done")
        for dependency in (
            "GATE-0017",
            "EXP-0014",
            "WI-0004",
            "WI-0011",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("EXP-0015", "depends_on")
            )
        self.assertIn(
            "EXP-0014", self.relation_targets("EXP-0015", "derived_from")
        )
        self.assertIn(
            "DONE — EXECUTED, METHOD PASSED", self.private_remote_context_experiment
        )
        self.assertIn(
            "Mindestgruppe beträgt exakt `2` von `3` Eingängen",
            self.private_remote_context_experiment,
        )
        self.assertIn(
            "`suppressed_context_present` als reines Boolean",
            self.private_remote_context_experiment,
        )
        self.assertIn(
            "keine Vorkommenszahlen und keine Einzelzuordnung",
            self.private_remote_context_experiment,
        )
        self.assertIn(
            "keine Änderung unter `src/sammlungslotse/`",
            self.private_remote_context_experiment,
        )
        self.assertIn(
            "Ein methodischer `pass` oder eine gemeinsame Kontextklasse ist keine",
            self.private_remote_context_experiment,
        )

    def test_exp0015_result_and_gate0018_select_synthetic_experiment(self) -> None:
        self.assertEqual("pass", self.exp0015_result["status"])
        self.assertEqual("shared_context_present", self.exp0015_result["qualification"])
        self.assertEqual(3, self.exp0015_result["input_count"])
        self.assertEqual(3, self.exp0015_result["parser_runs"])
        self.assertEqual(3, self.exp0015_result["remote_reference_input_count"])
        self.assertEqual(
            {"content.navigation": 3},
            self.exp0015_result["context_input_counts"],
        )
        self.assertFalse(self.exp0015_result["suppressed_context_present"])
        self.assertEqual(0, self.exp0015_result["unclassified_input_count"])
        self.assertTrue(self.exp0015_result["source_unchanged"])
        self.assertTrue(self.exp0015_result["cleanup_complete"])
        self.assertTrue(self.exp0015_result["path_free"])
        self.assertEqual("done", self.artifacts["GATE-0018"]["status"])
        for dependency in (
            "EXP-0015",
            "GATE-0017",
            "WI-0004",
            "WI-0011",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("GATE-0018", "depends_on")
            )
        for heading in (
            "### A — Rein synthetische Navigationskontext- und Sicherheitsmatrix vertiefen",
            "### B — Erklärbarkeitsarbeitsgegenstand getrennt erwägen",
            "### C — Sicherheitsregel oder Review-Lockerung getrennt untersuchen",
            "### K — Evidenz konservieren und bestehendes Review beibehalten",
            "### P — E-Book-Identitätszweig pausieren",
        ):
            self.assertIn(heading, self.post_exp0015_gate)
        self.assertIn(
            "Option A am 2026-09-01 ausdrücklich ausgewählt",
            self.post_exp0015_gate,
        )
        self.assertIn("**Ausgewählt als EXP-0016.**", self.post_exp0015_gate)
        self.assertIn(
            "B, C, K und P bleiben nicht ausgewählt", self.post_exp0015_gate
        )
        self.assertIn(
            "keine Änderung unter `src/sammlungslotse/`",
            self.post_exp0015_gate,
        )
        self.assertEqual("done", self.artifacts["EXP-0016"]["status"])
        for dependency in (
            "GATE-0018",
            "EXP-0015",
            "WI-0004",
            "WI-0011",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("EXP-0016", "depends_on")
            )
        self.assertIn(
            "EXP-0015", self.relation_targets("EXP-0016", "derived_from")
        )
        self.assertIn(
            "DONE — EXECUTED, METHOD PASSED", self.navigation_safety_experiment
        )
        self.assertIn(
            "genau 48 benannte Fälle", self.navigation_safety_experiment
        )
        for strategy in (
            "`review_all_http_s`",
            "`classify_and_keep_review`",
            "`strict_navigation_candidate`",
        ):
            self.assertIn(strategy, self.navigation_safety_experiment)
        self.assertIn("Bereits ein", self.navigation_safety_experiment)
        self.assertIn(
            "Fall qualifiziert die Strategie nicht",
            self.navigation_safety_experiment,
        )
        self.assertIn(
            "keine Produktfreigabe", self.navigation_safety_experiment
        )

    def test_exp0016_result_and_gate0019_select_downstream_experiment(self) -> None:
        self.assertEqual("pass", self.exp0016_result["status"])
        self.assertEqual(48, self.exp0016_result["case_count"])
        self.assertEqual(96, self.exp0016_result["parser_runs"])
        self.assertEqual(2, self.exp0016_result["repetitions"])
        self.assertTrue(self.exp0016_result["runs_semantically_identical"])
        self.assertTrue(all(self.exp0016_result["acceptance"].values()))
        self.assertFalse(any(self.exp0016_result["effects"].values()))
        self.assertTrue(self.exp0016_result["cleanup_complete"])
        self.assertTrue(self.exp0016_result["path_free"])
        for strategy, conservative_review in (
            ("review_all_http_s", 8),
            ("classify_and_keep_review", 8),
            ("strict_navigation_candidate", 0),
        ):
            outcome = self.exp0016_result["strategies"][strategy]
            self.assertEqual(
                "eligible_with_tradeoffs", outcome["classification"]
            )
            self.assertEqual(10, outcome["metrics"]["abstention"])
            self.assertEqual(
                conservative_review,
                outcome["metrics"]["conservative_review"],
            )
            self.assertEqual(0, outcome["metrics"]["context_false_negative"])
            self.assertEqual(0, outcome["metrics"]["context_mismatch"])
            self.assertEqual(
                0, outcome["metrics"]["critical_false_continue"]
            )

        self.assertEqual("done", self.artifacts["GATE-0019"]["status"])
        for dependency in (
            "EXP-0016",
            "GATE-0018",
            "EXP-0015",
            "WI-0004",
            "WI-0005",
            "WI-0011",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("GATE-0019", "depends_on")
            )
        for heading in (
            "### A — Synthetische Downstream-Isolation und Threat Model qualifizieren",
            "### B — Review-beibehaltende Kontexterklärung als Arbeitsgegenstand erwägen",
            "### C — Strikte Navigationsausnahme als Produktarbeitsgegenstand erwägen",
            "### K — Evidenz konservieren und bestehendes Review beibehalten",
            "### P — E-Book-Identitätszweig pausieren",
        ):
            self.assertIn(heading, self.post_exp0016_gate)
        self.assertIn(
            "A ist die kleinste nächste Evidenzfrage", self.post_exp0016_gate
        )
        self.assertIn(
            "Option A am 2026-09-01 ausdrücklich ausgewählt",
            self.post_exp0016_gate,
        )
        self.assertIn("**Ausgewählt als EXP-0017.**", self.post_exp0016_gate)
        self.assertIn(
            "B, C, K und P bleiben nicht ausgewählt", self.post_exp0016_gate
        )
        self.assertIn(
            "Kein Folgeexperiment oder Produktarbeitsgegenstand",
            self.post_exp0016_gate,
        )
        self.assertIn(
            "WI-0004-Review-Gate bleiben unverändert", self.post_exp0016_gate
        )

        self.assertEqual("done", self.artifacts["EXP-0017"]["status"])
        for dependency in (
            "GATE-0019",
            "EXP-0016",
            "WI-0004",
            "WI-0005",
            "WI-0010",
            "TEST-0001",
        ):
            self.assertIn(
                dependency, self.relation_targets("EXP-0017", "depends_on")
            )
        self.assertIn(
            "EXP-0016", self.relation_targets("EXP-0017", "derived_from")
        )
        self.assertIn(
            "DONE — METHOD PASSED", self.downstream_isolation_experiment
        )
        self.assertIn(
            "genau zwölf Fälle", self.downstream_isolation_experiment
        )
        self.assertIn(
            "genau 24 Providerläufe", self.downstream_isolation_experiment
        )
        self.assertIn(
            "18 Kriterien", self.downstream_isolation_experiment
        )
        self.assertIn(
            "`network=none`", self.downstream_isolation_experiment
        )
        self.assertIn(
            "keine Änderung unter `src/sammlungslotse/`",
            self.downstream_isolation_experiment,
        )
        self.assertIn(
            "neues getrenntes Ergebnisgate",
            self.downstream_isolation_experiment,
        )

    def test_exp0017_result_opens_gate0020_without_selecting_a_followup(self) -> None:
        self.assertEqual("pass", self.exp0017_result["status"])
        self.assertEqual(12, self.exp0017_result["case_count"])
        self.assertEqual(2, self.exp0017_result["repetitions"])
        self.assertEqual(24, self.exp0017_result["provider_runs"])
        self.assertTrue(self.exp0017_result["runs_semantically_identical"])
        self.assertTrue(all(self.exp0017_result["acceptance"].values()))
        self.assertEqual(
            {"context": 0, "s3_action": 0, "scheme_group": 0},
            self.exp0017_result["parser_oracle_mismatches"],
        )
        self.assertEqual(
            {"control_connections": 1, "deep_path_connections": 0},
            self.exp0017_result["canary"],
        )
        self.assertEqual("none", self.exp0017_result["isolation"]["network"])
        self.assertFalse(self.exp0017_result["effects"]["product_code_modified"])
        self.assertFalse(self.exp0017_result["effects"]["private_inputs"])

        self.assertEqual("proposed", self.artifacts["GATE-0020"]["status"])
        self.assertIn(
            "CAP-0002", self.relation_targets("GATE-0020", "parent")
        )
        for dependency in ("EXP-0017", "GATE-0019", "WI-0004", "WI-0005"):
            self.assertIn(
                dependency, self.relation_targets("GATE-0020", "depends_on")
            )
        for heading in (
            "### A — Weitere synthetische Lesesystem- und Aktivierungsevidenz qualifizieren",
            "### B — Review-beibehaltende Kontexterklärung als Arbeitsgegenstand auswählen",
            "### C — Strikte Navigationsausnahme als Produktarbeitsgegenstand auswählen",
            "### K — Evidenz konservieren und bestehendes Review beibehalten",
            "### P — E-Book-Identitätszweig pausieren",
        ):
            self.assertIn(heading, self.post_exp0017_gate)
        self.assertIn(
            "B ist die kleinste entwickelbare Produktfortsetzung",
            self.post_exp0017_gate,
        )
        self.assertIn(
            "Diese Empfehlung nimmt keine Option an", self.post_exp0017_gate
        )
        self.assertIn(
            "A, B, C, K und P sind nicht\nausgewählt",
            self.post_exp0017_gate,
        )
        followups = {
            reference
            for reference, artifact in self.artifacts.items()
            for relation in artifact.get("relations", [])
            if relation == {"target": "GATE-0020", "type": "depends_on"}
        }
        self.assertEqual(set(), followups)


if __name__ == "__main__":
    unittest.main()
