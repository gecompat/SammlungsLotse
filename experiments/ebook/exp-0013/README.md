# EXP-0013 Ausführung

Status: DONE — EXECUTED, METHOD PASSED; RESULT NOT_QUALIFIED

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_PRIVATE_WI0011_NONCOMPLETION_DIAGNOSTIC_EXPERIMENT.md`.

Enthalten sind zunächst:

- `execution-profile.json`: exakte Eingangs-, Laufzeit-, Kontroll- und
  Ausgabegrenzen;
- dieser Ausführungshinweis.

`result.json` entstand nach dem sauberen Preimage-Commit ausschließlich durch
den gebundenen privaten Hauptlauf. Es enthält nur die gemeinsame pfadfreie
Aggregation; private Einzelwerte oder Rohberichte wurden nicht gespeichert.

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

## Ergebnis

Das Ausführungspreimage ist
`6d32f5dad32481ef9ec163e742acb1ae77aaf226`. Die synthetische Kontrolle
bestand mit 3/3 tatsächlichen WI-0011-Abschlüssen, 9/9 Negativkontrollen,
identischer Aggregationswiederholung, unveränderten Quellen und vollständigem
Cleanup.

Der bestätigte private Hauptlauf verarbeitete genau drei EPUBs, vier
Suchläufe und drei WI-0011-Vergleiche. Alle drei Vergleiche endeten
`not_assessed` mit ausschließlich
`ingress.preflight_gate_not_open`. Das Ergebnis ist deshalb fachlich
`not_qualified`, obwohl die Methode alle 16/16 Kriterien bestand. Quellen,
Tempbereich und Container blieben unverändert beziehungsweise wurden
vollständig bereinigt.

Der historische Validator lautet:

```powershell
python tools/experiments/validate_exp_0013_result.py
```

GATE-0016 trennt die Bewertung dieses Befunds von jeder möglichen
Fortsetzung.
