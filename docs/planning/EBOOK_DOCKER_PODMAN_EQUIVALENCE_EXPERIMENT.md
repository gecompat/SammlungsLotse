# EXP-0022: Synthetische Docker-Podman-Projektionsäquivalenz

Status: ACCEPTED

Stand: 2026-09-19

Artifact: EXP-0022

## Zweck

EXP-0022 prüft produktcodefrei und ausschließlich synthetisch, ob Docker und
Podman für dieselbe task-private Calibre-Bibliothek dieselbe normalisierte,
pfadfreie Feldprojektion liefern. Der Versuch prüft keine öffentliche
Produkt-CLI und keine Runtime-Austauschbarkeit.

## Gebundener Gegenstand

- genau eine gemeinsame, neu materialisierte synthetische Calibre-Bibliothek;
- je zwei getrennte, strikt inspect-geprüfte Docker- und Podman-Projektionen;
- normalisierte pfadfreie Projektdigests, unveränderter Bibliothekssnapshot
  und vollständiges Container-/Task-Cleanup;
- sichtbare Docker- und Podman-Image-/Profilbindungen ohne Gleichsetzung der
  verschiedenen Config-IDs.

## Akzeptanzgrenzen

Jede fehlende Isolation, Projektion, Wiederholung oder Cleanup-Evidenz führt
zu `not_qualified`. Ein passender Vergleich qualifiziert nur die gebundene
synthetische Projektionsmatrix. Er verändert weder Produktcode noch Runtime-
Profile und entscheidet weder über den WI-0019-Vertrag noch über einen
Runtimewechsel.

## Ausführungsstand

not executed.
