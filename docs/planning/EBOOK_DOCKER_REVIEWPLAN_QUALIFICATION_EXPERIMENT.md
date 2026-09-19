# EXP-0021: Synthetische Docker-Äquivalenz des Calibre-Reviewplan-Laufwegs

Status: ACCEPTED

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

not executed. Vor der Ausführung werden das eigene Docker-Profil, der
synthetische Runner und die externe Werkzeugbewertung getrennt implementiert
und geprüft.
