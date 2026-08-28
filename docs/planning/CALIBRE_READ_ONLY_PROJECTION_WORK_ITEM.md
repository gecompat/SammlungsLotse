# WI-0007: Read-only Calibre-Bestandsprojektion umsetzen

Status: DONE — IMPLEMENTIERT UND SYNTHETISCH QUALIFIZIERT

Stand: 2026-08-28

Artifact: WI-0007

## Entscheidung

WI-0007 wird als nächste eng begrenzte Produktwave angenommen. Ein Nutzer
gibt genau eine lokale Calibre-Bibliothek ausdrücklich an und erhält eine
pfadfreie Bestandsprojektion auf stdout. Calibre bleibt das führende
E-Book-Fachsystem; SammlungsLotse liest ausschließlich über die dokumentierte
`calibredb`-CLI und übernimmt weder Calibres Datenmodell noch Schreibhoheit.

Die Originalbibliothek wird vor und nach dem Lauf vollständig geprüft, aber
niemals an Calibre oder den Container übergeben. Für jeden Lauf entsteht eine
neue task-private, begrenzte und nach dem Lauf verworfene Copy-on-read-
Arbeitskopie. Nur diese Kopie ist für Calibre beschreibbar. Der Produktvertrag
kennt keinen Hostpfad und keine internen Calibre-Tabellen.

## Begründung und Primärquellen

EXP-0002 hat Calibre `9.13.0` mit dreizehn erfolgreichen synthetischen
Kriterien untersucht. Der direkte read-only Mount ist nicht funktionsfähig,
weil Calibre beim lokalen Öffnen einen Dateisystemtest schreibt. Die
wegwerfbare Copy-on-read-Variante hielt beide Quellbibliotheken bytegleich
und projizierte unterstützte Felder reproduzierbar.

Die aktuelle Prüfung am 2026-08-28 bestätigt weiterhin Calibre `9.13.0` als
aktuelles Release. Das offizielle Linux-Artefakt besitzt 192554776 Bytes und
den veröffentlichten SHA-512-Wert
`c018cb47805040a9a83dc16986db618c539a7dc62f85da2760b7e22e0e8ada7533a01be797cdbd04a5d5f66c8efa2b0ac2db4819700e561351267cb4842a3fc6`.
Calibre steht unter GPL-3.0-only.

`calibredb list` ist die dokumentierte Bestandsabfrage. `--with-library`
wählt die lokale Bibliothek, `--fields` begrenzt die Ausgabe und
`--for-machine` liefert JSON. Remote-URLs und Content Server bleiben trotz
Unterstützung durch die CLI ausdrücklich außerhalb dieser Wave. Der
Standardwert von `--prefix` kann absolute Bibliothekspfade enthalten; deshalb
werden Formatwerte ausschließlich im Provideradapter zu normalisierten
Dateiendungen reduziert.

Primärquellen:

- [Calibre Linux-Download](https://calibre-ebook.com/download_linux);
- [Calibre 9.13.0](https://download.calibre-ebook.com/9.13.0/);
- [offizielle Calibre-Signaturen](https://calibre-ebook.com/signatures/);
- [calibredb-Handbuch](https://manual.calibre-ebook.com/generated/en/calibredb.html);
- [Calibre-Lizenz 9.13.0](https://github.com/kovidgoyal/calibre/blob/v9.13.0/LICENSE).

## Kleinster Nutzwert

Für genau eine ausdrücklich benannte Bibliothek liefert SammlungsLotse:

- die externe numerische Calibre-ID;
- den Titel;
- die Autoren als geordnete Liste;
- die Sprachen als geordnete Liste;
- vorhandene Formate als sortierte, normalisierte Erweiterungen.

Nicht angeforderte Calibre-Felder, Custom Columns, Tags, Identifikatoren,
Kommentare, Cover, Zeitstempel, interne UUIDs, Verzeichnisse und Dateinamen
werden nicht ausgegeben. Fehlende Werte bleiben als leere Listen oder leere
Zeichenfolge sichtbar und werden nicht erfunden.

## Anwendungs- und CLI-Vertrag

Die Implementierungs-Wave führt eine getrennte lokale Oberfläche ein:

```text
python tools/run_calibre_inventory.py CALIBRE_BIBLIOTHEK
python tools/run_calibre_inventory.py --json CALIBRE_BIBLIOTHEK
```

Die Bibliothek ist ein einzelnes erforderliches Verzeichnisargument. Globs,
Listen, Verzeichnisentdeckung, Calibre-Konfigurationssuche und implizite
Standardbibliotheken sind nicht erlaubt. URL-Schemata werden abgelehnt.

Die deutsche Ansicht zeigt nur die Projektion und eine pfadfreie technische
Einordnung. JSON verwendet die stabile Schema-ID
`sammlungslotse/calibre-read-only-projection/v1`, sortiert Datensätze nach
externer Calibre-ID und serialisiert Schlüssel stabil. Zwei Läufe über
denselben stabilen Snapshot und dasselbe Profil müssen byteidentisches JSON
erzeugen. Beide Ansichten erscheinen ausschließlich auf stdout; es gibt
keine Berichtsdatei und keine Produktpersistenz.

Prozesscodes:

- `0` für eine vollständig erzeugte Projektion;
- `4` für `not_assessed`, insbesondere fehlendes oder nicht bereitgestelltes
  exaktes Profil, instabile Quelle, inkompatible Werkzeugausgabe oder
  kontrollierten Werkzeugfehler;
- `3` für verletzte Eingangs-, Sicherheits-, Ressourcen- oder
  Ausgabegrenzen und unerwartete interne Fehler;
- `130` für eine ausdrückliche Unterbrechung nach vollständigem Cleanup.

## Providerneutrale Architekturgrenze

Die Anwendung nimmt einen bereits erzeugten, unveränderlichen
Bibliotheks-Snapshotvertrag entgegen. Ein Port beschreibt nur Profilidentität,
Snapshot-Digest, Ausführungsstatus und die minimale Projektion. Der Calibre-
Adapter übersetzt dokumentierte CLI-Felder in diesen Vertrag. Befehl,
Calibre-Feldnamen, Arbeitskopie, Container und Rohantwort enden am Adapter.

Die CLI-Komposition darf einen lokalen Locator ausschließlich an den
Copy-on-read-Adapter reichen. Kern, Ergebnisobjekte, deutsche Ausgabe und
JSON erhalten weder den Locator noch Dateinamen aus der Bibliothek. Es gibt
keinen direkten Zugriff auf `metadata.db`, keine SQL-Abfrage und keinen
Content-Server-Zugang.

## Copy-on-read- und Laufzeitgrenze

Die erste Implementierung muss fail-closed:

1. den expliziten Quellordner ohne Symlink-, Reparse- oder Spezialdateien
   inventarisieren und gegen feste Datei-, Byte-, Tiefen- und Namensgrenzen
   prüfen;
2. Größe und SHA-256 jeder regulären Datei sowie einen kanonischen
   Snapshot-Digest erfassen;
3. in einen neuen task-privaten Bereich unter einem ausdrücklich
   konfigurierten Temp-Root kopieren;
4. Arbeitskopie und Quelle erneut gegen das gebundene Inventar prüfen;
5. ausschließlich die Arbeitskopie unter einem festen Containerpfad
   beschreibbar an das exakte Calibre-Profil übergeben;
6. `calibredb list --with-library /library --for-machine --fields
   title,authors,languages,formats --sort-by id --ascending` netzwerklos,
   unprivilegiert und ressourcenbegrenzt ausführen;
7. Roh-stdout größenbegrenzt einlesen, streng validieren und pfadfrei
   projizieren;
8. Quelle nach dem Providerlauf erneut prüfen und Task sowie Container bei
   Erfolg, Fehler, Timeout und Unterbrechung entfernen.

Quelländerung während eines Laufs führt zu `not_assessed`. Ein unvollständiges
Cleanup oder eine Grenzverletzung führt fail-closed zu Prozesscode `3`.
Crashreste dürfen nur anhand eines eigenen WI-0007-Markers und ausschließlich
unter dem konfigurierten Temp-Root bereinigt werden.

## Exaktes Produktprofil

Die Implementierungs-Wave darf ausschließlich Calibre `9.13.0` über ein
vorab bereitgestelltes, Linux/amd64-digestgebundenes Podman-Image verwenden.
Das Profil bindet mindestens Artefakt-URL, Größe, SHA-512, Lizenz, Basisimage,
Buildpreimage, resultierende Image-ID, Podman-Mindestversion, Plattform,
UID/GID, Umgebungs-Whitelist, read-only Root, Capability-Entzug,
`no-new-privileges`, `network=none`, PID-, CPU-, RAM-, Swap-, tmpfs-, Zeit-
und Outputgrenzen.

Bereitstellung ist ein eigener expliziter Vorgang. Ein Bestandslauf lädt
nichts herunter, baut kein Image und fällt bei fehlender oder abweichender
Image-ID auf `not_assessed`. Eine andere Calibre-Version oder ein geändertes
Profil verlangt neue aktuelle Quellenprüfung und synthetische Qualifikation.

## Datenschutz und Evidenz

Titel und Autoren sind private Sammlungsmetadaten. Die ausdrücklich
angeforderte lokale stdout-Ausgabe darf sie enthalten, wird aber weder
protokolliert noch versioniert. Diagnosen, Tests, Profilnachweise und Pull
Requests verwenden ausschließlich synthetische TEST-0001-Bibliotheken und
enthalten keine Hostpfade, Benutzernamen, Bibliotheksnamen oder realen
Bestände. Der begrenzte Rohbericht bleibt task-privat und wird nach der
Projektion entfernt; nur sein Hash und seine Größe dürfen als technische
Provenienz in die pfadfreie Ausgabe eingehen.

## Akzeptanzkriterien

WI-0007 ist erst `done`, wenn:

1. genau ein explizites lokales Bibliotheksverzeichnis akzeptiert und jede
   automatische oder entfernte Zielermittlung abgelehnt wird;
2. Quelle, Kopie und erneute Quellprüfung durch einen kanonischen
   Dateisnapshot gebunden sind;
3. Symlinks, Reparse Points, Spezialdateien, instabile Dateien und alle
   festen Größen- und Strukturgrenzen fail-closed geprüft sind;
4. nur die Arbeitskopie den Calibre-Prozess erreicht und die Quelle vor,
   während und nach dem Lauf unverändert bleibt;
5. ausschließlich die dokumentierte `calibredb`-CLI und keine interne
   Datenbank- oder Serverkopplung verwendet wird;
6. Ergebnisdatensätze nur externe Calibre-ID, Titel, Autoren, Sprachen und
   normalisierte Formate enthalten;
7. deutsche und JSON-Ausgabe keine Host- oder Bibliothekspfade, Dateinamen,
   nicht angeforderten Felder oder Rohdiagnosen enthalten;
8. stabile Wiederholung und Sortierung byteidentisches JSON erzeugen;
9. unbekannte, fehlende und typabweichende Werkzeugfelder sichtbar und
   fail-closed zu `not_assessed` führen;
10. das exakte Produktimage reproduzierbar aus allen gebundenen Eingängen
    gebaut und über seine Image-ID geprüft ist;
11. Netzwerk-, Benutzer-, Capability-, Prozess-, Zeit-, CPU-, RAM-, Swap-,
    tmpfs-, Umgebungs- und Outputgrenzen automatisiert und tatsächlich
    synthetisch geprüft sind;
12. Erfolg, Werkzeugfehler, Outputgrenze, Timeout, Abbruch und Crashrecovery
    keine Container oder Taskdaten zurücklassen;
13. reale private Bestände weder für Tests noch als Pull-Request-Evidenz
    verwendet werden;
14. Registry-, Dokument-, Fixture-, Experiment-, Produkt- und Foundation-
    Regression sowie `compileall` und `git diff --check` erfolgreich sind;
15. Projektstatus, Übergabe, Drittmaterial- und Bedienungsdokumentation den
    tatsächlichen Stand und die Grenzen wiedergeben.

## Nichtziele

Nicht Bestandteil von WI-0007 sind mehrere Bibliotheken pro Aufruf,
automatische Calibre-Erkennung, Content Server, Remote-URLs, Custom Columns,
Tags, Identifikatoren, Cover, Volltext, Suche, Persistenz, Browser, REST,
Agents, Kombination mit dem Dateieingangsbericht, Windows-native
Calibre-Ausführung sowie Import, Export, Metadatenschreiben, Reparatur,
Verschieben, Umbenennen oder Löschen.

## Implementierungsreihenfolge

1. Diesen Vertrag und WI-0007 als `accepted` auf `origin/main` registrieren.
2. Produktport, Copy-on-read-Adapter, Calibre-Provider, getrennte CLI und
   exaktes Laufzeitprofil in einer eigenen Implementierungs-Wave ergänzen.
3. Automatisierte Verträge, zwei vollständige reproduzierbare Image-Builds
   und tatsächliche synthetische CLI-/Podman-Abnahme ausführen.
4. Erst nach vollständiger lokaler Regression und exakten erforderlichen
   GitHub-Checks mergen und WI-0007 auf `done` setzen.

Die Benutzerfreigabe vom 2026-08-28 umfasst Planung, Registrierung,
Implementierung, ausschließlich synthetische Qualifikation, Pull Requests,
exakte CI-Prüfung und Merge nach `origin/main`.

## Implementierung und Abnahme

Die getrennte Implementierungs-Wave hat den angenommenen Vertrag umgesetzt:

- `sammlungslotse.calibre_inventory` trennt Modell, Anwendungsport,
  Copy-on-read-Workspace, Calibre-Provider und Podman-Executor;
- der Quellsnapshot inventarisiert nur reguläre Dateien und bindet relative
  Namen, Größen und SHA-256-Werte unter festen Datei-, Summen-, Tiefen- und
  Pfadgrenzen;
- nur die geprüfte task-private Kopie wird beschreibbar unter `/library`
  gemountet; die Quelle erreicht weder Container noch Calibre;
- der feste Wrapper ruft ausschließlich `calibredb list` mit der minimalen
  Feld-Whitelist auf;
- `tools/run_calibre_inventory.py` liefert eine deutsche Ansicht oder
  deterministisches JSON und akzeptiert genau eine explizite Bibliothek;
- Bereitstellung, tatsächliche Qualifikation und CI-Nachweis sind getrennte
  Werkzeuge; ein Nutzerlauf lädt und baut nichts.

Das offizielle 192554776-Byte-Artefakt wurde erneut gegen seinen SHA-512-Wert
geprüft. Zwei frische Builds aus dem digestgebundenen Linux/amd64-Basisimage
erzeugten dieselbe Image-ID
`sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5`.

Eine ausschließlich aus TEST-0001 erzeugte synthetische Calibre-Bibliothek
wurde tatsächlich über das Produktprofil projiziert. Deutsche Ausgabe und
zwei JSON-Läufe waren erfolgreich; die JSON-Läufe waren byteidentisch. Die
Projektion enthielt genau einen Datensatz mit ID, Titel, Autor, Sprache und
Format, aber keinen Host- oder Bibliothekspfad. Quellsnapshot und
Bibliotheksdateien blieben unverändert; Taskbereich und Profilcontainer waren
nach allen Läufen leer. Der eingecheckte Nachweis bindet 17/17 Kriterien an
Profil, Image-ID und vollständiges Produktpreimage.
