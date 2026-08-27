# GATE-0001: Vergleich des ersten E-Book-Vertikalablaufs

Status: AUSGEWERTET — VERTAGT; GATE OFFEN

Stand: 2026-08-27

Artifact: GATE-0001

## Ergebnis

GATE-0001 nimmt derzeit weder die Eingangstriage noch die Bestandsprüfung als
ersten Vertikalablauf an. Die Auswahl wird begründet vertagt.

Die Bestandsprüfung besitzt die breitere Kette bereits ausgeführter
Experimente. Diese Kette ist jedoch noch kein vollständiger Nutzerablauf und
stützt sich auf eine Calibre-Copy-on-read-Grenze sowie ein nicht
produktqualifiziertes Ace-Profil. Die Eingangstriage ist weniger an ein
Fachsystem gekoppelt und besitzt den kleineren Ausstiegsaufwand. Ihr
sicherheitskritischer erster Entscheid — welche Eingänge stabil, unterstützt,
geschützt, riskant oder nicht tief prüfbar sind — ist aber noch nicht als
zusammenhängendes Profil empirisch belegt.

Eine Auswahl allein nach der Zahl bestandener Experimente würde diese
unterschiedlichen Evidenzlücken verdecken. Die Vertagung hält beide
Ausstiegswege offen und autorisiert weder Produktcode noch einen Writer.

## Fortschreibung nach EXP-0006

EXP-0006 wurde nach dieser ersten Vergleichsauswertung als getrennte
Evidenzwelle ausgeführt und hat 16/16 Akzeptanzkriterien sowie 11/11 vorab
gebundene Preflight-Zeilen bestanden. Kritische Fehlfreigaben waren null, die
beiden Wiederholungen semantisch identisch und die protokollierten Netzwerk-,
Dateisystem-, Prozess- und Ressourcengrenzen wirksam.

Die nachfolgende Vergleichstabelle hält weiterhin den Befund der ersten
Gate-Auswertung fest. Diese Experiment-Wave nimmt keinen Kandidaten an und
schreibt das Gate nicht stillschweigend um. GATE-0001 bleibt `proposed` und
wird als nächster getrennter Planungsschritt mit dem versionierten Ergebnis
neu ausgewertet.

## Entscheidungsgrenze

Verglichen werden ausschließlich zwei read-only Produktzuschnitte:

- **Bestandsprüfung (S1):** eine explizit ausgewählte Calibre-Bibliothek als
  begrenzten Snapshot erfassen, Qualitäts- und Identitätsbefunde ableiten und
  Review-Kandidaten begründen;
- **Eingangstriage (S2):** einen stabilen neuen Datei-Snapshot erfassen,
  Format-, Schutz-, Sicherheits- und Qualitätsfähigkeit bestimmen und
  begründete nächste Entscheidungen oder Enthaltung ausgeben.

Nicht entschieden werden Stack, Programmiersprache, Persistenz, Suche,
Oberfläche, öffentlicher Vertrag, konkreter Produktadapter, Produktwerkzeug,
Deployment, FolioTone-Übernahme oder schreibende Fähigkeit.

## Bewertungsverfahren

Jedes Kriterium verwendet dasselbe Vokabular:

- `BELEGT`: durch den versionierten Vertrag und ausgeführte Evidenz gedeckt;
- `TEILWEISE`: relevante Evidenz liegt vor, aber nicht für den vollständigen
  Kandidatenablauf;
- `OFFEN`: die für eine Gate-Annahme notwendige Evidenz fehlt;
- `NICHT_ANWENDBAR`: das Kriterium gehört nicht zum Kandidaten.

Die Einstufungen werden nicht zu einer Punktzahl verdichtet. Ein einzelner
sicherheits- oder wirkungsrelevanter offener Punkt kann eine Gate-Annahme
verhindern.

## Gemeinsame Evidenzbasis

- TEST-0001 `0.2.0`: 26 ausführbare `Kern`-Fälle und 44 Komponenten;
- EXP-0002: reproduzierbare, pfadbereinigte Calibre-Projektion für zwei
  synthetische Zielbibliotheken über Copy-on-read;
- EXP-0003: verlustfreie EPUBCheck- und Ace-Rohbefunde für sieben Fälle;
- EXP-0004: sechs Sollpaare auf fünf getrennten Identitätsebenen;
- EXP-0005: begrenzte netzwerklose EPUBCheck-Ausführung unter Podman.

Die vier TEST-0001-`Ausbau`-Fälle sind nicht materialisiert. Alle Experimente
verwenden kleine synthetische Eingänge. Keines qualifiziert einen
Produktadapter, einen vollständigen Ablauf oder einen Technologie-Stack.

## Vergleich

| Kriterium | Bestandsprüfung | Eingangstriage |
|---|---|---|
| Nutzerfrage und erlaubte Wirkung | `BELEGT`: S1 begrenzt den Ablauf auf begründete Befunde und Review-Kandidaten | `BELEGT`: S2 begrenzt den Ablauf auf Klassifikation, Kandidaten und Enthaltung |
| Vollständiger ausführbarer Ablauf | `OFFEN`: Projektion, Werkzeugbefund und Identitätsbewertung wurden getrennt, nicht als Nutzerablauf, ausgeführt | `OFFEN`: Einzelbefunde bestehen, aber der vorgelagerte Fähigkeitsentscheid wurde nicht zusammenhängend ausgeführt |
| Eingang und Snapshot | `TEILWEISE`: zwei synthetische Bibliotheken sind reproduzierbar; direkter read-only Mount ist widerlegt, Content Server offen | `TEILWEISE`: stabile, wachsende, unbekannte, defekte, geschützte und riskante Kernfälle existieren; ein gemeinsames Preflight-Profil fehlt |
| Format- und Sicherheitsabdeckung | `TEILWEISE`: EPUBCheck und Containergrenzen sind belegt; Ace ist nicht produktqualifiziert und andere Bestandsformate sind nicht breit geprüft | `TEILWEISE`: relevante TEST-0001-Oracles existieren; ihre sichere Reihenfolge und Klassifikationsgüte sind nicht empirisch belegt |
| Identitäts- und Dublettenevidenz | `TEILWEISE`: fünf Ebenen sind an sechs gezielten Paaren belegt, jedoch nicht an einem vollständigen Bestand | `TEILWEISE`: dieselbe kleine Evidenz unterstützt Kandidaten gegen Zielbestände, aber keine Eingangsentscheidung im Ganzen |
| Messbarkeit und Enthaltung | `TEILWEISE`: getrennte Metriken und Enthaltung sind definiert; Nutzerreview und End-to-End-Abdeckung fehlen | `TEILWEISE`: Fehlerkosten und Metriken sind definiert; besonders Schutzklassifikation und Enthaltungsqualität wurden nicht als Ablauf gemessen |
| Datenschutz, Netzwerk und Ressourcen | `TEILWEISE`: enge Experimentprofile sind belegt; das Profil des zusammengesetzten Ablaufs fehlt | `TEILWEISE`: unveränderte Eingänge und Werkzeugisolation sind belegt; das Preflight- und Ablaufprofil fehlt |
| Fachsystemkopplung und Ausstieg | `TEILWEISE`: unterstützter CLI-Weg und pfadbereinigte Projektion sind eng begrenzt; Copy-on-read bleibt Calibre-spezifisch | `BELEGT`: der Zuschnitt setzt kein führendes Fachsystem voraus und kann vor jedem tieferen Adapter stoppen |
| Austauschbarkeit der Werkzeuge | `TEILWEISE`: Rohberichte bleiben getrennt; die konkrete Produktalternative zu Ace ist offen | `TEILWEISE`: tiefe Werkzeuge können hinter dem Fähigkeitsentscheid austauschbar bleiben; dieser Vertrag ist noch nicht ausgeführt |
| Schwerster Restfehler | übersehener schwerer Bestandsbefund bei nur teilweise erfasstem Bestand | gefährlicher oder unvollständiger Eingang wird zu früh als tief prüfbar eingestuft |
| Gate-Reife | `NICHT ANNEHMBAR` | `NICHT ANNEHMBAR` |

## Prüfung der Gate-Voraussetzungen

| Voraussetzung aus dem Erkundungsplan | Befund |
|---|---|
| Nutzerfragen und vollständiger Ablauf | Nutzerfragen sind beschrieben; ein vollständiger ausführbarer Ablauf fehlt für beide Kandidaten |
| Messbare Akzeptanzkriterien | für S1 und S2 beschrieben, noch nicht End-to-End erhoben |
| ausreichende TEST-0001-Fassung | gemeinsame Kernfälle sind `ready`; die kandidatspezifische Ablaufabdeckung ist nur teilweise belegt |
| relevante Experimentergebnisse | EXP-0002 bis EXP-0005 liegen vor und zeigen auch Negativbefunde |
| Objekt- und Adaptergrenzen | als Produktgrenzen beschrieben, nicht als angenommener Anwendungsvertrag konkretisiert |
| Datenschutz-, Netzwerk- und Ressourcenprofil | für einzelne Experimente belegt, nicht für einen vollständigen Kandidatenablauf |
| Ausstiegswege wesentlicher Abhängigkeiten | Eingangstriage ist fachsystemneutral; Calibre- und Ace-Ausstieg sind nur teilweise geklärt |
| Vergleich mehrerer Produktzuschnitte | mit diesem Dokument erfüllt |
| Auswahl oder Vertagung | begründete Vertagung; GATE-0001 bleibt offen |

Damit ist die Vergleichsarbeit abgeschlossen, nicht aber das Gate zur
Produktimplementierung.

## Genau eine ausgeführte Evidenzwelle

Vor der erneuten Gate-Auswertung wurde genau eine weitere Evidenzwelle
verfolgt: **read-only Eingangstriage-Preflight für Format- und
Fähigkeitsklassifikation**. Sie ist als EXP-0006 registriert, unter
[EBOOK_EXPERIMENTS.md](EBOOK_EXPERIMENTS.md) spezifiziert und empirisch
abgeschlossen.

Die Wave soll ausschließlich mit synthetischen TEST-0001-Eingängen prüfen,
ob vor jedem tiefen Werkzeuglauf reproduzierbar unterschieden werden kann:

- stabil und für eine explizit unterstützte tiefe Prüfung geeignet;
- noch instabil und deshalb zu vertagen;
- unbekanntes oder nicht unterstütztes Format;
- geschützt oder verschlüsselt, ohne Schutzumgehung;
- strukturell defekt oder mit aktivem beziehungsweise entferntem Inhalt;
- durch Pfad-, Expansion-, Zeit- oder andere Ressourcengrenzen zu stoppen;
- nicht sicher entscheidbar und deshalb manuell zu prüfen oder zu enthalten.

### Mindestnachweis

- alle einschlägigen vorhandenen TEST-0001-`Kern`-Oracles werden abgedeckt;
- die Inhaltsbeobachtung schlägt Dateiendung und ungeprüfte Metadaten;
- tiefe Parser und Werkzeuge starten nur nach einer positiven Fähigkeit;
- `unsupported`, `unknown`, Reviewbedarf und Enthaltung bleiben getrennt;
- Originalhashes bleiben unverändert, Netzwerk- und Schreibwirkungen sind
  null und Ressourcenabbrüche sind begrenzt;
- zwei unabhängige Wiederholungen erzeugen dieselben semantischen Ergebnisse;
- Fehlklassifikationen werden nach den asymmetrischen S2-Fehlerkosten
  ausgewiesen, nicht durch einen Gesamtscore verdeckt;
- Profil, Eingänge, erwartete Ergebnisse und Stopkriterien sind vor dem Lauf
  versioniert.

EXP-0006 ist `done`. Exaktes Ausführungsprofil, wegwerfbarer Runner,
Ergebnisvertrag und Ergebnisvalidator wurden vor den gewerteten
Wiederholungen versioniert. Der Versuch hat keinen Produktcode, keine UI,
keine Persistenz, keinen Writer und keine reale oder private Datei
eingeführt.

## Wiederöffnung und Ausgänge

Nach genau dieser Evidenzwelle wird GATE-0001 getrennt erneut ausgewertet.
Zulässig bleiben drei Ausgänge:

1. Eingangstriage annehmen, wenn der Preflight die kritische S2-Lücke
   schließt und der kleinste vollständige read-only Ablauf begrenzbar ist;
2. Bestandsprüfung annehmen, wenn die Eingangstriage-Lücke nicht mit einem
   vertretbar engen Profil geschlossen werden kann und S1 als kleinerer,
   klarer begrenzter Ablauf begründet wird;
3. beide verwerfen oder erneut vertagen, aber nur mit einem neu benannten
   entscheidenden Blocker; daraus folgt nicht automatisch eine weitere
   Experimentserie.

Keine dieser Optionen autorisiert einen Writer. Ein angenommener
Vertikalablauf müsste anschließend als eigener registrierter Arbeitsgegenstand
geplant werden.
