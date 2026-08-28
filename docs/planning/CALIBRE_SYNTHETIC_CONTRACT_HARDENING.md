# WI-0008: Synthetischen Calibre-Projektionsvertrag reproduzierbar härten

Status: DONE — IMPLEMENTIERT UND SYNTHETISCH QUALIFIZIERT

Stand: 2026-08-28

Artifact: WI-0008

## Ziel

WI-0008 macht die tatsächliche synthetische Qualifikation des bereits
implementierten WI-0007-Produktpfads reproduzierbar und mehrgliedrig. Ein
eingecheckter Qualifikationsweg materialisiert eine ausschließlich
synthetische Calibre-Bibliothek aus gebundenen TEST-0001-Eingängen, führt das
unveränderte exakte Produktprofil aus und prüft die erwartete minimale
Projektion.

Die Wave ist eine Härtungs- und Evidenzwave. Sie fügt keine neue
Nutzerfähigkeit hinzu und erweitert den WI-0007-Vertrag nicht.

## Gebundene synthetische Fälle

Die Materialisierung muss mindestens drei voneinander unterscheidbare
Calibre-Datensätze erzeugen und folgende Fallformen gemeinsam abdecken:

- mehrere Autoren in stabiler Reihenfolge;
- mehrere Sprachen einschließlich Deutsch und einer RTL-Sprache;
- mindestens einen Datensatz mit mehreren Formaten;
- mindestens einen Datensatz ohne Format oder ohne optionale Listenwerte;
- Unicode in Titel oder Autorennamen;
- bewusst unterschiedliche externe Calibre-IDs und eine von der
  Erstellungsreihenfolge unabhängige, nach ID sortierte Projektion.

Die Medien stammen ausschließlich aus der aktiven TEST-0001-Fixture-Version.
Synthetische Metadaten und die genaue Erzeugungssequenz werden eingecheckt.
Es werden keine privaten Bibliotheken, Hostpfade, Benutzernamen oder
Bibliotheksnamen als Evidenz gespeichert.

## Materialisierungsgrenze

Der schreibende Calibre-Aufruf ist ausschließlich ein Test- und
Qualifikationswerkzeug. Er darf nur in einem neu erzeugten, ausdrücklich
angegebenen Bereich unter `C:\rep\tmp\SammlungsLotse` arbeiten und muss
Ziele außerhalb dieses Bereichs ablehnen. Er ist nicht aus der Produkt-CLI
erreichbar und darf keine bestehende Bibliothek öffnen oder verändern.

Die Materialisierung verwendet das bereits gebundene Calibre-9.13.0-Image
und dokumentierte `calibredb`-Befehle. Netzwerk, automatische Zielsuche und
Hostkonfiguration bleiben ausgeschlossen. Eingangsdateien werden read-only
eingebunden; der erzeugte Prüfbestand ist wegwerfbar und muss nach der
Qualifikation vollständig entfernt werden.

## Qualifikationsvertrag

Die Implementierungs-Wave muss mindestens nachweisen:

1. Die eingecheckte Materialisierung erzeugt bei zwei frischen Läufen
   denselben fachlichen Bibliotheksinhalt.
2. Die tatsächliche Produkt-CLI verarbeitet genau eine ausdrücklich
   angegebene synthetische Bibliothek über die vorhandene Copy-on-read-
   Grenze.
3. Deutsche und JSON-Ausgabe enthalten ausschließlich Calibre-ID, Titel,
   Autoren, Sprachen und normalisierte Formate.
4. Zwei JSON-Produktläufe sind byteidentisch und nach externer Calibre-ID
   sortiert.
5. Mehrfachautoren, Mehrsprachigkeit, Mehrformat, fehlende Werte und Unicode
   werden gegen vorab festgelegte Oracles geprüft.
6. Rohwerte mit Pfaden, Dateinamen, nicht erlaubten Feldern oder
   typabweichenden Strukturen gelangen nicht in die Projektion.
7. Quell-Fixtures und synthetische Quellbibliothek bleiben während der
   Produktläufe bytegleich.
8. Erfolg und bewusst ausgelöste Fehler-, Timeout-, Outputgrenzen- und
   Abbruchpfade hinterlassen weder Profilcontainer noch Taskdaten.
9. Der Qualifikationsnachweis bindet vollständiges Produkt- und
   Materialisierungs-Preimage, Profil-ID, Image-ID, Falloracles und
   Kriterienergebnis.
10. Registry-, Dokument-, Fixture-, Experiment-, WI-0005-, WI-0007-,
    Produkt-, Foundation-, `compileall`- und `git diff --check`-Regression
    sind erfolgreich.

## Unveränderte Produktgrenzen

WI-0008 ändert nicht:

- genau eine ausdrücklich angegebene lokale Bibliothek pro Aufruf;
- die fünf Felder ID, Titel, Autoren, Sprachen und Formate;
- deutsche oder deterministische JSON-Ausgabe ausschließlich auf stdout;
- Copy-on-read, dokumentierte `calibredb`-CLI und exaktes
  Calibre-9.13.0-Profil;
- keine automatische Erkennung, Remote-Verbindung, Persistenz oder Writes;
- keine direkte Kopplung an `metadata.db` oder interne Calibre-Tabellen.

Ein Produktcode-Diff ist nur zulässig, wenn die erweiterte tatsächliche
Qualifikation einen konkreten Vertragsfehler reproduziert. Eine solche
Korrektur muss innerhalb der unveränderten Grenzen bleiben, durch einen
gezielten Regressionstest gedeckt und im Pull Request ausdrücklich erklärt
werden.

## Nichtziele

Nicht Bestandteil sind reale Bestände, Last- oder Skalierungsversprechen,
mehrere Bibliotheken, automatische Erkennung, Content Server, Remote-URLs,
weitere Calibre-Felder, Custom Columns, Tags, Identifikatoren, Cover,
Volltext, Suche, Dubletten, externe Metadaten, Routing, Persistenz, Browser,
REST, Agents, native Windows-Calibre-Ausführung und jeder Writer.

## Ausführungsreihenfolge

1. GATE-0004 und diesen angenommenen Vertrag ohne Produktcode nach
   `origin/main` mergen.
2. Materialisierungswerkzeug, Oracles, automatisierte Verträge und
   erweiterten Qualifikationsnachweis in einer eigenen Implementierungs-Wave
   ergänzen.
3. Zwei frische Materialisierungen, tatsächliche deutsche und JSON-
   Produktläufe sowie die vollständige lokale Regression ausführen.
4. Erst nach exakten erforderlichen GitHub-Checks mergen und WI-0008 auf
   `done` setzen.

Die Benutzeranweisung vom 2026-08-28 autorisiert die autonome Fortsetzung
über Planung, Registrierung, ausschließlich synthetische Implementierung und
Qualifikation, Pull Requests, exakte CI-Prüfung und Merge nach
`origin/main`.

## Implementierung und Abnahme

Die getrennte Implementierungs-Wave hat einen manifestgebundenen
Materialisierer ergänzt. Er akzeptiert nur ein neues Ziel unter
`C:\rep\tmp\SammlungsLotse`, prüft drei TEST-0001-Fixture-Hashes, das exakte
Profil und die Image-ID und führt ausschließlich dokumentierte
`calibredb add`, `add_format` und `list`-Aufrufe aus. Jede Fixture wird
einzeln read-only, die neue synthetische Bibliothek schreibbar und weder
Netzwerk noch Hostkonfiguration eingebunden. Container und Fehlerreste werden
begrenzt bereinigt.

Die erste tatsächliche mehrgliedrige Materialisierung reproduzierte einen
Produktvertragsfehler: `calibredb --for-machine` serialisiert mehrere Autoren
als eine mit ` & ` getrennte Zeichenfolge. Der Adapter behandelte diese
bislang als einen Autor. Der Parser trennt jetzt genau diese dokumentierte
Maschinenform; ein fokussierter Regressionstest bindet das Verhalten. Calibre
normalisiert die synthetischen Sprachangaben tatsächlich auf ISO-639-3
`deu` und `ara`; das Oracle bindet diese beobachtete Form.

Der endgültige v2-Nachweis bestand 29/29 Kriterien. Zwei frisch
materialisierte Bibliotheken ergaben dieselbe fachliche Drei-Datensatz-
Projektion. Reale deutsche und JSON-Produktläufe belegten Mehrfachautoren,
Mehrsprachigkeit, Mehrformat, fehlende Werte, Unicode, minimale Felder,
Pfadfreiheit und byteidentische Wiederholung. Quell-Fixtures und beide
Bibliotheken blieben unverändert. Timeout, Outputgrenze und simulierter
Abbruch räumten Taskbereiche auf; nach der Gesamtqualifikation blieben weder
Qualifikationsroot noch Profil- oder Materialisierungscontainer zurück.
