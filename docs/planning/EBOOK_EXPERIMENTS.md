# E-Book-Experimentverträge

Status: IN EXECUTION — EXP-0002 AND EXP-0005 PASSED; EXP-0003 AND EXP-0004 NOT EXECUTED

Stand: 2026-08-27

Artifacts: EXP-0001, EXP-0002, EXP-0003, EXP-0004, EXP-0005

## Zweck und Grenze

Dieses Dokument zerlegt den Sammelrahmen EXP-0001 in vier kleine,
entscheidungsfähige Experimente. Die Experimentfragen und Passkriterien sind
dauerhaft; ihre Implementierungen dürfen wegwerfbar bleiben.

Kein Experiment wählt den Produkt-Stack, baut eine gemeinsame
Produktarchitektur oder autorisiert einen Writer. Alle Eingänge stammen aus
TEST-0001. Dessen synthetischer Kern liegt validiert in Fixture-Version
`0.2.0` vor. `0.1.0` bleibt als historischer Snapshot erhalten;
werkzeugspezifische Materialisierung bleibt Teil des jeweiligen
Experimentprofils. Reale Calibre-Bibliotheken und private Medien bleiben
außerhalb des Umfangs.

## Gemeinsamer Experimentvertrag

Jeder spätere Lauf benötigt vor Ausführung:

- genaue Frage und abzugrenzende Alternativhypothese;
- referenzierte TEST-0001-Fälle und Fixture-Version;
- unveränderlichen Eingangs-Snapshot;
- versioniertes Werkzeug- und Ausführungsprofil;
- fest erlaubte Eingänge, Ausgaben und Wirkungen;
- Rohbericht, normalisierte Projektion und Transformationsprovenienz;
- Messverfahren, Pass-, Fail- und Stoppkriterien;
- Zeit-, Speicher-, Platten-, Prozess- und Ausgabegrenzen;
- Netzwerk- und Dateisystemgrenze;
- Cleanup für abgeleitete temporäre Daten;
- Einschränkungen und offene Folgefragen.

Ein fehlgeschlagener Lauf ist Evidenz. Er wird nicht durch einen anderen
Toolaufruf oder eine stillschweigend geänderte Fixture ersetzt.

## EXP-0002 — Read-only Calibre-Bestandsprojektion

### Entscheidungsfrage

Lässt sich eine synthetische Calibre-Bibliothek über dokumentierte,
unterstützte Leseoperationen vollständig genug, versioniert und ohne private
Pfadlecks in einen SammlungsLotse-Snapshot projizieren?

### Zu vergleichende Varianten

- lokal ausgewählte synthetische Bibliothek;
- optional derselbe Bestand über einen synthetisch konfigurierten Calibre
  Content Server;
- kleine explizite Feldprojektion gegenüber einer breiteren Projektion;
- Verhalten bei Custom Columns, mehreren Bibliotheken und unbekannten
  Feldern.

Die Varianten sind Untersuchungsgegenstände, keine Adapterentscheidung.

### Eingänge

- mindestens zwei synthetische Zielbibliotheken aus TEST-0001;
- Bücher mit mehreren Formaten, Custom Columns und fehlenden Werten;
- eindeutige und mehrdeutige Routingfälle;
- dokumentierte Calibre- und Schnittstellenversion.

### Zu erhebende Evidenz

- tatsächlich aufgerufener Befehl mit bereinigten Argumentwerten;
- Exitcode, Laufzeit und Standardfehlerklassifikation;
- unveränderte maschinenlesbare Rohantwort;
- Feld-, Typ-, Null-, Reihenfolge- und Paginationverhalten;
- Auftreten absoluter Pfade oder anderer privater Locators;
- Vorher-/Nachher-Snapshot der synthetischen Bibliothek;
- Unterschiede zwischen lokalen und Servervarianten.

### Passkriterien

- eine feste minimale Lese- und Feld-Whitelist ist empirisch ableitbar;
- die Standardprojektion enthält keine absoluten privaten Pfade, Secrets oder
  nicht angeforderten Felder;
- mehrere Bibliotheken bleiben getrennte Ziele;
- unbekannte Felder und inkompatible Versionen führen zu sichtbarem
  `unsupported` oder begrenzter Projektion;
- identischer Eingang erzeugt semantisch identische Projektionen;
- Calibre-Bestand, Metadaten, Cover und Dateien bleiben byte- und
  fachzustandsbezogen unverändert;
- interne Calibre-Tabellen werden weder Kernvertrag noch direkter
  Schreibzugang.

### Fail- und Stoppkriterien

- eine angeblich lesende Variante verändert den synthetischen Bestand;
- eine notwendige Information ist nur durch direkte interne
  Datenbankkopplung erhältlich;
- private Pfade lassen sich nicht zuverlässig aus der Standardprojektion
  fernhalten;
- Authentisierung oder Berechtigungen würden für den Versuch einen
  allgemeinen Schreibzugang erfordern;
- der Adaptervertrag wäre nur für eine undokumentierte Toolversion
  formulierbar.

### Ausführungsergebnis

EXP-0002 wurde am 2026-08-27 mit Calibre `9.13.0` und dem Profil
`exp-0002-podman-calibre-9.13.0/v1` gegen zwei synthetische Bibliotheken aus
TEST-0001 `0.2.0` ausgeführt. Alle dreizehn Akzeptanzprüfungen sind
erfolgreich; Quell-Snapshots, Arbeitskopien, Projektionen, unbekannte Felder
und Pfadgrenzen sind versioniert belegt. Der vollständige Nachweis steht unter
[experiments/ebook/exp-0002](../../experiments/ebook/exp-0002/README.md).

Ein direkter read-only Mount ist ausdrücklich **nicht** qualifiziert:
Calibre benötigt beim lokalen Bibliotheksöffnen einen temporären
Dateisystemtest. Der erfolgreiche lokale Weg isoliert deshalb jeden Lauf über
eine neue wegwerfbare Arbeitskopie; der Quell-Snapshot wird nicht für Calibre
gemountet und bleibt bytegleich. Die Content-Server-Variante bleibt offen.

## EXP-0003 — EPUB-Konformitäts- und Accessibility-Evidenz

### Entscheidungsfrage

Lassen sich Rohberichte unterschiedlicher EPUB-Prüfwerkzeuge verlustfrei
erhalten und zugleich in gemeinsame, erklärbare Befunde projizieren, ohne
Werkzeugcodes, Profile oder manuellen Prüfbedarf zu verdecken?

### Eingänge

- valide und absichtlich ungültige EPUB-Fälle aus TEST-0001;
- Struktur-, Navigation-, Aktivinhalt- und Accessibility-Fälle;
- mindestens ein automatisch nicht abschließend entscheidbarer
  Accessibility-Fall;
- versionierte Werkzeug- und Standardprofile.

### Zu erhebende Evidenz

- vollständiger maschinenlesbarer Rohbericht je Werkzeug;
- Werkzeugname, Version, Profil, Exitcode und Laufzeit;
- Meldungscode, Originalschweregrad, interne Fundstelle und Kontext;
- normalisierte Qualitätsdimension, Status und Reviewbedarf;
- Pfadbereinigung zwischen internem Rohbericht und Standardprojektion;
- Unterschiede zwischen Werkzeugversionen oder Profilen.

### Passkriterien

- jeder normalisierte Befund verweist auf den unveränderten Rohbefund;
- Meldungscodes, Schweregrade, Fundstellen und Profil bleiben rekonstruierbar;
- neue oder unbekannte Meldungen bleiben als sichtbare Evidenz erhalten;
- automatische, manuelle und nicht anwendbare Accessibility-Prüfungen sind
  unterscheidbar;
- ein sauberer automatischer Bericht erzeugt kein allgemeines
  Barrierefreiheitsurteil;
- absichtliche TEST-0001-Fehler werden im vereinbarten Profil reproduzierbar
  gefunden;
- Original-EPUBs bleiben unverändert und ein Netzabruf findet nicht statt.

### Fail- und Stoppkriterien

- Normalisierung verwirft oder überschreibt Rohmeldungen;
- ein globaler Score ersetzt Einzelbefunde;
- Textlokalisierung wird als stabiler maschinenlesbarer Schlüssel benötigt;
- absolute Hostpfade oder private Inhalte gelangen in Standardberichte;
- das Werkzeug verändert oder repariert den Eingang während der Prüfung.

## EXP-0004 — Gestufte E-Book-Identitätskandidaten

### Entscheidungsfrage

Welche Kombination aus positiver und negativer Evidenz trennt
Dateigleichheit, Repräsentationsgleichheit, gleiche Ausgabe und Werkbezug mit
ausreichender Precision und begründeter Enthaltung?

### Stufen

1. `byte`: kryptografischer Hash derselben Bytefolge;
2. `package`: normalisierte Paket- und Ressourcenmerkmale;
3. `representation`: inhaltlich gleiche Repräsentation trotz Verpackung;
4. `edition`: gleiche bibliografische Ausgabe in einem oder mehreren Formaten;
5. `work`: Werkbezug bei verschiedenen Ausgaben, Übersetzungen oder
   Bearbeitungen.

Die Stufen sind Untersuchungskategorien und noch kein angenommenes
Kernschema.

### Eingänge

- alle Identitäts-Sollpaare aus TEST-0001;
- positive und negative Paare je Stufe;
- Leseprobe, Vollausgabe, Übersetzung und Titelkollision;
- fehlende und widersprüchliche Metadaten.

### Zu erhebende Evidenz

- eingesetzte Merkmale und ihre Gegenstandsebene;
- positive, negative und fehlende Evidenz;
- Kandidatenerzeugung vor teurem Vergleich;
- Ergebnis, Unsicherheit und Enthaltungsgrund;
- Precision, Recall, selektive Genauigkeit und Abdeckung je Stufe;
- Laufzeit und Ressourcen je Vergleichsphase.

### Passkriterien

- Bytegleichheit wird korrekt erkannt, ohne Quellen oder Locators zu
  verschmelzen;
- Neuverpackung wird nicht fälschlich als Bytegleichheit dargestellt;
- gleiche Ausgabe in anderem Format bleibt von Dateigleichheit getrennt;
- Übersetzung und Neuauflage werden nicht als austauschbare Ausgabe bewertet;
- der negative Titelkollisionsfall führt zu `verschieden` oder Enthaltung;
- jeder Kandidat zeigt positive und negative Evidenz;
- kein Kandidat löst Zusammenführung, Entfernung, Verschieben oder Schreiben
  aus.

### Fail- und Stoppkriterien

- ein einzelner Identifikator oder Ähnlichkeitsscore wird zur universellen
  Identität;
- Ergebnisse verschiedener Stufen werden zu einer booleschen Dublette
  zusammengezogen;
- fehlende Evidenz wird als negative Evidenz behandelt;
- ein Verfahren erreicht höhere Abdeckung nur durch falsche positive
  Ausgaben- oder Werkzusammenführungen;
- die Methode benötigt reale private Vergleichsdaten, bevor sie am
  synthetischen Goldstandard messbar ist.

## EXP-0005 — Isolierte E-Book-Werkzeugausführung

### Entscheidungsfrage

Kann ein externes E-Book-Werkzeug reproduzierbar mit enger Dateisystem-,
Netzwerk-, Prozess- und Ressourcengrenze ausgeführt und kontrolliert
abgebrochen werden?

### Eingänge

- kleine valide, ungültige und ressourcenbegrenzende TEST-0001-Fälle;
- ein versioniertes Werkzeugpaket mit dokumentierter Herkunft und Lizenz;
- explizit getrennte read-only Eingabe und beschreibbare temporäre Ausgabe;
- minimierte nicht geheime Umgebungswerte.

### Zu erhebende Evidenz

- kanonisches Werkzeug- und Ausführungsprofil;
- Eingangs- und erlaubte Ausgangsmounts oder gleichwertige Grenzen;
- Netzwerkzustand, Benutzer, Fähigkeiten und Prozessbaum;
- Zeit-, Speicher-, CPU-, Platten- und Ausgabegrenzen;
- Exit-, Timeout-, Kill- und Cleanup-Verhalten;
- Vorher-/Nachher-Hash des Originals;
- zwei Wiederholungsläufe mit identischem Eingang und Profil.

### Passkriterien

- Eingänge sind während der Ausführung read-only;
- Ausgaben entstehen ausschließlich im vorgesehenen temporären Bereich;
- Netzwerkzugriff ist für den netzwerklosen Vertrag technisch unterbunden;
- Zeit-, Speicher- und Ausgabegrenzen beenden den jeweiligen Sollfall
  kontrolliert;
- Abbruch hinterlässt keinen laufenden Kindprozess und verändert kein
  Original;
- relevante Profile und Toolartefakte sind versioniert und mit Herkunft
  nachweisbar;
- Wiederholungsläufe liefern semantisch gleichwertige Befunde;
- Secrets und nicht erlaubte Host-Umgebungswerte sind im Prozess nicht
  verfügbar.

### Fail- und Stoppkriterien

- ein Werkzeug benötigt allgemeinen Host- oder Netzwerkzugriff ohne
  begrenzbare Alternative;
- Eingänge müssen beschreibbar eingebunden werden;
- Ressourcenlimits sind nur dokumentiert, aber nicht empirisch wirksam;
- Abbruch oder Fehler beschädigt Eingang, Zielbibliothek oder Hostzustand;
- Toolversion, Lizenz oder Herkunft ist nicht reproduzierbar belegbar.

### Ausführungsergebnis

EXP-0005 wurde am 2026-08-27 mit dem Profil
`exp-0005-podman-epubcheck-5.3.0/v1` gegen TEST-0001 `0.2.0` ausgeführt und
hat alle elf Akzeptanzprüfungen erfüllt. Der versionierte Ergebnis- und
Profilnachweis steht unter
[experiments/ebook/exp-0005](../../experiments/ebook/exp-0005/README.md).
EPUBCheck-Ausgaben waren in je zwei validen und ungültigen Läufen semantisch
gleich. Read-only-, Netzwerk-, Zeit-, Prozess-, Speicher-, CPU-, Output- und
Umgebungsgrenzen waren empirisch wirksam; alle Originalhashes blieben gleich.

Das Ergebnis qualifiziert ausschließlich diesen wegwerfbaren Podman-
Linux/amd64-Weg. Es wählt keinen Produktcontainer und ersetzt nicht die
fachliche Werkzeugbewertung in EXP-0003.

## Noch nicht registrierte Experimentäste

Die folgenden Themen bleiben Möglichkeiten innerhalb von EXP-0001, sind aber
noch keine ausführungsreifen Experimente:

- allgemeine Format- und Sicherheitsklassifikation über EPUB hinaus;
- Extraktion und externe Metadatenprovider;
- PDF- und OCR-Qualität;
- Volltext- und semantische Suche;
- Rendering- und Reader-Matrix;
- Reparatur, Transformation und jeder schreibende Sandbox-Versuch.

Für diese Äste fehlen mindestens ein passender TEST-0001-Ausbau, konkrete
Nutzeraufgaben oder ein separates Writer-Gate. Es werden noch keine weiteren
EXP-Referenzen reserviert.

## Vorgesehene Erkenntnisreihenfolge

1. TEST-0001-Kernfixtures und Oracles erzeugen — abgeschlossen;
2. EXP-0005 als gemeinsame Sicherheitsqualifikation ausführen — abgeschlossen;
3. EXP-0002 als getrennte Calibre-Projektion ausführen — abgeschlossen;
4. EXP-0003 unabhängig mit EPUBCheck- und Ace-Evidenz ausführen;
5. EXP-0004 erst mit vollständigen positiven und negativen Sollpaaren
   bewerten;
6. Ergebnisse ohne gemeinsame Spike-Implementierung vergleichen;
7. Eingangstriage und Bestandsprüfung an GATE-0001 gegenüberstellen.

Die Reihenfolge ist ein Lernplan und keine freigegebene Produktroadmap.
