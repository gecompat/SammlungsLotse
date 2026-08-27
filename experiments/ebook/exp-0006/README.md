# EXP-0006 — Read-only Eingangstriage-Preflight

Status: PASSED

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

Das bestandene Ergebnis ist Evidenz für diesen fixierten synthetischen
Preflight, nicht für Produktreife, Produktionssicherheit oder die Wahl einer
E-Book-Schiene an GATE-0001.

## Ausführungsergebnis

Der vollständige Lauf am 2026-08-27 unter Podman 6.1.0 auf Linux/amd64 hat
alle 16 Akzeptanzkriterien erfüllt. Alle elf vorab gebundenen Matrixzeilen
entsprachen dem Soll; acht Fälle blieben außerhalb des tiefen Werkzeugwegs,
drei positiv gegatete Kontrollen starteten ihn, und die Zahl kritischer
Fehlfreigaben war null. Beide Wiederholungen erzeugten den identischen
semantischen Digest
`e14077d5cb783052cd79b309c60d3ae709f363523597e735be087a79a66b4ba4`.

Ein erster Infrastrukturversuch wurde nicht gewertet: Das zunächst im
Container-tmpfs abgelegte Ergebnis war nach Prozessende für `podman cp` nicht
mehr verfügbar. Der Ergebnistransport wurde daraufhin als eigener
Preimage-Commit auf den bereits größenbegrenzten, angehängten
Standardausgabekanal umgestellt. Ein späterer Repository-Selbstscan fand im
Runner ein Klartext-Pfadmuster, das den Privacy-Guard selbst auslöste. Auch
diese rein konstruktive Erkennungskorrektur wurde vor dem endgültigen Lauf
committed. Weil sich der gebundene Runner-Hash änderte, wurden vorhandene
Laufergebnisse verworfen und beide gewerteten Wiederholungen vollständig neu
gestartet. Dasselbe Vorgehen galt für die abschließende Härtung der
Input-Grenze, Umgebungsbelege und vollständigen CI-Neuberechnung: Erst nach
ihrem Preimage-Commit entstanden die hier festgehaltenen Wiederholungen.
Sollmatrix, Probeentscheidungen, Fixture und Sicherheitsgrenzen wurden dabei
nicht nach einem fachlichen Ergebnis verändert.

Der pfadbereinigte Nachweis steht in [result.json](result.json). Vollständige
Rohberichte bleiben außerhalb von Git; `result.json` hält Dateinamen, Größen
und SHA-256-Hashes fest. Die Evidenz gilt nur für die elf kleinen
synthetischen Zeilen und dieses wegwerfbare Containerprofil. Sie qualifiziert
keinen Produktparser, keinen allgemeinen PDF-Weg und keine Produktlaufzeit.
