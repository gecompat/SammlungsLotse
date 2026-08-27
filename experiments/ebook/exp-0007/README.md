# EXP-0007 — Unveränderlicher Snapshot-zu-Werkzeug-Übergang

Status: PASSED

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

## Ausführungsergebnis

Der vollständige Lauf am 2026-08-27 unter Python 3.12.10 auf Windows und
Podman 6.1.0 auf Linux/amd64 hat alle 16 Akzeptanzkriterien erfüllt. Je
Plattform wurden zwei synthetische Snapshots über alle drei Varianten und je
zwei Wiederholungen geprüft. Alle zwölf positiven Prozessläufe pro Plattform
bestätigten exakt Snapshot-SHA-256 und -Größe; die semantischen
Wiederholungsdigests waren je Kombination identisch und alle Originalhashes
blieben unverändert.

V1 und V2 sind `QUALIFIED`. V3 ist `REJECTED`, weil der Provider den
Original-Locator erhält und die koordinierte Änderungskontrolle eine
TOCTOU-Lücke zwischen Snapshot und Werkzeuglesung reproduziert. Die
optionale V2-Kompatibilitätswiederholung gegen das bereits
provenienzgebundene lokale EPUBCheck-5.3.0-Profil war für beide synthetischen
Eingänge qualifiziert. Dies ist keine Provider- oder Produktentscheidung.

Unfreigegebene, instabile, hashabweichende und übergroße Eingänge starteten
keinen Prozess. Streamabbruch, stdout-/stderr-Limit, Timeout,
Kindprozessabschluss sowie Erfolg-, Fehler-, Unterbrechungs-, Temp- und
Crashrest-Cleanup waren wirksam. Das Linux-Profil las Netzwerk-, Benutzer-,
Capability-, Root-, PID-, CPU-, RAM-, tmpfs-, Umgebungs-, Mount- und
Outputgrenzen nach dem Lauf zurück.

Ein erster nicht gewerteter Lauf deckte beim optionalen
EPUBCheck-Kompatibilitätsschritt eine Windows-Cleanup-Lücke für die dort
ebenfalls read-only gesetzte Arbeitskopie auf. Der Runner wurde korrigiert,
als neues Preimage `466fa62ca5d30e9f1b9701095fd16286dd780c18`
festgeschrieben und danach wurden Windows-, Linux- und Kompatibilitätsläufe
vollständig neu ausgeführt. Der fehlgeschlagene Tempbereich wurde gezielt
bereinigt; sein synthetischer Rohartefakt bleibt außerhalb von Git als
Fehlerhistorie erhalten.

Der pfad- und namensminimierte Nachweis steht in [result.json](result.json).
Vollständige Rohbelege verbleiben unter dem projektkontrollierten lokalen
Artefaktbereich außerhalb von Git.
