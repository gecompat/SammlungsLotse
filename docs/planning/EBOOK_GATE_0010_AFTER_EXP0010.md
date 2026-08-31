# GATE-0010: Produktfortsetzung nach EXP-0010 bewerten

Status: AUSGEWERTET — OPTION A / WI-0012 AUSGEWÄHLT

Stand: 2026-08-31

Artifact: GATE-0010

## Entscheidung

Der Nutzer hat am 2026-08-31 ausdrücklich Option A ausgewählt. Als nächste
kleine Produktwave wird WI-0012 angenommen: ein enger Fail-safe-Guardrail für
den bestehenden EPUB-Identitätskandidatenbericht.

WI-0012 beseitigt ausschließlich die empirisch belegte False-Same-Kaskade.
Identifier- und Titelüberlappung dürfen eine Ausgabe nur noch dann als
`candidate_same` einstufen, wenn zusätzlich die Repräsentation gleich und die
vorhandenen Metadaten kompatibel sind. Werkgleichheit darf weiterhin nur aus
einer nach diesem Guardrail qualifizierten Ausgabengleichheit folgen.

Das öffentliche v1-Berichtsschema, die fünf vorhandenen Identitätsebenen und
die getrennten positiven, negativen und fehlenden Evidenzkanäle bleiben
erhalten. Die Auswahl nimmt weder ein rollenbewusstes Metadatenmodell noch
eine Publikationsstufe oder Collection-Neumodellierung vorweg.

## Zweck

Dieses Ergebnisgate trennt die unmittelbar belegte False-Same-Ursache von
drei weiter reichenden Modelllücken. Die Bewertung selbst implementiert keine
Produktregel; sie autorisiert mit der ausdrücklichen Auswahl ausschließlich
den unter WI-0012 begrenzten Guardrail.

## Verifizierter EXP-0010-Befund

EXP-0010 ist methodisch 12/12 abgeschlossen:

- genau zehn vorab gebundene synthetische Paare wurden bewertet;
- 16 Einzel-EPUBs der acht Qualitätsfälle bestanden EPUBCheck 5.3.0 ohne
  Befund;
- vier Einzel-EPUBs der zwei getrennten Negativkontrollen lieferten die
  erwarteten Konformitätsfehler `OPF-030` und/oder `RSC-005`;
- zwei vollständige Produktwiederholungen besaßen denselben semantischen
  Digest;
- Eingänge, Pfadfreiheit, Netzwerkgrenze, Bestandswirkung und Cleanup
  blieben gebunden;
- Produktcode und TEST-0001 wurden nicht verändert.

Die Produktqualität auf den acht konformen Paaren lautet `not_qualified`.
Drei Fälle erzeugten je einen kritischen False Same auf Ausgaben- und
Werkebene:

1. gleicher primärer Identifier bei stark widersprüchlichem Inhalt;
2. gleicher typisierter Zusatz-Identifier bei verschiedenen primären
   Identifiern und Ausgaben;
3. gleicher untypisierter Zusatzwert bei verschiedenen primären Identifiern
   und kontrolliert verschiedenen Werken.

Damit entstanden sechs kritische False Same. Die Precision von
`candidate_same` betrug auf Ausgabe und Werk im gezielten Goldstandard je
0,25. Dieser Wert ist keine Schätzung realer Häufigkeiten.

## Getrennte Ursachen

### Unmittelbar entscheidungswirksame Ursache

`identity.edition.identifier_title` behandelt jeden überlappenden
`dc:identifier` zusammen mit Titel- und Creator-Überlappung als
`candidate_same`. Die Regel unterscheidet weder primäre von zusätzlichen
Identifiern noch verlangt sie kompatible Repräsentationsevidenz. Der
Werkentscheid `identity.work.same_edition` übernimmt diese Ausgabengleichheit
anschließend unverändert.

Diese Kaskade erklärt alle sechs kritischen Befunde der konformen Matrix.

### Semantische Fähigkeitslücken

EXP-0010 belegt außerdem getrennt:

- `identity.publication_stage_absent`: Der Produktbericht besitzt keine
  eigene Ebene für die EPUB-Publikation.
- `metadata.identifier_roles_flattened`: Primäre und zusätzliche Identifier
  samt `identifier-type` werden in eine Wertemenge eingeebnet.
- `metadata.collections_flattened_as_work_references`: Collection-Name, -Typ,
  -ID und -Position werden nicht erhalten; nur der Name erscheint als
  `work_references`.

Die vier Collection-Fälle erzeugten im gebundenen Goldstandard keine
Oracle-Abweichung. Das rechtfertigt keine Fortführung der falschen
Feldsemantik, belegt aber, dass ein isoliertes Collection-Veto nicht die
aktuelle False-Same-Ursache beheben würde.

## Mögliche Fortsetzungen

### A — Engen Fail-safe-Guardrail einführen

Ein kleines WI würde ausschließlich die nachgewiesene False-Same-Kaskade
härten:

- Identifier- und Titelüberlappung allein erzeugt keine Ausgabengleichheit;
- `candidate_same` auf Ausgabenebene benötigt im aktuellen v1-Vertrag
  zusätzlich gleiche Repräsentation und kompatible Metadaten;
- bei verschiedener Repräsentation bleibt der Dienst `different` oder
  enthält sich, bis ein späterer rollenbewusster Vertrag existiert;
- Werkgleichheit darf nur aus einer nach diesem Guardrail qualifizierten
  Ausgabengleichheit folgen;
- bestehende positive, negative und fehlende Evidenz bleibt sichtbar.

- unmittelbare Fehlerwirkung: sehr hoch für die sechs belegten False Same;
- Kopplung: niedrig, weil öffentliches Schema und Metadatenmodell unverändert
  bleiben;
- Reversibilität: hoch;
- bewusster Nachteil: geringere Ausgabenabdeckung und mögliche False
  Negatives bei verändertem Inhalt;
- Einordnung: als WI-0012 ausgewählt.

### B — Rollenbewusstes Metadatenmodell v2 einführen

Ein breiteres WI würde primäre und zusätzliche Identifier,
`identifier-type`, `dcterms:modified` sowie vollständige
Collection-Mitgliedschaften modellieren.

- Qualitätsnutzen: hoch und fachlich nachhaltiger;
- Kopplung: mittel bis hoch durch Modell, JSON-Schema, CLI, Tests und
  bestehende Qualifikationsbelege;
- Risiko: mehrere Bedeutungsänderungen werden in einer Wave gekoppelt;
- Einordnung: sinnvoll verfolgen, aber nicht als kleinste unmittelbare
  Risikobremse.

### C — Publikationsstufe und Metadatenmodell gemeinsam neu schneiden

Eine neue Identitätsstufe könnte EPUB-Publikation, Ausgabe und Werk
ausdrücklich trennen und die rollenbewussten Metadaten aus B verwenden.

- Erkenntnis- und Modellnutzen: sehr hoch;
- Kopplung: hoch;
- Risiko: vorzeitige Architekturentscheidung für den bislang reversiblen
  Prototyp;
- Einordnung: erst nach einem engeren Produkt- und Nutzervertrag verfolgen.

### D — Collection-Semantik isoliert korrigieren

`work_references` könnte in `collection_memberships` überführt und
Collection-Bezug nicht mehr als explizite Werkreferenz bezeichnet werden.

- fachlicher Nutzen: klare Provenienz und korrekte Benennung;
- unmittelbare Wirkung auf die sechs False Same: keine;
- Kopplung: mittel durch Berichtsschema und Qualifikationsbelege;
- Einordnung: sinnvoll als Teil von B, derzeit nicht allein priorisieren.

### F — Unabhängige read-only Bestandsqualität priorisieren

Der Identitätsast könnte sichtbar pausiert und ein unabhängiger
Bestandsqualitätsbefund ohne Identitätsentscheidung verfolgt werden. Der
offene False-Same-Befund bliebe bestehen.

### K — Pausieren

Keine neue Wave. Bestehende Nachweise bleiben erhalten; der aktuelle
Identitätsdienst darf nicht als auf der EXP-0010-Matrix qualifiziert
dargestellt werden.

## Vergleich der kleinsten Entscheidungsmenge

| Option | unmittelbare Risikoreduktion | langfristige Semantik | Kopplung | Empfehlung |
|---|---:|---:|---:|---|
| A — Fail-safe-Guardrail | sehr hoch | begrenzt | niedrig | als WI-0012 ausgewählt |
| B — Metadatenmodell v2 | hoch | hoch | mittel bis hoch | sinnvoll nach engerem Vertrag |
| C — Publikationsstufe plus v2 | hoch | sehr hoch | hoch | derzeit zu breit |
| F — unabhängiger Qualitätsast | keine für Identität | keine | niedrig bis mittel | valide Umpriorisierung |
| K — pausieren | keine neue Exposition | keine | keine | valider Ausstieg |

A ist ausgewählt, weil es exakt die empirisch belegte Kaskade stoppt, ohne
die drei weiter reichenden Modellfragen in dieselbe Wave zu ziehen. B und D
bleiben dadurch möglich und werden nicht vorentschieden.

## Kanten, die nicht überschritten werden

- EXP-0010 und seine Oracles werden nicht nachträglich umgeschrieben.
- EPUBCheck ist kein bibliografisches Identitätsorakel.
- Ein Guardrail wird nicht als vollständige Identifier- oder
  Collection-Semantik dargestellt.
- Geringere Abdeckung ist bei hohen False-Same-Kosten ein sichtbarer
  Trade-off und kein verdeckter Erfolg.
- Keine Option autorisiert Suche, Persistenz, reale/private Medien,
  Fachsystem- oder Dateischreiben.

## Gate-Folgen

- GATE-0010 ist mit der ausdrücklichen Auswahl von A `done`.
- WI-0012 ist als eigener Arbeitsgegenstand `accepted`.
- Produktcode beginnt erst nach Merge dieser Planungs-Wave nach `main`.
- EXP-0010, seine Falloracles und sein Ergebnis werden nicht umgeschrieben.
- Die geringere Ausgabenabdeckung bleibt als bewusster Trade-off sichtbar.
- Metadatenmodell v2, Publikationsstufe und Collection-Semantik benötigen
  später eine eigene Entscheidung.
- Nach WI-0012 wird erneut getrennt bewertet; keine weitere Produktwave wird
  durch dieses Gate vorweggenommen.
