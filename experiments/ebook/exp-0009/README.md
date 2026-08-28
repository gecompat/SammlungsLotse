# EXP-0009 — Identitäts- und Enthaltungsevidenz verbreitern

Status: PREIMAGE IN ARBEIT — EMPIRISCHER LAUF AUSSTEHEND

Stand: 2026-08-28

Artifact: EXP-0009

## Zweck und Grenze

EXP-0009 misst den unveränderten WI-0009-Identitätsdienst gegen genau 18
vorab gebundene synthetische Paare. Es erweitert weder Produktcode noch
TEST-0001 und wählt keine Kandidatensuche, Architektur, Provider-,
Persistenz-, UI-, API-, Agent- oder Writerfläche.

Der Messvertrag trennt Byte, Paket, Repräsentation, Ausgabe und Werk. Er
erfasst je Ebene Oracle-Matrix, False Positives, False Negatives, Precision,
Recall, selektive Genauigkeit, Abdeckung, Enthaltung und
Erklärungsvollständigkeit. Drei unsichere oder beschädigte Pakete müssen
fail-closed als `not_assessed` enden.

## Versionierter Versuchsaufbau

- `execution-profile.json` bindet Grenzen, Stufen, Entscheidungen, Metriken,
  zwei Wiederholungen und die reine Standardbibliotheksausführung.
- `case-manifest.json` bindet sämtliche synthetischen Feldwerte,
  Generatorvarianten und erlaubten Entscheidungen vor dem ersten Lauf.
- `tools/experiments/run_exp_0009.py` materialisiert pro Wiederholung neue
  kleine EPUB-Paare unter dem expliziten Taskpfad, ruft ausschließlich den
  Produktdienst auf und entfernt seine temporäre Run-Wurzel.
- `tests/experiments/test_exp_0009.py` prüft Generatorgrenzen,
  Ebenentrennung, fail-closed Negativfälle und die Unabhängigkeit der
  Produktentscheidung vom Oracle.

Ein methodisch bestandener Versuch kann die beobachtete Produktqualität als
`qualified`, `qualified_with_findings` oder `not_qualified` ausweisen. Ein
kritischer Befund ist sichtbar zu erhalten und darf in dieser Wave nicht
durch eine Produktänderung repariert werden.

## Ausführung

Vor dem empirischen Lauf:

    python tools/experiments/run_exp_0009.py --validate-profile

    python -m unittest tests.experiments.test_exp_0009 -v

Der tatsächliche Lauf darf erst von einem sauberen eingecheckten Preimage
erfolgen:

    python tools/experiments/run_exp_0009.py \
      --temp-root C:\rep\tmp\SammlungsLotse\exp-0009

Anschließende CI-geeignete Prüfung ohne neue Materialisierung:

    python tools/experiments/run_exp_0009.py --validate-result

## Noch kein Ergebnis

Profil, Generator und Oracles werden zuerst eingefroren. Solange kein sauberer
Preimage-Commit und kein vollständiger Doppellauf vorliegen, existiert weder
ein empirischer Status noch eine Qualitätsaussage.
