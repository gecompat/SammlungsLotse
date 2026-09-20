# EXP-0025: Docker-gebundene synthetische Mehrbibliotheksprojektion

Status: ACCEPTED

Stand: 2026-09-20

Artifact: EXP-0025

## Zweck

EXP-0025 qualifiziert ausschließlich, ob zwei bis drei getrennte,
task-private TEST-0001-Calibre-Bibliotheken über einen eigenen,
profil-, image- und inspect-gebundenen Docker-Weg minimal und pfadfrei
projiziert werden können. Er erweitert keine öffentliche Oberfläche und
entscheidet keine Zielbibliothek.

## Vorbedingungen

Vor einem tatsächlichen Lauf muss WI-0020 einen eigenständigen Docker-
Produktpreimage bereitstellen: gebundenes Profil, lokales Image,
zurückgelesene Isolationswerte sowie eine Docker-E2E-Qualifikation. Das
historische EXP-0021-Transferprofil ist kein Produktprofil. EXP-0022 bleibt
`not_qualified` und wird weder als Voraussetzung noch als
Runtimeäquivalenznachweis verwendet.

## Gebundener Lauf

- Die Matrix enthält genau zwei oder drei getrennte TEST-0001-Bibliotheken;
  Bibliothekspositionen sind eindeutig und werden ausschließlich anonym
  ausgegeben.
- Je Bibliothek entstehen zwei unabhängige Projektionen. Determinismus wird
  nur innerhalb derselben Bibliothek geprüft; Gleichheit zwischen
  Bibliotheken wird weder verlangt noch fachlich gedeutet.
- Jede Ausführung verwendet ausschließlich eine frische task-private
  Copy-on-read-Kopie. Quelle und Kopie werden vor und nach der Ausführung
  hashgebunden geprüft; nur die Arbeitskopie darf schreibbar gemountet sein.
- Vor jedem Start werden Docker-Client und -Server, Image-ID,
  Linux/amd64-Plattform, Entrypoint, Command, vollständige Image-Umgebung
  und die zurückgelesene Containerisolation exakt gebunden. Netzwerk bleibt
  deaktiviert; Root-Dateisystem, Capabilities, UID, PID-, CPU-, Speicher-,
  Swap-, Ulimit-, tmpfs-, Log- und Mountgrenzen bleiben fail-closed.
- Das eingecheckte Ergebnis enthält nur Positionen, Versionen, Zählwerte,
  normalisierte Projektdigests, Snapshot-/Cleanup- und Isolationsbelege.
  Titel, Autoren, externe IDs, Formate, Pfade, Rohberichte und private Daten
  bleiben ausgeschlossen.

## Akzeptanz

Der Nachweis besteht nur bei exakt gebundenem Preimage, zwei semantisch
identischen Wiederholungen je Bibliothek, unveränderten TEST-0001-Quellen,
vollständigem Task- und Containercleanup sowie null Netzwerk-, Persistenz-,
Import-, Writer-, Discovery- und Produktoberflächenwirkung. Abweichendes
Profil, Image, Inspect, Output, Quellsnapshot oder Cleanup führt zu
`not_qualified` ohne Teilprojektion und ohne Fallback.

Der CI-Validator liest nur den eingecheckten Nachweis und das gebundene
Preimage; er startet weder Docker noch Netzwerk.

## Nichtziele

Keine öffentliche Mehrbibliotheksoberfläche, Kandidaten- oder Rankinglogik,
Zielwahl, Same-/New-/Importaussage, Persistenz, Index, Suche, Discovery,
Writer, Docker-Podman-Vergleich oder Änderung bestehender Podman- und
WI-0019-Verträge.
