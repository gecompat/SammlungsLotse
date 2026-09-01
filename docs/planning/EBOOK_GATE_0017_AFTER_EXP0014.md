# GATE-0017: EXP-0014-Ergebnis und dreifache Remote-Ressourcen-Reviewentscheidung bewerten

Status: PROPOSED — OPEN FOR EXPLICIT SELECTION

Stand: 2026-09-01

Artifact: GATE-0017

## Zweck

Dieses Gate bewertet den methodisch bestandenen EXP-0014-Befund. Es trennt
die nun bekannte gemeinsame WI-0004-Reviewursache von jeder Aussage über
Gefährlichkeit, EPUB-Qualität oder eine nötige Produktkorrektur. Ohne
ausdrückliche Auswahl wird weder ein Folgeexperiment noch ein
Produktarbeitsgegenstand registriert.

## Verifizierte Evidenz

- Das saubere Ausführungspreimage ist Commit
  `e82d01e6d669e85646dafd6ab3d569fc38e0d71b`.
- Vier tatsächliche synthetische WI-0004-JSON-Läufe deckten
  `continue_deep_read_only`, `review`, `stop` und `abstain` ab. Die
  Projektionsmatrix ergänzte `defer`.
- Alle elf Negativkontrollen und zwei semantisch identische
  Aggregationswiederholungen bestanden.
- Der Nutzer bestätigte erneut denselben Satz aus genau drei privaten EPUBs
  wie in EXP-0013. Jede neutrale task-private Kopie durchlief genau einmal
  den unveränderten WI-0004-JSON-Weg.
- Die Folgeaktionsaggregation lautet ausschließlich `review=3`; alle vier
  anderen öffentlichen Aktionen stehen auf null.
- Die Befundaggregation enthält ausschließlich `format.epub=3` und
  `security.remote_resource=3`.
- Die zugehörige öffentliche Beobachtung
  `epub.remote_reference.present` trat dreimal auf. Die drei Snapshots waren
  stabil, als ZIP/EPUB erkannt und flach im Markup geprüft.
- Unbekannte Beobachtungs- und Befundcodes stehen jeweils auf null. Private
  Werte, URLs, Domains, Metadaten, Locators, Pfade, Hashwerte, Größen und
  Rohberichte wurden nicht aufbewahrt.
- Quellen blieben bytegleich unverändert; Taskmaterial und Prozesse wurden
  vollständig bereinigt.
- Das 907-Byte-Ergebnis besitzt ausschließlich dreizehn erlaubte
  Gruppenfelder und den SHA-256-Wert
  `0eab4893eb85d05c07622bfe70721a58f03e8285e199738b1513237dc3207411`.

## Interpretation

Der dreifache EXP-0013-Nichtabschluss ist innerhalb der vorhandenen
WI-0004-Grenze erklärt: Jede der drei EPUB-Kopien enthielt mindestens eine
vom flachen Preflight erkannte HTTP(S)-Remote-Referenz. Der bestehende
Vertrag leitete deshalb jeweils auf `review` und öffnete den tiefen
read-only Werkzeugweg nicht.

Dies belegt weder Schadcode noch eine tatsächlich ausgeführte
Netzwerkverbindung. EXP-0014 speicherte absichtlich weder Referenzwerte noch
Einzelzuordnungen und prüfte nicht, ob die Referenz beispielsweise in einem
Bild-, Link-, Stylesheet- oder Metadatenkontext steht. Ebenso wenig belegt
der Befund EPUB-Standardsgültigkeit, bibliografische Identität oder einen
Produktfehler. Das vorhandene Review-Gate verhielt sich gemäß seinem
aktuellen Sicherheitsvertrag.

## Optionen

### A — Private Referenzarten produktcodefrei und pfadfrei qualifizieren

Ein neues enges Experiment könnte höchstens dieselben drei erneut explizit
bestätigten EPUBs verwenden und ausschließlich vorab gebundene, gruppierte
Referenzkontexte zählen. URLs, Domains, Fragmente, Inhalte, Metadaten,
Einzelzuordnungen und Rohberichte blieben ausgeschlossen. Netzwerk,
Produktcode und tiefe Werkzeuge blieben aus.

- Vorteil: klärt, ob die drei Reviewentscheidungen auf demselben groben
  Kontext beruhen, bevor eine Produktregel erwogen wird;
- Risiko: auch Kontextklassen sind neue private Evidenz und benötigen einen
  eigenen strikten Mindestmengen- und Datenschutzvertrag;
- Einordnung: **kleinste evidenzschließende Fortsetzung**, falls die drei
  privaten Fälle weiter untersucht werden sollen.

### B — Ausschließlich synthetische Remote-Referenzmatrix vertiefen

Eine synthetische Wave könnte TEST-0001 um getrennte HTML-/SVG-/CSS- und
Attributkontexte, mehrere Referenzen sowie Grenz- und Täuschungsfälle
erweitern. Sie benötigt keine privaten Dateien, kann die konkrete Art der
drei realen Referenzen aber nicht zuordnen.

### C — Produktarbeitsgegenstand getrennt erwägen

Ein später separat zu registrierender Arbeitsgegenstand könnte eine
erklärbarere Reviewausgabe oder differenziertere fail-safe Regeln
untersuchen. Diese Option ist keine Implementierungsfreigabe. Vor Produktcode
müssten Zielverhalten, False-Negative-Kosten, Kompatibilität und ein eigener
synthetischer Produktnachweis angenommen werden.

### K — Evidenz konservieren und bestehendes Review beibehalten

EXP-0014 bleibt historisch prüfbar. Der aktuelle konservative WI-0004-Weg
bleibt unverändert; die drei Fälle benötigen weiterhin Review und gelangen
nicht automatisch in den tiefen read-only Weg.

### P — E-Book-Identitätszweig pausieren

Der Zweig wird ausdrücklich pausiert. Andere SammlungsLotse-Themen bleiben
unberührt.

## Empfehlung

A ist die kleinste weitere Evidenzfrage, wenn die konkrete Blockade dieser
drei EPUBs weiter eingegrenzt werden soll. B ist die datenschutzärmste
Vertiefung, beantwortet aber die reale Kontextfrage nicht. K ist die sichere
Endposition, wenn das vorhandene konservative Reviewverhalten genügt. C ist
ohne Referenzarten- oder erweiterte synthetische Evidenz verfrüht.

Die Empfehlung nimmt keine Option an. Erst eine ausdrückliche Nutzerwahl
schließt GATE-0017 und kann einen getrennten Vertrag autorisieren.

## Harte Grenzen

- methodischer `pass` ist keine Produktfreigabe;
- `security.remote_resource` ist ein Reviewgrund, kein Schadensnachweis;
- keine automatische Lockerung oder Umgehung des WI-0004-Review-Gates;
- keine private Verzeichnis-, Glob-, Index- oder rekursive Suche;
- keine Aufbewahrung privater URLs, Domains, Metadaten, Einzelwerte,
  Locators, Pfade, Hashwerte oder Rohoutputs;
- kein Netzwerk, keine Persistenz, kein tiefer Werkzeuglauf und keine
  Bestandswirkung;
- keine Änderung unter `src/sammlungslotse/` ohne getrennt angenommenen
  Produktarbeitsgegenstand.

## Gate-Stand

- EXP-0014 ist `done`; Methode und pfadfreies Aggregat sind historisch
  gebunden.
- GATE-0017 ist `proposed` und offen.
- A, B, C, K und P sind nicht ausgewählt.
- Kein Produktarbeitsgegenstand ist registriert; Produktcode bleibt
  unverändert.
