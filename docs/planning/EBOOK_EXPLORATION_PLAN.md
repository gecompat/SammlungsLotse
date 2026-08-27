# E-Book-Erkundungs- und Erkenntnisplan

Status: BRAINSTORMING — KEINE AUSFÜHRBARE PRODUKTROADMAP

Stand: 2026-08-27

Artifacts: WI-0002, WI-0003, REQ-0002, RISK-0001, TEST-0001, EXP-0001 bis
EXP-0006, GATE-0001

## Ziel

Dieser Plan ordnet die weitere Analyse der E-Book-Linie vom Groben ins Detail.
Er soll spätere Entscheidungen mit reproduzierbarer Evidenz ermöglichen,
ohne SammlungsLotse früh an einen Stack, ein Format, ein Fachsystemdetail,
eine Suchtechnik, eine Benutzeroberfläche oder einen Writer zu koppeln.

Der vollständige fachliche Möglichkeitenraum steht in
[EBOOK_LANDSCAPE.md](EBOOK_LANDSCAPE.md). Der Plan autorisiert keinen
Produktcode oder schreibenden Operationstyp. Die TEST-0001-Fixture-
Validierung wurde ausgeführt; EXP-0002 bis EXP-0005 sind empirisch
abgeschlossen.

Die konkretisierten Nutzerentscheidungen und Messverträge stehen in
[EBOOK_SCENARIOS_AND_METRICS.md](EBOOK_SCENARIOS_AND_METRICS.md). TEST-0001
ist in [EBOOK_REFERENCE_CORPUS.md](EBOOK_REFERENCE_CORPUS.md) spezifiziert;
die einzelnen Experimentverträge stehen in
[EBOOK_EXPERIMENTS.md](EBOOK_EXPERIMENTS.md).

## Hauptrisiko RISK-0001

Das zentrale Risiko ist eine frühe Kopplung der E-Book-Schiene an eine
scheinbar naheliegende Teillösung. Mögliche Sackgassen sind:

- `Buch = Datei` oder `Werk = Calibre-Datensatz`;
- EPUB als hart eingebautes Gesamtmodell statt als Formatprofil;
- Calibre-interne Tabellen oder Verzeichnisse als Kernvertrag;
- ein globaler Qualitätsscore als Ersatz für Befunde;
- ein Suchindex oder Embedding-Modell als kanonische Wahrheit;
- ein UI- oder Transportmodell als Anwendungsschicht;
- ein allgemeiner Writer mit übertragbarer Freigabe;
- externe Metadaten- oder KI-Provider als zwingende Laufzeitabhängigkeit;
- der Versuch, alle Medienlinien durch ein gemeinsames Fachschema zu
  vereinheitlichen;
- die ungeprüfte Übernahme einer FolioTone-Architektur oder ihres Backlogs.

### Gegenmaßnahmen

- Datei, Repräsentation, Ausgabe, Werk, Person und Zielbibliothek trennen;
- Rohbeobachtung, Evidenz, Ableitung, Vorschlag, Entscheidung und Operation
  getrennt erhalten;
- Format-, Fachsystem-, Werkzeug- und Providerzugänge als austauschbare
  Adapter behandeln;
- Qualitätsdimensionen einzeln und versioniert ausweisen;
- Originale unverändert lassen und Derivate explizit verknüpfen;
- lokale und netzwerklose Verträge zuerst prüfen;
- Experimente wegwerfbar halten und keine Spike-Struktur zum Produktkern
  erklären;
- Entscheidungen erst an ausdrücklich formulierten Gates treffen;
- sichtbares Nutzerverhalten separat von API- und Komponententests abnehmen;
- jeden Writer als eigenen Operationstyp mit eigener Sicherheitskette
  behandeln.

## Mögliche erste Produktzuschnitte

Die Einordnung ist eine Untersuchungshypothese und keine Priorisierung.

| Zuschnitt | Enthaltener Ablauf | Erkenntniswert | Typische Gefahr |
|---|---|---|---|
| Eingangstriage | Eingang erfassen, prüfen, Dubletten und Metadaten bewerten, Ziel vorschlagen | berührt viele Kernverträge ohne Bestandsänderung | zu viele Qualitätsdimensionen gleichzeitig |
| Bestandsprüfung | Calibre-Bibliotheken read-only inventarisieren und Qualitätsbefunde darstellen | früher Nutzen für vorhandene Bestände | reine Reportinglösung oder Calibre-Nachbildung |
| Suche zuerst | Bestand erfassen, indexieren und über Metadaten, Volltext oder Semantik erschließen | hoher sichtbarer Nutzerwert | Index- oder KI-Technik prägt zu früh das Modell |
| Reparaturwerkbank | Befunde prüfen und reproduzierbare Derivate erzeugen | direkte Qualitätsverbesserung | Transformation und Schreiben beginnen zu früh |
| Calibre-Orchestrierung | freigegebene Änderungen planen, ausführen und nachprüfen | vollständiger Integrationsnutzen | Sicherheitskette und Recovery werden unterschätzt |

Als derzeit erkenntnisreichste Versuchshypothese gilt eine read-only
Eingangstriage. Sie würde einen synthetischen Eingangsordner und mehrere
synthetische Calibre-Zielbibliotheken erfassen, Formate inventarisieren, EPUB
tief prüfen, Dubletten- und Metadatenkandidaten erklären und ein Routing
vorschlagen oder sich enthalten. Sie würde nichts verschieben, transformieren
oder in Calibre schreiben. GATE-0001 hat diese Hypothese im ersten Vergleich
noch nicht angenommen.

## Erkenntnisstufen

### B0 — Möglichkeitenraum

Ziel:

- Produktrollen und Qualitätsdimensionen vollständig genug erfassen;
- geltende Grenzen von offenen Möglichkeiten trennen;
- bekannte Sackgassen und Gegenmaßnahmen festhalten;
- keine Technologie oder Ausführungsreihenfolge wählen.

Ergebnis:

- [EBOOK_LANDSCAPE.md](EBOOK_LANDSCAPE.md);
- dieser Erkenntnisplan;
- registrierte vorgeschlagene Capability, Anforderung, Risiko, Testvertrag,
  Experiment und Gate.

### B1 — Nutzerfragen, Szenarien und Messgrößen

WI-0003 hat die sechs read-only Nutzerentscheidungen, Qualitäts- und
Automatisierungsmatrix, Messgrößen und asymmetrischen Fehlerkosten auf
Dokumentationsebene konkretisiert. Die kanonischen Detailverträge stehen in
[EBOOK_SCENARIOS_AND_METRICS.md](EBOOK_SCENARIOS_AND_METRICS.md). Planung und
Nachverifikation einer später autorisierten Änderung bleiben hinter dem
getrennten Writer-Gate B7.

Der vollständige spätere Szenarienraum umfasst mindestens:

1. vorhandenen Calibre-Bestand prüfen;
2. neue Eingänge triagieren;
3. Dublettenkandidaten entscheiden;
4. Metadatenkonflikte entscheiden;
5. E-Books strukturiert, inhaltlich und semantisch suchen;
6. ein Ziel unter mehreren Bibliotheken vorschlagen;
7. eine Änderung nur planen und prüfen;
8. eine später autorisierte Änderung nachverifizieren.

Jedes Szenario benötigt:

- Nutzer und auslösendes Problem;
- Eingänge und vorausgesetzten Zustand;
- sichtbares Ergebnis und mögliche Enthaltung;
- Datenschutz- und Netzwerkgrenze;
- erlaubte Wirkungsstufe;
- messbare Akzeptanzkriterien;
- Fehler-, Abbruch- und Wiederaufnahmeverhalten;
- ausdrücklich nicht enthaltene Wirkungen.

Mögliche Messgrößen sind:

- Precision und Recall von Kandidaten auf einem Goldstandard;
- Anteil reproduzierbarer und erklärbarer Befunde;
- Anteil korrekt erkannter `unknown`- oder `not_applicable`-Fälle;
- Nutzerzeit und Korrekturen pro Reviewentscheidung;
- stabile Ergebnisse bei identischem Eingang und Werkzeugprofil;
- Durchsatz, Latenz, Speicher- und Plattenbedarf;
- korrektes Überspringen unveränderter Eingänge;
- korrektes Fortsetzen nach Abbruch;
- Zahl unbeabsichtigter Schreibwirkungen im read-only Bereich: null.

### B2 — TEST-0001: synthetischer Referenzkorpus

Die konkreten Kern- und Ausbau-Sollfälle, Oracles, Datenregeln und
Passkriterien stehen in
[EBOOK_REFERENCE_CORPUS.md](EBOOK_REFERENCE_CORPUS.md). TEST-0001 ist nach
Erzeugung und Validierung aller 26 `Kern`-Fälle in der aktiven Fixture-Version
`0.2.0` `ready`. Version `0.1.0` bleibt als historischer Snapshot erhalten.
Die vier `Ausbau`-Fälle und weitere werkzeugspezifische Experimentmaterialien
bleiben offen. Die folgende Liste bleibt die kategorische Übersicht.

Der Referenzkorpus soll kleine, nachvollziehbare Sollfälle statt reale private
Sammlungsdaten enthalten. Vorgesehene Fallgruppen sind:

- valides EPUB 2 und valides EPUB 3.3;
- beschädigtes Archiv, ungültige OCF-Struktur und fehlende Ressource;
- Reflowable, Fixed Layout, Skript, Remote-Ressource und Media Overlay;
- fehlende Navigation, fehlendes Cover und Accessibility-Fehler;
- widersprüchliche Titel-, Personen-, Sprach- und Identifikatorwerte;
- byteidentische Dateien mit anderen Namen;
- inhaltsgleiche EPUB-Pakete mit abweichender Verpackung oder Metadaten;
- gleiche Ausgabe in zwei Formaten;
- Übersetzung, Neuauflage und anderes Werk mit ähnlichem Titel;
- Leseprobe und Vollausgabe;
- Text-PDF, Scan-PDF, verschlüsseltes PDF und fehlerhafte OCR;
- nichtlateinische Schrift, RTL und mehrsprachiger Inhalt;
- große Datei, tiefe Verzeichnisstruktur und Ressourcenlimitfall;
- zwei Zielbibliotheken mit eindeutigem Routing;
- ein mehrdeutiger Routingfall mit erwarteter Enthaltung;
- Abbruch und Wiederaufnahme eines inkrementellen Laufs.

Für jeden Fall werden Eingang, erwartete Beobachtungen, erwartete Befunde,
zulässige Unsicherheit, verbotene Wirkungen und Herkunft dokumentiert.
Öffentliche Testbücher können nur nach Lizenz- und Provenienzprüfung ergänzt
werden.

### B3 — EXP-0001: wegwerfbare Experimente

EXP-0001 bleibt der Sammelrahmen. Die entscheidungsreifen Fragen für
read-only Calibre-Projektion, EPUB-Evidenz, gestufte Identität, isolierte
Werkzeugausführung und Eingangstriage-Preflight sind als EXP-0002 bis
EXP-0006 registriert. Ihre kanonischen Eingänge, Pass-, Fail- und
Stoppkriterien stehen in [EBOOK_EXPERIMENTS.md](EBOOK_EXPERIMENTS.md).
EXP-0002 bis EXP-0005 sind ausgeführt; EXP-0006 ist `proposed`.

#### Calibre-Lesezugang (EXP-0002)

Fragen:

- Welche dokumentierten read-only Informationen liefert `calibredb` lokal
  und über den Content Server?
- Welche Unterschiede bestehen bei Feldern, Pfaden, Templates, mehreren
  Bibliotheken, Authentisierung und Fehlerverhalten?
- Lassen sich private absolute Pfade aus Standardprojektionen fernhalten?
- Welche Stabilitäts- und Versionsannahmen hätte ein Adapter?

#### Format- und Sicherheitsklassifikation

Fragen:

- Welche Formate und Schutzmerkmale lassen sich ohne tiefe Inhaltsanalyse
  zuverlässig erkennen?
- Wie werden Parserfehler, unbekannte Varianten, Ressourcenlimits und
  potenziell aktive Inhalte dargestellt?
- Wie bleibt eine nicht tief unterstützte Datei trotzdem inventarisiert?

#### EPUB-Konformität und Accessibility (EXP-0003)

Fragen:

- Wie werden EPUBCheck- und Ace-Rohberichte verlustfrei gespeichert?
- Welche Meldungen lassen sich stabil normalisieren, ohne Werkzeugcodes zu
  verstecken?
- Welche Regeln sind standard-, profil- oder werkzeugversionsabhängig?
- Welche Ergebnisse benötigen zwingend manuelles Review?

#### Extraktion und Metadaten

Fragen:

- Welche Rohmetadaten liefern Calibre, EPUB, PDF und weitere Kandidaten?
- Wie werden nicht unterstützte oder still ignorierte Felder erkannt?
- Welche Informationen gehören zur Repräsentation, Ausgabe, zum Werk oder
  zur Person?
- Welche Extraktionswerkzeuge sind lizenzierbar, wartbar und ausreichend
  reproduzierbar?

#### Identität und Dublettenkandidaten (EXP-0004)

Fragen:

- Welche Ebenen werden durch Bytehash, normalisierten Pakethash,
  Textfingerprint, Identifikatoren und Metadatenähnlichkeit abgedeckt?
- Welche negativen Merkmale verhindern falsches Zusammenführen?
- Welche Kandidatenqualität wird auf TEST-0001 erreicht?
- Wann muss das System sich enthalten?

#### Suche

Fragen:

- Welche Nutzerfragen lassen sich mit strukturierter Suche und Volltext
  beantworten?
- Welchen zusätzlichen Nutzen liefert semantische Suche?
- Welche lokale Technik erfüllt Recall, Latenz, Ressourcen- und
  Datenschutzgrenzen?
- Wie bleiben Index und Embeddings vollständig regenerierbar?

#### Externe Metadatenprovider

Fragen:

- Welcher Provider deckt welche Identifikatoren, Sprachen und Ausgaben ab?
- Welche minimalen strukturierten Angaben müssen übertragen werden?
- Welche Lizenz-, Limit-, Kosten- und Cachingbedingungen gelten?
- Wie werden widersprüchliche Antworten und Provider-Ausfall behandelt?
- Bleibt der lokale Ablauf ohne Provider sinnvoll?

#### Isolierte Werkzeugausführung (EXP-0005)

Fragen:

- Welche Tools benötigen native Installation, WSL oder Container?
- Können Netzwerk, Dateisystem, Benutzer, Prozesse, Zeit, Speicher und
  Ausgabegröße begrenzt werden?
- Sind Toolprofile reproduzierbar, versioniert und providerneutral
  beschreibbar?
- Beschädigt ein Abbruch niemals Original oder Fachsystembestand?

#### Eingangstriage-Preflight (EXP-0006)

Fragen:

- Kann eine flache, begrenzte Inspektion Formatfähigkeit und nächste Aktion
  vor jedem tiefen Werkzeuglauf getrennt bestimmen?
- Bleiben instabile, unbekannte, geschützte und riskante Eingänge zuverlässig
  außerhalb des tiefen EPUB-Wegs?
- Bleiben `unsupported`, `unknown`, Reviewbedarf und Enthaltung getrennt?
- Sind alle Entscheidungen zweifach reproduzierbar, netzwerklos und ohne
  Original- oder Fachsystemschreibwirkung?

#### Schreibender Sandbox-Versuch

Dieser Versuch gehört erst hinter ein separates Writer-Gate. Er verwendet
ausschließlich eine synthetische Calibre-Bibliothek und genau einen später
ausgewählten Operationstyp. Er darf nicht mit den read-only Experimenten
vermischt werden.

### B4 — GATE-0001: ersten vertikalen Ablauf auswählen

Der getrennte [GATE-0001-Vergleich](EBOOK_GATE_0001_COMPARISON.md) hat
Eingangstriage und Bestandsprüfung gegen dieselben Voraussetzungen bewertet.
Ergebnis ist eine begründete Vertagung; GATE-0001 bleibt offen.

GATE-0001 kann erst angenommen werden, wenn mindestens vorliegen:

- beschriebene Nutzerfragen und ein vollständiger Ablauf;
- messbare Akzeptanzkriterien;
- TEST-0001 in einer für den Ablauf ausreichenden ersten Fassung;
- relevante Ergebnisse aus EXP-0001;
- geklärte Objekt- und Adaptergrenzen;
- Datenschutz-, Netzwerk- und Ressourcenprofil;
- belegte Ausstiegswege für wesentliche Abhängigkeiten;
- Vergleich mehrerer Produktzuschnitte;
- begründete Auswahl oder begründete Vertagung.

Das Gate entscheidet zunächst nur über den ersten read-only Vertikalablauf.
Es autorisiert keinen produktiven Writer.

### B5 — möglicher read-only Produktprototyp

Erst nach GATE-0001 wäre ein dünner vollständiger Prototyp denkbar. Er sollte:

- einen gemeinsamen Anwendungsvertrag verwenden;
- Fachsystem-, Format-, Werkzeug- und Provideradapter trennen;
- Rohbeobachtungen und abgeleitete Projektionen unterscheiden;
- synthetisch und lokal ohne Netzwerk prüfbar sein;
- unterbrechbar und inkrementell arbeiten;
- eine sichtbare Nutzerentscheidung oder Enthaltung ermöglichen;
- keine produktiven Schreibrechte besitzen.

Wenn eine Browseroberfläche Bestandteil des Nutzwerts ist, muss ihr
tatsächliches sichtbares Verhalten separat geprüft werden. Komponenten-, API-
oder Routentests allein belegen die Browserakzeptanz nicht.

### B6 — optionale Erweiterungsäste

Nach unabhängigem Nutzenbeleg können einzeln folgen:

- tiefere Metadaten- und Normdatenauflösung;
- unscharfes Werk- und Ausgabenmatching;
- PDF- und OCR-Qualität;
- Volltextsuche;
- semantische Suche;
- Accessibility-Review;
- Rendering- und Reader-Matrix;
- reproduzierbare Derivate und Reparaturen.

Jeder Ast kann angenommen, vertagt oder verworfen werden, ohne den
read-only Kern unbrauchbar zu machen.

### B7 — getrenntes Writer-Gate

Ein Writer benötigt eine neue angenommene Entscheidung und wählt genau einen
Operationstyp. Import, Format ergänzen, Format ersetzen, Metadaten schreiben,
Cover schreiben, Bibliothek wechseln und Löschen bleiben getrennt.

Ein Writer-Vertrag benötigt mindestens:

- genaue Ziel- und Berechtigungsgrenze;
- Vorbedingungen und erneute Zustandsprüfung;
- prüfbaren Plan oder Vorschau;
- explizite Autorisierung;
- Idempotenz- und Nebenwirkungsvertrag;
- begrenzte Ausführung über einen unterstützten Calibre-Adapter;
- Nachprüfung gegen den geplanten Zustand;
- Fehler-, Abbruch- und Wiederherstellungsverhalten;
- synthetische Laufzeitprüfung des vollständigen Nutzerwegs.

## Kriterien für spätere Entscheidungen

Optionen sollen nicht allein nach Funktionsumfang bewertet werden. Für jede
wesentliche Auswahl sind mindestens zu vergleichen:

- belegter Nutzerwert;
- Genauigkeit und Kosten von Fehlentscheidungen;
- Reversibilität und Ausstiegsweg;
- Datenschutz und Offline-Fähigkeit;
- Erklärbarkeit und manuelle Überprüfbarkeit;
- Wartung, Sicherheit und Lizenz;
- Reproduzierbarkeit und Testbarkeit;
- Leistung und inkrementelle Skalierung;
- Betriebs- und Integrationsaufwand;
- Wiederverwendbarkeit gemeinsamer Verträge ohne fachliche
  Vereinheitlichung;
- Grad der Kopplung an Calibre, Format, Werkzeug, Provider und UI.

Bewertungen werden erst nach passenden Experimenten vergeben. Dieses
Dokument enthält bewusst keine gewichtete Nutzwertanalyse.

## Bewusst noch nicht entscheiden

- Programmiersprache und Runtime;
- Persistenz- und Suchtechnologie;
- Browser-, Desktop-, CLI- oder Plugin-Ansatz;
- kanonisches E-Book-Format;
- konkretes KI-Modell oder Embeddingverfahren;
- konkrete Metadatenprovider;
- konkrete Calibre-Adapterform;
- Gewichtung eines Qualitätsscores;
- erster produktiver Writer;
- FolioTone-Codeübernahme;
- Implementierungs-Waves oder Termine.

## Nächste Analyse

WI-0003 hat B1 auf Dokumentationsebene abgeschlossen. Die TEST-0001-
Kernfixtures, Oracles, Hashes, Herkunft und verbotenen Wirkungen sind in der
aktiven Version `0.2.0` reproduzierbar manifestiert und validiert. EXP-0005
hat ein enges Podman-Ausführungsprofil netzwerklos qualifiziert. EXP-0002 hat
zwei synthetische Calibre-Ziele reproduzierbar und pfadbereinigt über eine
Copy-on-read-Grenze projiziert; der direkte read-only Mount ist als nicht
unterstützt belegt. EXP-0003 hat EPUBCheck- und Ace-Rohbefunde verlustfrei
referenziert, Ace aber wegen offener Sandbox- und Abhängigkeitsrisiken nicht
produktqualifiziert. EXP-0004 hat alle sechs Identitäts-Sollpaare zweifach
auf fünf getrennten Ebenen ausgewertet; die perfekte synthetische Precision
und der perfekte synthetische Recall sind wegen der kleinen gezielten Menge
keine Produktprognose. WI-0002 und der Vergleich der beiden
Produktzuschnitte sind abgeschlossen. GATE-0001 bleibt nach der begründeten
Vertagung `proposed`: Beide Kandidaten besitzen noch keine ausreichende
End-to-End-Evidenz. Vor der erneuten Gate-Auswertung ist genau eine weitere
Evidenzwelle vorgesehen: der als EXP-0006 registrierte read-only
Eingangstriage-Preflight für Format- und Fähigkeitsklassifikation. Sein
Experimentvertrag ist spezifiziert, die Ausführung aber noch nicht begonnen
oder autorisiert. Auch EXP-0006 beginnt keinen Produktcode.
