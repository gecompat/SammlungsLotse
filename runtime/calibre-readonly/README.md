# WI-0007-Laufzeitprofil und WI-0008-Qualifikation

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

Der tatsächliche WI-0008-Lauf erzeugt ausschließlich unter
`C:\rep\tmp\SammlungsLotse` zwei frische synthetische Bibliotheken aus dem
eingecheckten Manifest und den hashgebundenen TEST-0001-Fixtures. Vorhandene
Ziele und Pfade außerhalb dieses Temp-Unterbaums werden abgelehnt:

    python tools/qualify_calibre_readonly_profile.py --qualification-root C:\rep\tmp\SammlungsLotse\wi-0008-qualification --result C:\rep\artifacts\SammlungsLotse\wi-0008-qualification.json

Der Lauf prüft die reale Drei-Datensatz-Projektion, zwei semantisch gleiche
Materialisierungen, deutsche und stabile JSON-Ausgabe sowie Cleanup bei
Erfolg, Timeout, Outputgrenze und Abbruch. Der Qualifikationsroot wird danach
vollständig entfernt. Das schreibende Materialisierungswerkzeug gehört nur
zum synthetischen Testweg und ist nicht aus der Produkt-CLI erreichbar.

Die netzwerklose CI-Prüfung validiert nur den eingecheckten, an Profil,
Image-ID, Manifest-, Materialisierungs- und Produktpreimage gebundenen
v2-Nachweis:

    python tools/qualify_calibre_readonly_profile.py --validate-result
