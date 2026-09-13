# GATE-0025: Erste nutzbare E-Book-Reviewplanung auswählen

Status: DONE — OPTION A AUTONOM AUSGEWÄHLT

Stand: 2026-09-13

Artifact: GATE-0025

## Ausgangslage

Die vorhandenen E-Book-Bausteine sind einzeln read-only qualifiziert: ein expliziter Eingangsordner, die Projektion genau einer Calibre-Bibliothek, der Vergleich zweier EPUBs und der Vergleich eines EPUB mit einem bekannten Calibre-Datensatz. Sie bilden noch keinen Arbeitsablauf, mit dem ein Nutzer einen Eingang gegen einen Bestand prüfen kann. Insbesondere fehlen eine begrenzte Kandidatenerzeugung, eine zusammenhängende Reviewliste und ein erklärbarer, wirkungsloser Integrationsplan.

Der Nutzer hat am 2026-09-13 ausdrücklich die autonome Entwicklung eines tatsächlich nützlichen Ablaufs beauftragt. Diese Auswahl ersetzt keine Datenschutz-, Fachsystem- oder Schreibgrenze.

## Optionen

### A — Read-only Eingangs-zu-Calibre-Reviewplan vorbereiten

Ein neuer, ausschließlich synthetischer Experimentvertrag prüft zunächst, ob ein expliziter Eingangsordner und bis zu drei explizite, minimale Calibre-Projektionssnapshots deterministisch zu begrenzten Dublettenkandidaten und einer erklärbaren Reviewplanung verbunden werden können. Erst ein Ergebnisgate darf daraus einen Produktarbeitsgegenstand ableiten.

- Nutzen: verbindet vorhandene Bausteine zu dem ersten praktischen Nutzerablauf, ohne einen Bestand zu verändern.
- Risiko: Kandidatenerzeugung ist keine Vollständigkeits- oder Dublettenbehauptung; Unsicherheit und Grenztreffer müssen sichtbar bleiben.
- Wirkung: keine Produktcode-, Netzwerk-, Persistenz- oder Fachsystemwirkung.

### B — Suche oder Persistenz zuerst umsetzen

Nicht auswählen. Beide Flächen benötigen ein allgemeines Daten-, Aufbewahrungs- und Technologieentscheidungsmodell. Sie lösen das akute Problem der Eingangsbewertung nicht unmittelbar.

### C — Calibre-Import zuerst umsetzen

Nicht auswählen. Import ist eine schreibende Operation und benötigt einen eigenen angenommenen Adapter-, Autorisierungs-, Vorprüfungs-, Wiederherstellungs- und Nachprüfungsvertrag. Ohne prüfbaren Plan wäre er fachlich und sicherheitlich verfrüht.

### K — Bestehende Einzelbausteine konservieren

Nicht auswählen. Die bestehenden Nachweise bleiben unverändert erhalten, reichen aber allein nicht für den ausdrücklich verlangten Nutzablauf.

## Auswahl

Option A ist ausgewählt. EXP-0019 wird als neue, produktcodefreie Evidenzwave registriert. Es untersucht nur die begrenzte Verbindung von synthetischem Eingangsordner, Projektionssnapshots, Kandidatengründen und Reviewklassen. Ein erfolgreicher Experimentlauf ist keine Produktfreigabe; ein getrenntes Ergebnisgate entscheidet danach über einen angenommenen Produktarbeitsgegenstand.

## Zielbild der ersten Produktwave

Der spätere, noch nicht angenommene Nutzerablauf lautet: genau ein ausdrücklich gewählter Eingangsordner wird gegen eine ausdrücklich gewählte Calibre-Bibliothek geprüft. Er liefert je Eingang eine begründete manuelle Reviewentscheidung und höchstens einen nicht ausführbaren Integrationshinweis. Ein späterer Ausbau auf mehrere Bibliotheken bleibt im Experiment ausdrücklich getrennt; eine automatische Zielauswahl wird nicht behauptet.

## Harte Grenzen

- kein Import, keine Calibre- oder Dateischreiboperation, kein Verschieben, Umbenennen, Löschen oder Metadatenschreiben;
- kein direkter Zugriff auf Calibre-Datenbanken, kein Netzwerk und keine automatische Bibliotheksentdeckung;
- keine Persistenz, kein Index, keine Berichtdatei, kein Watcher und keine Benutzeroberfläche oder REST-Schnittstelle;
- keine reale oder private Sammlung, kein privater Inhalt, Pfad, Titel, Autor, Identifier, Hash oder Rohbericht in Git;
- eine Kandidatenliste beweist weder Vollständigkeit noch Dublettenidentität; `no_candidate_found` ist niemals ein Import- oder Neuheitsbeweis;
- bestehende Intake-, Deep-read-only-, Calibre- und Identitätsverträge bleiben unverändert.
