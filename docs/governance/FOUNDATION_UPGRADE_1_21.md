# Foundation 1.21 und Prüfung der Testzyklen

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0024

Artifact UID: urn:uuid:01a120e0-7346-75c0-a66b-734b881ef859

Stand: 2026-10-09

## Grenze und Quellbindung

Ein Implementierungsverantwortlicher bearbeitet nur den Foundationtransfer,
die tatsächlichen Test-/CI-/Log-/Reviewwege und die dadurch nötige lokale
Governancekorrektur. Produktarchitektur, Experimente, Fixtures, historische
Hashes, Runtimeinfrastruktur und Automation bleiben außerhalb. Nach
Foundation-, Projekt-, Selektor- und betroffenen Regressionen sowie dem
geschützten PR-Merge endet die Wave. Verbrauchsmessung für Accounttokens oder
CI-Minuten liegt nicht verlässlich vor; Einsparungen werden nicht behauptet.

`origin/main` von `gecompat/AI_Repository_Foundation` wurde einmal auf
`d720db4f2f0d043756a958d5195d0e62090b1c8f` festgelegt. Dessen
Manifest und Feature-Katalog bestimmen Version 1.21.0. Installierter
Ausgangsstand war 1.20.0 aus
`39ae5c534bb0cf78046485754ed1be7867bf9534`.
Der Quellhelper ermittelte sieben Kandidaten (ein neues Feature, sechs
materielle Änderungen); [die vollständige Bewertung](FOUNDATION_UPGRADE_1_21.json)
klassifiziert jeden genau einmal. Der Transfer folgt `foundation/AI_TRANSFER.md`
des gepinnten Quellstands. Die bestehenden Adapter sowie
`artifact-registry-github` und `rule-context-cache` bleiben ausgewählt.
Die [Provenienz](../../.ai/foundation/installation-provenance.json) bindet
Manifesthash, Quellcommit und ausgewählte Dateien. Root-Bridge und vorhandener
Registryworkflow behalten begründete Projekt-Overrides. Die
[1.20-Bewertung](FOUNDATION_UPGRADE_1_20.md) bleibt historisch.

## Tatsächlicher Overhead und Disposition

| Bereich | Befund und Schutzvertrag | Disposition |
| --- | --- | --- |
| Testtrigger | `Repository Quality` startete für jeden PR-Head und `main`-Push alle Runtime- und historischen Prüfungen, auch bei reinem Status-/Handover-Diff. Aktuelle Headbindung bleibt Pflicht. | [DEC-0006](../decisions/DEC-0006-CI_VALIDATION_SCOPE.md) lässt nur für exakt diese zwei Dokumente die nicht betroffenen Runtime-Schritte aus; Projekt-/Registryprüfung und beide erforderlichen CI-Kontexte bleiben. Unbekannte Diffs führen zur Vollprüfung. |
| Doppelte Ergebnisvalidatoren | TEST-0001, EXP-0002 bis EXP-0007 und EXP-0009 bis EXP-0017 wurden direkt im Workflow und nochmals durch die Repository-Suite geprüft. Die Suite enthält zusätzliche Negativ-/Semantiktests. | 16 direkte Wiederholungen entfallen; Suite-Oracles, historische Preimages und die fünf nicht äquivalent abgedeckten WI-Qualifikationsschritte bleiben. |
| Validator-Selbsttests und Phasen | Der Text „für Produkt-, Governance- und Fixture-Code“ konnte als volle lokale Suite nach jedem Edit gelesen werden. Unbekannte gemeinsame Abhängigkeiten müssen konservativ bleiben. | `VALIDATION.md` trennt fokussierte Entwicklung von stabiler Integration. Für alle Pfade außer der exakten Status-Allowlist bleibt CI zunächst voll: ohne vollständige semantische Abhängigkeitsmatrix wäre eine breitere Auswahl nicht ausreichend abgesichert. |
| Logs und Modelle | CI-Exitstatus und lokale Logs sind deterministisch auswertbar. Es besteht kein Projektzwang, grüne Gesamtausgaben ins Modell zu laden oder Belege wiederholt semantisch prüfen zu lassen. | Relevante Fehler und Bindungen lokal eingrenzen; weitere Review-/Modellaufrufe nur bei neuer semantischer Frage, Befund, geänderten Eingängen oder vorgeschriebenem Review. Keine neue Reader- oder Telemetrieinfrastruktur. |
| Review und Polling | Projektregeln verlangen einen Owner, endlichen Umfang und zusätzliche Reviews nur mit konkreter offener Frage. Concurrency ersetzt überholte CI-Läufe; exakter Head bleibt nötig. | Diese Schutzregeln bleiben. Kein automatisches Review-von-Review und kein unverändertes Polling. PR-Status wird ereignis-/zustandsgebunden geprüft. |

Die getrennte `Artifact Registry Integrity`-Prüfung bleibt wegen
Cross-PR-Kollisionen und semantischem Merge erforderlich; ihr einfacher
Head-Check ist zwar teilweise redundant, aber der eigenständige Pflichtkontext
und dessen Fehlerisolation schützen die Registrierung. Der Foundationvalidator
ist kein Ersatz für diese Projektchecks. Keine allgemeine `docs/`-Ausnahme:
historische Ergebnis-, Planungs- und Governancequellen können semantische
Abhängigkeiten von Produkt oder Evidenz besitzen.

Die Selektorregressionen prüfen Status-Positivfälle, Produkt-/Test-/gemeinsame
Abhängigkeiten, unbekannte Pfade, ungültige Commits, Git-Fehler und Löschungen.
Ein übersprungener Runtime-Schritt wird als nicht anwendbar, nie als frisch
ausgeführt behandelt. Lokale und CI-Prüfergebnisse werden nach Ausführung
auf den jeweiligen Stand gebunden; keine alte grüne Prüfung wird auf einen
neuen Head übertragen.

## Lokaler Prüfstand

Am 2026-10-09 bestanden auf Windows: der Foundation-1.21-Validator mit den
beiden ausgewählten Fähigkeiten (`FOUNDATION_INTEGRITY`: 82 INFO, keine
Warnung/Fehler/Blocker), Projekt- und v2-Registryvalidator (93 Artefakte),
Governance-Discovery (194 Quellen, 92 unter `docs/`), Selektor-/Upgrade- und
Rule-Context-Regressions, die vollständige Repository-Suite unter Python
3.13 (361 Tests, vier sichtbare Windows-Symlink-Skips) und die fünf weiterhin
separaten aktuellen Produktqualifikations-Ergebnisvalidatoren. Die Suite
enthielt die bytegenaue TEST-0001-Reproduktion und alle durch den Workflow
entfernten historischen Ergebnisvalidierungen; diese wurden nicht nochmals
direkt ausgeführt. Der Selektor wählt für diesen gemischten Workflow-/Regel-
Diff den vollständigen Pfad. `git diff --check` meldete keine Textfehler.

Der CI-Check auf dem exakten PR-Head und der geschützte Merge sind separate
Integrationsbelege; der lokale Prüfstand behauptet sie nicht vor Ausführung.
