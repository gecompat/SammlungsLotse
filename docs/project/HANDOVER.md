# Übergabe

Status: AUTHORITATIVE

Stand: 2026-08-27

## Aktueller Stand

SammlungsLotse ist als eigenständiges Projekt initialisiert. Die
Produktimplementierung hat noch nicht begonnen. Die ergebnisoffene
Entwicklungsplanung untersucht die E-Book-Linie, ohne sie als erste
Implementierungslinie auszuwählen. AI Repository Foundation 1.7.0 ist
semantisch integriert. Die Bewertung steht unter
docs/governance/FOUNDATION_UPGRADE_1_7.md.

main ist geschützt. Änderungen benötigen die erfolgreichen Checks
repository-quality und registry-integrity.

Die maßgeblichen Produktgrenzen stehen in docs/product/PROJECT_CHARTER.md und
docs/architecture/BOUNDARIES.md. Die Startentscheidungen stehen unter
docs/decisions/.

Der aktuelle E-Book-Brainstorming-Stand steht unter
docs/planning/EBOOK_LANDSCAPE.md. Die weitere Erkenntnisreihenfolge steht
unter docs/planning/EBOOK_EXPLORATION_PLAN.md. WI-0002 ist `in_progress`;
GATE-0001 bleibt offen.

WI-0003 ist auf Dokumentationsebene abgeschlossen. Die sechs
Nutzerentscheidungen und Messverträge stehen unter
docs/planning/EBOOK_SCENARIOS_AND_METRICS.md. TEST-0001 ist unter
docs/planning/EBOOK_REFERENCE_CORPUS.md bis auf Kern- und Ausbau-Sollfälle,
Oracles und Datenregeln konkretisiert, aber noch nicht ausgeführt. Die
getrennten, ebenfalls noch nicht ausgeführten Experimentverträge EXP-0002 bis
EXP-0005 stehen unter docs/planning/EBOOK_EXPERIMENTS.md.

## Fortsetzung

Die nächste Arbeit setzt WI-0002 mit der TEST-0001-Fixture-Wave fort. Sie
erzeugt ausschließlich die synthetischen `Kern`-Fälle, dokumentiert Herkunft,
Hashes und maschinenlesbare Oracles und validiert ihre verbotenen Wirkungen.
Erst danach werden EXP-0002 bis EXP-0005 einzeln ausgeführt. Die Arbeit beginnt
weder Produktcode noch einen Writer und trifft keine Technologie- oder
Vertikalablaufentscheidung vor GATE-0001.

## Harte Grenzen

- Fachsysteme bleiben führend.
- Kein FolioTone-Code wird ohne Rechte- und Eignungsprüfung übernommen.
- Kein reales privates Sammlungsmedium gelangt in Git.
- Produktcode wird nicht ohne registrierten Arbeitsgegenstand begonnen.
- Schreibende Fähigkeiten benötigen eine eigene Entscheidung und vollständige
  Sicherheitskette.

## Noch nicht entschieden

- erste Medienlinie;
- erster vollständiger Nutzerablauf;
- Programmiersprache und Laufzeit;
- Persistenz und Suche;
- Deployment und UI;
- konkrete REST- und Agent-Verträge;
- konkrete FolioTone-Wiederverwendung;
- erster E-Book-Vertikalablauf;
- Tiefe der ersten Formatunterstützung und konkrete Qualitätsprofile;
- konkrete Calibre-, Werkzeug- und Metadatenprovider-Adapter;
- Format des TEST-0001-Ausführungsmanifests und konkrete Fixture-Generatoren;
- konkrete, empirisch qualifizierte Werkzeug- und Ausführungsprofile für
  EXP-0002 bis EXP-0005;
- ein optionales Repository-Continuity-Verfahren mit getrennten Rulesets,
  autorisierten Akteuren und Ausfallschwelle. Bis zu einer angenommenen
  Entscheidung existiert kein Break-Glass-Bypass.

## Validierung

Die aktuellen Prüfergebnisse stehen ausschließlich in
docs/project/PROJECT_STATUS.md.
