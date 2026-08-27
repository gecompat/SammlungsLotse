# TEST-0001: Synthetischer E-Book-Referenzkorpus

Status: PROPOSED TEST CONTRACT — FIXTURES NOT EXECUTED

Stand: 2026-08-27

Artifacts: TEST-0001, WI-0003

## Zweck

TEST-0001 definiert die Sollfälle, gegen die spätere E-Book-Verfahren
reproduzierbar bewertet werden. Dieses Dokument ist der Testvertrag. Die
eigentlichen Dateien, Generatoren, Hashmanifeste und Laufberichte entstehen
erst in einer nachfolgenden Wave.

Der Korpus verwendet keine realen privaten Medien oder Sammlungsinventare. Er
autorisiert weder Toolinstallation noch Produktcode, externe Anfragen oder
schreibende Fachsystemoperationen.

## Testorakel je Fall

Jeder ausführbare Fall benötigt mindestens:

- stabilen `case_key` innerhalb von TEST-0001;
- Fallgruppe und geprüfte Nutzerentscheidung;
- Erzeugungsverfahren und Herkunft aller Bestandteile;
- Eingangsdateien oder Ablauf- und Snapshotbeschreibung;
- erwartete Rohbeobachtungen;
- erwartete Befunde und erlaubte Alternativbefunde;
- erwartete Enthaltung, `unknown`, `not_applicable` oder `unsupported`;
- ausdrücklich verbotene Ergebnisse und Wirkungen;
- betroffene Qualitätsdimensionen;
- Ressourcenprofil und Abbruchbedingung;
- Prüfmethode und gegebenenfalls manuelle Schritte;
- nach Erzeugung berechnete Hashes und Fixture-Version.

`case_key` ist ein lokaler Schlüssel innerhalb von TEST-0001 und keine
konkurrierende Artefaktreferenz. Neue eigenständig verwaltete Testverträge
werden weiterhin über die Registration Authority registriert.

## Daten- und Konstruktionsregeln

- Text, Metadaten, Cover und Binärbestandteile werden minimal synthetisch
  erzeugt oder stammen nachweislich aus gemeinfreien beziehungsweise
  ausdrücklich weiterverteilbaren Quellen.
- Bewusst fehlerhafte Dateien entstehen durch dokumentierte Mutationen einer
  kleinen synthetischen Ausgangsdatei.
- Erzeugung und Verpackung müssen reproduzierbar sein. Nichtfachliche
  Unterschiede wie zufällige ZIP-Zeitstempel werden kontrolliert oder im
  Oracle ausdrücklich berücksichtigt.
- Schutzfälle enthalten nur synthetische Marker oder technisch ungefährliche
  Testverschlüsselung. Sie umgehen keinen realen Schutz.
- Ressourcenlimitfälle verwenden kleine Generatoren oder deklarierte
  simulierte Limits statt gefährlich großer versionierter Binärdateien.
- Externe Testbestände werden nur in einer getrennten optionalen Suite mit
  Quellrevision, Lizenz, Attribution und unveränderter oder dokumentiert
  abgeleiteter Form verwendet.
- Ein öffentlicher Upstream-Test belegt nicht automatisch die
  SammlungsLotse-Akzeptanz; sein lokales Oracle bleibt ausdrücklich.

## Kernkorpus v0.1

`Kern` bezeichnet die erste ausführbare Fassung. `Ausbau` bleibt im Vertrag,
wird aber nicht benötigt, um die ersten vier Experimente zu beginnen, sofern
deren eigene Eingänge vollständig abgedeckt sind.

| case_key | Stufe | Konstruktion | Wesentliches Oracle |
|---|---|---|---|
| `ingress-stable-minimal` | Kern | kleine abgeschlossene synthetische EPUB-Datei | stabiler Snapshot, Hash und Format erkannt; keine Wirkung |
| `ingress-growing-file` | Kern | Größe oder Änderungsrevision wechselt zwischen zwei Beobachtungen | Analyse wird vertagt oder als instabil markiert |
| `container-corrupt` | Kern | abgeschnittenes oder strukturell defektes Archiv | Parserfehler als Befund; kein Entpacken am Original |
| `container-path-traversal` | Kern | Archiveintrag mit ausbrechendem Pfad | Sicherheitsbefund; kein Schreiben außerhalb des Arbeitsbereichs |
| `container-expansion-limit` | Kern | stark komprimierbare synthetische Ressource mit kleinem Testlimit | begrenzter Abbruch und Ressourcenbefund |
| `protected-or-encrypted` | Kern | synthetisch geschützter oder verschlüsselter Container | Schutzstatus oder `unsupported`; keine Umgehung |
| `format-unknown` | Kern | unbekannte minimale Binärsignatur mit E-Book-Endung | Inhaltssignatur schlägt Dateiendung; tiefe Analyse enthält sich |
| `epub2-valid-minimal` | Ausbau | minimales valides EPUB-2-Paket | Version erkannt und profilbezogene Befunde nachvollziehbar |
| `epub33-valid-reflow` | Kern | minimales valides EPUB 3.3 mit Navigation und Cover | keine erfundenen Fehler; Rohbericht und Profil erhalten |
| `epub33-valid-fixed` | Ausbau | minimales Fixed-Layout-Paket | Layouttyp erkannt; nicht als Reflowable bewertet |
| `epub-missing-resource` | Kern | Manifest- oder Spine-Ressource fehlt | erwarteter Struktur- oder Referenzbefund mit Fundstelle |
| `epub-navigation-defect` | Kern | Navigation fehlt oder verweist ungültig | Navigationsbefund getrennt von allgemeiner Öffnbarkeit |
| `epub-active-or-remote` | Kern | Skript oder Remote-Ressource im Paket | Merkmal und Risiko sichtbar; kein Netzabruf |
| `epub-a11y-auto-finding` | Kern | Bild ohne geeignete textuelle Alternative | automatischer Befund mit Werkzeugcode und Fundstelle |
| `epub-a11y-manual-required` | Kern | syntaktisch vorhandene, aber inhaltlich fragwürdige Beschreibung | kein automatisches Konformitätsurteil; manuelles Review erforderlich |
| `metadata-conflict-title` | Kern | Paket-, Dateiname- und Calibre-Snapshot enthalten abweichende Titel | drei Beobachtungen bleiben erhalten; Konflikt statt Überschreiben |
| `metadata-contributor-roles` | Kern | Autor, Übersetzer und Herausgeber mit ähnlichen Namen | Personenbeitrag und Rolle bleiben getrennt |
| `metadata-multilingual-rtl` | Ausbau | mehrsprachige Metadaten und RTL-Inhalt | Sprache, Richtung und Schrift bleiben erhalten |
| `edition-sample-vs-full` | Kern | kurze Leseprobe und längere Vollausgabe mit ähnlichen Metadaten | keine Gleichsetzung als austauschbare Repräsentationen |
| `identity-byte-equal` | Kern | identische Bytes unter zwei Namen und Pfaden | byteidentisch; Quelle und Locator bleiben getrennt |
| `identity-repackaged` | Kern | gleiche Inhalte mit anderer ZIP-Reihenfolge und Verpackungsmetadaten | nicht bytegleich; Kandidat auf Repräsentationsebene |
| `identity-multiformat-edition` | Kern | synthetische EPUB- und PDF-Repräsentation derselben Ausgabe | Ausgabenkandidat, keine Dateigleichheit |
| `identity-edition-vs-translation` | Kern | Ausgangsausgabe und Übersetzung desselben Werks | möglicher Werkbezug, aber verschiedene Ausgaben |
| `identity-title-collision` | Kern | anderes Werk mit gleichem oder stark ähnlichem Titel | negativer Sollfall; keine Identitätszusammenführung |
| `routing-unique` | Kern | Regeln und Evidenz passen genau zu einem von zwei Zielbeständen | ein erklärter Zielkandidat, keine Ausführung |
| `routing-ambiguous` | Kern | widersprüchliche Merkmale passen zu mehreren Zielen | erwartete Enthaltung und sichtbarer Konflikt |
| `routing-unknown` | Ausbau | keine Regel oder unbekannte Inhaltsklasse | kein Standardziel; `unknown` oder Enthaltung |
| `run-unchanged-skip` | Kern | identischer Eingangs- und Profil-Snapshot in zweitem Lauf | teure Analyse wird nachvollziehbar wiederverwendet oder übersprungen |
| `run-resume` | Kern | kontrollierter Abbruch nach einem bekannten Zwischenschritt | Fortsetzung ohne doppelte oder verlorene Ergebnisse |
| `run-tool-timeout` | Kern | synthetischer Werkzeuglauf überschreitet kleines Zeitlimit | begrenzter Abbruch, partieller Status, Original unverändert |

## Sollbeziehungen für Identität

Die Identitätsfälle bilden keine einzelne boolesche Dublettenwahrheit. Das
Oracle unterscheidet mindestens:

| Paar | Datei | Repräsentation | Ausgabe | Werk |
|---|---|---|---|---|
| `identity-byte-equal` | gleich | Kandidat gleich | Kandidat gleich | Kandidat gleich |
| `identity-repackaged` | verschieden | Kandidat gleich | Kandidat gleich | Kandidat gleich |
| `identity-multiformat-edition` | verschieden | verschieden | Kandidat gleich | Kandidat gleich |
| `identity-edition-vs-translation` | verschieden | verschieden | verschieden | Kandidat verbunden |
| `identity-title-collision` | verschieden | verschieden | verschieden | verschieden |

`Kandidat gleich` oder `Kandidat verbunden` ist ein erwarteter
Entscheidungsgegenstand und noch keine kanonische Zusammenführung.

## Zielbibliotheken

Die erste Korpusfassung enthält mindestens zwei synthetische Calibre-
Zielbibliotheken mit absichtlich unterschiedlichen Regeln. Ihre Namen und
Inhalte sind rein fiktiv. Das Oracle beschreibt:

- welche Felder und Formate im read-only Snapshot erwartet werden;
- welche lokalen Locators intern benötigt und nach außen bereinigt werden;
- welche Fälle eindeutig passen;
- welche Fälle mehrere Regeln erfüllen;
- welche Fälle kein geeignetes Ziel besitzen;
- dass keine interne Calibre-Tabelle direkt geändert wird.

## Ausführungsmanifest der nächsten Wave

Die Fixture-Wave erzeugt ein maschinenlesbares Manifest aus diesem Vertrag.
Das Format wird erst in dieser Wave ausgewählt. Es muss mindestens enthalten:

- TEST-0001 und Fixture-Version;
- `case_key` und erzeugte Bestandteile;
- Hash und Größe jedes Eingangs;
- Erzeugungsrezept oder dokumentierte Mutation;
- erwartete Beobachtungs- und Befundschlüssel;
- erlaubte Ergebnisvarianten;
- verbotene Wirkungen;
- Lizenz- und Herkunftsnachweis;
- Generator- und Toolprofil, falls ein Werkzeug beteiligt war.

## Passkriterien für die Fixture-Wave

TEST-0001 bleibt bis zur tatsächlichen Fixture-Erzeugung und Prüfung
`proposed`. Die erste ausführbare Fassung ist ausreichend, wenn:

- alle `Kern`-Fälle reproduzierbar erzeugt werden;
- jeder Fall ein maschinenlesbares und menschlich prüfbares Oracle besitzt;
- Hashes und Herkunft vollständig sind;
- keine privaten oder nicht weiterverteilbaren Inhalte enthalten sind;
- absichtlich ungültige Fälle nicht versehentlich als allgemeine
  Referenzqualität dargestellt werden;
- mindestens zwei unabhängige Identitätsstufen und beide Routingergebnisse
  einschließlich Enthaltung geprüft werden können;
- Original-Fixtures während aller read-only Versuche unverändert bleiben;
- Registry-, Dokumentations- und relevante Laufzeitprüfungen erfolgreich
  sind.
