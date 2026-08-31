# EXP-0012: Begrenzte Calibre-Kandidatensuche produktcodefrei qualifizieren

Status: ACCEPTED — NOT EXECUTED

Stand: 2026-08-31

Artifact: EXP-0012

## Auswahl und Zweck

Der Nutzer hat in GATE-0014 ausdrücklich Option A ausgewählt. Dieses
Experiment prüft ergebnisoffen, ob unterstützte read-only Calibre-Suchen für
genau ein Eingangs-EPUB in genau einer synthetischen Bibliothek eine kleine,
hart begrenzte und erklärbare Kandidatenmenge liefern können. Erst danach wird
jeder Kandidat getrennt über den unveränderten WI-0011-Vertrag bewertet.

Die Auswahl autorisiert diesen Experimentvertrag und seine getrennte
Ausführung nach dem Merge. Sie autorisiert keinen Produktalgorithmus, keine
vollständige Dublettenprüfung, keine Persistenz und keinen Produktcode.

## Gebundene Ausgangslage

- WI-0007 bindet Calibre 9.13.0, das exakte Linux/amd64-Image und eine
  task-private Copy-on-read-Bibliothek ohne Netzwerk.
- EXP-0008 bindet die unterstützte Einzelrecord-EPUB-Übergabe.
- WI-0011 bewertet genau ein Eingangs-EPUB gegen genau einen expliziten
  Calibre-Kandidaten und bleibt standardmäßig V1.
- WI-0013 V2 bleibt ein ausdrückliches Opt-in und wird nicht zum Default.
- TEST-0001 und eine neue ausschließlich synthetische Calibre-Bibliothek sind
  die einzigen Eingaben des reproduzierbaren Abnahmenachweises.

Auf ausdrücklichen Nutzerhinweis wird zusätzlich ein lokaler privater
Praxissmoke aus höchstens drei einzelnen EPUBs aus einer nur zur Laufzeit
übergebenen Quelle ausgeführt. Die Dateien werden ausschließlich read-only
ausgewählt, einzeln in einen task-privaten Tempbereich kopiert und dort zu
einer task-privaten Calibre-Bibliothek materialisiert. Weder Dateien noch
Titel, Autoren, Quellpfade, Hashes, Calibre-Metadaten oder Rohoutputs gelangen
in Git. Der Lauf darf nur eine anonyme Aggregatzusammenfassung liefern,
entscheidet kein Akzeptanzkriterium und wird einschließlich aller Kopien
bereinigt.

Die offizielle Calibre-Suchschnittstelle dokumentiert feldgebundene Suchen,
unter anderem für `title`, `author` und `identifiers`. Die lokal aus dem exakt
gebundenen Image erhobene `calibredb search --help`-Ausgabe bestätigt eine
kommagetrennte ID-Ausgabe und `--limit`; `calibredb list --help` bestätigt
maschinenlesbare Ausgabe, `--search` und die minimale Feldprojektion. Diese
Schnittstellenhinweise sind Voraussetzungen, nicht Ergebnisnachweise.

Primärquellen:

- <https://manual.calibre-ebook.com/gui.html#the-search-interface>
- <https://manual.calibre-ebook.com/generated/en/calibredb.html>

## Vorab gebundene Suchstrategien

### V1 — Exakter typisierter Identifier

Query: `identifiers:=<type>:=<value>`.

Fehlt im Eingangsfall ein geeigneter typisierter Identifier, ist V1
`not_applicable`. Es gibt keinen stillen Fallback auf Titel oder Autor.

### V2 — Exakter Titel plus exakter Autor

Query: `title:"=<title>" and author:"=<author>"`.

Titel und Autor müssen beide im Eingangsmanifest gebunden sein. Fehlende
Felder machen V2 `not_applicable`.

### V3 — Feldgebundener Titel- und Autor-Contains

Query: `title:"<title>" and author:"<author>"`.

V3 ist ausdrücklich keine unscharfe Suche, kein Ranking und keine
Volltextsuche. Fehlende gebundene Felder machen die Variante
`not_applicable`.

## Synthetische Aufgaben und Oracles

Das Ausführungsmanifest bindet vor der Messung genau acht Aufgaben:

1. eindeutiger Identifier derselben Edition;
2. wiederverwendeter Identifier mit Inhaltskonflikt;
3. eindeutiger Titel und Autor ohne Identifier;
4. Titelkollision bei verschiedenem Autor;
5. Autorenkollision bei verschiedenem Titel;
6. gleicher Titel und Autor bei mehreren Editionen;
7. Interpunktions- oder Zeichenvariante;
8. kein Treffer.

Für jede anwendbare Strategie nennt das Manifest den exakten Query-String,
die erwarteten relevanten IDs und ausdrücklich erlaubte Zusatzkandidaten.
Diese Oracles dürfen weder an `calibredb` noch an WI-0011 übergeben werden.

## Ausführungs- und Evidenzvertrag

Für jede anwendbare Aufgabe und Strategie gilt in genau dieser Reihenfolge:

1. `calibredb search --with-library /library --limit 5 <query>` wird im
   gebundenen, netzwerklosen Calibre-Container auf der task-privaten Kopie
   ausgeführt.
2. Erlaubt ist nur eine leere oder kommaseparierte Folge positiver IDs. Die
   IDs werden dedupliziert und numerisch sortiert.
3. Fehler, Timeout, ungültige Ausgabe, mehr als fünf IDs oder ein
   Output-Overrun führen fail-closed zu einem sichtbaren Methodenfehler.
4. Für jede ID wird über `calibredb list --for-machine` nur
   `title,authors,languages,formats,identifiers` projiziert. Formatangaben
   bleiben pfadfrei.
5. Jeder Kandidat wird danach einzeln und unverändert über
   `tools/run_ebook_calibre_identity.py --json` bewertet. Such- und
   Identitätsevidenz bleiben getrennte Objekte.
6. Genau fünf Kandidaten setzen `candidate_limit_reached=true`; daraus folgt
   ausdrücklich keine Vollständigkeitsbehauptung.

Jede der acht Aufgaben wird mit allen drei Strategien in genau zwei
Wiederholungen ausgeführt. Nicht anwendbare Kombinationen bleiben sichtbar
und werden nicht als Treffer oder Fehler umgedeutet.

## Harte Grenzen

- genau eine synthetische Calibre-Bibliothek pro Lauf;
- genau ein Eingangs-EPUB pro Aufgabe;
- genau drei Strategien, acht Aufgaben und zwei Wiederholungen;
- höchstens fünf Kandidaten je Suchlauf und höchstens zwölf Bibliotheksrecords;
- höchstens 512 UTF-8-Bytes je Query;
- höchstens 128 KiB je stdout- oder stderr-Strom;
- höchstens 30 Sekunden je Werkzeugschritt;
- unveränderte WI-0007-Grenzen für Netzwerk, Root-Dateisystem, Benutzer,
  Prozesse, CPU und RAM;
- keine reale oder private Bibliothek, kein Netzwerk, keine direkte
  `metadata.db`-Nutzung, keine Persistenz und keine Bestandsänderung im
  reproduzierbaren Abnahmenachweis; ausgenommen ist nur der ausdrücklich
  getrennte lokale Drei-EPUB-Praxissmoke mit denselben Laufzeitgrenzen;
- keine Änderung unter `src/sammlungslotse/` und keine neue öffentliche CLI-,
  API-, UI-, Agent- oder Writerfläche.

## Messgrößen

Pro Strategie werden getrennt ausgewiesen:

- anwendbare und tatsächlich ausgeführte Suchläufe;
- Recall gegen die vorab gebundenen relevanten IDs und sichtbare Misses;
- Zusatzkandidaten, Precision und Kandidatenanzahl;
- Erreichen der Fünfergrenze;
- nachgelagerte WI-0011-Stufen je Kandidat;
- kritische False-Same-Fälle, Enthaltungen und Restunsicherheit;
- Gleichheit beider Wiederholungen;
- Hashes und Unverändertheit von Quelle, Fixtures und Bibliothekskopie;
- vollständiges Task- und Container-Cleanup.

Eine Strategie wird als `eligible_with_tradeoffs`, `not_qualified` oder
`inconclusive` klassifiziert. Das Experiment darf mehrere oder keine
qualifizierte Strategie liefern; es bestimmt keinen Sieger und kein Ranking.

## Methodische Akzeptanzkriterien

Das Experiment ist nur `pass`, wenn alle folgenden 16 Kriterien erfüllt sind:

1. exaktes WI-0007-Profil, Image und Git-Preimage sind gebunden;
2. die Matrix enthält genau drei Strategien, acht Aufgaben und zwei Läufe;
3. alle Medien, Metadaten und Oracles sind synthetisch und vorab gehasht;
4. nur die erlaubten `calibredb search`- und `list`-Wege werden verwendet;
5. jede Kandidatenmenge bleibt bei höchstens fünf IDs;
6. Fehler und Grenzerreichung bleiben sichtbar;
7. die Projektion enthält nur die gebundenen minimalen Felder;
8. jeder Kandidat durchläuft getrennt den unveränderten WI-0011-Vertrag;
9. Recall, Misses, Zusatzkandidaten und Precision werden ausgewiesen;
10. Such- und Identitätsevidenz bleiben getrennt;
11. kritische False Same werden ausdrücklich gezählt;
12. beide Wiederholungen sind semantisch identisch;
13. Eingangs-EPUBs, Quellfixtures und Bibliotheksquelle bleiben unverändert;
14. Netzwerk, direkte Datenbanknutzung, Persistenz und Produktcode fehlen;
15. alle eingecheckten Resultate sind pfadfrei;
16. Taskmaterial, Container und temporäre Bibliothekskopien sind bereinigt.

Der private Praxissmoke ist zusätzlich erfolgreich, wenn höchstens drei
EPUB-Kopien eine task-private Bibliothek bilden, jede gebundene read-only
Suche begrenzt ausgeführt wird, kein privater Wert in eingecheckter Evidenz
erscheint, die Quellen unverändert bleiben und sämtliche Kopien bereinigt
werden. Sein Fehlschlag bleibt sichtbar, ändert aber nicht rückwirkend den
synthetischen Methodenstatus.

## Ausführungsfolge

1. Diese Auswahl- und Vertragswave wird validiert, gemergt und auf
   `origin/main` post-merge geprüft.
2. Die Ausführung beginnt erst danach in einem neuen isolierten Worktree vom
   exakten neuen `origin/main`.
3. Manifest, Runner, synthetische Fixtures und Tests werden ohne Produktcode
   implementiert und als sauberes Preimage committed.
4. Erst gegen dieses Commit werden beide tatsächlichen Podman-Läufe erzeugt.
5. Ein historischer Validator bindet Resultat, Preimage und Runner dauerhaft.
6. Das Ergebnis öffnet ein neues getrenntes Ergebnisgate. Es autorisiert
   selbst bei `pass` keine Produktübernahme.

## Nicht-Ziele

- kein Produkt-Suchalgorithmus und kein Ranking;
- keine vollständige Dubletten- oder Bestandsprüfung;
- keine Auswahl einer Zielstrategie vor der Messung;
- keine automatische Same-, Import-, Routing- oder Schreibentscheidung;
- keine Erweiterung auf mehrere Bibliotheken;
- keine V1-Deprecation oder V2-Defaultänderung.
