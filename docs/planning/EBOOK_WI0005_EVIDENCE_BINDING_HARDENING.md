# WI-0010: WI-0005-Laufzeitpreimage vollständig binden

Status: DONE — IMPLEMENTIERT UND SYNTHETISCH QUALIFIZIERT

Stand: 2026-08-28

Artifact: WI-0010

## Anlass

Der eingecheckte WI-0005-Produktnachweis bindet Profil, Containerdefinition,
Executor und tiefe Adaptermodule. Der tatsächliche CLI-Lauf führt zusätzlich
den paketlosen Runner und weitere Module unter
`src/sammlungslotse/ebook_intake/` aus. Diese Dateien waren nicht vollständig
Bestandteil des Qualifikationsdigests. Eine spätere Änderung hätte deshalb
die bestehende Ergebnisdatei nicht in jedem Fall ungültig gemacht.

## Grenze

WI-0010 ist ausschließlich eine Härtungs- und Evidenzwave. Sie:

- bindet den Runner, das Paket-Initialisierungsmodul und alle Python-Module
  des Intake-Pakets automatisch an den WI-0005-Produktnachweis;
- verhindert durch einen Regressionstest, dass ein neues Intake-Modul
  ungebunden bleibt;
- erzeugt den bestehenden 12/12-Nachweis mit dem unveränderten exakten
  EPUBCheck-5.3.0-Profil neu;
- dokumentiert die getrennten aktiven synthetischen Grenzproben.

Sie ändert weder CLI und Ergebnisverträge noch Provider, Image, Executor,
Ressourcenwerte, Produktfunktion oder Nutzeroberfläche.

## Aktive Grenzproben

Am 2026-08-28 wurden auf Windows mit Python 3.12.10 und Podman 6.1.0 gegen
die unveränderte Image-ID des WI-0005-Profils getrennt ausgeführt:

- Netzwerk: ausschließlich Loopback und erfolglose externe Namensauflösung
  unter zurückgelesenem `NetworkMode=none`;
- Prozesse: aktiver Fork-Versuch endet an `PidsLimit=32` mit `Cannot fork`;
- Speicher: Allokation oberhalb 384 MiB endet bei identischer RAM-/Swap-
  Grenze mit OOM-Kill und Exit 137;
- CPU: vier Worker werden bei `NanoCpus=1000000000` aktiv gedrosselt;
- Unterbrechung: `Ctrl+C` während eines tatsächlichen EPUBCheck-Laufs
  entfernt Container und Task vollständig;
- Recovery: ein eindeutig eigener abgelaufener Crashrest wird vor einem
  erfolgreichen tatsächlichen EPUBCheck-Lauf entfernt;
- Eingang: 32 MiB plus ein Byte endet vor Task- und Prozesserzeugung
  fail-closed als `resource.input_limit_exceeded`.

Zwei gleichzeitig gestartete tiefe Läufe erzeugten getrennte Tasks und
Container und räumten vollständig auf, endeten unter gemeinsamer Last jedoch
beide als `not_assessed`. Parallelbetrieb wird dadurch nicht qualifiziert;
WI-0006 verarbeitet mehrere Eingänge weiterhin bewusst sequenziell.

## Akzeptanz

WI-0010 ist `done`, wenn:

1. alle Python-Dateien des Intake-Pakets, der Runner und die direkt
   ausgeführten WI-0005-Laufzeitdateien im Preimage enthalten sind;
2. ein Test jede neue ungebundene Intake-Datei erkennt;
3. die tatsächliche Podman-Qualifikation erneut 12/12 Kriterien erfüllt;
4. alle bestehenden Repository- und Registry-Prüfungen erfolgreich sind;
5. keine neue Produktwirkung oder Abhängigkeit entsteht.

## Umsetzung und Abnahme

Der WI-0005-Nachweis bindet nun automatisch alle Python-Dateien unter
`src/sammlungslotse/ebook_intake/`, das Paket-Initialisierungsmodul und den
paketlosen Runner. Das vollständige Preimage umfasst 22 Dateien. Der neue
Regressionstest vergleicht den eingecheckten Nachweis mit dem tatsächlichen
Paketbestand und wird bei jeder neu hinzukommenden ungebundenen Python-Datei
rot.

Die tatsächliche lokale Podman-Neuqualifikation bestand mit unveränderter
Image-ID erneut 12/12 Kriterien. Der erzeugte Nachweis war vollständig an die
22 erwarteten Dateien gebunden, hinterließ keine Container und verwendete
ausschließlich synthetische TEST-0001-Medien. Alle 136 Repository-Tests,
Registry- und Repository-Prüfung, TEST-0001, EXP-0002 bis EXP-0007, WI-0008,
WI-0009, `compileall` und `git diff --check` waren erfolgreich.

Damit ist die festgestellte Preimage-Lücke geschlossen. Die getrennten
aktiven Grenzproben erweitern die lokale Evidenz, werden aber nicht als neue
Produktoberfläche oder Qualifikation paralleler Ausführung dargestellt.
