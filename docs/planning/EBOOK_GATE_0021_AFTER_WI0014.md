# GATE-0021: WI-0014-Ergebnis und sichere Produktfortsetzung bewerten

Status: DONE — OPTION A AUSGEWÄHLT

Stand: 2026-09-02

Artifact: GATE-0021

## Zweck

Dieses Gate bewertet den bestandenen, commitgebundenen WI-0014-
Produktnachweis getrennt von jeder weiteren Produktentscheidung. WI-0014 ist
abgeschlossen. Ohne neue ausdrückliche Nutzerauswahl werden weder ein
Folgearbeitsgegenstand registriert noch Produktcode, öffentlicher Vertrag oder
Review-Gate weiter verändert.

## Verifizierte Evidenz

- Das saubere Ausführungspreimage ist Commit
  `ed7f173896b7365d2f91fb47baa1bc4065c23bcb`. Beide erforderlichen GitHub-
  Checks waren vor dem einmaligen Hauptlauf auf exakt diesem Commit grün.
- Der ausschließlich synthetische Hauptlauf bestand 16/16 Kriterien. Alle 48
  EXP-0016-Fälle wurden zweimal ohne Kontext- oder Schemagruppenmismatch
  klassifiziert; beide Wiederholungen waren identisch.
- Zwölf deterministisch materialisierte EXP-0017-EPUBs durchliefen den
  öffentlichen Einzeldatei-CLI-Weg. V1 und Human-Ausgabe blieben in allen
  zwölf Fällen bytegleich zum gebundenen Ausgangscommit. V2 war in beiden
  Wiederholungen deterministisch und unterschied sich fachlich nur durch die
  additive Kontextprojektion.
- Elf vom bestehenden WI-0004-Gate erkannte Fälle blieben auf `review` und
  `deep_read_only_allowed=false`. Der eine bewusst nicht vom bestehenden
  V1-Muster erkannte Kontrollfall blieb unverändert außerhalb des Reviews und
  erhielt in V2 `not_applicable`; WI-0014 hat ihn nicht neu klassifiziert oder
  freigegeben.
- Einzel-, Batch- und kombinierter V2-Bericht verwendeten ihre gebundenen
  Schemata. Der kombinierte Reviewfall startete keinen Deep-Provider.
- Berichte blieben pfad- und wertfrei, Eingänge bytegleich und Taskmaterial
  vollständig bereinigt. Netzwerk, Persistenz, Writer, private Daten,
  Fachsystem- und Sammlungswirkung fehlten.
- Der eingecheckte Nachweis unter
  `runtime/ebook-intake-context/qualification.json` besitzt SHA-256
  `16b33a98904157593de335ce0aa8a8348f3c1d9a795fdbe34765251a5dbc3046`.
- Die abhängigen Produktnachweise blieben geschlossen und wurden auf dem
  erweiterten Stand tatsächlich erneuert: WI-0005 bestand 12/12 und WI-0011
  mit dem unveränderten Calibre-9.13.0-Image 23/23 Kriterien.

## Interpretation

Der Befund qualifiziert die enge additive V2-Erklärung für die gebundene
synthetische Matrix und den exakten Produktstand. Er belegt keine allgemeine
Sicherheit von EPUB-Inhalten oder Linkzielen, keine Nutzerabsicht, keine
vollständige Abdeckung realer EPUBs und keine Grundlage zur Verringerung des
manuellen Reviews. V1 bleibt Standard; V2 bleibt ausschließlich explizites
JSON-Opt-in. Das WI-0004-Review-Gate bleibt unverändert.

## Optionen

### A — Den qualifizierten V2-Vertrag stabil halten

V2 bleibt in seinem aktuellen engen Umfang als explizites JSON-Opt-in
erhalten. Künftige Änderungen müssen die eingecheckte Qualifikation und die
V1-Bytekompatibilität als Regression bestehen; es wird kein neuer
Produktarbeitsgegenstand registriert.

- Vorteil: nutzt den erreichten Erklärwert bei minimaler weiterer Kopplung;
- Risiko: die Erklärung bleibt bewusst grob und reduziert keinen Review.

### B — Weitere additive, review-beibehaltende Erklärung erwägen

Ein neuer, separat zu registrierender Arbeitsgegenstand könnte eine weitere
explizite Oberfläche für dieselben groben Klassen untersuchen, etwa eine
opt-in lesbare Projektion. Vor Implementierung müssten Oberfläche,
Kompatibilität, Lokalisierung, Datenschutz und Rückfallverhalten neu gebunden
werden. `review` und das Deep-Read-Gate dürften sich nicht ändern.

- Vorteil: könnte die Erklärung außerhalb maschinenlesbarer JSON-Ausgaben
  zugänglicher machen;
- Risiko: vergrößert den öffentlichen Vertrag ohne automatischen
  Sicherheits- oder Sortiergewinn.

### K — Ergebnis konservieren und keine Fortsetzung beginnen

WI-0014 und sein Nachweis bleiben historisch prüfbar. Es wird weder eine
Stabilitätsentscheidung über den jetzigen Umfang hinaus getroffen noch ein
Folgeartefakt registriert.

### P — E-Book-Zweig pausieren

Der Zweig wird ausdrücklich pausiert. Andere SammlungsLotse-Themen bleiben
unberührt.

## Empfehlung

A ist die kleinste sichere Fortsetzung: Der qualifizierte Vertrag bleibt
stabil, ohne neue Produktfläche oder Reviewlockerung. K ist ebenso sicher,
wenn derzeit kein weiterer Erklärwert benötigt wird. B ist nur sinnvoll,
wenn eine konkrete zusätzliche Nutzeroberfläche ausdrücklich gewünscht wird.
P bleibt die bewusste Pause.

## Auswahl

Der Nutzer hat am 2026-09-02 ausdrücklich Option A gewählt. Der
qualifizierte V2-Vertrag bleibt damit in seinem bestehenden engen Umfang als
explizites JSON-Opt-in stabil. Es wird kein Folgearbeitsgegenstand
registriert und keine neue Produktfläche, Reviewlockerung oder weitere
Autorisierung abgeleitet.

## Harte Grenzen

- kein neuer Arbeitsgegenstand ohne ausdrückliche Auswahl;
- keine Lockerung oder Umgehung des WI-0004-Review-Gates;
- keine erneute private Analyse ohne neuen engen Vertrag und ausdrückliche
  Bestätigung;
- keine Aufbewahrung privater Werte, Locators, Pfade, Hashwerte oder
  Rohoutputs;
- keine Netzwerk-, Persistenz-, Routing-, Writer- oder Bestandswirkung;
- keine Aussage über Sicherheit, Vertrauen oder Erreichbarkeit eines Ziels.

## Gate-Stand

- WI-0014 ist `done` und mit 16/16 Kriterien qualifiziert.
- GATE-0021 ist `done`; Option A ist ausdrücklich ausgewählt.
- V1 bleibt Standard, V2 bleibt explizites JSON-Opt-in.
- `review` und `deep_read_only_allowed=false` bleiben unverändert.
- Option A registriert keine Folgearbeit.
