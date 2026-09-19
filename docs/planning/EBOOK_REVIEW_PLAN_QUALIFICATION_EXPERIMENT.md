# EXP-0020: Synthetische End-to-End-Qualifikation des E-Book-Reviewplans

Status: ACCEPTED

Stand: 2026-09-19

Artifact: EXP-0020

## Zweck

EXP-0020 prüft ausschließlich mit TEST-0001-Material, ob der öffentliche
WI-0019-CLI-Weg einen expliziten Eingangsordner und eine explizite,
synthetische Calibre-Bibliothek deterministisch zu begrenzten manuellen
Reviewhinweisen verbindet.

## Gebundener Gegenstand

- genau eine synthetische Einzelbibliothek über das bestehende
  Copy-on-read-Profil;
- ein begrenzter Eingangsordner mit positiven, blockierten, Nicht-EPUB- und
  Kandidatenlimit-Fällen;
- zwei semantisch identische Wiederholungen mit pfad-, titel- und
  inhaltsfreier Standardausgabe;
- Prüfung von Quellenhash, Task- und Container-Cleanup sowie fehlenden
  Netzwerk-, Persistenz-, Import-, Writer- und Bestandswirkungen.

## Akzeptanzgrenzen

Ein erfolgreicher Lauf beweist keine Kandidatenvollständigkeit, keine
Dublettengleichheit, keine Zielauswahl und keine reale
Calibre-Kompatibilität. Mehrere Bibliotheken, Routing und jede schreibende
Operation bleiben außerhalb.

## Ausführungsstand

Der Runner und seine synthetischen Verträge sind implementiert und lokal
fokussiert geprüft. Der tatsächliche synthetische Lauf ist `pending manual
validation`: Podman ist verfügbar, aber das exakt an WI-0007 gebundene Image
`localhost/sammlungslotse-calibre-readonly:wi-0007` fehlt lokal. Der Lauf
scheiterte vor Materialisierung und CLI-Ausführung kontrolliert; der neue
Taskroot wurde vollständig bereinigt. Ein fehlendes Laufresultat wird nicht
als bestandene Qualifikation dargestellt.
