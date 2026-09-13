# GATE-0024: Bytegebundene Fixture-Reproduzierbarkeit eindeutig begrenzen

Status: DONE — ENTSCHEIDUNGSVORBEREITUNG ABGESCHLOSSEN

Stand: 2026-09-13

Artifact: GATE-0024

## Befund

Die vollständige TEST-0001-Semantikprüfung besteht unter Python 3.14. Die
bytegenaue Reproduktion unterscheidet sich dort jedoch wegen `zlib-ng`
gegenüber den historischen ZIP-Bytes. Python 3.13 mit zlib 1.3.1 reproduziert
denselben Korpus bytegenau. Fixture-Inhalte und semantische Oracles sind nicht
betroffen.

## Optionen

- A: inkompatible zlib-ng-Toolchains vor der bytegenauen Reproduktion
  eindeutig ausweisen; ausgewählt.
- B: historische Fixtures und Hashes neu generieren; abgelehnt, weil dies
  gebundene Evidenz umschreiben würde.
- C: eine neue kanonische, versionsunabhängige ZIP-Evidenzform einführen;
  nicht Teil dieser kleinen Maintenance-Wave.

## Ergebnis

Die drei Optionen bleiben für eine spätere ausdrückliche kanonische
Toolchain- oder Versionsentscheidung getrennt erhalten. Es wird in dieser
Gate-Wave keine Fixture-, Generator-, Validator- oder Produktänderung
begonnen. WI-0018 wurde deshalb als vorzeitig registrierte Folgearbeit
`rejected`; seine Referenz bleibt dauerhaft reserviert.
