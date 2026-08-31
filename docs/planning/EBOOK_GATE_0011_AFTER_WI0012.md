# GATE-0011: Fortsetzung nach WI-0012 ergebnisoffen bewerten

Status: DONE — OPTION A / EXP-0011 AUSGEWÄHLT

Stand: 2026-08-31

Artifact: GATE-0011

## Auswahlentscheidung

WI-0012 hat die sechs kritischen False Same der unveränderten
EXP-0010-Qualitätsmatrix auf null reduziert. Der positive
Gleichrepräsentationsfall bleibt `candidate_same`; der abhängige
WI-0011-Calibre-Weg wurde gegen denselben Analyzer-Preimage erneut 23/23
qualifiziert.

Damit ist die unmittelbar sicherheitsrelevante False-Same-Kaskade beendet.
Dieser Erfolg entscheidet aber weder das öffentliche Metadatenmodell noch
eine neue Identitätsstufe oder die nächste Produktfunktion.

Der Nutzer hat am 2026-08-31 ausdrücklich Option A gewählt. Damit ist genau
EXP-0011 als produktcodefreie Vertrags- und Evidenzwave angenommen. Die
Optionen B, C, D, E, F und K bleiben nicht ausgewählt. Der akzeptierte
[Experimentvertrag](EBOOK_IDENTITY_METADATA_CONTRACT_EXPERIMENT.md) vergleicht
drei vorab gebundene Vertragsvarianten; er implementiert weder Produktcode
noch ein öffentliches Schema oder eine neue Entscheidungsregel.

## Gebundener Restbefund

Zwei der acht konformen EXP-0010-Qualitätsfälle weichen auf Werkebene
weiterhin vom Goldstandard ab:

- `same-primary-strong-content-conflict` liefert `candidate_related`, obwohl
  das Werkoracle nur `different` oder `abstain` erlaubt;
- `shared-untyped-additional-different-primary` liefert ebenfalls
  `candidate_related`, obwohl das Werkoracle nur `different` oder `abstain`
  erlaubt.

Beide aktuellen Restentscheidungen stammen aus der Regel
`identity.work.title_creator`, nicht aus einer Gleichheits- oder
Collection-Regel. Die flache Identifier- und Collection-Projektion bleibt
als sichtbare Evidenz im Bericht vorhanden, ist aber nicht die unmittelbar
ausgeführte Entscheidungsregel dieser zwei Restfälle.

Diese Befunde sind schwächere Kandidatenhinweise und keine
Gleichheitsfreigaben. Sie können unnötige manuelle Prüfungen auslösen, haben
aber nicht die Fehlerwirkung der inzwischen beseitigten False Same. Eine
weitere Regelhärtung nur auf diesen zwei synthetischen Fällen wäre deshalb
ohne zusätzliche Evidenz anfällig für Überanpassung und neue False Negatives.

Getrennt davon bleiben drei semantische Fähigkeitslücken belegt:

- `metadata.identifier_roles_flattened`: primäre und zusätzliche Identifier
  samt Typ werden eingeebnet;
- `metadata.collections_flattened_as_work_references`: Collection-Name,
  -Typ, -ID und -Position werden nicht erhalten; der Name wird irreführend
  als `work_references` bezeichnet;
- `identity.publication_stage_absent`: EPUB-Publikation, Ausgabe und Werk
  können nicht als drei eigene Ebenen ausgedrückt werden.

Die Lücken sind fachlich real, aber ihre gemeinsame Behebung würde Modell,
öffentliches JSON-Schema, CLI, Tests und vorhandene Qualifikationsnachweise
koppeln. EXP-0010 belegt noch nicht, welche Zielstruktur den größten
Nutzwert bei der kleinsten kompatiblen Änderung hat.

## Entscheidungskriterien

Jede Fortsetzung wird getrennt bewertet nach:

1. Schutz vor hochpreisigen False Same;
2. Nutzen für eine konkrete read-only Nutzerentscheidung;
3. semantischer Korrektheit und Erklärbarkeit der Evidenz;
4. Reife und Breite der vorhandenen synthetischen Evidenz;
5. Kopplung an Modell, öffentliches Schema, CLI und Nachweise;
6. Reversibilität und Kompatibilität mit den bestehenden v1-Verbrauchern;
7. Risiko von Überanpassung oder verdeckter Architekturfestlegung.

## Mögliche Fortsetzungen

### A — Produktcodefreie Vertrags- und Evidenzwave

Ein begrenztes Experiment würde vor jeder Implementierung drei
Vertragsvarianten auf dem unveränderten TEST-0001-/EXP-0010-Material
vergleichen:

- eine additive, kompatibilitätsorientierte Darstellung der Rollen und
  Collection-Provenienz;
- ein rollenbewusstes Berichtsschema v2 bei unverändert fünf
  Identitätsebenen;
- ein Berichtsschema v2 mit eigener Publikationsstufe.

Das Experiment würde Informationsverlust, Erklärbarkeit, Auswirkungen auf
die zwei `candidate_related`-Restfälle und die Migrationslast vorhandener
Nachweise messen. Es verändert weder Produktcode noch EXP-0010-Oracles und
entscheidet noch kein Zielschema.

- unmittelbare Produktwirkung: keine;
- Erkenntnisnutzen: hoch für die offene Vertrags- und Stufenentscheidung;
- Kopplung: niedrig;
- Reversibilität: sehr hoch;
- Einordnung: **als EXP-0011 ausgewählt**.

### B — Engen Guardrail gegen die zwei False-Related-Restfälle umsetzen

Ein kleines WI könnte `candidate_related` auf Werkebene weiter einschränken.

- unmittelbare Fehlerwirkung: begrenzt auf schwächere Review-Hinweise;
- Vorteil: kleine Codeänderung und sichtbare Reduktion der zwei Abweichungen;
- Risiko: Überanpassung an zwei synthetische Fälle und Verlust nützlicher
  Kandidaten ohne Rollenmodell;
- Einordnung: erst nach zusätzlicher Evidenz sinnvoll.

### C — Collection-Semantik isoliert korrigieren

`work_references` könnte durch strukturierte `collection_memberships` mit
Name, Typ, ID und Position ersetzt werden.

- fachlicher Nutzen: hohe Provenienz- und Benennungskorrektheit;
- Wirkung auf Restbefunde: keine direkte; beide aktuellen Abweichungen
  stammen aus `identity.work.title_creator`;
- Kopplung: mittel durch öffentliches Schema und Qualifikationsnachweise;
- Einordnung: fachlich sinnvoll, aber vor einer Vertragsentscheidung nicht
  die kleinste reversible Wave.

### D — Rollenbewusstes Metadatenmodell v2 ohne neue Stufe umsetzen

Ein neues Berichtsschema könnte primäre und zusätzliche Identifier samt Typ,
Publikationsänderung und vollständige Collection-Mitgliedschaften erhalten,
die fünf bestehenden Identitätsebenen aber beibehalten.

- Nutzer- und Semantiknutzen: hoch;
- Kopplung: mittel bis hoch;
- Risiko: die Entscheidung gegen eine eigene Publikationsstufe würde in die
  Implementierung vorgezogen;
- Einordnung: tragfähige Produktoption nach geklärtem Vertrag.

### E — Publikationsstufe und Metadatenmodell v2 gemeinsam einführen

EPUB-Publikation, Ausgabe und Werk würden als eigene Ebenen modelliert und
mit rollenbewussten Metadaten verbunden.

- Modellnutzen: sehr hoch;
- Kopplung und Migrationslast: hoch;
- Risiko: vorzeitige Architekturfestlegung für den weiterhin begrenzten
  Prototyp;
- Einordnung: derzeit zu breit für die nächste Wave.

### F — Unabhängige read-only Bestandsqualität priorisieren

Der Identitätsast kann sichtbar pausieren, während eine getrennte
Bestandsqualitätsfrage ohne neue Identitäts-, Metadaten- oder
Bestandswirkungsentscheidung bewertet wird. Der Restbefund bleibt dabei
offen dokumentiert.

### K — Pausieren

Keine neue Wave. Der bestehende v1-Bericht bleibt mit seinem qualifizierten
False-Same-Guardrail und den zwei sichtbaren `candidate_related`-
Restabweichungen bestehen.

## Vergleich

| Option | direkter Nutzwert | Evidenzreife | Kopplung | Reversibilität | Bewertung |
|---|---:|---:|---:|---:|---|
| A — Vertrags-/Evidenzwave | mittelbar hoch | hoch für Fragestellung | niedrig | sehr hoch | als EXP-0011 ausgewählt |
| B — Restfall-Guardrail | niedrig bis mittel | niedrig | niedrig | hoch | Überanpassungsrisiko |
| C — Collection-Korrektur | mittel | mittel | mittel | mittel | fachlich richtig, partiell |
| D — Metadatenmodell v2 | hoch | mittel | mittel bis hoch | mittel | nach Vertragsklärung |
| E — Publikationsstufe plus v2 | potenziell sehr hoch | niedrig bis mittel | hoch | niedrig | derzeit zu breit |
| F — unabhängiger Qualitätsast | getrennt | offen | niedrig bis mittel | hoch | valide Umpriorisierung |
| K — pausieren | keine neue Wirkung | ausreichend zum Stoppen | keine | vollständig | valider Ausstieg |

## Auswahlbegründung

Option A ist die kleinste belastbare Fortsetzung. Der Guardrail hat den
kritischen Fehler bereits beendet; der verbleibende Engpass ist nun die
ungeklärte Vertragsform, nicht ein weiterer nachgewiesener
Gleichheitsfehler. Eine produktcodefreie Vergleichswave kann diese
Unsicherheit reduzieren, ohne ein öffentliches v2-Schema oder eine
Publikationsstufe vorwegzunehmen.

Die ausdrückliche Auswahl schließt GATE-0011 und autorisiert ausschließlich
Registrierung und Planung von EXP-0011. Der Experimentlauf beginnt erst in
einer eigenen Ausführungswave aus dem danach verifizierten `origin/main`.
Eine spätere Produktübernahme benötigt nach dem Experiment ein neues
getrenntes Ergebnisgate.

## Kanten, die nicht überschritten werden

- WI-0012, EXP-0010 und deren Oracles werden nicht umgeschrieben.
- `candidate_related` wird nicht als bestätigte Dublette oder Werkgleichheit
  dargestellt.
- Ein Standards-valider EPUB ist kein bibliografisches Identitätsorakel.
- Keine Option autorisiert reale/private Medien, automatische Suche, mehrere
  Dateien, IDs oder Bibliotheken, neue Calibre-Felder, externe Metadaten,
  Persistenz, Routing, Browser, REST, Agents oder Writes.
- Fachsysteme bleiben führend; SammlungsLotse liefert unterstützende,
  read-only Evidenz und enthält sich außerhalb gebundener Aussagen.

## Gate-Folgen

- GATE-0011 ist mit der ausdrücklichen Auswahl von A `done`.
- EXP-0011 ist als eigener Experimentvertrag `accepted`, aber noch nicht
  ausgeführt.
- Kein Produktarbeitsgegenstand ist registriert und Produktcode bleibt
  unverändert.
- Die EXP-0011-Ausführung benötigt eine isolierte Wave und eine ihrem Risiko
  angemessene Abnahme.
- Bis dahin gilt der aktuelle WI-0012-v1-Vertrag unverändert.
