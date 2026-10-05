# Foundation-Upgrade 1.19 und Cache-Integration

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0021

Datum: 2026-10-05

## Vergleichsstand und Autorisierung

- bisherige Foundation: 1.8.0 aus
  `7ddc29988b23570f462e46ebf527f8dfdd05fd75`;
- neue Foundation: 1.19.0 aus
  `4aafd20442275d0fdedf291fc6e12e8fe1f683cc`;
- Quelle: https://github.com/gecompat/AI_Repository_Foundation;
- Adapter: GitHub Copilot, Claude Code und Gemini;
- ausgewählte optionale Fähigkeiten: `artifact-registry-github` und
  `rule-context-cache` gemäß DEC-0003 und DEC-0005;
- Nutzerauftrag: die geprüften Integrationsprobleme beheben und die aktuelle
  Foundation integrieren.

Der vollständige Kerntransfer richtet sich ausschließlich nach dem Manifest
des exakten Quellcommits. Vor dem Transfer wurde jede ausgewählte Quelldatei
gegen ihren portablen SHA-256 geprüft. Die MIT-Notice bleibt erhalten; die
Projektlizenz, Produktarchitektur, historischen IDs und Registration Authority
werden nicht migriert.

## Vollständige Feature-Bewertung

Der deterministische Delta-Befehl für 1.8.0 bis 1.19.0 liefert genau zehn
Kandidaten. Die schemaförmige Bewertung mit Kandidatengründen, Evidenz,
Empfehlungen und Entscheidungsgrenzen steht in
[FOUNDATION_UPGRADE_1_19.json](FOUNDATION_UPGRADE_1_19.json).

| Feature | Klassifikation | Ergebnis |
|---|---|---|
| `ai-client-integration` | `RECOMMENDED` | Requested-/Actual-Nachweis und manuelle Fallbacks als Kernvertrag; vorhandene Adapter bleiben Discovery-Brücken. |
| `ai-host-preparation` | `NOT_APPLICABLE` | Keine KI-Modellprovisionierung; bestehende Produktprovisionierer bleiben eigenständige Verträge. |
| `ai-runtime-adapters` | `NOT_APPLICABLE` | Keine angenommene produktseitige Modelllaufzeit oder Runtime-Verbindung. |
| `ai-work-execution` | `NOT_APPLICABLE` | Kein Foundation-basierter KI-Executor und keine neue Produkt-Ausführungsarchitektur. |
| `ai-work-orchestration` | `RECOMMENDED` | Runtime-neutrale Planungs-, Autorisierungs-, Daten- und Evidenzgrenzen als Kernpolicy und Schemas. |
| `central-artifact-registry` | `ALREADY_EQUIVALENT` | v2-Registry, semantische Merge-Prüfung und Actions v7 bereits vorhanden; Bootstrap bleibt erhalten. |
| `ci-supersession-and-integration-queue` | `RECOMMENDED` | Bestehende Supersession dokumentiert; Commitbindung und harte Abbruchgrenzen ergänzt. |
| `installed-foundation-provenance` | `APPLY_DEFAULT` | Exakte Installationsprovenienz für alle ausgewählten Quellen und begründeten Overrides. |
| `model-routing-interoperability` | `RECOMMENDED` | Dynamische Evidenz-, Erfolgskosten- und Fallbackregeln als Kernvertrag; keine konkrete Modellkonfiguration. |
| `session-lifecycle-management` | `RECOMMENDED` | Deterministische Metriken, natürliche Grenzen und kleine Delta-Übergaben; keine automatische Rotation eingerichtet. |

Die Empfehlungen sind mit dem Kerntransfer integriert oder als Auswahlgrenze
explizit festgehalten. Die optionalen `model-router`, `ai-work`,
`ai-runtime-adapters`, `ai-executor`, `ai-provisioning`,
`ai-client-integration` und `ai-orchestrator` bleiben nicht ausgewählt.
Konkrete Provider, Credentials, Remoteverarbeitung, Ausführungsbudgets,
Clientkonfigurationsänderungen, Rotationsschwellen und persistenter
Sitzungszustand benötigen bei späterer Einführung ihre eigene Entscheidung.
Diese Prüfung enthält keine offenen `CONFLICT`-Klassifikationen.

## Behobene Integrationsprobleme

Das unveränderte Cache-Werkzeug liegt jetzt am manifestierten Ziel
`.ai/foundation/rule_context_cache/rule_context_cache.py`. Die frühere Kopie
unter `.ai/foundation/capabilities/rule-context-cache/` wurde nach Prüfung der
logischen Inhaltsgleichheit entfernt. LF und CRLF wurden nur für diesen
Vergleich normalisiert; die `.gitattributes` bleibt unverändert.

Der bisherige unformatierte Governance-Verweis in `AGENTS.md` war für die
Referenz-Discovery unsichtbar. Der vollständige Verweispfad verwendet jetzt
Markdown-Links: Root-Einstieg, Projektregelrouter und Entscheidungsindex.
Der Index enthält auch die bereits angenommenen DEC-0004 und DEC-0005.

Der Foundation-Cache kann unformatierte Verweise nicht selbst als fehlende
Projektautorität erkennen. Deshalb bleibt sein Referenzcode unverändert,
während die Projektprüfung `tools/governance/validate_rule_context.py` die
tatsächlich erfassten Quellen gegen die kanonischen Projektregeln und alle
angenommenen Registry-Entscheidungen prüft. Sie ist Bestandteil der regulären
Repositoryvalidierung und ein verpflichtender Vorabcheck vor Cache-Check oder
Record. Eine Lücke sperrt Wiederverwendung und Persistenz; native Discovery
und die vollständige erste Scopeanalyse bleiben verpflichtend.

Die aktuelle [Validierungsanleitung](VALIDATION.md) wählt beide Fähigkeiten
aus. Die frühere [1.8-Bewertung](FOUNDATION_UPGRADE_1_8.md) bleibt ein
historischer Nachweis ihrer damaligen Auswahl und wird nicht umgeschrieben.
Es wurde kein persistenter Operatorcache angelegt oder konfiguriert.

## Semantischer Transfer und Herkunft

- `COMPLEMENTARY`: Neue Kernpolicies und Schemas ergänzen die
  Projektgovernance, ohne neue ausführbare KI-Fähigkeiten auszuwählen.
- `PROJECT_STRONGER`: Datenschutz, Writer-Gates, Projektvalidatoren und
  fehlender Break-Glass-Bypass bleiben erhalten.
- `PROJECT_SELECTABLE_OVERRIDE`: Vorhandene CI-Supersession bleibt bestehen;
  Ressourcenklassen und Integrationsbindung stehen in `VALIDATION.md`.
- `INTENTIONAL_OVERRIDE`: `AGENTS.md` erhält ausschließlich den aktualisierten
  Foundation-Block plus die projektspezifischen Discovery- und Cachegrenzen.
- `INTENTIONAL_OVERRIDE`: Der Registry-Workflow erhält seine vorhandene
  Bootstrap-Behandlung, Projektregistrypfad und Concurrency-Konfiguration.
- Alle übrigen ausgewählten Foundation-Dateien entsprechen dem aktuellen
  Manifest. Die Receipt steht unter
  [installation-provenance.json](../../.ai/foundation/installation-provenance.json).
- Historische Artefakte, bestehende Registrierungen, v2-Profil und
  `register_artifact.py` bleiben erhalten; WI-0021 registriert nur diesen
  Upgrade-Umfang.

GitHub-Schutz und Bypass-Akteure werden nicht geändert. Workflowdateien und
grüne Läufe allein belegen keine serverseitige Durchsetzung. Die bestehende
Empfehlung für getrennte Core-Safety-/CI-Gates-Rulesets bleibt eine spätere
Projektentscheidung; fehlende erforderliche Checks blockieren weiterhin.

## Validierung

Die aktuellen Ergebnisse und ausstehenden GitHub-Prüfungen stehen im
[Projektstatus](../project/PROJECT_STATUS.md). Diese Wave prüft:

- `FOUNDATION_INTEGRITY`: aktueller Quellvalidator mit beiden ausgewählten
  Fähigkeiten und exakter Receipt;
- `PROJECT_SEMANTIC`: Projekt-, Registry- und transitive Discovery-Prüfung;
- `RUNTIME_EMPIRICAL`: Cache-Regressionsfälle, vollständiger
  Repositorytestadapter und Kompilierung betroffener Governance-Werkzeuge;
- commitgenaue GitHub-Checks `repository-quality` und `registry-integrity`.

Produktcontainer, private Medien und externe KI-Laufzeiten sind keine
Ausführungsziele dieser Wave. Die Fixture-Prüfung verwendet die verfügbare
Python-3.13-/zlib-1.3.1-Toolchain; historische Ergebnisbindungen werden nicht
gelockert.
