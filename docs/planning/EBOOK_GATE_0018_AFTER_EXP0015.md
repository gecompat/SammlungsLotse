# GATE-0018: EXP-0015-Ergebnis und gemeinsamen Navigationskontext bewerten

Status: DONE — OPTION A / EXP-0016 AUSGEWÄHLT

Stand: 2026-09-01

Artifact: GATE-0018

## Zweck

Dieses Gate bewertet den methodisch bestandenen EXP-0015-Befund. Es trennt
die gemeinsame grobe Kontextklasse von jeder Aussage über Gefährlichkeit,
Erreichbarkeit, EPUB-Gültigkeit oder eine erforderliche Produktkorrektur.
Ohne ausdrückliche Auswahl wird weder ein Folgeexperiment noch ein
Produktarbeitsgegenstand registriert.

## Auswahlentscheidung

Der Nutzer hat Option A am 2026-09-01 ausdrücklich ausgewählt. GATE-0018 ist
damit abgeschlossen und ausschließlich EXP-0016 als akzeptiertes, noch nicht
ausgeführtes Experiment registriert.

Die Auswahl autorisiert nach Merge, Post-Merge-Prüfung und einem sauberen
Ausführungspreimage nur die rein synthetische Navigationskontext- und
Sicherheitsmatrix. Sie autorisiert keine weitere private Analyse, keine
Produktregel und keine Lockerung oder Umgehung des bestehenden
WI-0004-Review-Gates. B, C, K und P bleiben nicht ausgewählt.

## Verifizierte Evidenz

- Das saubere Ausführungspreimage ist Commit
  `cefe2d29b54b8e6cbc60b07b1485da473565cda7`; beide erforderlichen
  GitHub-Checks bestanden vor dem privaten Lauf auf exakt diesem Commit.
- Sieben von sieben Kontextklassen, 19 von 19 Negativkontrollen und
  32 synthetische Parserläufe bestanden; beide Aggregationswiederholungen
  waren identisch.
- Der Nutzer hatte denselben Satz aus genau drei privaten EPUBs erneut
  bestätigt. Jede neutrale task-private Kopie durchlief genau einmal den
  gebundenen lokalen Parser.
- Alle drei Eingänge enthielten mindestens eine vom WI-0004-Muster erfasste
  HTTP(S)-Remote-Referenz.
- Die einzige sichtbare Kontextklasse ist `content.navigation=3`. Es gab
  keine nur einmal vertretene bekannte Klasse und keinen unklassifizierten
  Eingang.
- Private Werte, URLs, Domains, Inhalte, ZIP-Eintragsnamen, Vorkommenszahlen,
  Einzelzuordnungen, Locators, Pfade, Eingangshashes und Rohoutputs wurden
  nicht aufbewahrt.
- Quellen blieben bytegleich unverändert; Taskmaterial wurde vollständig
  bereinigt.
- Das 483-Byte-Ergebnis ist über SHA-256
  `651ad195b54531d20e0fc6ff882df6e1d4b38765e877057faf7858f36dae50a1`
  an das historische Preimage gebunden.

## Interpretation

Innerhalb der vorab gebundenen Projektion beruhen die drei bestehenden
WI-0004-Reviewentscheidungen gemeinsam auf Navigationskontext. Weil keine
seltene Klasse unterdrückt wurde und kein Eingang unklassifiziert blieb,
trat in diesem Dreiersatz keine weitere gebundene Kontextklasse auf.

Der Befund enthält absichtlich weder Vorkommenszahlen noch konkrete Tags,
Dokumentstellen oder Einzelzuordnungen. Er belegt insbesondere nicht, ob eine
Referenz erreichbar, vertrauenswürdig, nutzeraktiviert oder automatisch
verarbeitet würde. `content.navigation` ist deshalb weder ein
Unbedenklichkeits- noch ein Schadensnachweis. Das konservative WI-0004-Gate
verhielt sich weiterhin vertragsgemäß.

## Optionen

### A — Rein synthetische Navigationskontext- und Sicherheitsmatrix vertiefen

**Ausgewählt als EXP-0016.**

Ein neues produktcodefreies Experiment könnte ausschließlich synthetisch
externe Hyperlinks, Package-/Content-Navigation, Täuschungsfälle,
Nicht-HTTP(S)-Varianten und die asymmetrischen Kosten einer möglichen
Differenzierung vergleichen. Es würde keine privaten Dateien erneut lesen
und keine Produktregel auswählen.

- Vorteil: schließt die kleinste verbleibende Evidenzlücke vor jeder
  Produktentscheidung;
- Risiko: synthetische Fälle belegen nicht die konkrete Nutzerabsicht oder
  Vertrauenswürdigkeit realer Ziele;
- Einordnung: **empfohlene evidenzschließende Fortsetzung**, falls weiter
  entwickelt werden soll.

### B — Erklärbarkeitsarbeitsgegenstand getrennt erwägen

Ein später separat zu registrierender Produktarbeitsgegenstand könnte das
bestehende `review` beibehalten und ausschließlich eine grobe, pfadfreie
Kontexterklärung untersuchen. Vor Produktcode müssten Datenschutzvertrag,
Kompatibilität, unbekannte Klassen und vollständige synthetische
Produktqualifikation angenommen werden.

### C — Sicherheitsregel oder Review-Lockerung getrennt untersuchen

Eine mögliche Differenzierung zwischen Navigations- und eingebetteten
Remote-Ressourcen hätte höhere False-Negative-Kosten. Sie benötigt vor jeder
Implementierung ein eigenes Threat Model, Täuschungs- und Rückfalltests sowie
einen ausdrücklich angenommenen Produktarbeitsgegenstand. Diese Option ist
keine Freigabe, das aktuelle Review zu umgehen.

### K — Evidenz konservieren und bestehendes Review beibehalten

EXP-0015 bleibt historisch prüfbar. Der aktuelle konservative WI-0004-Weg
bleibt unverändert; die drei Fälle benötigen weiterhin Review.

### P — E-Book-Identitätszweig pausieren

Der Zweig wird ausdrücklich pausiert. Andere SammlungsLotse-Themen bleiben
unberührt.

## Empfehlung

A ist die kleinste datenschutzschonende Fortsetzung, weil sie keine weitere
private Evidenz erhebt und vor einer Produktregel erst die Sicherheits- und
Entscheidungsmatrix klärt. K ist die sichere Endposition, wenn das bestehende
Reviewverhalten genügt. B kann die Verständlichkeit erhöhen, verändert aber
bereits Produktcode. C ist ohne die Evidenz aus A verfrüht.

Die Empfehlung nahm A für sich noch nicht an. Der Nutzer hat A inzwischen
ausdrücklich ausgewählt. EXP-0016 bindet deshalb vorab eine ausschließlich
synthetische, standardsbezogene Kontext-, Täuschungs- und Fehlkostenmatrix.
Unabhängig vom Ergebnis benötigt jede Produktfortsetzung ein neues getrenntes
Gate und für Produktcode zusätzlich einen angenommenen Arbeitsgegenstand.

## Harte Grenzen

- methodischer `pass` und `content.navigation=3` sind keine Produktfreigabe;
- keine automatische Lockerung oder Umgehung des WI-0004-Review-Gates;
- keine weitere private Analyse ohne neuen engen Vertrag und ausdrückliche
  Bestätigung;
- keine Aufbewahrung privater Werte, Locators, Pfade, Hashwerte oder
  Rohoutputs;
- kein Netzwerk, keine Persistenz, kein tiefer Werkzeuglauf und keine
  Bestandswirkung;
- keine Änderung unter `src/sammlungslotse/` ohne getrennt angenommenen
  Produktarbeitsgegenstand.

## Gate-Stand

- EXP-0015 ist `done`; Methode und pfadfreies Aggregat sind historisch
  gebunden.
- GATE-0018 ist `done`.
- EXP-0016 ist `done`; Matrix, Runner und Ergebnis sind historisch gebunden.
- GATE-0019 ist `done`; der Nutzer hat dort Option A ausgewählt.
- EXP-0017 ist `accepted`, aber noch nicht ausgeführt.
- B, C, K und P sind nicht ausgewählt.
- Kein Produktarbeitsgegenstand ist registriert; Produktcode bleibt
  unverändert.
- Die Ausführung erfolgte in einer neuen isolierten Wave vom gemergten
  `origin/main` und gegen ein sauberes Commit-Preimage.
