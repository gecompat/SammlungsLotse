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
- [WI-0007: read-only Calibre-Bestandsprojektion](CALIBRE_READ_ONLY_PROJECTION_WORK_ITEM.md);
- [GATE-0004: nächste Wave nach der Calibre-Projektion](EBOOK_GATE_0004_AFTER_CALIBRE_PROJECTION.md);
- [WI-0008: synthetischen Calibre-Vertrag härten](CALIBRE_SYNTHETIC_CONTRACT_HARDENING.md);
- [GATE-0005: nächsten read-only Nutzwert auswählen](EBOOK_GATE_0005_AFTER_CALIBRE_HARDENING.md);
- [WI-0009: Identitätskandidatenbericht für zwei EPUB-Dateien](EBOOK_IDENTITY_CANDIDATE_REPORT_WORK_ITEM.md);
- [WI-0010: WI-0005-Laufzeitpreimage vollständig binden](EBOOK_WI0005_EVIDENCE_BINDING_HARDENING.md);
- [GATE-0006: nächste Evidenzfrage nach WI-0010](EBOOK_GATE_0006_AFTER_WI0010.md);
- [EXP-0008: unterstützte Calibre-Einzelrecord-EPUB-Übergabe](EBOOK_CALIBRE_SINGLE_RECORD_HANDOFF_EXPERIMENT.md);
- [GATE-0007: Produktfortsetzung nach EXP-0008](EBOOK_GATE_0007_AFTER_EXP0008.md);
- [WI-0011: explizites EPUB gegen einen Calibre-Datensatz](EBOOK_CALIBRE_IDENTITY_COMPARISON_WORK_ITEM.md);
- [GATE-0008: Fortsetzung nach WI-0011 ergebnisoffen bewerten](EBOOK_GATE_0008_AFTER_WI0011.md);
- [EXP-0009: Identitäts- und Enthaltungsevidenz verbreitern](EBOOK_IDENTITY_EVIDENCE_HARDENING_EXPERIMENT.md);
- [GATE-0009: Fortsetzung nach EXP-0009 und Metadatensemantik bewerten](EBOOK_GATE_0009_AFTER_EXP0009.md);
- [EXP-0010: EPUB-Metadaten- und Oracle-Evidenz standardgebunden prüfen](EBOOK_STANDARDS_BOUND_METADATA_ORACLE_EXPERIMENT.md);
- [GATE-0010: Produktfortsetzung nach EXP-0010 bewerten](EBOOK_GATE_0010_AFTER_EXP0010.md);
- [WI-0012: False-Same-Guardrail für den EPUB-Identitätsbericht](EBOOK_IDENTITY_FALSE_SAME_GUARDRAIL_WORK_ITEM.md);
- [GATE-0011: Fortsetzung nach WI-0012 ergebnisoffen bewerten](EBOOK_GATE_0011_AFTER_WI0012.md);
- [EXP-0011: rollenbewusste Metadaten- und Identitätsverträge vergleichen](EBOOK_IDENTITY_METADATA_CONTRACT_EXPERIMENT.md);
- [GATE-0012: Fortsetzung nach EXP-0011 bewerten](EBOOK_GATE_0012_AFTER_EXP0011.md);
- [WI-0013: rollenbewussten EPUB-Identitätsbericht V2 umsetzen](EBOOK_IDENTITY_ROLE_AWARE_V2_WORK_ITEM.md);
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
Die getrennte Implementierungs-Wave ist abgeschlossen und synthetisch über
automatisierte sowie tatsächliche CLI- und Podman-Läufe abgenommen.

Die nächste neu entschiedene Produktwave ist WI-0007. Sie übernimmt den in
EXP-0002 belegten lokalen Calibre-Zugriff als enges Produktprofil: genau eine
ausdrücklich angegebene Bibliothek, eine unveränderte begrenzte Copy-on-read-
Arbeitskopie, die dokumentierte `calibredb`-CLI und eine pfadfreie Projektion
auf Calibre-ID, Titel, Autoren, Sprachen und Formate. Planung und Registrierung
sind angenommen. Die getrennte Implementierungs-Wave ist abgeschlossen: Das
exakte Calibre-9.13.0-Image wurde reproduzierbar gebaut, der Adapter umgesetzt
und die deutsche sowie stabile JSON-CLI ausschließlich synthetisch mit 17/17
Produktkriterien qualifiziert.

GATE-0004 hat anschließend drei getrennte Fortsetzungen verglichen. Es wählt
WI-0008 aus, um die konkrete Evidenz- und Reproduzierbarkeitslücke des
einzelnen tatsächlichen Calibre-Datensatzes zu schließen. WI-0008 ist
abgeschlossen: Die reproduzierbare Drei-Datensatz-Materialisierung deckte
eine reale Mehrfachautoren-Normalisierung auf, die eng korrigiert und durch
den neuen v2-Produktnachweis mit 29/29 Kriterien qualifiziert wurde. Die Wave
ändert weder Produktoberfläche und Felder noch Einzelbibliotheks-,
Read-only-, Datenschutz- oder Writer-Grenzen.

GATE-0005 hat danach den expliziten Zwei-EPUB-Paarvergleich, einen Vergleich
gegen Calibre und neue Provider-/Mehrbibliotheksflächen getrennt bewertet.
Es wählt WI-0009 als kleinsten nächsten Nutzwert. WI-0009 ist umgesetzt und
synthetisch mit 16/16 Kriterien qualifiziert: Genau zwei explizite
unveränderliche EPUB-Snapshots liefern einen pfadfreien, erklärbaren
Identitätskandidatenbericht. Kandidaten, negative und fehlende Evidenz sowie
Enthaltung bleiben getrennt; es gibt keine Bestandsaktion.

WI-0010 ist als reine Härtungswave abgeschlossen. Der WI-0005-
Produktnachweis bindet nun den Runner und alle Intake-Pythonmodule
automatisch, besitzt einen Regressionstest gegen künftige Auslassungen und
wurde mit dem unveränderten exakten Podman-Profil erneut 12/12 qualifiziert.
Dies entscheidet keine weitere Produktfunktion und qualifiziert keinen
Parallelbetrieb.

GATE-0006 hat anschließend fünf getrennte Fortsetzungen verglichen. Es wählt
EXP-0008 als genau eine neue synthetische Evidenzwave: Die unterstützte
Calibre-CLI soll für eine explizite externe ID ausschließlich ein
bytegleiches EPUB aus einer task-privaten Copy-on-read-Arbeitskopie
bereitstellen. Die getrennte Ausführung ist mit 16/16 Kriterien
abgeschlossen. Ein positives Ergebnis belegt nur die technische Naht; ein
neues Ergebnisgate muss Produktvergleich, Alternativen und Pausieren erneut
bewerten. Produktcode, Calibre-Vergleich, mehrere Bibliotheken, Persistenz und
Writers sind dadurch nicht freigegeben.

GATE-0007 hat diese Ergebnisbewertung mit fünf getrennten Fortsetzungen
abgeschlossen. Es wählt WI-0011 als kleinste read-only Produktwave: genau ein
explizites Eingangs-EPUB wird gegen genau einen expliziten Calibre-Datensatz
über einen providerneutralen Snapshot-Handoff und den unveränderten
fünfstufigen WI-0009-Bericht verglichen. Die getrennte Implementierungswave
ist abgeschlossen und auf dem eingefrorenen Preimage `d70c6de` mit 23/23
ausschließlich synthetischen Kriterien qualifiziert. Nach WI-0012 wurde der
abhängige Produktweg gegen den neuen Analyzer-Preimage `97017a2` erneut
tatsächlich 23/23 qualifiziert. Automatische Suche, mehrere Dateien, IDs oder
Bibliotheken, Persistenz und jede Bestandswirkung bleiben außerhalb. Vor einer
weiteren Produktwave ist ein neues getrenntes Ergebnisgate erforderlich.

GATE-0008 ist ausgewertet und EXP-0009 abgeschlossen. Der methodische
Doppellauf bestand 12/12 Kriterien, qualifizierte den unveränderten
WI-0009-Identitätsdienst auf der breiteren adversariellen Paarmatrix aber
nicht: Ein Metadatenkollisionsfall erzeugte trotz widersprüchlicher
Werkreferenzen je einen kritischen False-Same-Befund auf Ausgaben- und
Werkebene. Der Befund blieb bis zu einem neuen Ergebnisgate offen. Dieses Gate
wählte inzwischen WI-0012; dessen enger Guardrail beseitigt die kritischen
Gleichheitsfreigaben. Kandidatensuche, Architektur-, Provider-, Persistenz-,
UI- und Writerentscheidungen bleiben offen.

GATE-0009 ist mit der ausdrücklichen Auswahl von Option A abgeschlossen. Es
trennt die zwei
EXP-0009-Oracle-Abweichungen von einer neu erkannten Semantiklücke: Das
aktuelle interne Feld `work_references` enthält tatsächlich EPUB-
`belongs-to-collection`-Werte, während primäre und zusätzliche Identifier
nicht unterschieden werden. EXP-0010 ist deshalb als genau eine
standardsgebundene, produktcodefreie Evidenzwave angenommen und ausgeführt.
Die Methode bestand 12/12; sechs kritische False Same auf Ausgabe und Werk
sowie drei getrennte semantische Fähigkeitslücken lassen die Produktqualität
`not_qualified`. GATE-0010 hat nach ausdrücklicher Nutzerauswahl den engen
Fail-safe-Guardrail als WI-0012 angenommen. Die Implementierung ist
abgeschlossen und mit 19/19 synthetischen Kriterien qualifiziert; die sechs
kritischen False Same sind auf null reduziert. Zwei schwächere
`candidate_related`-Werkabweichungen bleiben sichtbar. Rollenbewusstes
Metadatenmodell, Publikationsstufe, Collection-Semantik, unabhängige
Fortsetzung und Pausieren bleiben getrennt offen.

GATE-0011 und EXP-0011 sind abgeschlossen. Der gebundene Doppellauf bestand
14/14 Kriterien und zeigte für V1, V2 und V3 null Rollenverlust sowie
vollständige Provenienz. Der Nutzer hat in GATE-0012 ausdrücklich Option A
gewählt. WI-0013 ist deshalb als enger rollenbewusster V2-Zielvertrag
`accepted`, aber noch nicht implementiert. V1 bleibt unveränderter Standard;
V2 wird nur explizit aktiviert und bewahrt die fünf vorhandenen
Produktstufen. Publikationsstufe, V1-Deprecation, Suche, Persistenz und Writes
bleiben außerhalb. Die Implementierung beginnt erst nach Integration und
Post-Merge-Prüfung dieser Planungswave in einem neuen isolierten Worktree.

## Nicht übernehmen

FolioTone-Backlog, Wave-Nummern und Implementierungsstatus werden nicht als
SammlungsLotse-Plan importiert.
