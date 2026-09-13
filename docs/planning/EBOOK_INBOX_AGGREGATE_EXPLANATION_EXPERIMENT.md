# EXP-0018: Synthetische Erklärbarkeit von E-Book-Eingangsordneraggregaten prüfen

Status: ACCEPTED — HARNESS PREPARED, EMPIRICAL RUN NOT EXECUTED

Stand: 2026-09-13

Artifact: EXP-0018

## Zweck

EXP-0018 prüft produktcodefrei, ob die bestehenden pfadfreien WI-0016-
Ordnerberichte für eine begrenzte synthetische Matrix vollständig und
deterministisch in manuelle Prioritätsklassen zusammengefasst werden können.
Die Klassen sind ausschließlich Experimentauswertung: Sie ändern weder die
öffentliche CLI noch `next_action`, `review` oder das Deep-Read-Gate.

## Gebundene Ausgangslage

- WI-0016 inventarisiert genau einen expliziten Ordner read-only und ohne
  automatische tiefe Prüfung.
- WI-0004 und WI-0006 liefern die bestehenden Einzel- beziehungsweise
  Mehrdatei-Entscheidungen.
- TEST-0001 liefert die einzigen EPUB-Eingänge; eine minimale synthetische
  PDF-Datei dient nur als bereits unterstützter Nicht-EPUB-Fall.
- Der Experimentrunner liegt außerhalb von `src/sammlungslotse/` und ruft
  ausschließlich `tools/run_ebook_intake.py --json --input-directory` auf.

## Vorab gebundene Matrix

| Fall | Synthetische Eingänge | Erwartete Klasse |
| --- | --- | --- |
| `continue_only` | stabiler EPUB | `review_deep_read_only` |
| `review_only` | EPUB mit Remote-Referenz | `manual_review_required` |
| `unsupported_only` | PDF | `no_supported_epub` |
| `mixed` | stabiler EPUB, Review-EPUB, PDF | `manual_review_required` |
| `candidate_limit` | 33 minimale EPUB-Dateien | `inventory_incomplete` |
| `unavailable` | fehlender Ordner | `inventory_unavailable` |

Die Zuordnung ist ausschließlich eine Erklärung der vorhandenen Ergebnisse:

- `inventory_unavailable` für `status=unavailable`;
- `inventory_incomplete` für `status=limit_exceeded` oder nicht vollständiges
  Inventar;
- `manual_review_required`, sobald ein Einzelbericht `next_action=review`
  ausweist;
- `review_deep_read_only`, sobald ausschließlich
  `continue_deep_read_only`-Eingänge vorliegen;
- `no_supported_epub`, sobald keine EPUB-Triage möglich ist.

Andere Kombinationen führen fail-closed zu `manual_review_required`; daraus
folgt keine Freigabe oder Ausführung einer Folgeaktion.

## Methodische Akzeptanzkriterien

Der Nachweis ist nur bestanden, wenn:

1. genau die sechs vorab gebundenen Fälle je zweimal über den tatsächlichen
   JSON-Ordner-CLI-Weg laufen;
2. beide Wiederholungen jedes Falls bytegleich sind;
3. jede erwartete Prioritätsklasse zutrifft und keine unbekannte Klasse
   entsteht;
4. die Auswertung nur bereits sichtbare Status-, Zähler- und
   `next_action`-Werte verwendet;
5. sämtliche stdout-Berichte pfad- und namensfrei bleiben;
6. alle TEMP-Eingänge aus TEST-0001 oder minimalen synthetischen Bytes
   entstehen und nach dem Lauf entfernt sind;
7. kein Deep-Provider, Netzwerk, Persistenz, Fachsystemzugriff, Writer oder
   Produktcode ausgeführt beziehungsweise geändert wird.

## Ergebnisgrenzen

Ein bestandener Nachweis belegt ausschließlich die sechs gebundenen
synthetischen Situationen. Er belegt weder eine allgemeine Qualität realer
Ordner noch eine automatische Priorisierung, keinen Import und keine
Lockerung des manuellen Reviews. Ein Ergebnisgate entscheidet erst nach dem
Nachweis, ob eine neue Produktoberfläche überhaupt sinnvoll ist.

## Aktueller Ausführungsstand

Der produktcodefreie Runner, die gebundene Matrix und fokussierte Harness-
Tests sind vorbereitet. Ein lokaler Charakterisierungslauf bestätigte die
sechs erwarteten Klassen und die vollständige Bereinigung; er ist kein
empirischer Ergebnisnachweis. Die Ausführung mit eingechecktem Ergebnis bleibt
bis zu einem sauberen Preimage und den dafür erforderlichen grünen
Repository-Checks `not executed`.
