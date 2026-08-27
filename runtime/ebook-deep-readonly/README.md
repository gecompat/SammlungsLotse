# WI-0005-Laufzeitprofil

Status: PRODUCT PROFILE — LOCAL, EXPLICIT, DIGEST-BOUND

Dieses Verzeichnis bindet den ersten tiefen read-only Produktadapter an genau
EPUBCheck `5.3.0`, Eclipse Temurin `21.0.12.1+1`, Linux/amd64 und Podman. Der
Produktkern bleibt provider- und executorneutral. Das Profil ist weder ein
allgemeines Deploymentkonzept noch eine Freigabe weiterer Werkzeuge.

## Gebundene Bestandteile

- `profile.json`: vollständiges Provider-, Build-, Image-, Befehls-,
  Isolations-, Ressourcen-, Output- und Recovery-Preimage;
- `Containerfile`: digestgebundener, unprivilegierter Mehrstufen-Build;
- `EpubCheckWrapper.java`: kleiner Wrapper ohne Shell, der stdout und stderr
  begrenzt auffängt und das Output-tmpfs bis zum kontrollierten Kopieren des
  vollständigen JSON-Berichts gemountet hält;
- `qualification.json`: eingecheckter, mit ausschließlich synthetischen
  Eingängen erzeugter lokaler Podman-Nachweis.

Ein Provider-, Runtime-, Basisimage-, Befehls-, Executor- oder
Oberflächenwechsel erfordert eine neue Bewertung, ein neues Preimage und eine
frische Qualifikation. Die vorhandene Qualifikation darf dann nicht
weiterverwendet werden.

## Bewusste lokale Bereitstellung

Die Medienprüfung installiert oder lädt nichts automatisch. Das lokale Image
wird getrennt und ausdrücklich bereitgestellt:

    python tools/provision_ebook_deep_profile.py --cache-root C:\rep\cache\SammlungsLotse\ebook-deep-readonly

Das Werkzeug akzeptiert ausschließlich die in `profile.json` gebundenen
Artefaktgrößen und SHA-256-Werte, prüft das Basisimage sowie die gebaute
Image-ID und gibt keine Medieninhalte aus. Ein reproduzierbarer Build muss bei
zwei frischen Läufen dieselbe Image-ID liefern.

## Expliziter Nutzerlauf

Der bestehende Standardweg bleibt unverändert und startet kein tiefes
Werkzeug:

    python tools/run_ebook_intake.py --json <synthetische-oder-eigene-datei>

Erst der Opt-in-Schalter und ein ausdrücklich konfigurierter, nicht
versionierter Task-Root erlauben nach positivem Preflight den Adapter:

    python tools/run_ebook_intake.py --deep-read-only --deep-temp-root C:\rep\tmp\SammlungsLotse\ebook-deep-readonly --json <synthetische-oder-eigene-datei>

WI-0006 erlaubt mehrere ausdrücklich angegebene Dateien. Jeder positiv
freigegebene Snapshot erhält einen getrennten task-privaten Lauf; ein
geschlossenes Gate oder `not_assessed` überspringt keinen späteren Eingang:

    python tools/run_ebook_intake.py --deep-read-only --deep-temp-root C:\rep\tmp\SammlungsLotse\ebook-deep-readonly --json DATEI_A DATEI_B

Exitcode `0` bezeichnet eine abgeschlossene Werkzeugausführung, auch wenn
EPUBCheck einzelne Konformitätsbefunde liefert. Exitcode `4` bezeichnet
`not_assessed`, beispielsweise bei geschlossenem Gate, fehlender Laufzeit,
Timeout, Hashabweichung, ungültigem Bericht oder Cleanupfehler. Das Ergebnis
ist ausschließlich EPUBCheck-Konformitätsevidenz und keine Aussage über
Barrierefreiheit, Inhalt, Lesbarkeit, Authentizität oder Gesamtqualität.

## Qualifikation und CI-Prüfung

Der tatsächliche lokale Podman-Lauf verwendet nur TEST-0001-Medien und
schreibt sein zunächst nicht versioniertes Ergebnis unter `C:\rep\artifacts`:

    python tools/qualify_ebook_deep_profile.py --temp-root C:\rep\tmp\SammlungsLotse\wi-0005-qualification --result C:\rep\artifacts\SammlungsLotse\wi-0005-qualification.json

Die netzwerklose CI-Prüfung wiederholt weder Downloads noch Containerläufe:

    python tools/qualify_ebook_deep_profile.py --validate-result

Sie bindet den eingecheckten Nachweis an das aktive Profil, die Image-ID, die
aktuellen Fixture-Hashes, zwölf Akzeptanzwerte sowie die zurückgelesenen
Isolations-, Output- und Timeoutbelege.

Nach der WI-0006-Mehrdatei-Erweiterung wurde die vollständige Qualifikation
erneut ausgeführt, weil `cli.py` Teil des gebundenen WI-0005-Preimages ist.
Der eingecheckte Nachweis bindet deshalb auch die unveränderte Ein-Datei-
Kompatibilität des erweiterten CLI-Stands.
