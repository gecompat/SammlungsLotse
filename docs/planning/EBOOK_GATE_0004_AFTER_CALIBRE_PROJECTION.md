# GATE-0004: Nächste Wave nach der Calibre-Projektion auswählen

Status: AUSGEWERTET — WI-0008 AUSGEWÄHLT

Stand: 2026-08-28

Artifact: GATE-0004

## Entscheidung

Als nächste Wave wird WI-0008 ausgewählt: Der bestehende synthetische
Calibre-Produktnachweis wird reproduzierbar materialisiert und auf mehrere
gezielte Datensätze erweitert. Die Wave ändert weder den Nutzervertrag noch
die fünf ausgegebenen Felder von WI-0007. Sie verwendet keine realen
Bibliotheken und führt keine schreibende Produktfähigkeit ein.

Der heutige WI-0007-Nachweis belegt das exakte Produktprofil tatsächlich,
enthält aber nur einen Calibre-Datensatz. Die Erzeugung dieser synthetischen
Bibliothek ist zudem noch kein eingecheckter, eigenständig prüfbarer
Vertrag. Damit bleibt offen, ob die echte `calibredb`-Ausgabe für
Mehrfachautoren, Mehrsprachigkeit, mehrere Formate, fehlende Werte und
Unicode genauso streng, deterministisch und pfadfrei verarbeitet wird wie
die isolierten Produkttests es erwarten.

## Bewertete Optionen

| Option | Nutzwert | Hauptrisiko | Entscheidung |
|---|---|---|---|
| A — synthetischen Calibre-Vertrag härten | Schließt eine konkrete Evidenz- und Reproduzierbarkeitslücke im bereits akzeptierten Produktpfad. | Liefert bewusst keine neue Nutzerfunktion. | Ausgewählt als WI-0008. |
| B — mehrere Bibliotheken oder automatische Erkennung | Erleichtert größere lokale Bestände. | Erweitert Zielermittlung, Datenschutzfläche und Fehlerkopplung entgegen der ausdrücklich gewählten Einzelbibliotheksgrenze. | Vertagt. |
| C — neue Qualitätsfunktion wie Identität, externe Metadaten oder Routing | Kann später höheren fachlichen Nutzwert liefern. | Benötigt neue Fach-, Provider-, Daten- und Fehlerverträge; vorhandene Evidenz reicht noch nicht für eine kleine sichere Produktwave. | Getrennt neu bewerten. |

## Auswahlmaßstab

Die Optionen wurden nach Nutzwert, vorhandener Evidenzlücke, Datenschutz,
Kopplung, Reversibilität und bestehender Autorisierung verglichen. Option A
bleibt vollständig innerhalb der bereits akzeptierten WI-0007-Grenze und
verändert weder Provider, Version, Image, Runtime, Produktoberfläche noch
Bestandswirkung. Sie ist deshalb die kleinste überprüfbare Fortsetzung.

Option B widerspricht der für WI-0007 ausdrücklich gewählten Beschränkung
auf genau eine angegebene Bibliothek. Option C kann fachlich wertvoll sein,
würde aber ohne eigenen Vergleich und neue Verträge mehrere bislang offene
Entscheidungen vorwegnehmen.

## Erfüllung der Gate-Bedingungen

- mindestens drei getrennte Optionen sind bewertet;
- die ausgewählte Wave adressiert eine konkret belegte Evidenzlücke;
- Nutzer-, Provider-, Datenschutz- und Writer-Grenzen bleiben unverändert;
- ausschließlich synthetische TEST-0001-Medien dürfen verwendet werden;
- Produktcode darf erst nach Merge des angenommenen WI-0008-Vertrags
  geändert werden;
- ein grüner Foundation- oder Registry-Check ersetzt weder die tatsächliche
  Calibre-Qualifikation noch die vollständige Produktregression.

## Nicht autorisiert

GATE-0004 autorisiert keine Mehrbibliotheksverarbeitung, automatische
Erkennung, Remote- oder Content-Server-Verbindung, zusätzliche
Calibre-Felder, reale private Bestände, Persistenz, Browser, REST, Agents,
Import, Export, Metadatenänderung oder andere Writes.
