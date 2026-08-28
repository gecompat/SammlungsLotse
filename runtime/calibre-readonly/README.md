# WI-0007-Laufzeitprofil

Status: PRODUCT PROFILE — LOCAL, EXPLICIT, DIGEST-BOUND

Dieses Verzeichnis bindet die read-only Bestandsprojektion an Calibre
`9.13.0`, Linux/amd64 und Podman. Calibre bleibt führendes Fachsystem. Das
Original wird vollständig gesnapshottet, aber nur eine task-private Kopie wird
beschreibbar unter `/library` in den netzwerklosen Container eingebunden.

## Bereitstellung

Ein Bestandslauf lädt und baut nichts. Das lokale Image wird vorher
ausdrücklich bereitgestellt:

    python tools/provision_calibre_readonly_profile.py --cache-root C:\rep\cache\SammlungsLotse\calibre-readonly

Downloadgröße, SHA-512, Basisimage, Plattform, Entrypoint und resultierende
Image-ID werden geprüft. Das Image wird nicht veröffentlicht; Distribution
verlangt eine eigene GPL-, Notice- und Quellbereitstellungsprüfung.

## Expliziter Nutzerlauf

    python tools/run_calibre_inventory.py --temp-root C:\rep\tmp\SammlungsLotse\calibre-readonly CALIBRE_BIBLIOTHEK

    python tools/run_calibre_inventory.py --json --temp-root C:\rep\tmp\SammlungsLotse\calibre-readonly CALIBRE_BIBLIOTHEK

Genau eine lokale Bibliothek ist erforderlich. Mehrfachziele, automatische
Erkennung, Content Server, URLs, Persistenz und Writes sind nicht enthalten.
Die Ausgabe enthält nur Calibre-ID, Titel, Autoren, Sprachen und normalisierte
Formate. Sie kann private Sammlungsmetadaten enthalten und darf nicht
ungeprüft protokolliert oder versioniert werden.

## Qualifikation und CI-Prüfung

Der tatsächliche Lauf verwendet nur eine unter `C:\rep\tmp` aus TEST-0001
erzeugte synthetische Calibre-Bibliothek:

    python tools/qualify_calibre_readonly_profile.py --library C:\rep\tmp\SammlungsLotse\wi-0007-qualification\library --temp-root C:\rep\tmp\SammlungsLotse\wi-0007-qualification\tasks --result C:\rep\artifacts\SammlungsLotse\wi-0007-qualification.json

Die netzwerklose CI-Prüfung validiert nur den eingecheckten, an Profil,
Image-ID und Produktpreimage gebundenen Nachweis:

    python tools/qualify_calibre_readonly_profile.py --validate-result
