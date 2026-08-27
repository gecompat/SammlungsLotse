# TEST-0001: Synthetischer E-Book-Referenzkorpus

Status: READY — SYNTHETIC CORE FIXTURES VALIDATED

Stand: 2026-08-27

Artifacts: TEST-0001, WI-0002, WI-0003

## Zweck

TEST-0001 definiert die Sollfälle, gegen die spätere E-Book-Verfahren
reproduzierbar bewertet werden. Dieses Dokument ist der Testvertrag. Alle 26
`Kern`- und vier `Ausbau`-Fälle sind als Fixture-Version `0.3.0` erzeugt und
validiert. Die früheren Fassungen `0.1.0` und `0.2.0` bleiben historische
Snapshots für bereits gebundene Experimente und Produktnachweise.

Generator, Manifest und Fixture-Einstieg stehen unter
[tests/fixtures/ebook/test-0001](../../tests/fixtures/ebook/test-0001/README.md).
Die Fixture-Validierung ist noch kein Lauf von EXP-0002 bis EXP-0006 und kein
fachlicher Produktbeleg.

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
- Der Generator verwendet ausschließlich die Python-Standardbibliothek,
  öffnet kein Netzwerk und verweigert ein bereits vorhandenes
  Ausgabeverzeichnis. Er enthält keine Produkt-, Adapter- oder
  Analyseimplementierung.

## Vollständiger Korpus v0.3

Version `0.3.0` materialisiert zusätzlich zu allen `Kern`-Fällen die vier
bereits vertraglich definierten `Ausbau`-Fälle. Die abgeschlossenen
Experimente EXP-0002 bis EXP-0007 und der WI-0005-Qualifikationsnachweis
bleiben unverändert an Version `0.2.0` gebunden; der neue Korpus deutet ihre
historische Evidenz nicht um.

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

Die erste Korpusfassung enthält zwei versionierte synthetische
Zielbibliothek-Snapshots mit absichtlich unterschiedlichen Regeln, Feldern,
Formaten, Custom Columns und fiktiven Büchern. Sie bilden keine interne
Calibre-Datenbank nach. Eine später für EXP-0002 benötigte lauffähige
Calibre-Bibliothek wird aus diesen Verträgen ausschließlich über das dort
qualifizierte, unterstützte Toolprofil erzeugt. Das Oracle beschreibt:

- welche Felder und Formate im read-only Snapshot erwartet werden;
- welche lokalen Locators intern benötigt und nach außen bereinigt werden;
- welche Fälle eindeutig passen;
- welche Fälle mehrere Regeln erfüllen;
- welche Fälle kein geeignetes Ziel besitzen;
- dass keine interne Calibre-Tabelle direkt geändert wird.

## Ausführungsmanifest v0.3.0

Das maschinenlesbare JSON-Manifest liegt unter
`tests/fixtures/ebook/test-0001/v0.3/manifest.json`. `schema_version` 1 bleibt
ein Fixture-Vertrag und wählt weder Produktpersistenz noch öffentliche API.
Das Manifest enthält:

- TEST-0001 und Fixture-Version;
- `case_key` und erzeugte Bestandteile;
- Hash und Größe jedes Eingangs;
- Erzeugungsrezept oder dokumentierte Mutation;
- erwartete Beobachtungs- und Befundschlüssel;
- erlaubte Ergebnisvarianten;
- verbotene Wirkungen;
- Lizenz- und Herkunftsnachweis;
- Generator- und Toolprofil, falls ein Werkzeug beteiligt war;
- die vier materialisierten `Ausbau`-Fallkeys und ihre getrennte Stufe.

Das Manifest enthält 26 Kernfälle, vier Ausbau-Fälle und insgesamt 49
Komponenten. Jede Komponente besitzt einen relativen Locator, Rolle,
Medientyp, Größe und SHA-256. Jedes Oracle enthält zusätzlich
Qualitätsdimension, Ressourcenprofil, Prüfmethode und verbotene Wirkungen.

## Ergebnis der Fixture-Wave

TEST-0001 ist nach tatsächlicher Erzeugung und Prüfung der vollständig
materialisierten Fassung `ready`. Die Passkriterien sind für Version `0.3.0`
erfüllt:

- alle 26 `Kern`- und vier `Ausbau`-Fälle wurden reproduzierbar erzeugt;
- jeder Fall besitzt ein maschinenlesbares Oracle und die Tabelle oben bleibt
  der menschlich prüfbare Vertrag;
- Hashes, Größen, Erzeugungsverfahren, Herkunft und MIT-Lizenz sind
  vollständig manifestiert;
- alle Inhalte sind unabhängig erzeugt und synthetisch;
- ungültige, riskante und Ressourcenlimitfälle sind ausdrücklich
  klassifiziert;
- Byte-, Repräsentations-, Ausgaben- und Werkbeziehungen sowie eindeutiges
  Routing und erwartete Enthaltung sind prüfbar;
- die read-only Prüfung einschließlich kontrolliertem Timeout ließ alle
  Original-Fixtures unverändert;
- Registry-, Dokumentations-, Reproduzierbarkeits- und Laufzeitprüfungen
  waren erfolgreich.

## Validierung und Grenzen

Lokal validiert am 2026-08-27 unter Python 3.12.10:

    python tools/fixtures/validate_ebook_reference_corpus.py

Ergebnis: 30 Fälle, 49 Komponenten, bytegenau reproduzierbar und während der
Prüfung unverändert. Der Validator prüft außerdem zentrale positive und
negative Sollbeziehungen, drei Routingresultate, EPUB-2-, Fixed-Layout- und
RTL-Marker, Pfad- und Expansionserkennung sowie einen synthetischen
100-ms-Timeout.

Version `0.1.0` bleibt unter `v0.1/` als historischer Snapshot erhalten. Der
erste reale EPUBCheck-Lauf in EXP-0005 erkannte sein OPF-Literal
`version="3.3"` als nicht unterstützt. Version `0.2.0` korrigiert dieses
Literal auf die für EPUB 3 weiterhin geltende Paketversion `3.0`, ohne die
Fallzahl, Fallkeys oder Oracles zu verändern. Version `0.3.0` übernimmt den
Kern bytegenau neu aus dem deterministischen Generator und ergänzt die vier
vorher nur vertraglich beschriebenen Ausbau-Fälle.

EPUBCheck 5.3.0 wurde tatsächlich gegen `epub2-valid-minimal`,
`epub33-valid-fixed` und `metadata-multilingual-rtl` ausgeführt. Nach der
Korrektur des EPUB-2-XHTML-1.1-Doctypes meldeten alle drei Fälle keine
Konformitätsfehler. Ein erster Fixed-Layout-Lauf erreichte kontrolliert das
Executor-Timeout und räumte vollständig auf; die unmittelbare Wiederholung
bestand. Dieser Nachweis qualifiziert nur die drei synthetischen Validfälle,
nicht weitere Formate, Accessibility oder Produktreife.

EPUBCheck wurde im Rahmen von EXP-0005 gegen die damals aktive Fassung
`0.2.0` ausgeführt; der Sicherheits- und Reproduzierbarkeitsnachweis war
erfolgreich. EXP-0002
hat zwei daraus synthetisch materialisierte Calibre-Bibliotheken erfolgreich
über eine Copy-on-read-Grenze projiziert. EXP-0003 hat EPUBCheck- und
Ace-Rohberichte gegen sieben ausgewählte Fälle je zweimal erhoben und
verlustfrei referenziert; der manuelle Accessibility-Fall bleibt ausdrücklich
manuell. EXP-0004 hat alle sechs Identitäts-Sollpaare auf fünf getrennten
Ebenen je zweimal bewertet.
EXP-0006 hat elf an Version `0.2.0` gebundene Kernfall-Zeilen in zwei
semantisch identischen, netzwerklosen Preflight-Wiederholungen bewertet;
Eingabehashes blieben unverändert und kritische Fehlfreigaben betrugen null.
Die Materialisierung der vier `Ausbau`-Fälle verändert diese historische
Evidenz nicht.
