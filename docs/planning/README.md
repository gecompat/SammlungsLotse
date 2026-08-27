# Planungseinstieg

Status: AUTHORITATIVE

Die ergebnisoffene Entwicklungsplanung hat den ersten begrenzten
Arbeitsgegenstand angenommen. Es gibt weiterhin keinen allgemeinen
Produktbacklog und keine freigegebene technische Roadmap.

## Aktueller Brainstorming-Stand

Die E-Book-Linie stellt mit WI-0004 den ersten begrenzten Produktprototyp,
ohne damit eine vollständige Medienlinie oder Roadmap festzulegen. Der
aktuelle Stand trennt bewusst Möglichkeiten, Untersuchungshypothesen,
Experimente und spätere Entscheidungen:

- [E-Book-Möglichkeitenraum](EBOOK_LANDSCAPE.md);
- [E-Book-Erkundungs- und Erkenntnisplan](EBOOK_EXPLORATION_PLAN.md);
- [GATE-0001-Vergleich der ersten Vertikalabläufe](EBOOK_GATE_0001_COMPARISON.md);
- [WI-0004: dünner read-only Eingangstriage-Prototyp](EBOOK_INTAKE_PROTOTYPE.md);
- [GATE-0002: Fortsetzung nach dem Prototyp](EBOOK_GATE_0002_AFTER_PROTOTYPE.md);
- [EXP-0007 und GATE-0003: Snapshot-zu-Werkzeug-Übergang](EBOOK_DEEP_READONLY_HANDOFF_EXPERIMENT.md);
- [GATE-0003: V2 auswählen](EBOOK_GATE_0003_HANDOFF_DECISION.md);
- [WI-0005: tiefen read-only Adapter begrenzen](EBOOK_DEEP_READONLY_ADAPTER_WORK_ITEM.md);
- [WI-0006: read-only Mehrdatei-Eingangsbericht](EBOOK_MULTI_FILE_INTAKE_REPORT.md);
- [Nutzerszenarien und Messverträge](EBOOK_SCENARIOS_AND_METRICS.md);
- [TEST-0001-Referenzkorpus](EBOOK_REFERENCE_CORPUS.md);
- [E-Book-Experimentverträge](EBOOK_EXPERIMENTS.md).

WI-0002 ist nach dem ergebnisoffenen GATE-0001-Vergleich `done`. WI-0003 hat
sechs read-only Nutzerentscheidungen und Messverträge auf Dokumentationsebene
abgeschlossen. TEST-0001 ist mit 26 `Kern`- und vier `Ausbau`-Fällen in der
aktiven Version `0.3.0` vollständig ausführbar und `ready`; `0.1.0` und
`0.2.0` bleiben historisch erhalten. EXP-0002 bis EXP-0006 sind
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
technischen Kopplung fest. Die Gate-Auswahl wählt keinen allgemeinen
Technologie-Stack und autorisiert keine schreibenden Operationen.

WI-0004 ist als erster eng begrenzter Produktprototyp `done`. Sein
kanonischer Vertrag endet nach einem unveränderten In-Memory-Snapshot,
flachem Preflight und sichtbarer CLI-Folgeaktion oder Enthaltung. Die Auswahl
von Python 3.12 und Standardbibliothek gilt nur für diesen reversiblen
Prototyp. Calibre, tiefe Werkzeuge, Persistenz, Browser, REST, Agents und
Writes bleiben außerhalb.

GATE-0002, EXP-0007 und GATE-0003 sind `done`. EXP-0007 hat drei
providerneutrale Übergaben eines unveränderlichen Snapshots an einen tiefen
read-only Werkzeugprozess verglichen: V1 und V2 sind qualifiziert, V3 ist
abgelehnt. GATE-0003 wählt V2 als Standardnaht. Die getrennte aktuelle
Werkzeug- und Vertragsbewertung nahm WI-0005 mit EPUBCheck 5.3.0 als erstem
Provider und einem austauschbaren Prozessport an. Die getrennte
Implementierungs-Wave ist `done`: Das aktuelle digestgebundene Podman-Profil
ist reproduzierbar gebaut, 12/12 synthetisch qualifiziert und ausschließlich
über den expliziten CLI-Opt-in erreichbar.

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

WI-0004 ist als erste Implementierungs-Wave entschieden und abgeschlossen.
Diese Auswahl gilt
nur für den dünnen Eingangstriage-Prototyp und nicht als Annahme der gesamten
E-Book-Linie.

## Nächste Erkenntnis-Wave

EXP-0005 hat die gemeinsame Sicherheitsqualifikation, EXP-0002 die lokale
Calibre-Projektion über eine Copy-on-read-Grenze, EXP-0003 die verlustfreie
EPUBCheck-/Ace-Evidenzprojektion und EXP-0004 die gestufte
Identitätsbewertung bestanden. Ihr erster Vergleich vertagte beide
Kandidaten. Die daraufhin als genau eine Evidenzwelle ausgeführte
EXP-0006-Qualifikation hat den engen read-only Eingangstriage-Preflight
synthetisch bestanden. Die getrennte Neubewertung hat deshalb S2 innerhalb
dieser Grenze angenommen. WI-0004 hat den dünnen Prototyp anschließend
registriert, vollständig begrenzt, implementiert und lokal abgenommen.
GATE-0002 hat daraufhin Kern-/CLI-Härtung, die Planung eines tiefen read-only
Adapters und das Pausieren verglichen und EXP-0007 ausgewählt. Das Experiment
hat V1 und V2 qualifiziert und V3 wegen Originalpfad- und TOCTOU-Risiko
abgelehnt. GATE-0003 wählt V2 als Standardnaht und schlägt WI-0005 vor. Die
anschließende aktuelle Werkzeug-, Lizenz-, Wartungs-, Betriebs- und
Vertragsbewertung nahm WI-0005 eng begrenzt an. Die eigene
Implementierungs-Wave hat das aktuelle Temurin-Artefakt, sämtliche
Build-Eingänge und die reproduzierbare Image-ID gebunden, den Adapter
umgesetzt und das exakte Profil vollständig mit synthetischen Medien
qualifiziert. Die anschließend ausgewählte nächste Produktwave ist WI-0006:
Sie erweitert ausschließlich die lokale CLI um einen kleinen read-only
Mehrdatei-Bericht für explizit angegebene Dateien. Schnelle Prüfung bleibt
Standard, tiefe EPUBCheck-Prüfung bleibt Opt-in; Verzeichnissuche,
Berichtsdatei, Persistenz, Fachsystemzugriff und Writes bleiben außerhalb.

## Nicht übernehmen

FolioTone-Backlog, Wave-Nummern und Implementierungsstatus werden nicht als
SammlungsLotse-Plan importiert.
