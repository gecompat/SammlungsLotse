# EXP-0016: Synthetische EPUB-Navigationskontext- und Sicherheitsmatrix qualifizieren

Status: DONE — EXECUTED, METHOD PASSED; THREE STRATEGIES ELIGIBLE_WITH_TRADEOFFS

Stand: 2026-09-01

Artifact: EXP-0016

## Auswahl und Zweck

Der Nutzer hat in GATE-0018 am 2026-09-01 ausdrücklich Option A ausgewählt.
EXP-0016 prüft ausschließlich an synthetischen Fällen, ob ein enger lokaler
Experimentparser Navigationskontexte von automatisch oder aktiv
verarbeitbaren Ressourcen, Package-Links, anderen Schemata und mehrdeutigen
Täuschungsfällen trennen kann. Drei vorab gebundene Strategien machen die
asymmetrischen Kosten einer möglichen späteren Differenzierung sichtbar.

Die Auswahl autorisiert diesen Experimentvertrag und seine getrennte
Ausführung nach Merge, Post-Merge-Prüfung und sauberem Commit-Preimage. Sie
autorisiert keine Produktregel, keine Änderung am WI-0004-Review-Gate und
keinen Produktcode. Das Ergebnis öffnet unabhängig von seiner Richtung ein
neues getrenntes Ergebnisgate.

## Gebundene Ausgangslage

- EXP-0015 ist `done`; sein privates Aggregat enthält ausschließlich die
  grobe Klasse `content.navigation=3`.
- EXP-0015 belegt weder konkreten Tag- oder Dokumentkontext noch
  Nutzeraktivierung, automatische Verarbeitung, Erreichbarkeit oder
  Vertrauenswürdigkeit.
- WI-0004 bleibt unverändert und leitet jede durch sein flaches Muster
  erkannte HTTP(S)-Remote-Referenz weiterhin fail-safe auf `review`.
- TEST-0001 0.3.0 bleibt unverändert. EXP-0016 erzeugt keine neue
  Produktfixture-Version und nutzt ausschließlich eigene synthetische
  Experimentfälle.

EXP-0015, sein Ergebnis, sein historischer Validator und sämtlicher
Produktcode bleiben unverändert.

## Standardsgebundenes Orakel

Das Ausführungspreimage bindet die folgenden Primärquellen:

- [EPUB 3.3, W3C Recommendation vom 2026-01-13](https://www.w3.org/TR/2026/REC-epub-33-20260113/);
- [EPUB Reading Systems 3.3, W3C Recommendation vom 2024-10-17](https://www.w3.org/TR/2024/REC-epub-rs-33-20241017/);
- [HTML Living Standard](https://html.spec.whatwg.org/), abgerufen und in
  Profil und Fallmanifest am 2026-09-01 kenntlich gemacht.

Für das Orakel gelten daraus nur diese eng benötigten Aussagen:

- ein ausgehender HTML-Hyperlink ist keine Publication Resource;
- ein Package-`link` kann eine externe Linked Resource bezeichnen, deren
  Abruf und Unterstützung optional sind;
- eine Remote Publication Resource ist von einem ausgehenden Hyperlink und
  einer Linked Resource getrennt;
- externe HTTP(S)-Links und Schemata mit Hilfsanwendung besitzen
  Nutzerzustimmungs- und Sicherheitsbelange;
- `data:` und `file:` sind keine harmlosen Ersatzformen für einen externen
  Hyperlink;
- ein HTML-`link` mit mehreren `rel`-Werten kann zugleich Hyperlink und
  automatisch verarbeitbarer External Resource Link sein.

Das Orakel behauptet weder eine einheitliche Implementierung aller
Lesesysteme noch die Vertrauenswürdigkeit eines Ziels. Es entscheidet nur die
synthetische Kontext- und Schutzklasse des jeweiligen Falls.

## Feste synthetische Matrix

Das Ausführungspreimage materialisiert genau 48 benannte Fälle in einem
versionierten JSON-Manifest. Jeder Fall enthält genau einen kleinen
synthetischen Package-, XHTML-, EPUB-Navigation-, SVG- oder CSS-Ausschnitt,
den Dokumenttyp, die erwartete Kontextklasse, die erwartete Schemagruppe und
die erlaubte Strategiefolge. Titel, Autoren, Identifier, private Inhalte und
private Locators fehlen.

Die 48 Fälle verteilen sich vorab wie folgt:

1. acht direkte nutzeraktivierte XHTML-, Navigation- und SVG-Hyperlinks;
2. sechs externe Package-`link`-Kontexte;
3. zehn automatisch verarbeitbare Manifest-, Bild-, Medien-, Stylesheet-,
   CSS- oder eingebettete Ressourcen;
4. sechs aktive, skriptende oder formulargebundene Netzwerkkontexte;
5. acht lokale, fragmentgebundene, `data:`, `file:`, `mailto:`, `tel:`,
   `ftp:` oder `urn:`-Varianten;
6. zehn mehrdeutige oder täuschende Fälle mit Misch-`rel`,
   protokollrelativer URL, Zeichenreferenz, Groß-/Kleinschreibung,
   Whitespace, fremdem Namespace, Kommentar-/Scriptliteral oder
   absichtlich nicht sicher klassifizierbarem Markup.

Mindestens je ein Fall bindet `http` und `https`, einfache und doppelte
Attribute, XML-Zeichenreferenzen, XHTML-`a` und `area`, SVG-`a`, ein
EPUB-Navigationsdokument, OPF-`link`, Manifest-`item`, HTML-`link` mit
`rel="next stylesheet"`, `img`, `audio` oder `video`, `script`, `form`,
CSS-`url(...)` und `@import`. Ein Fall kann mehrere syntaktische Merkmale
enthalten, gehört aber genau einer vorab festgelegten Orakelklasse an.

## Kontext- und Schemataxonomie

Der Experimentrunner gibt ausschließlich diese Kontextklassen aus:

- `content.user_activated_hyperlink`;
- `package.optional_linked_resource`;
- `publication.automatic_remote_resource`;
- `content.active_or_submission`;
- `reference.local_or_other_scheme`;
- `ambiguous_or_deceptive`.

Die Schemagruppe ist genau eine von:

- `http`;
- `https`;
- `network_path_reference`;
- `local_relative_or_fragment`;
- `data_or_file`;
- `helper_or_other`;
- `none`.

Unbekannte Elemente, Attribute, `rel`-Kombinationen, ungültiges Markup,
mehrere widersprüchliche Referenzen oder eine nicht eindeutige
Schemabestimmung werden nicht geraten. Sie ergeben
`ambiguous_or_deceptive` und die fail-closed Strategiefolge `review` oder
`abstain`.

## Vorab gebundene Vergleichsstrategien

Der Runner bewertet jeden Fall gegen genau drei synthetische Strategien:

### S1 — `review_all_http_s`

Jede erkannte HTTP(S)- oder protokollrelative Referenz bleibt `review`.
Andere Schemata werden ausschließlich gemäß ihrem gebundenen Schutzorakel als
`not_remote`, `review` oder `abstain` ausgewiesen. S1 bildet den
konservativen Vergleichspunkt ab, ohne WI-0004 auszuführen.

### S2 — `classify_and_keep_review`

Der Kontext wird erklärt, aber jede HTTP(S)-, protokollrelative,
automatische, aktive, Package-, mehrdeutige oder schutzbedürftige
Nicht-HTTP(S)-Referenz bleibt `review` beziehungsweise `abstain`. S2 darf nur
unnötige Reviewkosten sichtbar machen, nicht den Schutz reduzieren.

### S3 — `strict_navigation_candidate`

Nur ein eindeutig geparster direkter `http`- oder `https`-Hyperlink der
Klasse `content.user_activated_hyperlink` darf
`candidate_continue_deep_read_only` ergeben. Das Literal bezeichnet nur eine
synthetische Eignung für ein späteres getrenntes Produktgate. Es öffnet oder
lädt keinen Link und ist keine WI-0004-Entscheidung. Jeder andere oder
mehrdeutige Fall bleibt `review` oder `abstain`.

Keine Strategie wird durch EXP-0016 zum Produktstandard. Der Ergebnisbericht
ordnet die Strategien nicht automatisch und spricht keine
Implementierungsempfehlung aus.

## Asymmetrische Fehlerkosten und Qualifikation

Die vorab gebundene Rangfolge lautet:

1. `critical_false_continue`: Eine automatische, aktive, Package-,
   protokollrelative, schutzbedürftige Nicht-HTTP(S)- oder mehrdeutige
   Referenz erhält fälschlich `candidate_continue_deep_read_only`. Bereits ein
   Fall qualifiziert die Strategie nicht.
2. `context_false_negative`: Eine im Orakel enthaltene Referenz oder
   Schutzklasse bleibt unerkannt. Bereits ein Fall qualifiziert die Strategie
   nicht.
3. `context_mismatch`: Kontext- oder Schemagruppe weicht vom Orakel ab.
4. `conservative_review`: Ein eindeutiger direkter HTTP(S)-Hyperlink bleibt
   auf `review`. Dies ist sichtbarer manueller Aufwand, aber kein
   Sicherheitsfehler.
5. `abstention`: Ein gebundener Mehrdeutigkeitsfall bleibt fail-closed. Dies
   ist zulässig und wird getrennt gezählt.

Die beiden ersten Fehler dominieren jede mögliche Reduktion konservativer
Reviews. Eine Strategie ist nur `eligible_with_tradeoffs`, wenn alle 48 Fälle
zweimal verarbeitet wurden, beide Wiederholungen semantisch identisch sind,
Kontext und Schemagruppe exakt zum Orakel passen, null kritische
Fehlfortsetzungen und null False Negatives auftreten und alle verbotenen
Wirkungen fehlen. Sonst lautet ihr Status `not_qualified`.

Der methodische Gesamtstatus ist davon getrennt. Er kann `pass` lauten,
obwohl eine oder mehrere Strategien `not_qualified` sind, sofern der Runner
das vorab gebundene Ergebnis vollständig und wahrheitsgemäß ausweist.

## Ausführungs- und Ergebnisgrenze

Der Python-3.12-Standardbibliotheksrunner liegt ausschließlich unter
`tools/experiments/`. Er importiert und startet keinen Code unter
`src/sammlungslotse/`. Er liest nur Profil und Fallmanifest, erzeugt keine
EPUB-Datei, extrahiert nichts, startet keinen fachlichen Subprozess und
besitzt keinen Netzwerkclient.

Ein read-only Git-Aufruf darf vor der Ausführung ausschließlich den sauberen
Commit und die gebundenen öffentlichen Experimentdateien feststellen. Er
erhält keine Medienlocators. Arbeits- und Ergebnisziele liegen nur unter den
für SammlungsLotse vorgesehenen `C:\rep\tmp`- beziehungsweise
`C:\rep\artifacts`-Unterpfaden; der einzucheckende Bericht enthält keine
absoluten Pfade oder Hostdaten.

Das Ergebnis enthält ausschließlich:

- Schema, Experimentreferenz und Preimage-Commit;
- Hashbindungen für Profil, Manifest und Runner;
- feste Fall-, Klassen-, Schemata- und Wiederholungszahlen;
- pro Strategie die fünf Fehl- und Aufwandmetriken sowie
  `eligible_with_tradeoffs` oder `not_qualified`;
- methodische Akzeptanzwerte;
- boolesche Nachweise für Determinismus, Pfadfreiheit, fehlende private
  Eingänge, fehlende Produktimporte, fehlendes Netzwerk, fehlende
  Persistenz, fehlende Bestandswirkung und vollständiges Cleanup;
- methodischen Gesamtstatus `pass` oder `inconclusive`.

Snippets oder einzelne URLs werden nicht in den Ergebnisbericht kopiert. Das
versionierte Fallmanifest bleibt die einzige Detailquelle der vollständig
synthetischen Orakel.

## Ergebnis

Das saubere Ausführungspreimage ist Commit
`969fa6331afdfc4ceb808ffeed71f7a30193205b`. Vor dem synthetischen Hauptlauf
bestanden auf genau diesem Commit beide erforderlichen GitHub-Checks
`repository-quality` und `registry-integrity`.

Der gebundene Doppellauf verarbeitete genau 48 Fälle mit insgesamt
96 Parserläufen. Beide Wiederholungen waren semantisch identisch. Alle sechs
Kontextklassen und die sechs tatsächlich verwendeten Schemagruppen stimmten
ohne Context Mismatch oder False Negative mit dem Orakel überein. Alle
16 methodischen Akzeptanzwerte bestanden.

S1 `review_all_http_s` und S2 `classify_and_keep_review` behielten jeweils
acht konservative Reviews und zehn fail-closed Enthaltungen. S3
`strict_navigation_candidate` reduzierte die konservativen Reviews auf null
und behielt dieselben zehn Enthaltungen. Alle drei Strategien hatten null
kritische Fehlfortsetzungen, null False Negatives und null Context Mismatches
und sind innerhalb der gebundenen Matrix `eligible_with_tradeoffs`.

Private Eingänge, Produktimport, Netzwerk, Persistenz, tiefer Werkzeuglauf
und Bestandswirkung fehlten. Produktcode blieb unverändert; Taskmaterial
wurde vollständig bereinigt. Das 2.279-Byte-Ergebnis besitzt den SHA-256-Wert
`6c748dd1477dba56a37e19b7a5bf798d32e702e8d6d2a230ebfa3c98d775db08`.
Der historische Validator lautet:

```powershell
python tools/experiments/validate_exp_0016_result.py
```

GATE-0019 trennt die synthetische Trennbarkeit von jeder möglichen
Produktfortsetzung. Insbesondere ist `candidate_continue_deep_read_only`
keine Freigabe, einen Link zu öffnen oder das WI-0004-Review-Gate zu lockern.

## Methodische Akzeptanzkriterien

EXP-0016 ist methodisch nur bestanden, wenn alle folgenden 16 Kriterien
erfüllt sind:

1. Git-Preimage, GATE-0018, EXP-0015, WI-0004, WI-0011, TEST-0001 und die
   drei Standardsquellen sind gebunden;
2. genau 48 rein synthetische Fälle und ihre feste Verteilung sind
   materialisiert;
3. jeder Fall besitzt genau eine erwartete Kontextklasse, Schemagruppe und
   erlaubte Folge je Strategie;
4. alle sechs Kontextklassen und sieben Schemagruppen sind abgedeckt;
5. Package-, XHTML-, EPUB-Navigations-, SVG- und CSS-Kontexte sind vertreten;
6. HTTP(S), protokollrelative, lokale und andere Schemata bleiben getrennt;
7. Misch-`rel`, Zeichenreferenz-, Case-, Whitespace-, Namespace-, Literal-
   und ungültige Täuschungsfälle sind enthalten;
8. Unbekanntes und Mehrdeutiges führt fail-closed zu `review` oder
   `abstain`;
9. S1, S2 und S3 werden ohne nachträgliche Schwellen- oder Orakeländerung
   vollständig verglichen;
10. kritische Fehlfortsetzung, False Negative, Kontextabweichung,
    konservatives Review und Enthaltung bleiben getrennte Metriken;
11. null kritische Fehlfortsetzungen und null False Negatives sind harte
    Strategiebedingungen;
12. zwei vollständige Wiederholungen sind semantisch identisch;
13. der Ergebnisbericht wird vollständig aus Profil, Manifest und Läufen neu
    berechnet und hashgebunden;
14. fokussierte Positiv-, Negativ-, Manipulations- und Grenztests bestehen;
15. private Eingänge, Produktimport, Netzwerk, Persistenz, tiefer
    Werkzeuglauf, öffentliche Produktfläche und Bestandswirkung fehlen;
16. Produktcode bleibt unverändert und alle task-privaten Arbeitsdaten werden
    vollständig bereinigt.

Ein methodischer `pass` oder eine `eligible_with_tradeoffs`-Strategie ist
keine Produktfreigabe und kein Beleg der Vertrauenswürdigkeit eines Ziels.

## Historisch durchgeführte Ausführungsfolge

1. Die Auswahl- und Vertragswave wurde validiert, gemergt und auf
   `origin/main` post-merge geprüft.
2. Profil, 48-Fall-Manifest, Runner und fokussierte Tests wurden danach in
   einem neuen isolierten Worktree ohne Produktcode implementiert und als
   sauberes Preimage committed.
3. Erst nach grüner CI auf diesem exakten Preimage wurde der synthetische
   Doppellauf ausgeführt.
4. Der historische Validator bindet Profil, Manifest, Runner und Ergebnis an
   das Preimage, ohne den Experimentlauf in späteren Produktständen neu
   auszuführen.
5. Das Ergebnis öffnet GATE-0019; EXP-0016 wählt keine Produktfortsetzung.

## Harte Grenzen

- ausschließlich synthetische, versionierte Fälle; keine privaten Medien,
  Pfade, Metadaten, Hashes oder Rohoutputs;
- kein Import, Start oder Ändern von Produktcode;
- kein Netzwerk, fachlicher Subprozess, tiefer Werkzeuglauf, Calibre,
  Persistenz oder direkte Datenbanknutzung;
- keine automatische Lockerung oder Umgehung des WI-0004-Review-Gates;
- keine neue öffentliche CLI-, API-, UI-, Agent-, Diagnose-, Such-, Routing-
  oder Writerfläche;
- keine Bestandsänderung im führenden Fachsystem;
- jede Produktfortsetzung benötigt nach dem Ergebnis ein eigenes Gate und
  Produktcode zusätzlich einen registrierten angenommenen Arbeitsgegenstand.

## Nicht-Ziele

- keine erneute Auswertung der drei privaten EPUBs;
- keine Aussage über konkrete private Referenzen, Ziele oder Nutzerabsicht;
- keine Erreichbarkeits-, Download-, Browser- oder Lesesystemprüfung;
- keine allgemeine HTML-, URL-, EPUB- oder Threat-Model-Implementierung;
- keine Reparatur, Erklärung oder Lockerung von WI-0004 oder WI-0011;
- keine Produkt-, Architektur-, Provider-, UI- oder Writerentscheidung.
