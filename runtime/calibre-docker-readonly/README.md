# WI-0020 Docker-Produktpreimage

Status: GEBUNDEN — E2E-QUALIFIKATION AUSSTEHEND

Dieses Verzeichnis beschreibt ausschließlich die vorgesehenen lokalen
Docker-Eingänge für die read-only Calibre-Projektion. Es ersetzt weder das
Podman-Profil unter `runtime/calibre-readonly/` noch den öffentlichen
Produktvertrag.

Die Image-ID, die Basisimage-Config-ID und die vollständige Docker-
`Config.Env`-Projektion sind an zwei frische, identische lokale OCI-Exporte
gebunden. `Config.Env`
enthält auch gebundene, vom Basisimage geerbte Werte und ist deshalb nicht mit
der festen Prozess-Whitelist gleichzusetzen: Der Entrypoint setzt die fünf
zugelassenen Prozesswerte mit `env -i` neu. Diese Bindung ist noch keine
Laufzeitqualifikation: Der synthetische WI-0020-E2E-Nachweis muss Image,
Plattform, Containerisolation, Projektion und Cleanup gegen dieses Profil
prüfen.

Das vorgesehene Image bleibt Linux/amd64-gebunden, verwendet nur Calibre
`9.13.0` aus dem gebundenen Artefakt und führt ausschließlich die feste
`calibredb list`-Abfrage auf einer task-privaten Arbeitskopie aus. Docker wird
vor einem späteren Start separat auf Client und Server, Plattform, Image,
Entrypoint, Command, Environment und Isolation geprüft. Netzwerk, Persistenz,
Discovery, Import und sonstige Writer bleiben außerhalb.

Ein Bestandslauf darf weiterhin weder herunterladen noch bauen. Die
Preimage-Dateien enthalten absichtlich keinen Provisionierungs- oder
Ausführungsbefehl.

Die zeitgebundene Quellen- und Sicherheitsbeobachtung für das aktuelle
Basisimage sowie die lokale Buildbindung stehen getrennt in
`SOURCE_ASSESSMENT.md`. Keine davon ersetzt die E2E-Qualifikation.
