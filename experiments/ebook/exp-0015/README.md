# EXP-0015 Ausführung

Status: DONE — EXECUTED, METHOD PASSED; RESULT REVIEW 3/3

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_PRIVATE_REMOTE_REFERENCE_CONTEXT_EXPERIMENT.md`.

Enthalten sind:

- `execution-profile.json`: exakte Eingangs-, Parser-, Datenschutz-,
  Kontroll- und Ausgabegrenzen;
- `result.json`: ausschließlich die gemeinsame pfadfreie
  Mindestgruppenaggregation;
- dieser Ausführungshinweis.

`result.json` entstand erst nach Commit und erfolgreicher CI auf exakt dem
Ausführungspreimage sowie nach erneutem Nachweis der drei bestätigten direkten
EPUB-Locators. Private Einzelwerte oder Parserprojektionen wurden weder
ausgegeben noch gespeichert.

## Historisch durchgeführte Prüf- und Ausführungsfolge

Profil und statische Bindungen wurden auf dem später ausgeführten Preimage
mit folgendem Befehl geprüft. Nach Abschluss und Registry-Status `done` ist
statt dieses Current-Preimage-Modus der unten genannte historische Validator
maßgeblich:

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
`src/sammlungslotse/`. Die fachliche Bewertung bleibt GATE-0018 vorbehalten.

## Ergebnis

Das Ausführungspreimage ist
`cefe2d29b54b8e6cbc60b07b1485da473565cda7`. Vor dem privaten Lauf bestanden
auf diesem Commit beide erforderlichen GitHub-Checks. Die synthetische
Kontrolle bestand mit 7/7 Kontextklassen, 19/19 Negativkontrollen,
32 Parserläufen, identischer Aggregationswiederholung, unveränderten Quellen
und vollständigem Cleanup.

Der bestätigte private Hauptlauf verarbeitete genau drei EPUBs. In allen drei
Eingängen war `content.navigation` präsent. Weitere bekannte Klassen,
unterdrückte seltene Klassen oder unklassifizierte Eingänge traten im
gebundenen Aggregat nicht auf. Quellen blieben unverändert und das Cleanup war
vollständig.

Das 483-Byte-Ergebnis besitzt den SHA-256-Wert
`651ad195b54531d20e0fc6ff882df6e1d4b38765e877057faf7858f36dae50a1`.
Der historische Validator lautet:

```powershell
python tools/experiments/validate_exp_0015_result.py
```

Der Klassenbefund ist keine Aussage über einzelne Referenzen, Erreichbarkeit,
Ausführung, Gefährlichkeit oder EPUB-Gültigkeit und keine Produktfreigabe.
