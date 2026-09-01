# GATE-0019: EXP-0016-Ergebnis und mögliche Reviewdifferenzierung bewerten

Status: PROPOSED — OPEN FOR EXPLICIT SELECTION

Stand: 2026-09-01

Artifact: GATE-0019

## Zweck

Dieses Gate bewertet den methodisch bestandenen EXP-0016-Befund. Es trennt
die synthetische Trennbarkeit gebundener Referenzkontexte von jeder Aussage
über konkrete Lesesysteme, Werkzeug- oder Netzwerkverhalten, Nutzerabsicht,
Zielvertrauen und Produktsicherheit. Ohne ausdrückliche Auswahl wird weder
ein Folgeexperiment noch ein Produktarbeitsgegenstand registriert.

## Verifizierte Evidenz

- Das saubere Ausführungspreimage ist Commit
  `969fa6331afdfc4ceb808ffeed71f7a30193205b`; beide erforderlichen
  GitHub-Checks bestanden vor dem synthetischen Hauptlauf auf exakt diesem
  Commit.
- Genau 48 vorab gebundene Package-, XHTML-, EPUB-Navigations-, SVG-, CSS-,
  Schema- und Täuschungsfälle wurden je zweimal verarbeitet. Alle
  96 Parserläufe waren semantisch wiederholbar.
- Alle sechs Kontextklassen und sechs im Fallmanifest tatsächlich verwendeten
  Schemagruppen stimmten ohne Context Mismatch oder False Negative mit dem
  Orakel überein.
- S1 `review_all_http_s` und S2 `classify_and_keep_review` besitzen jeweils
  acht konservative Reviews, zehn fail-closed Enthaltungen und null kritische
  Fehlfortsetzungen.
- S3 `strict_navigation_candidate` besitzt null konservative Reviews, zehn
  fail-closed Enthaltungen und ebenfalls null kritische Fehlfortsetzungen.
- Alle drei Strategien sind innerhalb dieser Matrix
  `eligible_with_tradeoffs`; der methodische Gesamtstatus ist `pass` mit
  16 von 16 Akzeptanzwerten.
- Private Eingänge, Produktimport, Netzwerk, Persistenz, tiefer Werkzeuglauf
  und Bestandswirkung fehlten. Produktcode blieb unverändert und das
  Task-Cleanup war vollständig.
- Das 2.279-Byte-Ergebnis ist über SHA-256
  `6c748dd1477dba56a37e19b7a5bf798d32e702e8d6d2a230ebfa3c98d775db08`
  an das historische Preimage gebunden.

## Interpretation

Die vorab gebundene syntaktische Matrix kann direkte HTTP(S)-Hyperlinks von
Package-Links, automatisch verarbeitbaren Ressourcen, aktiven oder
formulargebundenen Kontexten, anderen Schemata und mehrdeutigen Fällen
trennen. Die strikte S3-Projektion reduzierte in dieser Matrix die acht
unnötigen Reviews, ohne einen der 40 übrigen Fälle freizugeben; zehn
Täuschungs- und Mehrdeutigkeitsfälle blieben auf `abstain`.

`candidate_continue_deep_read_only` ist ausschließlich ein synthetisches
Vergleichsliteral. EXP-0016 hat weder einen Link geöffnet noch ein
Lesesystem, EPUBCheck, den WI-0005-Executor oder ein anderes tiefes Werkzeug
ausgeführt. Es belegt nicht, dass alle realen EPUB-Varianten erfasst sind,
ein Ziel vertrauenswürdig ist, ein Nutzer den Link aktivieren will oder eine
spätere Downstream-Komponente die Referenz nie verarbeitet. Das konservative
WI-0004-Review-Gate verhielt sich weiterhin vertragsgemäß und bleibt
unverändert.

## Optionen

### A — Synthetische Downstream-Isolation und Threat Model qualifizieren

Ein neues getrenntes Experiment könnte ausschließlich synthetische EPUBs mit
den qualifizierten S3-, Ressourcen- und Täuschungskontexten gegen den exakt
gebundenen, unveränderten tiefen read-only Pfad untersuchen. Es müsste
effektive Netzwerklosigkeit, keine Linkaktivierung, Parserdifferenzen,
Fail-closed-Verhalten, Timeout, Outputgrenze und Cleanup vorab binden. Es
ändert keinen Produktcode und wählt noch keine Reviewlockerung.

- Vorteil: prüft die kleinste verbleibende Sicherheitslücke zwischen
  syntaktischer Klassifikation und möglicher Downstream-Ausführung;
- Risiko: bindet erneut einen konkreten Provider- und Executorstand und
  belegt weiterhin keine allgemeine Lesesystemsicherheit;
- Einordnung: **empfohlene evidenzschließende Fortsetzung**, falls eine
  spätere Reviewdifferenzierung weiter verfolgt werden soll.

### B — Review-beibehaltende Kontexterklärung als Arbeitsgegenstand erwägen

Ein später separat zu registrierender Produktarbeitsgegenstand könnte
`review` unverändert lassen und ausschließlich eine grobe, pfadfreie
Kontexterklärung ergänzen. Vor Produktcode müssten öffentlicher
Ausgabevertrag, unbekannte Klassen, Kompatibilität, Datenschutz und eine
vollständige synthetische Produktqualifikation angenommen werden.

- Vorteil: erhöht Erklärbarkeit ohne den Sicherheitsgate zu öffnen;
- Risiko: erzeugt eine neue öffentliche Produktsemantik und reduziert den
  manuellen Reviewaufwand nicht automatisch.

### C — Strikte Navigationsausnahme als Produktarbeitsgegenstand erwägen

Ein später separat zu registrierender Arbeitsgegenstand könnte S3 als
Kandidat für eine eng begrenzte Ausnahme vor dem tiefen read-only Pfad
bewerten. Vor Implementierung wären ein eigenes Threat Model, Downstream-
Isolation, vollständige adversarielle Produktmatrix, unbekannte
Klassenbehandlung, Rückfallregel und explizite Produktannahme erforderlich.

- Vorteil: könnte die acht synthetisch konservativen Reviews vermeiden;
- Risiko: ein einziger False Negative kann eine automatisch oder aktiv
  verarbeitbare Referenz fälschlich durch den Sicherheitsgate lassen;
- Einordnung: ohne die Evidenz aus A höheres und derzeit nicht geschlossenes
  Risiko.

### K — Evidenz konservieren und bestehendes Review beibehalten

EXP-0016 bleibt historisch prüfbar. Der aktuelle konservative WI-0004-Weg
bleibt unverändert; die drei zuvor untersuchten privaten EPUBs benötigen
weiterhin Review.

### P — E-Book-Identitätszweig pausieren

Der Zweig wird ausdrücklich pausiert. Andere SammlungsLotse-Themen bleiben
unberührt.

## Empfehlung

A ist die kleinste nächste Evidenzfrage, wenn eine spätere
Reviewdifferenzierung weiter untersucht werden soll. Sie prüft die bisher
nicht ausgeführte Downstream-Grenze, ohne bereits eine Produktregel
auszuwählen. B ist die niedrigere Produktwirkung für Erklärbarkeit, reduziert
aber kein Review. K ist die sichere Endposition, wenn das bestehende
Reviewverhalten genügt. C ist ohne die Downstream- und Threat-Model-Evidenz
aus A verfrüht.

Die Empfehlung nimmt keine Option an. Eine Fortsetzung erfordert die
ausdrückliche Auswahl von A, B, C, K oder P.

## Harte Grenzen

- methodischer `pass` und `eligible_with_tradeoffs` sind keine
  Produktfreigabe;
- null Fehler in 48 synthetischen Fällen belegen keine vollständige reale
  Eingangs- oder Lesesystemabdeckung;
- keine automatische Lockerung oder Umgehung des WI-0004-Review-Gates;
- keine erneute private Analyse ohne neuen engen Vertrag und ausdrückliche
  Bestätigung;
- keine Aufbewahrung privater Werte, Locators, Pfade, Hashwerte oder
  Rohoutputs;
- kein Produktcode ohne getrennt registrierten und angenommenen
  Arbeitsgegenstand;
- keine Bestandswirkung oder Änderung im führenden Fachsystem.

## Gate-Stand

- EXP-0016 ist `done`; Methode, Matrix und Ergebnis sind historisch gebunden.
- GATE-0019 ist `proposed` und offen für eine ausdrückliche Auswahl.
- A, B, C, K und P sind nicht ausgewählt.
- Kein Produktarbeitsgegenstand ist registriert; Produktcode und das
  WI-0004-Review-Gate bleiben unverändert.
