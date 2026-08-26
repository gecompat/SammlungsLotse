# Produkt- und Systemgrenzen

Status: AUTHORITATIVE PRE-ARCHITECTURE

Dieses Dokument legt Grenzen fest, die vor der technischen Architektur gelten.
Es wählt noch keinen Technologie-Stack.

## Systemrollen

Das führende Fachsystem verwaltet die produktive Sammlung seiner Domäne.
SammlungsLotse verwaltet domänenübergreifende Beobachtungen, Evidenz,
Provenienz, Suchableitungen, Regeln, Vorschläge und Ablaufzustände, soweit dies
für seinen Auftrag erforderlich ist.

Ein Adapter übersetzt zwischen einem Fachsystem und den
Anwendungsverträgen von SammlungsLotse. Datenbanktabellen, Befehle und
herstellerspezifische DTOs eines Fachsystems werden nicht zum Kernmodell.

## Verarbeitungskette

Die grundsätzliche Verarbeitung ist:

    Entdecken
      -> Beobachten und analysieren
      -> Entitäten und Metadaten auflösen
      -> Dublettenkandidaten bewerten
      -> Qualität und Zielzuordnung bewerten
      -> Änderung vorschlagen
      -> Änderung autorisieren
      -> über Fachsystemadapter ausführen
      -> Ergebnis verifizieren

Eine spätere Implementierung darf Schritte zusammenfassen, aber keine
Schreibfreigabe oder Verifikation stillschweigend entfernen.

## Wahrheit und Evidenz

Rohwerte werden nicht durch Normalisierung oder Anreicherung vernichtet.
Beobachtete, abgeleitete, externe, kanonische und vom Nutzer bestätigte Werte
bleiben unterscheidbar.

Werkzeug-, Provider- und KI-Ergebnisse sind Evidenz. Sie werden nicht ohne
Prüfung zur alleinigen Wahrheit.

## Fachsysteme

Fachsysteme werden ausschließlich über dokumentierte und unterstützte
Automationsschnittstellen eingebunden. Direkte Änderungen an internen
Datenbanken eines Fachsystems sind kein regulärer Integrationsweg.

Ein Fachsystemadapter ist austauschbar. Sein Ausfall darf den vorhandenen
Sammlungszustand nicht beschädigen.

## Sammlungsaufteilung und Routing

Eine Domäne kann mehrere getrennte Zielbestände besitzen. Die E-Book-Linie
muss beispielsweise mehrere Calibre-Bibliotheken als eigenständige Ziele
modellieren können.

Routing ist eine nachvollziehbare Entscheidung mit Regelversion, Evidenz und
Prüfstatus. Eine Klassifikation allein ist keine automatische
Schreibfreigabe.

## Lese- und Schreibgrenze

Analyse ist standardmäßig read-only. Jede schreibende Fähigkeit erhält einen
engen Operationstyp, definierte Vorbedingungen, Autorisierung,
Änderungsnachweis, Verifikation und Wiederherstellung.

Löschen, Verschieben, Umbenennen, Retagging und Import sind getrennte
Operationstypen. Die Freigabe eines Typs gibt keinen anderen Typ frei.

## REST und Agents

Browser, CLI, REST-Clients und Agents verwenden dieselbe Anwendungsschicht.
Sie erhalten keinen direkten Zugriff auf Persistenz, lokale Mediendateien oder
interne Fachsystemdatenbanken.

Agent-Aktionen sind versioniert, begrenzt, wiederholbar und auditierbar.
Lesende und schreibende Werkzeuge werden getrennt angeboten.

## Datenschutz und Netzwerkeinsatz

Lokale Verarbeitung bleibt ohne Netzwerk sinnvoll. Externe Anfragen sind
explizit konfiguriert, minimiert und nachvollziehbar. Absolute lokale Pfade,
Sammlungsinventare und private Inhalte werden nicht ohne eigene Freigabe an
externe Dienste übertragen.

## Skalierung

Verarbeitung großer Sammlungen erfolgt inkrementell. Unveränderte Dateien und
unveraltete Analyseergebnisse werden nicht ohne Grund erneut verarbeitet.
Teure Vergleiche benötigen eine begrenzende Kandidatenerzeugung.
