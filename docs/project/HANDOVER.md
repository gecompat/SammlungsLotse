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
unter docs/planning/EBOOK_EXPLORATION_PLAN.md. WI-0002 ist `done`. Der
Vergleich unter docs/planning/EBOOK_GATE_0001_COMPARISON.md hat weder
Eingangstriage noch Bestandsprüfung angenommen: GATE-0001 ist begründet
vertagt und bleibt offen.

WI-0003 ist auf Dokumentationsebene abgeschlossen. Die sechs
Nutzerentscheidungen und Messverträge stehen unter
docs/planning/EBOOK_SCENARIOS_AND_METRICS.md. TEST-0001 ist unter
docs/planning/EBOOK_REFERENCE_CORPUS.md als aktive Fixture-Version `0.2.0` mit allen
26 `Kern`-Fällen, 44 Komponenten, Hashes, Herkunft und Oracles ausführbar und
validiert; `0.1.0` bleibt als historischer Snapshot erhalten. Die vier
`Ausbau`-Fälle bleiben offen. EXP-0005 ist mit elf erfolgreichen
Isolationskriterien abgeschlossen. EXP-0002 ist mit dreizehn erfolgreichen
Calibre-Projektionskriterien abgeschlossen; der direkte read-only Mount ist
als nicht unterstützt und die Copy-on-read-Grenze als erfolgreich belegt.
EXP-0003 ist mit vierzehn erfolgreichen Evidenzkriterien abgeschlossen:
EPUBCheck- und Ace-Rohberichte bleiben getrennt und verlustfrei, unbekannte
Codes sowie manueller Prüfbedarf bleiben sichtbar. Das erprobte Ace-Profil
ist wegen deaktivierter Chromium-Sandbox und offener npm-Advisories nicht
produktqualifiziert. EXP-0004 ist mit fünfzehn erfolgreichen Kriterien
abgeschlossen: Sechs Sollpaare bleiben auf fünf Identitätsebenen getrennt,
Kandidaten zeigen positive und negative Evidenz, fehlende Evidenz bleibt
separat und Leseprobe/Vollausgabe führt auf Ausgabenebene zur Enthaltung. Die
perfekten Werte des kleinen synthetischen Goldstandards sind keine
Produktprognose. EXP-0006 ist als genau eine nächste Evidenzwelle registriert
und mit fester Sollmatrix, sicherer Reihenfolge, Pass-, Fail- und
Stoppkriterien spezifiziert, aber noch nicht ausgeführt. Alle Verträge stehen
unter docs/planning/EBOOK_EXPERIMENTS.md.

## Fortsetzung

Die nächste Arbeit implementiert und führt ausschließlich EXP-0006 als
gebundene Experiment-Wave aus. Vor dem ersten Lauf müssen Ausführungsprofil,
wegwerfbarer Runner, Ergebnisvertrag und Ergebnisvalidator unter
experiments/ebook/exp-0006/ versioniert sein. Die Wave verwendet nur die
festgelegten synthetischen TEST-0001-Eingänge und beginnt weder Produktcode
noch einen Writer. Erst nach ihrem versionierten Ergebnis wird GATE-0001
erneut ausgewertet.

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
- konkrete, empirisch qualifizierte Produktprofile; EXP-0002 qualifiziert nur
  den Copy-on-read-Calibre-Zugriff, EXP-0003 nur eine Evidenzprojektion mit
  nicht produktqualifiziertem Ace-Profil, EXP-0004 nur eine kleine
  synthetische Identitätsheuristik und EXP-0005 nur einen wegwerfbaren
  Sicherheitsweg; EXP-0006 ist noch nicht ausgeführt; keiner dieser Versuche
  wählt eine Produktlaufzeit;
- ein optionales Repository-Continuity-Verfahren mit getrennten Rulesets,
  autorisierten Akteuren und Ausfallschwelle. Bis zu einer angenommenen
  Entscheidung existiert kein Break-Glass-Bypass.

## Validierung

Die aktuellen Prüfergebnisse stehen ausschließlich in
docs/project/PROJECT_STATUS.md.
