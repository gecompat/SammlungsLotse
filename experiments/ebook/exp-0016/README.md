# EXP-0016 Ausführung

Status: DONE — EXECUTED, METHOD PASSED

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_SYNTHETIC_NAVIGATION_SAFETY_MATRIX_EXPERIMENT.md`.

Enthalten sind:

- `execution-profile.json`: exakte Standards-, Parser-, Strategie-,
  Fehlkosten-, Bindungs- und Ausgabegrenzen;
- `cases.json`: genau 48 kleine synthetische Orakelfälle;
- `result.json`: ausschließlich die gebundenen Klassen-, Schemata-,
  Strategie- und Akzeptanzaggregate;
- dieser Ausführungshinweis.

`result.json` entstand erst nach Commit und erfolgreicher CI auf exakt dem
Ausführungspreimage. Der Doppellauf verwendete keine privaten Medien und
erzeugte keine Einzel- oder Rohberichte.

## Gebundene Prüf- und Ausführungsfolge

Profil, Fallmanifest, Standardsquellen und Runtime-Bindungen wurden auf dem
später ausgeführten sauberen Preimage geprüft:

```powershell
python tools/experiments/run_exp_0016.py --validate-profile
```

Nach grüner CI wurde genau ein synthetischer Doppellauf mit neuen begrenzten
Pfaden unter `C:\rep` ausgeführt:

```powershell
python tools/experiments/run_exp_0016.py `
  --execute `
  --confirm-green-preimage-ci `
  --temp-root C:\rep\tmp\SammlungsLotse\exp-0016\qualification `
  --result C:\rep\artifacts\SammlungsLotse\exp-0016\qualification\result.json
```

Der Runner verarbeitet die 48 Manifestfälle je zweimal im Speicher. Nur die
Klassen-, Schemata-, Strategie- und Akzeptanzaggregate werden geschrieben.
Snippets, URLs oder Einzelfallzeilen erscheinen nicht im Ergebnis.

Der fachliche Parser importiert oder startet keinen Produktcode, besitzt
keinen Netzwerkclient und verwendet weder Calibre noch ein tiefes Werkzeug,
eine Datenbank oder eine öffentliche Produktschnittstelle. Ein Subprozess ist
ausschließlich für die read-only Bindung des sauberen Git-Preimages erlaubt.
Taskmaterial wird vor der Ergebnisdatei vollständig bereinigt.

## Ergebnisgrenze

Der methodische Status und die drei Strategiestatus bleiben getrennt. Eine
Strategie ist bereits bei einer kritischen Fehlfortsetzung oder einem False
Negative `not_qualified`. Konservative Reviews und fail-closed Enthaltungen
bleiben als niedrigere, getrennte Kosten sichtbar.

Ein methodischer `pass` oder eine Strategie mit
`eligible_with_tradeoffs` ist keine Produktfreigabe. Insbesondere wird
`candidate_continue_deep_read_only` nur als synthetisches Vergleichsliteral
ausgegeben; es verändert das WI-0004-Review-Gate nicht und öffnet keinen Link.

## Ergebnis

Das Ausführungspreimage ist
`969fa6331afdfc4ceb808ffeed71f7a30193205b`. Genau 48 Fälle wurden in zwei
semantisch identischen Wiederholungen mit insgesamt 96 Parserläufen
verarbeitet. Alle 16 methodischen Akzeptanzwerte bestanden.

S1 und S2 behielten je acht konservative Reviews; S3 reduzierte sie auf null.
Alle drei Strategien behielten zehn fail-closed Enthaltungen und hatten null
kritische Fehlfortsetzungen, null False Negatives sowie null Context
Mismatches. Sie sind innerhalb der gebundenen synthetischen Matrix jeweils
`eligible_with_tradeoffs`.

Das 2.279-Byte-Ergebnis besitzt den SHA-256-Wert
`6c748dd1477dba56a37e19b7a5bf798d32e702e8d6d2a230ebfa3c98d775db08`.
Der dauerhafte Validator wiederholt den Experimentlauf nicht:

```powershell
python tools/experiments/validate_exp_0016_result.py
```

Die fachliche Fortsetzung bleibt GATE-0019 vorbehalten.
