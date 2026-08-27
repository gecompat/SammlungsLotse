# EXP-0007 — Unveränderlicher Snapshot-zu-Werkzeug-Übergang

Status: IMPLEMENTIERT — EMPIRISCHE AUSFÜHRUNG AUSSTEHEND

## Zweck und Grenze

EXP-0007 vergleicht drei providerneutrale Übergabeformen zwischen dem
unveränderlichen WI-0004-Snapshot und einem synthetischen tiefen read-only
Werkzeugprozess. Es implementiert keinen Produktadapter und verändert keinen
Produktcode.

Die drei Varianten sind:

- V1: begrenzter Byte-Stream;
- V2: task-private, hashgebundene Materialisierung;
- V3: erneutes read-only Öffnen des Original-Locators.

Die Ausführung verwendet ausschließlich die zwei im Profil gebundenen
synthetischen TEST-0001-Kontrollen. Vollständige Rohbelege und temporäre
Arbeitskopien bleiben außerhalb von Git unter den projektkontrollierten
Artefakt- und Temp-Verzeichnissen.

## Versionierter Versuchsaufbau

- `execution-profile.json` bindet Eingänge, Sollhashes, Prozess-, Zeit-,
  Input-, Output-, Temp- und Containergrenzen vor dem ersten Messlauf.
- `probe.py` bildet ausschließlich den synthetischen Prozessrand ab.
- `driver.py` führt positive Wiederholungen und die vorab festgelegten
  Negativkontrollen für Snapshot-Bindung, Output, Timeout, Cleanup und TOCTOU
  aus.
- `Containerfile` erzeugt aus dem bereits lokal vorhandenen digest-gebundenen
  Python-Bild ein wegwerfbares Linux-Profil ohne Netzwerkzugriff beim Build.
- `tools/experiments/run_exp_0007.py` führt Windows und Linux getrennt aus,
  liest die Containergrenzen zurück und erzeugt erst danach `result.json`.

## Ausführung

Vor dem empirischen Lauf:

```text
python tools/experiments/run_exp_0007.py --validate-profile
python -m unittest tests.experiments.test_exp_0007 -v
```

Empirischer Lauf nach einem unveränderten Preimage-Commit:

```text
python tools/experiments/run_exp_0007.py
```

Der eingecheckte Ergebnisvertrag wird anschließend geprüft mit:

```text
python tools/experiments/run_exp_0007.py --validate-result
```

Ein erfolgreicher Versuch qualifiziert nur die ausdrücklich ausgewählte
Übergabenaht. GATE-0003 wertet das Ergebnis getrennt aus.
