# EXP-0022: Synthetische Docker-Podman-Projektionsäquivalenz

Status: DONE — NOT_QUALIFIED

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

RUNTIME_EMPIRICAL ausgeführt am 2026-09-19. Beide Runtimes erfüllten die
gebundene Isolation, bereinigten Container und Taskroot vollständig und
lieferten je zwei intern hashgleiche Projektionen bei unverändertem
Bibliothekssnapshot. Die normalisierten Docker- und Podman-Projektdigests
unterscheiden sich jedoch. EXP-0022 ist deshalb `not_qualified`; es belegt
keine Runtime-Austauschbarkeit. Die pfadfreie Evidenz steht unter
`experiments/ebook/exp-0022/result.json`.
