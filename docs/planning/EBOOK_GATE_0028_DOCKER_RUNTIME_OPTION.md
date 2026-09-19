# GATE-0028: Docker-Laufzeitoption für den E-Book-Reviewplan getrennt bewerten

Status: DONE — OPTION A AUTONOM AUSGEWÄHLT

Stand: 2026-09-19

Artifact: GATE-0028

## Ausgangslage

EXP-0020 darf den bestehenden öffentlichen WI-0019-Weg nur über das exakt
gebundene Podman-Profil prüfen. Der lokale Podman-Server erfüllt dessen
Mindestversion nicht; Docker Desktop ist hingegen verfügbar. Docker besitzt
einen getrennten Image-Speicher und ist kein Austausch ohne eigene Evidenz.

## Optionen

### A — Separate synthetische Docker-Äquivalenz prüfen

EXP-0021 erprobt produktcodefrei mit eigener Docker-Profildokumentation, ob
ein synthetischer Calibre-Reviewplan-Lauf die gebundenen Read-only- und
Isolationsgrenzen nachweisbar einhalten kann. Die Auswertung ist Evidenz für
eine spätere Runtimeentscheidung, keine Produktqualifikation.

### B — Bestehenden Podman-Produktvertrag auf Docker umstellen

Nicht auswählen. Das würde Profil, Executor und öffentliche Vertragsgrenzen
ändern, bevor die Docker-Isolation und Reproduzierbarkeit belegt sind.

### C — Podman-Mindestversion oder -Profil lockern

Nicht auswählen. Das vorhandene Profil bleibt historische, exakte Evidenz;
eine Lockerung darf nicht aus einer nicht erfüllten lokalen Voraussetzung
abgeleitet werden.

### K — Den bestehenden Stand konservieren

Der Podman-Vertrag bleibt unverändert; es wird keine Docker-Evidenz erzeugt.

## Auswahl

Option A wird unter der Autonomie-Autorisierung und der ausdrücklichen
Docker-Anweisung gewählt. EXP-0021 bleibt auf synthetische Daten, einen
ephemeren read-only Lauf und überprüfbare Isolation begrenzt.

## Harte Grenzen

- kein Produktcode und keine Änderung von Podman-Profil, -Executor oder
  öffentlicher CLI;
- kein Netzwerk, keine Persistenz, kein Import, kein Writer und keine
  Bestandswirkung;
- nur TEST-0001 und neu materialisierte, task-private synthetische Daten;
- kein Docker-Image aus dem Podman-Speicher als unbelegte Gleichwertigkeit;
- ein Ergebnis qualifiziert weder einen Runtimewechsel noch reale Bestände.
