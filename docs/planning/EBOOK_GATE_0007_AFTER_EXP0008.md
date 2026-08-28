# GATE-0007: Produktfortsetzung nach EXP-0008 auswählen

Status: AUSGEWERTET — WI-0011 AUSGEWÄHLT

Stand: 2026-08-28

Artifact: GATE-0007

## Entscheidung

Als nächste kleine Produktwave wird WI-0011 ausgewählt: ein read-only
Identitätskandidatenbericht zwischen genau einem ausdrücklich angegebenen
lokalen Eingangs-EPUB und genau einem ausdrücklich gewählten externen
Calibre-Datensatz aus genau einer lokalen Bibliothek.

Die Wave schließt den seit GATE-0005 vertagten kleinsten Bestandsvergleich.
WI-0009 stellt den fünfstufigen, erklärbaren Identitätsbericht bereit;
EXP-0008 belegt die bytegleiche, task-private Einzelrecord-EPUB-Übergabe über
die unterstützte Calibre-CLI. WI-0011 darf diese Verträge über einen neuen
providerneutralen Handoff-Port komponieren, aber weder Calibre-Schema noch
Experimentrunner zum Produktkern machen.

## Bewertete Optionen

| Option | Unmittelbarer Nutzwert | Schwerstes Risiko | Entscheidung |
|---|---|---|---|
| A — explizites Eingangs-EPUB gegen einen expliziten Calibre-Datensatz vergleichen | Beantwortet vor einer möglichen Integration die konkrete Frage, ob im führenden Fachsystem bereits dieselbe oder eine verwandte Repräsentation liegt. | Ein Kandidat könnte als Bestandswahrheit oder automatische Aktion missverstanden werden; Calibre-Kopplung könnte in den Identitätskern eindringen. | Als WI-0011 ausgewählt, nur mit fünf getrennten Evidenzebenen, Rollen, Enthaltung, providerneutralem Port und ohne Folgeaktion. |
| B — Qualitätslücken in der WI-0007-Bestandsprojektion zusammenfassen | Kann leere Titel-, Autoren-, Sprach- oder Formatwerte zur manuellen Prüfung bündeln. | Für die fünf Felder fehlen noch Nutzerpriorität, Fehlerkosten und ein Qualitätsorakel; leer ist nicht automatisch falsch. | Getrennt offenhalten. |
| C — mehrere Bibliotheken oder Routing beginnen | Nähert sich der Zielauswahl zwischen Teilbibliotheken. | Verbindet Zielmodell, Konfiguration, Erkennung, Klassifikation und Routing, obwohl der Einzelbestandsvergleich noch keinen Produktnachweis besitzt. | Nicht als nächste kleine Wave geeignet. |
| D — externe Metadaten, Accessibility, Suche, Persistenz oder UI beginnen | Kann Reichweite, Qualität oder Bedienbarkeit erhöhen. | Benötigt neue Provider-, Netzwerk-, Speicher- oder Architekturentscheidungen und beantwortet die bereits vorbereitete Bestandsfrage nicht. | Später getrennt bewerten. |
| E — nach EXP-0008 pausieren und keinen Produktpfad bilden | Bewahrt maximale Reversibilität. | Lässt eine nun technisch und fachlich eng begrenzbare Nutzerfrage trotz vorhandener Produkt- und Experimentgrundlage ungenutzt. | Derzeit nicht bevorzugt; bei gescheiterter WI-0011-Qualifikation erneut möglich. |

## Auswahlmaßstab

Bewertet wurden direkter Nutzerablauf, vorhandene Produkt- und
Experimentgrundlage, False-Positive-Kosten, Kopplung, Datenschutz,
Reversibilität und verbleibende Architekturentscheidungen. Option A benötigt
weder mehrere Bibliotheken, automatische Suche, neue Metadatenfelder,
Netzwerk noch Persistenz. Beide Eingänge und die Calibre-ID bleiben explizit;
der Bericht kann keine Bestandswirkung auslösen.

Die bestehende `IdentityCandidateService`-Anwendung akzeptiert bereits zwei
providerneutrale Snapshot-Reader. Der neue Calibre-Handoff kann nach
erfolgreichem, begrenztem Export ausschließlich unveränderliche Bytes und
pfadfreie Zustände liefern. Dadurch bleibt der Identitätskern frei von
Calibre-Befehlen, Arbeitsverzeichnissen und Datenbankschemata.

Option B benötigt zuerst einen eigenen Qualitätsmessvertrag. Optionen C und
D bündeln mehrere offene Entscheidungen. Option E bleibt eine valide
Rückfallentscheidung, besitzt nach dem positiven EXP-0008-Ergebnis aber
weniger unmittelbare Erkenntnis- und Nutzwirkung als der enge Vergleich.

## Gate-Folgen

- GATE-0007 ist mit dieser dokumentierten Auswahl `done`.
- WI-0011 ist als eigener read-only Arbeitsgegenstand `accepted`.
- Produktcode beginnt erst nach Merge dieser Planungs-Wave nach `main`.
- Der Calibre-Adapter bleibt austauschbar; nur ein providerneutraler
  Einzelrecord-Snapshotvertrag erreicht die Identitätsanwendung.
- Ein positiver Kandidat ist Evidenz für manuelle Prüfung, keine bestätigte
  Dublette, kein Importhindernis und keine Lösch-, Formatentfernungs- oder
  Metadatenfreigabe.
- Nach WI-0011 wird erneut getrennt bewertet; keine weitere Produktwave wird
  durch dieses Gate vorweggenommen.

## Nicht autorisiert

Nicht autorisiert sind automatische Calibre-Suche, mehrere IDs oder
Bibliotheken, andere Formate als EPUB, direkte `metadata.db`-Nutzung, neue
Calibre-Felder, Persistenz, Index, Routing, externe Provider, Netzwerk,
Browser, REST, Agents, Zusammenführung, Import, Formatentfernung,
Metadatenschreiben oder jede andere Bestandswirkung.
