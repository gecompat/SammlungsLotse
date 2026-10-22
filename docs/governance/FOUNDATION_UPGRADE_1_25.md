# Foundation 1.25 und verständliche Dokumentationswege

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0026

Artifact UID: urn:uuid:01a1617c-8a96-7827-b137-2f2ec0fa58d0

Stand: 2026-10-22

## Umfang und Quellbindung

Diese endliche Wave hat einen Implementierungsverantwortlichen. Sie umfasst
Foundation-Core und die bisher ausgewählten Fähigkeiten, vollständiges
Feature-Delta, semantische Projektintegration, betroffene menschliche
Dokumentationswege, Provenienz, lokale Prüfungen und geschützte PR-Integration.
Produktcode, Experimente, Testorakel, CI-Vertrauensinfrastruktur und
automatische Ausführung bleiben außerhalb. Nach Merge und Bereinigung des
eigenen Branches endet die Wave; weitere Reviews brauchen eine konkrete
offene Frage.

`origin/main` von `gecompat/AI_Repository_Foundation` wurde einmal auf
`9e1b9974de58ea775d40c7c6045cd5057ba8b30c` gepinnt. Das Manifest
an diesem Commit nennt Version 1.25.0. Installiert war 1.23.0 aus
`ec6ece8acde5328af0836bae559003eac1c51b41`. Der Quellhelper ermittelte
vier Kandidaten über 1.24 und 1.25; die [vollständige Bewertung](FOUNDATION_UPGRADE_1_25.json)
ordnet jeden genau einmal ein. Ältere Bewertungen und Prüfzahlen bleiben
historische Nachweise.

Die Manifest-Auswahl umfasst 81 Dateien mit Defaultadaptern sowie
`artifact-registry-github` und `rule-context-cache`: vor Transfer 68
unverändert, zwölf semantisch zu mergen, eine neu. Die neue
`TEST_EVIDENCE_REUSE_POLICY.md` ist ein Vertrag, kein CI-Adapter. Die
Coreänderungen sind quellengetreu übertragen. Der Root-Bridge-Hinweis wurde
in den geschützten Block integriert; die projektbezogene Discovery darunter
bleibt erhalten. Der Registryworkflow bewahrt seine Projektpfade und seinen
Bootstrap als begründete Abweichung. Die [dateigenaue Provenienz](../../.ai/foundation/installation-provenance.json)
bindet Manifest, Quellcommit und beide beabsichtigten Overrides.

## Semantisches Delta

Die neue Dokumentationsregel ist `APPLY_DEFAULT`. Der Root-README bleibt
Projekt- und Reifeeinstieg; die vorhandenen lokalen Befehle liegen nun in der
[read-only-Anleitung](../guides/LOCAL_READONLY_EXAMPLES.md), die Vorbereitung,
Berichtsdeutung, Grenzen und Fehlerhinweise verbindet. [docs/README.md](../README.md)
führt dorthin. [`.ai/README.md`](../../.ai/README.md) erklärt Menschen den
AI-Einstieg, Identität, kanonische Registry, Manifestprovenienz und Prüfwege,
ohne eine zweite Regelautorität zu bilden. Der Pfad `README → Anleitung →
Produktgrenzen/Validierung` und der technische Pfad `AGENTS.md → .ai-Überblick
→ Registry/Schema/Validator/Evidenz` wurden als betroffene Wege ausgewählt.
Die große chronologische [Planungsübersicht](../planning/README.md) verlangt
für neue Leser weiterhin vorausgesetzte interne Kennungen. WI-0027 hält
diese vorhandene Altlast in der Registry fest: Projektpflege ist die
verantwortliche Rolle; beim nächsten materiellen Umbau des Planungseinstiegs
sind aktuelle Aufgaben- und historische Nachweispfade zu gliedern. Das
Upgrade behauptet keine vollständige Dokumentationskonformität aller
Bestandsseiten.

Die aktualisierte mehrschichtige Validierung ist `APPLY_DEFAULT`: menschliche
Verständlichkeit gehört zu `PROJECT_SEMANTIC`; Linkintegrität und
`FOUNDATION_INTEGRITY` allein belegen sie nicht. Die neue deterministische
Erfolgsausgabe ohne reinen Bestätigungsmodellaufruf ist ebenfalls
`APPLY_DEFAULT`. Lokale, bereits strengere Vertragsauswahl und der endliche
Waveumfang bleiben kompatibel.

Die lokale-zu-CI-Testevidenzanerkennung ist `RECOMMENDED`, aber nicht
aktiviert. Ein geschützter Produzent/Verifier, Trust- und Widerrufsautorität,
vollständige Eingangs-/Umgebungs-/Frischeäquivalenz und ausdrücklich
zugelassene Gates fehlen. Hashes oder lokale PASS-Dateien ersetzen keinen
CI-Lauf. Bei künftig tatsächlich teuren äquivalenten Tests kann ein eigener
registrierter Scope Wirtschaftlichkeit und diese Grenzen prüfen; derzeit
bleibt die bestehende Pflicht-CI die notwendige Ausführung. Diese Empfehlung
ist keine offene Auswahl für das vorliegende Upgrade.

Ein `FOUNDATION_REQUIRED_CONFLICT`, verwaiste Projektregel oder zweite
Registrierungsautorität wurde nicht festgestellt. Produktgrenzen,
read-only-Verträge, dauerhafte Referenzen und historische
Experimentnachweise bleiben unangetastet.

## Tatsächlicher Verarbeitungsaufwand

Der CI-Selektor in `repository-quality.yml` führt für diesen gemischten
Foundation-/Dokumentations-/Registry-Diff den vollständigen Pfad aus. Die
enge Ausnahme aus DEC-0006 gilt nur für einen exakten Status-/Handover-Diff;
ein breiterer Dokumentations-Skip wäre ohne vollständige transitive
Abhängigkeitszuordnung ungesichert. `validate_repository.py` prüft Links,
Quellen und Discovery; `registry-integrity` prüft zusätzlich Cross-PR-
Kollisionen und semantische Mergegleichheit. Diese Kontexte sind verschieden.
Die Suite führt die historischen TEST-/EXP-Ergebnisverträge einmal aus;
aktuelle Produktqualifikationen bleiben gesondert. Fokussierte lokale
Upgrade-/Governancetests dienen der Entwicklung, eine volle Suite dem
stabilen Integrationsstand. Keine Testevidenz wird als remote ausgeführt
ausgegeben, wenn sie nur lokal vorliegt.

Mechanische Manifest-, Hash-, Registry-, Link-, Zähl- und CI-Bindungsfragen
werden lokal ausgewertet. Erfolgreiche Gesamtausgaben erfordern keinen
zusätzlichen Modellaufruf. Für semantische Dokumentationswege liest der
Implementierungsverantwortliche nur betroffene Seiten samt notwendigen
Folgeseiten; der Discoverycheck erfasst weiterhin die ganze maßgebliche
Governance. Kein wiederholtes unverändertes Polling, Review-von-Review oder
neuer Scheduler ist Teil dieser Wave. Ein unabhängiges Review wird nur bei
konkretem offenen Risiko oder bestehender Pflicht ergänzt. Ohne verlässliche
Account-/CI-Verbrauchsmessung werden keine Geld- oder Tokenersparnisse
behauptet; die Grenze ist dieser registrierte Umfang mit einem Owner.

## Prüfstand

Am 2026-10-22 bestanden am lokalen Integrationskandidaten: Quellmanifest-
und Manifesthash-Guard ohne Blocker oder stale Hashes; 65 gezielte
Foundation-Quelltests; Foundationvalidator mit 85 INFO und null Warnungen,
Fehlern oder Blockern; Projektvalidator; v2-Registryvalidator mit 96
Artefakten; vollständige Governance-Discovery mit 205 Quellen, davon 97
unter `docs/`; 20 fokussierte Upgrade-/Discovery-/Sessiontests sowie die
gesamte Repository-Suite unter Windows/Python 3.13 mit 361 erfolgreichen
Tests und vier sichtbaren Symlink-Skips. Der synthetische JSON-Eingangslauf
der neuen Anleitung war read-only erfolgreich; die dokumentierten CLI-
Optionen wurden mit den jeweiligen `--help`-Ausgaben abgeglichen.

Die betroffenen Leserwege wurden über README, Anleitung, Produktgrenzen,
Validierung und AI-/Registry-Einstieg verfolgt. Projektlinkprüfung und
manuelle Pfadprüfung decken diese Seiten ab; WI-0027 bleibt als begrenzte
historische Navigationslücke. Diese Prüfung behauptet keine UX-Abnahme
aller Bestandsdokumente. PR-Head- und nachgelagerte `main`-Checks bleiben
gesonderte Integrationsnachweise.
