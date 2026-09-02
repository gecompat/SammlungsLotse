# Foundation-Upgrade 1.8

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0015

## Vergleichsstand

- installierte Foundation-Version: 1.7.0;
- bisheriger Foundation-Quellcommit:
  `d49f978f33001fcc098998ff7c04ffb209b28033`;
- neue Foundation-Version: 1.8.0;
- neuer Foundation-Quellcommit:
  `7ddc29988b23570f462e46ebf527f8dfdd05fd75`;
- ausgewählte Adapter: GitHub Copilot, Claude Code und Gemini;
- ausgewählte optionale Fähigkeit: `artifact-registry-github`;
- nicht ausgewählte optionale Fähigkeit: `rule-context-cache`.

## Vollständige Feature-Bewertung

Zwischen 1.7.0 und 1.8.0 wurde genau ein Feature eingeführt oder materiell
geändert. Der mit dem Foundation-Werkzeug berechnete Kandidatensatz ist damit
vollständig.

### `rule-context-cache`: `RECOMMENDED`

Die Empfehlung ist anwendbar:

- SammlungsLotse wird in vielen getrennten, aufeinanderfolgenden Waves
  entwickelt;
- dieselben zusätzlichen Projektregeln und Abhängigkeiten werden dabei
  wiederholt vollständig gelesen und semantisch ausgewertet;
- die native `AGENTS.override.md`-/`AGENTS.md`-Discovery kann und muss bei
  jedem neuen Lauf erhalten bleiben;
- die Host-Richtlinie erlaubt einen nicht versionierten Cache außerhalb des
  Repositorys, ohne bereits einen projektspezifischen Cachepfad auszuwählen.

Übernommen wird der verpflichtende Sicherheitsvertrag für den Fall einer
späteren Cache-Nutzung: Ein Treffer benötigt die vollständige Repository-,
Worktree-, Scope-, Discovery-, Inhalts-, Git- und Abhängigkeitsevidenz.
Änderungen an Anweisungen, Scope oder Topologie sowie Unsicherheit führen zu
`CACHE_MISS`; begrenzte Änderungen an zusätzlichen Quellen invalidieren auch
alle transitiven Abhängigkeiten. Semantische Analysen bleiben sitzungslokal.

Die optionale Referenzimplementierung `rule-context-cache` wird in dieser
Wave nicht ausgewählt. Es wird weder ein persistenter Cacheeintrag noch ein
Projekt- oder Hostpfad konfiguriert. Eine spätere Einführung bleibt eine
eigene Projektentscheidung und muss die nicht versionierte, inhaltsfreie und
nicht autoritative Persistenzgrenze einhalten.

## Semantische Integration

- `COMPLEMENTARY`: Der Foundation-Block in `AGENTS.md`, `WORKING_RULES.md`
  und `MODEL_ROUTING_POLICY.md` ergänzt den projekt-eigenen Discovery- und
  Kostenvertrag um die fail-closed Wiederverwendungsregeln.
- `EQUIVALENT`: Die projekt-eigene Authority-Discovery außerhalb des
  verwalteten `AGENTS.md`-Blocks bleibt unverändert und führt weiterhin zu
  `docs/governance/PROJECT_RULES.md`.
- `PROJECT_STRONGER`: Projektstatus, Handover, Validierungsbefehle,
  Datenschutzgrenzen und die Registrierung bleiben weiterhin
  projektspezifisch führend.
- `PROJECT_STRONGER`: Der angepasste Registry-Workflow mit
  Bootstrap-Behandlung und aktuelleren Action-Versionen bleibt erhalten.
- Es bestehen keine `FOUNDATION_REQUIRED_CONFLICT`,
  `TARGET_INTERNAL_CONFLICT` oder `ORPHANED_AUTHORITY`.

## Semantischer Dateiplan

- `CREATE`: `.ai/foundation/RULE_CONTEXT_CACHE_POLICY.md` und
  `.ai/foundation/schemas/rule-context-cache.schema.json`;
- Upgrade auf die manifestierten 1.8-Quellen:
  `FOUNDATION_RULESET.md`, `feature_catalog.json`, `WORKING_RULES.md`,
  `MODEL_ROUTING_POLICY.md` und `repo_map.yaml`;
- semantisches Update ausschließlich des verwalteten Foundation-Blocks in
  `AGENTS.md`; die projekt-eigene Discovery bleibt erhalten;
- `UNCHANGED`: alle weiteren manifestierten Foundation-Kerndateien, Adapter
  und die ausgewählte Fähigkeit `artifact-registry-github`;
- `UNCHANGED`: `.ai/artifact_registry.json` bleibt Registration Authority im
  Profil `foundation-artifact-registry/v2`; WI-0015 dokumentiert nur diese
  Upgrade-Wave, historische IDs und Registrierungssemantik werden nicht
  migriert;
- `UNCHANGED`: Repository-Schutz und die offene Foundation-1.7-Empfehlung zur
  Repository-Kontinuität. Diese Wave ändert keine GitHub-Rulesets,
  Bypass-Akteure oder Ausfallschwellen.

## Validierungsumfang

- `FOUNDATION_INTEGRITY`: Foundation-Validator 1.8 mit der ausgewählten
  GitHub-Registry-Fähigkeit;
- `PROJECT_SEMANTIC`: Repository- und v2-Registry-Validierung;
- `RUNTIME_EMPIRICAL`: vollständiger Repositorytest und `compileall` für die
  betroffenen Governance-Werkzeuge;
- GitHub: die erforderlichen Checks für den exakten Pull-Request-Head und eine
  Post-Merge-Prüfung von `origin/main`.

## Lokales Ergebnis

Am 2026-09-02 wurden ausgeführt:

- Foundation-Zielvalidator 1.8: 4 INFO, 0 Warnungen, 0 Fehler und 0 Blocker;
- Projekt- und v2-Registry-Prüfung: erfolgreich für 62 Artefakte;
- vollständiger Repositorytest: 273 entdeckt, 15 eingefrorene
  Current-Preimage-Prüfungen ausgeschlossen, fünf historische Ersatzprüfungen
  und 258 erfolgreich ausgeführte Tests;
- `compileall` und `git diff --check`: erfolgreich;
- Foundation-Transfer-Manifest- und Feature-Katalog-Guard: jeweils 0 Blocker;
- Foundation-Quelltests: 94/94 erfolgreich.

Der Foundation-Projektvalidator meldete zusätzlich zwei nicht blockierende
Self-Scan-Warnungen im eigenen Validatorquelltext: Dieser enthält selbst das
Suchmuster für absolute Benutzerpfade und das kanonische Platzhaltermuster.
Er meldete 0 Fehler und 0 Blocker. Die GitHub-Prüfungen und die
Post-Merge-Verifikation werden commitgenau außerhalb dieses lokalen Nachweises
geführt.
