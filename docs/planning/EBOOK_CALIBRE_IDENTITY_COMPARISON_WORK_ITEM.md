# WI-0011: Explizites EPUB gegen einen Calibre-Datensatz read-only vergleichen

Status: DONE — SYNTHETISCH QUALIFIZIERT

Stand: 2026-08-28

Artifact: WI-0011

## Ziel und kleinster Nutzwert

Ein Nutzer gibt genau ein lokales Eingangs-EPUB, genau eine lokale
Calibre-Bibliothek und genau eine positive externe Calibre-ID ausdrücklich
an. SammlungsLotse liefert einen pfadfreien, erklärbaren
Identitätskandidatenbericht zwischen dem unveränderlichen Eingangs-Snapshot
und dem über Calibres unterstützte CLI bytegleich bereitgestellten
Record-EPUB.

Der Bericht unterstützt ausschließlich die manuelle Prüfung vor einer
möglichen Integration. Er bestätigt keine Dublette und löst keine
Bestandsaktion aus.

## Eingangs- und Auswahlvertrag

- genau eine lokale reguläre, symlink- und reparsefreie Datei mit Suffix
  `.epub`;
- genau ein ausdrücklich angegebenes lokales Calibre-Bibliotheksverzeichnis;
- genau eine dezimale externe Calibre-ID im Bereich `1` bis `999999999`;
- keine Listen, Kommaselektion, Globs, Verzeichnissuche, automatische
  Calibre-Erkennung, implizite Standardbibliothek oder Remote-URL;
- höchstens 4 MiB je EPUB und höchstens 8 MiB für beide unveränderlichen
  Snapshots zusammen;
- die bestehenden ZIP-, Eintrags-, Expansions-, Pfad-, Duplikat-,
  Verschlüsselungs- und Preflight-Grenzen aus WI-0009 bleiben wirksam.

Die 4-MiB-Grenze ist eine absichtliche enge erste Produktgrenze aus dem
qualifizierten EXP-0008-Profil. Größere EPUBs enden vor einer
Identitätsbewertung als `not_assessed`; eine spätere Erweiterung benötigt
eigene Evidenz und ändert nicht stillschweigend diesen Vertrag.

## Providerneutraler Handoff-Vertrag

Die Anwendung kennt einen Port für genau einen externen Record-Snapshot. Das
Ergebnis des Ports enthält ausschließlich:

- die angeforderte externe Record-ID;
- Profilidentität und Quell-Snapshot-Digest als technische Provenienz;
- `completed`, `not_assessed` oder `cleanup_failed`;
- bei `completed` einen unveränderlichen EPUB-Snapshot aus Bytes, Größe,
  SHA-256 und Suffix `.epub`;
- pfadfreie Reason- und Beobachtungscodes;
- explizite Wirkungswerte für Source-Unverändertheit, Task- und
  Container-Cleanup, Netzwerk und Writes.

Calibre-Befehl, Hostlocator, Dateiname, Arbeitskopie, Exportverzeichnis,
Container, Roh-stdout, Roh-stderr und interne Calibre-Werte enden am Adapter.
Der Port darf weder `metadata.db` direkt öffnen noch ein Calibre-Schema an den
Kern weiterreichen.

## Calibre-Adapter- und Laufzeitgrenze

Der erste Adapter verwendet ausschließlich das unveränderte exakte
Calibre-9.13.0-Image aus WI-0007 und den in EXP-0008 belegten Ablauf:

1. Quellbibliothek vollständig gegen die bestehenden Copy-on-read-Grenzen
   inventarisieren und hashen;
2. eine neue zufällige task-private Arbeitskopie erzeugen und gegen den
   Quell-Snapshot prüfen;
3. das exakte Image mit `network=none`, read-only Root, UID/GID
   `65532:65532`, Capability-Entzug, `no-new-privileges`, PID-, CPU-, RAM-,
   Swap-, tmpfs-, Zeit-, stdout-, stderr- und 4-MiB-Dateigrenze starten;
4. ausschließlich `calibredb export` mit genau einer ID,
   `--formats EPUB`, `--dont-update-metadata`, `--dont-write-opf`,
   `--dont-save-cover`, `--dont-save-extra-files`, `--single-dir` und einer
   ID-basierten Vorlage ausführen;
5. genau eine reguläre `<id>.epub`-Datei begrenzt und stabil in einen
   unveränderlichen In-Memory-Snapshot lesen;
6. Quellbibliothek erneut prüfen und Task sowie Container vor Rückgabe des
   Snapshots vollständig entfernen.

Fehlende ID, Datensatz ohne EPUB, mehrere oder ungültige IDs, unerwartete
Datei, Größenüberschreitung, Werkzeugfehler, Timeout, Unterbrechung,
Quelländerung und unvollständiges Cleanup führen fail-closed zu keinem
teilweisen Identitätsbericht.

## Identitäts- und Ergebnisvertrag

Der Eingangs-Snapshot erhält Rolle `ingress_epub`, der Record-Snapshot Rolle
`calibre_record_epub`. Danach verwendet die Anwendung unverändert die fünf
WI-0009-Ebenen:

1. `byte`;
2. `package`;
3. `representation`;
4. `edition`;
5. `work`.

Positive, negative und fehlende Evidenz, Enthaltung und Reason-Codes bleiben
getrennt. Der neue äußere Bericht verwendet Schema
`sammlungslotse/ebook-calibre-identity-candidate-report/v1` und enthält:

- `assessment` und pfadfreie Handoff-Reason-Codes;
- die explizite externe Calibre-ID;
- die feste Rollenabbildung für Position `1` und `2`;
- bei Erfolg den vollständigen unveränderten WI-0009-Identitätsbericht;
- Profil- und Snapshot-Provenienz ohne Locators;
- Wirkungs- und Cleanup-Zustände.

Der verschachtelte Identitätsbericht behält sein bestehendes Schema und seine
Semantik. Er wird nicht um Calibre-Felder erweitert. Zwei Läufe über dieselben
stabilen synthetischen Eingänge müssen byteidentisches JSON erzeugen.

## CLI-Vertrag

Die getrennte lokale Oberfläche lautet:

```text
python tools/run_ebook_calibre_identity.py --temp-root TEMP EINGANG.epub CALIBRE_BIBLIOTHEK ID
python tools/run_ebook_calibre_identity.py --json --temp-root TEMP EINGANG.epub CALIBRE_BIBLIOTHEK ID
```

Die deutsche Ansicht und JSON erscheinen ausschließlich auf stdout. Eingabe-
und Bibliothekspfade sowie Dateinamen erscheinen weder im Ergebnis noch in
Diagnosen. Der Temp-Root ist explizit und muss innerhalb des kontrollierten
Projekt-Tempbereichs liegen.

Prozesscodes:

- `0` für einen vollständig erzeugten Kandidatenbericht, auch bei Enthaltung;
- `2` für ungültige oder mehrfache Eingabeparameter vor jedem Containerstart;
- `4` für `not_assessed`, etwa fehlende ID, fehlendes EPUB, geschlossenes
  Preflight-Gate, fehlendes exaktes Profil oder kontrollierten Providerfehler;
- `3` für Grenz-, Sicherheits-, Struktur-, Output- oder Cleanupfehler;
- `130` für ausdrückliche Unterbrechung nach vollständigem Cleanup.

## Produktqualifikation

Die getrennte Implementierungs-Wave bindet das vollständige Produktpreimage
und verwendet ausschließlich TEST-0001 `0.3.0`. Mindestens folgende
tatsächlichen Fälle sind zweimal über den JSON-CLI-Prozess und einmal über
die deutsche Ansicht auszuführen:

- bytegleiches Eingangs- und Calibre-EPUB;
- neuverpackte beziehungsweise unterschiedliche Repräsentation;
- fachlich negativer Kandidat ohne falsche Gleichheitsfreigabe;
- fehlende ID und Datensatz ohne EPUB;
- ungültige und mehrere IDs vor Containerstart;
- Outputlimit, Timeout, simulierte Unterbrechung und Recovery;
- unveränderte Eingangsdatei, Quellbibliothek und Fixture-Hashes;
- vollständiges Task- und Container-Cleanup.

## Akzeptanzkriterien

WI-0011 ist erst `done`, wenn:

1. genau eine explizite Eingangsdatei, Bibliothek und positive externe ID
   akzeptiert werden;
2. Mehrfach-, Null-, negative, übergroße und nichtnumerische IDs vor
   Containerstart abgelehnt werden;
3. Eingangs- und Calibre-EPUB als getrennte unveränderliche Snapshots unter
   4 MiB erfasst werden;
4. die vorhandene WI-0009-Preflight- und Strukturgrenze beide Snapshots
   positiv gattet;
5. der Calibre-Handoff ausschließlich über den providerneutralen Port und die
   unterstützte CLI erfolgt;
6. das exakte WI-0007-Image und seine Isolation vollständig gebunden und
   zurückgelesen werden;
7. genau eine reguläre EPUB-Datei ohne OPF, Cover, Extras oder anderes Format
   exportiert wird;
8. der exportierte Snapshot bytegleich zum ausgewählten Calibre-Format bleibt;
9. Quellbibliothek, Eingangsdatei und Fixtures unverändert bleiben;
10. Byte-, Paket-, Repräsentations-, Ausgabe- und Werkebene samt positiver,
    negativer und fehlender Evidenz unverändert erhalten bleiben;
11. Rollen, externe ID, Provenienz, Reason-Codes und Wirkungen pfadfrei und
    deterministisch ausgegeben werden;
12. fehlende ID, fehlendes EPUB, unerwartete Ausgabe, Grenzverletzung,
    Werkzeugfehler und Timeout keinen Teilbericht erzeugen;
13. Erfolg, Fehler, Abbruch und Recovery keine Container oder Taskdaten
    zurücklassen;
14. Produktcode keine Netzwerk-, Datenbank-, Persistenz- oder Writerfähigkeit
    erhält;
15. zwei tatsächliche JSON-Wiederholungen byteidentisch sind und die deutsche
    Ansicht denselben fachlichen Zustand wiedergibt;
16. False Positives in den gebundenen negativen Fällen null sind;
17. Registry-, Dokument-, TEST-0001-, EXP-0002-bis-EXP-0008-, WI-0005-,
    WI-0008-, WI-0009-, Produkt-, `compileall`, `git diff --check`- und
    Foundation-Regression erfolgreich sind;
18. Projektstatus, Übergabe, Validierungs- und Bedienungsdokumentation den
    tatsächlichen engen Stand und alle Restgrenzen wiedergeben.

## Nichtziele

Nicht Bestandteil sind automatische Suche im Calibre-Bestand, mehrere IDs,
Dateien oder Bibliotheken, PDF/MOBI/AZW3, andere Calibre-Versionen, Content
Server, direkte Datenbanknutzung, Custom Columns, Tags, Cover, neue
Metadatenfelder, persistente Kandidaten, Index, Routing, Browser, REST,
Agents, statistische oder KI-Ähnlichkeit, bestätigte Dublette, Import,
Formatentfernung, Metadatenschreiben, Verschieben, Umbenennen, Löschen oder
jede andere Bestandswirkung.

## Ausführungsergebnis

WI-0011 wurde auf dem eingefrorenen Produktpreimage
`d70c6decb50f4560e52f64b4eef66fc8f4e76af2` ausschließlich mit
synthetischem TEST-0001-Material ausgeführt. Der eingecheckte Nachweis unter
`runtime/ebook-calibre-identity/qualification.json` bestand 23/23 Kriterien.

Der positive Calibre-Record-Snapshot blieb mit SHA-256
`1d98510717f6c3f22b3219bdedf8cbdf38785f060bfca0522f66ccf374f684a5`
bytegleich zum ausdrücklich ausgewählten EPUB. Zwei vollständige JSON-Läufe
waren byteidentisch. Eine neu gepackte Repräsentation wurde als
`representation_candidate`, der gebundene fachliche Negativfall ohne falsche
Gleichheitsfreigabe als `abstain` bewertet.

Fehlende und formatlose Datensätze, ungültige und mehrere IDs,
Eingangsgrößenüberschreitung, unerwartete Ausgabe, Outputlimit, Timeout,
simulierte Unterbrechung und Recovery endeten fail-closed. Eingangsdatei,
Quellbibliothek und Fixtures blieben unverändert. Nach allen tatsächlichen
CLI- und Podman-Läufen verblieben weder Taskdaten noch Container. 22
stdout-/stderr-Rohbelege liegen ausschließlich außerhalb von Git unter dem
kontrollierten Projekt-Artefaktpfad.

## Ausführungsreihenfolge

1. GATE-0007 und der angenommene Vertrag wurden getrennt nach `origin/main`
   integriert.
2. Providerneutraler Handoff-Port, Calibre-Adapter,
   Anwendungskomposition, getrennte CLI und automatisierte Verträge wurden
   in einer eigenen Wave umgesetzt.
3. Das vollständige Produktpreimage wurde vor der tatsächlichen
   synthetischen CLI-/Podman-Qualifikation commitgebunden.
4. Die lokale Qualifikation, vollständige Regression, beide erforderlichen
   GitHub-Checks, der reguläre Merge über PR #40 und die Post-Merge-Prüfung
   auf `origin/main` sind erfolgreich.

Die Benutzeranweisung vom 2026-08-28 autorisiert die autonome Fortsetzung
über diese Planung, die ausschließlich synthetische Implementierung und
Abnahme, Pull Request, exakte CI-Prüfung und Merge nach `origin/main`.
