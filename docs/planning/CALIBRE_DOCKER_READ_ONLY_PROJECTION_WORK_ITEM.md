# WI-0020: Docker-gebundene read-only Calibre-Projektion

Status: ACCEPTED

Stand: 2026-09-20

Artifact: WI-0020

## Ziel

Für genau eine explizite Calibre-Bibliothek wird die bestehende minimale,
pfadfreie read-only Projektion über einen eigenen Docker-Adapter qualifiziert.
Calibre bleibt führend; Podman bleibt ein unabhängiger optionaler Adapter.

## Grenzen

Das Docker-Profil, Image, Client/Server, Plattform und Inspect-Projektion sind
eigenständig gebunden. Kein Fallback zwischen Runtimes ist zulässig.
Nur eine task-private Copy-on-read-Bibliothek darf `calibredb list` mit der
bestehenden Feldwhitelist erreichen. Netzwerk, Persistenz, Discovery,
Mehrbibliotheken, Writer und automatische Downloads bleiben ausgeschlossen.
EXP-0022 bleibt `not_qualified`; WI-0020 behauptet keine Runtimeäquivalenz.

## Akzeptanz

1. Abweichendes Docker-Profil, Image, Inspect oder Plattform stoppt vor Start.
2. Quelle, Copy-on-read und Cleanup bleiben hashgebunden und fail-closed.
3. Docker läuft netzwerklos, unprivilegiert sowie ressourcen- und
   outputbegrenzt; nur die gebundene Calibre-Abfrage ist erlaubt.
4. Zwei synthetische Läufe liefern byteidentisches pfadfreies JSON oder eine
   ausdrücklich versionierte Alternative.
5. Timeout, Unterbrechung, Outputgrenze, Quellmutation und Cleanupfehler
   ergeben keine Projektion; Container und Taskdaten werden entfernt.
6. Ein Docker-E2E-Nachweis bindet Produktpreimage und Evidenz; sein
   CI-Validator startet weder Docker noch Netzwerk.

## Nichtziele

Kein Entfernen oder Lockern des Podman-Wegs, keine Mehrbibliothekslogik, kein
Import und keine Produktpersistenz.
