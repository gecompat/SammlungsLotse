# GATE-0003: Tiefen read-only Werkzeugadapter zur Planung freigeben

Status: AUSGEWERTET — V2 AUSGEWÄHLT, WI-0005 NUR VORGESCHLAGEN

Stand: 2026-08-27

Artifact: GATE-0003

## Entscheidung

Für einen späteren tiefen read-only Werkzeugadapter wird ausschließlich V2,
die task-private hashgebundene Materialisierung, als Standardübergabe
ausgewählt. Der vorgeschlagene Folgegegenstand ist WI-0005. Er ist nicht
angenommen und diese Gate-Auswertung implementiert keinen Produktadapter.

V1 bleibt eine qualifizierte optionale Optimierung für Provider, die einen
begrenzten Byte-Stream tatsächlich unterstützen. Der gemeinsame Kernvertrag
darf diese Fähigkeit nicht voraussetzen. V3, das erneute Öffnen des
Original-Locators durch den Provider, ist abgelehnt.

## Empirische Grundlage

EXP-0007 wurde am 2026-08-27 auf dem unveränderten Preimage-Commit
`466fa62ca5d30e9f1b9701095fd16286dd780c18` vollständig ausgeführt.

- Windows-nativ: Python 3.12.10;
- Linux: Podman 6.1.0, Linux/amd64;
- zwei synthetische TEST-0001-Snapshots;
- drei Übergabeformen mit je zwei positiven Wiederholungen pro Plattform;
- zwölf positive Prozessläufe je Plattform, alle exakt an Snapshot-SHA-256
  und -Größe gebunden;
- alle 16 Akzeptanzkriterien bestanden;
- alle Originalhashes unverändert;
- unfreigegebene, instabile, hashabweichende und übergroße Eingänge starteten
  keinen Werkzeugprozess;
- Streamabbruch, stdout-/stderr-Grenze, Timeout, Kindprozessabschluss,
  Fehler-, Unterbrechungs-, Temp- und Crashrest-Cleanup waren wirksam;
- die Containergrenzen für Netzwerk, Benutzer, Capabilities, Root-Dateisystem,
  PID, CPU, RAM, Zeit, Umgebung, tmpfs, Output und read-only Fixture wurden
  zurückgelesen und erfüllt;
- die optionale Kompatibilitätswiederholung gegen das bereits
  provenienzgebundene lokale EPUBCheck-5.3.0-Profil war für beide
  synthetischen V2-Eingänge qualifiziert.

Der minimierte Ergebnisvertrag steht unter
`experiments/ebook/exp-0007/result.json`. Vollständige synthetische Rohbelege
bleiben außerhalb von Git.

## Variantenbewertung

| Variante | Ergebnis | Schwerster Restfehler | Gate-Folge |
|---|---|---|---|
| V1 — Byte-Stream | `QUALIFIED` | Ein dateipfadbasiertes Werkzeug kann diese Übergabe nicht nutzen. | Als spätere providerbezogene Optimierung offenhalten; nicht zum Kernzwang machen. |
| V2 — task-private Materialisierung | `QUALIFIED` | Ein Hostabsturz kann einen begrenzten, durch Recovery zu beseitigenden Rest hinterlassen. | Als Standardnaht für WI-0005 auswählen. |
| V3 — Original-Locator | `REJECTED` | Der Provider erhält den Original-Locator; eine koordinierte Änderung zwischen Snapshot und Werkzeuglesung reproduziert die TOCTOU-Lücke. | Für den Produktadapter nicht zulassen. |

## Warum V2 ausgewählt ist

V2 verbindet die Sicherheitsgrenze mit der praktisch breitesten
Werkzeugkompatibilität:

- Der Anwendungskern übergibt weiterhin nur Snapshot-Bytes, Hash und Größe.
- Originalpfad und ursprünglicher Dateiname erreichen den Provider nicht.
- Die temporäre Repräsentation liegt außerhalb des Kerns in einem
  aufgabeneigenen Bereich mit zufälligem technischen Namen.
- Hashprüfungen vor und nach dem Providerlauf binden die tatsächlich gelesene
  Datei an den freigegebenen Snapshot.
- Erfolg, Providerfehler, Timeout und Unterbrechung räumen den Taskbereich;
  Crashreste sind begrenzt, sichtbar und durch einen Recovery-Sweep
  behandelbar.
- Dateipfadbasierte Werkzeuge können die Naht nutzen, ohne dass ihr konkretes
  Schema oder ihr Befehl in den Kern gelangt.

V1 verursacht weniger temporäre Schreibwirkung, schließt aber bereits den
vorhandenen dateipfadbasierten Kompatibilitätskandidaten aus. V3 wäre zwar
einfacher, verletzt jedoch die gewählte Entkopplungs- und Datenschutzgrenze.

## Erfüllung der Gate-Bedingungen

- Providerkopplung bleibt außerhalb des Kerns: erfüllt.
- Snapshot-Bindung und fail-closed Vorbedingungen: erfüllt.
- temporäre Schreibwirkung, Pfadweitergabe und Cleanup: für V2 erfüllt.
- providerneutraler Evidenzvertrag: im synthetischen Prozessrand belegt.
- keine Gesamtqualitäts- oder Accessibility-Aussage aus einem Werkzeug:
  ausdrücklich erhalten.

Damit darf WI-0005 vorgeschlagen werden. Die Annahme und Implementierung
dieses Gegenstands bleiben eine spätere getrennte Entscheidung.

## Nicht autorisiert

GATE-0003 autorisiert nicht:

- Produktcode in dieser Wave;
- einen konkreten EPUBCheck-, Ace-, Calibre- oder anderen Produktprovider;
- eine allgemeine Prozess-, Plugin-, Container- oder Runtime-Infrastruktur;
- reale oder private Medien;
- Netzwerkzugriff im Analysepfad;
- Persistenz, Cache, Queue, Browser, REST oder Agent;
- Import, Transformation oder einen anderen Writer.

