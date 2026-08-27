# Projektstatus

Status: AUTHORITATIVE

Stand: 2026-08-27

## Phase

Erster eng begrenzter Produktprototyp, reversible Snapshot-Übergabewave und
WI-0005 vollständig ausgeführt. Der erste tiefe read-only Produktadapter ist
eng begrenzt implementiert und mit einem exakten lokalen Podman-Profil
synthetisch qualifiziert.

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
  `Kern`-Fällen, 44 manifestierten Komponenten und vier weiterhin offenen
  `Ausbau`-Fällen;
- netzwerkloser, ausschließlich auf der Python-Standardbibliothek beruhender
  Generator und read-only Validator für die aktive TEST-0001-Fixture-Version
  `0.2.0`; der unveränderte historische Snapshot `0.1.0` bleibt erhalten;
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

## Nicht vorhanden

- allgemeiner Technologie-Stack jenseits der reversiblen WI-0004-Auswahl;
- allgemeines Laufzeit- oder Deploymentkonzept jenseits des eng begrenzten
  WI-0005-Executors;
- Produktdatenbank oder Suchindex;
- öffentliche REST-, Agent- oder Browser-Schnittstelle sowie eine
  produktqualifizierte allgemeine CLI;
- angenommener Entwicklungsbacklog oder freigegebene technische Roadmap;
- übernommener FolioTone-Code;
- Release.

## Validierung

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

WI-0005 ist `done`. Vor einer weiteren Erkenntnis- oder Produktwave ist neu
zu entscheiden, welche offene Qualitäts- oder Nutzerfrage als Nächstes den
höchsten Erkenntniswert besitzt. Die Implementierung autorisiert weder einen
zweiten Provider noch Ace, Calibre, Dubletten, Metadaten, Routing, dauerhafte
Persistenz, Browser, REST, Agents, native Windows-Ausführung oder Writes.

## Offene Punkte

- Eine professionelle Markenähnlichkeitsprüfung ist vor einer wirtschaftlich
  wesentlichen breiten Vermarktung weiterhin erforderlich.
- Eine spätere Entscheidung kann getrennte Core-Safety- und CI-Gates-Rulesets
  mit eng begrenztem Pull-Request-only-Bypass ausschließlich für nachgewiesene
  `INFRASTRUCTURE_UNAVAILABLE`-Fälle bewerten. Bis dahin bleibt jeder fehlende
  erforderliche Check merge-blockierend.

## Blocker

Keine bekannten Blocker im abgeschlossenen WI-0005-Vertrag. Jede Änderung an
Provider, Version, Runtime, Image, Executor oder Nutzeroberfläche verlangt
eine neue Bewertung und Qualifikation. Schreibende Fähigkeiten bleiben
unabhängig davon hinter einem eigenen Writer-Gate.
