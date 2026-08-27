# GATE-0001: Vergleich des ersten E-Book-Vertikalablaufs

Status: AUSGEWERTET — EINGANGSTRIAGE ANGENOMMEN; GATE GESCHLOSSEN

Stand: 2026-08-27

Artifact: GATE-0001

## Ergebnis der Neubewertung

GATE-0001 nimmt die **Eingangstriage (S2)** als ersten begrenzten read-only
E-Book-Vertikalablauf an. Die Bestandsprüfung (S1) bleibt eine mögliche
spätere Produktrolle, wird aber nicht als erster E-Book-Ablauf ausgewählt.

Die Annahme gilt ausschließlich für den kleinsten vollständigen Nutzwert:

1. genau einen ausdrücklich gewählten lokalen Eingang als stabilen,
   unveränderten Snapshot erfassen;
2. einen flachen, begrenzten Preflight ausführen;
3. Formatfähigkeit, Schutz-, Risiko- und Reviewzustand mit Evidenz sichtbar
   machen;
4. genau eine begründete nächste Aktion ausgeben: tiefe read-only Prüfung
   fortsetzen, vertagen, stoppen, manuell prüfen oder sich enthalten.

EXP-0006 schließt die in der ersten Auswertung benannte kritische S2-Lücke
für genau diesen Preflight: 11/11 vorab gebundene Matrixzeilen und 16/16
Akzeptanzkriterien bestanden, kritische Fehlfreigaben waren null, beide
Wiederholungen semantisch identisch und die Netzwerk-, Dateisystem-, Prozess-
und Ressourcengrenzen wirksam. Das genügt, um den kleinsten Ablauf begrenzt
zu planen; es belegt noch keinen Produktablauf.

S2 wird S1 vorgezogen, weil es vor Fachsystem-, Format- und Werkzeugadaptern
stoppen kann und damit den geringeren Kopplungs- und Ausstiegsaufwand besitzt.
Die asymmetrischen Fehlerkosten sind im angenommenen Ausschnitt beherrschbar:
Unsicherheit führt zu Review, Vertagung, Stopp oder Enthaltung, nicht zur
Freigabe. S1 besitzt zwar eine breitere Kette einzelner Experimente, setzt
aber bereits eine Calibre-spezifische Copy-on-read-Grenze voraus und enthält
mit dem nicht produktqualifizierten Ace-Profil einen zusätzlichen offenen
Werkzeugpfad.

Die Auswahl legt weder die erste Medien- oder Implementierungslinie des
Gesamtprodukts noch Stack, UI oder Produktarchitektur fest. Der nächste
Schritt ist ein **eigener registrierter Planungsgegenstand** für den dünnen
read-only Prototyp. GATE-0001 allein autorisiert keinen Produktcode.

## Annahmegrenze

Angenommen sind nur:

- explizite Auswahl genau eines lokalen Eingangs; Entwicklung und Abnahme
  verwenden ausschließlich synthetische Fixtures;
- stabiler, unveränderter Snapshot mit nachprüfbarer Eingangsidentität;
- flacher Format-, Schutz-, Sicherheits- und Fähigkeits-Preflight;
- getrennte Rohbeobachtung, abgeleitete Klassifikation und Begründung;
- fail-closed Entscheidung zwischen Fortsetzen, Vertagen, Stoppen, Review
  und Enthaltung;
- lokale, netzwerklose, begrenzte und unterbrechbare Ausführung;
- sichtbarer Abschluss ohne Änderung am Original oder an einem Fachsystem.

Nicht angenommen oder entschieden sind:

- Calibre-Zielbestand, Bestandsprüfung oder Fachsystemintegration;
- tiefe EPUB-, Accessibility-, Rendering- oder Reader-Prüfung;
- Dubletten-, Werk-, Ausgaben-, Metadaten- oder Routingentscheidung;
- produktiver Parser, konkretes Werkzeug oder Produktcontainer;
- Programmiersprache, Laufzeit, Persistenz, Suche oder öffentlicher Vertrag;
- Oberfläche, Deployment, KI-, Modell- oder Metadatenprovider;
- FolioTone-Übernahme, Transformation, Import oder andere Schreibfähigkeit;
- erste Medienlinie, erste Implementierungs-Wave oder Produktroadmap.

Jeder ausgeschlossene Ast benötigt eine eigene Planung und darf den
angenommenen Preflight nur über einen austauschbaren, ausdrücklich
autorisierten Vertrag erweitern. Er kann angenommen, vertagt oder verworfen
werden, ohne die Gate-Entscheidung umzudeuten.

## Bewertungsverfahren

Jedes Kriterium verwendet dasselbe Vokabular:

- `BELEGT`: durch den versionierten Vertrag und ausgeführte Evidenz für die
  Gate-Entscheidung gedeckt;
- `TEILWEISE`: relevante Evidenz liegt vor, aber nicht für den gesamten
  möglichen späteren Kandidatenumfang;
- `OFFEN`: notwendige Evidenz fehlt;
- `NICHT_ANWENDBAR`: das Kriterium gehört nicht zum Kandidaten.

Die Einstufungen werden nicht zu einer Punktzahl verdichtet. Der schwerste
Restfehler, seine Wirkung, die fail-closed Reaktion sowie Kopplungs- und
Ausstiegsaufwand entscheiden stärker als die Anzahl bestandener Versuche.

## Gemeinsame Evidenzbasis

- TEST-0001 `0.2.0`: 26 ausführbare `Kern`-Fälle und 44 Komponenten;
- EXP-0002: reproduzierbare, pfadbereinigte Calibre-Projektion für zwei
  synthetische Zielbibliotheken über Copy-on-read;
- EXP-0003: verlustfreie EPUBCheck- und Ace-Rohbefunde für sieben Fälle;
- EXP-0004: sechs Sollpaare auf fünf getrennten Identitätsebenen;
- EXP-0005: begrenzte netzwerklose EPUBCheck-Ausführung unter Podman;
- EXP-0006: begrenzter Eingangstriage-Preflight mit 11/11 Matrixzeilen,
  16/16 Akzeptanzkriterien, null kritischen Fehlfreigaben und zwei
  semantisch identischen Wiederholungen.

Die vier TEST-0001-`Ausbau`-Fälle sind nicht materialisiert. Alle Experimente
verwenden kleine synthetische Eingänge. Keines qualifiziert einen
Produktadapter, einen vollständigen Produktablauf oder einen
Technologie-Stack.

Diese Aussage beschreibt die Evidenzbasis zum Zeitpunkt von GATE-0001.
TEST-0001 `0.3.0` hat die vier Ausbau-Fälle später materialisiert; die
historische Gate-Entscheidung und alle an `0.2.0` gebundenen Nachweise bleiben
unverändert.

## Neubewertung

| Kriterium | Bestandsprüfung (S1) | Eingangstriage (S2) |
|---|---|---|
| Nutzerfrage und erlaubte Wirkung | `BELEGT`: S1 begrenzt den Ablauf auf begründete Befunde und Review-Kandidaten | `BELEGT`: S2 begrenzt den Ablauf auf Klassifikation, nächste read-only Aktion und Enthaltung |
| Kleinster vollständig begrenzbarer Ablauf | `TEILWEISE`: Projektion, Werkzeugbefund und Identitätsbewertung wurden getrennt ausgeführt; ein kleiner gemeinsamer Abschluss ist nicht belegt | `BELEGT`: expliziter Eingang, stabiler Snapshot, flacher Preflight und sichtbare nächste Aktion bilden einen vollständigen planbaren Ausschnitt |
| Eingang und Snapshot | `TEILWEISE`: zwei synthetische Bibliotheken sind reproduzierbar; direkter read-only Mount ist widerlegt, Content Server offen | `BELEGT`: EXP-0006 trennt stabile, wachsende, unbekannte, defekte, geschützte und riskante Kernfälle reproduzierbar |
| Format- und Sicherheitsabdeckung | `TEILWEISE`: EPUBCheck und Containergrenzen sind belegt; Ace ist nicht produktqualifiziert und andere Bestandsformate sind nicht breit geprüft | `BELEGT` für den flachen Preflight; `TEILWEISE` für spätere tiefe Formatwerkzeuge, die nicht Teil der Annahme sind |
| Identitäts- und Dublettenevidenz | `TEILWEISE`: fünf Ebenen sind an sechs gezielten Paaren belegt, jedoch nicht an einem vollständigen Bestand | `TEILWEISE`: Eingangsidentität und Unverändertheit sind belegt; Dubletten- und Werkbeziehungen bleiben außerhalb der Annahme |
| Messbarkeit und Enthaltung | `TEILWEISE`: getrennte Metriken und Enthaltung sind definiert; Nutzerreview und End-to-End-Abdeckung fehlen | `BELEGT` für Preflight-Fehlerkosten, kritische Fehlfreigabe, Folgeaktion und Reproduzierbarkeit; Nutzeroberfläche bleibt offen |
| Datenschutz, Netzwerk und Ressourcen | `TEILWEISE`: enge Experimentprofile sind belegt; das Profil des zusammengesetzten Ablaufs fehlt | `BELEGT` für den angenommenen Preflight: Eingänge unverändert, Netzwerk und Schreibwirkung null, Ressourcen und Abbruch begrenzt |
| Fachsystemkopplung und Ausstieg | `TEILWEISE`: unterstützter CLI-Weg und pfadbereinigte Projektion sind eng begrenzt; Copy-on-read bleibt Calibre-spezifisch | `BELEGT`: kein führendes Fachsystem erforderlich; der Ablauf kann vor jedem tieferen Adapter stoppen |
| Austauschbarkeit der Werkzeuge | `TEILWEISE`: Rohberichte bleiben getrennt; eine Produktalternative zum erprobten Ace-Profil ist offen | `BELEGT` an der Annahmegrenze, weil kein tiefes Werkzeug erforderlich ist; konkrete spätere Werkzeugadapter bleiben offen |
| Schwerster Restfehler | übersehener schwerer Bestandsbefund bei nur teilweise erfasstem Bestand | gefährlicher oder unvollständiger Eingang wird zu früh freigegeben; EXP-0006 belegt für den engen Preflight die fail-closed Reaktion ohne kritische Fehlfreigabe |
| Gate-Reife | `NICHT ALS ERSTER ABLAUF ANGENOMMEN` | `ANNEHMBAR ALS BEGRENZTER ERSTER READ-ONLY E-BOOK-ABLAUF` |

## Prüfung der Gate-Voraussetzungen

| Voraussetzung aus dem Erkundungsplan | Befund |
|---|---|
| Nutzerfrage und vollständiger Ablauf | S2 ist vom expliziten Eingang bis zur sichtbaren nächsten Aktion vollständig beschrieben und begrenzt; die Produktimplementierung folgt erst in einem eigenen Arbeitsgegenstand |
| Messbare Akzeptanzkriterien | S2-Preflight, Fehlerkosten, Enthaltung, Reproduzierbarkeit und Unverändertheit sind beschrieben und in EXP-0006 gemessen |
| ausreichende TEST-0001-Fassung | 26 `Kern`-Fälle und die 11 gebundenen Preflight-Zeilen reichen für den angenommenen dünnen Ausschnitt; `Ausbau` bleibt späteren Ästen vorbehalten |
| relevante Experimentergebnisse | EXP-0002 bis EXP-0006 liegen einschließlich Negativbefunden versioniert vor |
| Objekt- und Adaptergrenzen | Snapshot, Rohbeobachtung, Klassifikation, Folgeaktion und spätere Adapter sind für die Planung trennbar; konkrete Produktverträge bleiben Aufgabe des nächsten Arbeitsgegenstands |
| Datenschutz-, Netzwerk- und Ressourcenprofil | für den angenommenen Preflight durch EXP-0005 und EXP-0006 belegt; ein späteres Produktprofil muss erneut qualifiziert werden |
| Ausstiegswege wesentlicher Abhängigkeiten | S2 ist an der Annahmegrenze fachsystem- und tiefwerkzeugneutral und kann fail-closed stoppen |
| Vergleich mehrerer Produktzuschnitte | S1 und S2 wurden gegen dieselben Voraussetzungen, Fehlerfolgen und Kopplungskosten verglichen |
| Auswahl oder Vertagung | S2 ist innerhalb der dokumentierten Annahmegrenze ausgewählt; GATE-0001 ist `done` |

Damit ist das Auswahl-Gate abgeschlossen. Die Implementierung und ihre
Abnahme sind ausdrücklich noch offen.

## Historie: erste Auswertung und genau eine Evidenzwelle

Die erste Auswertung vertagte beide Kandidaten. S1 besaß die breitere Kette
aus EXP-0002 bis EXP-0005, aber keinen vollständigen Nutzerablauf und bereits
Calibre- sowie Ace-Kopplung. S2 hatte den geringeren Kopplungs- und
Ausstiegsaufwand, aber noch keinen empirisch zusammenhängenden
sicherheitskritischen Fähigkeitsentscheid.

Daraufhin wurde genau eine weitere Evidenzwelle verfolgt: EXP-0006,
**read-only Eingangstriage-Preflight für Format- und
Fähigkeitsklassifikation**. Profil, Eingänge, erwartete Ergebnisse und
Stopkriterien wurden vor den gewerteten Wiederholungen versioniert. Der
Versuch hat keinen Produktcode, keine UI, keine Persistenz, keinen Writer und
keine reale oder private Datei eingeführt.

Die Neubewertung ersetzt nicht diesen historischen Befund. Sie verwendet das
danach versionierte Ergebnis, um den bereits vorab festgelegten ersten
zulässigen Ausgang anzuwenden: S2 annehmen, wenn der Preflight die kritische
Lücke schließt und der kleinste vollständige read-only Ablauf begrenzbar ist.

## Nächster getrennter Schritt

WI-0004 hat in einer eigenen Planungs-Wave Akzeptanz, Vertragsgrenzen und
Abnahme für einen dünnen read-only Prototyp des angenommenen Ablaufs
konkretisiert und ist `accepted`. Produktcode darf erst in einer neuen Wave
vom kanonischen Plan-Merge beginnen.

WI-0004 darf GATE-0001 nicht stillschweigend um tiefe
Formatprüfung, Calibre, Dubletten, Metadaten, Routing, Persistenz, UI oder
Writes erweitern. Solche Äste bleiben getrennte, reversible Entscheidungen.
