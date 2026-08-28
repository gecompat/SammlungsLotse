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

## Geplantes enges WI-0007-Produktprofil

WI-0007 plant Calibre `9.13.0` als lokalen externen, read-only verwendeten
Bestandsprovider. Calibre ist GPL-3.0-only; das offizielle Linux-x86_64-
Artefakt wird nicht in Git aufgenommen und vor einem Image-Build gegen Größe
192554776 Bytes sowie den offiziellen SHA-512-Wert
`c018cb47805040a9a83dc16986db618c539a7dc62f85da2760b7e22e0e8ada7533a01be797cdbd04a5d5f66c8efa2b0ac2db4819700e561351267cb4842a3fc6`
geprüft. Die aktuelle Version, Lizenz, Schnittstelle und Provenienz wurden am
2026-08-28 anhand offizieller Calibre-Quellen erneut bestätigt.

Der Adapter verwendet ausschließlich `calibredb list` über eine wegwerfbare
Arbeitskopie. Ein Bestandslauf lädt keine Drittsoftware und baut kein Image.
Das Produktimage wird nicht veröffentlicht; eine Distribution benötigt eine
eigene vollständige GPL-, Notice- und Quellbereitstellungsprüfung. Diese
Planungs-Wave führt noch keine Laufzeitabhängigkeit ein.
