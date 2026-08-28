# EXP-0009 — Identitäts- und Enthaltungsevidenz verbreitern

Status: RUNTIME_EMPIRICAL METHOD PASSED — PRODUKTQUALITÄT NOT_QUALIFIED

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

## Ausführungsergebnis

Der vollständige Lauf auf dem eingefrorenen Preimage
`2ef2de0395e485283f3be4ca339ab5fed8657fee` erfüllte 12/12 methodische
Akzeptanzkriterien. Genau 18 Paare wurden in zwei unabhängigen
Materialisierungen bewertet. Beide semantischen Wiederholungsdigests waren
`6b548be8ba0963a827f95b192d3305160b629d0b6ed43d9046e2450ac78a5d67`.
Alle Eingänge blieben unverändert, drei vorab gebundene unsichere Pakete
endeten `not_assessed`, die temporäre Run-Wurzel wurde vollständig entfernt
und alle Wirkungsfelder blieben `false`.

Die beobachtete Produktqualität lautet dennoch `not_qualified`. Der Fall
`metadata-collision-work-conflict` besitzt auf beiden Seiten denselben Titel,
Creator, Identifier und dieselbe Sprache, aber ausdrücklich widersprüchliche
Werkreferenzen und verschiedenen Inhalt. Das Oracle erlaubt auf Ausgaben- und
Werkebene nur `different` oder `abstain`. Der unveränderte Produktdienst
lieferte auf beiden Ebenen `candidate_same`:

- `identity.edition.identifier_title` wertete Identifier und Titel positiv,
  obwohl `metadata.work_references_conflict` als negative Evidenz sichtbar
  war;
- `identity.work.same_edition` übernahm anschließend die falsche
  Ausgabengleichheit als Werkgleichheit.

Damit sind zwei kritische False-Same-Befunde offen. Sie werden nicht durch
Mittelwerte verdeckt und in dieser Experimentwave nicht repariert.

## Messwerte

| Ebene | Precision / Recall der positiven Labels | Abdeckung | Selektive Genauigkeit | Befund |
|---|---|---:|---:|---|
| Byte | `candidate_same`: 1,0 / 1,0 | 1,0 | 1,0 | kein Fehler |
| Paket | `candidate_same`: 1,0 / 1,0 | 1,0 | 1,0 | kein Fehler |
| Repräsentation | `candidate_same`: 1,0 / 1,0 | 1,0 | 1,0 | kein Fehler |
| Ausgabe | `candidate_same`: 0,875 / 1,0 | 0,666667 | 0,9 | ein kritischer False Same |
| Werk | `candidate_same`: 0,875 / 1,0; `candidate_related`: 1,0 / 1,0 | 0,866667 | 0,923077 | ein kritischer False Same |

Diese Werte beschreiben ausschließlich die 15 vollständig bewertbaren
synthetischen Paare. Sie schätzen keine Häufigkeit oder Qualität in realen
Sammlungen.

## Ergebniswirkung und Stopp

Der Experimentvertrag ist vollständig und reproduzierbar ausgeführt;
EXP-0009 ist deshalb `done`. Das Ergebnis qualifiziert den aktuellen
Produktdienst jedoch nicht für diesen verbreiterten adversariellen
Goldstandard. Vor einer Regeländerung, Produktwave oder anderen Fortsetzung
ist ein getrenntes Ergebnisgate erforderlich. Kandidatensuche, Provider,
Persistenz, UI, API, Agents, Writers und reale Medien bleiben außerhalb.
