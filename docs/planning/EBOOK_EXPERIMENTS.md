# E-Book-Experimentverträge

Status: EXP-0002 TO EXP-0006 PASSED

Stand: 2026-08-27

Artifacts: EXP-0001, EXP-0002, EXP-0003, EXP-0004, EXP-0005, EXP-0006

## Zweck und Grenze

Dieses Dokument zerlegt den Sammelrahmen EXP-0001 in kleine,
entscheidungsfähige Experimente. EXP-0002 bis EXP-0006 sind ausgeführt. Die
Experimentfragen und Passkriterien sind dauerhaft; ihre Implementierungen
dürfen wegwerfbar bleiben.

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

### Ausführungsergebnis

EXP-0003 wurde am 2026-08-27 mit EPUBCheck `5.3.0`, Ace `1.4.6` und dem
Profil `exp-0003-epubcheck-5.3.0-ace-1.4.6/v2` ausgeführt. Sieben
synthetische TEST-0001-Fälle liefen je zweimal; alle vierzehn
Akzeptanzprüfungen waren erfolgreich. Rohberichte, Codes,
Originalschweregrade, Fundstellen, Profile, unbekannte Meldungen und
Reviewbedarf bleiben über Hash und `raw_ref` rekonstruierbar. Der Nachweis
steht unter
[experiments/ebook/exp-0003](../../experiments/ebook/exp-0003/README.md).

Der erfolgreiche Evidenzvertrag ist keine Produktfreigabe für Ace. Sein
Puppeteer-Runner deaktiviert die Chromium-Sandbox, und der bei der
Provisionierung ausgeführte npm-Audit meldete 22 offene Befunde. Die äußere
Podman-Grenze war im synthetischen Versuch wirksam; eine spätere produktive
Werkzeugwahl muss die Abhängigkeits- und Sandboxlage neu bewerten.

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

### Ausführungsergebnis

EXP-0004 wurde am 2026-08-27 mit dem Profil
`exp-0004-identity-heuristic/v1` gegen TEST-0001 `0.2.0` ausgeführt und hat
alle fünfzehn Akzeptanzprüfungen erfüllt. Der versionierte Ergebnis- und
Profilnachweis steht unter
[experiments/ebook/exp-0004](../../experiments/ebook/exp-0004/README.md).

Sechs synthetische Sollpaare wurden je zweimal auf Byte-, Paket-,
Repräsentations-, Ausgaben- und Werkebene bewertet. Precision, Recall und
selektive Genauigkeit betrugen im kleinen Goldstandard je Ebene 1,0; es gab
keine False Positives. Die Ausgabenabdeckung blieb bewusst bei 5/6, weil
Leseprobe und Vollausgabe wegen widersprüchlicher Ausgabenevidenz zur
korrekten Enthaltung führten. Alle Kandidaten bewahrten positive und negative
Evidenz, fehlende Evidenz blieb separat und alle Eingänge unverändert.

Der Nachweis qualifiziert kein Produktmodell. Insbesondere sind die sechs
gezielten Paare, ein einzelner synthetischer Titelqualifikator und ein
fallgebundener Ausgabenschlüssel keine Evidenz für Robustheit in realen
Sammlungen. Writer, Zusammenführung und Entfernung blieben vollständig
außerhalb des Versuchs.

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

## EXP-0006 — Read-only Eingangstriage-Preflight

Status: PASSED

### Entscheidungsfrage

Kann ein flacher, begrenzter Preflight vor jedem tiefen Werkzeuglauf die
vorhandenen synthetischen S2-Eingänge reproduzierbar so klassifizieren, dass
kein instabiler, unbekannter, geschützter oder riskanter Eingang irrtümlich
für die tiefe read-only EPUB-Prüfung freigegeben wird?

Die Gegenhypothese lautet: Die vorhandenen Signale reichen für diese Grenze
nicht aus oder verlangen bereits unvertretbar tiefe beziehungsweise
gekoppelte Parser. Auch dieses Ergebnis wäre entscheidungsfähige Evidenz.

### Experimentgrenze

Der Preflight ist kein Produktadapter und keine allgemeine Formatbibliothek.
Er darf nur die für die Entscheidung erforderlichen Bytes und
Containerangaben begrenzt als Daten inspizieren. Er führt keinen eingebetteten
Inhalt aus, folgt keiner entfernten Referenz, umgeht keinen Schutz und
extrahiert nicht am Original.

Die experimentelle Ausgabe hält mindestens getrennt:

- `format_capability`: `supported`, `unsupported` oder `unknown`;
- `next_action`: `continue_deep_read_only`, `defer`, `stop`, `review` oder
  `abstain`;
- `deep_tool_allowed`: explizites Boolean nur für den geprüften tiefen
  EPUB-Werkzeugweg;
- Rohbeobachtungen, Befunde, Evidenzreferenzen und Begründung;
- angewandtes TEST-0001-Ressourcenprofil und beobachtete Wirkungen.

Diese Literale sind ein Experimentvertrag, kein vorweggenommener öffentlicher
Produktvertrag.

### Eingänge und Sollentscheidungen

EXP-0006 bindet sich an TEST-0001 `0.2.0`. Die folgende Matrix ist vor dem
Lauf fest und wird nicht aus dem Ergebnis abgeleitet:

| Eingang oder Kontrolle | `format_capability` | `next_action` | `deep_tool_allowed` |
|---|---|---|---|
| `ingress-stable-minimal` | `supported` | `continue_deep_read_only` | `true` |
| `epub33-valid-reflow` | `supported` | `continue_deep_read_only` | `true` |
| `ingress-growing-file` | `unknown` | `defer` | `false` |
| `container-corrupt` | `unsupported` | `stop` | `false` |
| `container-path-traversal` | `supported` | `stop` | `false` |
| `container-expansion-limit` | `supported` | `stop` | `false` |
| `protected-or-encrypted` | `unsupported` | `stop` | `false` |
| `format-unknown` | `unknown` | `abstain` | `false` |
| `epub-active-or-remote` | `supported` | `review` | `false` |
| PDF-Komponente aus `identity-multiformat-edition` | `unsupported` | `stop` | `false` |
| `run-tool-timeout` nach positiver Vorprüfung | `supported` | `stop` | `true` |

`unsupported` für die PDF-Komponente gilt nur für den in EXP-0006 geprüften
tiefen EPUB-Weg. Es ist keine Aussage, dass SammlungsLotse oder ein späterer
Adapter PDF grundsätzlich nicht unterstützen darf.

### Sichere Reihenfolge

1. Eingangsgröße, Hash und Stabilität gegen den versionierten Snapshot prüfen.
2. Inhaltssignatur vor Dateiendung und ungeprüften Metadaten bewerten.
3. Container-Eintragsnamen und deklarierte Größen ohne Extraktion gegen die
   TEST-0001-Grenzen prüfen.
4. Schutzmarker sowie aktive und entfernte Referenzen begrenzt als Daten
   inspizieren, ohne Inhalt auszuführen oder abzurufen.
5. Fähigkeit, Folgeentscheidung, Befunde und Begründung getrennt ausgeben.
6. Einen tiefen Werkzeugweg nur bei `deep_tool_allowed=true` starten; die
   Timeout-Kontrolle muss danach weiterhin begrenzt stoppen.

### Zu erhebende Evidenz

- genaue Fixture-, Manifest-, Runner- und Profilhashes;
- alle erwarteten und tatsächlich beobachteten Klassifikationen je Zeile;
- Rohbeobachtungen und Befunde aus dem TEST-0001-Oracle;
- Fälle, in denen ein tiefer Werkzeugstart erlaubt, verhindert oder
  kontrolliert beendet wurde;
- zwei unabhängige Wiederholungen mit semantischem Ergebnisdigest;
- Vorher-/Nachher-Hashes aller Eingänge;
- Netzwerk-, Dateisystem-, Zeit-, Prozess- und Ausgabegrenzen;
- Abweichungen ohne nachträgliche Schwellen- oder Profiländerung.

### Passkriterien

- alle elf Matrixzeilen entsprechen der vorab festgelegten Sollentscheidung;
- kein Fall mit `deep_tool_allowed=false` startet einen tiefen Werkzeugweg;
- sicherheitskritische Fehlfreigaben betragen exakt null;
- Signatur, Schutz-, Pfad-, Expansion-, Aktivinhalt- und Remote-Befunde bleiben
  als getrennte Evidenz sichtbar;
- `unsupported`, `unknown`, `review` und `abstain` werden nicht
  zusammengefasst oder als generischer Fehler ausgegeben;
- beide Wiederholungen sind semantisch identisch;
- Originalhashes bleiben unverändert; Netzwerk-, Fachsystem- und
  Originalschreibwirkungen sind exakt null;
- der 100-ms-Timeout aus `run-tool-timeout` beendet den synthetischen Helfer
  samt Kindprozessen und schreibt nur in den erlaubten temporären Bereich;
- alle fallgebundenen Eingangs-, Expansions- und Zeitgrenzen stammen aus dem
  versionierten TEST-0001-Manifest.

Die Metriken werden je Matrixzeile und Fehlerklasse ausgewiesen. Ein
Gesamtscore darf eine sicherheitskritische Fehlfreigabe nicht ausgleichen.

### Fail- und Stoppkriterien

- ein instabiler, unbekannter, geschützter, defekter oder riskanter Eingang
  erreicht entgegen der Matrix den tiefen Werkzeugweg;
- Dateiendung oder ungeprüfte Metadaten überschreiben die Inhaltssignatur;
- der Versuch benötigt eine reale oder private Datei, ein Fachsystem oder
  Netzwerkzugriff;
- eingebetteter Inhalt wird ausgeführt, eine Remote-Ressource abgerufen,
  Schutz umgangen oder am Original extrahiert;
- ein Ressourcenabbruch bleibt unkontrolliert oder hinterlässt Prozesse;
- Profil, Sollmatrix oder Grenzwerte werden nach Sichtung eines Ergebnisses
  stillschweigend geändert;
- die getrennten Ergebniszustände werden zu einem booleschen
  `safe`/`unsafe`-Wert oder Gesamtscore verdichtet.

### Ausführungsvoraussetzungen

Vor dem ersten empirischen Lauf müssen in einer getrennten Wave mindestens
ein versionsfestes Ausführungsprofil, der wegwerfbare Runner, ein
Ergebnisvertrag und ein CI-geeigneter Ergebnisvalidator unter
`experiments/ebook/exp-0006/` eingecheckt sein. Exakte Befehle, Umgebung,
Eingangs- und Ausgabepfade sowie Cleanup werden dort vor dem Lauf gebunden.

### Ausführungsergebnis

EXP-0006 wurde am 2026-08-27 mit dem Profil
`exp-0006-podman-ingress-preflight/v1` gegen TEST-0001 `0.2.0` unter Podman
6.1.0 auf Linux/amd64 ausgeführt. Alle 16 Akzeptanzkriterien und alle elf
vorab festgelegten Matrixzeilen waren erfolgreich. Acht Fälle blieben
außerhalb des tiefen Werkzeugwegs, drei positiv gegatete Kontrollen starteten
ihn, und kritische Fehlfreigaben betrugen null. `supported`, `unsupported`,
`unknown` sowie `continue_deep_read_only`, `defer`, `stop`, `review` und
`abstain` blieben getrennt sichtbar.

Beide vollständigen Wiederholungen erzeugten den identischen semantischen
Digest
`e14077d5cb783052cd79b309c60d3ae709f363523597e735be087a79a66b4ba4`.
Eingabehashes blieben unverändert. Netzwerkzugriff und verbotene Wirkungen
waren null; read-only Root und Fixture, unprivilegierte UID, Capability-
Entzug, `no-new-privileges`, PID-, CPU-, RAM-, Zeit-, tmpfs- und
Ausgabegrenzen wurden protokolliert und erfüllt.

Ein erster, nicht gewerteter Infrastrukturversuch erzeugte keinen
übernehmbaren Ergebnisdatensatz, weil das Ergebnis nach Prozessende aus dem
Container-tmpfs nicht mehr per `podman cp` verfügbar war. Nach der
versionierten Umstellung des begrenzten Ergebnistransports fand der
Repository-Selbstscan außerdem ein Klartext-Pfadmuster, das den Privacy-Guard
selbst auslöste. Auch diese rein konstruktive Erkennungskorrektur wurde vor
dem endgültigen Lauf committed. Weil sich der gebundene Runner-Hash änderte,
wurden vorhandene Laufergebnisse verworfen und beide gewerteten
Wiederholungen vollständig neu gestartet. Dasselbe galt für die abschließende
Härtung der Input-Grenze, Umgebungsbelege und CI-Neuberechnung: Erst nach
ihrem Preimage-Commit entstanden die eingefrorenen Wiederholungen. Matrix,
Fixture, Entscheidungslogik und Sicherheitsgrenzen blieben unverändert.

Profil, Probe, Runner, Containerdefinition und der CI-geeignete
Ergebnisvalidator stehen unter
[`experiments/ebook/exp-0006/`](../../experiments/ebook/exp-0006/); der
eingefrorene Nachweis steht in
[`result.json`](../../experiments/ebook/exp-0006/result.json). Das Ergebnis
qualifiziert nur diesen kleinen synthetischen Preflight. Es wählt weder einen
Produktparser noch eine Produktlaufzeit und entscheidet GATE-0001 nicht für
sich; die Annahme von S2 folgt aus der getrennten Gate-Neubewertung.

## Noch nicht registrierte Experimentäste

Die folgenden Themen bleiben Möglichkeiten innerhalb von EXP-0001, sind aber
noch keine ausführungsreifen Experimente:

- tiefe Format- und Sicherheitsanalyse über den engen EXP-0006-Preflight
  hinaus;
- Extraktion und externe Metadatenprovider;
- PDF- und OCR-Qualität;
- Volltext- und semantische Suche;
- Rendering- und Reader-Matrix;
- Reparatur, Transformation und jeder schreibende Sandbox-Versuch.

Für diese Äste fehlen mindestens ein passender TEST-0001-Ausbau, konkrete
Nutzeraufgaben oder ein separates Writer-Gate. Über EXP-0006 hinaus werden
noch keine weiteren EXP-Referenzen reserviert.

## Vorgesehene Erkenntnisreihenfolge

1. TEST-0001-Kernfixtures und Oracles erzeugen — abgeschlossen;
2. EXP-0005 als gemeinsame Sicherheitsqualifikation ausführen — abgeschlossen;
3. EXP-0002 als getrennte Calibre-Projektion ausführen — abgeschlossen;
4. EXP-0003 unabhängig mit EPUBCheck- und Ace-Evidenz ausführen — abgeschlossen;
5. EXP-0004 mit vollständigen positiven und negativen Sollpaaren bewerten —
   abgeschlossen;
6. Ergebnisse ohne gemeinsame Spike-Implementierung vergleichen —
   abgeschlossen;
7. Eingangstriage und Bestandsprüfung an GATE-0001 gegenüberstellen — mit
   begründeter Vertagung abgeschlossen;
8. EXP-0006 als genau eine nächste Evidenzwelle registrieren und spezifizieren
   — abgeschlossen;
9. EXP-0006 in einer getrennten, gebundenen Experiment-Wave ausführen —
   abgeschlossen;
10. GATE-0001 anhand des versionierten EXP-0006-Ergebnisses erneut auswerten
    — mit Annahme der eng begrenzten Eingangstriage abgeschlossen.

Die Reihenfolge ist ein Lernplan und keine freigegebene Produktroadmap. Der
Vergleich, die genaue Begrenzung von EXP-0006 und die Gate-Neubewertung stehen
unter [EBOOK_GATE_0001_COMPARISON.md](EBOOK_GATE_0001_COMPARISON.md). Als
nächster getrennter Schritt hat WI-0004 den dünnen read-only Prototyp unter
[EBOOK_INTAKE_PROTOTYPE.md](EBOOK_INTAKE_PROTOTYPE.md) registriert, begrenzt
und angenommen. Seine Implementierung beginnt erst vom kanonischen Plan-Merge.
