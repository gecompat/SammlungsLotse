# EXP-0014 Ausführung

Status: READY — PREIMAGE IMPLEMENTED; PRIVATE RUN NOT EXECUTED

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_PRIVATE_INGRESS_PREFLIGHT_CAUSE_EXPERIMENT.md`.

Enthalten sind vor dem privaten Lauf ausschließlich:

- `execution-profile.json`: exakte Eingangs-, WI-0004-, Kontroll- und
  Ausgabegrenzen;
- dieser Ausführungshinweis.

Ein `result.json` darf erst nach einem sauberen Preimage-Commit und nach der
erneuten ausdrücklichen Übergabe derselben drei EPUB-Locators wie in EXP-0013
entstehen. Private Einzelwerte oder vollständige WI-0004-Berichte werden
weder ausgegeben noch gespeichert.

## Prüf- und Ausführungsfolge

Profil und statische Bindungen:

```powershell
python tools/experiments/run_exp_0014.py --validate-profile
```

Die synthetischen Kontrollen führen vier tatsächliche WI-0004-JSON-Läufe auf
TEST-0001-Material aus. Sie decken `continue_deep_read_only`, `review`,
`stop` und `abstain` ab. Eine gebundene Projektionsmatrix ergänzt `defer`,
mehrere Beobachtungs- und Befundcodes, eine leere Befundmenge und maskierte
unbekannte Codes. Negativkontrollen prüfen Eingangsgrenzen, Teilabbruch,
ungültiges JSON, Datenschutz, Quellunverändertheit und Cleanup:

```powershell
python tools/experiments/run_exp_0014.py --synthetic-controls
```

Der private Hauptlauf benötigt genau drei explizite Dateien und die erneute
ausdrückliche Bestätigung, dass es sich um denselben Eingangssatz wie in
EXP-0013 handelt:

```powershell
python tools/experiments/run_exp_0014.py `
  --private-epub "<erste EPUB-Datei>" `
  --private-epub "<zweite EPUB-Datei>" `
  --private-epub "<dritte EPUB-Datei>" `
  --confirm-same-exp-0013-inputs
```

Die Locators werden weder ausgegeben noch versioniert. Jede neutrale
task-private Kopie durchläuft genau einmal den unveränderten Befehl
`python tools/run_ebook_intake.py --json`. Vollständige JSON-Berichte sowie
stdout und stderr bleiben begrenzt im Prozessspeicher. Vor der Aggregation
werden nur die öffentliche Folgeaktion und bekannte Code-Schlüssel
übernommen; Evidenzwerte, Snapshot, Hashes, Größen und alle übrigen Felder
werden verworfen.

Ein unbekannter öffentlicher Code erscheint nicht als Literal. Er erhöht nur
den betreffenden `unclassified`-Zählwert, setzt den Ergebnisstatus auf
`inconclusive` und führt zu Exitcode 2. Ausführungs-, Sicherheits- oder
Cleanupfehler erzeugen kein Teilergebnis.

Ein späteres Ergebnis eröffnet ein neues getrenntes Gate. EXP-0014
autorisiert weder eine Produktkorrektur noch eine Änderung unter
`src/sammlungslotse/`.
