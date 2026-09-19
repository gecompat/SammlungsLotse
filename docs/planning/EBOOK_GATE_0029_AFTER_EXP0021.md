# GATE-0029: EXP-0021-Ergebnis und Docker-Evidenzgrenze bewerten

Status: DONE — OPTION B AUTONOM AUSGEWÄHLT

Stand: 2026-09-19

Artifact: GATE-0029

## Ausgangslage

EXP-0021 belegt eine isolierte, ausschließlich synthetische Docker-
Projektionsumgebung. Docker und Podman verwenden getrennte Speicher und
unterschiedliche Config-IDs; der Nachweis ersetzt weder EXP-0020 noch den
öffentlichen WI-0019-Podman-CLI-Vertrag.

## Optionen

### A — Docker-Evidenz konservieren

Die erfolgreiche Umgebung bleibt als lokale Evidenz dokumentiert. Es entsteht
keine weitere Arbeit und keine Produktvertragsänderung.

### B — Produktcodefreien Docker-Podman-Vergleich durchführen

EXP-0022 vergleicht genau eine gemeinsame task-private synthetische
Calibre-Bibliothek in beiden Runtimes. Er bindet normalisierte pfadfreie
Projektionen, Inspect-Isolation und Cleanup, ohne Image-Identität oder
automatische Runtime-Austauschbarkeit zu behaupten.

### C — Runtime-Adapter oder Produktvertrag migrieren

Nicht auswählen. Dafür fehlen eine angenommene Architektur- und
Runtimeentscheidung, erneute Provider-/Lizenz-/Sicherheitsbewertung sowie die
vollständige öffentliche Vertragsqualifikation.

### K — Pausieren

Die vorhandene Evidenz bleibt erhalten; es wird keine Folge registriert.

## Auswahl

Option B wird unter der Autonomie-Autorisierung ausgewählt. EXP-0022 bleibt
ein ausschließlich synthetisches, produktcodefreies Experiment. Ein Erfolg
entscheidet weder über einen Runtimewechsel noch über eine Änderung der
Podman-CLI, eines Profils, Executors oder einer Nutzeroberfläche.

## Harte Grenzen

- kein Produktcode und keine Änderung von Podman- oder Docker-Produktvertrag;
- kein Netzwerk, keine Persistenz, kein Import, kein Writer und keine
  Bestandswirkung;
- keine Behauptung identischer Image-IDs oder automatischer Austauschbarkeit;
- nur task-private synthetische Bibliothek, pfadfreie Aggregate und Cleanup-
  Evidenz.
