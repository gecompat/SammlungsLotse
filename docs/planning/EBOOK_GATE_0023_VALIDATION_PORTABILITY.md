# GATE-0023: Sichere Validierungsportabilität nach EXP-0018 bewerten

Status: DONE — OPTION A AUTONOM AUSGEWÄHLT

Stand: 2026-09-13

Artifact: GATE-0023

## Befund

Unter der lokalen Windows-Umgebung ist die Erzeugung symbolischer Links ohne
die erforderliche Betriebssystemberechtigung nicht verfügbar. Zwei
synthetische Negativkontrollen behandeln diesen Umstand derzeit als Fehler,
während die WI-0016-Tests ihn bereits korrekt als Skip ausweisen. Davon
getrennt ändern unterschiedliche Python-/zlib-Versionen die bytegenaue
Kompression historischer EPUB-Fixtures; dieser Befund betrifft gebundene
Evidenz und darf nicht beiläufig durch Regeneration oder Lockerung repariert
werden.

## Optionen

### A — Fehlende Symlink-Fähigkeit eng als Skip behandeln

WI-0017 vereinheitlicht ausschließlich die beiden optionalen synthetischen
Kontrollen. Bei verfügbarer Fähigkeit bleiben sie unverändert aktiv; bei
nachweislich fehlender Fähigkeit wird der Test sichtbar übersprungen.

### B — Historische ZIP-Nachweise neu erzeugen

Nicht auswählen. Das würde historische bytegebundene Evidenz überschreiben,
ohne eine kanonische Laufzeit- oder Kompressionsentscheidung getroffen zu
haben.

### C — Kanonische ZIP-Reproduzierbarkeit neu entscheiden

Fachlich notwendig, aber breiter: eine getrennte Entscheidung muss entweder
eine exakte Toolchain binden oder eine neue semantische Evidenzform
begründen. Sie ist nicht Bestandteil von WI-0017.

## Auswahl und Grenzen

Option A ist die kleinste sichere, reversible Maintenance-Wave und wird unter
der Autonomie-Autorisierung ausgewählt. WI-0017 darf weder Produktcode noch
Fixture-, Hash-, Oracle- oder historische Ergebnisdateien verändern. Die
ZIP-Portabilitätsfrage bleibt ausdrücklich offen.
