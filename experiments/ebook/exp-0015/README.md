# EXP-0015 Ausführung

Status: ACCEPTED — EXECUTION PREIMAGE; PRIVATE RESULT ABSENT

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_PRIVATE_REMOTE_REFERENCE_CONTEXT_EXPERIMENT.md`.

Enthalten sind:

- `execution-profile.json`: exakte Eingangs-, Parser-, Datenschutz-,
  Kontroll- und Ausgabegrenzen;
- dieser Ausführungshinweis.

Ein privates `result.json` gehört ausdrücklich noch nicht zum Preimage. Der
Hauptlauf ist erst nach Commit, erfolgreicher CI auf exakt diesem Commit und
erneutem Nachweis der drei bestätigten direkten EPUB-Locators zulässig.

## Prüf- und Ausführungsfolge

Profil und statische Bindungen:

```powershell
python tools/experiments/run_exp_0015.py --validate-profile
```

Die ausschließlich synthetischen Kontrollen prüfen alle sieben gebundenen
Kontextklassen, Mindestgruppe und Unterdrückung, unklassifizierte Funde,
Nicht-HTTP(S)-Referenzen, deterministische Wiederholung sowie sämtliche
Eingangs-, ZIP-, Lese-, Datenschutz-, Teilabbruch- und Cleanupgrenzen:

```powershell
python tools/experiments/run_exp_0015.py --synthetic-controls
```

Der private Hauptlauf benötigt genau drei explizite Dateien und die erneute
ausdrückliche Bestätigung, dass es sich um denselben Eingangssatz wie in
EXP-0014 handelt:

```powershell
python tools/experiments/run_exp_0015.py `
  --private-epub "<erste EPUB-Datei>" `
  --private-epub "<zweite EPUB-Datei>" `
  --private-epub "<dritte EPUB-Datei>" `
  --confirm-same-exp-0014-inputs
```

Ein read-only Git-Aufruf bindet vor jeder privaten Eingangsprüfung das
vollständig eingecheckte Preimage. Er erhält keine privaten Argumente. Der
fachliche Parser selbst startet keinen Subprozess, importiert keinen
Produktcode, nutzt kein Netzwerk und extrahiert keine ZIP-Einträge.

Die Locators, Dateinamen, Inhalte, Referenzwerte, ZIP-Eintragsnamen, Hashes und
Größen werden weder ausgegeben noch versioniert. Jede neutrale task-private
Kopie durchläuft genau einen gebundenen Standardbibliotheks-Parserlauf. Pro
Eingang und Kontext bleibt nur ein boolescher Präsenzwert im Prozessspeicher.

Nur Klassen, die mindestens zwei Eingänge erreichen, dürfen mit einer
Eingangsanzahl im gemeinsamen Aggregat erscheinen. Eine nur einmal vertretene
Klasse wird ausschließlich durch `suppressed_context_present: true` belegt;
ihr Klassenliteral bleibt verborgen. Unklassifizierte Funde führen zu
`inconclusive`. Ausführungs-, Sicherheits- oder Cleanupfehler erzeugen kein
Teilergebnis.

EXP-0015 autorisiert weder eine Produktkorrektur noch eine Änderung unter
`src/sammlungslotse/`. Die fachliche Bewertung eines späteren Ergebnisses
bleibt einem nachgelagerten Gate vorbehalten.
