# EXP-0014 Ausführung

Status: DONE — EXECUTED, METHOD PASSED; RESULT REVIEW 3/3

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_PRIVATE_INGRESS_PREFLIGHT_CAUSE_EXPERIMENT.md`.

Enthalten sind:

- `execution-profile.json`: exakte Eingangs-, WI-0004-, Kontroll- und
  Ausgabegrenzen;
- `result.json`: ausschließlich die gemeinsame pfadfreie Aggregation;
- dieser Ausführungshinweis.

`result.json` entstand nach dem sauberen Preimage-Commit und nach erneuter
ausdrücklicher Bestätigung derselben drei EPUB-Locators wie in EXP-0013.
Private Einzelwerte oder vollständige WI-0004-Berichte wurden weder
ausgegeben noch gespeichert.

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

## Ergebnis

Das Ausführungspreimage ist
`e82d01e6d669e85646dafd6ab3d569fc38e0d71b`. Die synthetische Kontrolle
bestand mit 4/4 tatsächlichen WI-0004-Läufen, 11/11 Negativkontrollen,
identischer Aggregationswiederholung, unveränderten Quellen und vollständigem
Cleanup.

Der bestätigte private Hauptlauf verarbeitete genau drei EPUBs. Alle drei
Läufe ergaben `review`, `format.epub`,
`epub.remote_reference.present` und `security.remote_resource`. Unbekannte
Beobachtungs- oder Befundcodes traten nicht auf. Quellen und task-private
Kopien blieben unverändert beziehungsweise wurden vollständig bereinigt.

Das 907-Byte-Ergebnis besitzt den SHA-256-Wert
`0eab4893eb85d05c07622bfe70721a58f03e8285e199738b1513237dc3207411`.
Der historische Validator lautet:

```powershell
python tools/experiments/validate_exp_0014_result.py
```

GATE-0017 trennt die Bewertung dieses Reviewbefunds von jeder möglichen
Fortsetzung. EXP-0014 autorisiert weder eine Produktkorrektur noch eine
Änderung unter `src/sammlungslotse/`.
