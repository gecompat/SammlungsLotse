# EXP-0005: isolierte E-Book-Werkzeugausführung

Status: AUSGEFÜHRT — PASS

Stand: 2026-08-27

## Ergebnis

Ein versionsfestes EPUBCheck-Profil wurde unter Podman gegen synthetische
TEST-0001-Eingänge und gezielte Ressourcenproben ausgeführt. Alle elf
Akzeptanzprüfungen in [result.json](result.json) sind erfolgreich. Das
Experiment belegt diesen einen Linux/amd64-Ausführungsweg; es wählt weder
Produktlaufzeit noch Technologie-Stack oder gemeinsamen Spike-Unterbau.

## Werkzeug- und Ausführungsprofil

- Profil: `exp-0005-podman-epubcheck-5.3.0/v1`;
- EPUBCheck `5.3.0`, BSD-3-Clause, offizielles Release-Artefakt mit SHA-256
  `6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5`;
- Eclipse Temurin JRE `21.0.12+8`, offizielles Release-Artefakt mit SHA-256
  `8a379a67c91a3ae61ffb33d46e0a40c7ba35e70713c4db31cfca30492f792eff`;
- digest-gepinnte Python-Basis für die wegwerfbaren Proben;
- unprivilegierter Benutzer `65532:65532`, read-only Root und read-only
  Eingangsdatei, keine Linux-Capabilities und `no-new-privileges`;
- `network=none`, 32 Prozesse, eine CPU, 384 MiB ohne zusätzlichen Swap;
- 16 MiB tmpfs für temporäre Arbeit und 1 MiB tmpfs für Resultate;
- keine Containerlogs und exakt vier erlaubte Umgebungsvariablen.

Der Image-Build ist der einzige explizite Provisionierungsschritt mit
Netzwerkzugriff. Er lädt die beiden gepinnten öffentlichen Artefakte, prüft
ihre SHA-256-Werte und übernimmt die enthaltenen Lizenznachweise in das lokal
gebaute Image. Kein Drittanbieter-Binary wird versioniert oder veröffentlicht.
Alle Qualifikationsläufe selbst sind technisch netzwerklos.

Primärquellen:

- [EPUBCheck v5.3.0](https://github.com/w3c/epubcheck/releases/tag/v5.3.0);
- [EPUBCheck BSD-3-Clause](https://github.com/w3c/epubcheck/blob/v5.3.0/LICENSE.md);
- [Eclipse Temurin 21.0.12+8](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12%2B8);
- [offizielle Python-Image-Definition](https://github.com/docker-library/python/tree/f2c5d1b8a6adecb5b00b3c9331d4f863beade6b3/3.12/slim-trixie).

## Empirische Befunde

| Vertrag | Beobachtung |
|---|---|
| valider und ungültiger Eingang | je zwei Läufe; Exitcodes `0` und `1`; semantische Berichts-Digests innerhalb jeder Gruppe identisch |
| read-only Eingang | Schreibversuch scheitert mit `EROFS`; alle Vorher-/Nachher-Hashes gleich |
| Netzwerk | Verbindungsprobe scheitert unter geprüftem `NetworkMode=none` |
| Output/Platte | 4-MiB-Schreibversuch endet bei exakt 1 MiB mit `ENOSPC` |
| Speicher | 384-MiB-cgroup-Grenze beendet die Überallokation mit Exit `137` und `OOMKilled=true` |
| CPU | vier Lastprozesse verbrauchen zusammen rund 2,0 CPU-Sekunden in rund 2,0 Sekunden Wandzeit bei einer CPU |
| Zeit und Prozessbaum | 500-ms-Timeout beendet Haupt- und Kindprozess; der Container wird anschließend entfernt |
| Umgebung | nur `HOME`, `JAVA_HOME`, `LANG` und `PATH`; Host-Sentinel und Tokenvariablen fehlen |

Die unveränderten maschinenlesbaren Rohberichte liegen ausschließlich im
lokalen Artifact-Bereich. `result.json` enthält ihre Dateihashes, die
bereinigte Ausführungsprojektion und den zusammenfassenden Inhaltsdigest,
aber keinen privaten absoluten Pfad oder Hostnamen.

## Korpuskorrektur

Der erste reale EPUBCheck-Lauf deckte auf, dass TEST-0001 `0.1.0` im OPF das
Literal `version="3.3"` verwendete. EPUB-3.3-Publikationen verwenden dort
weiterhin `version="3.0"`. `0.1.0` bleibt deshalb als historischer Snapshot
unverändert; die korrigierte, erneut vollständig generierte und validierte
Fassung ist `0.2.0`. Der erfolgreiche EXP-0005-Nachweis verwendet nur
`0.2.0`.

## Vorläufige Läufe und Grenzen

Zwei Vorläufe wurden nicht als Erfolg umgedeutet:

1. Beim ersten Lauf ging tmpfs-Evidenz nach Containerende verloren. Daraufhin
   wurde die Evidenz vor dem kontrollierten Containerende kopiert.
2. Der zweite Lauf meldete 10/11, weil Podman `cap-drop=all` als vollständige
   Capability-Liste projiziert und weil der Korpusfehler sichtbar wurde.

Der abschließende Lauf qualifiziert nur Podman `6.1.0` auf Linux/amd64 mit
synthetischen kleinen Eingängen. Er trifft keine Aussage über private oder
große reale Sammlungen, andere Containerprovider oder die fachliche
Vollständigkeit von EPUBCheck.

## Reproduktion

Die Ausführung ist ein bewusster lokaler Experiment- und Provisionierungsschritt:

    python tools/experiments/run_exp_0005.py

CI führt keinen externen Download oder Containerlauf aus. Sie prüft stattdessen
Profil, Ergebnisvertrag, TEST-0001-Reproduzierbarkeit, Unit-Tests und
Repository-/Registry-Integrität:

    python tools/experiments/run_exp_0005.py --validate-result
