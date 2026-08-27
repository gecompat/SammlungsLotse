# WI-0006: Read-only Mehrdatei-Eingangsbericht umsetzen

Status: DONE — IMPLEMENTIERT UND SYNTHETISCH ABGENOMMEN

Stand: 2026-08-27

Artifact: WI-0006

## Entscheidung

WI-0006 wird als nächste eng begrenzte Produktwave angenommen. Die vorhandene
lokale E-Book-Eingangstriage verarbeitet künftig neben genau einer Datei auch
mehrere ausdrücklich in der CLI angegebene Dateien. Sie prüft alle Eingänge
unabhängig und vollständig und gibt einen gemeinsamen deutschen Bericht oder
einen stabilen JSON-Vertrag ausschließlich auf stdout aus.

Die schnelle WI-0004-Prüfung bleibt der Standard. Der bestehende WI-0005-
EPUBCheck-Adapter wird nur durch den vorhandenen expliziten
`--deep-read-only`-Schalter und nur für den jeweiligen positiv freigegebenen
Snapshot aufgerufen. Die Wave führt weder Verzeichnissuche noch Berichtsdatei,
Persistenz, Netzwerkzugriff, Fachsystemzugriff oder schreibende Medienwirkung
ein.

## Kleinster Nutzwert

Ein Nutzer kann eine kleine, ausdrücklich ausgewählte Gruppe lokaler Dateien
in einem Lauf prüfen und erhält:

- für jeden Eingang eine positionsgebundene, namen- und pfadfreie Triage;
- eine Zusammenfassung der Folgeaktionen und optionalen Tiefenbewertungen;
- alle erwartbaren Einzelfehler, ohne dass ein anderer Eingang übersprungen
  wird;
- dieselben Einzelverträge wie bei der bisherigen Ein-Datei-Prüfung;
- eine deterministische maschinenlesbare Gesamtausgabe für identische stabile
  Eingänge und dieselbe Reihenfolge.

Die Eingabeposition ist die einzige öffentliche Zuordnung. Dateiname,
Originalpfad, Verzeichnis und Archiveintragsnamen werden nicht als
Sammlungsinventar in den Gesamtvertrag aufgenommen.

## Anwendungs- und CLI-Vertrag

Die bestehende Oberfläche `tools/run_ebook_intake.py` bleibt der einzige
Einstieg:

```text
python tools/run_ebook_intake.py DATEI_A DATEI_B
python tools/run_ebook_intake.py --json DATEI_A DATEI_B
python tools/run_ebook_intake.py --deep-read-only \
  --deep-temp-root TEMP_ROOT DATEI_A DATEI_B
```

Genau ein Eingang bewahrt die bestehende WI-0004-/WI-0005-Ausgabe byte- und
bedeutungsgleich. Ab zwei Eingängen entsteht der neue Batch-Vertrag. Er
enthält eine Schema-ID, feste Grenzen, die Gesamtzahl, aggregierte Zähler und
eine in Eingabereihenfolge sortierte Liste. Jeder Listeneintrag enthält nur
seinen nullbasierten `input_index`, seinen Verarbeitungsstatus und den
vorhandenen Einzelbericht. Ein unerwarteter lokaler Fehler wird positions-
gebunden und ohne Locator als `internal_error` sichtbar; danach werden die
restlichen Eingänge weiter geprüft.

Der Prozesscode wird erst nach allen Eingängen bestimmt:

- `0`, wenn kein unerwarteter interner Fehler und bei aktivierter Tiefenprüfung
  kein `not_assessed` vorliegt;
- `4`, wenn mindestens eine angeforderte Tiefenprüfung `not_assessed` bleibt,
  aber kein interner Fehler auftrat;
- `3`, wenn mindestens ein interner Verarbeitungs- oder Ausgabegrenzenfehler
  auftrat;
- `130` bei ausdrücklicher Unterbrechung.

Ein fachliches `stop`, `review`, `defer` oder `abstain` ist weiterhin ein
erfolgreich erzeugtes Ergebnis und kein technischer Prozessfehler.

## Feste Grenzen der ersten Wave

- mindestens zwei und höchstens 32 ausdrücklich angegebene Dateien pro
  Batch-Bericht;
- höchstens 256 MiB summierte Snapshot-Bytes;
- unveränderte WI-0004-Einzelgrenzen, insbesondere 32 MiB pro Eingang;
- sequenzielle Verarbeitung ohne Parallel-, Queue- oder Hintergrundmodell;
- höchstens 48 MiB UTF-8 für den vollständigen JSON-Batch-Bericht;
- höchstens 20 sichtbare Einzelbefunde je Tiefenprüfung in der deutschen
  Ansicht; der vollständige begrenzte Rohbericht bleibt nur im JSON-Vertrag;
- keine Globs, Verzeichnisauflösung, rekursive Suche oder implizite
  Bestandsentdeckung durch Produktcode.

Wird eine Batch-Grenze bereits aus den Argumenten oder aus vollständig
erfassten Snapshotgrößen verletzt, endet die Gesamtausgabe fail-closed und
pfadfrei. Ein tiefer Providerlauf beginnt für einen Eingang erst nach dessen
positiver Triage; die übrigen Eingänge bleiben davon unabhängig.

## Architekturgrenze

Die neue Batch-Anwendungsschicht orchestriert bestehende Einzelverträge. Sie
ändert weder `TriageService`, `TriageReport`, `DeepReadOnlyToolPort` noch den
EPUBCheck-Providervertrag. Lokale Pfade bleiben ausschließlich im vorhandenen
Snapshot-Adapter und in der CLI-Komposition. Der Batch-Vertrag kennt nur
Positionen und Ergebnisumschläge.

Die Implementierung verwendet weiterhin Python 3.12 und die
Standardbibliothek. Sie führt keine neue Laufzeitabhängigkeit ein. Der
optionale tiefe Weg verwendet ausschließlich das bereits qualifizierte,
vorab bereitgestellte WI-0005-Profil und erzeugt je freigegebenem Snapshot
einen getrennten task-privaten Arbeitsbereich.

## Akzeptanzkriterien

WI-0006 ist erst `done`, wenn:

1. genau ein Eingang die bisherige deutsche und JSON-Ausgabe mit und ohne
   Tiefen-Opt-in unverändert bewahrt;
2. zwei bis 32 ausdrücklich übergebene Dateien vollständig, sequenziell und
   in Eingabereihenfolge verarbeitet werden;
3. Dateien, Verzeichnisse, Symlinks, fehlende und nicht unterstützte Eingänge
   ausschließlich über bestehende pfadfreie Ergebniswerte erscheinen;
4. `continue_deep_read_only`, `review`, `stop`, `defer` und `abstain` im
   Batch-Vertrag getrennt bleiben;
5. ein erwartbarer Fehler oder geschlossenes Gate keinen anderen Eingang
   überspringt;
6. ein unerwarteter Einzelfehler positionsgebunden `internal_error` erzeugt,
   keine privaten Angaben ausgibt und die restliche Verarbeitung fortsetzt;
7. tiefe Prüfung ohne Opt-in nie startet und mit Opt-in nur für jeden positiv
   freigegebenen Snapshot startet;
8. ein tiefes `not_assessed` sichtbar bleibt, die übrigen Eingänge nicht
   abbricht und nach vollständiger Ausgabe Prozesscode `4` ergibt;
9. Anzahl-, Einzel-, Summen- und Ausgabegrenzen positive und negative Tests
   besitzen;
10. zwei Läufe über dieselben stabilen Eingänge in derselben Reihenfolge
    byteidentisches JSON erzeugen;
11. unterschiedliche Eingabereihenfolgen ausschließlich die Position und
    Ergebnisreihenfolge nachvollziehbar ändern;
12. Berichte und Fehlermeldungen keine lokalen Pfade, privaten Dateinamen oder
    implizit entdeckten Bestandsdaten enthalten;
13. alle verarbeiteten Originale und das Repository-Dateiinventar vor und nach
    der sichtbaren synthetischen Abnahme unverändert sind;
14. Netzwerk-, Fachsystem- und dauerhafte Schreibwirkungen null bleiben und
    kein Verzeichnis automatisch gelesen wird;
15. Registry-, Dokument-, Fixture-, Experiment-, Produkt- und Foundation-
    Regression sowie `compileall` und `git diff --check` erfolgreich sind;
16. Projektstatus, Übergabe und CLI-Dokumentation den tatsächlichen Stand und
    die verbleibenden Grenzen wiedergeben.

## Nichtziele

Nicht Bestandteil von WI-0006 sind:

- Verzeichnis-, Bibliotheks-, Watcher-, Queue- oder Hintergrundverarbeitung;
- persistente Berichtsdateien, Datenbank, Cache oder Suchindex;
- Calibre oder ein anderes Fachsystem;
- Accessibility-, Metadaten-, Identitäts-, Dubletten- oder Routinglogik;
- Browser, REST, Agents, Plugins oder öffentliche API;
- Parallelisierung oder allgemeine Batch-Infrastruktur;
- Writer, Import, Reparatur, Transformation, Verschieben oder Umbenennen;
- ein zweiter tiefer Provider oder ein neues Ausführungsprofil;
- reale oder private Medien als Repository- oder PR-Evidenz.

## Implementierungsreihenfolge

1. Diesen Vertrag und WI-0006 als `accepted` auf `origin/main` registrieren.
2. Den Batch-Anwendungsvertrag und die CLI-Komposition in einer getrennten
   Implementierungs-Wave ergänzen.
3. Mit ausschließlich TEST-0001-Eingängen automatisiert und über tatsächliche
   CLI-Prozesse abnehmen.
4. Erst nach vollständiger lokaler Regression und den erforderlichen exakten
   GitHub-Checks mergen und WI-0006 auf `done` setzen.

Die Benutzerfreigabe vom 2026-08-27 umfasst diese Planung, Implementierung,
synthetische Abnahme, Pull Requests, exakte CI-Prüfung und den Merge nach
`origin/main`.

## Implementierung und Abnahme

Die getrennte Implementierungs-Wave hat den angenommenen Vertrag umgesetzt:

- `BatchIntakeService` verarbeitet ausschließlich explizit erzeugte
  `SnapshotReader` sequenziell und kennt keine Eingabepfade;
- `BatchReport` und `BatchItemReport` binden Schema, Position, Status,
  Zusammenfassung und die festen Anzahl-, Summen- und Ausgabegrenzen;
- genau ein CLI-Eingang verwendet unverändert den bisherigen Einzelweg, ab
  zwei Eingängen wird der neue Batch-Vertrag ausgegeben;
- erwartbare Snapshot- und Formatfehler bleiben normale Einzelberichte,
  unerwartete Fehler werden pfadfrei als `processing.internal_error`
  isoliert und spätere Eingänge weiterverarbeitet;
- ein Überschreiten der summierten Snapshotgrenze verhindert jeden tiefen
  Lauf und markiert nicht mehr verarbeitete Positionen fail-closed;
- der tiefe Opt-in verwendet unverändert den WI-0005-Adapter und erzeugt für
  jeden positiv freigegebenen Snapshot einen getrennten Task.

Siebzehn neue fokussierte Verträge prüfen alle fünf Folgeaktionen,
Reihenfolge, Determinismus, fehlende Eingänge, interne Fehler,
Weiterverarbeitung, Anzahl-, Summen- und Ausgabegrenzen, Tiefen-Opt-in,
Prozesscodes, Pfadbereinigung und Originalunverändertheit. Die vollständige
Repository-Regression umfasst 99 erfolgreiche Tests.

Eine tatsächliche lokale CLI-Abnahme verarbeitete EPUB 2 und ein
mehrsprachiges RTL-EPUB gemeinsam über das gebundene WI-0005-Profil. Beide
separaten EPUBCheck-5.3.0-Läufe endeten mit
`no_epubcheck_conformance_errors_reported`, vollständig bereinigten Tasks und
null verbleibenden Profilcontainern. Ihre Rohberichte blieben getrennt und
besitzen die SHA-256-Werte
`d2410027c3fede6e6e804d5f7028ae32e184bfdbaa233ccf26925a86c26fcf65` und
`35c1d551a773f0b9392279b42398db2b12268ebb76d7dc7d24a8ed32cdd64ec6`.
Der TEST-0001-Validator bestätigte danach erneut alle 30 Fälle, 49
Komponenten, reproduzierbare Erzeugung und unveränderte Eingänge.

Da WI-0005 die sichtbare CLI als Preimage bindet, wurde dessen vollständige
Produktqualifikation nach der Erweiterung erneut ausgeführt. Das neue exakte
CLI-Preimage
`493840b8f5ad2f2f97c0e7e605de25386ef3602936c5719b826cbc91e6e73b7a`
bestand alle 12 Kriterien einschließlich unverändertem Einzelweg, Erfolg,
Befund, geschlossenem Gate, `not_assessed`, effektiver Isolation,
Outputgrenze, Timeout sowie Task- und Container-Cleanup.
