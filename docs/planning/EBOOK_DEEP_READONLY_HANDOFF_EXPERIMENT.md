# EXP-0007: Unveränderlicher Snapshot-zu-Werkzeug-Übergang

Status: ACCEPTED — NUR EXPERIMENTAUSFÜHRUNG AUTORISIERT

Stand: 2026-08-27

Artifacts: EXP-0007, GATE-0003

## Zweck

EXP-0007 prüft, ob und wie exakt die von WI-0004 freigegebenen
Snapshot-Bytes an einen tiefen read-only Werkzeugprozess übergeben werden
können, ohne Original, Fachsystembestand oder Produktarchitektur zu
verändern.

Das Experiment erzeugt Entscheidungsevidenz für GATE-0003. Es implementiert
keinen Produktadapter und trifft keine Werkzeug-, Runtime- oder
Deploymententscheidung.

## Hypothese und Gegenhypothese

Hypothese: Mindestens eine providerneutrale Übergabeform bindet den
Werkzeugeingang reproduzierbar an SHA-256 und Größe des unveränderlichen
WI-0004-Snapshots, hält Original-, Netzwerk-, Prozess-, Ressourcen-, Pfad-,
Output- und Cleanup-Grenzen ein und bleibt außerhalb des Anwendungskerns.

Gegenhypothese: Jede praktisch nutzbare Übergabeform benötigt eine
unzulässige Originalpfadkopplung, unkontrollierte temporäre Schreibwirkung,
unzureichenden Prozessabschluss oder providerbezogene Kernfelder. Dann wird
kein Produktadapter vorgeschlagen.

## Untersuchungsobjekt

Der kanonische Experimentinput ist nicht der ursprüngliche Locator, sondern:

- der unveränderliche Byte-Snapshot;
- seine SHA-256;
- seine Größe;
- die bereits belegte WI-0004-Freigabe
  `deep_read_only_allowed=true`;
- eine experimentinterne, nicht öffentliche Korrelationskennung ohne
  Dateiname oder lokalen Pfad.

Nur synthetische TEST-0001-Fälle werden verwendet. Mindestens der stabile
Minimalfall und der valide EPUB-3.3-Fall bilden positive Kontrollen. Ein
instabiler, nicht freigegebener oder hashabweichender Eingang muss vor jedem
Werkzeugstart fail-closed enden.

## Zu vergleichende Übergabeformen

### V1 — Byte-Stream

Der Snapshot wird ohne Dateimaterialisierung über einen begrenzten Stream an
einen deterministischen synthetischen Prozess übergeben.

Zu prüfen sind:

- vollständige Byte- und Hashgleichheit am Prozessrand;
- Backpressure, vorzeitiger Abbruch und unvollständiger Stream;
- Eingangs-, stdout-, stderr- und Zeitgrenzen;
- Kindprozess- und Handle-Cleanup;
- Eignung nur für Provider, die einen Stream tatsächlich unterstützen.

V1 belegt keine Kompatibilität eines dateipfadbasierten Werkzeugs.

### V2 — task-private Materialisierung

Der Snapshot wird in einen neu erzeugten, ausschließlich für einen Lauf
bestimmten temporären Bereich materialisiert. Lokal liegt dieser Bereich
unter `C:\rep\tmp\SammlungsLotse\exp-0007`; Container verwenden ein
größenbegrenztes `tmpfs`. Ein zufälliger technischer Name ersetzt den
ursprünglichen Dateinamen.

Zu prüfen sind:

- Schreiben ausschließlich der erwarteten Snapshot-Bytes;
- SHA-256-Prüfung vor und nach der Providerübergabe;
- keine Vererbung des ursprünglichen Pfads oder Dateinamens;
- restriktive Berechtigungen und kein gemeinsam genutzter Cache;
- Cleanup nach Erfolg, Werkzeugfehler, Timeout und Unterbrechung;
- erkennbare, begrenzt behandelbare Reste nach simuliertem Prozessabsturz;
- read-only Übergabe der materialisierten Datei an den Werkzeugprozess.

Die Materialisierung ist eine abgeleitete temporäre Arbeitskopie und niemals
ein Sammlungsobjekt, Importkandidat oder dauerhafter Bericht.

### V3 — Original-Locator erneut öffnen

Der Adapter erhält den ausdrücklich gewählten synthetischen Locator, öffnet
ihn nur read-only und prüft Identität, Größe, Änderungszeit und SHA-256 gegen
den WI-0004-Snapshot unmittelbar vor und nach der Werkzeugausführung.

Zu prüfen sind:

- Erkennung eines Austauschs oder einer Änderung zwischen Preflight und
  Werkzeugstart;
- Offenlegung von Pfad und Dateiname an Prozess, Log oder Bericht;
- Dateisperren und Portabilität;
- Originalunverändertheit;
- Verhalten bei Rename, Delete und gleichzeitigem Schreiben.

Ein erfolgreicher Happy Path genügt V3 nicht. Nicht zuverlässig schließbare
TOCTOU- oder Pfadleck-Risiken führen zur Ablehnung dieser Variante.

## Ausführungsprofile

### Windows-natives Semantikprofil

Ein ausschließlich auf Python 3.12 Standardbibliothek beruhender
synthetischer Probeprozess vergleicht V1 bis V3. Das Profil belegt
Byteübergabe, Zustandsprüfung, Abbruch, Outputgrenzen und Cleanup auf dem
lokalen Host. Da dieses Profil keine Betriebssystem-Netzwerkisolation
behauptet, enthält der Probeprozess keine Netzwerkfähigkeit; statische Tests
prüfen diese Grenze.

### Linux-Isolationsprofil

Ein synthetischer Probeprozess läuft unter Podman/Linux amd64 mit:

- `network=none`;
- read-only Root;
- unprivilegierter numerischer UID;
- vollständig entzogenen Capabilities;
- `no-new-privileges`;
- begrenzten PIDs, CPU, Speicher, Zeit, temporärem Speicher und Output;
- leerer beziehungsweise explizit erlaubter Umgebung;
- deaktiviertem Container-Logtreiber;
- read-only Eingabe nach Abschluss der jeweiligen Übergabevorbereitung.

Die genauen Werte werden vor dem ersten Messlauf in
`execution-profile.json` festgeschrieben und danach nicht aus erfolgreichen
Ergebnissen zurückgerechnet.

Windows- und Linux-Profil belegen unterschiedliche Eigenschaften. Ein grüner
Windows-Lauf wird nicht als Beleg für Containerisolation dargestellt; ein
grüner Linux-Lauf ersetzt keine Windows-Semantikprüfung.

## Optionale Werkzeugkompatibilität

Erst nachdem der synthetische Vergleich vollständig ist, darf die am besten
begrenzte noch geeignete Dateivariante gegen das bereits in EXP-0005
provenienzgebundene EPUBCheck-5.3.0-Profil wiederholt werden. Dabei gelten:

- keine Netzwerkverbindung im Messlauf;
- keine stillschweigende neue Version oder Abhängigkeit;
- keine automatische Provisionierung innerhalb der Messung;
- fehlende lokale, hashgeprüfte Voraussetzungen ergeben `not executed`,
  nicht Erfolg;
- EPUBCheck bleibt ein Kompatibilitätskandidat und erscheint nicht im
  providerneutralen Kernvertrag.

Ace ist wegen der in EXP-0003 dokumentierten offenen Produktqualifikations-
und Abhängigkeitsrisiken nicht Teil von EXP-0007.

## Messvertrag

Jede Kombination aus Profil, Übergabeform, Fall und Wiederholung hält fest:

- Snapshot-SHA-256 und -Größe;
- tatsächlich am Prozessrand empfangene SHA-256 und Größe;
- Freigabezustand vor dem Start;
- Start-, Exit-, Timeout- und Abbruchzustand;
- stdout-, stderr- und retained-output-Größe;
- Prozess- und Kindprozessabschluss;
- angelegte temporäre Objekte, Maximalgröße und Cleanup-Ergebnis;
- Original-SHA-256 vor und nach dem Lauf;
- beobachtete Pfad-, Dateinamen- oder Inhaltslecks im Ergebnis;
- Netzwerk- und Sicherheitsprofil soweit technisch erzwungen;
- semantischen Digest des pfadbereinigten Ergebnisses;
- Einschränkungen und nicht belegte Eigenschaften.

## Akzeptanzkriterien

EXP-0007 ist erst `done`, wenn:

1. GATE-0002 und der angenommene EXP-0007-Vertrag vor Implementierung des
   Experiments kanonisch auf `origin/main` stehen.
2. Experimentcode ausschließlich unter `experiments/ebook/exp-0007/`,
   `tools/experiments/` und zugehörigen Tests liegt; Produktcode bleibt
   unverändert.
3. Alle drei Übergabeformen auf demselben versionierten synthetischen
   Snapshot und gegen dieselben Sollwerte geprüft werden.
4. Nicht freigegebene, instabile oder hashabweichende Eingänge keinen
   Werkzeugprozess starten.
5. Der Prozessrand für jeden gestarteten positiven Lauf exakt Snapshot-Hash
   und -Größe bestätigt.
6. Zwei Wiederholungen je positiver Kombination denselben semantischen
   Ergebnisdigest erzeugen.
7. Originalhashes vor und nach allen Läufen identisch bleiben.
8. Ergebnis und Diagnose keinen ursprünglichen lokalen Pfad, ursprünglichen
   Dateinamen, privaten Inhalt oder unminimierten Prozessbefehl enthalten.
9. Zeit-, Input-, stdout-, stderr- und retained-output-Grenzen durch
   Positiv- und Negativkontrollen wirksam belegt sind.
10. Timeout und Unterbrechung keine laufenden Kindprozesse hinterlassen.
11. V2 nur im aufgabeneigenen temporären Bereich schreibt und Cleanup für
    Erfolg, Fehler, Timeout und Unterbrechung belegt; simulierte Crashreste
    bleiben sichtbar und begrenzt behandelbar.
12. V3 mindestens Austausch, Rename und gleichzeitige Änderung fail-closed
    behandelt; nicht schließbare TOCTOU- oder Pfadleckrisiken werden als
    Ablehnungsgrund erhalten.
13. Das Linux-Profil die festgeschriebenen Netzwerk-, Benutzer-, Capability-,
    Root-, Prozess-, CPU-, Speicher-, Zeit-, Umgebungs- und Outputgrenzen
    tatsächlich zurückliest und erfüllt.
14. Windows- und Linux-Evidenz getrennt bleibt und fehlende Ausführung nicht
    als Plattformäquivalenz dargestellt wird.
15. Ein Vergleichsdokument jede Variante als `QUALIFIED`, `REJECTED`,
    `INCONCLUSIVE` oder `NOT_EXECUTED` mit schwerstem Restfehler einstuft.
16. Repository-, Registry-, Fixture-, bestehende Experiment- und
    vollständige Unit-Tests, `compileall` sowie `git diff --check`
    erfolgreich sind.

## Ergebnisartefakte der späteren Ausführungs-Wave

Die Ausführungs-Wave soll mindestens erzeugen:

```text
experiments/ebook/exp-0007/
  README.md
  execution-profile.json
  probe.py
  result.json
tools/experiments/run_exp_0007.py
tests/experiments/test_exp_0007.py
```

Vollständige kurzlebige Laufdaten bleiben außerhalb von Git unter
`C:\rep\artifacts\SammlungsLotse\exp-0007`. Nur minimierte synthetische
Verträge, Hashes, Messwerte und Schlussfolgerungen werden versioniert.

## GATE-0003

GATE-0003 bleibt `proposed`, bis EXP-0007 vollständig ausgeführt und
validiert ist. Die Gate-Auswertung darf einen Produktarbeitsgegenstand nur
vorschlagen, wenn mindestens eine Übergabeform `QUALIFIED` ist und:

- Providerkopplung außerhalb des Kerns bleibt;
- Snapshot-Bindung und fail-closed Vorbedingungen vollständig belegt sind;
- temporäre Schreibwirkung, Pfadweitergabe und Cleanup ausdrücklich in der
  gewählten Grenze liegen;
- das Ergebnis einen providerneutralen Evidenzvertrag zulässt;
- keine Aussage zur Gesamtqualität oder Accessibility aus einem einzelnen
  Werkzeug abgeleitet wird.

Andernfalls verlangt GATE-0003 eine eng benannte Härtung, weitere Evidenz
oder das Pausieren der E-Book-Linie.

## Nichtziele

EXP-0007 umfasst nicht:

- Produktcode oder öffentliche Verträge;
- einen allgemeinen Prozess-, Container- oder Plugin-Unterbau;
- Auswahl eines endgültigen Werkzeugs oder Technologie-Stacks;
- Download, Versionsrecherche oder Lizenzneubewertung externer Werkzeuge;
- Accessibility-, Rendering-, Reader-, Metadaten- oder Inhaltsqualität;
- Calibre, Bestand, Dubletten, Werk, Ausgabe oder Routing;
- reale oder private Medien;
- Persistenz, Cache, Queue, Browser, REST, Agent oder Hintergrundlauf;
- Transformation, Import oder einen anderen Writer.
