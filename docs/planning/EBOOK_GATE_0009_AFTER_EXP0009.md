# GATE-0009: Fortsetzung nach EXP-0009 und Metadatensemantik bewerten

Status: DONE — OPTION A AUSGEWÄHLT

Stand: 2026-08-28

Artifact: GATE-0009

## Zweck

Dieses Ergebnisgate trennt drei Fragen, die nach EXP-0009 nicht vermischt
werden dürfen:

1. Was hat das Experiment über den unveränderten Produktdienst tatsächlich
   gemessen?
2. Welche fachlichen Bedeutungen tragen die verwendeten EPUB-Metadaten und
   Oracles?
3. Welche Fortsetzung ist klein, reversibel und evidenzgerecht genug, ohne
   eine Produktkorrektur oder neue Produktfläche vorwegzunehmen?

GATE-0009 implementiert keine Regeländerung. Eine Empfehlung ist keine
Annahme eines Experiments, Arbeitsgegenstands oder Technologiepfads.

## Auswahlentscheidung

Der Nutzer hat am 2026-08-28 ausdrücklich Option A gewählt. Damit ist genau
EXP-0010 als standardsgebundene, produktcodefreie Metadaten- und
Oracle-Evidenzwave angenommen. Die Optionen B, F und K sowie die weiteren
Produktvorschläge bleiben nicht ausgewählt. Die Wahl autorisiert keine
Produktkorrektur.

## Verifizierter EXP-0009-Befund

EXP-0009 ist methodisch abgeschlossen:

- 18 vorab gebundene synthetische Paare wurden zweimal materialisiert;
- 12/12 methodische Kriterien und beide semantisch identischen
  Wiederholungen sind eingecheckt validierbar;
- drei Sicherheits- und Paketfälle endeten erwartbar `not_assessed`;
- Eingänge, Pfadfreiheit, Wirkungsfreiheit und Cleanup blieben gebunden;
- Produktcode und TEST-0001 wurden nicht verändert.

Im Fall `metadata-collision-work-conflict` erlaubte das Oracle auf Ausgaben-
und Werkebene nur `different` oder `abstain`. Der Dienst lieferte zweimal
`candidate_same`. Diese Oracle-Abweichung ist real und bleibt sichtbar.

Der Befund belegt jedoch noch nicht, welche einzelne Produktregel fachlich
richtig wäre. Er enthält zugleich eine Metadatensemantik, die vor einer
Korrektur genauer gebunden werden muss.

## Semantische Lücken im aktuellen Stand

### Collection-Metadaten sind keine Werkreferenzen

Der Produktparser liest jedes EPUB-Metafeld mit
`property="belongs-to-collection"` in das interne Feld `work_references`.
Überlappende Werte können anschließend `candidate_related` auf Werkebene
auslösen; unterschiedliche Werte erscheinen als
`metadata.work_references_conflict`.

Die aktuelle W3C-Empfehlung EPUB 3.3 definiert
`belongs-to-collection` dagegen als Namen einer Sammlung, zu der eine
Publikation gehört. Eine EPUB-Publikation darf zu mehreren Sammlungen gehören;
`collection-type` unterscheidet unter anderem `series` und `set`. Das Feld ist
damit weder ein eindeutiger Werkbezeichner noch ein exklusiver Gegenbeweis für
Werk- oder Ausgabenidentität.

Folge: Der EXP-0009-Fall zeigt sicher, dass widersprüchliche Evidenz bei
`candidate_same` nicht sperrt. Er belegt nicht, dass unterschiedliche
Collection-Namen allein `different` erzwingen dürfen.

### Identifier-Rollen und Herkunft fehlen

Der Parser sammelt alle `dc:identifier`-Werte in einer ungeordneten Menge.
Er wertet nicht aus:

- welches Element durch `package@unique-identifier` als primärer Identifier
  ausgewählt ist;
- ob ein Wert nur ein zusätzlicher Identifier ist;
- `identifier-type`, Schema oder Authority;
- die letzte Publikationsänderung;
- Herkunft oder Vertrauensstufe eines Identifiers.

Die EPUB-3.3-Autorenanforderung bindet einen primären Identifier über
`package@unique-identifier` an genau ein `dc:identifier`-Element und erlaubt
weitere Identifier. Die W3C-Empfehlung für Reading Systems warnt zugleich,
dass Systeme nicht auf tatsächliche Eindeutigkeit vertrauen sollen; gleiche
Identifier können weitere Metadaten zur Unterscheidung von Versionen oder
Publikationen erfordern.

Folge: `identifiers_overlap` ist im Produkt derzeit schwächer als der
Regelname `identity.edition.identifier_title` vermuten lässt.

### Der Goldstandard mischt konforme und absichtlich unvollständige Pakete

Der EXP-0009-Generator erzeugt für seine vollständig bewerteten Fälle keine
`package@unique-identifier`-Bindung und keine Identifier-IDs. Einzelne
adversarielle Fälle lassen außerdem verpflichtende bibliografische Felder
absichtlich fehlen. Das ist als Robustheitsprobe des aktuellen Preflight- und
Produktverhaltens reproduzierbar, aber nicht gleichbedeutend mit einem
Goldstandard ausschließlich EPUB-3.3-konformer Publikationen.

Folge: `not_qualified` bleibt die korrekte Bewertung relativ zum gebundenen
EXP-0009-Oracle. Eine konkrete Produktkorrektur darf daraus erst nach
getrennter Standards- und Oraclebindung abgeleitet werden.

## Primärquellen

Stand und Abruf: 2026-08-28.

- [W3C EPUB 3.3](https://www.w3.org/TR/epub-33/), insbesondere 5.5.3.1.1
  `dc:identifier`, D.3.3 `belongs-to-collection` und D.3.4
  `collection-type`;
- [W3C EPUB Reading Systems 3.3](https://www.w3.org/TR/epub-rs-33/),
  insbesondere 5.2 `Unique identifier` und 5.3 `Metadata`.

Diese Quellen beschreiben Format- und Verarbeitungskontrakte. Sie sind keine
bibliografische Werkautorität und ersetzen keine fallbezogenen Oracles.

## Mögliche Fortsetzungen

### A — Standardsgebundene Metadaten- und Oracle-Evidenz reparieren

Ein neues, weiterhin produktcodefreies Experiment würde zuerst eine kleine
EPUB-3.3-konforme Metadatenmatrix binden und den unveränderten Dienst erneut
messen.

Die Matrix müsste mindestens getrennt enthalten:

- korrekt gebundener primärer Unique Identifier;
- zusätzlicher Identifier mit und ohne `identifier-type`;
- gleicher primärer Identifier bei kleiner Revision und bei stark
  widersprüchlichem Inhalt;
- gleiche zusätzliche, aber verschiedene primäre Identifier;
- eine und mehrere Collection-Zugehörigkeiten mit `series` oder `set`;
- Collection-Überlappung ohne behauptete Werkidentität;
- fehlende oder nicht konforme Metadaten als eigene
  `not_assessed`-/Enthaltungsgruppe;
- positive, negative und mehrdeutige Oracles je Publikation, Ausgabe und
  Werk.

- Erkenntniswert: sehr hoch, weil sowohl Produktregel als auch Goldstandard
  betroffen sind;
- neue Kopplung: niedrig; Standardbibliothek, lokal und synthetisch genügen;
- Reversibilität: hoch;
- Nachteil: verschiebt eine Produktkorrektur um genau eine Evidenzwave;
- geeignete Form: nach ausdrücklicher Auswahl ein enges EXP, kein WI.

### B — Sofort einen konservativen Produktvertrag härten

Ein neues WI könnte `candidate_same` auf Ausgaben- und Werkebene sperren,
wenn starke negative Evidenz vorliegt, und Identifier-Rollen expliziter
modellieren.

Mögliche Leitplanken wären:

- kein `candidate_same` allein aus irgendeinem Identifier- und Titeloverlap;
- primärer und zusätzliche Identifier bleiben getrennt;
- unterschiedliche Repräsentationsinhalte und Metadatenkonflikte führen
  mindestens zu Enthaltung, bis eine stärkere Regel greift;
- Werkgleichheit wird nicht automatisch aus Ausgabengleichheit übernommen,
  wenn Gegenbelege vorhanden sind.

- Fehlerwirkung: reduziert mögliche False Same unmittelbar;
- neue Kopplung: mittel, weil Parser-, Modell-, Schema-, CLI- und
  Qualifikationsverträge betroffen wären;
- Reversibilität: mittel;
- Hauptrisiko: eine vorschnelle Regel erzeugt breite False Negatives oder
  zementiert erneut die falsche Collection-/Werksemantik;
- geeignete Form: erst nach ausdrücklicher Produktentscheidung und exakt
  gebundenem WI.

### C — Nur `work_references_conflict` als Veto einbauen

Die kleinste Codeänderung könnte bei verschiedenen
`belongs-to-collection`-Werten auf Ausgabe und Werk enthalten.

- Umsetzbarkeit: hoch;
- Fehlerwirkung: scheinbar direkt;
- fachliche Reife: niedrig;
- Hauptrisiko: verschiedene oder unvollständige Collection-Mitgliedschaften
  sind kein sicherer Werk- oder Ausgabenkonflikt;
- Einordnung: derzeit nicht sinnvoll verfolgen.

### D — Collection und Werk im Erklärungsmodell entkoppeln

Das Produkt könnte `work_references` zunächst korrekt als
`collection_memberships` benennen und Collection-Überlappung nicht mehr als
Werkbeleg verwenden.

- Qualitätsnutzen: klarere Provenienz und weniger semantische Überdehnung;
- neue Kopplung: mittel durch öffentliches Berichtsschema und bestehende
  Qualifikationsbelege;
- Grenze: löst die Identifier- und False-Same-Frage nicht allein;
- geeignete Form: möglicher Bestandteil einer späteren Produktwave, nicht
  isoliert aus diesem Gate ableiten.

### E — Begrenzte Kandidatensuche aus GATE-0008 wieder aufnehmen

Kandidatensuche könnte weiterhin hohen Nutzerwert liefern, würde aber mehr
Paare in den aktuell nicht qualifizierten Identitätsdienst einspeisen.

- Nutzerwert: hoch;
- Risiko: bekannte Unsicherheit wird vervielfacht und kann als vollständige
  Dublettenprüfung missverstanden werden;
- Einordnung: vor A oder B nicht als nächste Wave verfolgen.

### F — Unabhängige read-only Bestandsqualitätsbefunde verfolgen

Die frühere Option C aus GATE-0008 könnte ohne Verwendung einer
Identitätsentscheidung getrennt weiter untersucht werden.

- Nutzerwert: mittel bis hoch;
- Kopplung an den EXP-0009-Befund: niedrig;
- Grenze: der offene Identitätsbefund bleibt bestehen und darf nicht als
  gelöst erscheinen;
- geeignete Form: valide alternative Priorisierung, wenn der Nutzer bewusst
  den Identitätsast pausiert.

### K — Pausieren

Keine neue Wave; nur bestehende Nachweise und Sicherheitsbefunde pflegen.
Dies erhält den saubersten Ausstieg und lässt beide semantischen Fragen offen.

## Vergleich der kleinsten Entscheidungsmenge

| Option | Erkenntnis vor Bindung | unmittelbare Risikoreduktion | neue Kopplung | Empfehlung |
|---|---:|---:|---:|---|
| A — Standardsgebundene Evidenz | sehr hoch | mittel | niedrig | vorläufig empfohlen |
| B — konservative Produktwave | mittel | hoch, falls Regel richtig | mittel | erst nach stärkerem Oracle |
| F — unabhängiger Qualitätsast | hoch im anderen Nutzerproblem | keine für Identität | niedrig bis mittel | valide bewusste Umpriorisierung |
| K — pausieren | keine | keine neue Exposition | keine | valider Ausstieg |

A ist vorläufig empfohlen, weil die neue Primärquellenevidenz sowohl den
Produktvertrag als auch das EXP-0009-Oracle berührt. Eine direkte
Codekorrektur würde derzeit zwei unsichere Bedeutungen gleichzeitig
festschreiben.

## Kanten, die nicht überschritten werden

- EXP-0009 wird nicht nachträglich umetikettiert oder sein Ergebnis
  überschrieben.
- Eine Oracle-Abweichung ist kein automatischer Bugfixauftrag.
- `belongs-to-collection` wird nicht als Werk-ID behandelt.
- Ein `dc:identifier` wird ohne Rolle, Typ und Herkunft nicht zur alleinigen
  Ausgabenwahrheit.
- Ein standardkonformes Paket ist noch keine bibliografisch korrekte
  Metadatenquelle.
- Kandidaten bleiben Vorschläge und lösen keine Bestandswirkung aus.
- Keine Option autorisiert reale/private Medien, Netzwerk, Persistenz,
  Calibre-Schreiben oder andere Writers.

## Entscheidungsstopp

Die bisherige Stopgrenze ist durch die ausdrückliche Auswahl ausschließlich
für EXP-0010 aufgehoben. Nach dessen Ergebnisintegration ist vor jeder
Produktkorrektur, weiteren EXP-/WI-Registrierung oder anderen Fortsetzung ein
neues Ergebnisgate erforderlich. Bis dahin bleiben Produktcode und alle
anderen Optionen gesperrt.
