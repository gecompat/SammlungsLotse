# Foundation 1.23 und optionale Orchestratorverträge

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0025

Artifact UID: urn:uuid:01a12557-1ddb-7b2a-bb27-c4a105829c43

Stand: 2026-10-10

## Umfang und Quellbindung

Diese endliche Wave hat einen Implementierungsverantwortlichen: Foundation-
Core und bisher ausgewählte Fähigkeiten übertragen, vollständiges Feature-
Delta und Projektkollisionen prüfen, Provenienz und aktuelle Statusquellen
aktualisieren, betroffene Verträge lokal und im geschützten PR validieren.
Produktcode, Experimente, Runtimekonfiguration, Modell-Dispatch,
automatische Continuation, Benachrichtigungen und neue Infrastruktur gehören
nicht zu diesem Auftrag. Eine weitere Review braucht eine konkrete offene
Frage. Nach Merge und Branchbereinigung endet die Wave.

`origin/main` von `gecompat/AI_Repository_Foundation` wurde einmal auf
`ec6ece8acde5328af0836bae559003eac1c51b41` gepinnt. Das Manifest an
diesem Commit nennt Version 1.23.0; installiert war 1.21.0 aus
`d720db4f2f0d043756a958d5195d0e62090b1c8f`. Der Quellhelper ermittelte
sieben Kandidaten über 1.22 und 1.23. Die
[vollständige Bewertung](FOUNDATION_UPGRADE_1_23.json) ordnet jeden genau
einmal ein. Die historischen [1.21](FOUNDATION_UPGRADE_1_21.md)- und
[1.20](FOUNDATION_UPGRADE_1_20.md)-Prüfstände bleiben erhalten.

Die Transferauswahl bleibt bei den Defaultadaptern und den Fähigkeiten
`artifact-registry-github` und `rule-context-cache`: 80 manifestierte Dateien,
darunter zwei neue Core-Dateien für atomare lokale State-I/O und das
Orchestrator-Control-Schema. Die aktualisierten Stdio-/Orchestratorverträge
sind Regeln und Schemas, keine eingerichtete Ausführung. Der Root-Bridge-
Hinweis ist ein begründeter Projektmerge; der bestehende Registryworkflow
behält seinen Projektpfad und Bootstrap. Die
[dateigenaue Provenienz](../../.ai/foundation/installation-provenance.json)
bindet den Quellcommit, Manifesthash und alle ausgewählten Inhalte. Weder
Foundation-Projektzustand noch nicht ausgewählte optionale Runtimepayloads
werden übertragen.

## Semantische Einordnung

Der neue `RULE_CONTEXT_CACHE_POLICY.md` beschreibt die native Instruction-
Kette des jeweils aktiven Clients; für dieses Repository bleibt die konkrete
Codex-`AGENTS.md`-Kette maßgeblich. Das ist eine kompatible Spezialisierung,
kein zweiter Cache oder Discoveryweg. Die neue Orchestratorsteuerung ist
optional und verlangt eine gesonderte Host-/Job-/Budget-Autorität. Hier
existiert keine solche Konfiguration; der `HEARTBEAT`-Hinweis im Foundation-
Block startet nichts und verleiht keine Berechtigung.

Die katalogisierte Empfehlung zur Session-Lifecycle-Fortsetzung bleibt
sichtbar: Für dieses Projekt genügt derzeit die manuelle, repositorygebundene
Übergabe. Eine automatische Nachfolger-Session wäre eine eigene Entscheidung
mit attestiertem Host, Schwellen, externem Handoff-Speicher und endlichem
gemeinsamem Budget. Keine dieser Fähigkeiten wird in WI-0025 aktiviert.
Ein `FOUNDATION_REQUIRED_CONFLICT`, verwaiste Projektregel oder parallele
Registry-Autorität wurde bei der semantischen Sichtung nicht festgestellt.

## Tatsächlicher Verarbeitungsaufwand

Die Pflichtbewertung aus Foundation 1.21 bleibt an realen Wegen orientiert.
`repository-quality` führt bei dieser Änderung an Foundationregeln den
vollständigen Pfad aus; die exakte Status-/Handover-Ausnahme aus DEC-0006
greift nicht. TEST-0001 und historische EXP-Ergebnisse werden weiterhin
einmal durch die Suite geprüft, fünf eigenständige aktuelle
Produktqualifikationen bleiben getrennt. Der Projektvalidator und
`registry-integrity` behalten ihre verschiedenen Verträge und erforderlichen
Statuskontexte. Fokussierte lokale Governance-/Upgrade-Regressionen dienen
der Entwicklung; eine volle Suite gehört an den stabilen Integrationsstand.

Logs und Prüfergebnisse werden lokal auf Exitstatus, Fehler und betroffene
Bindungen reduziert. Es gibt weder verpflichtende Gesamtausgabe an ein Modell
noch Review-von-Review, wiederholtes unverändertes Polling oder einen neu
angelegten Scheduler. Die Projektregel mit einem Owner, begrenzter Wave und
Reviews nur bei konkreter Frage bleibt stärker als ein optionaler autonomer
Fortsetzungsweg. Ohne verlässliche Account-/CI-Kostenmessung werden keine
Geld-, Token- oder Zeiteinsparungen behauptet. Ein breiterer CI-Pfadfilter
bleibt wegen unvollständiger transitiver Runtime-Abhängigkeitszuordnung
bewusst ausgeschlossen; unbekannte Eingänge führen zur Vollprüfung.

## Lokale Validierung

Am 2026-10-10 bestanden: Foundationvalidator `FOUNDATION_INTEGRITY`
(84 INFO, keine Warnung, Fehler oder Blocker), Quellmanifest- und
Manifesthash-Guard, Projekt- und v2-Registryvalidator (94 Artefakte),
vollständige Governance-Discovery (197 Quellen, 94 unter `docs/`),
20 fokussierte Upgrade-/Rule-Context-Tests, 67 Quelltests der neuen
Orchestrator-/Stdio-/Upgrade-Referenzen und die vollständige lokale
Repository-Suite unter Windows/Python 3.13 (361 Tests, vier sichtbar
übersprungene Symlink-Fälle). `git diff --check` und der exakte
PR-Head-Check bleiben eigenständige Bindungen. Die Source-Tests qualifizieren
die Referenzen im Quellcheckout; sie behaupten keine aktivierte optionale
Runtime in SammlungsLotse.
