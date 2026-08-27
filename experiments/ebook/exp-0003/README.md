# EXP-0003: EPUB-Konformitäts- und Accessibility-Evidenz

Status: AUSGEFÜHRT — PASS; ACE NICHT PRODUKTQUALIFIZIERT

Stand: 2026-08-27

## Ergebnis

EPUBCheck `5.3.0` und Ace by DAISY `1.4.6` wurden in getrennten
netzwerklosen Podman-Containern gegen sieben synthetische TEST-0001-Fälle
ausgeführt. Jeder Fall lief zweimal. Alle vierzehn Akzeptanzprüfungen in
[result.json](result.json) sind erfolgreich.

Der Versuch belegt, dass vollständige maschinenlesbare Rohberichte außerhalb
von Git erhalten und über Hashes und `raw_ref` verlustfrei mit einer engen
gemeinsamen Befundprojektion verbunden werden können. Toolcode,
Originalschweregrad, Ausgang, interne Fundstelle, Profil und Reviewbedarf
bleiben sichtbar. Er wählt weder Produktadapter noch Runtime oder gemeinsames
Qualitätsschema.

## Werkzeug- und Ausführungsprofile

EPUBCheck verwendet unverändert das in EXP-0005 qualifizierte Profil
`exp-0005-podman-epubcheck-5.3.0/v1`.

Ace verwendet das Profil `exp-0003-epubcheck-5.3.0-ace-1.4.6/v2`:

- Ace `1.4.6`, MIT, exaktes npm-Paket und vollständiger npm-Lock;
- offizielles Puppeteer-Image `24.43.1` per OCI-Digest;
- Node `24.15.0` und Chrome for Testing `148.0.7778.97`;
- unprivilegierter Benutzer `10042:10042`, read-only Root,
  `cap-drop=all`, `no-new-privileges` und `network=none`;
- read-only EPUB-Eingang und begrenzte tmpfs-Ausgabe;
- vier CPUs, 2 GiB ohne zusätzlichen Swap, 256 Prozesse, 60 Sekunden
  Containergrenze und 8 MiB je Ausgabedatei;
- minimierte, explizit erlaubte Prozessumgebung.

Image-Build und `npm audit` sind getrennte Provisionierungsschritte mit
Netzwerkzugriff. Alle eigentlichen Werkzeugläufe sind netzwerklos.

Primärquellen:

- [EPUBCheck v5.3.0](https://github.com/w3c/epubcheck/releases/tag/v5.3.0);
- [EPUBCheck-Repository und JSON-Ausgabe](https://github.com/w3c/epubcheck);
- [Ace v1.4.6](https://github.com/daisy/ace/releases/tag/v1.4.6);
- [Ace-CLI](https://daisy.github.io/ace/docs/cli/);
- [Ace-JSON-Bericht](https://daisy.github.io/ace/docs/report-json/);
- [Ace-Lizenz](https://github.com/daisy/ace/blob/v1.4.6/LICENSE.txt).

## Empirische Werkzeugbefunde

| Werkzeug/Fall | Rohbefund | Normalisierte Grenze |
|---|---|---|
| EPUBCheck, valides Reflow-EPUB | keine Meldung | kein erfundener Fehler; keine Accessibility-Aussage |
| EPUBCheck, fehlende Ressource | `RSC-001` | Integritätsbefund mit interner EPUB-Fundstelle |
| EPUBCheck, Navigationsdefekt | `RSC-007` | Formatbefund; Code und Fundstelle bleiben erhalten |
| EPUBCheck, aktiver/entfernter Inhalt | zweimal `OPF-014`, einmal `RSC-006` | `OPF-014` als Sicherheitsbefund; unbekanntes `RSC-006` bleibt sichtbar und reviewpflichtig |
| Ace, formatvalides Reflow-EPUB | sechs automatische Meldungen | kein allgemeines Accessibility-Konformitätsurteil |
| Ace, Bild ohne Textalternative | sieben Meldungen einschließlich `image-alt` | automatischer Accessibility-Befund mit CSS- und CFI-Zeiger |
| Ace, schwacher vorhandener alt-Text | sechs automatische Meldungen, kein `image-alt` | manueller Reviewbedarf stammt sichtbar aus dem TEST-0001-Oracle, nicht aus einer erfundenen Ace-Meldung |

Die semantischen Projektionsdigests beider Wiederholungen sind für alle sieben
Fälle identisch. Veränderliche Berichtszeitpunkte bleiben im vollständigen
Rohbericht, werden aber nicht zu semantischen Schlüsseln.

## Offener Ace-Sicherheitsbefund

Ace `1.4.6` ist durch dieses Experiment **nicht** für einen Produktbetrieb
qualifiziert:

- der offizielle Puppeteer-Runner startet Chromium fest mit `--no-sandbox`
  und `--disable-setuid-sandbox`;
- `npm audit --omit=dev` meldete am Ausführungstag 22 offene Befunde:
  14 `high`, acht `moderate`, keine `critical`;
- darunter liegen für die Dateiverarbeitung relevante transitive Befunde zu
  `extract-zip` sowie weitere Befunde in Puppeteer- und ungenutzten
  HTTP-Abhängigkeiten;
- der kleine Fall benötigte empirisch vier CPUs und eine Prozessgrenze von
  256; engere Vorprofile liefen in Chromium-Timeouts.

Der Versuch begrenzt dieses Risiko mit synthetischen Eingängen, read-only
Root und Input, Capability-Entzug, `no-new-privileges`, `network=none`, tmpfs
und Containerlöschung. Diese äußere Begrenzung ist kein Ersatz für eine
spätere Neuprüfung der Ace-Abhängigkeitskette.

## Vorläufige Läufe

Vorläufe wurden nicht als Erfolg umgedeutet:

1. Ace lief mit zwei CPUs beziehungsweise 128 Prozessen in reproduzierbare
   Chromium-Protokoll-Timeouts.
2. Der Host behandelte den erwarteten EPUBCheck-Exitcode `1` zunächst als
   Wrapperfehler.
3. Die Pfadprüfung verwechselte `raw://` zunächst mit einem
   Windows-Laufwerkspräfix.
4. Eine globale Prüfung beanstandete interne Containerziele aus der
   Sicherheitsinspektion; die strengere Sperre blieb für Standardprojektionen
   erhalten, während nichtprivate Containerpfade als Nachweis sichtbar sind.

Der abschließende Lauf begann danach vollständig neu.

## Grenzen

Es wurden nur kleine synthetische TEST-0001-Dateien verarbeitet. Vollständige
Rohberichte liegen ausschließlich im lokalen Artifact-Bereich; Git enthält
ihre Hashes und die referenzierenden Projektionen. Ace meldet bestandene
Einzeltests nicht im JSON-Bericht. Weder ein leerer noch ein erfolgreicher
automatischer Bericht begründet allgemeine Barrierefreiheit.

## Reproduktion

Der vollständige lokale Provisionierungs- und Experimentlauf lautet:

    python tools/experiments/run_exp_0003.py

CI lädt keine Werkzeuge und startet keinen Container. Sie prüft den
eingecheckten Ergebnisvertrag:

    python tools/experiments/run_exp_0003.py --validate-result
