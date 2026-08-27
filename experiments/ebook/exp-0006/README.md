# EXP-0006 — Read-only Eingangstriage-Preflight

Status: PROFIL VERSIONIERT — NOCH NICHT AUSGEFÜHRT

## Zweck und Grenze

EXP-0006 prüft ausschließlich, ob eine eng begrenzte, synthetische
Eingangstriage unbekannte oder riskante E-Book-Eingänge früh genug anhält. Der
Versuch implementiert weder Produktcode noch eine öffentliche Schnittstelle,
Persistenz, einen Writer oder eine Integration in FolioTone beziehungsweise ein
anderes Fachsystem.

Die Entscheidungslogik hält `format_capability`, `next_action` und
`deep_tool_allowed` getrennt. Sie bewertet die elf vorab gebundenen Zeilen aus
TEST-0001 `0.2.0` in der festen Reihenfolge Snapshot, Signatur,
Container-Metadaten, Schutz beziehungsweise aktive Inhalte, Entscheidung und
Deep-Tool-Gate. Erwartungswerte werden erst nach der Entscheidung verglichen;
sie sind kein Entscheidungs-Oracle.

## Versionierter Versuchsaufbau

- `execution-profile.json` bindet Fixture-Version, Manifest-Hash, Bild-Digest,
  Umgebung, Ressourcen, Zeit- und Ausgabegrenzen sowie die elf erwarteten
  Zeilen.
- `Containerfile` baut ausschließlich aus dem bereits lokal vorhandenen,
  digest-gebundenen Python-Bild; der Build verwendet `--pull=never` und
  `--network=none`.
- `probe.py` nutzt nur die Python-Standardbibliothek, liest das Fixture
  read-only, extrahiert keine Originale und führt keine eingebetteten Inhalte
  aus.
- `tools/experiments/run_exp_0006.py` baut die Einweg-Umgebung, führt zwei
  Wiederholungen aus, übernimmt deren jeweils größenbegrenztes Ergebnis direkt
  über den angehängten Standardausgabekanal, prüft die Laufzeit-Isolation und
  erzeugt erst danach das versionierbare Ergebnis.
- `tests/experiments/test_exp_0006.py` prüft Profil, Entscheidungs-Matrix,
  Oracle-Unabhängigkeit, Deep-Tool-Gate und — sobald vorhanden — das
  eingefrorene Ergebnis.

Jede Wiederholung läuft ohne Netzwerk, mit read-only Root-Dateisystem,
read-only Fixture-Mount, leerer Capability-Menge, `no-new-privileges`, fester
UID/GID sowie CPU-, RAM-, PID-, Zeit-, tmpfs- und Ergebnisgrenzen. Schreibbar
sind nur die begrenzten Container-tmpfs-Mounts `/tmp` und `/output`; das
Ergebnis verlässt den Container über den größenbegrenzten Standardausgabekanal
und wird erst vom Host-Runner im Artefaktpfad abgelegt.

## Ausführung und Validierung

Profil und lokale Probe vor dem empirischen Lauf prüfen:

```text
python tools/experiments/run_exp_0006.py --validate-profile
python -m unittest tests.experiments.test_exp_0006 -v
```

Den expliziten empirischen Lauf ausführen:

```text
python tools/experiments/run_exp_0006.py
```

Rohbelege entstehen ausschließlich unter
`C:\rep\artifacts\SammlungsLotse\exp-0006`. Das zusammengefasste,
pfadbereinigte Ergebnis wird bei bestandenem Akzeptanzvertrag als
`result.json` neben diesem Dokument geschrieben und anschließend so geprüft:

```text
python tools/experiments/run_exp_0006.py --validate-result
```

Ein bestandenes Ergebnis wäre Evidenz für diesen fixierten synthetischen
Preflight, nicht für Produktreife, Produktionssicherheit oder die Wahl einer
E-Book-Schiene an GATE-0001.
