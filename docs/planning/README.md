# Planungseinstieg

Status: AUTHORITATIVE

Die ergebnisoffene Entwicklungsplanung hat begonnen. Es gibt weiterhin keinen
angenommenen Produktbacklog und keine freigegebene technische Roadmap.

## Aktueller Brainstorming-Stand

Die E-Book-Linie wird als möglicher erster Schwerpunkt untersucht, ist aber
noch nicht ausgewählt. Der aktuelle Stand trennt bewusst Möglichkeiten,
Untersuchungshypothesen, Experimente und spätere Entscheidungen:

- [E-Book-Möglichkeitenraum](EBOOK_LANDSCAPE.md);
- [E-Book-Erkundungs- und Erkenntnisplan](EBOOK_EXPLORATION_PLAN.md);
- [Nutzerszenarien und Messverträge](EBOOK_SCENARIOS_AND_METRICS.md);
- [TEST-0001-Referenzkorpus](EBOOK_REFERENCE_CORPUS.md);
- [E-Book-Experimentverträge](EBOOK_EXPERIMENTS.md).

WI-0002 ist `in_progress`. WI-0003 hat sechs read-only Nutzerentscheidungen
und Messverträge auf Dokumentationsebene abgeschlossen. TEST-0001 ist mit 26
synthetischen Kernfällen in der aktiven Version `0.2.0` ausführbar und
`ready`; `0.1.0` bleibt historisch erhalten. EXP-0002, EXP-0003 und EXP-0005
sind empirisch abgeschlossen. CAP-0002, REQ-0001, REQ-0002, EXP-0001,
EXP-0004 und GATE-0001 sind vorgeschlagen.
RISK-0001 hält das bereits anerkannte Risiko einer frühen fachlichen oder
technischen Kopplung fest. Keines dieser Artefakte wählt einen
Technologie-Stack, bestimmt den ersten Vertikalablauf oder autorisiert
Produktcode oder schreibende Operationen.

## Verbindliche Ausgangsbasis

Vor der ersten Planungs-Wave gelten:

- der [Projektauftrag](../product/PROJECT_CHARTER.md);
- die [Produkt- und Systemgrenzen](../architecture/BOUNDARIES.md);
- die angenommenen [Entscheidungen](../decisions/README.md);
- die [Projektregeln](../governance/PROJECT_RULES.md);
- die Registration Authority .ai/artifact_registry.json;
- der tatsächliche [Projektstatus](../project/PROJECT_STATUS.md).

## Erste Planungsfragen

Die erste Planungs-Wave soll:

1. den kleinsten vollständigen Nutzwert und die erste Medienlinie auswählen;
2. Nutzerablauf und Akzeptanzkriterien festlegen;
3. Kern- und Adaptergrenzen konkretisieren;
4. Technologieoptionen anhand des Ablaufs bewerten;
5. FolioTone-Wiederverwendungskandidaten mit Rechten und Kopplung prüfen;
6. Datenschutz-, Sicherheits- und Schreibgrenzen in testbare Anforderungen
   überführen;
7. Fähigkeiten, Anforderungen, Entscheidungen, Risiken, Gates und
   Arbeitsgegenstände über die Registry registrieren;
8. erst danach eine ausführbare Reihenfolge bilden.

Eine E-Book-Linie ist ein naheliegender Kandidat, aber weiterhin nicht als
erste Implementierungs-Wave entschieden.

## Nächste Erkenntnis-Wave

EXP-0005 hat die gemeinsame Sicherheitsqualifikation, EXP-0002 die lokale
Calibre-Projektion über eine Copy-on-read-Grenze und EXP-0003 die
verlustfreie EPUBCheck-/Ace-Evidenzprojektion bestanden. Als Nächstes folgt
EXP-0004 mit vollständigen positiven und negativen Sollpaaren. GATE-0001
bleibt bis zu diesem Ergebnis offen.

## Nicht übernehmen

FolioTone-Backlog, Wave-Nummern und Implementierungsstatus werden nicht als
SammlungsLotse-Plan importiert.
