# EXP-0023: Linux-Zombie-Cleanup von EXP-0007 synthetisch requalifizieren

Status: DONE

Stand: 2026-09-20

Artifact: EXP-0023

## Anlass und Ziel

Die Linux-Repositoryprüfung hat einen tatsächlichen Prozessgruppen-Timeout aus
EXP-0007 als nicht bereinigt bewertet, obwohl der betroffene Kindprozess nur
noch als nicht fortsetzungsfähiger Zombie auf das Reaping wartete. Der
POSIX-Live-Check muss einen solchen Zustand von einem aktiven Kindprozess
trennen. EXP-0023 qualifiziert ausschließlich diese Korrektur mit
synthetischer, pfadfreier Evidenz erneut.

## Abgrenzung

- Keine Produktfunktion, öffentliche CLI, Provider-, Image- oder
  Containerprofilübernahme.
- Keine realen Medien, privaten Daten, Netzwerkzugriffe, Persistenz oder
  Schreibwirkung außerhalb eines temporären synthetischen Testbereichs.
- EXP-0007 `result.json` und seine gebundenen historischen Komponenten bleiben
  unverändert. Ein separater historischer Validator bewahrt deren Aussage auf
  dem ursprünglichen Git-Preimage.
- Der vorhandene Podman-Nachweis wird weder ersetzt noch erweitert; für diese
  eng begrenzte Prozesssemantik ist kein Containerlauf erforderlich.

## Vorabvertrag

Die Umsetzung darf nur den EXP-0007-Driver, fokussierte synthetische
Prozesszustandskontrollen sowie die dauerhafte historische Resultatprüfung
betreffen. Der aktuelle Driver muss einen POSIX-Zombie als nicht aktiv
erkennen, darf aber bei fehlender oder nicht lesbarer `/proc`-Evidenz nicht
stillschweigend Erfolg annehmen. Ein aktiver Kindprozess bleibt aktiv.

## Akzeptanz

1. Das historische EXP-0007-Ergebnis validiert weiterhin gegen seinen
   gebundenen Git-Commit und unveränderte Ergebnisbindungen, ohne den neuen
   Driver gegen den alten Hash zu prüfen.
2. Die synthetische Zombie-Kontrolle bewertet den Status `Z` als nicht aktiv;
   eine aktive Kontrolle bleibt aktiv.
3. Der bestehende Timeout-, Prozessgruppen-Kill- und Reap-Ablauf bleibt
   fail-closed; fehlende `/proc`-Evidenz gilt nicht als Zombie-Nachweis.
4. Die fokussierten und vollständigen Repositoryprüfungen bestehen unter der
   unterstützten CI-Python-Version.
5. Die Evidenz bleibt frei von PIDs, lokalen Pfaden, Roh-`/proc`-Zeilen,
   privaten Daten und Laufzeitresten.

## Ausführung und Abschlussgrenze

Zuerst wird der historische CI-Vertrag unabhängig vom aktuellen Driver
validiert. Danach prüfen unitäre synthetische Kontrollen die neue
Zustandstrennung. Ein eventuell späterer tatsächlicher Linux-Lauf benötigt ein
eigenes, vorab gebundenes Ergebnisartefakt; diese Wave behauptet keine
Neuausführung der historischen EXP-0007-Laufzeitqualifikation.

Ein bestandener Maintenance-Nachweis ist keine Produkt-, Runtime- oder
Adapterfreigabe.

## Ergebnis

Die getrennte historische Git-Preimage-Prüfung und die beiden synthetischen
POSIX-Zustandskontrollen bestanden. Der vollständige Repositoryadapter lief
lokal mit 300 Tests und vier fähigkeitsbedingten Skips; auf Pull Request 95
bestanden außerdem `repository-quality` und `registry-integrity` unter
GitHub-Linux. Damit ist der eng begrenzte Maintenance-Nachweis abgeschlossen.
Er behauptet keine erneute historische EXP-0007-Laufzeitqualifikation.
