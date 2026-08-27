# E-Book-Nutzerszenarien und Messverträge

Status: BRAINSTORMING — ANALYSEVERTRAG, KEINE PRODUKTENTSCHEIDUNG

Stand: 2026-08-27

Artifacts: WI-0003, REQ-0002

## Zweck und Grenze

Dieses Dokument konkretisiert die Nutzerentscheidungen und Messgrößen der
E-Book-Erkundung. Es beschreibt, woran spätere Verfahren gemessen werden,
bevor Runtime, Persistenz, Oberfläche, Suchtechnik, Calibre-Adapter oder
Writer ausgewählt werden.

Die sechs Szenarien sind vergleichbare Testfragen und noch kein ausgewählter
Vertikalablauf. Sie autorisieren weder Produktcode noch Zugriff auf reale
Sammlungsdaten oder eine schreibende Operation. GATE-0001 bleibt offen.

Der geplante synthetische Testbestand steht in
[EBOOK_REFERENCE_CORPUS.md](EBOOK_REFERENCE_CORPUS.md). Die dazugehörigen
wegwerfbaren Spikes stehen in [EBOOK_EXPERIMENTS.md](EBOOK_EXPERIMENTS.md).

## Gemeinsamer Entscheidungsvertrag

Jedes Szenario wird unabhängig von einem späteren Zugangskanal durch folgende
Bestandteile beschrieben:

1. Nutzerfrage und auslösendes Problem;
2. Eingang und vorausgesetzter Snapshot;
3. beobachtete Rohwerte und weitere Evidenz;
4. erlaubte Ergebnisse einschließlich Enthaltung;
5. maximale Wirkungsstufe;
6. verbotene Wirkungen;
7. asymmetrische Folgen möglicher Fehler;
8. messbare Akzeptanzkriterien;
9. Abbruch-, Wiederaufnahme- und Veraltungsverhalten;
10. ausdrücklich nicht abgedeckter Umfang.

REQ-0002 ist als Anforderung vorgeschlagen: Ein Kandidat oder Vorschlag muss
Evidenz, Unsicherheit, erlaubte Ergebnisse, Fehlerfolgen und Wirkungsgrenze
ausweisen. Je näher ein Ergebnis an eine Bestandsänderung heranreicht, desto
höher sind die Anforderungen an Evidenz, erneute Zustandsprüfung und
Nutzerautorisierung.

## Ergebnisarten

Die folgenden Ergebnisarten sind fachlich verschieden:

- `observation`: ein Rohwert oder minimal strukturierter Werkzeugbefund;
- `finding`: eine aus Beobachtungen abgeleitete Feststellung;
- `candidate`: eine begründete mögliche Identität, Korrektur oder Zuordnung;
- `proposal`: ein prüfbarer Handlungsvorschlag ohne Ausführungsrecht;
- `abstain`: ausreichende Verarbeitung, aber zu wenig oder widersprüchliche
  Evidenz für einen Vorschlag;
- `unknown`: eine erforderliche Eigenschaft konnte nicht bestimmt werden;
- `not_applicable`: die Frage gilt für diesen Gegenstand nicht;
- `unsupported`: das aktive Fähigkeitsprofil unterstützt die notwendige
  Analyse nicht.

`abstain`, `unknown`, `not_applicable` und `unsupported` dürfen nicht als
Fehler oder leere Treffer zusammengefasst werden. Sie führen zu
unterschiedlichen Folgeentscheidungen und Messwerten.

## Szenario S1 — Vorhandenen Calibre-Bestand prüfen

### Nutzerfrage

Welche Bücher oder Repräsentationen einer ausgewählten Calibre-Bibliothek
benötigen Aufmerksamkeit, und warum?

### Eingang und Evidenz

- explizit ausgewählte synthetische Zielbibliothek;
- versionierter read-only Fachsystem-Snapshot;
- erlaubte bibliografische Felder, Formate und externe Locators;
- dateiseitige Beobachtungen nur, wenn der Zugriff getrennt erlaubt ist;
- Werkzeug-, Regel- und Profilversion je Befund.

### Erlaubte Ergebnisse

- vollständiger Snapshot im vereinbarten Feldumfang;
- technische, bibliografische oder bestandsbezogene Befunde;
- priorisierte Review-Kandidaten;
- `unknown`, `not_applicable`, `unsupported` oder begründete Enthaltung.

Maximale Wirkungsstufe ist 3: Kandidaten oder Bewertungen ableiten.

### Verbotene Wirkungen

- keine direkte Abfrage oder Änderung interner Calibre-Tabellen;
- keine Metadaten-, Cover-, Format-, Import- oder Löschoperation;
- keine absoluten privaten Pfade in Standardprojektionen;
- keine Gleichsetzung einer Calibre-ID mit Datei-, Ausgaben- oder
  Werkidentität.

### Fehlerfolgen und Messung

- Ein übersehener schwerer Integritätsbefund hat hohe Folgekosten.
- Ein falscher positiver Qualitätsbefund erzeugt Review-Aufwand, verändert
  aber keinen Bestand.
- Zu messen sind Snapshot-Abdeckung, Befund-Precision und -Recall,
  Erklärungsabdeckung, Laufzeit, Wiederholbarkeit, Pfadlecks und
  Schreibwirkungen.
- Erwartete Schreibwirkungen und Pfadlecks: jeweils null.

Nicht enthalten sind automatische Reparatur, Sortierung oder Bereinigung.

## Szenario S2 — Neuen Eingang triagieren

### Nutzerfrage

Kann eine neu eingegangene Datei sicher und sinnvoll weiter geprüft werden,
und welche nächsten Entscheidungen sind notwendig?

### Eingang und Evidenz

- stabiler synthetischer Eingangs-Snapshot;
- Dateisignatur, Größe, Hash und Containerstruktur;
- Schutz-, Aktivinhalt-, Ressourcen- und Formatmerkmale;
- formatbezogene Befunde und extrahierbare Rohmetadaten;
- bekannte Zielbestände als getrennte, read-only Snapshots.

### Erlaubte Ergebnisse

- Format- und Fähigkeitsklassifikation;
- Sicherheits- und Qualitätsbefunde;
- Dubletten-, Metadaten- und Routingkandidaten;
- weitere manuelle Prüfung, Enthaltung oder `unsupported`.

Maximale Wirkungsstufe ist 3. Eine Quarantäneentscheidung ist in dieser Wave
nur ein nicht ausführbarer Vorschlag.

### Verbotene Wirkungen

- kein Verschieben, Umbenennen, Entpacken am Original oder Importieren;
- kein Schutzumgehen;
- keine Netzwerkübertragung von Datei, Inhalt oder privatem Pfad;
- keine automatische Zielauswahl bei mehrdeutiger Evidenz.

### Fehlerfolgen und Messung

- Das Übersehen einer gefährlichen oder unvollständigen Datei hat hohe bis
  kritische Folgekosten.
- Ein vorsichtiger Review-Hinweis kostet Zeit, ist aber reversibel.
- Zu messen sind Erfassungs-Recall, korrekte Format- und Schutzklassifikation,
  Befund-Recall, Enthaltungsqualität, Ressourcenverbrauch und unveränderte
  Eingangsidentität.

Nicht enthalten sind Derivaterzeugung, Quarantäneausführung oder Import.

## Szenario S3 — Dublettenkandidaten entscheiden

### Nutzerfrage

Welche Beziehung besteht zwischen zwei oder mehreren Dateien oder
Medienobjekten?

### Eingang und Evidenz

- Bytehashes und Containermerkmale;
- strukturierte Inhalts- und Ressourcenfingerprints;
- Identifikatoren und bibliografische Rohwerte;
- positive und negative Merkmale für Repräsentation, Ausgabe und Werk;
- Herkunft und Zielbibliothek jedes Kandidaten.

### Erlaubte Ergebnisse

- byteidentisch;
- Kandidat für gleiche Repräsentation;
- Kandidat für gleiche Ausgabe in anderem Format;
- Kandidat für gleiches Werk, aber andere Ausgabe, Übersetzung oder
  Bearbeitung;
- verschieden;
- Enthaltung oder notwendiges manuelles Review.

Maximale Wirkungsstufe ist 3.

### Verbotene Wirkungen

- kein automatisches Zusammenführen von Identitäten;
- kein Format- oder Buchentfernen;
- keine Auswahl einer angeblich besten Datei als kanonisches Original;
- kein Überschreiben positiver oder negativer Evidenz durch einen Score.

### Fehlerfolgen und Messung

- Ein falsches positives Zusammenführen hätte in einer späteren
  Operationskette kritische Folgen. Kandidaten-Precision und Enthaltung haben
  deshalb Vorrang vor hoher automatischer Abdeckung.
- Ein übersehener Kandidat erzeugt hauptsächlich zusätzlichen Bestand und
  Review-Aufwand.
- Precision und Recall werden für jede Identitätsebene getrennt gemessen.
- Zusätzlich werden selektive Genauigkeit, Abdeckung, Erklärungsabdeckung und
  Korrekturzeit je Reviewentscheidung gemessen.

Nicht enthalten sind eine globale Werkautorität oder Löschregeln.

## Szenario S4 — Metadatenkonflikt auflösen

### Nutzerfrage

Welche bibliografische Aussage ist für welchen Gegenstand am besten belegt,
und welche Werte müssen unverändert sichtbar bleiben?

### Eingang und Evidenz

- eingebettete Datei- und Paketmetadaten;
- Calibre-Werte aus einem versionierten Snapshot;
- Dateiname oder Begleitdatei als getrennte Beobachtung;
- Nutzerbestätigung;
- später optional externe Providerantworten mit eigener Provenienz.

### Erlaubte Ergebnisse

- konfliktfreie Beobachtungsgruppe;
- Konflikt zwischen Quellen oder Gegenstandsebenen;
- Kandidat für Titel, Person, Rolle, Sprache, Identifikator, Reihe oder
  Ausgabemerkmal;
- bestätigter SammlungsLotse-Wert mit erhaltenen Ursprungswerten;
- Enthaltung.

Maximale Wirkungsstufe ist 3.

### Verbotene Wirkungen

- kein Überschreiben eingebetteter oder in Calibre gespeicherter Werte;
- keine Übernahme eines Providerwerts als alleinige Wahrheit;
- keine Verwendung einer ISBN als Werkidentität;
- kein Verlust von Rolle, Sprache, Quelle, Zeitpunkt oder Unsicherheit.

### Fehlerfolgen und Messung

- Eine falsche Person-, Rollen- oder Ausgabenzuordnung hat höhere Kosten als
  eine fehlende kosmetische Normalisierung.
- Zu messen sind Feldabdeckung, korrekt erkannte Konflikte, Vorschlags-
  Precision je Feld, Provenienzvollständigkeit, Enthaltungsquote und
  Nutzerkorrekturen.

Nicht enthalten sind Metadatenschreiben oder Providerwahl.

## Szenario S5 — E-Books suchen und auffällige Bestände finden

### Nutzerfrage

Findet der Nutzer bekannte Bücher, Textstellen, Themen oder Qualitätsprobleme
mit nachvollziehbaren Fundstellen?

### Eingang und Evidenz

- versionierter synthetischer Bestands-Snapshot;
- strukturierte Metadaten und Qualitätsbefunde;
- später optional extrahierter Volltext und regenerierbare Suchableitungen;
- eine festgelegte Menge konkreter Suchaufgaben mit erwarteten Treffern.

### Erlaubte Ergebnisse

- strukturierte Treffer und Facetten;
- Textfundstellen mit Repräsentationsbezug;
- Qualitäts- und Reviewansichten;
- leeres Ergebnis, `unsupported` oder begrenzte Antwort mit offengelegtem
  Suchumfang.

Maximale Wirkungsstufe ist 2: Befunde und Suchprojektionen erzeugen.

### Verbotene Wirkungen

- kein Suchindex als kanonische Wahrheit;
- keine Vermischung von Werk-, Ausgaben- und Dateitreffern;
- kein externer Versand von Volltext oder privaten Sammlungsmerkmalen;
- keine Behauptung semantischen Mehrwerts ohne Aufgabenvergleich.

### Fehlerfolgen und Messung

- Fehlende bekannte Treffer schaden dem Nutzwert stärker als zusätzliche klar
  erkennbare Kandidaten.
- Zu messen sind Recall auf Aufgabenebene, Precision der ersten Treffer,
  Fundstellenkorrektheit, Antwortzeit, Indexregenerierbarkeit und
  Nutzererfolg pro Aufgabe.

Nicht enthalten sind eine Suchtechnik- oder Embeddingentscheidung.

## Szenario S6 — Zielbibliothek vorschlagen

### Nutzerfrage

Welcher von mehreren getrennten Zielbeständen passt zu einem Eingang, oder
muss die Entscheidung offenbleiben?

### Eingang und Evidenz

- getrennte synthetische Zielbibliotheken und ihre versionierten Regeln;
- Klassifikation, Sprache, Metadaten- und Identitätsbefunde;
- erkannte Konflikte, Ausschlussregeln und Zielzustand;
- nachvollziehbare Regel- oder Modellversion.

### Erlaubte Ergebnisse

- genau ein begründeter Zielkandidat;
- mehrere Zielkandidaten mit Konflikt;
- kein geeignetes Ziel;
- Enthaltung und notwendige Nutzerentscheidung.

Maximale Wirkungsstufe ist 3.

### Verbotene Wirkungen

- kein Import, Verschieben oder Kopieren;
- keine Zielentscheidung allein aus einem Tag oder Modellscore;
- keine Übertragung einer Routingentscheidung auf spätere Fälle ohne
  versionierte Regel;
- keine stillschweigende Standardbibliothek bei fehlender Evidenz.

### Fehlerfolgen und Messung

- Ein falscher eindeutiger Zielvorschlag hat höhere Kosten als eine begründete
  Enthaltung.
- Zu messen sind selektive Genauigkeit, Abdeckung, korrekte Enthaltung,
  Regel- und Evidenzvollständigkeit, Nutzerkorrekturen und Entscheidungszeit.

Nicht enthalten sind die Definition produktiver Bibliothekspolitiken oder
eine Importfreigabe.

## Qualitäts- und Automatisierungsmatrix

Die Matrix bewertet nicht den späteren Produktwert. Sie zeigt, welche Art von
Evidenz und welche Voraussetzung eine Aktivität benötigt.

| Qualitätsbereich | Beispielaktivitäten | Prüfklasse | Früheste sinnvolle Evidenzstufe | Spätere Grenze |
|---|---|---|---|---|
| Eingang und Provenienz | Stabilität, Signatur, Hash, Herkunft | überwiegend deterministisch | TEST-0001 und lokaler Dateispike | produktive Quellen erst nach Gate |
| Integrität und Sicherheit | Archivfehler, Expansion, aktive oder geschützte Inhalte | deterministisch plus manuelles Risikoreview | TEST-0001 und EXP-0005 | keine Schutzumgehung |
| Formatkonformität | EPUB-Struktur, Links, Navigation | versioniertes Fachwerkzeug | TEST-0001 und EXP-0003 | Werkzeugbefund bleibt Evidenz |
| Darstellung | Reflow, Seiten, Bilder, Formeln, Readerabweichungen | Laufzeitmatrix plus manuelles Review | nach erstem Format-Goldstandard | keine allgemeine Readeraussage aus Einzeltest |
| Barrierefreiheit | automatische Regeln, Screenreader- und Inhaltsprüfung | Werkzeug plus zwingende manuelle Anteile | EXP-0003 für automatisierbaren Anteil | kein automatisches Konformitätsurteil |
| Inhaltliche Vollständigkeit | Leseprobe, fehlende Kapitel, OCR-Artefakte | heuristisch, vergleichend, manuell | erst nach geeigneten Sollpaaren | keine unbelegte Vollständigkeitsbehauptung |
| Bibliografische Qualität | Konflikte, Rollen, Sprache, Ausgabe | deterministisch, regelbasiert, später extern | S4 und TEST-0001 | Providerwahl separat |
| Identität | Byte-, Paket-, Ausgaben- und Werkbeziehung | deterministisch bis statistisch | EXP-0004 | Kandidat ist keine Zusammenführung |
| Suche | Metadaten, Volltext, semantische Ähnlichkeit | Information Retrieval, später modellbasiert | erst mit Suchaufgaben-Goldstandard | Index bleibt regenerierbar |
| Routing | Zielregeln, Konflikte, Enthaltung | regelbasiert, später statistisch | S6 und TEST-0001 | Vorschlag ist keine Importfreigabe |
| Transformation | Reparatur, OCR, Konvertierung, Cover | bestandsnah und potenziell schreibend | erst nach eigenem Derivat- und Writer-Gate | Original bleibt unverändert |
| Kontinuierliche Qualität | Drift, Wiederaufnahme, veraltete Befunde | operational und empirisch | TEST-0001 Ablauf-Sollfälle | erst im gewählten Produktablauf |

## Messgrößen

### Kandidatenqualität

- **Precision**: Anteil richtiger positiver Kandidaten an allen ausgegebenen
  positiven Kandidaten.
- **Recall**: Anteil gefundener positiver Sollfälle an allen positiven
  Sollfällen.
- **Selektive Genauigkeit**: Anteil richtiger Ergebnisse an den Fällen, in
  denen das Verfahren nicht enthielt.
- **Abdeckung**: Anteil der geeigneten Fälle, für die das Verfahren ein
  Ergebnis statt Enthaltung lieferte.
- **Korrekte Enthaltung**: Anteil der ausdrücklich mehrdeutigen Sollfälle, in
  denen keine eindeutige Empfehlung ausgegeben wurde.

Precision und Recall werden nicht über Datei-, Repräsentations-, Ausgaben- und
Werkebene gemittelt. Ein Verfahren kann auf einer Ebene gut und auf einer
anderen unbrauchbar sein.

### Evidenz- und Erklärungsqualität

- Anteil der Ergebnisse mit vollständiger Quelle, Methode, Profil und Version;
- Anteil der Ergebnisse mit sichtbarer positiver und negativer Evidenz;
- Anteil korrekt dargestellter `unknown`-, `not_applicable`-, `unsupported`-
  und Enthaltungsfälle;
- Anteil der Rohbefunde, die verlustfrei zu einer Ableitung zurückverfolgt
  werden können;
- Zahl der Nutzerkorrekturen aufgrund fehlender oder irreführender Erklärung.

### Nutzer- und Betriebsqualität

- Zeit bis zur richtigen Reviewentscheidung;
- Zahl notwendiger Ansichtswechsel oder Nachfragen;
- Durchsatz, Latenz, Speicher- und Plattenbedarf;
- identische semantische Ergebnisse bei identischem Eingang und Profil;
- korrektes Überspringen unveränderter Eingänge;
- korrektes Fortsetzen nach Abbruch;
- unbeabsichtigte Schreibwirkungen, Netzwerkübertragungen und private
  Pfadlecks: jeweils null im read-only Umfang.

## Asymmetrische Fehlerkosten

Die Einordnung ist eine Untersuchungsvorgabe und noch keine numerische
Schwellenentscheidung.

| Fehlertyp | Relative Folgekosten | Konsequenz für spätere Bewertung |
|---|---|---|
| gefährliche oder stark beschädigte Datei übersehen | hoch bis kritisch | Recall und sichere Unbekanntbehandlung priorisieren |
| unkritische Datei zum Review vorlegen | niedrig bis mittel | begrenzte False Positives sind akzeptabler als stille Freigabe |
| zwei verschiedene Ausgaben oder Werke zusammenfassen | kritisch | hohe Precision und Enthaltung verlangen |
| echte Dublette übersehen | mittel | zunächst Review-Aufwand statt Bestandsverlust |
| falsche Person, Rolle oder Ausgabe vorschlagen | hoch | feldbezogene Evidenz und Nutzerbestätigung verlangen |
| kosmetische Normalisierung nicht vorschlagen | niedrig | keine aggressive Automatisierung rechtfertigen |
| falsches Ziel eindeutig empfehlen | hoch | selektive Genauigkeit vor hoher Abdeckung |
| bei mehrdeutigem Routing enthalten | niedrig | Enthaltung als regulären Erfolg messen |
| automatische Accessibility-Prüfung als vollständig bestanden darstellen | kritisch | automatische und manuelle Evidenz strikt trennen |
| bekannten Suchtreffer nicht finden | mittel bis hoch | Recall auf realen Nutzeraufgaben messen |

## Abschlusskriterien WI-0003

WI-0003 ist auf Dokumentationsebene erfüllt, wenn:

- alle sechs Szenarien einen vollständigen Entscheidungsvertrag besitzen;
- Qualitätsaktivitäten nach Prüfklasse und Voraussetzung eingeordnet sind;
- asymmetrische Fehlerfolgen und Messgrößen benannt sind;
- TEST-0001 konkrete Sollfälle und Datenregeln besitzt;
- EXP-0002 bis EXP-0005 Frage, Eingänge, Pass- und Stoppkriterien besitzen;
- GATE-0001, Stack, Oberfläche, erster Vertikalablauf und Writer offen bleiben;
- Registry, Dokumentlinks, Datenschutz und Repository-Validierung erfolgreich
  geprüft sind.
