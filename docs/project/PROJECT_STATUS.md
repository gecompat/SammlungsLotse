# Projektstatus

Status: AUTHORITATIVE

Stand: 2026-09-02

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
GATE-0011 ist nach ausdrücklicher Auswahl von Option A abgeschlossen.
EXP-0011 ist als produktcodefreie Vertrags- und Evidenzwave ausgeführt. Der
commitgebundene Lauf bestand 14/14 Kriterien auf genau 15 synthetischen
Paaren; V1, V2 und V3 verlieren auf der EXP-0010-Rollenmatrix null Felder,
decken jeweils 145/145 Werte mit Provenienz ab und erhalten alle fünf
Produktstufen unverändert. Alle Varianten sind
`eligible_with_tradeoffs`. Der Nutzer hat in GATE-0012 ausdrücklich Option A
gewählt. GATE-0012 und WI-0013 sind `done`. Der enge rollenbewusste
V2-Zielvertrag ist umgesetzt und 29/29 synthetisch produktqualifiziert. V1
bleibt bytekompatibler Standard, V2 wird ausschließlich explizit aktiviert
und behält die fünf vorhandenen Produktstufen. Der abhängige WI-0011-Weg ist
auf demselben Preimage erneut 23/23 qualifiziert. Publikationsstufe und
V1-Deprecation sind nicht ausgewählt. GATE-0013 ist nach ausdrücklicher
Auswahl von Option A abgeschlossen: V1 bleibt Standard, V2 bleibt Opt-in und
kein neuer Produktarbeitsgegenstand ist registriert. Der Nutzer hat in
GATE-0014 ausdrücklich Option A gewählt. GATE-0014 und EXP-0012 sind
abgeschlossen. Der synthetische Lauf bestand 16/16 Methodenkriterien; V1 und
V3 sind `eligible_with_tradeoffs`, V2 ist wegen eines Misses
`not_qualified`. Der lokale private Drei-EPUB-Praxissmoke blieb bei vier
erfolgreich ausgeführten Suchen, vollständigem Cleanup, aber 0/3
abgeschlossenen WI-0011-Vergleichen `not_qualified`. Der Nutzer hat in
GATE-0015 ausdrücklich Option A gewählt. GATE-0015 ist abgeschlossen und
EXP-0013 abgeschlossen. Der erneut ausdrücklich bestätigte private Hauptlauf
verarbeitete genau dieselben drei EPUBs ohne Verzeichnissuche. Alle drei
WI-0011-Läufe endeten vor dem Record-Handoff mit
`ingress.preflight_gate_not_open`; das pfadfreie Ergebnis ist deshalb
`not_qualified`. Quellen blieben unverändert und das Cleanup war vollständig.
Der Nutzer hat in GATE-0016 ausdrücklich Option A gewählt. GATE-0016 ist
abgeschlossen und EXP-0014 ausgeführt. Der Nutzer bestätigte denselben Satz
aus genau drei EPUBs erneut; jede task-private Kopie durchlief genau einmal
den unveränderten WI-0004-JSON-Weg. Alle drei Ergebnisse lauteten `review`
mit `epub.remote_reference.present` und `security.remote_resource`.
Unbekannte Codes blieben null, Quellen unverändert und das Cleanup
  vollständig. Der Nutzer hat in GATE-0017 ausdrücklich Option A gewählt.
  GATE-0017 und EXP-0015 sind abgeschlossen. Nach grüner CI auf dem sauberen
  Preimage bestand die synthetische Kontrolle mit 7/7 Kontextklassen,
  19/19 Negativkontrollen und 32 Parserläufen. Der erneut bestätigte Hauptlauf
  verarbeitete genau drei EPUBs; die einzige gemeinsame grobe Klasse ist
  `content.navigation=3`. Es gab keine seltene bekannte Klasse und keinen
  unklassifizierten Eingang. Quellen blieben unverändert und das Cleanup war
  vollständig. Der Nutzer hat in GATE-0018 ausdrücklich Option A gewählt.
  GATE-0018 und EXP-0016 sind abgeschlossen. Der rein synthetische,
  produktcodefreie Doppellauf verarbeitete 48 Fälle in 96 Parserläufen. Alle
  16 Methodenkriterien bestanden; alle drei Strategien sind innerhalb der
  gebundenen Matrix `eligible_with_tradeoffs`, mit zehn fail-closed
  Enthaltungen und null kritischen Fehlfortsetzungen je Strategie.
  Der Nutzer hat in GATE-0019 ausdrücklich Option A gewählt. GATE-0019 und
  EXP-0017 sind abgeschlossen. Das korrigierte saubere Preimage `53a1e2d`
  bestand den vollständigen lokalen Repositorytest und beide exakten
  GitHub-Pflichtchecks. Der danach genau einmal ausgeführte synthetische
  Hauptlauf bestand 18/18 Kriterien mit zwölf Fällen, zwei semantisch
  identischen Wiederholungen, 24 Providerläufen, null Orakelmismatches, null
  Deep-Path-Kanarientreffern, effektiver Netzwerklosigkeit, fail-closed
  Grenzproben und vollständigem Cleanup. Der frühere `inconclusive`-Bericht
  auf `2bb29e0` bleibt unverändert außerhalb von Git. Der Nutzer hat in
  GATE-0020 ausdrücklich Option B gewählt. GATE-0020 ist abgeschlossen und
  WI-0014 als review-beibehaltende, pfadfreie V2-Kontexterklärung `done`.
  V2 bleibt explizites JSON-Opt-in für Einzel-, Batch- und kombinierten
  Bericht; V1, Humanweg, `review` und Deep-Read-Gate bleiben unverändert. Der
  einmalige commitgebundene Hauptlauf auf Preimage `ed7f173` bestand 16/16
  Kriterien. GATE-0021 ist `done`: Der Nutzer hat ausdrücklich Option A
  gewählt. Der qualifizierte V2-Vertrag bleibt als enges JSON-Opt-in stabil;
  es wird keine Folgearbeit registriert. AI Repository Foundation 1.8.0 ist
  davon getrennt semantisch integriert; die optionale Rule-Context-Cache-
  Fähigkeit bleibt ausdrücklich nicht ausgewählt.

## Vorhanden

- eigenständiges GitHub-Repository und lokale Codex-Projektzuordnung;
- MIT-Lizenz für eigenständig entwickelte SammlungsLotse-Inhalte;
- AI Repository Foundation 1.8.0;
- vollständige semantische 1.8-Upgrade-Bewertung unter
  docs/governance/FOUNDATION_UPGRADE_1_8.md;
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
  Profilbindung und nach dem WI-0014-Implementierungskandidaten gegen
  Preimage `7cb8407` erneuerter
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
- aktueller v3-Qualifikationsnachweis mit 29/29 Kriterien, fünf bestehenden
  TEST-0001-Paaren, acht konformen EXP-0010-Qualitätsfällen, zwei getrennten
  ungültigen Kontrollen, je zwei tatsächlichen V1- und V2-JSON-CLI-
  Wiederholungen, bytekompatiblem V1, 241/241 Provenienzeinträgen,
  unveränderten Eingängen, pfadfreier Ausgabe und vollständigem Task-Cleanup;
- historische EXP-0009- und EXP-0010-Validatoren, die die unveränderten
  Ergebnisse weiterhin gegen ihre eingefrorenen Git-Preimage-Commits mit je
  12/12 Kriterien prüfen;
- zwei sichtbare verbleibende Werk-Oracledifferenzen mit
  `candidate_related`, die nicht als vollständige Qualifikation der flachen
  Identifier- oder Collection-Semantik dargestellt werden;
- abgeschlossenes GATE-0011 mit ausdrücklicher Auswahl der produktcodefreien
  Vertrags- und Evidenzwave;
- abgeschlossener EXP-0011-Vertrag und historisch prüfbarer 14/14-Nachweis
  aus Preimage `a5aeb019`, genau drei experimentellen Vertragsvarianten, 15
  gebundenen synthetischen Paaren, zwei identischen semantischen
  Wiederholungen, null Rollenverlust, 145/145 Provenienzwerten je Variante,
  unveränderten aktuellen Entscheidungen und unverändertem Produktcode;
- abgeschlossenes GATE-0012 mit ausdrücklicher Auswahl des engen
  rollenbewussten V2-Zielvertrags;
- abgeschlossener WI-0013 mit bytekompatiblem V1-Standardpfad, explizitem
  V2-Opt-in, rollenbewusster Metadatenprojektion, fünf unveränderten
  Entscheidungsstufen und 29/29 synthetischem Produktnachweis;
- abgeschlossenes GATE-0013 mit ausdrücklicher Auswahl, den dualen Vertrag
  stabil zu halten, ohne neuen Produktarbeitsgegenstand, Defaultwechsel,
  Deprecation oder Publikationswave;
- abgeschlossenes GATE-0014 mit ausdrücklicher Auswahl der begrenzten,
  produktcodefreien Kandidatensuche;
- abgeschlossenes EXP-0012 mit 16/16 Methodenkriterien, zwei identischen
  Wiederholungen, V1 und V3 als `eligible_with_tradeoffs`, V2 als
  `not_qualified`, null unerwarteten Kandidaten und null kritischen False Same;
- lokaler privater Drei-EPUB-Smoke mit vier Suchläufen, unveränderten Quellen,
  vollständigem Cleanup und offenem 0/3-WI-0011-Nichtabschluss;
- abgeschlossenes GATE-0015 mit ausdrücklicher Auswahl der privaten,
  produktcodefreien Ursachenklärung;
- abgeschlossenes EXP-0013 mit 16/16 Methodenkriterien, genau drei erneut
  explizit bestätigten EPUBs, vier Suchläufen, drei vor dem Record-Handoff
  geschlossenen Ingress-Preflight-Gates, pfadfreiem `not_qualified`-Aggregat,
  unveränderten Quellen und vollständigem Cleanup;
- abgeschlossenes GATE-0016 mit ausdrücklicher Auswahl der privaten,
  produktcodefreien Intake-Ursachenqualifizierung;
- abgeschlossenes EXP-0014 mit 4/4 tatsächlichen synthetischen WI-0004-
  Kontrollen, 11/11 Negativkontrollen, genau denselben drei erneut bestätigten
  EPUBs, drei unveränderten WI-0004-JSON-Läufen, `review=3`,
  `security.remote_resource=3`, null unbekannten Codes, unveränderten Quellen
  und vollständigem Cleanup;
- abgeschlossenes GATE-0017 mit ausdrücklicher Auswahl der privaten,
  produktcodefreien und pfadfreien Referenzkontextgruppierung;
- abgeschlossenes EXP-0015 mit demselben erneut bestätigten Dreiersatz,
  7/7 synthetischen Kontextklassen, 19/19 Negativkontrollen, 32 synthetischen
  Parserläufen, genau einem privaten Parserlauf je task-privater Kopie,
  `content.navigation=3`, keiner seltenen oder unklassifizierten Klasse,
  unveränderten Quellen, vollständigem Cleanup und keinen privaten
  Referenzwerten oder Einzelzuordnungen;
- abgeschlossenes GATE-0018 mit ausdrücklicher Auswahl der rein synthetischen
  Navigationskontext- und Sicherheitsmatrix;
- abgeschlossenes EXP-0016 mit genau 48 synthetischen Package-, XHTML-,
  Navigation-, SVG-, CSS-, Schema- und Täuschungsfällen, zwei semantisch
  identischen Wiederholungen, 96 Parserläufen, 16/16 Methodenkriterien, drei
  `eligible_with_tradeoffs`-Strategien, jeweils zehn Enthaltungen und null
  kritischen Fehlfortsetzungen, False Negatives oder Context Mismatches;
- abgeschlossenes GATE-0019 mit ausdrücklicher Auswahl der synthetischen
  Downstream-Isolations- und Threat-Model-Qualifikation;
- abgeschlossenes EXP-0017 mit historisch gebundenem 18/18-Pass: genau zwölf
  zur Laufzeit erzeugte synthetische EPUBs aus vier S3-Navigations-, vier
  Ressourcen-/Aktiv- und vier Täuschungskontexten, zwei semantisch identische
  Wiederholungen, 24 abgeschlossene, isolierte und bereinigte Providerläufe,
  null Orakelmismatches und Deep-Path-Kanarientreffer, effektives
  `network=none`, fail-closed Timeout- und Outputproben sowie vollständiges
  Cleanup; der erste `inconclusive`-Bericht und die eng begrenzte Korrektur
  bleiben transparent dokumentiert, Produktcode und private Medien außerhalb;
- vorgeschlagenes GATE-0020 mit fünf ausdrücklich wählbaren Fortsetzungen,
  ohne ausgewählte Option, Folgeexperiment oder Produktarbeitsgegenstand;

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

Foundation-1.8-Upgrade-Wave: FOUNDATION_INTEGRITY, PROJECT_SEMANTIC und
RUNTIME_EMPIRICAL lokal validiert am 2026-09-02 unter Windows und Python
3.12.10. Der Foundation-1.8-Zielvalidator am exakten Quellcommit
`7ddc29988b23570f462e46ebf527f8dfdd05fd75` meldete 4 INFO, 0 Warnungen,
0 Fehler und 0 Blocker. Repository- und v2-Registry-Prüfung waren für 62
Artefakte erfolgreich. Der vollständige Repositorytest entdeckte 273 Tests,
ersetzte 15 eingefrorene Current-Preimage-Prüfungen durch fünf historische
Prüfungen und führte 258 Tests erfolgreich aus. `compileall` und
`git diff --check` waren grün.

Die getrennte Foundation-Quellprüfung meldete für Transfer-Manifest und
Feature-Katalog jeweils 0 Blocker; alle 94 Foundation-Tests bestanden. Der
Foundation-Projektvalidator meldete 0 Fehler und 0 Blocker sowie zwei
bekannte Self-Scan-Warnungen, weil sein eigener Quelltext die Suchmuster für
einen absoluten Benutzerpfad und ein Platzhalterliteral enthält. Die
optionale Fähigkeit `rule-context-cache` wurde nicht installiert oder
ausgeführt. Diese Evidenz belegt die 1.8-Integration, nicht die Auswahl einer
GATE-0021-Option oder einer persistenten Cachekonfiguration.

WI-0014-Ergebnisbindungs- und GATE-0021-Wave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-02
unter Windows und Python 3.12.10. Der historische 16/16-Produktnachweis und
24 fokussierte Produkt-, Qualifikations- und Gate-Prüfungen bestanden.
Repository- und v2-Registry-Prüfung waren für 61 Artefakte erfolgreich;
`compileall` und `git diff --check` waren grün. Der Foundation-Validator am
exakten installierten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Der vollständige Repositorytest wird auf dem finalen
Ergebnisbindungscommit durch die erforderliche GitHub-CI ausgeführt und
lokal nicht redundant wiederholt. Diese Evidenz belegt Ergebnisbindung und
das damals ergebnisoffene Gate; die Auswahl von Option A erfolgte anschließend
ausdrücklich durch den Nutzer.

WI-0014-Implementierungskandidat: PROJECT_SEMANTIC, RUNTIME_EMPIRICAL und
FOUNDATION_INTEGRITY lokal validiert am 2026-09-02 unter Windows und Python
3.12.10. 76 fokussierte Produkt-, Qualifikations- und Boundary-Prüfungen
sowie der historische EXP-0014-Nachweis bestanden. Der einmalige
vollständige Repositorytest entdeckte 270 Tests, schloss vier einzelne
eingefrorene Current-Preimage-Prüfungen und das elfprüfige eingefrorene
EXP-0014-Modul aus, ersetzte sie durch fünf Historical-Preimage-Prüfungen und
führte 255 Tests erfolgreich aus. Die separat erforderliche aktuelle
WI-0005-Deep-Read-only-Requalifizierung bestand 12/12 Kriterien. Die nach
der V2-Modellerweiterung ebenfalls erforderliche WI-0011-Requalifizierung
lief tatsächlich über Podman erneut 23/23 Kriterien und vollständiges
Cleanup. Repository- und v2-Registry-Prüfung waren für 60 Artefakte
erfolgreich; `compileall` und `git diff --check` waren grün. Der
Foundation-Validator am exakten
installierten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Beide GitHub-Pflichtchecks bestanden anschließend auf dem
exakten Ergebnispreimage `ed7f173896b7365d2f91fb47baa1bc4065c23bcb`.

Der danach genau einmal ausgeführte WI-0014-Hauptlauf bestand 16/16
Kriterien: 96 Klassifikatorläufe über 48 Fälle ohne Mismatch, 96
Einzeldatei-CLI-Läufe über zwölf Fälle mit bytegleichem V1 und
deterministischem V2, elf unverändert geschlossene Reviewfälle, ein
`not_applicable`-Kontrollfall, gültige Batch- und kombinierte V2-Schemata,
kein gestarteter Deep-Provider, pfadfreie Berichte, unveränderte Eingänge und
vollständiges Cleanup. Der eingecheckte Nachweis besitzt SHA-256
`16b33a98904157593de335ce0aa8a8348f3c1d9a795fdbe34765251a5dbc3046`.
Diese Evidenz qualifiziert WI-0014, nicht eine Reviewlockerung oder eine
weitere Produktwave.

GATE-0020-Auswahl- und WI-0014-Vertragswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Die 13 fokussierten Gate-, Registrierungs-
und Registryprüfungen bestanden. Repository- und v2-Registry-Prüfung waren
für 60 Artefakte erfolgreich. Der einmalige vollständige Repositorytest auf
dem stabilen Vertragskandidaten entdeckte 257 Tests, ersetzte genau fünf
eingefrorene Current-Preimage-Prüfungen durch ihre Historical-Preimage-
Prüfungen und führte 252 Tests erfolgreich aus. `git diff --check` war
erfolgreich. Der Foundation-Validator am exakten installierten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Produktcode blieb unverändert. Diese Evidenz belegt Auswahl,
Registrierung und Begrenzung von WI-0014, nicht dessen Implementierung oder
Produktqualifikation.

EXP-0017-Ausführungs- und Ergebnisbindungswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Das maßgebliche saubere
Ausführungspreimage `53a1e2dbefd03c7d770e949490ea1ec7783bfe98` bestand vor
dem Hauptlauf den einmaligen vollständigen lokalen Repositorytest mit 255
entdeckten, fünf gezielt durch Historical-Preimage-Prüfungen ersetzten und
250 erfolgreich ausgeführten Tests; die noch fehlende Ergebnisdatei erzeugte
genau einen erwarteten Skip. Beide erforderlichen GitHub-Checks waren auf
exakt diesem Commit grün.

Der danach genau einmal ausgeführte synthetische Hauptlauf bestand 18/18
Kriterien: zwölf Fälle, zwei semantisch identische Wiederholungen, 24
abgeschlossene, prozessgestartete, isolationsverifizierte und bereinigte
Providerläufe, null Kontext-, S3- oder Schemagruppenmismatches, genau eine
Kontrollverbindung und null Deep-Path-Kanarientreffer. Effektives
`network=none`, die vollständigen Isolationswerte, fail-closed Timeout- und
Outputproben, unveränderte Eingänge und vollständiges Cleanup wurden
zurückgelesen. Der 4.429-Byte-Bericht mit SHA-256
`ffb748bc7429b4362392c1464b6268bf404df74625420a8498d405558c88db61`
ist gegen dieses historische Preimage gültig. Der erste
`inconclusive`-Bericht auf `2bb29e0` bleibt unverändert außerhalb von Git;
seine getrennt getestete Semantikprojektionskorrektur und das neue grüne
Preimage sind transparent dokumentiert.

Für die Ergebnisbindung bestanden der historische Validator sowie 29 von 30
gemeinsam ausgeführten Fokusprüfungen unmittelbar. Die einzige Abweichung war
eine veraltete Satzbehauptung zum fortgeschriebenen GATE-0019-Stand; nach der
Anpassung bestand genau dieser betroffene Test. Repository- und v2-Registry-
Prüfung waren für 59 Artefakte erfolgreich; `compileall`, `git diff --check`,
die begrenzte Datenschutzsuche und der leere Produktcode-Diff waren
erfolgreich. Der Foundation-Validator am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Der vollständige Repositorytest wird auf dem finalen
Ergebnisbindungscommit durch die erforderliche GitHub-CI ausgeführt und
lokal nicht redundant wiederholt. Diese Evidenz belegt Methode und
Ergebnisbindung, nicht Produktfreigabe oder eine Lockerung des
WI-0004-Review-Gates.

GATE-0019-Auswahl- und EXP-0017-Vertragswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 58 Artefakte erfolgreich; die sieben fokussierten Gate-Tests bestanden.
Der einmalige kontrollierte Volltest auf dem stabilen Vertragskandidaten
entdeckte 242 Tests, ersetzte genau fünf eingefrorene Preimage-Prüfungen durch
gleichzählige Historical-Preimage-Prüfungen und führte 237 Tests erfolgreich
aus. `compileall`, `git diff --check`, die begrenzte Datenschutzsuche und die
Prüfung auf leeren Produktcode-Diff waren erfolgreich. FOUNDATION_INTEGRITY
am exakten Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033`
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Der read-only Host-Preflight fand
Podman Client und Server `6.1.0`, Linux/amd64 sowie die exakt gebundene
WI-0005-Image-ID
`sha256:d8143e59b2c478e0056200a3529b9beb74737885863c22097b198a9c0c92974e`.
Dies belegt die ausdrückliche Auswahl A, Registrierung und Begrenzung von
EXP-0017 sowie erreichbare Ausführungsvoraussetzungen. Es belegt weder einen
Experimentlauf, effektive Isolation während der zwölf Fälle, null
Kanarientreffer noch eine Produktfreigabe oder Lockerung des
WI-0004-Review-Gates.

EXP-0016-Ausführungs- und Ergebnisbindungswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Das saubere Ausführungspreimage
`969fa6331afdfc4ceb808ffeed71f7a30193205b` bestand vor dem Hauptlauf beide
erforderlichen GitHub-Checks. Der einmalige lokale Volltest auf diesem
stabilen Preimage entdeckte 240 Tests, ersetzte genau fünf eingefrorene
Preimage-Prüfungen durch gleichzählige Historical-Preimage-Prüfungen und
führte 235 Tests erfolgreich aus; die noch fehlende Ergebnisdatei erzeugte
genau einen erwarteten Skip. Danach verarbeitete genau ein bestätigter
synthetischer Doppellauf 48 Fälle in 96 Parserläufen. Beide Wiederholungen
waren semantisch identisch, alle 16 Akzeptanzwerte bestanden und alle drei
Strategien wurden `eligible_with_tradeoffs` eingestuft. S1 und S2 besitzen
je acht konservative Reviews, S3 null; jede Strategie besitzt zehn
fail-closed Enthaltungen und null kritische Fehlfortsetzungen, False
Negatives oder Context Mismatches.

Der historische Validator bindet das 2.279-Byte-Ergebnis mit SHA-256
`6c748dd1477dba56a37e19b7a5bf798d32e702e8d6d2a230ebfa3c98d775db08`
an Profil, 48-Fall-Manifest, Runner und Preimage, ohne den Hauptlauf erneut
auszuführen. Auf dem Ergebnisstand bestanden 25 gezielte Experiment-,
Historical-Result- und Gate-Tests sowie Repository- und v2-Registry-Prüfung
für 57 Artefakte. `compileall`, `git diff --check`, die begrenzte
Datenschutzsuche und die Prüfung auf leeren Produktcode-Diff bestanden.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Ein zweiter lokaler Volltest und ein zweiter Experimentlauf wurden
bewusst nicht ausgeführt; die vollständige Suite auf dem finalen
Ergebniscommit bleibt Aufgabe der erforderlichen GitHub-CI. Dies belegt den
synthetischen Befund, aber weder Produktsicherheit noch eine Lockerung des
WI-0004-Review-Gates.

GATE-0018-Auswahl- und EXP-0016-Vertragswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 56 Artefakte erfolgreich; die sechs fokussierten Gate-Tests bestanden.
Der einmalige kontrollierte Volltest auf dem stabilen Vertragskandidaten
entdeckte 230 Tests, ersetzte genau fünf eingefrorene Preimage-Prüfungen durch
gleichzählige Historical-Preimage-Prüfungen und führte 225 Tests erfolgreich
aus. `compileall`, `git diff --check` und die begrenzte Datenschutzsuche waren
erfolgreich; unter `src/sammlungslotse/` gab es keine Änderung.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt die ausdrückliche Auswahl A sowie den eng gebundenen,
noch nicht ausgeführten EXP-0016-Vertrag; es belegt weder ein
Experimentergebnis noch eine Produktfreigabe oder Lockerung des
WI-0004-Review-Gates.

EXP-0015-Ergebnis- und GATE-0018-Wave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 55 Artefakte erfolgreich; die sechs fokussierten Gate-Tests und alle
sieben historischen Ergebnisprüfungen bestanden. Der kontrollierte Testlauf
entdeckte 230 Tests, ersetzte genau fünf eingefrorene Preimage-Prüfungen durch
gleichzählige Historical-Preimage-Prüfungen und führte 225 Tests erfolgreich
aus. EXP-0015 blieb gegen das grüne Ausführungspreimage
`cefe2d29b54b8e6cbc60b07b1485da473565cda7` gebunden. Die synthetische
Kontrolle bestand mit 7/7 Kontextklassen, 19/19 Negativkontrollen und
32 Parserläufen. Das 483-Byte-Ergebnis mit SHA-256
`651ad195b54531d20e0fc6ff882df6e1d4b38765e877057faf7858f36dae50a1`
enthält ausschließlich `content.navigation=3`, keine seltene bekannte Klasse,
null unklassifizierte Eingänge, unveränderte Quellen und vollständiges
Cleanup. `compileall`, `git diff --check` und die begrenzte Datenschutzsuche
waren erfolgreich; unter `src/sammlungslotse/` gab es keine Änderung.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt Methode, pfadfreies Aggregat und die offene
Ergebnisentscheidung, nicht Erreichbarkeit, Ausführung, Gefährlichkeit,
EPUB-Gültigkeit oder eine Produktfreigabe.

GATE-0017-Auswahl- und EXP-0015-Vertragswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 54 Artefakte erfolgreich; die fünf fokussierten Gate-Tests bestanden.
Der kontrollierte Testlauf entdeckte 217 Tests, ersetzte genau fünf
eingefrorene Preimage-Prüfungen durch gleichzählige Historical-Preimage-
Prüfungen und führte 212 Tests erfolgreich aus. TEST-0001, EXP-0002 bis
EXP-0007, die historischen Ergebnisse von EXP-0009 bis EXP-0014 und die
Qualifikationsnachweise von WI-0005, WI-0008, WI-0013 und WI-0011 blieben
gültig. `compileall`, `git diff --check` und die begrenzte Datenschutzsuche
waren erfolgreich; unter `src/sammlungslotse/` gab es keine Änderung.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt die ausdrückliche Auswahl A sowie den eng gebundenen,
noch nicht ausgeführten EXP-0015-Vertrag; es belegt weder einen privaten
Referenzkontextbefund noch eine Produktfreigabe.

EXP-0014-Ergebnis- und GATE-0017-Wave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 53 Artefakte erfolgreich; die fünf fokussierten Gate-Tests und alle sechs
historischen Ergebnisprüfungen bestanden. Der kontrollierte Testlauf entdeckte
217 Tests, ersetzte genau fünf eingefrorene Preimage-Prüfungen durch
gleichzählige Historical-Preimage-Prüfungen und führte 212 Tests erfolgreich
aus. EXP-0014 blieb gegen das Ausführungspreimage
`e82d01e6d669e85646dafd6ab3d569fc38e0d71b` gebunden. Das 907-Byte-Ergebnis
mit SHA-256
`0eab4893eb85d05c07622bfe70721a58f03e8285e199738b1513237dc3207411`
enthält genau drei `review`-Aktionen und dreimal
`security.remote_resource`, keine unbekannten Codes, unveränderte Quellen und
vollständiges Cleanup. `compileall`, `git diff --check` und die begrenzte
Datenschutzsuche waren erfolgreich; unter `src/sammlungslotse/` gab es keine
Änderung. FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt Methode, pfadfreies Aggregat und die offene
Ergebnisentscheidung, nicht die Schädlichkeit der Referenzen, die
Standardsgültigkeit der EPUBs oder eine Produktfreigabe.

GATE-0016-Auswahl- und EXP-0014-Vertragswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 52 Artefakte erfolgreich; die fünf fokussierten Gate-Tests bestanden.
Der kontrollierte Testlauf entdeckte 205 Tests, ersetzte genau vier
Current-Preimage-Ergebnisprüfungen durch gleichzählige Historical-Preimage-
Prüfungen und führte 201 Tests erfolgreich aus. TEST-0001, EXP-0002 bis
EXP-0007, die historischen Ergebnisse von EXP-0009 bis EXP-0013 und die
Qualifikationsnachweise von WI-0005, WI-0008, WI-0013 und WI-0011 blieben
gültig. `compileall`, `git diff --check` und die Datenschutzsuche waren
erfolgreich; unter `src/sammlungslotse/` gab es keine Änderung.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt die ausdrückliche Auswahl A sowie den eng gebundenen,
noch nicht ausgeführten EXP-0014-Vertrag; es belegt weder einen privaten
Ursachenbefund noch eine Produktfreigabe.

EXP-0013-Ergebnis- und GATE-0016-Wave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-09-01
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 51 Artefakte erfolgreich. Der historische EXP-0013-Validator band das
561-Byte-Ergebnis mit SHA-256
`6ea2a583956602466edc5b8c11f658d86b975f22ca2b96821c22e4a21265b941`
an Preimage `6d32f5d`: genau drei Eingänge, vier Suchläufe, drei WI-0011-Läufe,
dreifaches `ingress.preflight_gate_not_open`, unveränderte Quellen,
vollständiges Cleanup und fachlicher Status `not_qualified`. TEST-0001,
EXP-0002 bis EXP-0007, die historischen Ergebnisse von EXP-0009 bis EXP-0013
und die Qualifikationsnachweise von WI-0005, WI-0008, WI-0013 und WI-0011
blieben gültig. Der kontrollierte Testlauf entdeckte 205 Tests, ersetzte
genau vier Current-Preimage-Ergebnisprüfungen durch gleichzählige Historical-
Preimage-Prüfungen und führte 201 Tests erfolgreich aus. `compileall`,
`git diff --check`, Datenschutzsuche und Cleanupprüfung waren erfolgreich;
unter `src/sammlungslotse/` gab es keine Änderung. FOUNDATION_INTEGRITY am
exakten Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033`
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies belegt Methode,
Aggregatbefund und die offene Ergebnisentscheidung, nicht den konkreten
Intake-Grund oder eine Produktfreigabe.

GATE-0015-Auswahl- und EXP-0013-Vertragswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-08-31
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 50 Artefakte erfolgreich; die fünf fokussierten Gate-Tests bestanden.
Der kontrollierte Testlauf entdeckte 197 Tests, ersetzte genau vier
Current-Preimage-Ergebnisprüfungen durch gleichzählige
Historical-Preimage-Prüfungen und führte 193 Tests erfolgreich aus. TEST-0001,
EXP-0002 bis EXP-0007, die historischen Ergebnisse von EXP-0009 bis EXP-0012
und die Qualifikationsnachweise von WI-0005, WI-0008, WI-0013 und WI-0011
blieben gültig. `compileall` und `git diff --check` waren erfolgreich.
FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler und
0 Blocker. Dies belegt die ausdrückliche Auswahl A sowie den eng gebundenen,
noch nicht ausgeführten EXP-0013-Vertrag; es belegt weder einen privaten
Diagnosebefund noch eine Produktfreigabe.

EXP-0012-Ergebnis- und GATE-0015-Wave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-08-31
unter Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren
für 49 Artefakte erfolgreich. Der kontrollierte Testlauf entdeckte 197 Tests,
ersetzte genau vier Current-Preimage-Ergebnisprüfungen durch gleichzählige
Historical-Preimage-Prüfungen und führte 193 Tests erfolgreich aus. EXP-0012
blieb historisch gegen `deddef0` mit 16/16 Kriterien prüfbar; EXP-0009,
EXP-0010 und EXP-0011 bestanden historisch weiterhin 12/12, 12/12 und 14/14.
`compileall` und `git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY am
exakten Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033`
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies belegt Methode, Ergebnisgate
und unveränderten Produktstand, nicht eine Produktfreigabe. Der getrennte
private Smoke wählte genau drei EPUBs, führte vier Suchen aus, bewahrte die
Quellen und bereinigte vollständig; 0/3 WI-0011-Abschlüsse bleiben als
anonymer offener Befund dokumentiert.

GATE-0014-Auswahl- und EXP-0012-Vertragswave: PROJECT_SEMANTIC, bestehende
RUNTIME_EMPIRICAL-Regression und FOUNDATION_INTEGRITY lokal validiert am
2026-08-31 unter Windows und Python 3.12.10. Repository- und v2-Registry-
Prüfung waren für 48 Artefakte erfolgreich. Der kontrollierte Testlauf
entdeckte 189 Tests,
ersetzte genau drei Current-Preimage-Ergebnisprüfungen durch
Historical-Preimage-Prüfungen und führte 186 Tests erfolgreich aus. Die
aktuellen WI-0013- und WI-0011-Produktnachweise bestanden weiterhin 29/29
beziehungsweise 23/23 Kriterien; EXP-0009, EXP-0010 und EXP-0011 blieben
historisch mit 12/12, 12/12 und 14/14 Kriterien prüfbar. `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY am exakten
Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen,
0 Fehler und 0 Blocker. Dies belegt die ausdrückliche Auswahl, den eng
gebundenen noch nicht ausgeführten Experimentvertrag und die Regression des
unveränderten Produktstands, nicht das Ergebnis von EXP-0012 oder eine
Produktübernahme.

GATE-0013-Ergebniswave: PROJECT_SEMANTIC, bestehende RUNTIME_EMPIRICAL-
Regression und FOUNDATION_INTEGRITY lokal validiert am 2026-08-31 unter
Windows und Python 3.12.10. Repository- und v2-Registry-Prüfung waren für 46
Artefakte erfolgreich. Der kontrollierte Testlauf entdeckte 189 Tests,
ersetzte genau drei Current-Preimage-Ergebnisprüfungen durch
Historical-Preimage-Prüfungen und führte 186 Tests erfolgreich aus. Die
aktuellen WI-0013- und WI-0011-Produktnachweise bestanden weiterhin 29/29
beziehungsweise 23/23 Kriterien; EXP-0009, EXP-0010 und EXP-0011 blieben
historisch mit 12/12, 12/12 und 14/14 Kriterien prüfbar. `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY am exakten
Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen,
0 Fehler und 0 Blocker. Dies belegt die registrierte Ergebnisentscheidung
und die Regression des unveränderten Produktstands, nicht eine neue
Produktfunktion, Migration oder Publikationsstufe.

WI-0013-Implementierungswave: PROJECT_SEMANTIC, RUNTIME_EMPIRICAL und
FOUNDATION_INTEGRITY lokal validiert am 2026-08-31 unter Windows, Python
3.12.10, Podman 6.1.0 und Calibre 9.13.0 auf Linux/amd64. Das
commitgebundene Produktpreimage
`dde132646f9e578f582231c2a7be946134490184` bestand 29/29 Kriterien auf fünf
TEST-0001-Paaren, acht konformen EXP-0010-Qualitätsfällen und zwei getrennten
ungültigen Kontrollen. V1 blieb bytekompatibler Standard, V2 entsprach der
gebundenen EXP-0011-Rollenprojektion, alle fünf Entscheidungen blieben
identisch, 241/241 Provenienzeinträge waren vollständig und es entstanden
null kritische False Same. Der Nachweis besitzt SHA-256
`feebe3ff325aec657fcff928c76bece18aa01c48a90aa5f8281620ee23b52e51`.
Der abhängige WI-0011-Weg wurde gegen denselben Preimage und das unveränderte
Calibre-Image tatsächlich erneut 23/23 qualifiziert; sein Nachweis besitzt
SHA-256
`90fbe6856aeb09f89e382c59312f7035ac9777de57a316fc336bb81fcf5a7d4e`.
Seine Taskwurzel wurde vollständig entfernt; 22 pfadfreie Rohbelege liegen
außerhalb von Git unter
`C:\rep\artifacts\SammlungsLotse\wi-0013-wi0011-requalification-dde1326`.
Die historischen EXP-0009-, EXP-0010- und EXP-0011-Validatoren bestanden
weiterhin 12/12, 12/12 und 14/14. Repository- und v2-Registry-Prüfung waren
für 45 Artefakte erfolgreich. Der kontrollierte Testlauf entdeckte 189 Tests,
ersetzte genau drei Current-Preimage-Ergebnisprüfungen durch Historical-
Preimage-Prüfungen und führte 186 Tests erfolgreich aus. `compileall` und
`git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY am exakten
Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen,
0 Fehler und 0 Blocker.

GATE-0012-Auswahl- und WI-0013-Planungswave: PROJECT_SEMANTIC, bestehende
RUNTIME_EMPIRICAL-Regression und FOUNDATION_INTEGRITY lokal validiert am
2026-08-31 unter Windows und Python 3.12.10. Repository- und v2-Registry-
Prüfung waren für 45 Artefakte erfolgreich. Der kontrollierte Testlauf
entdeckte 185 Tests, ersetzte genau drei Current-Preimage-Ergebnisprüfungen
durch Historical-Preimage-Prüfungen und führte 182 Tests erfolgreich aus.
`compileall` und `git diff --check` waren erfolgreich. FOUNDATION_INTEGRITY
am exakten Quellcommit `d49f978f33001fcc098998ff7c04ffb209b28033`
meldete 0 Warnungen, 0 Fehler und 0 Blocker. Dies belegt Auswahl,
Registrierung und Begrenzung von WI-0013, nicht dessen Implementierung oder
Produktqualifikation.

EXP-0011-Ausführungs- und GATE-0012-Ergebniswave: PROJECT_SEMANTIC,
RUNTIME_EMPIRICAL und FOUNDATION_INTEGRITY lokal validiert am 2026-08-31
unter Windows und Python 3.12.10. Der commitgebundene Lauf aus Preimage
`a5aeb0196d8d6a32fc90da46ca158ba693c6a0db` bestand 14/14 methodische
Kriterien auf 15 synthetischen Paaren; beide Wiederholungen lieferten den
semantischen SHA-256-Wert
`ec22878a8668852498b13181a24387c8f78838e2ee13eefe2c020bdd06df9cc5`.
Der historische Validator rechnete alle Ergebniswerte ohne Experimentlauf
neu. Repository- und v2-Registry-Prüfung waren für 44 Artefakte erfolgreich.
Der kontrollierte Testlauf entdeckte 185 Tests, ersetzte genau drei
Current-Preimage-Ergebnisprüfungen durch Historical-Preimage-Prüfungen und
führte 182 Tests erfolgreich aus. `compileall` und `git diff --check` waren
erfolgreich. FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Dies belegt Ausführung, Begrenzung und Entscheidungsreife,
nicht die Auswahl eines Zielvertrags oder eine Produktänderung.

GATE-0011-Auswahl- und EXP-0011-Planungswave: PROJECT_SEMANTIC, bestehende
RUNTIME_EMPIRICAL-Regression und FOUNDATION_INTEGRITY lokal validiert am
2026-08-31 unter Windows und Python 3.12.10. Repository- und v2-Registry-
Prüfung waren für 43 Artefakte erfolgreich. TEST-0001 bestätigte 30 Fälle
und 49 Komponenten; EXP-0002 bis EXP-0007, die historischen EXP-0009- und
EXP-0010-Ergebnisse sowie die eingecheckten WI-0005-, WI-0008-, WI-0011-
und WI-0012-Produktnachweise blieben gültig. Der kontrollierte Testlauf
entdeckte 178 Tests, ersetzte genau zwei veraltete Current-Preimage-
Ergebnisprüfungen eins zu eins durch Historical-Preimage-Prüfungen und
führte 176 Tests erfolgreich aus. `compileall` und `git diff --check` waren
erfolgreich. FOUNDATION_INTEGRITY am exakten Quellcommit
`d49f978f33001fcc098998ff7c04ffb209b28033` meldete 0 Warnungen, 0 Fehler
und 0 Blocker. Dies belegt Auswahl, Registrierung und Begrenzung von
EXP-0011, nicht die noch ausstehende Experimentausführung, einen führenden
Variantenbefund oder eine Produktübernahme.

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

WI-0015 ist abgeschlossen: Foundation 1.8.0 ist manifestgetreu und semantisch
integriert; der einzige neue Feature-Kandidat `rule-context-cache` ist
`RECOMMENDED`, seine optionale Referenzimplementierung aber nicht ausgewählt.
Die Produktfortsetzung bleibt davon unabhängig.

WI-0011, EXP-0009, GATE-0009, EXP-0010, GATE-0010, WI-0012, GATE-0011,
EXP-0011, GATE-0012, WI-0013, GATE-0013, GATE-0014, EXP-0012, GATE-0015,
EXP-0013, GATE-0016, EXP-0014, GATE-0017, EXP-0015, GATE-0018, EXP-0016,
GATE-0019, EXP-0017, GATE-0020 und WI-0014 sind abgeschlossen. Der Nutzer hat
in GATE-0020 ausdrücklich Option B gewählt. Der enge review-beibehaltende
V2-Produktvertrag bestand 16/16 commitgebundene Kriterien. Human- und
Standard-JSON-Ausgabe bleiben bytekompatibles V1; nur
`--json --report-version v2` aktiviert die pfadfreie Kontexterklärung. Das
WI-0004-Review-Gate bleibt unverändert. GATE-0021 ist `done`; der Nutzer hat
Option A gewählt. Der qualifizierte V2-Vertrag bleibt als enges explizites
JSON-Opt-in stabil. Es wird kein Folgearbeitsgegenstand registriert.
Automatische Suche, mehrere Dateien, IDs oder Bibliotheken, neue
Calibre-Felder, externe Metadaten, Persistenz, Routing, Browser, REST, Agents
und Writes bleiben nicht autorisiert.

## Offene Punkte

- Die optionale Foundation-Fähigkeit `rule-context-cache` ist empfohlen, aber
  nicht ausgewählt. Eine spätere Einführung benötigt eine eigene Bewertung
  des lokalen, nicht versionierten Cacheziels; semantische Analysen dürfen
  nicht persistent gespeichert werden.
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
