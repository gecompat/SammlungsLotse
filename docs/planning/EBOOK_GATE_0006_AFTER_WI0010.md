# GATE-0006: Nächste Evidenzfrage nach WI-0010 auswählen

Status: AUSGEWERTET — EXP-0008 AUSGEWÄHLT

Stand: 2026-08-28

Artifact: GATE-0006

## Entscheidung

Als nächste getrennte Wave wird EXP-0008 ausgewählt. Das Experiment prüft
ausschließlich mit synthetischem TEST-0001-Material, ob Calibre für genau
einen ausdrücklich gewählten externen Datensatz ein EPUB über die
unterstützte `calibredb`-CLI in eine task-private Übergabe exportieren kann.

Die Auswahl schließt die von GATE-0005 vertagte Erkenntnislücke zwischen der
minimalen Calibre-Bestandsprojektion aus WI-0007 und dem lokalen
Identitätskandidatenbericht aus WI-0009. Sie führt noch keine
Produktkopplung ein und entscheidet weder, dass ein solcher Vergleich
produktseitig sinnvoll ist, noch wie ein späterer Nutzerablauf aussehen soll.

## Aktuelle technische Ausgangsevidenz

Die lokal installierte, durch WI-0007 gebundene Calibre-Version 9.13.0 bietet
mit `calibredb export` eine dokumentierte Auswahl über konkrete externe IDs
und einen Formatfilter. Der Default aktualisiert beim Export Metadaten im
ausgegebenen E-Book. EXP-0008 muss deshalb `--dont-update-metadata` erzwingen
und die resultierenden Bytes selbst prüfen.

Eine nicht eingecheckte synthetische Auswahlprobe mit der exakten Image-ID
`sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5`
exportierte Datensatz `1` mit `--formats EPUB`,
`--dont-update-metadata`, ohne OPF, Cover oder Extra-Dateien. Das resultierende
EPUB war mit SHA-256
`1d98510717f6c3f22b3219bdedf8cbdf38785f060bfca0522f66ccf374f684a5`
bytegleich zum gebundenen TEST-0001-Eingang. Diese Probe begründet nur die
Experimentauswahl; sie ist kein reproduzierbarer Qualifikationsnachweis.

## Bewertete Optionen

| Option | Möglicher Nutzwert | Schwerstes Risiko | Entscheidung |
|---|---|---|---|
| A — unterstützte Einzelrecord-EPUB-Übergabe untersuchen | Kann einen ausdrücklich gewählten Calibre-Datensatz ohne interne Datenbankkopplung als begrenzte Evidenz für einen späteren Vergleich bereitstellen. | Der Export könnte Medien verändern, falsche oder mehrere Datensätze liefern oder Locators offenlegen. | Als EXP-0008 ausgewählt; Bytegleichheit, genaue Kardinalität und Fail-closed-Verhalten sind Pflicht. |
| B — Qualitätsübersicht aus den fünf WI-0007-Feldern bilden | Könnte Lücken bei Titel, Autoren, Sprachen oder Formaten sichtbar machen. | Die Felder tragen noch kein mehrdimensionales Qualitätsorakel; eine Zusammenfassung könnte leere Werte vorschnell als Fehler bewerten. | Vertagt, bis konkrete Nutzerfrage und Messvertrag getrennt vorliegen. |
| C — mehrere Bibliotheken entdecken, vergleichen oder routen | Nähert sich dem Ziel mehrerer Teilbibliotheken. | Erweitert Ziel-, Datenschutz-, Konfigurations- und Betriebsfläche gleichzeitig und könnte automatische Erkennung mit Routing vermischen. | Nicht als nächste kleine Wave geeignet. |
| D — externe Metadaten, Accessibility, Suche, Persistenz oder UI beginnen | Kann später fachliche Reichweite und Bedienbarkeit erhöhen. | Benötigt neue Provider-, Netzwerk-, Datenhaltungs- oder Architekturentscheidungen und ist nicht reversibel genug für die aktuelle Erkenntnislücke. | Getrennt offenhalten. |
| E — nur pausieren oder weitere bestehende Nachweise härten | Vermeidet jede neue Schnittstellenfrage. | WI-0010 hat die konkrete bekannte Preimage-Lücke bereits geschlossen; ohne neue Evidenz bleibt der vertagte Calibre-Abgleich ungeklärt. | Derzeit nicht bevorzugt; bei negativem EXP-0008-Ergebnis erneut möglich. |

## Auswahlmaßstab

Bewertet wurden unmittelbare Erkenntniswirkung, vorhandene synthetische
Grundlage, Kopplung, Datenschutz, Reversibilität, asymmetrische Fehlerkosten
und verbleibender Produktentscheidungsbedarf. Option A verwendet ein bereits
gebundenes lokales Werkzeugprofil und genau eine unterstützte Schnittstelle.
Sie kann vollständig mit wegwerfbaren Bibliotheken und ohne Produktcode
ausgeführt werden.

Die anderen Optionen beantworten die konkrete, seit GATE-0005 offene
Schnittstellenfrage nicht oder verbinden mehrere noch offene Produkt- und
Architekturentscheidungen. EXP-0008 ist deshalb die kleinste sichere
Erkenntniswave, nicht automatisch die nächste Produktwave.

## Gate-Folgen

- GATE-0006 ist mit dieser dokumentierten Auswahl `done`.
- EXP-0008 ist als eigener Experimentgegenstand `accepted`.
- Die Ausführung beginnt erst nach Merge dieser Planungs-Wave nach `main`.
- Ein positives Ergebnis belegt nur eine sichere technische
  Einzelrecord-Übergabe. Ein Produktvergleich gegen Calibre benötigt danach
  ein neues Gate und einen eigenen angenommenen Arbeitsgegenstand.
- Ein negatives Ergebnis führt fail-closed zur Neubewertung der Optionen;
  interne `metadata.db`-Kopplung wird dadurch nicht erlaubt.

## Nicht autorisiert

Nicht autorisiert sind Änderungen am Calibre-Quellbestand, direkter Zugriff
des SammlungsLotse-Produkts auf `metadata.db`, mehrere IDs, mehrere
Bibliotheken, automatische Erkennung, Content Server, Netzwerk, neue
Produktfelder, Produktcode, Vergleich oder Zusammenführung von Identitäten,
Persistenz, Routing, Browser, REST, Agents und jeder Writer.
