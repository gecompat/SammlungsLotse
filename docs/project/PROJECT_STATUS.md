# Projektstatus

Status: AUTHORITATIVE

Stand: 2026-08-27

## Phase

Angenommene Planung des ersten eng begrenzten Produktprototyps nach
ergebnisoffener E-Book-Erkundung.

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
- als WI-0004 angenommener Vertrag für einen lokalen read-only
  Eingangstriage-Prototyp mit In-Memory-Snapshot, flachem Preflight,
  getrennter Evidenz und sichtbarer CLI-Folgeaktion; Implementierung beginnt
  erst nach dem kanonischen Plan-Merge.

## Nicht vorhanden

- Produktcode;
- ausgewählter Technologie-Stack;
- Laufzeit- oder Deploymentkonzept;
- Produktdatenbank oder Suchindex;
- öffentliche REST-, Agent-, CLI- oder Browser-Schnittstelle;
- angenommener Entwicklungsbacklog oder freigegebene technische Roadmap;
- übernommener FolioTone-Code;
- Release.

## Validierung

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
Produktlaufzeit oder fachliche E-Book-Akzeptanz; Produktcode existiert nicht.

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

Nach dem kanonischen Merge der angenommenen WI-0004-Planung beginnt eine neue
Implementierungs-Wave vom exakten `origin/main`. Sie implementiert und prüft
nur Snapshot, flachen Preflight, gemeinsamen Ergebnisvertrag und lokale CLI.
Calibre, tiefe Formatprüfung, Dubletten, Metadaten, Routing, Persistenz,
Browser, REST, Agents und Writes bleiben außerhalb.

## Offene Punkte

- Eine professionelle Markenähnlichkeitsprüfung ist vor einer wirtschaftlich
  wesentlichen breiten Vermarktung weiterhin erforderlich.
- Eine spätere Entscheidung kann getrennte Core-Safety- und CI-Gates-Rulesets
  mit eng begrenztem Pull-Request-only-Bypass ausschließlich für nachgewiesene
  `INFRASTRUCTURE_UNAVAILABLE`-Fälle bewerten. Bis dahin bleibt jeder fehlende
  erforderliche Check merge-blockierend.

## Blocker

Keine bekannten Blocker für WI-0004. Produktimplementierung bleibt bis zum
kanonischen Merge des angenommenen Arbeitsgegenstands nicht autorisiert.
Schreibende Fähigkeiten bleiben unabhängig davon hinter einem eigenen
Writer-Gate.
