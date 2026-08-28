# GATE-0008: Fortsetzung nach WI-0011 ergebnisoffen bewerten

Status: AUSGEWERTET — OPTION A UND EXP-0009 AUSGEWÄHLT

Stand: 2026-08-28

Artifact: GATE-0008

## Zweck

Dieses Gate beantwortet noch nicht, was als Nächstes implementiert wird. Es
ordnet nach dem abgeschlossenen WI-0011:

- welche qualitätssteigernden Tätigkeiten grundsätzlich möglich sind;
- welche davon auf dem aktuellen Stand sinnvoll untersuchbar erscheinen;
- welche ohne neue Architektur-, Provider-, Persistenz- oder Writerbindung
  tatsächlich umsetzbar wären;
- welche Voraussetzungen, Abbruchkanten und getrennten Entscheidungen eine
  spätere Auswahl benötigt.

Eine Empfehlung in diesem Dokument war keine Annahme eines Experiments,
Arbeitsgegenstands, Providers oder Technologiepfads. Der Nutzer hat am
2026-08-28 ausdrücklich Option A gewählt. Dadurch ist ausschließlich das
getrennte Evidenzexperiment EXP-0009 angenommen; Produktcode, Provider- und
Technologiepfade bleiben unentschieden.

## Verifizierte Ausgangslage

WI-0011 ist auf `origin/main` integriert und post-merge validiert. Der enge
Produktweg kann genau ein explizites Eingangs-EPUB mit genau einem expliziten
Calibre-Datensatz aus genau einer lokalen Bibliothek read-only vergleichen.
Er verwendet:

- getrennte unveränderliche Snapshots;
- eine task-private Copy-on-read-Arbeitskopie der Calibre-Bibliothek;
- die unterstützte `calibredb`-CLI hinter einem providerneutralen Port;
- fünf getrennte Identitätsebenen für Byte, Paket, Repräsentation, Ausgabe
  und Werk;
- positive, negative und fehlende Evidenz sowie Enthaltung;
- pfadfreie deutsche und deterministische JSON-Ausgabe;
- fail-closed Ressourcen-, Fehler-, Abbruch-, Recovery- und Cleanupgrenzen;
- keine Netzwerk-, Persistenz-, Writer- oder Bestandswirkung.

Der synthetische Produktnachweis bestand 23/23 Kriterien. Diese Evidenz
belegt den engen Ablauf, nicht Genauigkeit oder Skalierung in realen
Sammlungen. Insbesondere sind automatische Kandidatensuche, mehrere Dateien,
IDs oder Bibliotheken, größere EPUBs, weitere Calibre-Felder, produktive
Last, externe Metadaten, Accessibility-Gesamtbewertung, Suche, Persistenz,
Routing, UI und Writes nicht qualifiziert.

## Qualitätssteigernde Tätigkeiten unabhängig von einer Produktwahl

Die folgenden Tätigkeiten können mehrere spätere Optionen verbessern. Die
Bewertung beschreibt nur Möglichkeit, erwartbaren Erkenntniswert und
Umsetzbarkeit; sie nimmt keine Tätigkeit als neue Wave an.

| Tätigkeit | Mögliche Qualitätssteigerung | Aktuelle Umsetzbarkeit | Wesentliche Grenze |
|---|---|---|---|
| Identitäts-Goldstandard verbreitern | Misst False Positives, False Negatives und Enthaltung je Ebene statt nur einzelner positiver Beispiele. | Hoch mit neuen synthetischen Sollpaaren und bestehenden fünf Ebenen. | Keine Aussage über reale Häufigkeiten; keine privaten Medien. |
| Schwierige Ausgabenbeziehungen ergänzen | Trennt Reprint, Revision, Übersetzung, Sammelband, Auszug, Leseprobe, DRM- oder beschädigte Variante genauer. | Hoch bis mittel; Oracles müssen fachlich eindeutig sein. | Unklare Fälle dürfen nicht künstlich eindeutig etikettiert werden. |
| Metadaten- und Unicode-Robustheit prüfen | Verbessert Personen-, Rollen-, Sprach-, Reihen- und Identifierbehandlung. | Hoch auf synthetischer Ebene. | Normalisierung ist keine bibliografische Wahrheit. |
| Property-, Mutations- und Differenztests | Findet instabile Parser-, ZIP-, Reihenfolge-, Grenz- und Determinismusfehler. | Hoch, lokal und ohne neue Produktfähigkeit. | Generierte Fälle brauchen gebundene Seeds und verständliche Oracles. |
| Ressourcen- und Skalierungsprofile messen | Belegt Laufzeit, Speicher, Kandidatenanzahl, Bibliotheksgröße und Abbruchverhalten. | Mittel mit synthetischen, stufenweise größeren Bibliotheken. | Der aktuelle 4-MiB-Vertrag wird nicht stillschweigend erweitert. |
| Provider- und Versionsdrift erkennen | Verhindert unbemerkte Änderungen von Calibre-Ausgabe, Image oder CLI-Semantik. | Hoch als read-only Vertrags- und Requalifikationsprüfung. | Ein Upgrade bleibt eine eigene Entscheidung und Qualifikation. |
| Reason-Codes und Review-Erklärung prüfen | Macht Enthaltung, Konflikte und nächste manuelle Prüfung verständlicher. | Hoch über Schema-, CLI- und Nutzerentscheidungsfälle. | Kein UI- oder Review-Workflow wird dadurch ausgewählt. |
| Datenschutz- und Leakage-Tests verbreitern | Prüft Pfade, Dateinamen, Rohstreams, Fehlertexte, Tempdaten und Abbruchreste. | Hoch, lokal und synthetisch. | Logging oder Telemetrie bleiben außerhalb, solange kein Vertrag existiert. |
| Adapter-Konformitätstests definieren | Erhält Austauschbarkeit und verhindert Calibre-Schemaeintrag in den Kern. | Hoch für den bestehenden Snapshot-Port. | Noch kein zweiter Provider und keine allgemeine Pluginarchitektur. |
| Lizenz-, Herkunfts- und Abhängigkeitsnachweise pflegen | Reduziert Wartungs- und Lieferkettenrisiken. | Hoch als wiederholbare Maintenance-Prüfung. | Ersetzt keine Produktqualifikation einer neuen Version. |
| Dokumentations- und Bedienungsproben | Findet missverständliche Rollen, Wirkungen, Prozesscodes und Grenzen. | Hoch mit synthetischen CLI-Szenarien. | Eine CLI-Probe belegt keine Browser- oder Endnutzer-UI. |

## Mögliche Fortsetzungen

### A — Identitäts- und Evidenzqualität härten

Ein getrenntes Experiment könnte den synthetischen Goldstandard für S3
erweitern und Precision, Recall, selektive Genauigkeit, Abdeckung,
Enthaltungsqualität und Erklärungsabdeckung je Identitätsebene messen.

- unmittelbarer Qualitätsnutzen: hoch, weil jeder spätere
  Bestandskandidatenweg von diesen Aussagen abhängt;
- neue Kopplung: niedrig;
- Umsetzbarkeit: hoch mit lokalen synthetischen Fixtures;
- Hauptrisiko: ein größerer kleiner Goldstandard könnte weiterhin fälschlich
  als Produktprognose gelesen werden;
- geeignete Form: zuerst Evidenzexperiment, noch keine neue Produktfunktion.

### B — Begrenzte Kandidatensuche in genau einer Bibliothek untersuchen

Ein Experiment könnte prüfen, ob aus genau einem Eingangs-EPUB über
unterstützte read-only Calibre-Such- und Projektionsbefehle eine begrenzte,
erklärbare Kandidatenmenge erzeugt werden kann, die anschließend einzeln den
WI-0011-Vertrag durchläuft.

- unmittelbarer Nutzwert: hoch, weil der Nutzer die externe Calibre-ID nicht
  mehr vorab kennen müsste;
- neue Kopplung: mittel durch Suchfelder, Queryvertrag, Kandidatenlimit,
  Ranking und Recall;
- Umsetzbarkeit: mittel, zunächst nur als synthetisches Experiment;
- Hauptrisiko: unvollständige Suche kann als vollständige Dublettenprüfung
  missverstanden werden, ungebremste Kandidatenmengen können Ressourcen
  binden;
- notwendige Vorbedingungen: konkrete Suchaufgaben, Recall-orientierte
  Oracles, harte Kandidaten- und Zeitgrenzen, sichtbarer Suchumfang und
  Enthaltung;
- geeignete Form: unterstützte CLI-Varianten vergleichen, ohne direkte
  Datenbanknutzung, Persistenz oder Produktübernahme.

### C — Read-only Bestandsqualitätsbefunde definieren

Auf der WI-0007-Projektion könnten leere, widersprüchliche oder auffällige
Titel-, Autoren-, Sprach- und Formatwerte als getrennte Beobachtungen für
manuelle Prüfung untersucht werden.

- unmittelbarer Nutzwert: mittel bis hoch für vorhandene Bestände;
- neue Kopplung: niedrig bis mittel;
- Umsetzbarkeit: mittel, weil Feldorakel und Fehlerkosten noch fehlen;
- Hauptrisiko: `leer`, ungewöhnlich oder uneinheitlich ist nicht automatisch
  falsch;
- notwendige Vorbedingungen: Nutzerprioritäten, feldbezogene Oracles,
  Provenienz, Enthaltung und keine globale Qualitätszahl;
- geeignete Form: zuerst Mess- und Befundvertrag, dann synthetisches
  Experiment.

### D — Explizite Mehrdatei- oder Mehr-ID-Vergleiche komponieren

WI-0006 und WI-0011 könnten sequenziell für ausdrücklich zugeordnete Paare
ausgeführt werden.

- unmittelbarer Nutzwert: mittel durch weniger Einzelaufrufe;
- neue Kopplung: mittel durch Zuordnung, Teilfehler, Resume, Summenlimits und
  Ergebnisgröße;
- Umsetzbarkeit: technisch mittel, fachlich erst nach Festlegung der
  Zuordnungssemantik;
- Hauptrisiko: Batch-Komfort wird mit automatischer Kandidatenauswahl
  verwechselt;
- geeignete Form: erst nach Entscheidung, ob explizite Paarlisten überhaupt
  ein relevantes Nutzerproblem lösen.

### E — Mehrere Bibliotheken und Routing untersuchen

Mehrere getrennte Calibre-Bibliotheken könnten als mögliche Ziele oder
Bestandsquellen betrachtet werden.

- unmittelbarer Nutzwert: potenziell hoch für S6;
- neue Kopplung: hoch durch Bibliotheksidentität, Konfiguration,
  Zielzustände, Klassifikation, Regeln und Konflikte;
- Umsetzbarkeit: nur sinnvoll mit synthetischen Zielregeln und eindeutigen
  sowie mehrdeutigen Routing-Oracles;
- Hauptrisiko: eine Bestandsfundstelle wird fälschlich zur Ziel- oder
  Importentscheidung;
- geeignete Form: nicht mit Suche, Import oder Writer bündeln; frühestens ein
  eigenständiges Routingexperiment.

### F — Bibliografische Konflikte read-only erklären

Eingebettete EPUB-Metadaten und die minimale Calibre-Projektion könnten als
getrennte Beobachtungsquellen für S4 verglichen werden.

- unmittelbarer Nutzwert: hoch bei tatsächlichen Konflikten;
- neue Kopplung: mittel durch Feld-, Rollen-, Gegenstands- und
  Provenienzmodell;
- Umsetzbarkeit: mittel mit synthetischen Konfliktfällen;
- Hauptrisiko: Quelle oder Normalisierung wird zur kanonischen Wahrheit;
- geeignete Form: feldweise Kandidaten und Enthaltung, kein Schreiben und
  noch keine externe Providerwahl.

### G — Format- und Accessibility-Evidenz vertiefen

EPUBCheck-Befunde und die noch nicht produktqualifizierte Ace-Evidenz könnten
für getrennte Qualitätsdimensionen neu bewertet werden.

- unmittelbarer Nutzwert: mittel bis hoch für Qualitätsreview;
- neue Kopplung: mittel bis hoch bei einem weiteren Werkzeugprovider;
- Umsetzbarkeit: EPUBCheck-seitig hoch, Ace-seitig wegen bestehender
  Sicherheits- und Abhängigkeitsrisiken derzeit begrenzt;
- Hauptrisiko: automatische Prüfung wird als vollständige
  Accessibility-Bewertung dargestellt;
- geeignete Form: zuerst aktuelle Sicherheits-, Wartungs- und
  Evidenzqualifikation; keine stillschweigende Produktübernahme.

### H — Strukturierte, Volltext- oder semantische Suche beginnen

S5 verspricht hohen sichtbaren Nutzwert, benötigt jedoch Suchaufgaben,
Objektgrenzen, Extraktion, Indexlebenszyklus, Datenschutz, Regeneration und
Leistungsziele.

- unmittelbarer Nutzwert: potenziell sehr hoch;
- neue Kopplung: hoch bis sehr hoch;
- Umsetzbarkeit: Experimente sind möglich, eine Produktwahl ist noch nicht
  reif;
- Hauptrisiko: Index- oder Modelltechnik prägt das Kernmodell vor einem
  Aufgaben-Goldstandard;
- geeignete Form: Suchaufgaben und Oracles zuerst, strukturierte Suche,
  Volltext und Semantik getrennt untersuchen.

### I — Persistenz, Review-Oberfläche, REST oder Agents auswählen

Diese Zugänge können Bedienbarkeit und Wiederaufnahme verbessern, benötigen
aber Datenlebenszyklus, Berechtigungen, Versionierung, Pagination,
Löschkonzept, Betriebsmodell und tatsächliche Oberflächenabnahme.

- unmittelbarer Nutzwert: abhängig vom gewählten Nutzerablauf;
- neue Kopplung: sehr hoch;
- Umsetzbarkeit: technisch möglich, fachlich ohne ausgewählten persistenten
  Ablauf verfrüht;
- Hauptrisiko: Transport und Speicherung werden zur Architekturentscheidung,
  bevor der Nutzwert geklärt ist;
- geeignete Form: nicht als nächste kleine E-Book-Wave.

### J — Import, Format-, Metadaten- oder andere Bestandsoperationen

Schreibende Operationen könnten später manuellen Aufwand direkt reduzieren.
Jeder Operationstyp benötigt jedoch eine eigene vollständige
Autorisierungs-, Vorschau-, Idempotenz-, Nachprüfungs- und Recoverykette.

- unmittelbarer Nutzwert: potenziell hoch;
- Fehlerwirkung: kritisch;
- Umsetzbarkeit: vor eigenem Writer-Gate nicht autorisiert;
- Hauptrisiko: Kandidat, Routingvorschlag oder Qualitätsbefund wird zur
  Schreibfreigabe;
- geeignete Form: derzeit nicht verfolgen.

### K — Pausieren und nur Maintenance betreiben

Das Projekt könnte nach dem abgeschlossenen engen Vertikalweg keine neue
Produktfläche öffnen und nur Profile, Abhängigkeiten, Nachweise,
Dokumentation und Sicherheitsbefunde aktuell halten.

- unmittelbarer Nutzwert: Erhalt der Verlässlichkeit und maximaler
  Ausstiegsweg;
- neue Kopplung: keine;
- Umsetzbarkeit: hoch;
- Hauptrisiko: bekannte Nutzerfragen bleiben ungelöst;
- geeignete Form: valide Option, insbesondere wenn kein nächster Nutzwert
  priorisiert werden soll.

## Einordnung vor der Auswahl

Die kleinste kurzfristig sinnvolle Entscheidungsmenge besteht aus A, B, C
und K:

1. **A — Identitätsqualität härten** besitzt den höchsten direkten
   Qualitätshebel bei der geringsten neuen Kopplung. Diese Bewertung war die
   Grundlage der späteren ausdrücklichen Auswahl.
2. **B — Kandidatensuche experimentieren** schließt die größte sichtbare
   Lücke im aktuellen Nutzerablauf, benötigt aber vor Produktcode einen
   Suchaufgaben- und Recallvertrag.
3. **C — Bestandsqualitätsbefunde definieren** kann hohen read-only Nutzen
   liefern, benötigt zuerst feldbezogene Nutzerprioritäten und Oracles.
4. **K — pausieren** bleibt der sauberste Ausstiegsweg.

D bis G können später sinnvoll sein, bündeln derzeit aber mehr offene
Fachverträge oder Voraussetzungen. H und I benötigen eigenständige
Architekturentscheidungen. J bleibt hinter einem Writer-Gate.

## Kanten, die nicht stillschweigend überschritten werden

- Ein größerer Goldstandard ist keine Aussage über reale Sammlungsqualität.
- Kandidatensuche ist keine vollständige Dublettenprüfung.
- Eine gefundene Calibre-ID ist keine Ziel-, Import- oder Löschentscheidung.
- Mehrere Bibliotheken werden nicht als bloße Schleife über einen
  Einzelbibliotheksvertrag eingeführt.
- Leere oder ungewöhnliche Metadaten werden nicht automatisch zu Fehlern.
- Ein Score ersetzt keine einzelnen Qualitätsbefunde oder Gegenbelege.
- Ein Suchindex wird nicht zur kanonischen Bestandswahrheit.
- UI, REST oder Agents erhalten keine Sonderrechte und werden nicht vor dem
  Anwendungsvertrag ausgewählt.
- Provider-, Runtime-, Image- oder Limitänderungen erfordern neue Evidenz.
- Reale private Medien oder Sammlungsinventare gelangen nicht in Git oder
  externe Dienste.
- Keine Empfehlung in diesem Gate autorisiert Produktcode oder Writes.

## Gate-Ergebnis

Der Nutzer hat am 2026-08-28 **A — Identitäts- und Evidenzqualität härten**
ausgewählt. GATE-0008 ist damit ausgewertet. Als einzige direkte Folge ist
[EXP-0009](EBOOK_IDENTITY_EVIDENCE_HARDENING_EXPERIMENT.md) angenommen und
registriert. Das Experiment verbreitert den synthetischen Goldstandard,
misst den unveränderten WI-0009-Produktdienst und darf auch Produktlücken als
gültigen Erkenntnisbefund liefern.

B bis K bleiben katalogisierte Alternativen und sind weder verworfen noch
angenommen. Die Auswahl autorisiert insbesondere keine Kandidatensuche,
Produktänderung, Architektur, Provider-, Persistenz-, UI-, API-, Agent- oder
Writerfläche. Nach EXP-0009 ist vor jeder solchen Fortsetzung erneut getrennt
zu entscheiden.
