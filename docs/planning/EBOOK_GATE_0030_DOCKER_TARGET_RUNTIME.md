# GATE-0030: Docker als Zielruntime für die E-Book-Linie bewerten

Status: DONE

Stand: 2026-09-20

Artifact: GATE-0030

## Befund

EXP-0021 belegt eine eng gebundene, synthetische Docker-Umgebung. EXP-0022
blieb jedoch `not_qualified`: Docker- und Podman-Projektionen waren jeweils
intern korrekt, ihre gemeinsamen normalisierten Digests unterschieden sich.
Der Befund wird nicht umdefiniert.

## Optionen

1. Docker als Zielruntime unter neuem Produktvertrag wählen; Podman bleibt
   optional und getrennt qualifiziert.
2. Podman als alleinigen Produktvertrag beibehalten.
3. Zuerst ein weiteres Ursachenexperiment durchführen.

## Auswahl

Die ausdrückliche Nutzerentscheidung wählt Option 1. Sie autorisiert keine
Produktimplementierung: Jeder Docker-Weg braucht ein eigenes Profil,
Image-Provenienz, zurückgelesene Isolation und eine vollständige
Produktqualifikation. Podman wird nicht entfernt und darf nur mit eigenem
erfülltem Profil parallel laufen. Read-only-, Datenschutz- und Writer-Grenzen
bleiben unverändert.
