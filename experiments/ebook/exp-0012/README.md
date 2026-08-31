# EXP-0012 Ausführung

Status: PREIMAGE IMPLEMENTED — RESULT NOT YET GENERATED

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
