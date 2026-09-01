# EXP-0015: Private Remote-Referenzkontexte produktcodefrei und pfadfrei gruppieren

Status: ACCEPTED — NOT EXECUTED

Stand: 2026-09-01

Artifact: EXP-0015

## Auswahl und Zweck

Der Nutzer hat in GATE-0017 am 2026-09-01 ausdrücklich Option A ausgewählt
und damit denselben Dreiersatz privater EPUBs wie in EXP-0014 erneut
bestätigt. EXP-0015 prüft ausschließlich, ob mindestens zwei dieser drei
Eingänge dieselbe vorab gebundene grobe Kontextklasse für eine HTTP(S)-
Remote-Referenz besitzen.

Die Auswahl autorisiert diesen Experimentvertrag und seine getrennte
Ausführung nach Merge, Post-Merge-Prüfung und sauberem Commit-Preimage. Sie
autorisiert keine Produktkorrektur, keine neue Diagnoseoberfläche, keine
Lockerung des WI-0004-Review-Gates und keinen Produktcode. Das Ergebnis
öffnet ein neues getrenntes Ergebnisgate.

## Gebundene Ausgangslage

- EXP-0014 ist `done`; sein historischer Nachweis bindet für alle drei
  Eingänge `review`, `epub.remote_reference.present` und
  `security.remote_resource`.
- EXP-0014 speicherte weder Referenzwerte noch Einzelzuordnungen und traf
  keine Aussage über den groben Kontext einer Remote-Referenz.
- Der bestehende WI-0004-Vertrag bleibt unverändert und leitet jede erkannte
  Remote-Referenz weiterhin fail-safe auf `review`.
- TEST-0001 0.3.0 bleibt das synthetische Referenzkorpus. EXP-0015 erweitert
  dieses Korpus nicht und verwendet für seine Kontextmatrix ausschließlich
  task-private synthetische EPUBs.

EXP-0014, sein Ergebnis, der historische Validator und Produktcode werden
nicht verändert.

## Private Eingangsgrenze

Der Hauptlauf akzeptiert genau drei wiederholte `--private-epub`-Argumente
und die maschinenlesbare Bestätigung, dass es derselbe in GATE-0017 erneut
bestätigte EXP-0014-Eingangssatz ist.

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
Prozessspeicher der Bytegleichheits- und Quellunverändertheitsprüfung. Sie
erscheinen weder in stdout oder stderr noch in Ergebnis- oder
Repositoryevidenz.

## Ausführungs- und Parsergrenze

Nach bestandener Eingangskontrolle gilt genau diese Reihenfolge:

1. Jede Datei wird unter einem positionsgebundenen neutralen Namen in einen
   neuen task-privaten Tempbereich kopiert und bytegleich geprüft.
2. Ein ausschließlich unter `tools/experiments/` liegender, mit dem Preimage
   gebundener Python-3.12-Standardbibliotheksparser liest jede Kopie genau
   einmal. Er importiert keinen Code unter `src/sammlungslotse/`.
3. Der Parser extrahiert keine ZIP-Einträge auf das Dateisystem. Er erzwingt
   vor dem Lesen Grenzen für Dateigröße, Eintragsanzahl, deklarierte
   Gesamtgröße, Einzelentry, relative Namen, Kompressionsverhältnis und
   insgesamt gelesene Markupbytes.
4. Gelesen werden nur vorab erlaubte Paket-, XHTML-/HTML-, SVG-, NCX- und
   CSS-Einträge. Binäre Nutzdaten bleiben ungelesen.
5. HTTP(S)-Werte werden ausschließlich im lokalen Parserzustand erkannt und
   sofort auf eine vorab gebundene Kontextklasse reduziert. Der Wert selbst,
   sein Domain-, Pfad- oder Fragmentanteil und der ZIP-Eintragsname gelangen
   nicht in die Projektion.
6. Pro Eingang und Kontextklasse bleibt nur ein boolescher Präsenzwert im
   Prozessspeicher. Vorkommenszahlen und Einzelzuordnungen werden nicht
   aggregiert.
7. Erst nach drei vollständigen Läufen, nachgeprüften Quellen und
   vollständigem Cleanup wird genau ein gemeinsames Aggregat geschrieben.

Es gibt keinen Netzwerkclient, keinen Subprozess, keine direkte
Datenbanknutzung, keinen tiefen Werkzeuglauf und keine Bestandswirkung.

## Vorab gebundene Kontexttaxonomie

Das Ausführungspreimage bindet genau diese groben öffentlichen Klassen:

- `package.metadata_or_link`: OPF-/Package-Metadaten, Manifest- oder
  Linkattribute;
- `content.navigation`: Navigation oder Hyperlink in einem Inhaltsdokument;
- `content.embedded_resource`: eingebettete Bild-, Audio-, Video-, Objekt-
  oder vergleichbare Ressourcenattribute;
- `stylesheet.resource`: CSS-`url(...)`, `@import`, Stylesheet-Link oder
  Inline-Style;
- `svg.resource`: SVG-Ressourcen- oder Linkattribute;
- `markup.other_attribute`: anderes Markupattribut mit Remote-Referenz;
- `text_or_script.literal`: Remote-Literal außerhalb der vorigen
  Attribut- und Styleklassen.

Die Taxonomie ist eine Experimentprojektion und keine Produktregel. Eine
Referenz kann innerhalb eines Eingangs mehrere Klassen belegen. Parserfehler,
überschrittene Grenzen oder nicht sicher klassifizierbare Funde führen
fail-closed beziehungsweise zu `inconclusive`; sie werden nicht durch
Raten einer Klasse verborgen.

## Mindestgruppen- und Aggregationsvertrag

Die Mindestgruppe beträgt exakt `2` von `3` Eingängen. Die einzige zulässige
private Ausgabe besitzt genau diese gruppenbezogenen Felder:

- Schema und Experimentreferenz;
- feste Eingangsanzahl `3` und feste Parserlaufanzahl `3`;
- feste Mindestgruppe `2`;
- `remote_reference_input_count` ohne Einzelzuordnung;
- alphabetisch sortierte `context_input_counts`, jedoch ausschließlich für
  Kontextklassen, die in mindestens zwei Eingängen präsent sind;
- `suppressed_context_present` als reines Boolean, falls mindestens eine
  bekannte Kontextklasse nur einen Eingang erreicht; weder Klassenliteral
  noch Anzahl werden dafür ausgegeben;
- `unclassified_input_count` ohne Rohwert oder Einzelzuordnung;
- `qualification` mit `shared_context_present`, `no_shared_context` oder
  `inconclusive`;
- boolesche Nachweise für Quellunverändertheit, Pfadfreiheit und Cleanup;
- methodischer Gesamtstatus `pass` oder `inconclusive`.

Es gibt keine Einzelausgabe, stabile Eingangskennung oder
Vorkommenshäufigkeit. Insbesondere fehlen Position, Dateiname, Titel, Autor,
Identifier, Sprache, Locator, Pfad, ZIP-Eintragsname, Referenzwert, URL,
Domain, Fragment, Inhalt, Metadatenwert, Hash, Größe, Rohbericht und
Zeitstempel.

Eine nicht vorab gebundene Kontextklasse wird nie als Literal ausgegeben.
Ein unklassifizierter Fund erhöht nur den gemeinsamen
`unclassified_input_count`, setzt `qualification` und Status auf
`inconclusive` und verhindert jede Produktableitung. Eine Teilaggregation
wird bei Abbruch oder unvollständigem Cleanup nicht geschrieben.

## Synthetische Kontrollen

Vor dem privaten Lauf bindet das Ausführungspreimage ausschließlich
task-private synthetische Kontrollen:

1. jede der sieben Kontextklassen auf mindestens zwei von drei synthetischen
   EPUBs;
2. mehrere Klassen in einem Eingang ohne Vorkommenszählung;
3. eine nur einmal vertretene bekannte Klasse, deren Literal vollständig
   unterdrückt bleibt;
4. einen nicht sicher klassifizierbaren Fund, der ausschließlich
   `unclassified_input_count` und `inconclusive` erzeugt;
5. lokale, fragmentgebundene, `data:`- und andere Nicht-HTTP(S)-Referenzen,
   die keine Remote-Klasse erzeugen;
6. Groß-/Kleinschreibung, XML-Escapes, einfache und doppelte Attribute sowie
   CSS-`url(...)` und `@import`;
7. beschädigte Archive, Pfadtraversal, Links, verschlüsselte Einträge,
   Duplikate und alle Größen-, Entry-, Ratio- und Lesebudgets;
8. zwei oder vier Eingänge, doppelte Eingänge, Verzeichnisse, Teilabbruch,
   Quelländerung, private Ausgabefelder und unvollständiges Cleanup;
9. zwei semantisch identische Wiederholungen des vollständigen synthetischen
   Aggregats.

Die synthetischen Kontrollen belegen Methode, Grenzen und
Datenschutzprojektion. Sie ersetzen den ausdrücklich ausgewählten privaten
Hauptlauf nicht.

## Harte Grenzen

- genau drei in GATE-0017 erneut bestätigte private EPUBs im Hauptlauf;
- genau ein gebundener lokaler Parserlauf je task-privater Kopie;
- Mindestgruppe `2`; seltene Klassen bleiben ohne Literal unterdrückt;
- keine Vorkommenszahlen und keine Einzelzuordnung;
- kein Produktimport und keine Änderung unter `src/sammlungslotse/`;
- kein Netzwerk, Subprozess, tiefer Werkzeuglauf, Calibre, Persistenz oder
  direkte Datenbanknutzung;
- keine Aufbewahrung privater Arbeitskopien, Referenzen, Metadaten,
  ZIP-Eintragsnamen, Locators, Pfade, Hashes, Größen oder Rohoutputs;
- keine neue öffentliche CLI-, API-, UI-, Agent-, Diagnose-, Such-, Routing-
  oder Writerfläche;
- keine Bestandsänderung im führenden Fachsystem.

## Methodische Akzeptanzkriterien

EXP-0015 ist methodisch nur bestanden, wenn alle folgenden 18 Kriterien
erfüllt sind:

1. Git-Preimage, EXP-0014, GATE-0017, WI-0004, WI-0011 und TEST-0001 sind
   gebunden;
2. der Hauptlauf akzeptiert ausschließlich genau drei direkte reguläre
   EPUB-Locators und keine Verzeichnisse;
3. GATE-0017 bindet die Nutzerbestätigung desselben EXP-0014-Eingangssatzes;
4. Dateityp, Link-, Reparse-, Einzel- und Summengrenzen werden vor dem Kopieren
   geprüft;
5. ausschließlich positionsgebundene task-private Kopien werden verarbeitet;
6. jede Kopie durchläuft genau einmal den gebundenen lokalen Parser;
7. Archiveinträge werden nicht extrahiert und alle ZIP-/Lesebudgets gelten
   fail-closed;
8. ausschließlich erlaubte Markup- und Styleeinträge werden gelesen;
9. alle HTTP(S)-Werte werden vor der Projektion verworfen;
10. die sieben Kontextklassen sind vollständig vorab gebunden;
11. pro Eingang und Klasse bleibt ausschließlich ein boolescher Präsenzwert;
12. sichtbare Klassen erfüllen Mindestgruppe `2`;
13. seltene bekannte Klassen bleiben ohne Literal vollständig unterdrückt;
14. unklassifizierte Funde bleiben literal- und pfadfrei sichtbar und führen
    zu `inconclusive`;
15. alle synthetischen Positiv-, Negativ-, Grenz- und
    Datenschutzkontrollen bestehen;
16. beide synthetischen Wiederholungen sind semantisch identisch;
17. alle drei Quellen bleiben bytegleich unverändert;
18. Produktcode und Bestandswirkungen fehlen; Taskmaterial ist vollständig
    bereinigt.

Ein methodischer `pass` oder eine gemeinsame Kontextklasse ist keine
Produktfreigabe. Der Befund beschreibt nur diesen ausdrücklich begrenzten
Dreiersatz und öffnet ein getrenntes Ergebnisgate.

## Ausführungsfolge

1. Diese Auswahl- und Vertragswave wird validiert, gemergt und auf
   `origin/main` post-merge geprüft.
2. Profil, Runner, synthetische Kontrollen und Tests werden danach in einem
   neuen isolierten Worktree ohne Produktcode implementiert und als sauberes
   Preimage committed.
3. Erst gegen dieses Preimage werden die drei bereits mit Option A erneut
   bestätigten Locators genau einmal je task-privater Kopie verarbeitet.
4. Ein historischer Validator bindet ausschließlich die zulässige
   Mindestgruppenaggregation an das Preimage. Private Arbeits- oder Rohdaten
   bleiben außerhalb von Git.
5. Das Ergebnis öffnet ein neues getrenntes Gate; EXP-0015 wählt keine
   Produktfortsetzung.

## Nicht-Ziele

- keine Reparatur oder Lockerung von WI-0004 oder WI-0011;
- keine Aussage über Gefährlichkeit, Erreichbarkeit, Ausführung oder
  Vertrauenswürdigkeit einer Remote-Referenz;
- keine Aussage über EPUB-Standardsgültigkeit, Inhalt, Qualität oder
  bibliografische Identität der drei privaten EPUBs;
- keine Erweiterung auf weitere Dateien, Bibliotheken oder Verzeichnisse;
- keine dauerhafte private Diagnosedatenbank;
- keine Produkt-, Architektur-, Provider-, UI- oder Writerentscheidung.
