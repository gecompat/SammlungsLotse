# Foundation 1.20 und effiziente Governance

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0023

Artifact UID: urn:uuid:01a12056-7d0b-7e2f-a889-9f8d67bc3731

Stand: 2026-10-09

## Registrierter Umfang und Quellbindung

Ein Implementierungsverantwortlicher bearbeitet genau diese Governancewave:
Foundationtransfer, lokale Discovery-/Lese-/Cacheverträge, Statusabgleich und
begrenzte aktuelle Sicherheitsanalyse. Keine Produktarchitektur, neue
Runtime-Infrastruktur, Automation oder weitere Produktwave. Ein zusätzlicher
Reviewer benötigt eine konkrete offene Frage. Verbrauchsmessung für Geld oder
Accounttokens ist nicht verfügbar; der endliche Taskumfang und ein Owner sind
die operative Grenze. Nach Integration und Bereinigung endet die Wave.

`origin/main` von `gecompat/AI_Repository_Foundation` wurde einmal am
2026-10-09 aufgelöst und auf
`39ae5c534bb0cf78046485754ed1be7867bf9534` gepinnt. Manifest und Feature-Katalog
dieses sauberen Quellstands bestimmen Foundation 1.20.0. Ausgangsversion ist
1.19.0 aus `4aafd20442275d0fdedf291fc6e12e8fe1f683cc`.

Historische Bewertungen bleiben auffindbar:
[1.7](FOUNDATION_UPGRADE_1_7.md), [1.8](FOUNDATION_UPGRADE_1_8.md) und
[1.19](FOUNDATION_UPGRADE_1_19.md). Der erweiterte Discoverycheck fand den
zuvor nicht erreichbaren 1.7-Bericht anhand seiner Autoritätsdeklaration.
Der fehlende Link wurde ergänzt; Quelle und historischer Status bleiben erhalten.

Das Direct-AI-Transfer-/Upgradeverfahren des Quellcommits wurde verwendet:
alle 78 ausgewählten Quellen vor Transfer gegen ihre portablen Manifesthashes
geprüft, bestehende Zielbytes gegen die alte Provenienz abgeglichen und die
beiden projektspezifischen Mergeziele semantisch erhalten. Ausgewählt bleiben
die Defaultadapter und `artifact-registry-github`, `rule-context-cache`.
Kein optionaler Planner, Router, Executor, Provisionierer oder Orchestrator
wird zusätzlich installiert. Core enthält neu die Processing-Efficiency-
Policy, Detailreferenz, speicherbasierte Referenz und Budgetschema.

Die [dateigenaue Provenienz](../../.ai/foundation/installation-provenance.json)
enthält den Manifesthash, Quellcommit und jeden installierten Hash. Die
Overrides sind der ergänzte projektgeführte Root-Einstieg und der vorhandene
Registryworkflow mit Projektpfad, Bootstrap und bestehender CI-Konfiguration.
MIT-Notice, Rootlizenz, Produktprofile und historische Kennungen bleiben erhalten.

## Vollständiges semantisches Delta

Der Quellhelper ermittelte 21 Kandidaten: ein neues Feature und 20 materielle
Änderungen. Die [maschinenlesbare Bewertung](FOUNDATION_UPGRADE_1_20.json)
klassifiziert jeden genau einmal mit Projektevidenz und Begründung. Kein
Feature wird aus einem vermuteten fehlenden Bedarf ausgelassen.

Die Effizienzempfehlung ist durch den Nutzerauftrag autorisiert und umgesetzt:
scopeabhängige Lektüre, sichere Sessionwiederverwendung ohne persistenten
Operatorcache, ein Owner und endlicher Umfang. Die datierte Fortschreibung
von [DEC-0005](../decisions/DEC-0005-RULE_CONTEXT_CACHE.md) dokumentiert die
dauerhafte lokale Auswahl, ohne ihre ursprüngliche Entscheidung zu ersetzen.

Offen bleibt die bereits bekannte Empfehlung `repository-continuity-break-glass`.
Empfehlung für diese Wave: strikte Pflicht-CI behalten. Ein späterer Ausfallpfad
braucht eine separate angenommene Entscheidung zu Akteuren, Klassifikation,
Audit und verpflichtender Nachvalidierung. Alternative ist, dauerhaft auf
verfügbare Pflicht-CI zu warten. Es gibt aktuell keinen CI-Ausfall und keinen
Upgradeblocker. Es wird kein Bypass eingerichtet oder verwendet.

## Wirksame Projektregeln und sichere Wiederverwendung

Vor dem Upgrade erfasste die reine Repository-Discovery am unveränderten
Ausgangscommit `bddb40ca6b5a133b7075196590724dc38ebb0d21` 180 Quellen,
darunter 81 unter `docs/`; der frühere 177-Quellen-Befund bleibt historisch.
Die Zahlen stammen aus Repositorydiscovery ohne globale Hostinstructions,
nicht aus einer Bescheinigung der aktiven Clientkonfiguration.

[Projektregeln](PROJECT_RULES.md), [Validierung](VALIDATION.md) und Root-
`AGENTS.md` trennen jetzt den vollständigen Auffindbarkeitsgraph von der
notwendigen semantischen Auswahl. Sämtliche angenommenen Entscheidungen
bleiben im Discoverygate; keine Entscheidung wird allein wegen ihres Status
vor jeder Bearbeitung gelesen. Der Validator entdeckt zusätzlich neu
deklarierte `AUTHORITATIVE`-Quellen unabhängig von den Links unter Prüfung.
Das Entfernen eines Links versteckt deshalb keine maßgebliche Autorität.

Der Sessioncaller muss aktuelle native Autorität und effektive Discovery
belegen, ausgewählte reale Working-Tree-Bytes prüfen und alle transitiven
semantischen Abhängigkeiten inventarisieren. Nur tatsächlich vorhandene
Analyse am exakten Schlüssel ist wiederverwendbar. Die unveränderte Core-
Referenz benötigt keinen persistenten Record. Verlorene Analyse, unbekannte
Discovery, neue Autorität oder unvollständige Abhängigkeiten erlauben keinen
erfundenen Treffer. Commit-/Worktreewechsel werden frisch gebunden.

Der getrennte persistente Cache behält den vollständigen Graph, strikte
Git-/Worktreebindung, atomare Records und alle drei bisherigen Statuswerte.
Es ist kein Operatorcache eingerichtet. Die Regression verwendet kontrollierte
synthetische native Discoveryevidenz; sie behauptet keine attestierte
Live-Clientdiscovery oder tatsächlich eingesparte Modellkosten.

## Aktueller GitHub-/Repositoryabgleich

[PR #128](https://github.com/gecompat/SammlungsLotse/pull/128) ist seit
2026-10-05T18:28:10Z gemergt. Mergecommit und lokales/entferntes main am
Beginn dieser Wave sind identisch:
`bddb40ca6b5a133b7075196590724dc38ebb0d21`. Beide damaligen Pflichtchecks
`repository-quality` und `registry-integrity` sind `SUCCESS`. Vor Anlage
dieser Wave bestanden null offene PRs.

Aktueller [Projektstatus](../project/PROJECT_STATUS.md) und
[Handover](../project/HANDOVER.md) korrigieren die überholte
Integrationsaussage. Der [WI-0022-Prüfbericht](BRANCH_CONSOLIDATION_2026_10_05.md)
behält seine lokalen Vor-Merge-Prüfstände und erhält einen datierten Nachtrag.
GraphQL bestätigte erneut strikte erforderliche Checks auf main und
`allowsForcePushes=false`. Historische grüne Ergebnisse sind keine Validierung
späterer Commits.

## Aktuelle Ace-/npm-Sicherheitsanalyse

Am 2026-10-09 wurde eine temporäre Kopie ausschließlich von `package.json`
und `package-lock.json` aus EXP-0003 mit lokalem Node `24.19.0` und npm
`11.17.0` geprüft:

    npm audit --omit=dev --json --ignore-scripts --no-fund --no-progress

Der Aufruf war auf 120 Sekunden begrenzt, ohne Installation, Paket-Scripts,
Browser- oder Containerstart. Nur der öffentliche Abhängigkeitsgraph ging an
die npm-Registry. Exitcode 1 bedeutet hier gefundene Sicherheitsbefunde; der
Audit lieferte ein gültiges Ergebnis ohne Infrastrukturfehler. Die
[npm-Dokumentation](https://docs.npmjs.com/cli/v11/commands/npm-audit/)
beschreibt diese Abfrage und die getrennte mutierende `fix`-Operation.

Ergebnis: 34 betroffene Pakete beziehungsweise Metavulnerabilities, davon
2 `critical`, 20 `high`, 12 `moderate`, null `low`/`info`. Das ist keine Anzahl
einzigartiger Advisories und kein Nachweis tatsächlicher Ausnutzbarkeit im
isolierten Experiment. Die kritischen Paketaggregate betreffen `handlebars`
und `proxy-addr`; aktuelle Primärreferenzen sind unter anderem
[GHSA-p8wg-vrv2-v86f](https://github.com/advisories/GHSA-p8wg-vrv2-v86f) und
[GHSA-jqcg-44mw-7w3h](https://github.com/advisories/GHSA-jqcg-44mw-7w3h).

Der Lockhash blieb vor/nach Audit unverändert:
`f1b20f79e0c1c5b7cb5aae2f3890bafe5f455a352a311476d2f6f8578f1f3074`.
Der außerhalb von Git verbleibende aktuelle Audit-JSON-Bericht hat SHA-256
`15c9eb03186a57bd694f3dc78c6685f70e385a90c610b25dda81e68558879ecf`.
Die historische EXP-0003-Evidenz mit 22 Befundpaketen wird nicht überschrieben.

GitHub meldete beim getrennten vollständigen GraphQL-Abgleich 35 offene
Dependabot-Alerts, alle am EXP-0003-Lock: 18 `HIGH`, 13 `MODERATE`, 4 `LOW`.
Die unterschiedlichen Zahlen/Schweregrade sind getrennte npm-Paketaggregate
und GitHub-Alerts aus unterschiedlichen Datenbanken. Kein Alarm wurde
dismissiert; die enge Dependabot-PR-Ausnahme bleibt erhalten.

Das eingefrorene Profil deaktiviert weiterhin die interne Chromium-Sandbox.
Die damalige äußere Podman-Isolation ist historische Evidenz, keine aktuelle
Ace-Produktqualifikation. Ace bleibt außerhalb des Produktpfads. Empfehlung:
historischen Nachweis erhalten und Ace weiterhin nicht produktiv übernehmen.
Falls Accessibility künftig ausgewählt wird, braucht ein neues Experimentprofil
oder eine Produktübernahme einen eigenen registrierten Scope, aktuelles
Abhängigkeits-/Sandboxprofil und getrennte Qualifikation. Alternativen sind
ein separat geprüftes aktuelles Ace-Profil oder ein anderes geeignetes Werkzeug;
beides benötigt eine erläuterte Ergebnis-/Nutzerauswahl. Diese Wave führt
keinen solchen Auftrag ein.

## Validierung und Abschlussbindung

Lokal am 2026-10-09 unter Windows/Python 3.13.15 mit zlib 1.3.1 erfolgreich:

- Gepinnter Foundationvalidator, Profil `full`, beide ausgewählten Fähigkeiten:
  `FOUNDATION_INTEGRITY`, 82 INFO, null Warnungen/Fehler/Blocker.
- `validate_repository.py`, v2-Registryvalidator: Projektverträge und 91 Artefakte.
- `validate_rule_context.py`: 190 auffindbare Quellen, 88 unter `docs/`, keine
  fehlende maßgebliche Quelle. Der Graph wurde erweitert, nicht verkürzt.
- `run_repository_tests.py`: 373 Tests entdeckt, 17 eingefrorene Current-
  Prüfungen ersetzt, sechs historische Ersatzprüfungen und eine sichtbare
  Capability-Ausnahme; 356 Tests ausgeführt, vier sichtbare Windows-Symlink-Skips.
  Darin acht Discovery-, elf Session-/Persistenz- und eine Upgrade-Regression.
- `validate_ebook_reference_corpus.py`: TEST-0001 0.3.0, alle 30 Fälle und
  49 Komponenten bytegenau reproduzierbar, Eingänge unverändert.
- `run_exp_0003.py --validate-result`: 14/14; vier EXP-0003-Regressionen bestanden.
- Kompilierung betroffener Foundation-/Governance-/Testmodule und `git diff --check`.
- Leerer Git-Diff gegen den Ausgangscommit für Produktcode, Runtimeprofile,
  alle Experimente/Fixtures, CI-Workflows und die Dependabot-Konfiguration.

Der erste Fixture-/Suitelauf unter dem inzwischen voreingestellten Python
3.14.7 war nicht erfolgreich: byteverschiedene ZIP-Regeneration und fünf
Produkt-/Preimage-Assertions. Das entspricht der schon dokumentierten
[GATE-0024-Grenze](../planning/EBOOK_GATE_0024_ZIP_REPRODUCIBILITY.md), wird
nicht als grün umgedeutet und nicht durch Fixtureänderungen verdeckt. Ein
anfänglicher Fehler im neuen Provenienztest verwendete einen falschen
Receipt-Feldnamen; er wurde am tatsächlichen Schema korrigiert. Der
vollständige korrigierte Lauf unter dem vorhandenen Python 3.13 bestand.
Diese Wave trifft keine neue allgemeine Toolchainentscheidung. Die Pflicht-CI
verwendet ihren bestehenden Python-3.12-Pfad.

Die geschützte PR-Integration benötigt beide Pflichtchecks auf dem exakten
Head. Ihre Bindung wird nach erfolgreichem Lauf ergänzt. Kein historischer
grüner Befund wird als Ergebnis für den neuen Head übernommen.
