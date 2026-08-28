# EXP-0008 — Unterstützte Calibre-Einzelrecord-EPUB-Übergabe

Status: PREIMAGE VORBEREITET — EMPIRISCHER LAUF AUSSTEHEND

Stand: 2026-08-28

## Zweck und Grenze

EXP-0008 qualifiziert ausschließlich eine synthetische Übergabenaht. Genau
eine explizite externe Calibre-ID darf aus einer task-privaten
Copy-on-read-Arbeitskopie über `calibredb export` genau ein vorhandenes EPUB
bereitstellen. Das Experiment implementiert keinen Produktadapter und keinen
Identitätsvergleich.

Das Calibre-Quellsystem bleibt unverändert. Direkter Zugriff des
Experimentcodes auf interne Calibre-Datenbanken, mehrere IDs, andere Formate,
Netzwerk, reale Bibliotheken, Persistenz und Writes sind ausgeschlossen.

## Versionierter Versuchsaufbau

- `execution-profile.json` bindet das unveränderte WI-0007-
  Calibre-9.13.0-Profil, die exakte Image-ID, die synthetische
  Qualifikationsbibliothek, den positiven Datensatz und alle Grenzen.
- `tools/experiments/run_exp_0008.py` materialisiert eine frische
  synthetische Bibliothek über unterstützte Calibre-Befehle, erzeugt pro Fall
  eine neue Copy-on-read-Arbeitskopie, liest Containergrenzen zurück und
  entfernt alle eigenen Tasks und Container.
- Der positive Befehl erzwingt `--dont-update-metadata`, schließt OPF, Cover,
  Extra-Dateien und andere Formate aus und akzeptiert nur eine reguläre
  `<id>.epub`-Datei mit dem gebundenen Hash.
- Fehlende ID, Datensatz ohne EPUB, mehrere oder ungültige IDs, unerwartete
  Ausgabe, Outputgrenze, Timeout, simulierte Unterbrechung und Recovery sind
  getrennte Negativkontrollen.
- `result.json` entsteht erst nach einem unveränderten Preimage-Commit und
  enthält nur pfadfreie normalisierte Evidenz. Begrenzte Rohbelege bleiben
  außerhalb von Git unter `C:\rep\artifacts\SammlungsLotse`.

## Ausführung

Vor dem empirischen Lauf:

    python tools/experiments/run_exp_0008.py --validate-profile

    python -m unittest tests.experiments.test_exp_0008 -v

Der tatsächliche Lauf erfolgt erst nach dem Preimage-Commit:

    python tools/experiments/run_exp_0008.py \
      --temp-root C:\rep\tmp\SammlungsLotse\exp-0008 \
      --evidence-root C:\rep\artifacts\SammlungsLotse\exp-0008

Der eingecheckte Ergebnisvertrag wird anschließend ohne Containerlauf
geprüft:

    python tools/experiments/run_exp_0008.py --validate-result

## Ergebniswirkung

`qualified` belegt nur, dass das gebundene Calibre-Profil genau einen
synthetischen EPUB-Datensatz über die unterstützte CLI sicher übergeben kann.
Ein späterer Produktvergleich benötigt ein neues Ergebnisgate und einen
eigenen angenommenen Arbeitsgegenstand. `not_qualified` und `inconclusive`
führen fail-closed zu keiner Produktübernahme.
