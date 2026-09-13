# EXP-0018: Synthetische Erklärbarkeit von E-Book-Eingangsordneraggregaten prüfen

Status: DONE — EXECUTED, 7/7 METHOD CRITERIA PASSED

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

## Ausführungsergebnis

Das saubere Preimage `da9f4b3f20e39c615bf9a56a70bfbd5635999ac8` bestand die
beiden erforderlichen GitHub-Checks `repository-quality` und
`registry-integrity`. Danach wurden alle sechs Fälle je zweimal über den
tatsächlichen JSON-Ordner-CLI-Weg ausgeführt. Alle sieben methodischen
Akzeptanzkriterien bestanden: die Wiederholungen waren bytegleich, jede
erwartete Klasse trat ein, Ausgaben blieben pfad- und namensfrei, Quellen
blieben unverändert und der flüchtige Taskbereich wurde vollständig bereinigt.
Netzwerk, Deep-Provider, Persistenz, Fachsystemzugriff, Writer und
Produktcodewirkung fehlten. Der pfadfreie Nachweis steht unter
`experiments/ebook/exp-0018/result.json`.

Das Ergebnis qualifiziert keine neue Produktoberfläche und lockert weder
`review` noch das Deep-Read-Gate.
