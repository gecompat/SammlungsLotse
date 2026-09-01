# EXP-0017: Synthetische Downstream-Isolation des tiefen EPUB-Pfads qualifizieren

Status: ACCEPTED — NOT EXECUTED

Stand: 2026-09-01

Artifact: EXP-0017

## Zweck

EXP-0017 prüft ausschließlich mit synthetischen EPUBs, ob der exakt
gebundene und unveränderte WI-0005-Downstream-Pfad die in EXP-0016
unterschiedenen Navigations-, Ressourcen- und Täuschungskontexte unter seinen
tatsächlichen Isolations- und Fehlergrenzen verarbeitet. Das Experiment
schließt die Evidenzlücke zwischen syntaktischer Klassifikation und tiefer
read-only Werkzeugausführung. Es wählt keine Produktregel.

`Ohne Produktcodeänderung` bedeutet hier: Der Experimentharness ruft den
vorhandenen `EpubCheckProvider` mit seinem vorhandenen `PodmanExecutor`, der
vorhandenen task-privaten Materialisierung und dem vorhandenen exakten
Laufzeitprofil auf. Unter `src/sammlungslotse/` wird nichts ergänzt oder
geändert. Der Harness umgeht nur innerhalb des Experiments kontrolliert das
unveränderte WI-0004-Anwendungsgate, damit der dahinterliegende Pfad isoliert
beobachtet werden kann. Diese Umgehung wird nicht zu einer Produktoberfläche.

## Auswahl und Hypothesen

Der Nutzer hat in GATE-0019 ausdrücklich Option A ausgewählt. EXP-0017 bindet
vor der Ausführung folgende Hypothesen:

1. Der tatsächliche WI-0005-Executor besitzt für jeden Matrixlauf effektiv
   `network=none`; keine synthetische Referenz erreicht die lokale
   Messkanarie.
2. Die EXP-0016-Kontextklassifikation bleibt für alle zwölf ausgewählten
   Fälle korrekt. EPUBCheck-Befunde werden daneben als getrennte
   Provider-Evidenz bewahrt und nicht in eine Sicherheitsklassifikation
   umgedeutet.
3. Normalfälle wiederholen sich semantisch identisch. Timeout, Outputgrenze,
   Isolationsdrift, ungültiger Bericht oder Cleanupfehler bleiben fail-closed
   und erzeugen keine positive Folgeentscheidung.

Ein Bestehen belegt weder Zielvertrauen noch Nutzerabsicht, allgemeine
Lesesystemsicherheit, vollständige EPUB-Variantenabdeckung oder die
Zulässigkeit einer Review-Lockerung.

## Gebundener Downstream-Stand

Die Ausführungswave bindet vor dem ersten Hauptlauf mindestens:

- das saubere Git-Preimage und grüne Pflichtchecks auf exakt diesem Commit;
- alle Python-Dateien unter `src/sammlungslotse/ebook_intake/`, ohne sie zu
  verändern;
- `tools/run_ebook_intake.py`, `tools/qualify_ebook_deep_profile.py` und den
  neuen EXP-0017-Runner;
- das vollständige EXP-0016-Fallmanifest und dessen eingefrorenen Parser;
- das neue EXP-0017-Fallmanifest und den deterministischen EPUB-
  Materialisierer;
- WI-0005-Profil
  `wi-0005-epubcheck-5.3.0-temurin-21.0.12.1+1-podman-linux-amd64/v1`;
- EPUBCheck `5.3.0`, Podman Client und Server `6.1.0` auf Linux/amd64 sowie
  Image-ID
  `sha256:d8143e59b2c478e0056200a3529b9beb74737885863c22097b198a9c0c92974e`;
- die tatsächlichen Profilgrenzen für Netzwerk, Benutzer, Capabilities,
  Root-Dateisystem, Input-Mount, PID, CPU, RAM, Swap, Umgebung, Zeit,
  stdout, stderr, Rohbericht und tmpfs-Output.

Ein abweichender Provider, eine abweichende Version, Image-ID, Runtime,
Plattform, Produktdatei oder Profilgrenze bricht vor dem Hauptlauf ab. Es
erfolgt kein Download, Build, Update oder automatischer Ersatz.

## Vorab gebundene Fallmatrix

Das Manifest enthält genau zwölf Fälle, abgeleitet aus bereits gebundenen
EXP-0016-Orakeln:

| Gruppe | EXP-0016-Fälle | Gebundene Bedeutung |
|---|---|---|
| S3-Navigation | `usr-001`, `usr-004`, `usr-006`, `usr-007` | XHTML-Link, EPUB-Navigation, Entity-Variante und SVG-Link; S3-Literal bleibt `candidate_continue_deep_read_only` |
| Ressourcen und Aktivität | `pkg-001`, `res-002`, `act-001`, `res-009` | optionaler Package-Link, Bildressource, Scriptquelle und CSS-URL; S3-Literal bleibt `review` |
| Mehrdeutig und täuschend | `amb-001`, `amb-003`, `amb-006`, `amb-009` | gemischtes `rel`, Kommentar, fremdes Element und gemischter Link-/Bildkontext; S3-Literal bleibt `abstain` |

Jeder Fall wird als kleines vollständiges EPUB mit festen ZIP-Zeitstempeln,
deterministischer Reihenfolge, `mimetype`, Containerdatei, Package-Dokument
und nur den erforderlichen Content-Dokumenten materialisiert. Das Manifest
bindet Dokumentart, Snippet, erwartete EXP-0016-Kontextklasse,
Schemagruppierung, S3-Aktion, Einbettungsstelle und verbotene Wirkungen.

Absichtlich mehrdeutige oder nicht konforme Konstrukte dürfen
EPUBCheck-Befunde erzeugen. Konformität ist kein methodisches Muss. Ein
Werkzeugausfall oder unvollständiger Bericht wird dagegen nicht als
erfolgreiche Verarbeitung umgedeutet.

## Threat Model und Kontrollen

| Bedrohung | Kontrolle | Gebundene Evidenz |
|---|---|---|
| Remote-Link oder Ressource wird aktiviert | alle Remoteziele zeigen auf eine kurzlebige lokale Messkanarie; der exakte Executor bleibt `network=none` | genau eine getrennte positive Sensitivitätsverbindung vor Reset, danach null Deep-Path-Verbindungen |
| Parsersemantik wird verwechselt | EXP-0016 klassifiziert das gebundene Snippet; EPUBCheck liefert nur getrennte Konformitätsevidenz | null Kontext- oder S3-Orakelmismatches; Providerzustände und Originalcodes separat |
| Isolationsprofil driftet | Container wird vor Start über den vorhandenen Executor zurückgelesen | Netzwerk, Mounts, UID, Capabilities, Privilegien, Root, tmpfs, Ressourcen und Befehl entsprechen dem Profil |
| Prozess hängt | ausschließlich für die Negativprobe wird nur das Timeout in einer In-Memory-Kopie verschärft | `not_assessed`, Zustand `timeout`, Container und Task vollständig entfernt |
| Output wächst unkontrolliert | getrennte lokale tmpfs-Grenzprobe mit demselben Image und denselben Isolationsschaltern | 4 MiB Versuch scheitert an der gebundenen 2-MiB-Outputgrenze; Probecontainer entfernt |
| Pfade, URLs oder Rohinhalt gelangen in Evidenz | Ergebnis enthält nur vorab erlaubte Aggregate und öffentliche Providercodes | pfadfreier, URL-freier Ergebnisvertrag ohne Rohberichte oder Meldungstexte |
| Eingang oder Bestand wird verändert | EPUB-Bytes existieren nur im begrenzten Task und werden vor/nach jedem Lauf gehasht | identische Hashes, leere Taskwurzel, null Produkt-, Persistenz- oder Bestandswirkung |
| Experiment wird zur Produktfreigabe umgedeutet | direkter Harness-Aufruf und S3-Literal bleiben ausdrücklich experimentell | WI-0004-Gate und Produktcode unverändert; neues Ergebnisgate unabhängig vom Befund |

Die Messkanarie ist ein lokales, kurzlebiges Instrument ohne private Daten:
Sie lauscht nur während des Experiments auf einem zufälligen Host-Port. Eine
getrennte lokale Kontrollverbindung belegt die Zählfunktion; danach wird der
Zähler auf null gesetzt. Der Ergebnisbericht enthält weder Port noch Host,
URL, Payload oder Zeitstempel. Die Kanarie und ihre Kontrollverbindung sind
keine externe Anfrage und kein Produktbestandteil.

Die Kanarie ist kein Kernel-Syscall- oder Paketmitschnitt. Der
Netzwerk-Egress-Nachweis beruht zusätzlich und primär auf dem effektiven,
vor Prozessstart zurückgelesenen Podman-Netzwerkmodus `none`. Diese Grenze
und die fehlenden Kanarientreffer belegen nur den gebundenen Executorstand.

## Ablauf

1. Die Auswahl- und Vertragswave wird validiert, gemergt und auf
   `origin/main` post-merge geprüft.
2. Eine neue isolierte Ausführungswave implementiert nur Manifest,
   Materialisierer, Runner und fokussierte Tests außerhalb von
   `src/sammlungslotse/`.
3. Profil, Runtime, Image, Produkthashes, Fallmanifest, Runner und
   Ergebnisvertrag werden auf einem sauberen Commit geprüft.
4. Der vollständige lokale Repositorytest läuft einmal auf diesem stabilen
   Preimage. Danach müssen beide GitHub-Pflichtchecks auf exakt dem Commit
   grün sein.
5. Der bestätigte Hauptlauf materialisiert die zwölf EPUBs einmal und führt
   jeden Fall in genau zwei Wiederholungen über den unveränderten tiefen Pfad;
   zusammen entstehen genau 24 Providerläufe. Isolation, Kanarie, Timeout und
   Outputgrenze werden im selben gebundenen Lauf geprüft.
6. Ein historischer Validator bindet Manifest, Runner, unveränderten
   Produktstand und Ergebnis an das Preimage, ohne Container- oder
   Experimentläufe später zu wiederholen.
7. Ein neues getrenntes Ergebnisgate wird unabhängig vom Ausgang geöffnet.

Ein fehlgeschlagener oder abgebrochener Hauptlauf wird nicht partiell
fortgesetzt. Nach einer Implementierungskorrektur ist ein neues sauberes
Preimage mit neuer CI erforderlich; nur ein danach vollständig neu
ausgeführter Lauf darf als Ergebnis gelten.

## Ergebnisvertrag

Das versionierte Ergebnis enthält ausschließlich:

- Schema, Artifact-ID, Preimage-Commit und Hashbindungen;
- Fallzahl `12`, Wiederholungen `2` und Providerläufe `24`;
- Gruppenzahlen `4/4/4`;
- Zahl der EXP-0016-Kontext-, Schema- und S3-Orakelmismatches;
- je Wiederholung aggregierte Ausführungszustände, Assessments,
  Providercode-Häufigkeiten, Rohbericht-Gesamtgröße und maximale
  Einzelberichtgröße;
- semantische Wiederholungsidentität und getrennte Parserdifferenzaggregate;
- effektive Isolationswerte ohne Hostdetails;
- Kanarien-Sensitivitäts- und Deep-Path-Trefferzahlen;
- Timeout-, Output-, Eingangs-, Task- und Container-Cleanup-Aggregate;
- die unten definierten Akzeptanzwerte, Status und ausschließlich boolesche
  Wirkungsgrenzen.

Nicht versioniert werden EPUB-Dateien, Rohberichte, stdout, stderr,
Meldungstexte, URLs, Ports, Container- oder Tasknamen, Hostdaten, absolute
Pfade oder Einzelereignisse. Temporäre Diagnoseartefakte bleiben unter neuen
engen Pfaden in `C:\rep\tmp`; das gebundene Ergebnis entsteht zunächst unter
`C:\rep\artifacts` und wird erst nach Datenschutz- und Vertragsprüfung in
den Repository-Ergebnisvertrag übernommen.

## Methodische Akzeptanzkriterien

EXP-0017 ist methodisch nur bestanden, wenn alle folgenden 18 Kriterien
erfüllt sind:

1. sauberes Preimage und beide Pflichtchecks sind an exakt denselben Commit
   gebunden;
2. Profil, Provider, Runtime, Plattform, Image, Produktdateien, Manifest und
   Runner entsprechen vollständig dem Preimage;
3. das Manifest enthält genau zwölf Fälle mit exakt vier Fällen je Gruppe;
4. alle EPUBs werden deterministisch und innerhalb der gebundenen Größen-
   und ZIP-Grenzen materialisiert;
5. EXP-0016-Kontext, Schema und S3-Aktion stimmen für 12/12 Fälle mit dem
   vorab gebundenen Orakel überein;
6. genau zwei Wiederholungen und 24 tatsächliche Providerläufe finden statt;
7. jeder Matrixlauf startet den unveränderten Providerprozess, verifiziert
   Isolation und liefert einen vollständigen begrenzten Bericht;
8. beide Wiederholungen sind nach Entfernung technischer Zufallswerte
   semantisch identisch;
9. Parser- und Providerbefunde bleiben getrennt und alle Providercodes
   verlustfrei aggregiert;
10. die Messkanarie erkennt vor Reset genau eine positive Kontrollverbindung;
11. alle 24 Deep-Path-Läufe erzeugen zusammen null Kanarientreffer;
12. die effektive Containerisolation stimmt einschließlich `network=none`
   vollständig mit dem Profil überein;
13. die Timeoutprobe endet fail-closed als `not_assessed` und bereinigt Task
   sowie Container;
14. die Outputprobe weist den 4-MiB-Versuch an der 2-MiB-Grenze ab und
   entfernt den Probecontainer;
15. alle Eingangsbytes bleiben unverändert und jede Taskwurzel ist am Ende
   leer;
16. Ergebnis und Diagnose sind pfadfrei, URL-frei, größenbegrenzt und
   enthalten keine privaten oder rohen Inhalte;
17. Produktcode, WI-0004-Gate, Profil, Fachsystem und Sammlung bleiben
   unverändert; externe Netzwerk-, Persistenz- und Bestandswirkungen sind
   null;
18. das Ergebnis öffnet ein neues Gate und wählt keine Produktfortsetzung.

Bereits ein fehlender Pflichtcheck, Preimage- oder Imageunterschied,
Orakelmismatch, unvollständiger Lauf, Kanarientreffer, Isolationsdrift,
nicht fail-closed beendeter Grenzfall, Cleanuprest, Pfad-/URL-Leak oder
Produktänderung ergibt keinen methodischen `pass`.

## Harte Grenzen

- ausschließlich synthetische, zur Laufzeit erzeugte EPUBs;
- keine erneute Verwendung der drei privaten Dateien oder anderer privater
  Medien;
- keine Änderung unter `src/sammlungslotse/`;
- kein neuer Provider, keine neue Runtime, kein Image-Build und kein
  Download;
- keine Änderung am WI-0005-Profil oder WI-0004-Review-Gate;
- keine öffentliche CLI-, REST-, Browser-, Agent- oder Persistenzfläche;
- keine Interpretation von EPUBCheck als Zielvertrauens-, Inhalts-,
  Accessibility- oder Gesamtsicherheitsurteil;
- keine Review-Lockerung, automatische Linkaktivierung, Reparatur,
  Transformation, Suche, Bestandsaktion oder Writer-Fähigkeit.

## Abbruch- und Fortsetzungsregel

Fehlen Podman, das exakte Image oder eine gebundene Voraussetzung, bleibt
EXP-0017 `accepted` und `not executed`. Bei Isolationsdrift, Kanarientreffer,
inkompletter Matrix, Cleanupfehler oder Produktänderung lautet das Ergebnis
nicht `pass`; es wird keine Regel nachjustiert, um den Befund zu verdecken.

Nach dem historisch gebundenen Ergebnis bewertet ein neues getrenntes Ergebnisgate:
weitere Evidenz, Review-beibehaltende Erklärbarkeit, eine mögliche
Produktregel, konservatives Beibehalten oder Pausieren. EXP-0017 selbst
autorisiert keine dieser Fortsetzungen.
