# Übergabe

Status: AUTHORITATIVE

Stand: 2026-08-31

## Aktueller Stand

SammlungsLotse ist als eigenständiges Projekt initialisiert. Nach
ergebnisoffener E-Book-Erkundung ist WI-0004 als erster eng begrenzter,
reversibler Produktprototyp implementiert und lokal vollständig abgenommen.
AI Repository Foundation 1.7.0 ist semantisch integriert. Die Bewertung steht
unter docs/governance/FOUNDATION_UPGRADE_1_7.md.

main ist geschützt. Änderungen benötigen die erfolgreichen Checks
repository-quality und registry-integrity.

Die maßgeblichen Produktgrenzen stehen in docs/product/PROJECT_CHARTER.md und
docs/architecture/BOUNDARIES.md. Die Startentscheidungen stehen unter
docs/decisions/.

Der aktuelle E-Book-Brainstorming-Stand steht unter
docs/planning/EBOOK_LANDSCAPE.md. Die weitere Erkenntnisreihenfolge steht
unter docs/planning/EBOOK_EXPLORATION_PLAN.md. WI-0002 ist `done`. Die
Neubewertung unter docs/planning/EBOOK_GATE_0001_COMPARISON.md hat die
Eingangstriage als eng begrenzten ersten read-only E-Book-Vertikalablauf
angenommen; GATE-0001 ist `done`. Bestandsprüfung bleibt ein möglicher
späterer Ast.

WI-0003 ist auf Dokumentationsebene abgeschlossen. Die sechs
Nutzerentscheidungen und Messverträge stehen unter
docs/planning/EBOOK_SCENARIOS_AND_METRICS.md. TEST-0001 ist unter
docs/planning/EBOOK_REFERENCE_CORPUS.md als aktive Fixture-Version `0.3.0`
mit allen 26 `Kern`- und vier `Ausbau`-Fällen, 49 Komponenten, Hashes,
Herkunft und Oracles ausführbar und validiert; `0.1.0` und `0.2.0` bleiben
historische Snapshots. EXP-0002 bis EXP-0007 und WI-0005 bleiben an den
historischen Snapshot `0.2.0` gebunden. EXP-0005 ist mit elf erfolgreichen
Isolationskriterien abgeschlossen. EXP-0002 ist mit dreizehn erfolgreichen
Calibre-Projektionskriterien abgeschlossen; der direkte read-only Mount ist
als nicht unterstützt und die Copy-on-read-Grenze als erfolgreich belegt.
EXP-0003 ist mit vierzehn erfolgreichen Evidenzkriterien abgeschlossen:
EPUBCheck- und Ace-Rohberichte bleiben getrennt und verlustfrei, unbekannte
Codes sowie manueller Prüfbedarf bleiben sichtbar. Das erprobte Ace-Profil
ist wegen deaktivierter Chromium-Sandbox und offener npm-Advisories nicht
produktqualifiziert. GitHub Dependabot meldet zusätzlich elf offene Befunde,
zehn `high` und einen `moderate`, ausschließlich im eingefrorenen
EXP-0003-Ace/npm-Baum. EXP-0004 ist mit fünfzehn erfolgreichen Kriterien
abgeschlossen: Sechs Sollpaare bleiben auf fünf Identitätsebenen getrennt,
Kandidaten zeigen positive und negative Evidenz, fehlende Evidenz bleibt
separat und Leseprobe/Vollausgabe führt auf Ausgabenebene zur Enthaltung. Die
perfekten Werte des kleinen synthetischen Goldstandards sind keine
Produktprognose. EXP-0006 ist mit 16 erfolgreichen Kriterien abgeschlossen:
Alle elf vorab gebundenen Preflight-Zeilen stimmen in zwei semantisch
identischen Wiederholungen überein, acht Fälle bleiben außerhalb des tiefen
Werkzeugwegs, drei positiv gegatete Kontrollen starten ihn und kritische
Fehlfreigaben betragen null. Alle Verträge und Ergebnisgrenzen stehen unter
docs/planning/EBOOK_EXPERIMENTS.md.

GATE-0002, EXP-0007 und GATE-0003 sind `done`. EXP-0007 hat V1 und V2 unter
getrennten Windows- und Linux/Podman-Profilen qualifiziert und V3 wegen
Originalpfadweitergabe und reproduzierter TOCTOU-Lücke abgelehnt. GATE-0003
wählt V2, die task-private hashgebundene Materialisierung, als Standardnaht.
Die getrennte aktuelle Werkzeug- und Vertragsbewertung nahm WI-0005 an. Die
anschließende Implementierungs-Wave ist `done`: EPUBCheck 5.3.0 läuft hinter
providerneutralem Handoff- und Prozessport, V2 materialisiert task-privat und
hashgebunden, und das frisch gebundene Linux/amd64-Podman-Profil mit Temurin
`21.0.12.1+1` ist reproduzierbar gebaut und 12/12 synthetisch qualifiziert.
Der tiefe Lauf bleibt expliziter CLI-Opt-in nach positivem Preflight.

WI-0006 ist als nächste Produktwave angenommen, implementiert und in
`docs/planning/EBOOK_MULTI_FILE_INTAKE_REPORT.md` begrenzt. Sie verarbeitet
mehrere ausdrücklich angegebene Dateien vollständig und sequenziell über die
vorhandenen Einzelverträge. Die schnelle Prüfung bleibt Standard, der
tiefe EPUBCheck-Weg bleibt Opt-in. Die synthetische Abnahme umfasst 99 Tests
und zwei tatsächliche getrennte EPUBCheck-Läufe mit vollständigem Cleanup.

WI-0007 ist als nächste getrennte Produktwave angenommen und unter
`docs/planning/CALIBRE_READ_ONLY_PROJECTION_WORK_ITEM.md` vollständig
begrenzt. Genau eine explizite lokale Calibre-Bibliothek soll über eine
task-private Copy-on-read-Arbeitskopie und Calibre 9.13.0 pfadfrei auf ID,
Titel, Autoren, Sprachen und Formate projiziert werden. Die getrennte
Implementierungs-Wave ist abgeschlossen: Das Image wurde zweimal
reproduzierbar gebaut, der Adapter implementiert und die tatsächliche
synthetische Produktqualifikation bestand 17/17 Kriterien einschließlich
tatsächlichem Timeout und tatsächlicher Rohoutput-Grenze.

GATE-0004 ist `done`. Es hat die Härtung des vorhandenen synthetischen
Calibre-Vertrags, Mehrbibliothekszugriff und eine neue Qualitätsfunktion
getrennt verglichen und WI-0008 ausgewählt. WI-0008 ist `done`: Eine
eingecheckte, reproduzierbare und mehrgliedrige synthetische Calibre-
Materialisierung samt Oracles wurde ergänzt. Sie reproduzierte die echte
`calibredb`-Mehrfachautorenform, führte zu einer eng getesteten Parserkorrektur
und bestand danach 29/29 Kriterien. Produktoberfläche, Feldprojektion,
Einzelbibliotheks- und Read-only-Grenzen bleiben unverändert.

GATE-0005 ist `done`. Es hat einen expliziten Zwei-EPUB-Paarvergleich, einen
Vergleich gegen Calibre sowie neue Provider- oder Mehrbibliotheksflächen
getrennt bewertet und WI-0009 ausgewählt. WI-0009 ist `done`: Genau zwei
ausdrückliche unveränderliche EPUB-Snapshots werden über einen pfadfreien,
erklärbaren Identitätskandidatenbericht verglichen. Kandidaten, negative und
fehlende Evidenz sowie Enthaltung bleiben getrennt. Der eingecheckte
Produktnachweis bestand 16/16 synthetische Kriterien; es gibt keine
Bestandsaktion.

WI-0010 ist `done`. Die reine Härtungswave bindet jetzt alle tatsächlich am
WI-0005-CLI-Lauf beteiligten Intake-Pythonmodule und den Runner automatisch
an den Produktnachweis. Das unveränderte EPUBCheck-Profil wurde erneut 12/12
qualifiziert; aktive synthetische Grenzproben für Netzwerk, PID, RAM, CPU,
Unterbrechung, Recovery und Eingangslimit wurden getrennt dokumentiert.
Parallelbetrieb bleibt ausdrücklich nicht qualifiziert.

GATE-0006 ist `done`. Es hat fünf Anschlussoptionen getrennt bewertet und
EXP-0008 als kleinste nächste Erkenntniswave ausgewählt. Der angenommene
Experimentvertrag prüft genau eine explizite Calibre-ID, ausschließlich EPUB,
Bytegleichheit, task-private Copy-on-read-Grenzen, Negativfälle und Cleanup
mit synthetischem TEST-0001-Material. Die getrennte Ausführung ist mit 16/16
Kriterien abgeschlossen; eine Produktwave ist damit nicht freigegeben.

GATE-0007 ist `done`. Es hat den expliziten Einzelrecord-Vergleich,
Bestandsqualitätsübersicht, Mehrbibliotheks-/Routing-Arbeit, neue
Provider-/Architekturflächen und Pausieren getrennt bewertet. WI-0011 ist als
kleinste read-only Produktwave `done`: genau ein Eingangs-EPUB, eine
Bibliothek und eine externe Calibre-ID, providerneutraler Snapshot-Handoff,
unveränderter fünfstufiger Identitätsbericht und keine Bestandsaktion. Der
eingecheckte Nachweis bindet das Preimage `d70c6de` und bestand 23/23
ausschließlich synthetische Kriterien. Nach WI-0012 wurde der abhängige Weg
gegen den neuen Analyzer-Preimage `97017a2` tatsächlich erneut 23/23
qualifiziert.

## Fortsetzung

WI-0004 ist `done`. Der Produktcode liegt unter
`src/sammlungslotse/ebook_intake/`, die sichtbare lokale Oberfläche unter
`tools/run_ebook_intake.py`. Die Grenze endet nach stabilem
In-Memory-Snapshot, flachem Preflight und sichtbar begründeter CLI-Folgeaktion
oder Enthaltung. Calibre, tiefe Formatprüfung, Dubletten, Metadaten, Routing,
Persistenz, Browser, REST, Agents und jeder Writer bleiben außerhalb.

WI-0005 ist abgeschlossen. Der kanonische Vertrag und seine Abnahme stehen
unter `docs/planning/EBOOK_DEEP_READONLY_ADAPTER_WORK_ITEM.md`; Bereitstellung
und Bedienung des exakten Profils stehen unter
`runtime/ebook-deep-readonly/README.md`. WI-0010 hat die vollständige
Laufzeit-Preimage-Bindung und zusätzliche aktive Grenznachweise ergänzt,
ohne den Produktvertrag zu erweitern. Die anschließende Bewertung hat
WI-0006 als kleinen read-only Mehrdatei-Bericht ausgewählt; seine
Implementierung ist abgeschlossen. Eine weitere Produktwave ist nicht
automatisch freigegeben. WI-0006 entscheidet insbesondere keinen zweiten
Provider, keine allgemeine Containerstrategie und keine schreibende Fähigkeit.

WI-0007 ist `done`. Produktport, Copy-on-read-Grenze, exaktes
Calibre-9.13.0-Profil sowie deutsche und stabile JSON-CLI liegen unter
`src/sammlungslotse/calibre_inventory/`, `runtime/calibre-readonly/` und
`tools/run_calibre_inventory.py`. WI-0008 ist als reine synthetische
Härtungswave abgeschlossen. Eine weitere Produktwave ist nicht automatisch
freigegeben. Insbesondere sind mehrere Bibliotheken, automatische Erkennung,
Content Server, Persistenz und Writer weiterhin außerhalb.

WI-0009 ist abgeschlossen. Produktcode und CLI liegen unter
`src/sammlungslotse/ebook_identity/` und `tools/run_ebook_identity.py`, der
reproduzierbare Nachweis unter `runtime/ebook-identity/`. WI-0009 selbst
enthält keinen Calibre-Adapter, keine Verzeichnissuche, mehr als zwei
Eingänge, Persistenz, Routing oder Writes.

EXP-0008 ist abgeschlossen. Der pfadfreie Nachweis liegt unter
`experiments/ebook/exp-0008/`; das genaue Preimage ist `fb08732b`. Die
unterstützte Calibre-Einzelrecord-Übergabe ist nur synthetisch technisch
qualifiziert. GATE-0007 hat daraufhin WI-0011 angenommen.

WI-0011 ist abgeschlossen. Providerneutraler Port, Adapter, Anwendung und
CLI liegen unter `src/sammlungslotse/ebook_calibre_identity/` und
`tools/run_ebook_calibre_identity.py`; Profil und 23/23-Produktnachweis unter
`runtime/ebook-calibre-identity/`. Der tatsächliche Lauf belegte
Bytegleichheit, Repackaging, Enthaltung, Grenzen, Recovery und vollständiges
Cleanup. Nach der WI-0012-Guardrail-Änderung bestand der aktuelle Nachweis
gegen Preimage `97017a2` und das unveränderte Calibre-9.13.0-Image erneut
23/23 Kriterien. Automatische Suche, mehrere Dateien, IDs oder Bibliotheken,
Persistenz, Routing, UI, REST, Agents und Bestandswirkungen bleiben außerhalb.
Vor einer weiteren Produktwave ist erneut getrennt zu bewerten.

WI-0012 ist abgeschlossen. Der öffentliche WI-0009-v1-Berichtsvertrag und
die fünf Ebenen blieben unverändert; `candidate_same` auf Ausgabenebene
benötigt jetzt zusätzlich gleiche Repräsentation und kompatible Metadaten.
Der aktuelle v2-Produktnachweis bindet den Preimage-Commit `97017a2`, fünf
TEST-0001-Paare und acht konforme EXP-0010-Qualitätsfälle. Er bestand 19/19
Kriterien und reduzierte die sechs kritischen False Same auf null. Zwei
`candidate_related`-Werkabweichungen bleiben ausdrücklich sichtbar.
Metadatenmodell v2, Publikationsstufe, Collection-Neumodellierung, Suche,
Persistenz und Writes bleiben außerhalb.

GATE-0008 ist ausgewertet und EXP-0009 abgeschlossen. Zwei unabhängige Läufe
über 18 vorab gebundene synthetische Paare erfüllten 12/12 methodische
Kriterien. Die damalige Produktqualität war `not_qualified`: Der Fall
`metadata-collision-work-conflict` erzeugte trotz verschiedener Inhalte und
widersprüchlicher Werkreferenzen `candidate_same` auf Ausgaben- und
Werkebene. Das Experiment selbst veränderte keinen Produktcode; der später
ausgewählte WI-0012-Guardrail beseitigt diese kritischen Freigaben, ohne den
historischen Befund umzuschreiben. Kandidatensuche, Architektur, Provider,
Persistenz, UI, API, Agents und Writers bleiben unentschieden.

GATE-0009 ist mit der ausdrücklichen Auswahl von Option A abgeschlossen. Die
aktuelle
Primärquellenprüfung zeigt, dass `belongs-to-collection` Collection-
Mitgliedschaft und keine Werk-ID beschreibt und dass der Produktparser den
primären EPUB-Identifier nicht von zusätzlichen Identifiern trennt. Auch die
EXP-0009-Matrix bindet diese Rollen noch nicht standardkonform. EXP-0010 ist
deshalb als genau eine produktcodefreie Evidence-Repair-Wave angenommen und
ausgeführt. Der methodische Nachweis bestand 12/12: 16 konforme Einzelpakete
bestanden EPUBCheck, vier absichtlich ungültige Kontrollen wurden korrekt
abgewiesen und beide Produktwiederholungen waren semantisch identisch. Die
Produktqualität ist wegen sechs kritischer False Same auf Ausgabe und Werk
`not_qualified`. Publikationsstufe, Identifier-Rollen und Collection-Semantik
fehlen getrennt. Der Nutzer hat für GATE-0010 ausdrücklich Option A gewählt.
GATE-0010 und WI-0012 sind `done`. Der Guardrail ist synthetisch qualifiziert;
EXP-0010 und seine Oracles blieben unverändert und sind über den historischen
Git-Preimage-Validator weiterhin 12/12 prüfbar.

GATE-0011 ist als getrenntes Ergebnisgate registriert und
entscheidungsbereit. Es trennt die zwei schwächeren `candidate_related`-
Werkabweichungen von der irreführend eingeebneten Collection-Semantik, den
fehlenden Identifier-Rollen und der fehlenden Publikationsstufe. Option A,
eine produktcodefreie Vertrags- und Evidenzwave, ist empfohlen, aber noch
nicht ausgewählt. A, B, C, D, E, F und K bleiben offen; weder EXP-0011 noch
WI-0013 ist registriert. Die nächste zulässige Aktion ist die ausdrückliche
Nutzerauswahl, nicht Produktimplementierung.

## Harte Grenzen

- Fachsysteme bleiben führend.
- Kein FolioTone-Code wird ohne Rechte- und Eignungsprüfung übernommen.
- Kein reales privates Sammlungsmedium gelangt in Git.
- Produktcode wird nicht ohne registrierten Arbeitsgegenstand begonnen.
- Schreibende Fähigkeiten benötigen eine eigene Entscheidung und vollständige
  Sicherheitskette.

## Noch nicht entschieden

- erste vollständige Medienlinie jenseits des WI-0004-Prototyps;
- Programmiersprache und Laufzeit jenseits der reversiblen WI-0004-Auswahl
  Python 3.12 mit Standardbibliothek und des eng begrenzten, austauschbaren
  WI-0005-Prozessadapters;
- Persistenz und Suche;
- Deployment und UI;
- konkrete REST- und Agent-Verträge;
- konkrete FolioTone-Wiederverwendung;
- Tiefe der ersten Formatunterstützung und konkrete Qualitätsprofile;
- Accessibility- und externe Metadatenprovider-Adapter sowie weitere tiefe
  Werkzeugprovider jenseits EPUBCheck 5.3.0; der enge Calibre-
  Bestandsprovider ist mit WI-0007 implementiert, nicht aber weitere
  Calibre-Felder oder -Operationen;
- weitere empirisch qualifizierte Produktprofile jenseits des engen
  WI-0005-EPUBCheck-Profils; EXP-0002 qualifiziert nur den
  Copy-on-read-Calibre-Zugriff, EXP-0003 nur eine Evidenzprojektion mit nicht
  produktqualifiziertem Ace-Profil, EXP-0004 nur eine kleine synthetische
  Identitätsheuristik, EXP-0005 nur einen wegwerfbaren Sicherheitsweg und
  EXP-0006 nur einen kleinen synthetischen Preflight;
- ein optionales Repository-Continuity-Verfahren mit getrennten Rulesets,
  autorisierten Akteuren und Ausfallschwelle. Bis zu einer angenommenen
  Entscheidung existiert kein Break-Glass-Bypass.

## Validierung

Die aktuellen Prüfergebnisse stehen ausschließlich in
docs/project/PROJECT_STATUS.md.
