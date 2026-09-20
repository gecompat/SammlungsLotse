# WI-0020 Docker-Preimage

Status: PREIMAGE — NICHT AUSFÜHRBAR

Dieses Verzeichnis beschreibt ausschließlich die vorgesehenen lokalen
Docker-Eingänge für die read-only Calibre-Projektion. Es ersetzt weder das
Podman-Profil unter `runtime/calibre-readonly/` noch den öffentlichen
Produktvertrag.

Die Image-ID, die Basisimage-Config-ID und die vollständige Docker-
`Config.Env`-Projektion sind absichtlich noch nicht gebunden. Deshalb darf
`profile.json` nicht als Laufzeitprofil geladen und weder provisioniert noch
gestartet werden. Ein späterer eigener Arbeitsgegenstand muss diese Werte nach
einem reproduzierbaren, expliziten Docker-Build prüfen und erst danach das
Profil aktivieren.

Das vorgesehene Image bleibt Linux/amd64-gebunden, verwendet nur Calibre
`9.13.0` aus dem gebundenen Artefakt und führt ausschließlich die feste
`calibredb list`-Abfrage auf einer task-privaten Arbeitskopie aus. Docker wird
vor einem späteren Start separat auf Client und Server, Plattform, Image,
Entrypoint, Command, Environment und Isolation geprüft. Netzwerk, Persistenz,
Discovery, Import und sonstige Writer bleiben außerhalb.

Ein Bestandslauf darf weiterhin weder herunterladen noch bauen. Die
Preimage-Dateien enthalten absichtlich keinen Provisionierungs- oder
Ausführungsbefehl.
