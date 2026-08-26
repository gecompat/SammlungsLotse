# FolioTone-Bewertung und Neustart

Status: OWNER SOURCE NOTE

Erfasst am: 2026-08-26

## Befund

Die groben Ziele von FolioTone bleiben sinnvoll. Die bestehende Implementierung
hat sich jedoch von der ursprünglichen Produktrolle entfernt. Insbesondere
darf ein unterstützendes System nicht zum führenden System einer Fachdomäne
werden.

Calibre-Probleme waren der Anlass für die Neubewertung, aber nicht deren
einziger Gegenstand. Die Fragestellung betrifft alle Medienlinien.

## Folgerung

SammlungsLotse beginnt als eigenständiges Projekt mit eigenem Repository,
eigener Identität, eigener Planung und eigener Architektur.

FolioTone bleibt:

- fachliche Referenz;
- Quelle für bekannte Fehler und gewonnene Erkenntnisse;
- mögliche Spenderquelle für klar abgegrenzte Komponenten;
- kein automatisch zu übernehmendes Gesamtgerüst.

## Wiederverwendungskandidaten

Folgende FolioTone-Bereiche können einzeln geprüft werden:

- rekursive Erfassung und Dateihashes;
- Evidenz- und Provenienzkonzepte;
- Ausführung externer Werkzeuge über Adapter;
- Kandidatenerzeugung, Matching und Review;
- Sammlungszustand und inkrementelle Verarbeitung;
- Sicherheitsmuster für schreibende Operationen;
- synthetische Tests und Prüffälle.

Persistenz, Workflows, Benutzeroberflächen und schreibende Operationen werden
nicht pauschal übertragen.

## Übernahmeregel

Jede Übernahme benötigt:

1. einen konkreten SammlungsLotse-Anwendungsfall;
2. einen Vergleich zwischen Übernahme, Anpassung und Neuimplementierung;
3. Herkunft mit Repository, Commit und Quelldatei;
4. Prüfung von Urheberrecht, Lizenz und Drittbestandteilen;
5. Entfernung von FolioTone-spezifischer Kopplung;
6. Tests gegen den SammlungsLotse-Vertrag;
7. eine nachvollziehbare Entscheidung im neuen Projekt.

FolioTone verwendet eine eigene Attribution-and-Non-Commercial-Redistribution-
Lizenz. SammlungsLotse verwendet MIT. Deshalb ist FolioTone-Code nicht allein
aufgrund technischer Eignung unter MIT übertragbar.
