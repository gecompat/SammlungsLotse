# WI-0011 Calibre-Identitäts-Handoff

`profile.json` bindet die enge lokale Produktgrenze für den read-only
Vergleich genau eines expliziten Eingangs-EPUB mit genau einem expliziten
Calibre-Datensatz. Das Profil verweist per SHA-256 auf das unveränderte
WI-0007-Laufzeitprofil und erlaubt ausschließlich den in EXP-0008
qualifizierten `calibredb export`-Aufruf.

Das Verzeichnis enthält keine Bibliothek, EPUB-Datei, Roh-Ausgabe oder
Taskdaten. Solche ausschließlich synthetischen Daten müssen unter den
kontrollierten Temp- und Artefaktpfaden außerhalb von Git bleiben.
