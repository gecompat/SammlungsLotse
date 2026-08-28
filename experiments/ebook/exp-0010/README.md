# EXP-0010 — standardgebundene EPUB-Metadaten- und Oracle-Evidenz

Status: PREIMAGE PREPARED — NOT EXECUTED

Stand: 2026-08-28

Artifact: EXP-0010

## Zweck und Grenze

EXP-0010 misst den unveränderten WI-0009-Identitätsdienst gegen zehn vorab
gebundene synthetische Paare. Die Matrix trennt primäre und zusätzliche
Identifier, `dcterms:modified` sowie Collection-Name, -Typ, -ID und -Position.
Ein unabhängiger Lauf des bestehenden WI-0005-EPUBCheck-5.3.0-Profils hält
Paketkonformität von der bibliografischen Fallwahrheit getrennt.

Produktcode, TEST-0001, reale/private Medien, Downloads, Netzwerk, Calibre,
Persistenz und Bestandswirkungen bleiben außerhalb.

## Versionierter Versuchsaufbau

- `execution-profile.json` bindet Produktgrenzen, vorhandenes
  EPUBCheck-Profil, Fallzahlen, Stufen, Metriken und zwei
  Produktwiederholungen.
- `case-manifest.json` bindet vor dem ersten Lauf Generatorfelder,
  Konformitätserwartungen, Publikationsoracles, fünfstufige Produktoracles und
  fallbezogene Begründungen.
- `tools/experiments/run_exp_0010.py` materialisiert nur synthetische EPUBs,
  projiziert die Standardrollen, prüft jedes Einzelpaket einmal mit dem
  bestehenden netzwerklosen Provider und ruft den unveränderten Produktdienst
  zweimal auf.
- `tests/experiments/test_exp_0010.py` prüft Generator, Rollenprojektion,
  Oracle-Unabhängigkeit und enge Wirkungsgrenzen ohne Containerstart.

## Ausführung

Vor dem empirischen Lauf:

    python tools/experiments/run_exp_0010.py --validate-profile
    python -m unittest tests.experiments.test_exp_0010 -v

Der tatsächliche Lauf darf erst von einem sauberen eingecheckten Preimage
erfolgen:

    python tools/experiments/run_exp_0010.py \
      --temp-root C:\rep\tmp\SammlungsLotse\exp-0010

Anschließende CI-geeignete Prüfung ohne neue Materialisierung oder
Containerstarts:

    python tools/experiments/run_exp_0010.py --validate-result

## Ausführungsergebnis

Noch nicht ausgeführt. Die Oracles und Generatorparameter werden mit dem
Preimage-Commit eingefroren, bevor `result.json` erzeugt wird.
