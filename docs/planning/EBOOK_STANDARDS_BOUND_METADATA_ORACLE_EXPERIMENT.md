# EXP-0010: EPUB-Metadaten- und Oracle-Evidenz standardgebunden prüfen

Status: DONE — METHODE 12/12, PRODUKTQUALITÄT NOT_QUALIFIED

Stand: 2026-08-28

Artifact: EXP-0010

## Gate-Entscheidung

Der Nutzer hat am 2026-08-28 in GATE-0009 ausdrücklich Option A gewählt.
Damit ist genau dieses produktcodefreie Evidenzexperiment angenommen.
Die Auswahl autorisiert keine Produktkorrektur, Kandidatensuche,
Architektur-, Provider-, Persistenz-, UI-, API-, Agent- oder
Writerentscheidung.

## Entscheidungsfrage

Welche Qualitätsaussage trägt der unveränderte WI-0009-
Identitätskandidatenbericht, wenn primäre und zusätzliche Identifier,
Publikationsänderung sowie Collection-Name, -Typ, -ID und -Position in einer
vorab gebundenen synthetischen Matrix getrennt modelliert werden?

Das Experiment soll insbesondere klären:

- ob der Dienst den primären EPUB-Identifier unzulässig mit zusätzlichen
  Identifiern gleichbehandelt;
- ob ein gleicher Identifier bei stark widersprüchlichem Inhalt weiterhin
  ohne Enthaltung zu `candidate_same` führt;
- welche Produktentscheidungen allein aus Collection-Namen entstehen;
- ob mehrere oder verschiedene Collections ohne behauptete Werkidentität
  angemessen behandelt werden;
- welche Aussage im aktuellen Produktvertrag für die Ebene der EPUB-
  Publikation fehlt;
- ob nicht konforme Metadatenkontrollen getrennt von der
  Produktqualitätsmatrix sichtbar bleiben.

## Getrennte Autoritäten

Vier Aussagearten dürfen nicht zusammengezogen werden:

1. EPUB-3.3-Autorenanforderungen bestimmen Struktur und Rollen der
   Paketmetadaten.
2. EPUBCheck 5.3.0 liefert unabhängige Konformitätsevidenz für die
   materialisierten synthetischen Pakete.
3. Das Testorakel stammt aus der vorab gebundenen kontrollierten
   Fallprovenienz und nicht aus dem Produktbericht oder aus EPUBCheck.
4. Der unveränderte WI-0009-Dienst liefert die zu messende
   Produktbeobachtung.

Standardkonformität ist keine bibliografische Wahrheit. Ein formal gültiges
Paket kann irreführende oder wiederverwendete Identifier enthalten. Ebenso
belegt eine gemeinsame Collection nur die manifestierte Gruppenzugehörigkeit
und nicht automatisch dieselbe Publikation, Ausgabe oder dasselbe Werk.

## Primärquellenbindung

Stand und Abruf: 2026-08-28.

- [W3C EPUB 3.3](https://www.w3.org/TR/epub-33/), insbesondere 5.4
  `package`, 5.5.3.1.1 `dc:identifier`, 5.5.5 `dcterms:modified`, D.3.3
  `belongs-to-collection`, D.3.4 `collection-type`, D.3.7
  `group-position` und D.3.8 `identifier-type`;
- [W3C EPUB Reading Systems 3.3](https://www.w3.org/TR/epub-rs-33/),
  insbesondere 5.2 `Unique identifier` und 5.3 `Metadata`.

Der Paketvertrag bindet mindestens `dc:title`, `dc:identifier`,
`dc:language` und `dcterms:modified`. Das `package@unique-identifier`
verweist auf die ID des primären `dc:identifier`. Reading Systems sollen
nicht darauf vertrauen, dass derselbe Unique Identifier tatsächlich nur eine
Publikation bezeichnet, und bei etablierten Identifiern den
`identifier-type` berücksichtigen.

## Vorab gebundene Fallmatrix

Die Ausführungswave materialisiert genau zehn synthetische Paare. Acht Paare
bestehen aus strukturell EPUB-3.3-konformen Paketen. Zwei getrennte
Negativkontrollen verletzen absichtlich genau eine Metadatenpflicht und
werden nicht in die Produktqualitätsmetriken eingerechnet.

| Fall | Standard-/Metadatenkante | Vorab gebundene Fallwahrheit |
|---|---|---|
| `same-primary-minor-revision` | gleicher gebundener primärer Identifier, nur `dcterms:modified` und Paketbytes verschieden | gleiche Publikation und Ausgabe; Repräsentation bleibt gleich |
| `same-primary-strong-content-conflict` | gleicher primärer Identifier bei stark widersprüchlichem Inhalt | adversarielle Identifier-Wiederverwendung; Publikation, Ausgabe und Werk dürfen nicht ohne Gegenprüfung gleichgesetzt werden |
| `shared-typed-additional-different-primary` | verschiedene primäre Identifier, gleicher zusätzlicher ONIX-typisierter Identifier | verschiedene Publikationen und Ausgaben desselben synthetischen Werks |
| `shared-untyped-additional-different-primary` | verschiedene primäre Identifier, gleicher untypisierter Zusatzwert | verschiedene, nicht als werkgleich behauptete Publikationen |
| `series-overlap-distinct-works` | gleicher Collection-Name und dieselbe Collection-ID vom Typ `series` | verschiedene Werke derselben Serie; nur Beziehung, keine Gleichheit |
| `set-overlap-distinct-members` | gleicher Collection-Name und dieselbe Collection-ID vom Typ `set`, verschiedene Positionen | verschiedene Bestandteile desselben Sets; nur Beziehung, keine Gleichheit |
| `multiple-collections-partial-overlap` | zwei Collections links, eine überlappende Collection rechts | verschiedene Ausgaben desselben synthetischen Werks; Mehrfachzugehörigkeit bleibt erhalten |
| `different-collections-same-work` | verschiedene Collection-Namen und -IDs | verschiedene Ausgaben desselben synthetischen Werks; Collection-Konflikt ist kein Werkgegenbeweis |
| `invalid-missing-primary-binding` | `package@unique-identifier` verweist nicht auf ein vorhandenes Element | nicht konforme Kontrolle; bibliografische Ebenen werden nicht qualifiziert |
| `invalid-missing-modified` | `dcterms:modified` fehlt | nicht konforme Kontrolle; bibliografische Ebenen werden nicht qualifiziert |

Das Manifest bindet für jeden Fall zusätzlich:

- die erwartete EPUBCheck-Klasse je Seite;
- eine Publikationsentscheidung aus `same`, `different`, `abstain` oder
  `not_assessed`;
- erlaubte Entscheidungen für Byte, Paket, Repräsentation, Ausgabe und
  Werk;
- eine kurze fallbezogene Oracle-Begründung;
- Generatorfelder, Collection- und Identifier-Rollen sowie verbotene
  Wirkungen.

Der Produktdienst erhält weder das Oracle noch die kontrollierte
Fallprovenienz.

## Versuchsaufbau

Die getrennte Ausführungswave darf nur:

1. Manifest und Ausführungsprofil validieren;
2. jedes Paar unter einem neuen expliziten Taskpfad unter
   `C:\rep\tmp\SammlungsLotse\exp-0010` materialisieren;
3. die relevanten EPUB-3.3-Metadatenrollen unabhängig aus dem OPF
   projizieren;
4. jedes der zwanzig unterschiedlichen Einzelpakete einmal mit dem bereits
   qualifizierten, netzwerklosen EPUBCheck-5.3.0-Profil von WI-0005 prüfen;
5. alle zehn Paare zweimal neu materialisieren und mit dem unveränderten
   `IdentityCandidateService` auswerten;
6. eine pfadfreie Ergebnisdatei erzeugen und alle temporären Taskdaten
   entfernen.

Die EPUBCheck-Prüfung verwendet ausschließlich das bereits gebundene Profil
`wi-0005-epubcheck-5.3.0-temurin-21.0.12.1+1-podman-linux-amd64/v1` mit
`network=none`, unveränderlichem Eingang, task-privater Materialisierung und
vollständigem Cleanup. Es wird kein neuer Provider oder Download eingeführt.

## Messvertrag

Getrennt erhoben werden:

- erwartete und tatsächliche EPUBCheck-Klasse samt Codes;
- primärer Identifier, zusätzliche Identifier und deren Typ/Scheme;
- `dcterms:modified`;
- alle Collections mit Name, ID, Typ, Identifier und Gruppenposition;
- die flache Metadatenprojektion des unveränderten Produktdienstes;
- Publikationsoracle ohne behauptete Produktstufe;
- Oracle-Matrix, Fehlentscheidungen und Enthaltung für die fünf
  vorhandenen Identitätsstufen;
- kritische False Same auf Ausgabe und Werk;
- getrennte semantische Fähigkeitslücken für Identifier-Rollen,
  Collection-Semantik und Publikationsstufe;
- Wiederholungsdigest, Eingangs-Hashes, Pfadfreiheit, Wirkungen und Cleanup.

Die Produktqualitätsmetriken verwenden nur die acht konformen Matrixfälle.
Die zwei nicht konformen Kontrollen bleiben als eigene Beobachtungen
erhalten. Eine Metrik mit Nenner null wird `not_applicable` und nicht 1,0.

## Akzeptanzkriterien

EXP-0010 ist methodisch ausgeführt, wenn:

1. Manifest, Profil, Runner, bestehendes EPUBCheck-Profil und vollständiger
   WI-0009-Produktpreimage SHA-256-gebunden sind;
2. genau zehn vorab gebundene Paare materialisiert werden;
3. alle acht konformen Paare auf beiden Seiten ohne EPUBCheck-Fehler bestehen;
4. beide Negativkontrollen auf beiden Seiten die erwartete
   EPUBCheck-Fehlerklasse liefern;
5. primäre und zusätzliche Identifier samt Refinements getrennt
   rekonstruierbar bleiben;
6. eine, mehrere, gleiche und verschiedene Collections samt Typ, ID und
   Position getrennt rekonstruierbar bleiben;
7. jede Fallwahrheit ein vorab gebundenes Publikations-, Ausgaben- und
   Werkoracle mit Begründung besitzt;
8. alle Produktentscheidungen gegen das Oracle geprüft und kritische False
   Same einzeln sichtbar sind;
9. zwei unabhängige Produktwiederholungen semantisch identisch sind;
10. Eingänge unverändert, Ergebnis und Meldungen pfadfrei und Cleanup
    vollständig bleiben;
11. Produktcode, TEST-0001, Netzwerkgrenze, Fachsysteme, Persistenz und
    Bestände unverändert bleiben;
12. ein CI-geeigneter Validator den eingecheckten Ergebnisvertrag ohne
    erneute Container- oder Experimentausführung vollständig nachrechnet.

Ein methodisch bestandener Versuch darf die Produktqualität als
`qualified`, `qualified_with_findings` oder `not_qualified` ausweisen.
Gefundene Produktlücken werden nicht in dieser Wave korrigiert.

## Fail- und Stoppkriterien

Der Versuch wird nicht als ausgeführt dargestellt, wenn:

- ein Oracle nach Kenntnis eines Produkt- oder EPUBCheck-Ergebnisses geändert
  wird;
- EPUBCheck als bibliografisches Identitätsorakel verwendet wird;
- eine nicht konforme Kontrolle in die konforme Qualitätsmatrix gelangt;
- Experimentcode eigene Produktentscheidungen erzeugt;
- Produktcode, TEST-0001 oder ein produktiver Bestand verändert wird;
- ein kritischer False Same, eine Rollenlücke oder ein Cleanupfehler
  verdeckt wird;
- reale/private Medien, Netzwerkzugriff oder Pfadlecks auftreten.

Nach der Ergebnisintegration endet die autonome Arbeit an einem neuen
Ergebnisgate. EXP-0010 autorisiert keine Produktkorrektur.

## Vorgesehene Nachweise

Vor dem empirischen Lauf:

    python tools/experiments/run_exp_0010.py --validate-profile
    python -m unittest tests.experiments.test_exp_0010 -v

Der empirische Lauf darf erst von einem sauberen eingecheckten Preimage
erfolgen:

    python tools/experiments/run_exp_0010.py \
      --temp-root C:\rep\tmp\SammlungsLotse\exp-0010

CI-geeignete Ergebnisprüfung:

    python tools/experiments/run_exp_0010.py --validate-result

## Ausführungsergebnis

Der vollständige Lauf auf dem eingefrorenen Preimage
`fbb481b4e5f869943c0a668502d37e867b2db5ce` erfüllte alle zwölf
methodischen Akzeptanzkriterien. Alle 16 Einzelpakete der acht konformen
Qualitätsfälle bestanden EPUBCheck 5.3.0 ohne Befund. Die vier Pakete der
zwei getrennten Negativkontrollen lieferten erwartbar `OPF-030` und/oder
`RSC-005`. Zwei Produktwiederholungen erzeugten denselben semantischen Digest
`6ad0a299de564216adc4684a8d9cbd851f717d8b007ecaab5b3be530347b1973`.

Die Produktqualität lautet `not_qualified`. Drei konforme Fälle erzeugten
je einen kritischen False Same auf Ausgabe und Werk:

- gleicher primärer Identifier bei stark widersprüchlichem Inhalt;
- gleicher typisierter Zusatz-Identifier bei verschiedenen primären
  Identifiern und Ausgaben;
- gleicher untypisierter Zusatzwert bei verschiedenen primären Identifiern
  und kontrolliert verschiedenen Werken.

Damit sind sechs kritische False Same sichtbar. Die gezielte
`candidate_same`-Precision betrug auf Ausgabe und Werk je 0,25. Außerdem
belegt der Lauf getrennt die fehlende Publikationsstufe, eingeebnete
Identifier-Rollen und als `work_references` eingeebnete Collection-Semantik.
Die vier konformen Collection-Fälle entsprachen ihren Oracles; ein isoliertes
Collection-Veto würde die aktuelle False-Same-Ursache deshalb nicht beheben.

Der vollständige Ergebnisvertrag steht in
[`result.json`](../../experiments/ebook/exp-0010/result.json). README,
Manifest und Profil bleiben als gebundenes Preimage unverändert. Das Ergebnis
autorisiert keine Produktkorrektur. Die Fortsetzung ist in GATE-0010 offen zu
entscheiden.
