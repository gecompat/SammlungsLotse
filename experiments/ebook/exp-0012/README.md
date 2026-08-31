# EXP-0012 Ausführung

Status: DONE — EXECUTED, 16/16 METHOD CRITERIA PASSED

Der Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_CALIBRE_CANDIDATE_SEARCH_EXPERIMENT.md`.

Enthalten sind:

- `execution-profile.json`: exakte Laufzeit-, Befehls- und Ressourcengrenzen;
- `case-manifest.json`: zwölf synthetische Bibliotheksrecords, acht Aufgaben
  und die vorab gebundenen relevanten sowie erlaubten zusätzlichen IDs;
- `result.json`: erst nach dem sauberen Preimage-Commit erzeugte, pfadfreie
  Evidenz.

Der reproduzierbare Lauf verwendet ausschließlich TEST-0001-Material:

```powershell
python tools/experiments/run_exp_0012.py
```

Der auf ausdrücklichen Nutzerwunsch mögliche private Praxissmoke wird über
`--private-source` opt-in aktiviert. Er wählt höchstens drei kleine EPUBs,
kopiert sie nur in einen geschützten Task-Tempbereich und gibt ausschließlich
eine anonyme Aggregatzusammenfassung aus. Private Dateien, Metadaten, Pfade,
Hashes und Rohoutputs werden nicht eingecheckt; alle Kopien werden bereinigt.

Ein `pass` qualifiziert nur die Experimentmethode. Die Variantenklassifikation
und jede mögliche Produktfortsetzung werden getrennt in GATE-0015 bewertet.

## Ergebnis

Der commitgebundene synthetische Lauf auf Preimage `deddef0` bestand alle
16/16 Methodenkriterien in zwei semantisch identischen Wiederholungen:

- V1: `eligible_with_tradeoffs`, Recall 1,0, Precision 0,75, nur 3/8 Aufgaben
  anwendbar und ein erlaubter Zusatzkandidat bei wiederverwendetem Identifier;
- V2: `not_qualified`, Recall 0,8889, Precision 1,0 und ein gebundener Miss
  bei der Zeichen-/Teilwertvariante;
- V3: `eligible_with_tradeoffs`, Recall 1,0, Precision 0,9 und ein erlaubter
  Zusatzkandidat;
- null unerwartete Kandidaten, null kritische False Same und keine erreichte
  Fünfergrenze;
- Quellen, Bibliothekskopie und Fixtures unverändert, pfadfreies Ergebnis und
  vollständiges Task- sowie Container-Cleanup.

Der getrennte private Praxissmoke materialisierte genau drei EPUB-Kopien,
führte vier Suchläufe aus, bewahrte die Quellen und bereinigte alle Kopien.
Er blieb `not_qualified`, weil 0/3 nachgelagerte WI-0011-Vergleiche
`completed` erreichten. Nur diese anonyme Aggregation wurde berichtet; private
Dateien, Werte, Pfade, Hashes und Rohoutputs wurden nicht aufbewahrt.
