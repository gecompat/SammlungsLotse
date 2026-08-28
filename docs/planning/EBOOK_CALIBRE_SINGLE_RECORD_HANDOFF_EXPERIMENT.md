# EXP-0008: Unterstützte Calibre-Einzelrecord-EPUB-Übergabe qualifizieren

Status: DONE — SYNTHETISCH QUALIFIZIERT

Stand: 2026-08-28

Artifact: EXP-0008

## Erkenntnisziel

EXP-0008 beantwortet genau eine Frage: Kann das bereits gebundene lokale
Calibre-9.13.0-Profil für genau einen ausdrücklich gewählten externen
Datensatz ein vorhandenes EPUB über eine unterstützte CLI-Schnittstelle
bytegleich, begrenzt und task-privat bereitstellen, ohne den Quellbestand zu
verändern oder interne Calibre-Schemata zum Produktvertrag zu machen?

Das Experiment untersucht nur die Übergabenaht. Es implementiert noch keinen
Vergleich zwischen einem Eingangs-EPUB und einem Calibre-Datensatz.

## Hypothese

`calibredb export` kann auf einer wegwerfbaren Copy-on-read-Arbeitskopie mit
einer einzelnen externen ID, `--formats EPUB` und
`--dont-update-metadata` genau ein unverändertes EPUB in einen task-privaten
Ausgang schreiben. OPF, Cover, Extra-Dateien und alle anderen Formate können
für diese Übergabe ausgeschlossen werden.

Die Hypothese gilt als widerlegt, wenn Calibre mehr oder andere Dateien
ausgibt, EPUB-Bytes ändert, den Quell-Snapshot verändert, nicht eindeutig
zwischen fehlender ID und fehlendem EPUB unterscheidbar fail-closed endet oder
die Grenzen und das Cleanup nicht zuverlässig durchgesetzt werden können.

## Gebundene Grundlage

- ausschließlich TEST-0001 `0.3.0` und die synthetische WI-0008-
  Calibre-Materialisierung;
- das unveränderte Profil
  `wi-0007-calibre-9.13.0-podman-linux-amd64/v1`;
- die exakte lokale Image-ID
  `sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5`;
- eine ausdrücklich angegebene synthetische Quellbibliothek und genau eine
  externe numerische Calibre-ID;
- ausschließlich die unterstützten Befehle `calibredb add`,
  `calibredb add_format`, `calibredb list` und `calibredb export` für Aufbau,
  Oracle und Probe.

Der Experimentcode darf `metadata.db` weder direkt öffnen noch ihr Schema
auswerten. Calibre selbst darf seine eigene Datenbank innerhalb der
wegwerfbaren Arbeitskopie über seine unterstützte CLI verwenden.

## Versuchsablauf

1. Das aktuelle Profil, die Image-ID, das vollständige Experimentpreimage
   und alle verwendeten Fixture-Hashes werden vor dem Lauf gebunden.
2. Eine frische synthetische Bibliothek mit Datensatz `1` samt EPUB und PDF,
   Datensatz `2` ohne Format und Datensatz `3` mit EPUB wird ausschließlich
   über unterstützte Calibre-Befehle erzeugt.
3. Vor der Probe werden Quellbibliothek und Fixtures byteweise gesnapshottet.
4. Für jeden Fall entsteht eine zufällige, task-private Copy-on-read-
   Arbeitskopie mit getrenntem Exportverzeichnis.
5. Der positive Fall exportiert genau ID `1` und nur EPUB mit
   `--dont-update-metadata`, `--dont-write-opf`, `--dont-save-cover`,
   `--dont-save-extra-files`, `--single-dir` und einer ID-basierten Vorlage.
6. Ein Experimentadapter akzeptiert nur genau eine positive dezimale ID und
   prüft nach dem Prozess genau eine reguläre `.epub`-Datei, Größe und
   erwarteten Hash. Links, Reparse Points, weitere Dateien und unerwartete
   Namen führen fail-closed zum Abbruch.
7. Getrennte Negativfälle verwenden eine fehlende ID, ID `2` ohne EPUB,
   mehrere IDs, einen ungültigen Identifikator, eine zu kleine Outputgrenze,
   Timeout, simulierte Unterbrechung und Recovery eines eindeutig eigenen
   abgelaufenen Tasks.
8. Nach jedem Fall werden Container und Taskbereiche entfernt. Abschließend
   werden Quell- und Fixture-Snapshots erneut verglichen.

## Akzeptanzkriterien

EXP-0008 ist nur dann `done`, wenn ein reproduzierbarer eingecheckter Nachweis
mindestens bestätigt:

1. exakte Profil-, Image-, Plattform- und vollständige Preimage-Bindung;
2. ausschließlich synthetische gebundene Eingänge;
3. genau eine explizite externe ID und genau das Format EPUB;
4. Verwendung von `calibredb export` statt interner Datenbankkopplung;
5. exakt eine reguläre Ausgabedatei im positiven Fall;
6. Bytegleichheit des exportierten EPUB mit dem erwarteten Fixture;
7. keine OPF-, Cover-, Extra- oder weiteren Formatdateien;
8. unveränderte Quellbibliothek und Fixture-Eingänge;
9. task-private, zufällige und begrenzte Arbeits- und Exportbereiche;
10. zurückgelesene Netzwerk-, Benutzer-, Root-Dateisystem-, Capability-,
    Prozess-, CPU- und Speicherisolation des exakten Containers;
11. fail-closed-Ergebnisse für fehlende ID, fehlendes EPUB, mehrere oder
    ungültige IDs sowie unerwartete Ausgaben;
12. wirksame Input-, Output-, stdout-, stderr- und Zeitgrenzen;
13. vollständiges Container- und Task-Cleanup bei Erfolg, Fehler, Timeout,
    Unterbrechung und Recovery;
14. keine Pfade, Medienbytes oder Calibre-internen Werte im strukturierten
    Ergebnis;
15. zwei semantisch und bytegleich serialisierte positive Wiederholungen;
16. keine Produkt-, Bestands-, Netzwerk-, Persistenz- oder Writerwirkung.

## Ergebnisklassen

- `qualified`: alle Kriterien sind erfüllt; nur die technische
  Einzelrecord-Übergabe ist belegt.
- `not_qualified`: mindestens ein Sicherheits-, Bytegleichheits-,
  Eindeutigkeits- oder Cleanup-Kriterium scheitert; kein Produktpfad darf
  daraus entstehen.
- `inconclusive`: die Umgebung liefert keinen vertrauenswürdigen Befund; der
  Versuch wird nicht als bestanden dargestellt.

## Ausführungsergebnis

EXP-0008 wurde am 2026-08-28 mit dem exakten Calibre-9.13.0-Image unter
Python 3.12.10 und Podman 6.1.0 auf Linux/amd64 vollständig ausgeführt. Der
eingecheckte Nachweis bindet das Preimage
`fb08732b71b6e214aa039a9f3d428a3b12c379ac` und erfüllt 16/16 Kriterien.

Beide positiven Wiederholungen exportierten genau eine EPUB-Datei mit 1521
Bytes und dem erwarteten SHA-256
`1d98510717f6c3f22b3219bdedf8cbdf38785f060bfca0522f66ccf374f684a5`.
Die normalisierten Ergebnisse waren bytegleich. Fehlende ID, Datensatz ohne
EPUB, mehrere oder ungültige IDs, unerwartete Ausgabe, Outputgrenze, Timeout
und simulierte Unterbrechung endeten getrennt fail-closed. Recovery, Quell-
und Fixture-Unverändertheit, zurückgelesene Containerisolation sowie
vollständiges Task- und Container-Cleanup waren erfolgreich.

Ein erster nicht übernommener 15/16-Lauf deckte ausschließlich eine
labelabhängige Rohbeleg-Schlüsselung im Ergebnisrunner auf. Nach einem
fokussierten Regressionstest und neuem Preimage wurde die gesamte Matrix
wiederholt. Das qualifizierte Ergebnis belegt keine fachliche Identität und
autorisiert keinen Produktvergleich.

## Nicht Bestandteil

Nicht Bestandteil sind reale oder private Bibliotheken, ein Produktadapter,
ein Vergleich gegen ein Eingangs-EPUB, Identitätsentscheidung,
Bestandsabgleich, mehrere IDs oder Bibliotheken, Content Server, direkte
`metadata.db`-Nutzung, neue Metadatenfelder, Persistenz, Routing, UI, REST,
Agents, Import, Metadatenschreiben, Löschen oder eine andere Bestandswirkung.

Nach dem Experiment wird das Ergebnis in einem neuen Gate bewertet. Weder
`qualified` noch die technische Verfügbarkeit von `calibredb export`
autorisiert automatisch eine Produktwave.
