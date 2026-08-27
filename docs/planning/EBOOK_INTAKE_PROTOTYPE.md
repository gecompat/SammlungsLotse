# WI-0004: Dünner read-only E-Book-Eingangstriage-Prototyp

Status: ACCEPTED — IMPLEMENTIERUNG INNERHALB DER GRENZE AUTORISIERT

Stand: 2026-08-27

Artifact: WI-0004

## Ziel und kleinster vollständiger Nutzwert

Eine Person wählt genau eine lokale Datei aus und erhält ohne Veränderung des
Eingangs eine sichtbare, begründete Antwort auf zwei Fragen:

1. Ist der Eingang für eine spätere tiefe read-only Prüfung unterstützt,
   nicht unterstützt oder nicht sicher entscheidbar?
2. Soll der nächste Schritt `continue_deep_read_only`, `defer`, `stop`,
   `review` oder `abstain` sein?

Der Prototyp endet mit dieser Antwort. Er führt den vorgeschlagenen nächsten
Schritt nicht aus.

## Autorisierungsgrundlage

GATE-0001 hat Eingangstriage ausschließlich innerhalb der Grenze aus stabilem
Snapshot, flachem Preflight und sichtbarer Folgeaktion oder Enthaltung
angenommen. EXP-0006 belegt die kritische fail-closed Entscheidung an elf
synthetischen Zeilen. WI-0004 konkretisiert diese Grenze als ersten
Produktprototyp und ist vor Beginn der Implementierung `accepted`.

Die Annahme von WI-0004 gilt nicht für Erweiterungen des Umfangs.

## Vollständiger Ablauf

```text
lokal ausgewählte reguläre Datei
  -> begrenzter unveränderter In-Memory-Snapshot
  -> flache Signatur- und Containerbeobachtung
  -> getrennte Beobachtungen und Befunde
  -> fail-closed Formatfähigkeit und Folgeaktion
  -> deutsche CLI-Ansicht oder pfadbereinigter JSON-Bericht
```

### Eingangsgrenze

- genau eine ausdrücklich angegebene reguläre Datei;
- keine Verzeichnisrekursion und kein automatisches Entdecken;
- symbolische Links werden nicht verfolgt;
- Entwicklung, Tests und Abnahme verwenden ausschließlich TEST-0001 oder
  andere minimale synthetische Fixtures;
- maximal 32 MiB Eingangsgröße;
- der Snapshot besteht aus unveränderlichen Bytes im Arbeitsspeicher;
- Größe, Änderungsidentität und Dateihash werden während der Erfassung
  gegengeprüft; Veränderung führt zu `defer`.

### Flacher Preflight

Der Preflight beobachtet ausschließlich:

- Dateiendung, magische Signatur, Größe und SHA-256;
- Öffnungsfähigkeit als ZIP und exakten EPUB-Mimetype;
- Anzahl, komprimierte und deklarierte expandierte Größe der Einträge;
- absolute Pfade, Parent-Traversal und doppelte Mimetype-Einträge;
- ZIP-Verschlüsselungsflags und `META-INF/encryption.xml`;
- begrenzte bytebasierte Hinweise auf Script- oder Remote-Inhalt.

Er extrahiert keine Datei, führt keinen Inhalt aus und verwendet keinen
allgemeinen XML-, HTML-, EPUB- oder PDF-Parser. Die Ressourcenobergrenzen
sind 512 Archiveinträge, 128 MiB deklarierte Gesamtexpansion, 2 MiB je flach
gelesenem Markup-Eintrag, 16 MiB insgesamt gelesenem Markup und 128 KiB
serialisiertem Bericht. Eine Überschreitung führt zu `stop`.

### Ergebnisvertrag

Der gemeinsame Anwendungsvertrag trägt die Kennung
`sammlungslotse/ebook-intake-report/v1` und trennt:

- `snapshot`: Größe und SHA-256, aber keinen lokalen Pfad;
- `observations`: unveränderte oder minimal strukturierte Rohbeobachtungen;
- `findings`: aus Beobachtungen abgeleitete Befunde mit stabilen Codes;
- `format_capability`: `supported`, `unsupported` oder `unknown`;
- `next_action`: genau einen der fünf Gate-Zustände;
- `deep_read_only_allowed`: getrennte boolesche Fähigkeit;
- `effects`: explizit null für Netzwerk, Original-, Fachsystem- und andere
  Dateisystemschreibwirkungen sowie für gestartete tiefe Werkzeuge;
- `limits`: die tatsächlich angewandten Ressourcenobergrenzen.

Der Bericht enthält weder absolute noch relative lokale Pfade, Dateinamen,
Archiv-Eintragsnamen, URLs, Inhalte oder extrahierte Metadaten. Numerische
Größen und Hashes bleiben zulässige lokale Evidenz.

## Kern- und Adaptergrenzen

- Der Anwendungskern orchestriert Snapshot und Preflight, kennt aber weder
  CLI-Argumente noch Betriebssystempfade.
- Ein lokaler Snapshot-Adapter ist die einzige Komponente mit Dateizugriff.
- Der Preflight arbeitet ausschließlich auf dem unveränderlichen Snapshot.
- CLI und JSON sind Projektionen desselben Berichts und enthalten keine
  eigene Entscheidungslogik.
- Spätere Format-, Werkzeug-, Fachsystem- oder Provideradapter dürfen nur
  hinter `continue_deep_read_only` folgen und gehören nicht zu WI-0004.

## Begrenzte technische Auswahl

Für WI-0004 wird Python 3.12 mit ausschließlich der Standardbibliothek
verwendet. Produktcode liegt unter `src/sammlungslotse/`; ein dünner lokaler
Starter unter `tools/` stellt die CLI-Abnahme bereit. Es gibt keine
Installation, keinen Hintergrunddienst, keinen Container, keine Datenbank,
keinen Cache und keine Netzwerkbibliothek.

Diese Auswahl ist eine reversible Prototypentscheidung und keine allgemeine
Produktarchitektur. Der Anwendungsvertrag enthält keine Python- oder
CLI-spezifischen Fachfelder. Ein späterer Runtime- oder Oberflächenwechsel
darf den Kernvertrag ersetzen, ohne GATE-0001 auszuweiten.

## Sichtbare Oberfläche

Die einzige sichtbare Oberfläche dieser Wave ist eine lokale CLI:

```text
python tools/run_ebook_intake.py <synthetische-datei>
python tools/run_ebook_intake.py --json <synthetische-datei>
```

Die Standardansicht ist deutsch und zeigt Formatfähigkeit, Folgeaktion,
Snapshot-Evidenz sowie Beobachtungs- und Befundcodes. `--json` gibt den
kanonisch sortierten Anwendungsvertrag aus. Beide Wege schreiben keine
Berichtsdatei. Browser, REST und Agent-Zugang sind nicht Bestandteil des
Nutzwerts und werden nicht vorentschieden.

## Akzeptanzkriterien

WI-0004 ist erst `done`, wenn alle folgenden Punkte tatsächlich belegt sind:

1. Der Arbeitsgegenstand ist vor Produktcode kanonisch auf `origin/main` als
   `accepted` registriert.
2. Produktcode verwendet nur die Python-Standardbibliothek und enthält keine
   Netzwerk-, Persistenz-, Subprozess-, Extraktions- oder Schreibfähigkeit.
3. Ein stabiler synthetischer EPUB-Eingang ergibt reproduzierbar
   `supported`, `continue_deep_read_only` und
   `deep_read_only_allowed=true`.
4. Unbekannte Signatur, PDF, defektes ZIP, Traversal, Expansion,
   Verschlüsselung sowie Script-/Remote-Hinweise führen zu den vorab
   festgelegten getrennten fail-closed Ergebnissen.
5. Ein während der Erfassung veränderter Eingang führt zu `defer`, ohne
   Formatfreigabe.
6. Originalhashes bleiben vor und nach jedem End-to-End-Lauf identisch;
   beobachtete Netzwerk-, Original-, Fachsystem- und Dateischreibwirkungen
   sind null.
7. Zwei Läufe über denselben stabilen Eingang erzeugen byteidentische
   JSON-Ausgabe.
8. Berichte und Fehlermeldungen enthalten keinen absoluten oder relativen
   lokalen Pfad und keinen privaten Datei- oder Archiveintragsnamen.
9. Ressourcen- und Ergebnisgrenzen werden durch positive und negative Tests
   nachgewiesen.
10. Tatsächliche CLI-Prozesse belegen sichtbar mindestens `continue`,
    `review`, `stop` und `abstain`; `defer` wird über den injizierbaren
    Snapshot-Vertrag deterministisch geprüft.
11. Repository-, Registry-, bestehende Fixture-/Experiment- und vollständige
    Produkttests sind erfolgreich; `compileall` und `git diff --check` sind
    sauber.

## Verbotene Wirkungen und Nichtziele

Nicht Bestandteil und nicht autorisiert sind:

- Calibre oder ein anderes Fachsystem;
- tiefe EPUB-, Accessibility-, Rendering-, Reader- oder PDF-Prüfung;
- Dubletten-, Werk-, Ausgaben-, Metadaten- oder Routingentscheidungen;
- Extraktion, Derivat, Quarantäne, Verschieben, Umbenennen oder Import;
- Persistenz, Suche, Index, Queue, Hintergrundlauf oder Batchverarbeitung;
- Browser, REST, Agent, Plugin, KI, Modell oder externer Provider;
- Netzwerkzugriff, Telemetrie oder Übertragung lokaler Evidenz;
- Ausführung eines eingebetteten Inhalts oder eines tiefen Werkzeugs;
- reale oder private Dateien als Repository-, Test- oder PR-Evidenz;
- Übernahme von FolioTone-Code.

## Planannahme

Die Planung ist am 2026-08-27 angenommen, weil sie den von GATE-0001
ausgewählten Nutzwert vollständig abschließt, die kritischste Fehlwirkung
fail-closed behandelt und alle späteren Kopplungsäste außerhalb hält. Die
Standardbibliothek, In-Memory-Verarbeitung und CLI lassen sich ohne Migration
einer Datenbank, eines Dienstes oder eines öffentlichen API-Vertrags wieder
verwerfen.

Die Implementierung darf erst von dem Commit beginnen, auf dem diese
Annahme und die Registrierung von WI-0004 in `origin/main` kanonisch sind.

## Abschluss und Fortsetzung

Nach Implementierung und vollständiger Abnahme wird WI-0004 in einer
getrennten Wave auf `done` gesetzt. Danach wird nicht automatisch ein
Erweiterungsast begonnen. Die nächste Entscheidung vergleicht auf Basis des
tatsächlichen Nutzwerts mindestens: Stabilität und UX des Kerns vertiefen,
einen austauschbaren tiefen read-only Werkzeugadapter planen oder die
E-Book-Schiene zugunsten einer anderen Medienlinie pausieren.
