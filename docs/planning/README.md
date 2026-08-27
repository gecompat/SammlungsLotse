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
- [GATE-0001-Vergleich der ersten Vertikalabläufe](EBOOK_GATE_0001_COMPARISON.md);
- [Nutzerszenarien und Messverträge](EBOOK_SCENARIOS_AND_METRICS.md);
- [TEST-0001-Referenzkorpus](EBOOK_REFERENCE_CORPUS.md);
- [E-Book-Experimentverträge](EBOOK_EXPERIMENTS.md).

WI-0002 ist nach dem ergebnisoffenen GATE-0001-Vergleich `done`. WI-0003 hat
sechs read-only Nutzerentscheidungen und Messverträge auf Dokumentationsebene
abgeschlossen. TEST-0001 ist mit 26
synthetischen Kernfällen in der aktiven Version `0.2.0` ausführbar und
`ready`; `0.1.0` bleibt historisch erhalten. EXP-0002 bis EXP-0006 sind
empirisch abgeschlossen. CAP-0002, REQ-0001, REQ-0002 und EXP-0001 sind
vorgeschlagen. EXP-0006 hat alle 16 Akzeptanzkriterien und die
elf vorab gebundenen Preflight-Zeilen in zwei semantisch identischen
Wiederholungen erfüllt.
GATE-0001 ist nach getrennter Neubewertung `done`: Die Eingangstriage ist
innerhalb der engen Grenze aus stabilem Snapshot, flachem Preflight und
begründeter Folgeaktion oder Enthaltung als erster read-only
E-Book-Vertikalablauf angenommen. Bestandsprüfung bleibt ein möglicher
späterer Ast.
RISK-0001 hält das bereits anerkannte Risiko einer frühen fachlichen oder
technischen Kopplung fest. Die Gate-Auswahl wählt keinen Technologie-Stack,
keine erste Medien- oder Implementierungslinie und autorisiert weder
Produktcode noch schreibende Operationen.

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
Calibre-Projektion über eine Copy-on-read-Grenze, EXP-0003 die verlustfreie
EPUBCheck-/Ace-Evidenzprojektion und EXP-0004 die gestufte
Identitätsbewertung bestanden. Ihr erster Vergleich vertagte beide
Kandidaten. Die daraufhin als genau eine Evidenzwelle ausgeführte
EXP-0006-Qualifikation hat den engen read-only Eingangstriage-Preflight
synthetisch bestanden. Die getrennte Neubewertung hat deshalb S2 innerhalb
dieser Grenze angenommen. Als nächster Schritt wird ein eigener
Arbeitsgegenstand für den dünnen Prototyp registriert und geplant; bis zu
dessen Annahme bleibt Produktcode nicht autorisiert.

## Nicht übernehmen

FolioTone-Backlog, Wave-Nummern und Implementierungsstatus werden nicht als
SammlungsLotse-Plan importiert.
