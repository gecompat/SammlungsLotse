# EXP-0011: Rollenbewusste Metadaten- und Identitätsverträge produktcodefrei vergleichen

Status: DONE — EXECUTED, 14/14 METHOD CRITERIA PASSED

Stand: 2026-08-31

Artifact: EXP-0011

## Ausführungsergebnis

Der produktcodefreie Lauf wurde aus dem vollständigen Git-Preimage
`a5aeb0196d8d6a32fc90da46ca158ba693c6a0db` ausgeführt. Genau 15 gebundene
synthetische Paare wurden in zwei unabhängigen Wiederholungen auf V1, V2 und
V3 projiziert. Beide Wiederholungen besitzen denselben semantischen
SHA-256-Wert
`ec22878a8668852498b13181a24387c8f78838e2ee13eefe2c020bdd06df9cc5`.

Alle 14 methodischen Kriterien sind erfüllt. Jede Variante verliert auf der
acht Fälle umfassenden Rollenmatrix null Felder, deckt 145/145 projizierte
Werte mit Quelle und Status ab, erhält die fünf vorhandenen
Produktentscheidungen vollständig und lässt beide
`identity.work.title_creator`-Restfälle sichtbar. V1 erhält die 13
qualifizierten v1-Berichte bytegenau; V1 und V2 weisen die
Publikationsstufenlücke aus, V3 stellt eine getrennte, mangels Produktregel
korrekt `not_assessed` bleibende Stufe dar.

Alle drei Varianten sind `eligible_with_tradeoffs`; keine wurde als
Zielvertrag ausgewählt. Ergebnis und vollständige Projektionen stehen unter
`experiments/ebook/exp-0011/result.json`. Die Fortsetzung wird ausschließlich
im getrennten [GATE-0012](EBOOK_GATE_0012_AFTER_EXP0011.md) entschieden.

## Gate-Entscheidung

Der Nutzer hat am 2026-08-31 in GATE-0011 ausdrücklich Option A gewählt.
Damit ist genau dieses produktcodefreie Vertrags- und Evidenzexperiment
angenommen. Die Optionen B, C, D, E, F und K bleiben nicht ausgewählt.

Die Auswahl autorisiert weder eine Produktregel noch ein öffentliches
Berichtsschema, eine neue Identitätsstufe oder Produktcode. Planung und
Registrierung werden in dieser Wave integriert; der Experimentlauf beginnt
erst getrennt aus einem danach verifizierten `origin/main`.

## Entscheidungsfrage

Welche von drei vorab gebundenen Vertragsformen erhält die bereits
standardgebundenen Identifier-Rollen, Publikationsänderung und
Collection-Provenienz am vollständigsten, erklärt die bestehenden
Identitätsentscheidungen am klarsten und besitzt die kleinste vertretbare
Migrationslast?

Das Experiment soll insbesondere klären:

- ob der öffentliche v1-Bericht bytegenau unverändert bleiben kann, während
  ein getrennter Evidenzumschlag die fehlenden Rollen transportiert;
- ob ein rollenbewusster v2-Bericht mit den bisherigen fünf
  Identitätsebenen genügt;
- welchen zusätzlichen Erkenntniswert eine eigene Publikationsstufe liefert;
- welche Variante Collection-Mitgliedschaft korrekt von Werkreferenz trennt;
- wie die zwei verbleibenden `candidate_related`-Werkabweichungen in jeder
  Variante erklärt werden, ohne eine neue Entscheidungsregel zu erfinden;
- welche bestehenden Verbraucher und Qualifikationsnachweise bei einer
  späteren Produktübernahme migriert werden müssten.

## Getrennte Autoritäten

Fünf Aussagearten werden nicht zusammengezogen:

1. Die standardgebundene Projektion aus EXP-0010 bestimmt die beobachteten
   Identifier-Rollen, `dcterms:modified`-Werte und Collection-Strukturen.
2. TEST-0001 und die EXP-0010-Fallprovenienz bestimmen die gebundenen
   synthetischen Fälle und Oracles.
3. Der aktuelle WI-0012-v1-Bericht liefert ausschließlich die bestehende
   Produktbeobachtung und ihre Entscheidungen.
4. Die drei Varianten sind experimentelle Vertragsprojektionen und kein
   implementiertes Produktmodell.
5. Die Migrationsbewertung beschreibt statisch betroffene Verträge und
   Nachweise; sie behauptet keine reale Verbraucherhäufigkeit.

Weder das Falloracle noch EPUBCheck noch eine Variantenbewertung darf als
Eingang einer neuen Identitätsentscheidung verwendet werden.

## Gebundenes Material

Die spätere Ausführungswave verwendet ausschließlich bereits versioniertes,
synthetisches Material:

- fünf aktive TEST-0001-Identitätspaare: `byte_equal`, `repackaged`,
  `sample_full`, `title_collision` und `translation`;
- acht konforme EXP-0010-Qualitätsfälle;
- die zwei getrennten nicht konformen EXP-0010-Kontrollen;
- den aktuellen WI-0012-Qualifikationsnachweis als v1-Produktbeobachtung;
- den historischen EXP-0010-Ergebnisvertrag und sein eingefrorenes
  Produktpreimage als Standards-, Oracle- und Provenienznachweis.

Damit werden genau 15 Paare betrachtet. Die acht konformen EXP-0010-Fälle
bilden weiterhin die semantische Rollenmatrix. Die zwei nicht konformen
Kontrollen bleiben `not_assessed` und werden nicht in eine
Produktqualitätsaussage umgedeutet. Fehlende Rollen in TEST-0001 werden
explizit als nicht vorhanden dargestellt und nicht erfunden.

Keine Fixture, kein Oracle und kein historischer Ergebnisvertrag wird
verändert oder neu etikettiert.

## Vorab gebundene Varianten

Die Variantenbezeichnungen und Feldnamen sind ausschließlich
Experimentbegriffe. Sie reservieren kein öffentliches Produktschema.

### V1 — Unveränderter v1-Bericht plus Evidenzbegleiter

Der aktuelle JSON-Bericht
`sammlungslotse/ebook-identity-candidate-report/v1` bleibt bytegenau
unverändert. Ein getrenntes, über `input_index` zugeordnetes
Experimentobjekt transportiert zusätzlich:

- den durch `package@unique-identifier` gebundenen primären Identifier;
- zusätzliche Identifier samt vorhandenem `identifier-type`;
- `dcterms:modified`;
- alle Collection-Mitgliedschaften mit Name, Typ, Identifier und
  Gruppenposition;
- die Herkunft jedes Werts aus der standardgebundenen Projektion.

V1 minimiert die unmittelbare Verbraucheränderung, erzeugt aber zwei
zusammenzuführende Verträge und besitzt weiterhin keine eigene
Publikationsentscheidung.

### V2 — Rollenbewusster Bericht v2 mit fünf Stufen

Ein experimenteller Gesamtbericht ersetzt die flachen Felder
`identifiers` und `work_references` durch rollen- und provenienzbewusste
Strukturen. Byte, Paket, Repräsentation, Ausgabe und Werk bleiben als fünf
Stufen erhalten. Alle bestehenden Entscheidungen, Regel-IDs sowie positiven,
negativen und fehlenden Evidenzkanäle werden unverändert abgebildet.

V2 beseitigt die irreführende Collection-Benennung in einem Vertrag, kann
das gebundene Publikationsoracle aber weiterhin nicht als eigene Stufe
ausdrücken.

### V3 — Rollenbewusster Bericht v2 mit Publikationsstufe

V3 verwendet dieselben strukturierten Metadaten wie V2 und ergänzt zwischen
Repräsentation und Ausgabe genau eine experimentelle Stufe `publication`.
Die vorhandenen fünf Produktentscheidungen bleiben unverändert. Die neue
Stufe enthält mangels Produktregel keine Produktentscheidung und trägt
`assessment: not_assessed`; das bereits gebundene EXP-0010-
Publikationsoracle wird nur außerhalb der Variantenprojektion verwendet, um
die Ausdrucksfähigkeit des Stufenvertrags zu prüfen.

V3 besitzt die vollständigste Ausdrucksfähigkeit, bringt aber die größte
Schema-, CLI-, Test- und Nachweismigration mit und kann eine spätere
Architekturentscheidung vorwegnehmen.

## Gemeinsame Mindeststruktur

V1 bis V3 müssen pro Eingang verlustfrei darstellen können:

- `input_index` und unveränderte bestehende Hash-/Größenbeobachtungen;
- primären Identifierwert und die referenzierte Element-ID;
- jeden zusätzlichen Identifierwert und vorhandenen Typ;
- `dcterms:modified`;
- jede Collection mit Name, `collection-type`, Identifier und
  `group-position`;
- Quelle und Status `observed`, `derived` oder `missing` für jedes
  experimentell projizierte Feld.

Collection-Werte dürfen in keiner Variante als explizite Werkreferenz
bezeichnet werden. Fehlende Werte bleiben fehlend; leere Zeichenketten,
synthetische Defaults oder Oraclewerte ersetzen keine Beobachtung.

## Messvertrag

Für jede Variante wird ein Vektor ohne gewichteten Gesamtscore erhoben:

- **Rollenverlust:** Anzahl und Liste der gegenüber der standardgebundenen
  Quelle verlorenen oder zusammengezogenen Felder;
- **Semantische Benennung:** Verstöße gegen die Trennung von Identifierrolle,
  Collection-Mitgliedschaft und Werkbezug;
- **Provenienzdeckung:** Anteil der projizierten Werte mit eindeutiger Quelle;
- **Entscheidungstreue:** Gleichheit der vorhandenen fünf Entscheidungen,
  Regel-IDs und Evidenzkanäle mit dem aktuellen v1-Bericht;
- **Publikationsausdruck:** ob eine Publikationsaussage getrennt darstellbar
  ist, ohne Ausgabe oder Werk umzudeuten;
- **Restfall-Erklärbarkeit:** welche beobachtete Evidenz bei
  `same-primary-strong-content-conflict` und
  `shared-untyped-additional-different-primary` sichtbar ist;
- **v1-Kompatibilität:** Bytegleichheit des v1-Berichts und erforderlicher
  Join- oder Migrationsaufwand;
- **Migrationsfläche:** statische Liste betroffener Modell-, JSON-, CLI-,
  Test- und Qualifikationsverträge;
- **Determinismus und Grenzen:** zwei semantisch identische Wiederholungen,
  pfadfreie Ausgabe, unveränderte Eingänge und Null-Bestandswirkung.

Die zwei Restfälle bleiben in allen Varianten die aktuellen
`candidate_related`-Beobachtungen aus `identity.work.title_creator`.
EXP-0011 misst, ob eine Variante die maßgebliche Evidenz verständlicher
darstellt; es erklärt keinen Fall durch eine neue Produktregel für gelöst.

## Akzeptanzkriterien

EXP-0011 ist methodisch ausgeführt, wenn:

1. Plan, Variantenvertrag, Runner, TEST-0001-Manifest, EXP-0010-Manifest und
   -Ergebnis sowie aktueller WI-0012-Qualifikationsnachweis vollständig
   SHA-256- und Git-Preimage-gebunden sind;
2. genau die 15 gebundenen Paare und keine realen Medien betrachtet werden;
3. V1, V2 und V3 als drei getrennte Projektionen vollständig erzeugt werden;
4. V1 den aktuellen v1-Bericht für alle 13 qualifizierten Produktfälle
   bytegenau erhält;
5. jede beobachtete Identifierrolle, Publikationsänderung und
   Collection-Struktur der acht konformen EXP-0010-Fälle in jeder Variante
   verlustfrei und mit Provenienz darstellbar ist;
6. keine Variante Collection-Mitgliedschaft als Werkreferenz bezeichnet;
7. die vorhandenen fünf Produktentscheidungen, Regel-IDs und Evidenzkanäle
   in keiner Variante verändert werden;
8. V1 und V2 die fehlende eigene Publikationsstufe sichtbar als Lücke
   ausweisen und V3 sie getrennt darstellen kann;
9. beide `candidate_related`-Restfälle samt tatsächlicher Regel
   `identity.work.title_creator` in jeder Variante sichtbar bleiben;
10. für jede Variante eine vollständige v1-Feldabbildung sowie eine statische
    Migrationsflächenliste vorliegt;
11. zwei unabhängige Projektionen denselben semantischen Digest liefern;
12. Eingänge unverändert, Ausgaben pfadfrei und Netzwerk, Container,
    Persistenz, Fachsysteme sowie Bestände unberührt bleiben;
13. Produktcode, öffentliches Schema, TEST-0001, EXP-0010 und vorhandene
    Qualifikationsnachweise bytegenau unverändert bleiben;
14. ein CI-geeigneter Validator Ergebnis, Bindungen, Messvektoren und alle
    Akzeptanzwerte ohne erneute Experimentausführung nachrechnet.

Ein methodisch bestandenes Experiment darf Varianten als `eligible`,
`eligible_with_tradeoffs` oder `not_eligible` einordnen. Es wählt keinen
Zielvertrag. Selbst eine eindeutig führende Variante benötigt ein neues
getrenntes Ergebnisgate vor jeder Produktübernahme.

## Fail- und Stoppkriterien

Der Versuch wird nicht als ausgeführt dargestellt, wenn:

- eine Variante nach Kenntnis ihres Vergleichsergebnisses umdefiniert wird;
- Oraclewerte als beobachtete Metadaten oder Produktentscheidungen erscheinen;
- eine neue Heuristik die zwei Restfälle im Experiment umklassifiziert;
- V1 seinen bestehenden v1-Bericht verändert;
- eine Collection erneut als Werkreferenz bezeichnet wird;
- fehlende Metadaten durch erfundene Defaults verdeckt werden;
- Produktcode, öffentliches Schema, Fixtures, historische Ergebnisse oder
  bestehende Qualifikationsnachweise verändert werden;
- reale/private Medien, Netzwerkzugriff, Persistenz, Pfadlecks oder
  Bestandswirkungen auftreten.

## Vorgesehener Ausführungsrahmen

Die getrennte Ausführungswave darf ausschließlich Standardbibliothekscode
unter `tools/experiments/` und versionierte Experimentartefakte unter
`experiments/ebook/exp-0011/` ergänzen. Sie liest die gebundenen Quellen
read-only, erzeugt keine neuen Medien und benötigt weder Container noch
Netzwerk.

Vorgesehene Nachweise vor dem Lauf:

    python tools/experiments/run_exp_0011.py --validate-profile
    python -m unittest tests.experiments.test_exp_0011 -v

Der tatsächliche Lauf erfolgt erst aus einem sauberen, eingecheckten
Preimage:

    python tools/experiments/run_exp_0011.py

CI-geeignete Ergebnisprüfung:

    python tools/experiments/run_exp_0011.py --validate-result

Diese Befehle sind im getrennten Ausführungspreimage implementiert. Der
tatsächliche Experimentlauf wurde noch nicht ausgeführt und bleibt bis zum
sauberen, eingecheckten Preimage gesperrt.

## Ausführungsreihenfolge

1. GATE-0011-Auswahl und dieser akzeptierte Experimentvertrag werden
   gemeinsam nach `main` integriert.
2. Der kanonische `main`-Stand und die erforderlichen GitHub-Prüfungen werden
   post-merge verifiziert.
3. Erst danach beginnt die Implementierung des Experimentprofils in einem
   neuen isolierten Worktree.
4. Der vollständige Experimentpreimage wird vor dem Lauf commitgebunden.
5. Ergebnis und Validator werden in einer eigenen Wave integriert.
6. Vor jeder Produktübernahme bewertet ein neues getrenntes Ergebnisgate V1,
   V2, V3, unabhängige Fortsetzung und Pausieren erneut.
