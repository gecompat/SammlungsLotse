# EXP-0016 Ausführung

Status: READY — SYNTHETIC PREIMAGE NOT EXECUTED

Stand: 2026-09-01

Dieser Ordner bindet die produktcodefreie Ausführung aus
`docs/planning/EBOOK_SYNTHETIC_NAVIGATION_SAFETY_MATRIX_EXPERIMENT.md`.

Enthalten sind vor der Ausführung:

- `execution-profile.json`: exakte Standards-, Parser-, Strategie-,
  Fehlkosten-, Bindungs- und Ausgabegrenzen;
- `cases.json`: genau 48 kleine synthetische Orakelfälle;
- dieser Ausführungshinweis.

`result.json` entsteht erst nach Commit und erfolgreicher CI auf exakt dem
Ausführungspreimage. Der Doppellauf verwendet keine privaten Medien und
erzeugt keine Einzel- oder Rohberichte.

## Gebundene Prüf- und Ausführungsfolge

Profil, Fallmanifest, Standardsquellen und Runtime-Bindungen werden auf dem
sauberen Preimage geprüft:

```powershell
python tools/experiments/run_exp_0016.py --validate-profile
```

Nach grüner CI wird genau ein synthetischer Doppellauf mit neuen begrenzten
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

Nach der Ausführung bindet ein eigener historischer Validator das Ergebnis an
das Preimage. Die fachliche Fortsetzung bleibt einem neuen Ergebnisgate
vorbehalten.
