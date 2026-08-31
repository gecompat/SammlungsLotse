# GATE-0012: Fortsetzung nach EXP-0011 ergebnisoffen bewerten

Status: DONE — OPTION A / WI-0013 AUSGEWÄHLT

Stand: 2026-08-31

Artifact: GATE-0012

## Auswahlentscheidung

Der Nutzer hat am 2026-08-31 ausdrücklich Option A ausgewählt. Damit ist
GATE-0012 `done`. Der enge rollenbewusste V2-Zielvertrag wird getrennt als
WI-0013 registriert. Diese Auswahl autorisiert ausschließlich dessen
Planung und eine nach erfolgreicher Integration beginnende, begrenzte
Implementierungswave. V1 bleibt zunächst unveränderter Standard; eine
Deprecation oder Entfernung von V1 ist nicht ausgewählt.

## Gebundener Ergebnisstand

EXP-0011 ist aus dem vollständigen Git-Preimage
`a5aeb0196d8d6a32fc90da46ca158ba693c6a0db` ausgeführt. Der methodische
Nachweis besteht 14/14 Kriterien auf genau fünf TEST-0001-Paaren, acht
konformen EXP-0010-Qualitätsfällen und zwei getrennten nicht konformen
Kontrollen. Die zwei unabhängigen Projektionen besitzen denselben
semantischen SHA-256-Wert
`ec22878a8668852498b13181a24387c8f78838e2ee13eefe2c020bdd06df9cc5`.

Für jede Variante gelten auf der acht Fälle umfassenden Rollenmatrix:

- null verlorene Rollenfelder;
- 145/145 eindeutig mit Quelle und Beobachtungsstatus versehene Werte;
- null neue semantische Benennungsverstöße;
- unveränderte Entscheidungen, Regel-IDs sowie positive, negative und
  fehlende Evidenzkanäle der fünf bestehenden Produktstufen;
- beide verbleibenden `candidate_related`-Fälle mit der tatsächlichen Regel
  `identity.work.title_creator` weiterhin sichtbar;
- Einstufung `eligible_with_tradeoffs`, nicht Auswahl eines Zielvertrags.

Die zwei nicht konformen Kontrollen bleiben auf Experimentebene
`not_assessed`. Ihre aktuell beobachtbaren v1-Produktberichte werden nicht
als Qualitätsaussage gewertet. Produktcode, öffentliches Schema, Fixtures,
EXP-0010, Qualifikationsnachweise, Netzwerk, Container, Persistenz,
Fachsysteme und Bestände blieben unverändert.

## Ergebnis je Variante

### V1 — v1-Bericht plus Evidenzbegleiter

- Der öffentliche v1-Bericht bleibt in allen 13 qualifizierten Fällen
  bytegenau erhalten.
- Der getrennte Begleiter erhält Identifier-Rollen,
  `dcterms:modified` und vollständige Collection-Provenienz verlustfrei.
- Die experimentseigene Struktur nennt Collections korrekt
  `collection_memberships`. Das unveränderte v1-Payload enthält weiterhin
  sein historisches Feld `work_references`; dieser Altschaden ist sichtbar,
  aber nicht stillschweigend umgeschrieben.
- Kleinste unmittelbare Schemaänderung, aber dauerhafter Join über
  `input_index`, zusätzlicher Vertrag und keine Publikationsstufe.

### V2 — rollenbewusster v2-Bericht mit fünf Stufen

- Rollen und Provenienz liegen in genau einem Bericht vor.
- Die fünf vorhandenen Produktstufen bleiben unverändert.
- Collection-Mitgliedschaft wird nicht mehr als Werkreferenz bezeichnet.
- Kein Begleiter-Join, aber Migration von Modell, JSON, CLI, Tests sowie
  WI-0012-/WI-0011-Nachweisen.
- Die fehlende eigene Publikationsstufe bleibt ausdrücklich eine Lücke.

### V3 — rollenbewusster v2-Bericht mit Publikationsstufe

- Rollen und Provenienz entsprechen V2.
- Eine getrennte Stufe `publication` ist strukturell ausdrückbar.
- Mangels Produktregel bleibt sie korrekt `assessment: not_assessed`; das
  Publikationsoracle wird nicht zur Produktentscheidung.
- Größte Ausdrucksfähigkeit, aber größte Migrationsfläche und stärkste
  Architekturvorwirkung.

## Entscheidungskriterien

Die Fortsetzung wird ohne gewichteten Gesamtscore bewertet nach:

1. konkretem read-only Nutzwert;
2. semantischer Korrektheit und Erklärbarkeit;
3. v1-Kompatibilität und Verbraucherwirkung;
4. Umfang von Modell-, JSON-, CLI-, Test- und Nachweismigration;
5. Reife einer tatsächlich implementierbaren Produktregel;
6. Reversibilität und Risiko vorzeitiger Architekturfestlegung;
7. verbleibender Unsicherheit jenseits der 15 synthetischen Paare.

## Mögliche Fortsetzungen

### A — V2 als engen Zielvertrag auswählen

Ein neuer, getrennt registrierter Produktarbeitsgegenstand würde ein
rollenbewusstes v2-Schema mit den bisherigen fünf Stufen planen und danach
in einer begrenzten Wave umsetzen. V1 bliebe zunächst unverändert verfügbar;
Migration und Deprecation müssten ausdrücklich festgelegt werden.

- direkter Nutzerwert: hoch durch korrekte Rollen in einem Bericht;
- Evidenzreife: hoch für Rollen- und Provenienzerhalt;
- Kopplung: mittel bis hoch;
- Restunsicherheit: Publikation bleibt ohne eigene Stufe;
- Einordnung: **engste zusammenhängende Produktoption**.

### B — V1 als additive Kompatibilitätsoption auswählen

Ein neuer Arbeitsgegenstand würde ausschließlich einen Evidenzbegleiter zum
unveränderten v1-Bericht planen und umsetzen.

- direkter Nutzerwert: mittel bis hoch;
- Kompatibilität: maximal;
- Kopplung: niedrig bis mittel;
- Restlast: Join, zweiter Vertrag und fortbestehender v1-Semantikschaden;
- Einordnung: konservativste Produktoption.

### C — V3 erst durch ein Publikationsregel-Experiment vertiefen

Vor Produktcode würde ein neues enges Experiment ausschließlich klären,
welche beobachtbare Evidenz eine Publikationsentscheidung tragen kann und
wann Enthaltung erforderlich bleibt.

- Erkenntniswert: hoch für die offene Publikationsstufe;
- unmittelbare Produktwirkung: keine;
- Kopplung: niedrig;
- Risiko: zusätzliche Zeit ohne direkten Produktnutzen;
- Einordnung: richtige Vorstufe, falls Publikation strategisch wichtig ist.

### D — V3 direkt als Zielvertrag auswählen

Ein neuer Produktarbeitsgegenstand würde rollenbewusstes v2 und eine neue
Publikationsstufe gemeinsam planen. Die Stufe dürfte bis zu einer späteren
Regel weiterhin nur `not_assessed` liefern.

- Ausdrucksfähigkeit: maximal;
- Evidenzreife: hoch für Struktur, niedrig für Produktentscheidung;
- Kopplung und Migration: hoch;
- Einordnung: derzeit breiteste und am stärksten vorprägende Produktoption.

### F — Unabhängige read-only Bestandsqualität priorisieren

Der Identitätsast bleibt dokumentiert offen; eine getrennte Bestandsfrage
wird ohne Schema- oder Identitätsänderung bewertet.

### K — Pausieren

Keine neue Wave. Der qualifizierte WI-0012-v1-Bericht bleibt unverändert;
EXP-0011 bleibt als Entscheidungsnachweis verfügbar.

## Vergleich

| Option | unmittelbarer Nutzwert | Evidenzreife | Kopplung | Reversibilität | zentrale Last |
|---|---:|---:|---:|---:|---|
| A — V2 | hoch | hoch für Rollen | mittel–hoch | mittel | v2-Migration, Publikationslücke |
| B — V1 plus Begleiter | mittel–hoch | hoch | niedrig–mittel | hoch | Join und zweiter Vertrag |
| C — Publikationsregel-Experiment | mittelbar | offen | niedrig | sehr hoch | weiterer Evidenzschritt |
| D — V3 | potenziell hoch | gemischt | hoch | niedrig–mittel | breite Migration ohne Regel |
| F — unabhängiger Ast | getrennt | offen | niedrig–mittel | hoch | Identitätsfrage bleibt offen |
| K — pausieren | keine neue Wirkung | ausreichend zum Stoppen | keine | vollständig | kein neuer Nutzwert |

## Gate-Bewertung

EXP-0011 beseitigt die Unsicherheit, ob Rollen und Provenienz technisch
verlustfrei projizierbar sind: Das gelingt in allen drei Varianten. Es
entscheidet nicht die Priorität zwischen maximaler Kompatibilität, einem
zusammenhängenden v2-Bericht und einer neuen Publikationsstufe.

Wenn ein nächster Produktnutzen im Identitätsast gewünscht ist, ist A die
engste zusammenhängende Option. B ist bei dominanter v1-Kompatibilität
vertretbar. C ist die belastbarste Fortsetzung, wenn eine eigene
Publikationsentscheidung fachlich wichtig ist. D besitzt ohne Produktregel
noch keine proportionale Evidenzreife.

Mit der ausdrücklichen Auswahl von A ist diese Bewertung abgeschlossen.
WI-0013 übernimmt ausschließlich den zusammenhängenden V2-Bericht mit den
fünf bestehenden Produktstufen. B, C, D, F und K sind nicht ausgewählt.
Insbesondere wird weder ein Evidenzbegleiter noch eine Publikationsstufe,
Publikationsregel oder unabhängige Produktlinie autorisiert.

## Kanten, die nicht überschritten werden

- Kein EXP-0011-Oracle wird zur Produktentscheidung.
- Die zwei `candidate_related`-Restfälle werden nicht umklassifiziert.
- Standardsvalidität ist kein bibliografisches Identitätsorakel.
- Keine Option autorisiert reale/private Medien, automatische Suche,
  Persistenz, Routing, Browser, REST, Agents oder Writes.
- Fachsysteme bleiben führend; SammlungsLotse wirkt unterstützend und
  read-only.
