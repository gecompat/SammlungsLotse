# Projektstatus

Status: AUTHORITATIVE

Stand: 2026-08-31

## Phase

Erster eng begrenzter Produktprototyp, reversible Snapshot-Übergabewave,
WI-0005 und WI-0006 vollständig ausgeführt. Der erste tiefe read-only
Produktadapter ist eng begrenzt implementiert und mit einem exakten lokalen
Podman-Profil synthetisch qualifiziert; mehrere ausdrücklich angegebene
Dateien können sequenziell in einem pfadfreien Bericht zusammengefasst werden.
WI-0007 ist als eng begrenzte Calibre-Produktwave implementiert und mit einem
exakten lokalen Podman-Profil ausschließlich synthetisch qualifiziert.
GATE-0004 hat die nächste Fortsetzung neu bewertet. WI-0008 ist als reine
Härtungs- und Evidenzwave implementiert und mit 29/29 synthetischen Kriterien
qualifiziert.
GATE-0005 hat den nächsten read-only Nutzwert neu bewertet. WI-0009 ist als
enger Zwei-EPUB-Identitätskandidatenbericht implementiert und mit 16/16
synthetischen Kriterien qualifiziert.
WI-0010 hat anschließend ausschließlich den WI-0005-Laufzeitnachweis
gehärtet: Alle Intake-Module und der Runner sind vollständig gebunden, das
unveränderte Produktprofil ist erneut 12/12 qualifiziert.
GATE-0006 hat danach die nächste Erkenntnisfrage getrennt bewertet und
EXP-0008 ausgewählt. Der angenommene Experimentvertrag prüft ausschließlich
eine unterstützte, bytegleiche und task-private EPUB-Übergabe für genau einen
synthetischen Calibre-Datensatz. Die getrennte Ausführung ist mit 16/16
Kriterien abgeschlossen.
GATE-0007 hat das Ergebnis gegen vier alternative Fortsetzungen bewertet und
WI-0011 als kleinste nächste read-only Produktwave ausgewählt. Planung und
Registrierung des expliziten EPUB-gegen-Calibre-Datensatz-Vergleichs wurden
getrennt integriert. Die Implementierung ist abgeschlossen und mit 23/23
synthetischen Kriterien qualifiziert.
GATE-0008 ist danach ergebnisoffen ausgearbeitet und nun ausgewertet. Der
Nutzer hat Option A gewählt. EXP-0009 ist als genau ein getrenntes
synthetisches Evidenzexperiment ausgeführt. Der methodische Nachweis bestand
12/12 Kriterien; zwei kritische False-Same-Befunde qualifizieren die
Produktqualität auf dem verbreiterten Goldstandard jedoch nicht.
GATE-0009 ist nach ausdrücklicher Auswahl von Option A abgeschlossen. Es hält
fest,
dass EPUB-`belongs-to-collection` im aktuellen Produkt als
`work_references` überdehnt wird, primäre und zusätzliche Identifier nicht
getrennt sind und EXP-0009 deshalb noch keine konkrete Produktregel
autorisiert. EXP-0010 ist als genau eine standardgebundene, produktcodefreie
Metadaten- und Oracle-Evidenzwave ausgeführt. Der methodische Nachweis
bestand 12/12, die Produktqualität ist wegen sechs kritischer False Same auf
Ausgabe und Werk jedoch `not_qualified`. GATE-0010 ist nach ausdrücklicher
Nutzerauswahl mit Option A abgeschlossen. WI-0012 ist als enger
False-Same-Guardrail umgesetzt und mit 19/19 synthetischen Kriterien
qualifiziert. Die sechs kritischen False Same sind auf null reduziert; zwei
schwächere `candidate_related`-Werkabweichungen bleiben sichtbar. Der davon
abhängige WI-0011-Calibre-Identitätsweg wurde gegen den neuen Analyzer-
Preimage `97017a2` tatsächlich erneut mit 23/23 Kriterien qualifiziert.
GATE-0011 ist nun als getrenntes Ergebnisgate registriert und
entscheidungsbereit. Es trennt die zwei schwächeren `candidate_related`-
Werkabweichungen von Identifier-Rollen, Collection-Provenienz und fehlender
Publikationsstufe. Eine produktcodefreie Vertrags- und Evidenzwave ist als
kleinste reversible Fortsetzung empfohlen; die Auswahl bleibt offen und es
ist kein Folgeartefakt registriert.

## Vorhanden

- eigenständiges GitHub-Repository und lokale Codex-Projektzuordnung;
- MIT-Lizenz für eigenständig entwickelte SammlungsLotse-Inhalte;
- AI Repository Foundation 1.7.0;
- vollständige semantische 1.7-Upgrade-Bewertung unter
  docs/governance/FOUNDATION_UPGRADE_1_7.md;
- Projektauftrag, Produktgrenzen und Glossar;
- projektbezogene Datenschutz-, Git-, Dokumentations- und
  Wiederverwendungsregeln;
- angenommene Startentscheidungen DEC-0001 bis DEC-0003;
- zentrale Artefaktregistrierung im v2-Profil;
- lokale Registry- und Repository-Prüfwerkzeuge;
- Pull-Request-Workflows für Registry- und Repository-Integrität;
- aktiver Branchschutz für main mit strikt erforderlichen GitHub-Actions-
  Checks repository-quality und registry-integrity;
- registrierter E-Book-Möglichkeitenraum CAP-0002 und vorgeschlagene
  mehrdimensionale Qualitätsanforderung REQ-0001;
- abgeschlossener Erkundungsgegenstand WI-0002 mit RISK-0001, TEST-0001,
  EXP-0001 und GATE-0001;
- auf Dokumentationsebene abgeschlossene B1-Wave WI-0003 mit sechs
  Nutzerentscheidungen, Qualitäts- und Automatisierungsmatrix, Messverträgen
  und asymmetrischen Fehlerkosten;
- vorgeschlagene Anforderung REQ-0002 sowie die abgeschlossenen Versuche
  EXP-0002 bis EXP-0006;
- ausführbarer Testvertrag TEST-0001 mit 26 validierten synthetischen
  `Kern`-Fällen, vier materialisierten `Ausbau`-Fällen und 49 manifestierten
  Komponenten;
- netzwerkloser, ausschließlich auf der Python-Standardbibliothek beruhender
  Generator und read-only Validator für die aktive TEST-0001-Fixture-Version
  `0.3.0`; die unveränderten historischen Snapshots `0.1.0` und `0.2.0`
  bleiben für gebundene Evidenz erhalten;
- empirisch bestandenes EXP-0005-Profil für eine isolierte, unprivilegierte,
  netzwerklose EPUBCheck-Ausführung unter Podman mit wirksamen Datei-,
  Prozess-, Zeit-, Speicher-, CPU-, Output- und Umgebungsgrenzen;
- empirisch bestandenes EXP-0002-Profil für zwei getrennte synthetische
  Calibre-Bibliotheken, minimale pfadbereinigte Feldprojektionen und eine
  Copy-on-read-Grenze bei bytegleichen Quell-Snapshots;
- empirisch bestandenes EXP-0003-Evidenzprofil mit getrennten EPUBCheck- und
  Ace-Rohberichten, verlustfreier Werkzeugprojektion und explizitem manuellem
  Prüfbedarf; das erprobte Ace-Ausführungsprofil ist nicht
  produktqualifiziert;
- empirisch bestandenes EXP-0004-Profil mit fünf getrennten Identitätsebenen,
  positiven, negativen und fehlenden Evidenzkanälen sowie begründeter
  Enthaltung ohne Bestandswirkung;
- empirisch bestandenes EXP-0006-Profil mit elf vorab gebundenen
  Preflight-Zeilen, getrennten Fähigkeits- und Folgeentscheidungen, null
  kritischen Fehlfreigaben und zwei semantisch identischen Wiederholungen
  unter begrenzter netzwerkloser Podman-Ausführung;
- abgeschlossenes GATE-0001 mit angenommener Eingangstriage als eng
  begrenztem ersten read-only E-Book-Vertikalablauf; Bestandsprüfung bleibt
  ein möglicher späterer Ast. Die Auswahl autorisiert für sich weder
  Produktcode noch einen Writer;
- als WI-0004 abgeschlossener lokaler read-only Eingangstriage-Prototyp mit
  In-Memory-Snapshot, flachem Preflight, getrennter Evidenz und sichtbarer
  deutscher oder JSON-CLI-Folgeaktion;
- ausschließlich auf Python 3.12 und Standardbibliothek beruhender,
  paketlos startbarer Produktcode unter `src/sammlungslotse/ebook_intake/`
  und `tools/run_ebook_intake.py`;
- automatisierte Produktverträge und tatsächliche CLI-End-to-End-Abnahme für
  `continue_deep_read_only`, `review`, `stop` und `abstain`; `defer` ist am
  injizierbaren Snapshot-Port deterministisch belegt;
- abgeschlossenes GATE-0002 mit getrenntem Vergleich von Kern-/CLI-Härtung,
  tiefer read-only Adapterfortsetzung und Pausieren;
- abgeschlossenes EXP-0007 mit getrennten Windows- und Linux/Podman-Profilen,
  16/16 erfüllten Kriterien, qualifiziertem Byte-Stream und task-privater
  Materialisierung sowie abgelehntem Original-Locator;
- abgeschlossenes GATE-0003 mit V2 als ausgewählter Standardnaht;
- abgeschlossenes WI-0005 mit EPUBCheck 5.3.0 hinter providerneutralem
  Handoff- und Prozessport, V2-Taskmaterialisierung und Recovery,
  unverändertem vollständigem Rohbericht, explizitem CLI-Opt-in sowie frisch
  gebundenem und 12/12 qualifiziertem Linux/amd64-Podman-Profil;
- reproduzierbar gebaute Image-ID
  `sha256:d8143e59b2c478e0056200a3529b9beb74737885863c22097b198a9c0c92974e`
  mit Temurin-JRE und Build-JDK `21.0.12.1+1`, digestgebundenem Debian-Basisbild
  und getrennten Grenzen für Prozess, Zeit, CPU, RAM, Swap, Input, Netzwerk,
  Umgebung, stdout, stderr und Output;
- aktuelle Primärquellenprüfung für Provider, BSD-3-Clause-Lizenz,
  Wartungsstand, offizielle Releaseprovenienz und Temurin-Laufzeitstand. Das
  EXP-0005-Profil mit Temurin 21.0.12+8 bleibt historische Evidenz und ist
  ausdrücklich kein übernommenes Produktprofil;
- elf aktuelle offene GitHub-Dependabot-Befunde, zehn `high` und einen
  `moderate`, sämtlich im eingefrorenen Ace/npm-Experimentbaum von EXP-0003.
  Sie bestätigen dessen bestehende Nichtqualifikation, werden nicht
  verworfen und betreffen keinen implementierten Produktadapter.
- abgeschlossener Arbeitsgegenstand WI-0006 für einen kleinen read-only
  Mehrdatei-Eingangsbericht über ausschließlich explizit angegebene Dateien;
  schnelle Prüfung bleibt Standard, tiefe EPUBCheck-Prüfung bleibt Opt-in,
  Ein-Datei-Ausgaben bleiben unverändert und Verzeichnissuche, Berichtsdatei,
  Persistenz, Fachsystemzugriff sowie Writes bleiben außerhalb;
- positionsgebundener Batch-Vertrag mit höchstens 32 Eingängen, 256 MiB
  summierten Snapshot-Bytes und 48 MiB UTF-8-Ausgabe, vollständiger
  sequenzieller Verarbeitung innerhalb der Grenzen sowie isolierten
  `internal_error`- und `not_assessed`-Ergebnissen.
- abgeschlossener Arbeitsgegenstand WI-0007 für genau eine ausdrücklich
  angegebene lokale Calibre-Bibliothek, eine unveränderte begrenzte
  Copy-on-read-Arbeitskopie und eine pfadfreie stdout-Projektion auf externe
  Calibre-ID, Titel, Autoren, Sprachen und Formate;
- am 2026-08-28 erneut anhand offizieller Primärquellen bestätigtes Calibre
  9.13.0 mit dokumentierter `calibredb`-Schnittstelle, GPL-3.0-only-Lizenz,
  Artefaktgröße und offiziellem SHA-512-Wert.
- providerneutraler Calibre-Bestandsvertrag, begrenzter Verzeichnissnapshot,
  task-private Copy-on-read-Arbeitskopie, dokumentierter CLI-Adapter und
  getrennte deutsche sowie deterministische JSON-stdout-Oberfläche;
- zweimal reproduzierbar gebaute, exakte Linux/amd64-Image-ID
  `sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5`
  mit netzwerklosem, unprivilegiertem und ressourcenbegrenztem Podman-Profil;
- eingecheckter WI-0007-Produktnachweis mit 17/17 Kriterien aus einer
  ausschließlich synthetischen TEST-0001-Calibre-Bibliothek, byteidentischen
  JSON-Wiederholungen, unverändertem Quellsnapshot sowie vollständigem Task-
  und Container-Cleanup.
- abgeschlossenes GATE-0004 mit getrenntem Vergleich von synthetischer
  Vertrags- und Evidenzhärtung, Mehrbibliothekszugriff und neuer
  Qualitätsfunktion;
- abgeschlossener WI-0008-Vertrag mit eingecheckter, reproduzierbarer
  Drei-Datensatz-Materialisierung, hashgebundenen TEST-0001-Fixtures,
  tatsächlicher Calibre-Normalisierung und v2-Produktnachweis mit 29/29
  Kriterien;
- eng korrigierte und automatisiert gebundene Mehrfachautoren-Projektion für
  die tatsächliche `calibredb --for-machine`-Trennform ` & `, ohne Änderung
  der fünf Produktfelder oder der Einzelbibliotheksgrenze.
- abgeschlossenes GATE-0005 mit getrenntem Vergleich von explizitem
  Zwei-EPUB-Identitätsbericht, Calibre-Bestandsvergleich und neuen Provider-
  oder Mehrbibliotheksflächen;
- abgeschlossener WI-0009-Vertrag für genau zwei ausdrückliche,
  unveränderliche EPUB-Snapshots, fünf getrennte Identitätsebenen, sichtbare
  Enthaltung und ausschließlich pfadfreie stdout-Ausgabe ohne Folgeaktion;
- ausschließlich auf der Python-3.12-Standardbibliothek beruhender lokaler
  EPUB-/OPF-Adapter mit begrenzter In-Memory-Analyse, stabiler deutscher und
  deterministischer JSON-CLI sowie Windows-Reparse-Point-Sperre;
- eingecheckter WI-0009-Produktnachweis mit fünf gebundenen TEST-0001-Paaren,
  je zwei tatsächlichen CLI-Wiederholungen, unveränderten Fixture-Hashes,
  null falschen Gleichheitskandidaten in den Negativfällen und 16/16
  erfüllten Kriterien;
- abgeschlossener WI-0010-Härtungsvertrag mit automatischer Bindung aller
  Intake-Pythonmodule und des Runners, Regressionstest gegen künftige
  Auslassungen, 22 gebundenen Preimage-Dateien und erneutem 12/12-
  Produktnachweis für das unveränderte WI-0005-Profil.
- abgeschlossenes GATE-0006 mit getrenntem Vergleich von
  Einzelrecord-Übergabe, Bestandsqualitätsübersicht, Mehrbibliothekszugriff,
  neuen Provider-/Architekturflächen und Pausieren;
- abgeschlossener EXP-0008-Vertrag mit exakt gebundenem Calibre-9.13.0-
  Profil, zwei bytegleichen positiven Einzelrecord-Wiederholungen,
  getrennten Fail-closed-Negativfällen und vollständigem Cleanup ohne
  Produkt- oder Bestandswirkung.
- abgeschlossenes GATE-0007 mit getrenntem Vergleich von explizitem
  Einzelrecord-Identitätsbericht, Bestandsqualitätsübersicht,
  Mehrbibliotheks-/Routing-Arbeit, neuen Provider-/Architekturflächen und
  Pausieren;
- abgeschlossener WI-0011-Vertrag für genau ein explizites Eingangs-EPUB,
  eine explizite Bibliothek und eine externe Calibre-ID über einen
  providerneutralen read-only Snapshot-Handoff ohne Bestandswirkung;
- getrennte deutsche und deterministische JSON-CLI unter
  `tools/run_ebook_calibre_identity.py`, exakte Calibre-9.13.0-
  Profilbindung und nach WI-0012 gegen Preimage `97017a2` erneuerter
  eingecheckter 23/23-Produktnachweis mit tatsächlichen synthetischen Podman-,
  Grenz-, Recovery- und Cleanupfällen;
- ausgewertetes GATE-0008 mit katalogisierten qualitätssteigernden
  Tätigkeiten, elf weiterhin sichtbaren Fortsetzungsoptionen und der
  ausdrücklichen Auswahl A;
- abgeschlossener EXP-0009-Vertrag für genau 18 synthetische adversarielle
  Identitätspaare, zwei semantisch identische Wiederholungen und 12/12
  methodische Kriterien ohne Produktcode oder Bestandswirkung;
- historischer Qualitätsbefund aus `metadata-collision-work-conflict`: je ein
  kritischer False Same auf Ausgaben- und Werkebene trotz verschiedener
  Inhalte und widersprüchlicher expliziter Werkreferenzen, inzwischen durch
  WI-0012 fail-safe beseitigt, ohne EXP-0009 umzuschreiben;
- abgeschlossenes GATE-0009 mit ausdrücklicher Auswahl der
  standardsgebundenen Evidenzreparatur;
- abgeschlossener EXP-0010-Vertrag für genau zehn synthetische Paare, getrennte
  primäre und zusätzliche Identifier, Collection-Rollen, vorab gebundene
  Publikations-/Ausgaben-/Werkoracles und unabhängige EPUBCheck-Evidenz ohne
  Produktcode oder Bestandswirkung;
- methodisch bestandener EXP-0010-Nachweis mit 16/16 konformen
  EPUBCheck-Einzelpaketen, vier erwartbar abgewiesenen Negativkontrollen, zwei
  semantisch identischen Produktwiederholungen und sechs kritischen False
  Same;
- drei getrennte semantische Fähigkeitslücken: fehlende Publikationsstufe,
  eingeebnete Identifier-Rollen und als `work_references` eingeebnete
  Collection-Semantik;
- abgeschlossenes GATE-0010 mit ausdrücklicher Auswahl des engen
  Fail-safe-Guardrails;
- abgeschlossener WI-0012-Guardrail, der die sechs belegten False Same durch
  eine zusätzliche Repräsentationsbedingung auf null reduziert, ohne
  öffentliches v1-Schema, Metadatenmodell, Publikationsstufe oder
  Collection-Semantik zu erweitern;
- aktueller v2-Produktnachweis mit 19/19 Kriterien, fünf bestehenden
  TEST-0001-Paaren, acht konformen EXP-0010-Qualitätsfällen, je zwei
  byteidentischen JSON-CLI-Wiederholungen, deutscher Ansicht, unveränderten
  Eingängen, pfadfreier Ausgabe und vollständigem Task-Cleanup;
- historische EXP-0009- und EXP-0010-Validatoren, die die unveränderten
  Ergebnisse weiterhin gegen ihre eingefrorenen Git-Preimage-Commits mit je
  12/12 Kriterien prüfen;
- zwei sichtbare verbleibende Werk-Oracledifferenzen mit
  `candidate_related`, die nicht als vollständige Qualifikation der flachen
  Identifier- oder Collection-Semantik dargestellt werden;
- registriertes, entscheidungsbereites GATE-0011 mit sieben getrennten
  Fortsetzungen, Empfehlung A ohne Vorentscheidung und unverändertem
  Produktcode.

## Nicht vorhanden

- allgemeiner Technologie-Stack jenseits der reversiblen WI-0004-Auswahl;
- allgemeines Laufzeit- oder Deploymentkonzept jenseits des eng begrenzten
  WI-0005- und WI-0007-Executors;
- Produktdatenbank oder Suchindex;
- öffentliche REST-, Agent- oder Browser-Schnittstelle sowie eine
  produktqualifizierte allgemeine CLI;
- angenommener Entwicklungsbacklog oder freigegebene technische Roadmap;
- übernommener FolioTone-Code;
- Release.

## Validierung

GATE-0011-Ergebnisgate-Wave: PROJECT_SEMANTIC, bestehende
RUNTIME_EMPIRICAL-Regression und FOUNDATION_INTEGRITY lokal validiert am
2026-08-31 unter Windows und Python 3.12.10. Repository- und v2-Registry-
Prüfung waren für 42 Artefakte erfolgreich. TEST-0001 bestätigte 30 Fälle
und 49 Komponenten; EXP-0002 bis EXP-0007, die historischen EXP-0009- und
EXP-0010-Ergebnisse sowie die eingecheckten WI-0005-, WI-0008-, WI-0011-
und WI-0012-Produktnachweise blieben gültig. Der kontrollierte Testlauf
entdeckte 178 Tests, ersetzte genau zwei veraltete Current-Preimage-
Ergebnisprüfungen eins zu eins durch Historical-Preimage-Prüfungen und
führte 176 Tests erfolgreich aus. `compileall` und `git diff --check` waren
erfolgreich. FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Dies belegt Registrierung, Trennung und Entscheidungsreife
von GATE-0011, nicht die Auswahl oder Ausführung einer Folgewave, ein neues
Metadatenmodell oder eine Produktänderung.

WI-0012-Implementierungswave: PROJECT_SEMANTIC, RUNTIME_EMPIRICAL und
FOUNDATION_INTEGRITY lokal validiert am 2026-08-31 unter Windows, Python
3.12.10, Podman 6.1.0 und Calibre 9.13.0 auf Linux/amd64. Das
commitgebundene Produktpreimage
`97017a2f33b314a6623685a2d07c9638babc0f40` bestand 19/19 Guardrail-
Kriterien mit null kritischen False Same und zwei ausdrücklich sichtbaren
`candidate_related`-Restabweichungen. Der abhängige WI-0011-Weg wurde gegen
denselben Analyzer-Preimage tatsächlich erneut 23/23 qualifiziert; sein
aktueller Nachweis besitzt SHA-256
`8c4120cbcdf21524674a17a906f44226df9194a11c1189dc8bdfad20c47f9b2e`.
Repository- und v2-Registry-Prüfung waren für 41 Artefakte erfolgreich.
TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis EXP-0007 sowie
die historischen EXP-0009- und EXP-0010-Nachweise und die eingecheckten
WI-0005-, WI-0008-, WI-0011- und WI-0012-Produktnachweise blieben gültig. Der
kontrollierte Testlauf entdeckte 177 Tests, ersetzte genau zwei veraltete
Current-Preimage-Ergebnisprüfungen eins zu eins durch Historical-Preimage-
Prüfungen und führte 175 Tests erfolgreich aus. `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY am exakten
Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen,
0 Fehler und 0 Blocker. Dies belegt den engen Guardrail und seine
synthetischen abhängigen Produktwege, nicht ein vollständiges
bibliografisches Identitätsmodell oder reale Häufigkeiten.

GATE-0010-Auswahl- und WI-0012-Planungswave: PROJECT_SEMANTIC, bestehende
RUNTIME_EMPIRICAL-Regression und FOUNDATION_INTEGRITY lokal validiert am
2026-08-31 unter Windows und Python 3.12.10. Repository- und v2-Registry-
Prüfung waren für 41 Artefakte erfolgreich. TEST-0001 bestätigte 30 Fälle
und 49 Komponenten; EXP-0002 bis EXP-0010 sowie die eingecheckten WI-0005-,
WI-0008-, WI-0009- und WI-0011-Nachweise blieben gültig. Alle 173
Repository-Tests, `compileall` und `git diff --check` waren erfolgreich.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Dies belegt Auswahl, Registrierung und Begrenzung von WI-0012,
nicht die noch ausstehende Guardrail-Implementierung oder Produktqualität.

EXP-0010-Ausführungs- und GATE-0010-Ergebniswave: RUNTIME_EMPIRICAL,
PROJECT_SEMANTIC und FOUNDATION_INTEGRITY lokal validiert am 2026-08-28 unter
Windows und Python 3.12.10. Der eingefrorene Preimage-Commit
`fbb481b4e5f869943c0a668502d37e867b2db5ce` erfüllte 12/12 methodische
Kriterien: 16 konforme Einzelpakete bestanden EPUBCheck 5.3.0, vier
absichtlich ungültige Kontrollen wurden erwartbar abgewiesen und zwei
Produktwiederholungen waren semantisch identisch. Sechs kritische False Same
und drei getrennte Fähigkeitslücken ergeben `not_qualified` für die
Produktqualität. Repository- und v2-Registry-Prüfung waren für 40 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0010 sowie die eingecheckten WI-0005-, WI-0008-, WI-0009- und WI-0011-
Nachweise blieben gültig. Alle 173 Repository-Tests, `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY am exakten
Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen,
0 Fehler und 0 Blocker. Dies belegt den synthetischen EXP-0010-Befund und
den offenen Entscheidungsraum, nicht reale Häufigkeiten oder eine
Produktkorrektur.

GATE-0009-Auswahl- und EXP-0010-Planungswave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Windows und
Python 3.12.10. Repository- und v2-Registry-Prüfung waren für 39 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0009 sowie die eingecheckten WI-0005-, WI-0008-, WI-0009- und WI-0011-
Nachweise blieben gültig. Alle 165 Repository-Tests, `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY meldete 0
Warnungen, 0 Fehler und 0 Blocker. Dies belegt Auswahl, Registrierung und
Begrenzung des EXP-0010-Vertrags, nicht die noch ausstehende Ausführung oder
eine Produktkorrektur.

GATE-0009-Ergebnisgate-Wave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Windows und
Python 3.12.10. Repository- und v2-Registry-Prüfung waren für 38 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0009 sowie die eingecheckten WI-0005-, WI-0008-, WI-0009- und WI-0011-
Nachweise blieben gültig. Alle 165 Repository-Tests, `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY meldete 0
Warnungen, 0 Fehler und 0 Blocker. Dies belegt den getrennten
Entscheidungsraum und seine Primärquellenbindung, nicht die Auswahl einer
Folgewave oder eine Produktkorrektur.

EXP-0009-Ausführungswave: RUNTIME_EMPIRICAL und PROJECT_SEMANTIC lokal
validiert am 2026-08-28 unter Windows und Python 3.12.10. Der eingefrorene
Preimage-Commit `2ef2de0395e485283f3be4ca339ab5fed8657fee` führte genau 18
synthetische Paare zweimal aus. Der Ergebnisvertrag bestand 12/12 methodische
Kriterien; beide semantischen Wiederholungsdigests waren identisch. Drei
Negativfälle endeten erwartbar `not_assessed`, alle Eingänge blieben
unverändert und die Run-Wurzel wurde vollständig entfernt. Die getrennte
Produktbewertung lautet wegen zweier kritischer False Same
`not_qualified`. Repository- und v2-Registry-Prüfung waren für 37 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0009 sowie die eingecheckten WI-0005-, WI-0008-, WI-0009- und WI-0011-
Nachweise blieben gültig. Alle 165 Repository-Tests, `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY meldete 0
Warnungen, 0 Fehler und 0 Blocker. Dies belegt Methode und synthetische
Befunde, nicht reale Häufigkeiten oder eine Produktkorrektur.

GATE-0008-Auswahl- und EXP-0009-Planungswave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Windows und
Python 3.12.10. Repository- und v2-Registry-Prüfung waren für 37 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0008 sowie die eingecheckten WI-0005-, WI-0008-, WI-0009- und WI-0011-
Nachweise blieben gültig. Alle 159 Repository-Tests und `compileall` waren
erfolgreich; `git diff --check` meldete keine Fehler. FOUNDATION_INTEGRITY
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies belegt Auswahl,
Registrierung und Begrenzung des EXP-0009-Vertrags sowie die unveränderte
Bestandsregression, nicht die noch ausstehende Experimentausführung oder eine
Produktqualifikation.

GATE-0008-Brainstormingwave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Windows und
Python 3.12.10. Repository- und v2-Registry-Prüfung waren für 36 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0008 sowie die eingecheckten WI-0005-, WI-0008-, WI-0009- und WI-0011-
Nachweise blieben gültig. Alle 159 Repository-Tests und `compileall` waren
erfolgreich; `git diff --check` meldete keine Fehler. FOUNDATION_INTEGRITY
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies belegt den offenen
Optionsraum, seine Registrierung und die unveränderte Bestandsregression,
nicht die Auswahl oder Qualifikation einer Folge-Wave.

WI-0011-Implementierungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal
validiert am 2026-08-28 unter Windows, Python 3.12.10, Podman 6.1.0 und
Calibre 9.13.0 auf Linux/amd64. Das vor der tatsächlichen Ausführung
eingefrorene Produktpreimage
`d70c6decb50f4560e52f64b4eef66fc8f4e76af2` bestand 23/23 Kriterien. Zwei
positive JSON-Wiederholungen waren byteidentisch; der exportierte Record-
Snapshot blieb mit SHA-256
`1d98510717f6c3f22b3219bdedf8cbdf38785f060bfca0522f66ccf374f684a5`
bytegleich. Repackaging ergab `representation_candidate`, der fachliche
Negativfall ohne falsche Gleichheitsfreigabe `abstain`. Fehlende und
formatlose Datensätze, ungültige und mehrere IDs, Größenüberschreitung,
unerwartete Ausgabe, Outputlimit, Timeout und simulierte Unterbrechung
endeten fail-closed; Recovery und vollständiges Cleanup waren erfolgreich.
22 pfadfreie Rohbelege liegen außerhalb von Git. Repository- und v2-
Registry-Prüfung waren für 35 Artefakte erfolgreich; alle bestehenden
EXP-0002-bis-EXP-0008- und WI-0005-, WI-0008-, WI-0009-Nachweise blieben
gültig. Alle 159 Repository-Tests und `compileall` waren erfolgreich;
`git diff --check` meldete keine Fehler. FOUNDATION_INTEGRITY meldete 0
Warnungen, 0 Fehler und 0 Blocker. PR #40 wurde mit geprüftem Head
`56efcd9fe322b12f3d39df9dffdbdbc67eaead3d` regulär gemergt. Der
Merge-Commit `44093ace0b9716780bc9ea6d09166655edf67d3d` besitzt exakt die vorige
Main-Basis und den PR-Head als Eltern; Merge- und Headbaum sind gleich. Der
Post-Merge-Lauf `33154832441` auf exakt diesem `origin/main` war erfolgreich.

GATE-0007-/WI-0011-Planungswave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Windows und
Python 3.12.10. Repository- und v2-Registry-Prüfung waren für 35 Artefakte
erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis
EXP-0008 sowie die eingecheckten WI-0005-, WI-0008- und WI-0009-Nachweise
blieben gültig. Alle 145 Repository-Tests und `compileall` waren erfolgreich;
`git diff --check` meldete keine Fehler. FOUNDATION_INTEGRITY meldete 0
Warnungen, 0 Fehler und 0 Blocker. Dies belegt Planung, Registry, Dokumente
und bestehende Regression, nicht die noch ausstehende WI-0011-Implementierung
oder Produktqualifikation.

EXP-0008-Ausführungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal
validiert am 2026-08-28 unter Windows, Python 3.12.10, Podman 6.1.0 und
Calibre 9.13.0 auf Linux/amd64. Das gebundene Preimage `fb08732b` erzeugte
zwei bytegleiche positive Einzelrecord-EPUB-Übergaben und bestand nach
vollständiger Neuausführung 16/16 Kriterien. Fehlende oder formatlose
Datensätze, mehrere und ungültige IDs, unerwartete Ausgabe, Outputlimit,
Timeout und simulierte Unterbrechung endeten fail-closed; Recovery, Quell-
und Fixture-Unverändertheit sowie vollständiges Task- und Container-Cleanup
waren erfolgreich. Ein erster 15/16-Lauf wurde wegen ausschließlich
labelabhängiger Rohbeleg-Schlüssel verworfen; die Normalisierung erhielt vor
dem vollständigen Wiederholungslauf einen eigenen Regressionstest.
Repository- und v2-Registry-Prüfung waren für 33 Artefakte erfolgreich.
TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis EXP-0008 sowie
die eingecheckten WI-0005-, WI-0008- und WI-0009-Nachweise waren gültig. Alle
145 Repository-Tests und `compileall` waren erfolgreich; `git diff --check`
meldete keine Fehler. FOUNDATION_INTEGRITY meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies qualifiziert nur die synthetische technische Übergabenaht,
nicht einen Calibre-Vergleich oder eine Produktfunktion.

GATE-0006-/EXP-0008-Planungswave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Windows,
Python 3.12.10 und Podman 6.1.0. Repository- und v2-Registry-Prüfung waren für
33 registrierte Artefakte erfolgreich. TEST-0001 bestätigte 30 Fälle und 49
Komponenten; EXP-0002 bis EXP-0007 sowie die eingecheckten WI-0005-, WI-0008-
und WI-0009-Nachweise blieben gültig. Alle 136 Repository-Tests und
`compileall` waren erfolgreich; `git diff --check` meldete keine Fehler.
FOUNDATION_INTEGRITY meldete 0 Warnungen, 0 Fehler und 0 Blocker. Eine
nicht eingecheckte Auswahlprobe mit der exakten Calibre-Image-ID exportierte
Datensatz `1` über die unterstützte CLI als bytegleiches EPUB und hinterließ
keine Container oder aktiven Probeverzeichnisse. Sie begründet nur die
Auswahl; die EXP-0008-Ausführung und Qualifikation sind noch nicht erfolgt.

WI-0010-Härtungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert
am 2026-08-28 unter Windows, Python 3.12.10 und Podman 6.1.0 mit Linux/amd64.
Das WI-0005-Preimage bindet nun automatisch alle Intake-Pythonmodule, das
Paket-Initialisierungsmodul und den Runner; der neue Regressionstest erfasst
künftige ungebundene Module. Eine frische tatsächliche Podman-Qualifikation
mit der unveränderten Image-ID bestand 12/12 Kriterien und band 22 Dateien.
Getrennte aktive Proben belegten `NetworkMode=none`, die PID-Grenze 32,
384 MiB RAM ohne zusätzlichen Swap, eine CPU, Abbruch- und Recovery-Cleanup
sowie den Eingang-Grenzfall 32 MiB plus ein Byte. Zwei parallele tiefe Läufe
blieben voneinander isoliert und räumten vollständig auf, endeten unter
gemeinsamer Last jedoch beide fail-closed als `not_assessed`; Parallelbetrieb
ist weiterhin nicht qualifiziert. Repository- und v2-Registry-Prüfung waren
für 31 Artefakte erfolgreich. TEST-0001, EXP-0002 bis EXP-0007, WI-0005,
WI-0008 und WI-0009 waren gültig; alle 136 Repository-Tests und `compileall`
waren erfolgreich, `git diff --check` meldete keine Fehler. Die Wave ändert
keine Produktfunktion, CLI, Provider-, Image-, Executor- oder Ressourcengrenze.

WI-0009-Implementierungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal
validiert am 2026-08-28 unter Python 3.12.10. Fünf gebundene synthetische
Paare wurden je zweimal über den tatsächlichen JSON-CLI-Prozess sowie einmal
über die deutsche Ansicht ausgeführt. Der eingecheckte Produktnachweis
bestand 16/16 Kriterien für Bytegleichheit, Neuverpackung, Titelkollision,
Übersetzung, Leseprobe/Vollausgabe, Ebenentrennung, Evidenzkanäle,
Determinismus, Pfadfreiheit und unveränderte Eingänge. Alle 135 Repository-
Tests waren erfolgreich. Die vollständigen Registry-, Fixture-, EXP-0002-
bis EXP-0007-, WI-0005-, WI-0008-, `compileall`, `git diff --check`- und
Foundation-Prüfungen waren ebenfalls erfolgreich. Dies qualifiziert nur den
engen synthetischen Zwei-EPUB-Bericht, nicht reale Bestände, statistische
Genauigkeit, Calibre-Abgleich, automatische Suche, Persistenz oder Writes.

GATE-0005-/WI-0009-Planungswave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Python
3.12.10. Repository- und v2-Registry-Prüfung waren für 30 registrierte
Artefakte erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten;
EXP-0002 bis EXP-0007 sowie die eingecheckten WI-0005- und WI-0008-
Produktnachweise bestätigten unverändert ihre gebundenen Kriterien. Alle 123
Repository-Tests und `compileall` waren erfolgreich; `git diff --check`
meldete keine Fehler. FOUNDATION_INTEGRITY meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt Plan-, Registry-, Dokument-, Fixture- und bestehende
Regressionsintegrität, nicht die noch ausstehende WI-0009-Implementierung
oder einen produktqualifizierten Identitätsvergleich.

WI-0008-Implementierungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal
validiert am 2026-08-28 unter Python 3.12.10, Podman 6.1.0 und Calibre 9.13.0.
Der eingecheckte Materialisierer erzeugte zweimal frisch drei synthetische
Datensätze aus drei hashgebundenen TEST-0001-Fixtures. Die fachlichen
Projektionen waren identisch und deckten Mehrfachautoren, Mehrsprachigkeit,
Mehrformat, leere Werte und Unicode ab. Der erste Lauf reproduzierte die
tatsächliche `calibredb --for-machine`-Autorentrennung; die eng begrenzte
Parserkorrektur ist durch einen fokussierten Regressionstest gebunden. Der
endgültige LF-gebundene v2-Produktnachweis bestand 29/29 Kriterien mit
byteidentischen JSON-Wiederholungen, deutscher Ansicht, unveränderten
Fixtures und Bibliotheken sowie vollständigem Task-, Qualifikationsroot- und
Container-Cleanup einschließlich Timeout, Outputgrenze und simuliertem
Abbruch. Repository- und v2-Registry-Prüfung waren für 28 Artefakte
erfolgreich; TEST-0001 bestätigte 30 Fälle und 49 Komponenten, EXP-0002 bis
EXP-0007 sowie WI-0005 blieben gültig. Alle 123 Repository-Tests und
`compileall` waren erfolgreich; `git diff --check` meldete keine Fehler.
FOUNDATION_INTEGRITY meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies
qualifiziert die reproduzierbare synthetische Vertragsabdeckung und die
Mehrfachautorenkorrektur, nicht reale Bestände, Last, mehrere Bibliotheken,
neue Felder oder Writes.

GATE-0004-/WI-0008-Planungswave: PROJECT_SEMANTIC und bestehende
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-28 unter Python
3.12.10. Repository- und v2-Registry-Prüfung waren für 28 registrierte
Artefakte erfolgreich. TEST-0001 bestätigte 30 Fälle und 49 Komponenten;
EXP-0002 bis EXP-0007 sowie die eingecheckten WI-0005- und WI-0007-
Produktnachweise bestätigten unverändert ihre gebundenen Kriterien. Alle 117
Repository-Tests und `compileall` waren erfolgreich; `git diff --check`
meldete keine Fehler. FOUNDATION_INTEGRITY meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt Plan-, Registry-, Dokument-, Fixture- und bestehende
Regressionsintegrität, nicht die noch ausstehende WI-0008-Implementierung
oder eine erweiterte tatsächliche Calibre-Qualifikation.

WI-0007-Implementierungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal
validiert am 2026-08-28 unter Python 3.12.10, Podman 6.1.0 und Calibre 9.13.0.
18 neue fokussierte Produktverträge prüfen Profilbindung, Snapshot- und
Copy-on-read-Grenzen, Symlinks, Datei-, Summen- und Pfadlimits, minimale
Projektion, Determinismus, Pfadbereinigung, Quelländerung, ungültige oder
unverifizierte Providerergebnisse, Fehlerzustände, Recovery und Cleanup.
Zwei frische Image-Builds erzeugten dieselbe gebundene Image-ID. Eine echte
deutsche und zwei echte JSON-CLI-Ausführungen gegen eine aus TEST-0001
erzeugte synthetische Calibre-Bibliothek waren erfolgreich; die JSON-Ausgaben
waren byteidentisch, Quelle, Task-Root und Containerbestand blieben sauber.
Der eingecheckte Produktnachweis bestand 17/17 Kriterien, darunter tatsächlicher
Timeout und tatsächliche Rohoutput-Grenze mit vollständigem Cleanup. Die vollständige
Repository-Regression umfasst 117 erfolgreiche Tests. Registry-, Fixture-,
EXP-0002- bis EXP-0007-, WI-0005-, WI-0007-, `compileall`-,
`git diff --check`- und Foundation-Prüfungen waren erfolgreich. Dies
qualifiziert genau die lokale Einzelbibliotheksprojektion, nicht reale
Bestände, Mehrfachziele, automatische Erkennung, Serverzugriff, Persistenz
oder Writes.

WI-0007-Planungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert
am 2026-08-28 unter Python 3.12.10 und Podman 6.1.0. Repository- und
v2-Registry-Prüfung waren für 26 registrierte Artefakte erfolgreich.
TEST-0001 bestätigte 30 Fälle und 49 Komponenten; EXP-0002 bis EXP-0007 sowie
der eingecheckte WI-0005-Produktnachweis bestätigten unverändert ihre
gebundenen Kriterien. Alle 99 Repository-Tests und `compileall` waren
erfolgreich; `git diff --check` meldete keine Fehler. FOUNDATION_INTEGRITY
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies belegt Plan-, Registry-,
Dokument-, Fixture- und bestehende Regressionsintegrität, nicht die noch
ausstehende WI-0007-Implementierung oder eine Calibre-Produktqualifikation.

WI-0006-Implementierungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal
validiert am 2026-08-27 unter Python 3.12.10, Podman 6.1.0 und EPUBCheck
5.3.0. Siebzehn neue fokussierte Batch-Verträge und alle 99 Repository-Tests
waren erfolgreich. Tatsächliche deutsche und JSON-CLI-Prozesse belegten
vollständige Verarbeitung, alle fünf Folgeaktionen, Pfadbereinigung,
Determinismus, Grenzen und unveränderte Eingänge. Eine tatsächliche tiefe
Zwei-Dateien-Abnahme prüfte ein valides EPUB 2 und ein mehrsprachiges
RTL-EPUB: Beide getrennten Providerläufe endeten ohne EPUBCheck-
Konformitätsbefund, mit vollständigem Task- und Container-Cleanup. TEST-0001
bestätigte danach erneut 30 Fälle, 49 Komponenten und unveränderte Eingänge.
Die wegen der CLI-Preimage-Änderung erforderliche vollständige WI-0005-
Neuqualifikation bestand erneut 12/12 Kriterien mit dem exakten CLI-Hash
`493840b8f5ad2f2f97c0e7e605de25386ef3602936c5719b826cbc91e6e73b7a`.
Repository-, Registry-, EXP-0002- bis EXP-0007- und WI-0005-Verträge,
`compileall` und `git diff --check` waren auf dem vollständigen Wave-Stand
erfolgreich. FOUNDATION_INTEGRITY meldete 0 Warnungen, 0 Fehler und 0
Blocker. Dies qualifiziert den kleinen lokalen Mehrdatei-Bericht, nicht
Verzeichnissuche, reale private Medien, allgemeine Batch-Infrastruktur,
Persistenz, Fachsysteme oder Writes.

TEST-0001-Ausbau-Wave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert
am 2026-08-27 unter Python 3.12.10, Podman 6.1.0 und EPUBCheck 5.3.0. Der
Fixture-Validator bestätigte Version `0.3.0` mit 30 Fällen und 49
Komponenten, vollständigen Hash- und Herkunftsangaben, bytegenauer
Regeneration, unveränderten Eingängen und null aufgeschobenen Ausbau-Fällen.
Die neuen Oracles prüfen EPUB 2 mit NCX, EPUB 3 Fixed Layout, mehrsprachigen
RTL-Inhalt und Routing ohne passende Regel. Tatsächliche tiefe Läufe über die
drei validen EPUBs endeten ohne EPUBCheck-Konformitätsbefund und mit
vollständigem Cleanup. Ein erster Fixed-Layout-Lauf erreichte fail-closed das
Executor-Timeout und räumte vollständig auf; die unmittelbare Wiederholung
bestand. Alle bestehenden EXP- und WI-0005-Ergebnisverträge bleiben
unverändert an Version `0.2.0` gebunden. Der netzwerkabhängige aktuelle
`npm audit` reproduzierte für den eingefrorenen EXP-0003-Ace-Baum 22
Befundpakete, 14 `high` und acht `moderate`; der von npm vorgeschlagene
Downgrade von Ace 1.4.6 auf 1.2.5 ist kein sicherer Aktualisierungspfad.
Repository- und v2-Registry-Prüfung, alle eingecheckten EXP-0002- bis
EXP-0007- sowie WI-0005-Ergebnisverträge, alle 82 Repository-Tests,
`compileall`, `git diff --check` und FOUNDATION_INTEGRITY mit 0 Warnungen,
0 Fehlern und 0 Blockern waren erfolgreich. Eine frische tatsächliche
WI-0005-Podman-Qualifikation bestand erneut 12/12 Kriterien mit der exakt
gebundenen Image-ID und null verbleibenden Containern. Die offiziellen
Projektquellen führen weiterhin EPUBCheck 5.3.0, Ace 1.4.6, Temurin
21.0.12.1+1 und Podman 6.1.0 als aktuelle Releases.

WI-0005-Implementierungswave: RUNTIME_EMPIRICAL lokal validiert am
2026-08-27 unter Python 3.12.10 und Podman 6.1.0 für das exakte Profil
`wi-0005-epubcheck-5.3.0-temurin-21.0.12.1+1-podman-linux-amd64/v1`.
Zwei frische Builds aus den größen- und SHA-256-gebundenen EPUBCheck-,
Temurin-JRE-, Temurin-JDK- und Debian-Eingängen erzeugten dieselbe erwartete
Image-ID. Die tatsächliche Produktqualifikation bestand 12/12 Kriterien:
unveränderter Standardweg, Opt-in-Erfolg, realer `RSC-001`-Befund,
geschlossenes Gate, `not_assessed`, effektive Prestart-Isolation,
Outputgrenze, Timeout, Originalunverändertheit sowie vollständiges
Container- und Task-Cleanup. Ausschließlich drei TEST-0001-Medien wurden
verwendet; ihre SHA-256-Werte blieben unverändert. PROJECT_SEMANTIC,
Registry-, Fixture- und eingecheckte Ergebnisverträge, alle 82 synthetischen
Repository-Tests, `compileall` und `git diff --check` wurden lokal
erfolgreich ausgeführt. Dies belegt nur den eng gebundenen EPUBCheck-Adapter,
nicht Gesamtqualität, Accessibility, allgemeine Container-, Deployment- oder
Writer-Fähigkeit.

WI-0005-Bewertungswave: aktuelle offizielle Primärquellen für EPUBCheck,
Lizenz, Repositorypflege, veröffentlichte Repository-Advisories, Temurin-LTS
und Podman-Laufzeitgrenzen am 2026-08-27 geprüft. EPUBCheck 5.3.0 ist
weiterhin das aktuelle produktionsreife Release; dessen offizieller
Artefakt-SHA-256 stimmt mit der vorhandenen EXP-0005-Provenienz überein. Die
offizielle Adoptium-Releasequelle führt inzwischen Temurin
`jdk-21.0.12.1+1`; das EXP-0005-Preimage `21.0.12+8` wurde daher nicht als
Produktlaufzeit übernommen. PROJECT_SEMANTIC und vollständige
RUNTIME_EMPIRICAL-Regression wurden lokal validiert: Repository- und
v2-Registry-Prüfung waren für 24 registrierte Artefakte erfolgreich,
TEST-0001 bestätigte 26 Fälle und 44 Komponenten, EXP-0002 bis EXP-0007
bestätigten 13/13, 14/14, 15/15, 11/11, 16/16 und 16/16 Kriterien. Alle 63
synthetischen Repository-Tests, `compileall` und `git diff --check` waren
erfolgreich. Der Produktcode blieb unverändert. Dies belegt aktuelle
Quellenauswertung einschließlich der Zuordnung aller elf beim PR-Push
gemeldeten Dependabot-Befunde zum eingefrorenen EXP-0003-Ace-Baum,
Entscheidungs-, Registry-, Dokument-, Fixture- und Regressionsintegrität,
nicht einen implementierten oder produktqualifizierten Adapter.

EXP-0007-Ausführungs- und GATE-0003-Wave: PROJECT_SEMANTIC und vollständige
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-27. Repository- und
v2-Registry-Prüfung waren für 24 registrierte Artefakte erfolgreich.
TEST-0001 bestätigte 26 Fälle und 44 Komponenten; EXP-0002 bis EXP-0007
bestätigten 13/13, 14/14, 15/15, 11/11, 16/16 und 16/16 Kriterien. Alle 63
synthetischen Repository-Tests, `compileall` und `git diff --check` waren
erfolgreich. Der Produktcode blieb unverändert. Dies belegt Experiment-,
Gate-, Registry-, Dokument-, Fixture- und Regressionsintegrität, nicht die
Annahme oder Implementierung von WI-0005 und nicht Produktreife.

EXP-0007 und GATE-0003: RUNTIME_EMPIRICAL am 2026-08-27 unter Python 3.12.10
auf Windows und Podman 6.1.0 auf Linux/amd64 ausgeführt. Je Plattform
bestanden zwölf positive Prozessläufe über zwei synthetische Snapshots, drei
Varianten und zwei Wiederholungen; insgesamt waren alle 16 Akzeptanzkriterien
erfüllt. V1 und V2 sind `QUALIFIED`, V3 ist `REJECTED`. Unfreigegebene,
instabile, hashabweichende und übergroße Eingänge starteten keinen Prozess;
Snapshot-, Original-, Output-, Timeout-, Kindprozess-, Temp-, Crashrest- und
Containergrenzen waren wirksam. Die optionale V2-Kompatibilitätswiederholung
gegen das bereits gebundene lokale EPUBCheck-5.3.0-Profil war für beide
synthetischen Eingänge qualifiziert. Der Nachweis qualifiziert die
Übergabenaht, nicht Produktadapter, Providerwahl, reale Medien oder
Produktreife. Ein erster nicht gewerteter Lauf deckte eine Windows-Cleanup-
Lücke im optionalen Kompatibilitätsschritt auf; nach Korrektur und neuem
Preimage wurden beide Plattformen und die Kompatibilität vollständig neu
ausgeführt.

GATE-0002-/EXP-0007-Planungswave: PROJECT_SEMANTIC und
RUNTIME_EMPIRICAL-Regression lokal validiert am 2026-08-27 unter Python
3.12.10. Repository- und v2-Registry-Prüfung waren für 23 registrierte
Artefakte erfolgreich. TEST-0001 bestätigte 26 Fälle und 44 Komponenten;
EXP-0002 bis EXP-0006 bestätigten 13/13, 14/14, 15/15, 11/11 und 16/16
Kriterien. Alle 57 synthetischen Repository-Tests, `compileall` und
`git diff --check` waren erfolgreich. Der Produktcode blieb unverändert.
Dies belegt Entscheidungs-, Registry-, Dokument-, Fixture- und vorhandene
Ergebnisintegrität, nicht die noch ausstehende Ausführung von EXP-0007, eine
qualifizierte Übergabeform oder Produktreife.

WI-0004-Implementierungswave: PROJECT_SEMANTIC, RUNTIME_EMPIRICAL und die
sichtbare CLI-Abnahme lokal validiert am 2026-08-27 unter Python 3.12.10.
Repository- und v2-Registry-Prüfung waren für 20 registrierte Artefakte
erfolgreich. TEST-0001 bestätigte 26 Fälle und 44 Komponenten; EXP-0002 bis
EXP-0006 bestätigten 13/13, 14/14, 15/15, 11/11 und 16/16 Kriterien. Alle 54
synthetischen Repository-Tests, davon 25 fokussierte Produkttests,
`compileall` und `git diff --check` waren erfolgreich. Getrennte tatsächliche
CLI-Prozesse zeigten `continue_deep_read_only`, `review`, `stop` und
`abstain`; zwei stabile JSON-Läufe waren byteidentisch. Die vier
Eingabehashes und das vollständige Arbeitsbaum-Dateiinventar blieben vor und
nach der Abnahme unverändert. Dies qualifiziert nur den lokalen
synthetischen WI-0004-Prototyp, nicht reale Medien, tiefe Formatqualität,
Produktreife oder einen allgemeinen Stack.

WI-0004-Planungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL-Regression lokal
validiert am 2026-08-27 unter Python 3.12.10. Repository- und
v2-Registry-Prüfung waren für 20 registrierte Artefakte erfolgreich.
TEST-0001 bestätigte 26 Fälle und 44 Komponenten; die eingecheckten
Ergebnisverträge von EXP-0002 bis EXP-0006 bestätigten 13/13, 14/14, 15/15,
11/11 und 16/16 Kriterien. 29 synthetische Unit-Tests, `compileall` und
`git diff --check` waren erfolgreich. Dies belegt Plan-, Registry-, Dokument-,
Fixture- und vorhandene Ergebnisintegrität, nicht die noch ausstehende
WI-0004-Implementierung oder Produktreife.

GATE-0001-Neubewertung: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL-Regression
lokal validiert am 2026-08-27 unter Python 3.12.10. Repository- und
v2-Registry-Prüfung waren für 19 registrierte Artefakte erfolgreich.
TEST-0001 bestätigte 26 Fälle und 44 Komponenten; die eingecheckten
Ergebnisverträge von EXP-0002 bis EXP-0006 bestätigten 13/13, 14/14, 15/15,
11/11 und 16/16 Kriterien. 29 synthetische Unit-Tests, `compileall` und
`git diff --check` waren erfolgreich. Die LF-Bindung für `Containerfile`
hält den in EXP-0006 versionierten Containerdefinitionshash auch im
Windows-Worktree bytegleich. Diese Prüfungen belegen Dokument-, Link-,
Registry-, Fixture- und vorhandene Ergebnisintegrität, nicht Produktreife;
kein Containerexperiment wurde in dieser Planungs-Wave erneut ausgeführt.

EXP-0006-Ausführungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL-Regression
lokal validiert am 2026-08-27. Repository- und v2-Registry-Prüfung waren für
19 registrierte Artefakte erfolgreich. TEST-0001 bestätigte unverändert 26
Fälle und 44 Komponenten; die eingecheckten Ergebnisverträge von EXP-0002
bis EXP-0006 bestätigten 13/13, 14/14, 15/15, 11/11 und 16/16 Kriterien. 29
synthetische Unit-Tests, `compileall` und `git diff --check` waren
erfolgreich. Dies belegt Registry-, Dokument-, Link-, Fixture-, Ergebnis- und
Regressionsintegrität, nicht Produktreife. Die Gate-Entscheidung selbst folgt
aus der getrennten fachlichen Neubewertung, nicht aus der Anzahl erfolgreicher
Prüfungen.

EXP-0006: RUNTIME_EMPIRICAL lokal validiert am 2026-08-27 unter Podman 6.1.0
mit Linux/amd64. Sechzehn Akzeptanzprüfungen und alle elf vorab gebundenen
Matrixzeilen waren erfolgreich. Acht Fälle blieben außerhalb des tiefen
Werkzeugwegs, drei positiv gegatete Kontrollen starteten ihn, kritische
Fehlfreigaben betrugen null und beide Wiederholungen erzeugten den
identischen semantischen Digest
`e14077d5cb783052cd79b309c60d3ae709f363523597e735be087a79a66b4ba4`.
Eingabehashes blieben unverändert; Netzwerkzugriff, Original- und
Fachsystemschreibwirkungen waren null. Read-only Root und Fixture,
unprivilegierte UID, Capability-Entzug, `no-new-privileges`, PID-, CPU-, RAM-,
Zeit-, tmpfs-, Umgebungs- und Ausgabegrenzen wurden protokolliert und erfüllt.
Das Ergebnis qualifiziert nur den kleinen synthetischen Preflight, nicht
Produktparser oder Produktlaufzeit. EXP-0006 entscheidet GATE-0001 nicht
selbst, sondern liefert Evidenz für dessen getrennte Neubewertung.

EXP-0006-Vertragswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL-Regression lokal
validiert am 2026-08-27. Repository- und v2-Registry-Prüfung waren für 19
registrierte Artefakte erfolgreich. TEST-0001 bestätigte unverändert 26 Fälle
und 44 Komponenten; die eingecheckten Ergebnisverträge von EXP-0002 bis
EXP-0005 bestätigten 13/13, 14/14, 15/15 und 11/11 Kriterien. 24 synthetische
Unit-Tests, `compileall` und `git diff --check` waren erfolgreich. Dies belegt
Registrierung, Dokument-, Link-, Registry- und Regressionsintegrität, nicht
die noch ausstehende Implementierung oder Ausführung von EXP-0006.

GATE-0001-Vergleich: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert
am 2026-08-27. Repository- und v2-Registry-Prüfung waren für 18 registrierte
Artefakte erfolgreich. TEST-0001 bestätigte 26 Fälle und 44 Komponenten; die
eingecheckten Ergebnisverträge von EXP-0002 bis EXP-0005 bestätigten 13/13,
14/14, 15/15 und 11/11 Kriterien. 24 synthetische Unit-Tests, `compileall`
und `git diff --check` waren erfolgreich. Diese Prüfungen belegen
Dokument-, Link-, Registry- und vorhandene Ergebnisintegrität, nicht die
fachliche Güte eines noch nicht ausgeführten vollständigen Vertikalablaufs.

EXP-0004: RUNTIME_EMPIRICAL lokal validiert am 2026-08-27 unter Python
3.12.10. Fünfzehn Akzeptanzprüfungen waren erfolgreich. Sechs synthetische
TEST-0001-Sollpaare wurden in zwei semantisch identischen Wiederholungen auf
Byte-, Paket-, Repräsentations-, Ausgaben- und Werkebene bewertet. Precision,
Recall und selektive Genauigkeit betrugen auf diesem kleinen gezielten
Goldstandard je Ebene 1,0, ohne False Positives. Die Ausgabenabdeckung blieb
bewusst bei 5/6: Leseprobe und Vollausgabe führten auf Ausgabenebene zur
korrekten Enthaltung. Alle Kandidaten zeigen positive und negative Evidenz;
fehlende Evidenz blieb separat, Eingaben blieben unverändert und beobachtete
Schreibwirkungen waren null. Die perfekten synthetischen Werte sind keine
Produktprognose und qualifizieren weder Produktmodell noch Stack oder Writer.

EXP-0003: RUNTIME_EMPIRICAL lokal validiert am 2026-08-27 unter Podman 6.1.0.
Vierzehn Akzeptanzprüfungen waren über sieben synthetische TEST-0001-Fälle
und jeweils zwei Wiederholungen erfolgreich. EPUBCheck 5.3.0 lieferte für
die Fehlerfälle die Originalcodes `RSC-001`, `RSC-007`, `OPF-014` und
`RSC-006`; der unbekannte Code `RSC-006` blieb unverändert, unklassifiziert
und prüfpflichtig. Ace 1.4.6 lieferte seine Rohbefunde getrennt; der manuelle
Prüfbedarf stammt ausschließlich aus dem TEST-0001-Oracle. Semantische
Wiederholungsdigests waren identisch, Eingabehashes blieben unverändert und
vollständige Maschinenberichte liegen nur im nicht versionierten
Artefaktbereich, während `result.json` deren Hashes festhält. Das strikt
begrenzte, netzwerklose Podman-Profil ist lediglich Experimentnachweis:
Ace startet Chromium mit deaktivierter Sandbox, und der eingefrorene
Abhängigkeitsbaum weist 22 bekannte npm-Befunde aus. Damit ist dieses
Ace-Profil ausdrücklich nicht produktqualifiziert und keine Stackentscheidung.

EXP-0002: RUNTIME_EMPIRICAL lokal validiert am 2026-08-27 unter Podman 6.1.0
mit Linux/amd64. Calibre 9.13.0 wurde aus dem SHA-512-geprüften offiziellen
Release-Artefakt in ein digest-gepinntes Experimentimage gebaut. Dreizehn
Akzeptanzprüfungen waren erfolgreich: zwei getrennte Zielbibliotheken,
minimale Feld- und Custom-Column-Projektion, Pagination, sichtbares
`unsupported` für unbekannte Felder, Pfadbereinigung, identische
Wiederholungen, unveränderte Quell-Snapshots, netzwerklose unprivilegierte
Ausführung und keine direkte Datenbankkopplung. Ein direkter read-only Mount
scheitert wegen Calibres Dateisystemtest kontrolliert; nur die wegwerfbare
Copy-on-read-Variante ist qualifiziert. Der Content-Server-Zugang bleibt
offen. Dies ist kein Produktadapter und keine Stackentscheidung.

EXP-0005: RUNTIME_EMPIRICAL lokal validiert am 2026-08-27 unter Podman 6.1.0
mit Linux/amd64 und cgroup v2. EPUBCheck 5.3.0 und Temurin 21.0.12+8 wurden
aus SHA-256-geprüften offiziellen Release-Artefakten in ein lokales,
digest-gepinntes Experimentimage gebaut. Elf Akzeptanzprüfungen waren
erfolgreich: valide und ungültige Wiederholungsläufe, read-only Eingang,
unveränderte Originalhashes, `network=none`, leere Hostumgebung,
Capability-Entzug, Zeit- und Kindprozess-Cleanup, 384-MiB-Speichergrenze,
Ein-CPU-Quote und 1-MiB-Outputgrenze. Das Ergebnis qualifiziert nur dieses
wegwerfbare Profil, nicht einen Produkt-Stack oder die fachliche
EPUBCheck-/Accessibility-Normalisierung aus EXP-0003.

TEST-0001-Fixture-Wave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert
am 2026-08-27 unter Python 3.12.10. Der Fixture-Validator bestätigte in der
aktiven Version `0.2.0` 26
`Kern`-Fälle und 44 Komponenten, vollständige Hash- und Herkunftsangaben,
zentrale Fallorakel, bytegenaue Regeneration und unveränderte Eingänge. Der
kontrollierte 100-ms-Timeout, Pfad-Traversal-Erkennung,
Expansion-Limit-Erkennung, positive und negative Identitätspaare sowie beide
Routingresultate waren erfolgreich. Zehn synthetische Unit-Tests,
`compileall` und `git diff --check` waren erfolgreich. EXP-0002 bis EXP-0005
wurden getrennt ausgeführt. Version `0.1.0` bleibt unverändert und ist wegen
des dortigen OPF-Literals `version="3.3"` nicht mehr die aktive
Experimentbasis.

B1-Planungswave: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert am
2026-08-27. `tools/governance/validate_repository.py` und die
v2-Registry-Validierung waren für 18 registrierte Artefakte erfolgreich.
Fünf synthetische Governance-Unit-Tests, `compileall` und `git diff --check`
waren erfolgreich. Dies belegt Dokument-, Link- und Registry-Integrität,
nicht die fachliche Güte noch nicht erzeugter TEST-0001-Fixtures oder die
Ausführung von EXP-0002 bis EXP-0005.

E-Book-Planungsstand: PROJECT_SEMANTIC und RUNTIME_EMPIRICAL lokal validiert am
2026-08-27. `tools/governance/validate_repository.py` und die
v2-Registry-Validierung waren für zwölf registrierte Artefakte erfolgreich.
Fünf synthetische Governance-Unit-Tests, `compileall` und `git diff --check`
waren erfolgreich. Dies belegt Dokument- und Governance-Integrität, nicht
Produktlaufzeit oder fachliche E-Book-Akzeptanz; Produktcode existierte in
dieser Planungswave noch nicht.

FOUNDATION_INTEGRITY: validated am 2026-08-26 für Foundation 1.7.0 und
artifact-registry-github. Der Foundation-Validator aus Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete im Profil full:
4 INFO, 0 WARNING, 0 ERROR und 0 BLOCKING.

PROJECT_SEMANTIC: validated am 2026-08-26 durch
tools/governance/validate_repository.py und die v2-Registry-Validierung für
fünf registrierte Artefakte.

RUNTIME_EMPIRICAL: validated am 2026-08-26 für die Governance-Werkzeuge unter
Python 3.12.10. Fünf synthetische Unit-Tests waren erfolgreich. compileall und
git diff --check waren erfolgreich. Eine Produktlaufzeit existiert nicht.

FOUNDATION_SOURCE: validated am 2026-08-26. Transfer-Manifest- und
Feature-Catalog-Guard meldeten jeweils 0 BLOCKING. Alle 72 synthetischen
Foundation-Unit-Tests waren erfolgreich.

Repository Quality: validated auf GitHub für den exakten initialen
main-Merge-Commit 4c0818c6bd649b346f5648d5b7c030c3b80a0af7:

https://github.com/gecompat/SammlungsLotse/actions/runs/32983348296

Repository Quality und Artifact Registry Integrity: validated auf GitHub für
den exakten Head f7e048bd3f438b1f74a52390d4d63bb2e72a48e7 des
Validierungs-Pull-Requests:

https://github.com/gecompat/SammlungsLotse/actions/runs/32983701050

https://github.com/gecompat/SammlungsLotse/actions/runs/32983700984

Validierungs-Pull-Request:

https://github.com/gecompat/SammlungsLotse/pull/6

Der Validierungs-Pull-Request wurde als Merge-Commit
44fbdea5aff7cc4e56503e88814aa752103d1653 integriert.

GitHub-Administration: validated am 2026-08-26 über die GitHub-API. main
verlangt die strikt aktuellen Checks repository-quality und
registry-integrity vom GitHub-Actions-Anbieter. Die Regeln gelten für
Administratoren. Force-Pushes und Branch-Löschung sind gesperrt. Offene
Review-Gespräche müssen vor dem Merge aufgelöst sein.

Es existieren keine Repository-Rulesets und kein autorisiertes
Break-Glass-Verfahren. Die Foundation-1.7-Empfehlung zur
Repository-Kontinuität ist bewertet, aber nicht administrativ aktiviert.

Branchschutz-Nachweis-Pull-Request:

https://github.com/gecompat/SammlungsLotse/pull/8

## Nächster Schritt

WI-0011, EXP-0009, GATE-0009, EXP-0010, GATE-0010 und WI-0012 sind
abgeschlossen. GATE-0011 ist entscheidungsbereit und trennt den beseitigten
kritischen False-Same-Befund von den zwei verbleibenden `candidate_related`-
Werkabweichungen sowie den offenen Rollen-, Collection- und
Publikationsfragen. Als kleinste reversible Fortsetzung ist A, eine
produktcodefreie Vertrags- und Evidenzwave, empfohlen. A, B, C, D, E, F und
K bleiben auswählbar; keine Folge ist angenommen oder registriert.
Automatische Suche, mehrere Dateien, IDs oder Bibliotheken, neue
Calibre-Felder, externe Metadaten, Persistenz, Routing, Browser, REST, Agents
und Writes bleiben nicht autorisiert.

## Offene Punkte

- Eine professionelle Markenähnlichkeitsprüfung ist vor einer wirtschaftlich
  wesentlichen breiten Vermarktung weiterhin erforderlich.
- Eine spätere Entscheidung kann getrennte Core-Safety- und CI-Gates-Rulesets
  mit eng begrenztem Pull-Request-only-Bypass ausschließlich für nachgewiesene
  `INFRASTRUCTURE_UNAVAILABLE`-Fälle bewerten. Bis dahin bleibt jeder fehlende
  erforderliche Check merge-blockierend.

## Blocker

Keine bekannten Blocker. Jede Änderung an
Provider, Version, Runtime, Image, Executor oder Nutzeroberfläche verlangt
eine neue Bewertung und Qualifikation. Schreibende Fähigkeiten bleiben
unabhängig davon hinter einem eigenen Writer-Gate.
