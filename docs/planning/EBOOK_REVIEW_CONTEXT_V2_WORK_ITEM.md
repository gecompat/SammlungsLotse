# WI-0014: Review-Kontexterklärung V2 für die EPUB-Eingangstriage umsetzen

Status: DONE — 16/16 COMMITGEBUNDENE PRODUKTKRITERIEN BESTANDEN

Stand: 2026-09-02

Artifact: WI-0014

## Auswahl und Zweck

Der Nutzer hat in GATE-0020 am 2026-09-01 ausdrücklich Option B ausgewählt.
WI-0014 ergänzt deshalb ausschließlich eine grobe, pfadfreie Erklärung für
den bereits bestehenden WI-0004-Reviewfall. Die Erklärung verwendet die in
EXP-0016 synthetisch qualifizierte Kontexttaxonomie. Sie ändert weder
`next_action=review` noch `deep_read_only_allowed=false` und öffnet keinen
tiefen Werkzeugpfad.

EXP-0017 belegt die Isolation des gebundenen WI-0005-Pfads, ist aber keine
Freigabe zur Lockerung des Review-Gates. Private EXP-0015-Eingänge werden
nicht erneut gelesen oder ausgewertet. Ihr historisches, anonym aggregiertes
Ergebnis bleibt unverändert.

## Öffentlicher Aufrufvertrag

- Der vorhandene Aufruf ohne Versionsoption bleibt unverändert.
- Die menschliche Ausgabe bleibt bytegenau unverändert.
- `--json` erzeugt weiterhin bytegenau den jeweiligen V1-Bericht.
- V2 wird ausschließlich durch `--json --report-version v2` aktiviert.
- `--report-version` ohne `--json` wird mit dem vorhandenen pfadfreien
  Nutzungsfehler abgelehnt.
- Unbekannte Versionswerte werden abgelehnt; es gibt keinen impliziten
  Defaultwechsel.
- Der Vertrag gilt einheitlich für Einzel-, Batch- und kombinierten
  Triage-/Deep-Bericht. Ihre V2-Schemata lauten:
  `sammlungslotse/ebook-intake-report/v2`,
  `sammlungslotse/ebook-intake-batch-report/v2` und
  `sammlungslotse/ebook-intake-combined-report/v2`.

V1 bleibt in allen drei Projektionswegen Standard. Ein vorhandener Verbraucher
muss weder migrieren noch ein neues Feld tolerieren.

## Gebundener V2-Berichtsvertrag

V2 behält sämtliche V1-Felder und ergänzt ausschließlich innerhalb jedes
Triageberichts:

```json
{
  "review_context": {
    "assessment": "classified",
    "classes": ["content.user_activated_hyperlink"]
  }
}
```

`classes` ist eine alphabetisch sortierte, duplikatfreie Liste und enthält
ausschließlich Literale aus dieser EXP-0016-Taxonomie:

- `content.user_activated_hyperlink`;
- `package.optional_linked_resource`;
- `publication.automatic_remote_resource`;
- `content.active_or_submission`;
- `reference.local_or_other_scheme`;
- `ambiguous_or_deceptive`.

`assessment` besitzt genau drei Werte:

- `classified`: Der Triagebericht steht auf `review` und alle erklärten
  Kontexte konnten den bekannten Klassen zugeordnet werden.
- `ambiguous_or_unknown`: Der Triagebericht steht auf `review`, aber
  mindestens ein Kontext ist mehrdeutig, unbekannt, nicht sicher lesbar oder
  nicht vollständig klassifizierbar. `classes` enthält dann zwingend
  `ambiguous_or_deceptive`; sicher erkannte weitere Klassen dürfen daneben
  erhalten bleiben.
- `not_applicable`: Die bestehende Folgeaktion ist nicht `review`; `classes`
  ist leer. V2 erhebt dann keine neue Kontextbehauptung.

Die Erklärung enthält keine Anzahl, Reihenfolge, Entry-Bezeichnung, Datei-
oder Archivpfade, URL, Hostnamen, Schemaziele, Snippets, Inhalte, Metadaten
oder private Werte. Sie erlaubt keine Rückrechnung auf eine konkrete
Referenz.

## Unveränderte Entscheidungssemantik

Für denselben Eingang müssen V1 und V2 dieselben Werte für
`next_action`, `deep_read_only_allowed`, `format_capability`, `observations`,
`findings`, `snapshot`, `limits` und `effects` liefern. Insbesondere bleibt
jede bereits erkannte Remote-Referenz oder aktive Oberfläche auf `review`;
WI-0014 führt keine Ausnahme für Navigation ein.

Die neue Klassifikation darf die vorhandene WI-0004-Erkennung weder ersetzen
noch deren Ergebnis steuern. Wenn Klassifikation und bestehende Erkennung
nicht sicher zusammengeführt werden können, bleibt die vorhandene
Entscheidung unverändert und V2 fällt auf `ambiguous_or_unknown` zurück.

## Implementierungsgrenze

Die Implementierung darf nur den bestehenden lokalen, begrenzten und
read-only EPUB-Eingangsweg um eine interne Kontextprojektion und explizite
V2-Renderer erweitern. Python 3.12 und die Standardbibliothek bleiben die
Laufzeitwahl. Die Klassifikation darf nur bereits innerhalb der bestehenden
Markup-Grenzen gelesene Bytes verwenden und weder zusätzliche Archiveinträge
öffnen noch extrahieren.

Außerhalb bleiben:

- Änderung oder Lockerung des WI-0004-Review-Gates;
- Start des WI-0005-Providers aus einem Reviewfall;
- reale oder private Medien und erneute private Analyse;
- Netzwerk, Browser, REST, Agents oder externe Metadatenprovider;
- Persistenz, Cache, Datenbank oder neue Writerfläche;
- Änderung von Original, Sammlung, Calibre oder anderem Fachsystem;
- URL-, Zielvertrauens-, Erreichbarkeits- oder Lesesystemsicherheitsaussagen;
- Änderung eingefrorener EXP-0015-, EXP-0016- oder EXP-0017-Ergebnisse.

## Synthetischer Produktqualifikationsvertrag

Die Implementierungswave beginnt erst nach Merge und Post-Merge-Prüfung
dieses Vertrags in einem neuen sauberen Worktree. Ihr commitgebundener
Produktnachweis muss mindestens belegen:

1. Die menschliche Ausgabe und sämtliche Standard-/V1-JSON-Projektionen sind
   gegen den gebundenen Ausgangsstand bytegleich.
2. Die 48 EXP-0016-Orakelfälle werden zweimal durch den Produktklassifikator
   verarbeitet; alle sechs Klassen stimmen ohne Context False Negative oder
   Mismatch überein.
3. Die zwölf EXP-0017-Fälle werden als deterministische, begrenzte EPUBs
   materialisiert und je zweimal über den tatsächlichen öffentlichen
   Einzeldatei-CLI-Weg in V1 und V2 geprüft.
4. Jeder dieser bestehenden Reviewfälle bleibt in V1 und V2 auf
   `next_action=review` und `deep_read_only_allowed=false`; kein Deep-Provider
   wird gestartet.
5. Einzel-, Batch- und kombinierte V2-Projektion verwenden ausschließlich
   ihr gebundenes V2-Schema und dieselbe Triage-Kontextstruktur.
6. Mehrdeutige, unbekannte, nicht lesbare und nicht anwendbare Kontrollen
   belegen den exakten Rückfallvertrag ohne implizite Freigabe.
7. Berichte bleiben begrenzt, deterministisch und pfadfrei; Eingänge bleiben
   bytegleich und Taskmaterial wird vollständig entfernt.
8. Netzwerk, Persistenz, Writer, private Daten, Fachsystem- und
   Sammlungswirkung fehlen.
9. Die historischen EXP-0015-, EXP-0016- und EXP-0017-Validatoren sowie
   Repository-, Registry-, Dokumentations-, Datenschutz- und Foundation-
   Prüfungen bleiben erfolgreich.

Parserorakel, tatsächliche CLI-Projektion und Repositoryregression sind drei
getrennte Nachweise. Ein grüner Teilnachweis ersetzt keinen der beiden
anderen. Unveränderte Vollprüfungen werden erst auf dem stabilen Kandidaten
und nicht nach jeder Zwischenänderung wiederholt.

## Implementierung und Ergebnis

Der additive V2-Kandidat ist umgesetzt. Das interne Modell trägt eine
validierte, sortierte Kontextprojektion; `context.py` reproduziert die sechs
EXP-0016-Klassen mit Standardbibliotheksparsern. Die bestehende flache
WI-0004-Erkennung bleibt alleinige Autorität für `next_action` und das
Deep-Read-Gate. Einzel-, Batch- und kombinierter JSON-Weg aktivieren V2 nur
über `--json --report-version v2`; alle Default- und Humanpfade bleiben V1.

`runtime/ebook-intake-context/profile.json` und
`tools/qualify_ebook_intake_context.py` binden den Ausgangscommit, beide
synthetischen Fallmatrizen, die vollständige Intake-Laufzeit und die drei
öffentlichen Projektionsflächen. Der tatsächliche Hauptlauf blieb bis zum
sauberen, vollständig getesteten und in beiden Pflichtchecks grünen Preimage
`ed7f173896b7365d2f91fb47baa1bc4065c23bcb` gesperrt und wurde danach genau
einmal ausgeführt.

Auf dem stabilen lokalen Kandidaten bestanden 76 fokussierte Produkt- und
Boundary-Prüfungen, der historische EXP-0014-Nachweis und 255/255 durch den
Repositoryadapter ausgeführte Tests. Die wegen der erweiterten Intake-
Laufzeit erforderliche WI-0005-Requalifizierung bestand unabhängig 12/12
Kriterien. Der ebenfalls vom erweiterten Intake-Modell abhängige WI-0011-
Produktweg wurde tatsächlich mit Podman erneut qualifiziert und bestand
23/23 Kriterien. Projekt-, Registry-, Kompilierungs-, Diff- und Foundation-
Prüfungen waren ebenfalls grün.

Der Hauptlauf bestand 16/16 Kriterien. Die 48 EXP-0016-Fälle liefen zweimal
ohne Mismatch; alle zwölf öffentlichen CLI-Fälle behielten V1 bytegleich und
V2 deterministisch. Elf bestehende Reviewfälle blieben geschlossen, der
bewusste Nicht-Review-Kontrollfall erhielt `not_applicable`, Batch und
kombinierter Bericht verwendeten die gebundenen V2-Schemata, kein
Deep-Provider startete und alle Eingänge sowie das Cleanup blieben
unverändert. Der pfadfreie Nachweis unter
`runtime/ebook-intake-context/qualification.json` besitzt SHA-256
`16b33a98904157593de335ce0aa8a8348f3c1d9a795fdbe34765251a5dbc3046`.
WI-0014 ist damit `done`.

## Ergebnisfolge

Die bestandene Implementierung und Produktqualifikation hat GATE-0021 als
getrenntes Ergebnisgate geöffnet. Der Nutzer hat anschließend ausdrücklich
Option A gewählt: V2 bleibt in seinem bestehenden engen Umfang als explizites
JSON-Opt-in stabil. Die Auswahl registriert keine Folgearbeit und leitet keine
weitere Produktänderung ab.

## Nicht-Ziele

- keine automatische Reviewreduktion;
- keine Navigationsausnahme;
- keine Sicherheitsbewertung eines Links oder Ziels;
- keine allgemeine HTML-, XML-, CSS-, URL- oder EPUB-Parserbibliothek;
- keine erneute Aussage über einzelne private Bücher;
- keine UI-, Routing-, Such-, Persistenz- oder Writerentscheidung.
