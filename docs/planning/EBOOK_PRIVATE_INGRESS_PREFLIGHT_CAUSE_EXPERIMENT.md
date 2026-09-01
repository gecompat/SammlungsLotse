# EXP-0014: Private Ingress-Preflight-Ursachen produktcodefrei qualifizieren

Status: DONE — EXECUTED, METHOD PASSED; RESULT REVIEW 3/3

Stand: 2026-09-01

Artifact: EXP-0014

## Auswahl und Zweck

Der Nutzer hat in GATE-0016 am 2026-09-01 ausdrücklich Option A ausgewählt.
EXP-0014 qualifiziert ausschließlich, welche bereits öffentlichen
WI-0004-Folgeaktionen, Beobachtungs- und Befundcodes die drei in EXP-0013
belegten geschlossenen Ingress-Vorprüfungen erklären.

Die Auswahl autorisierte diesen Experimentvertrag und seine getrennte
Ausführung nach Merge und Post-Merge-Prüfung. Sie autorisierte keine
Produktkorrektur, keine neue Diagnoseoberfläche und keinen Produktcode. Das
Ergebnis öffnet ein neues getrenntes Ergebnisgate.

## Gebundene Ausgangslage

- EXP-0013 bestand 16/16 Methodenkriterien. Alle drei privaten WI-0011-Läufe
  endeten vor dem Record-Handoff mit
  `ingress.preflight_gate_not_open`.
- Der historische EXP-0013-Nachweis bewahrt nur ein pfadfreies Aggregat. Er
  enthält keine private Einzelzuordnung und keinen konkreten Intake-Grund.
- WI-0011 verwendet für seine Ingress-Entscheidung unverändert den
  WI-0004-Eingangstriagevertrag.
- Der öffentliche WI-0004-JSON-Vertrag enthält `next_action`,
  `observations` und `findings`. Seine Evidenzwerte können Hashes, Größen und
  andere Einzelwerte enthalten; EXP-0014 darf ausschließlich die öffentlichen
  Code-Schlüssel und die Folgeaktion übernehmen.
- Die möglichen öffentlichen Folgeaktionen bleiben
  `continue_deep_read_only`, `defer`, `stop`, `review` und `abstain`.

EXP-0013, sein Ergebnis und sein historischer Validator werden nicht
verändert.

## Private Eingangsgrenze

Der auswertbare Hauptlauf akzeptiert genau drei wiederholte
`--private-epub`-Argumente und die ausdrückliche Bestätigung, dass es dieselben
drei Eingänge wie in EXP-0013 sind.

Für jeden Eingang gilt:

- reguläre vorhandene Datei mit Endung `.epub`;
- kein Symlink, Reparse Point oder anderer indirekter Locator;
- größer als null und höchstens 4 MiB;
- alle drei Dateien zusammen höchstens 12 MiB;
- ausschließlich read-only geöffnet;
- keine Verzeichnis-, Glob-, Index- oder rekursive Suche.

Weniger oder mehr als drei Eingänge, doppelte Locators, ein Verzeichnis oder
eine verletzte Dateigrenze brechen vor jeder Auswertung fail-closed ab.
Fehlermeldungen geben keinen Locator aus. SHA-256-Werte dienen nur im
Prozessspeicher der Quellunverändertheitsprüfung und erscheinen weder in
stdout oder stderr noch in Ergebnis- oder Repositoryevidenz.

## Diagnoseablauf

Nach bestandener Eingangskontrolle gilt genau diese Reihenfolge:

1. Jede Datei wird unter einem positionsgebundenen neutralen Namen in einen
   neuen task-privaten Tempbereich kopiert und bytegleich geprüft.
2. Jede task-private Kopie durchläuft genau einmal den unveränderten Befehl
   `python tools/run_ebook_intake.py --json <KOPIE>`.
3. stdout und stderr werden ausschließlich begrenzt im Prozessspeicher
   gehalten. Der vollständige JSON-Bericht wird gegen den gebundenen
   WI-0004-Vertrag geprüft und nicht gespeichert oder ausgegeben.
4. Vor jeder Aggregation werden ausschließlich `next_action` sowie die
   `code`-Schlüssel aus `observations` und `findings` übernommen. Sämtliche
   `values`, der `snapshot`, Hashes, Größen und übrigen Felder werden
   verworfen.
5. Erst nach drei vollständigen Läufen sowie nachgeprüfter Quelle und
   vollständigem Cleanup wird eine gemeinsame Aggregation erzeugt.

Der tiefe read-only Werkzeugweg wird nicht gestartet. EXP-0014 bewertet
weder EPUB-Standardsgültigkeit noch bibliografische Identität oder
Produktqualität.

## Aggregationsvertrag

Die einzige zulässige private Ausgabe besitzt genau diese gruppenbezogenen
Felder:

- Schema und Experimentreferenz;
- feste Eingangsanzahl `3` und feste Anzahl von drei Intake-Läufen;
- `next_action_counts` für alle fünf öffentlichen Folgeaktionen;
- alphabetisch sortierte `observation_code_counts`;
- alphabetisch sortierte `finding_code_counts`;
- Zählwerte für nicht vorab gebundene Beobachtungs- und Befundcodes;
- boolesche Nachweise für Quellunverändertheit, Pfadfreiheit und Cleanup;
- Gesamtstatus `pass` oder `inconclusive`.

Es gibt keine Einzelausgabe und keine stabile Eingangskennung. Insbesondere
fehlen Position, Dateiname, Titel, Autor, Identifier, Sprache, Format,
Locator, Pfad, Hash, Größe, Evidenzwert, Rohbericht und Zeitstempel.

Das Ausführungspreimage bindet die zu diesem Produktstand öffentlichen
Beobachtungs- und Befundcodes als Allowlist. Ein neuer oder nicht
vorab gebundener Code wird nicht als Literal ausgegeben, erhöht nur den
jeweiligen `unclassified`-Zählwert und setzt den Gesamtstatus auf
`inconclusive`. Eine Teilaggregation wird bei Abbruch oder unvollständigem
Cleanup nicht ausgegeben.

## Synthetische Kontrollen

Vor dem privaten Lauf bindet das Ausführungspreimage ausschließlich
synthetische Kontrollen:

1. tatsächliche WI-0004-JSON-CLI-Läufe über TEST-0001-Material für die
   vorhandenen Folgeaktionen `continue_deep_read_only`, `review`, `stop` und
   `abstain`;
2. eine vorab gebundene Projektionsmatrix einschließlich `defer`, mehrfacher
   Beobachtungs- und Befundcodes sowie leerer Befundmenge;
3. den nachweislichen Ausschluss aller Evidenzwerte, Snapshot-Felder, Hashes,
   Größen und privaten Felder aus der Aggregation;
4. Negativkontrollen für zwei oder vier Eingänge, doppelte Eingänge,
   Verzeichnisse, Links, Größenüberschreitung, Teilabbruch, ungültiges JSON,
   unbekannte Codes, private Ausgabefelder und unvollständiges Cleanup;
5. zwei semantisch identische Aggregationswiederholungen.

Die synthetischen Kontrollen belegen Methode und Datenschutzgrenzen. Sie
ersetzen den ausdrücklich ausgewählten privaten Diagnoselauf nicht.

## Harte Grenzen

- genau drei erneut explizit bestätigte private EPUBs im Hauptlauf;
- genau ein unveränderter WI-0004-JSON-Lauf je Eingang;
- keine tiefe Werkzeugausführung und keine Calibre-Materialisierung;
- kein Netzwerk, keine Persistenz und keine direkte Datenbanknutzung;
- keine Aufbewahrung privater Arbeitskopien oder vollständiger JSON-Berichte;
- keine privaten Einzelwerte, Metadaten, Locators, Pfade, Hashes, Größen oder
  Rohoutputs;
- keine Änderung unter `src/sammlungslotse/`;
- keine neue öffentliche CLI-, API-, UI-, Agent-, Diagnose-, Such-, Routing-
  oder Writerfläche;
- keine Bestandsänderung im führenden Fachsystem.

## Methodische Akzeptanzkriterien

EXP-0014 ist methodisch nur bestanden, wenn alle folgenden 16 Kriterien
erfüllt sind:

1. Git-Preimage, EXP-0013, WI-0004, WI-0011 und TEST-0001 sind gebunden;
2. der Hauptlauf akzeptiert ausschließlich genau drei explizite
   `--private-epub`-Argumente und keine Verzeichnisse;
3. alle drei Eingänge wurden vom Nutzer als derselbe EXP-0013-Eingangssatz
   bestätigt;
4. Dateityp, Link-, Reparse-, Einzel- und Summengrenzen werden vor dem Kopieren
   geprüft;
5. ausschließlich positionsgebundene task-private Kopien werden verarbeitet;
6. jede Kopie durchläuft genau einmal den unveränderten WI-0004-JSON-CLI-Weg;
7. tiefer Werkzeugweg, Calibre, Netzwerk und Datenbankzugriff bleiben aus;
8. der vollständige WI-0004-Bericht bleibt nur begrenzt im Prozessspeicher;
9. ausschließlich Folgeaktion sowie Beobachtungs- und Befundcode-Schlüssel
   gelangen in die Aggregation;
10. Evidenzwerte, Snapshot, Hashes, Größen und private Felder fehlen;
11. unbekannte Codes bleiben als reine `unclassified`-Zählwerte sichtbar und
    führen zu `inconclusive`;
12. die synthetischen CLI-, Projektions- und Negativkontrollen bestehen;
13. beide Aggregationswiederholungen sind semantisch identisch;
14. alle drei Quellen bleiben bytegleich unverändert;
15. Produktcode, Persistenz und Bestandswirkungen fehlen;
16. Taskmaterial und Prozessreste sind vollständig bereinigt.

Ein methodischer `pass` ist keine Produktfreigabe. Die beobachteten
Gruppenhäufigkeiten beschreiben nur diesen ausdrücklich begrenzten
Eingangssatz.

## Ausführungsergebnis

Das saubere Ausführungspreimage ist Commit
`e82d01e6d669e85646dafd6ab3d569fc38e0d71b`. Die vier tatsächlichen
synthetischen WI-0004-Läufe, alle elf Negativkontrollen und beide
Aggregationswiederholungen bestanden.

Der Nutzer bestätigte am 2026-09-01 erneut denselben Satz aus genau drei
privaten EPUBs wie in EXP-0013. Der Hauptlauf führte für jede neutrale
task-private Kopie genau einen unveränderten WI-0004-JSON-Lauf aus. Das
pfadfreie Aggregat lautet:

- `next_action_counts.review=3`; alle anderen Folgeaktionen stehen auf null;
- `finding_code_counts.format.epub=3`;
- `finding_code_counts.security.remote_resource=3`;
- `observation_code_counts.epub.remote_reference.present=3`;
- unbekannte Beobachtungs- und Befundcodes jeweils null;
- Quellen unverändert, Pfadfreiheit belegt und Cleanup vollständig;
- Gesamtstatus `pass`.

Das 907-Byte-Ergebnis besitzt den SHA-256-Wert
`0eab4893eb85d05c07622bfe70721a58f03e8285e199738b1513237dc3207411`.
Es enthält keine privaten Referenzwerte, URLs, Domains, Metadaten,
Einzelzuordnungen, Locators, Pfade, Hashwerte, Größen oder Rohberichte.

Der Befund erklärt den dreifachen Ingress-Preflight-Nichtabschluss innerhalb
des bestehenden WI-0004-Vertrags: Remote-Ressourcen führen fail-safe zu
`review`. Er belegt weder Schadcode, EPUB-Standardsgültigkeit,
bibliografische Identität noch einen Produktfehler. GATE-0017 bewertet jede
mögliche Fortsetzung getrennt.

## Ausführungsfolge

1. Die Auswahl- und Vertragswave wurde validiert, gemergt und auf
   `origin/main` post-merge geprüft.
2. Profil, Runner, synthetische Kontrollen und Tests wurden in einem neuen
   isolierten Worktree ohne Produktcode implementiert und als Preimage
   `e82d01e` committed.
3. Gegen dieses Commit wurden dieselben drei privaten Locators erneut
   bestätigt und genau einmal je task-privater Kopie verarbeitet.
4. Der historische Validator bindet ausschließlich die zulässige
   Aggregation an das Preimage. Private Arbeits- oder Rohdaten bleiben
   außerhalb von Git.
5. GATE-0017 ist als getrennte Ergebnisentscheidung offen; EXP-0014 wählt
   keine Produktfortsetzung.

## Nicht-Ziele

- keine Reparatur von WI-0004 oder WI-0011;
- keine Aussage über EPUB-Standardsgültigkeit, Inhalt, Qualität oder
  bibliografische Identität der drei privaten EPUBs;
- keine Erweiterung auf weitere Dateien, Bibliotheken oder Verzeichnisse;
- keine dauerhafte private Diagnosedatenbank;
- keine Produkt-, Architektur-, Provider-, UI- oder Writerentscheidung.
