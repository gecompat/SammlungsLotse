# GATE-0016: Ergebnis nach EXP-0013 und geschlossene private Ingress-Gates bewerten

Status: DONE — OPTION A / EXP-0014 AUSGEWÄHLT

Stand: 2026-09-01

Artifact: GATE-0016

## Zweck

Dieses Gate bewertet den methodisch bestandenen, fachlich jedoch
`not_qualified` gebliebenen EXP-0013-Befund. Es trennt die nun lokalisierte
Ingress-Lücke von jeder Produktkorrektur. Ohne ausdrückliche Auswahl wird
weder ein Folgeexperiment noch ein Produktarbeitsgegenstand registriert.

## Auswahlentscheidung

Der Nutzer hat Option A am 2026-09-01 ausdrücklich ausgewählt. GATE-0016 ist
damit abgeschlossen und ausschließlich EXP-0014 als akzeptiertes, noch nicht
ausgeführtes Experiment registriert.

Die Auswahl autorisiert die getrennte Planung und Ausführung der
produktcodefreien Intake-Ursachenqualifizierung nach Merge und
Post-Merge-Prüfung. Sie autorisiert keine Reparatur, Produktdiagnostik oder
Produktänderung. B, C, K und P bleiben nicht ausgewählt.

Da private Locators und Rohberichte absichtlich nicht aufbewahrt wurden,
müssen genau dieselben drei EPUBs für den späteren Hauptlauf erneut explizit
übergeben und als derselbe EXP-0013-Eingangssatz bestätigt werden. EXP-0014
führt keine Verzeichnis- oder Dateisuche aus.

## Verifizierte Evidenz

- Das saubere Ausführungspreimage ist Commit
  `6d32f5dad32481ef9ec163e742acb1ae77aaf226`.
- Drei tatsächliche synthetische WI-0011-Positivkontrollen, neun
  Negativkontrollen und zwei semantisch identische Aggregationswiederholungen
  bestanden.
- Der ausdrücklich bestätigte private Hauptlauf nahm genau drei reguläre
  EPUBs, materialisierte eine task-private Calibre-Bibliothek und führte vier
  gebundene V1-/V2-Suchen aus.
- Alle drei WI-0011-Läufe endeten `not_assessed`; alle drei einzigen
  Reason-Codes lauteten `ingress.preflight_gate_not_open`.
- Die Eintrittsstufenaggregation lautet: `ingress_preflight=3`, alle anderen
  Stufen einschließlich `unclassified=0`.
- Quellen blieben bytegleich unverändert. Ergebnis, Taskmaterial und
  Container wurden pfadfrei beziehungsweise vollständig bereinigt; private
  Metadaten, Locators, Hashes, Querys, IDs und Rohoutputs wurden nicht
  aufbewahrt.
- Das 561-Byte-Ergebnis besitzt ausschließlich zwölf erlaubte Gruppenfelder
  und den SHA-256-Wert
  `6ea2a583956602466edc5b8c11f658d86b975f22ca2b96821c22e4a21265b941`.

## Interpretation

Calibre-Materialisierung und die vier gebundenen Suchläufe funktionierten.
Der Nichtabschluss liegt nicht im Record-Handoff oder in der
Identitätsanalyse, sondern bereits in der vorhandenen WI-0011-Ingress-
Vorprüfung.

Der breite Reason-Code sagt nicht, welche konkrete Intake-Beobachtung das
Gate für die drei privaten EPUBs geschlossen hat. Standardsgültigkeit,
Bibliografie oder Identität lassen sich daraus ebenso wenig ableiten wie ein
Produktfehler. Eine genauere private Ursachenanalyse wäre eine neue, enger
gebundene Evidenzfrage.

## Optionen

### A — Private Intake-Gate-Ursachen produktcodefrei qualifizieren

**Ausgewählt als EXP-0014.**

Ein Folgeexperiment verwendet höchstens dieselben drei erneut explizit
bestätigten EPUBs und den unveränderten vorhandenen Intake-Weg. Es darf nur
pfadfreie Gruppenhäufigkeiten der bestehenden Gate-Aktion sowie der bereits
öffentlichen Beobachtungs- und Grundcodes ausgeben. Einzelwerte, Rohberichte,
Pfade, Hashes, Metadaten und Produktänderungen bleiben ausgeschlossen.

### B — Ausschließlich synthetische Intake-Matrix vertiefen

Eine synthetische Wave erweitert TEST-0001-Kontrollen für bekannte offene und
geschlossene Intake-Gates. Sie benötigt keine privaten Dateien, kann den
realen dreifachen Nichtabschluss aber nicht ursächlich zuordnen.

### C — Produktdiagnostik getrennt erwägen

Ein späterer Produktarbeitsgegenstand könnte eine explizite, datenschutzarme
Erklärung geschlossener Ingress-Gates untersuchen. Diese Option registriert
noch keinen Produktcode und benötigt vor jeder Umsetzung einen eigenen
akzeptierten Vertrag.

### K — Evidenz konservieren

EXP-0013 bleibt als abgeschlossener Befund erhalten. Es folgt weder ein
Experiment noch Produktarbeit.

### P — E-Book-Identitätszweig pausieren

Der Zweig wird ausdrücklich pausiert. Andere SammlungsLotse-Themen bleiben
unberührt.

## Empfehlung

A ist die kleinste evidenzschließende Fortsetzung. Sie nutzt nur bestehende
read-only Produktoberflächen und könnte unterscheiden, ob ein bekannter
Schutz-, Container-, Stabilitäts- oder Reviewgrund vorliegt. B vermeidet
private Eingänge, beantwortet aber die reale Lücke nicht. C wäre verfrüht,
solange die Ursache unbekannt ist.

Die Empfehlung nahm A für sich noch nicht an. Der Nutzer hat A inzwischen
ausdrücklich ausgewählt. EXP-0014 bindet deshalb genau die produktcodefreie
Ursachenqualifizierung; eine Reparatur oder Produktübernahme benötigt
unabhängig vom Ergebnis ein neues getrenntes Gate.

## Harte Grenzen

- kein automatisches Ableiten einer Reparatur aus `not_qualified`;
- keine Änderung an WI-0011 oder unter `src/sammlungslotse/`;
- keine Verzeichnis-, Glob-, Index- oder rekursive private Suche;
- keine privaten Einzelwerte, Metadaten, Locators, Hashes oder Rohoutputs;
- kein Netzwerk, keine direkte Datenbanknutzung und keine Persistenz;
- kein Schreibzugriff auf ein führendes Fachsystem;
- jede Fortsetzung benötigt eine ausdrückliche Auswahl und einen getrennten
  akzeptierten Vertrag.

## Gate-Stand

- GATE-0016 ist `done`.
- EXP-0014 ist `accepted`, aber noch nicht ausgeführt.
- B, C, K und P sind nicht ausgewählt.
- Kein Produktarbeitsgegenstand ist registriert; Produktcode bleibt
  unverändert.
- Die Ausführung beginnt erst in einer neuen isolierten Wave vom gemergten
  `origin/main` und benötigt die erneute explizite Übergabe derselben drei
  privaten EPUBs.
