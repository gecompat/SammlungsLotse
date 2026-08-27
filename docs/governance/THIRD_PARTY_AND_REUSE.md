# Drittmaterial und FolioTone-Wiederverwendung

Status: AUTHORITATIVE

## Lizenzgrenze

SammlungsLotse verwendet die MIT-Lizenz aus LICENSE.

Die übertragenen Foundation-Dateien behalten den gesonderten MIT-Hinweis unter
.ai/foundation/AI_REPOSITORY_FOUNDATION_NOTICE.md.

FolioTone verwendet auf dem geprüften Stand
08267eadf5aba3696fa3a24ef6b3a70f2174bf7e eine eigene
Attribution-and-Non-Commercial-Redistribution-Lizenz. Sie ist ausdrücklich
keine Open-Source-Lizenz.

Deshalb wird FolioTone-Code nicht automatisch unter die MIT-Lizenz von
SammlungsLotse gestellt.

## Anforderungen an eine Übernahme

Vor jeder Code-, Test-, Dokumentations- oder Fixture-Übernahme aus FolioTone
oder einem anderen Projekt sind zu dokumentieren:

- konkrete Quelldatei und Quellcommit;
- Urheber und weitere Beitragende;
- anwendbare Lizenz und erforderliche Hinweise;
- Recht zur Übernahme, Änderung und MIT-Weitergabe;
- Drittbestandteile und deren eigene Bedingungen;
- technische Abhängigkeiten und FolioTone-spezifische Kopplung;
- ausgewählter SammlungsLotse-Vertrag und zugehörige Tests.

Wenn die Rechtekette nicht eindeutig ist, wird nicht kopiert. Eine unabhängige
Neuimplementierung anhand eines SammlungsLotse-Vertrags bleibt möglich, sofern
keine geschützten Ausdrucksformen oder unzulässigen Bestandteile übernommen
werden.

## Provenienz

Übernommene Bestandteile erhalten einen Eintrag in einer späteren
Drittmaterial- oder Herkunftsübersicht. Commitnachweise und erforderliche
Copyright-Hinweise bleiben erhalten.

## Externe Abhängigkeiten

Neue Bibliotheken, Container, Datensätze, Modelle, Dienste und Werkzeuge
werden vor Aufnahme nach Wartung, Lizenz, Sicherheit, Datenschutz, Kosten,
Reproduzierbarkeit und Ausstiegsweg bewertet.

Öffentliche Verfügbarkeit oder kostenlose Nutzung ist kein Rechtenachweis.

## Enges WI-0005-Produktprofil

WI-0005 bindet drei externe Laufzeitbestandteile, ohne ihre Archive in Git
aufzunehmen oder sie automatisch während einer Medienprüfung zu beziehen:

| Bestandteil | Gebundene Version | Lizenz und Verwendung |
|---|---|---|
| W3C EPUBCheck | 5.3.0 | BSD-3-Clause; lokaler externer Konformitätsprüfer |
| Eclipse Temurin JRE | 21.0.12.1+1 | GPL-2.0-only WITH Classpath-exception-2.0; lokale Java-Laufzeit |
| Eclipse Temurin JDK | 21.0.12.1+1 | GPL-2.0-only WITH Classpath-exception-2.0; nur reproduzierbarer Build des kleinen Wrappers |
| Debian bookworm-slim | bookworm-20260824-slim | digestgebundenes lokales Basisimage mit paketbezogenen Debian-Lizenzen |

Versionen, offizielle URLs, Artefaktgrößen, SHA-256-Werte, Basisimage-Revision
und resultierende Linux/amd64-Image-ID stehen vollständig in
`runtime/ebook-deep-readonly/profile.json`. Die explizite Provisionierung
prüft vorhandene Cachedateien erneut und bricht bei jeder Abweichung ab. Das
Laufzeitimage wird in dieser Wave nicht veröffentlicht; eine spätere
Distribution verlangt eine eigene Lizenz- und Notice-Prüfung.
