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
docs/planning/EBOOK_REFERENCE_CORPUS.md als aktive Fixture-Version `0.2.0` mit allen
26 `Kern`-Fällen, 44 Komponenten, Hashes, Herkunft und Oracles ausführbar und
validiert; `0.1.0` bleibt als historischer Snapshot erhalten. Die vier
`Ausbau`-Fälle bleiben offen. EXP-0005 ist mit elf erfolgreichen
Isolationskriterien abgeschlossen. Die noch nicht ausgeführten Verträge
EXP-0002 bis EXP-0004 stehen mit dem Ergebnis unter
docs/planning/EBOOK_EXPERIMENTS.md.

## Fortsetzung

Die nächste Arbeit setzt WI-0002 mit EXP-0002 fort. Genau zwei synthetische
Calibre-Bibliotheken werden zunächst ausschließlich über dokumentierte
Calibre-Schreibbefehle als Experimentmaterial erzeugt. Die eigentliche
Bestandsprojektion verwendet danach nur eine minimale dokumentierte
`calibredb`-Leseoperation im qualifizierten netzwerklosen Profil und prüft
Pfadlecks, Wiederholbarkeit und Vorher-/Nachher-Zustand. Die Arbeit beginnt
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
- konkrete, empirisch qualifizierte Werkzeug- und Ausführungsprofile für
  EXP-0002 bis EXP-0004; EXP-0005 qualifiziert nur einen wegwerfbaren
  Sicherheitsweg und wählt keine Produktlaufzeit;
- ein optionales Repository-Continuity-Verfahren mit getrennten Rulesets,
  autorisierten Akteuren und Ausfallschwelle. Bis zu einer angenommenen
  Entscheidung existiert kein Break-Glass-Bypass.

## Validierung

Die aktuellen Prüfergebnisse stehen ausschließlich in
docs/project/PROJECT_STATUS.md.
