# WI-0020 Docker-Preimage: Quellen- und Sicherheitsbeobachtung

Status: OBSERVED_PREIMAGE — NICHT QUALIFIZIEREND

Stand: 2026-09-20

Diese Beobachtung aktualisiert ausschließlich den öffentlichen,
Linux/amd64-gebundenen Basisimage-Eingang des nicht ausführbaren WI-0020-
Preimages. Sie ist kein Produktprofil, kein Buildnachweis und keine
End-to-End-Qualifikation.

## Gebundene Beobachtung

Die offizielle Docker-Python-Referenz `3.12.14-slim-trixie` wurde am
2026-09-20 auf ihren damaligen Multi-Architektur-Index
`sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9`
aufgelöst. Die zugehörige Linux/amd64-Manifestreferenz lautet
`sha256:44ff437bba879d4941b710a369a8f19266aea34b29002807f0c487fabc9eec9b`;
deren OCI-Config-Digest lautet
`sha256:9e87977b867847e186d066f531ef783b006d582a985c341c269446088d90f2c4`.
Der Containerfile- und Profilverweis binden ausschließlich den Indexdigest.
Die Config-ID bleibt im Preimage absichtlich ungebunden und wird erst durch
einen späteren lokalen Build und `docker image inspect` zum Laufzeitvertrag.

Die Prüfung verwendete Docker Client und Server 29.8.0 auf Linux/amd64 sowie
Docker Scout 1.24.0. Für genau die öffentliche Registry-Referenz, Plattform
Linux/amd64 und nur fixierbare `critical`-/`high`-Befunde meldete Scout 0
kritische und 0 hohe Befunde. Die Beobachtung ist zeit- und datenbankgebunden;
sie ist keine dauerhafte Sicherheitszusage und deckt weder das spätere
Calibre-Artefakt noch ein gebautes WI-0020-Image ab.

Der zuvor gebundene Indexdigest
`sha256:7a8b475003c4fe15a2cd4e55e5cfc2f3560bdc9333d624f24cdd6d4340fd7a17`
meldete bei gleicher Plattform sechs kritische und zwölf hohe, fixierbare
Befunde. Er wird deshalb nicht weiter als WI-0020-Basisimage verwendet.

## Calibre- und Betriebsgrenzen

Die bestehende Calibre-Bindung bleibt unverändert: Version `9.13.0`,
GPL-3.0-only, offizielle Linux-x86_64-Quelle, 192554776 Bytes und der im
Profil hinterlegte SHA-512. Die Versionsbindung ist keine Aussage, dass 9.13.0
die aktuelle Calibre-Release ist. Eine Versionsänderung benötigt eine eigene
Bewertung.

Es wurde keine Calibre-Datei geladen, entpackt, gebaut oder gestartet und
keine Bibliothek verwendet. Ein späterer Schritt muss das Archiv erneut gegen
Größe und SHA-512 prüfen, den Build ausschließlich gegen den gebundenen Digest
ausführen, Image und Isolation auslesen sowie die synthetische WI-0020-
Qualifikation durchführen. Bis dahin bleiben Image-ID, vollständige
`Config.Env`, E2E-Evidenz und EXP-0025 ausdrücklich offen.

## Lokale Produktpreimage-Bindung

Nach erneuter lokaler Größen- und SHA-512-Prüfung des gebundenen
Calibre-9.13.0-Archivs lieferten zwei frische netzwerklose Linux/amd64-
BuildKit-OCI-Exporte mit Epochenzeitstempeln dieselbe lokale Image-ID
`sha256:c07a99a129439121a9839fcee58625c8b31d71a6f09fa3c4bddf7544695790b0`.
Image-Konfiguration und Layerfolge waren identisch. Der lokale Docker-
Inspectwert der Basisreferenz lautet der oben gebundene Indexdigest
`sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9`;
das Feld `base_image.config_id` bindet dagegen den oben dokumentierten
Linux/amd64-OCI-Config-Digest
`sha256:9e87977b867847e186d066f531ef783b006d582a985c341c269446088d90f2c4`.
Die vollständige `Config.Env`-Reihenfolge ist im Profil gebunden.

Dies ist ausschließlich ein gebundenes Produktpreimage. Es wurden keine
Container erstellt oder gestartet und keine Bibliothek verwendet. E2E-
Evidenz, zurückgelesene Containerisolation und EXP-0025 bleiben offen.
