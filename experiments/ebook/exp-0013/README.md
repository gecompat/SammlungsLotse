# EXP-0013 Ausführung

Status: READY — PREIMAGE NOT EXECUTED

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_PRIVATE_WI0011_NONCOMPLETION_DIAGNOSTIC_EXPERIMENT.md`.

Enthalten sind zunächst:

- `execution-profile.json`: exakte Eingangs-, Laufzeit-, Kontroll- und
  Ausgabegrenzen;
- dieser Ausführungshinweis.

`result.json` darf erst nach einem sauberen Preimage-Commit und nur durch den
gebundenen privaten Hauptlauf entstehen. Er enthält ausschließlich die
gemeinsame pfadfreie Aggregation; private Einzelwerte oder Rohberichte werden
nicht gespeichert.

## Prüf- und Ausführungsfolge

Profil und statische Bindungen:

```powershell
python tools/experiments/run_exp_0013.py --validate-profile
```

Die synthetischen Kontrollen führen drei tatsächliche WI-0011-Vergleiche auf
TEST-0001-Material aus und prüfen Aggregationsmatrix, Negativgrenzen,
Wiederholbarkeit, Quellunverändertheit und Cleanup:

```powershell
python tools/experiments/run_exp_0013.py --synthetic-controls
```

Der private Hauptlauf akzeptiert keine Quelle und keine Verzeichnissuche. Er
benötigt genau drei explizite Dateien und die ausdrückliche Bestätigung, dass
dies derselbe Eingangssatz wie im EXP-0012-Praxissmoke ist:

```powershell
python tools/experiments/run_exp_0013.py `
  --private-epub "<erste EPUB-Datei>" `
  --private-epub "<zweite EPUB-Datei>" `
  --private-epub "<dritte EPUB-Datei>" `
  --confirm-same-exp-0012-inputs
```

Die Locators werden weder ausgegeben noch versioniert. Ein gültiger
`not_qualified`-Befund ist eine abgeschlossene Diagnose mit bekannten
Nichtabschlussgründen und führt deshalb zu Exitcode 0. Ein unbekannter
Reason-Code bleibt sichtbar, setzt das Ergebnis auf `inconclusive` und führt
zu Exitcode 2. Ausführungs-, Sicherheits- oder Cleanupfehler erzeugen kein
Teilergebnis.

Ein Ergebnis eröffnet ein neues getrenntes Gate. EXP-0013 autorisiert keine
Produktkorrektur und keine Änderung unter `src/sammlungslotse/`.
