# EXP-0021: Synthetische Docker-Äquivalenz des Calibre-Reviewplan-Laufwegs

Status: DONE

Stand: 2026-09-19

Artifact: EXP-0021

## Zweck

EXP-0021 prüft ausschließlich synthetisch und produktcodefrei, ob Docker den
für einen begrenzten Calibre-Reviewplan erforderlichen Lauf mit explizit
geprüfter Isolation ausführen kann. Es ersetzt weder EXP-0020 noch den
Podman-Produktvertrag.

## Gebundener Gegenstand

- ein Docker-spezifisches, nachvollziehbar provisioniertes Linux/amd64-Image;
- genau eine task-private synthetische Calibre-Bibliothek und ein begrenzter
  synthetischer Eingangsordner;
- zwei semantisch identische Wiederholungen mit pfadfreier Evidenz;
- Vorstartprüfung per `docker inspect` für Image, Entrypoint, `--pull=never`,
  `--network=none`, read-only Root, Capability-Entzug, no-new-privileges,
  unprivilegierten Nutzer sowie Prozess-, CPU-, Speicher-, Swap-, ulimit-,
  tmpfs- und Bind-Mount-Grenzen;
- Nachprüfung von Quellenhashes, Container-/Task-Cleanup und fehlenden
  Netzwerk-, Persistenz-, Import-, Writer- und Bestandswirkungen.

## Akzeptanzgrenzen

Abweichungen in der Inspect-Projektion, fehlende Voraussetzungen oder nicht
eindeutig nachweisbare Isolation führen fail-closed zu `not_qualified`; der
Container startet dann nicht. Ein erfolgreicher Nachweis entscheidet weder
über Produktübernahme noch über Ersatz des Podman-Profils, Versionen,
Lizenzbewertung oder eine reale Calibre-Bibliothek.

## Ausführungsstand

RUNTIME_EMPIRICAL validiert am 2026-09-19. Der netzwerkfreie Docker-Lauf
materialisierte genau eine task-private synthetische Calibre-Bibliothek und
führte zwei getrennte Projektionen aus. Beide Projektdigests waren identisch,
der Bibliothekssnapshot blieb unverändert und Container sowie Taskroot wurden
vollständig bereinigt. Die Docker-Config-ID unterscheidet sich dokumentiert
von der Podman-Quell-ID; Linux/amd64 und der Entrypoint sind separat exakt
gebunden. Das Ergebnis qualifiziert ausschließlich diese Docker-
Projektionsumgebung, nicht den öffentlichen WI-0019-Podman-CLI-Vertrag oder
einen Runtimewechsel. Die pfadfreie, commitgebundene Evidenz steht unter
`experiments/ebook/exp-0021/result.json`.
