# Projektregeln

Status: AUTHORITATIVE

Diese Regeln ergänzen die AI Repository Foundation. Bei einem echten Konflikt
mit einer erforderlichen Foundation-Mindestregel ist der Konflikt vor der
Arbeit zu lösen.

## Verbindliche Lesereihenfolge

Vor einer wesentlichen Änderung sind abhängig vom Umfang zu lesen:

1. docs/project/PROJECT_STATUS.md;
2. docs/project/HANDOVER.md;
3. docs/product/PROJECT_CHARTER.md;
4. docs/architecture/BOUNDARIES.md;
5. docs/planning/README.md und .ai/artifact_registry.json bei Planung;
6. betroffene Dateien unter docs/decisions/;
7. docs/governance/DOCUMENTATION_STYLE.md bei Dokumentation;
8. docs/governance/VALIDATION.md vor Auswahl oder Ausführung von Prüfungen;
9. docs/reference/GLOSSARY.md bei Fachbegriffen;
10. docs/governance/THIRD_PARTY_AND_REUSE.md bei Übernahme, Abhängigkeiten oder
   externer Software.

## Projektphase

Das Projekt befindet sich vor der Entwicklungsplanung. Es existiert noch keine
freigegebene Produktarchitektur und keine Produktimplementierung.

Produktcode, Laufzeitabhängigkeiten und Infrastruktur werden erst nach einem
registrierten und angenommenen Arbeitsgegenstand eingeführt.

## Produktgrenzen

- Fachsysteme bleiben für ihre Domäne führend.
- SammlungsLotse unterstützt Analyse, Qualität, Suche und Orchestrierung.
- Externe Werkzeuge und Fachsysteme werden über austauschbare Adapter
  eingebunden.
- Fachsystemspezifische Schemata und Befehle enden am Adapter.
- REST, CLI, Browser und Agents verwenden dieselben Anwendungsverträge.
- Ein Zugangskanal umgeht keine Autorisierung oder Datenschutzregel.

## Datenschutz

- Reale private Medien, extrahierte private Inhalte und Sammlungsinventare
  werden nicht versioniert.
- Tests und Beispiele verwenden minimale synthetische, gemeinfreie oder
  ausdrücklich weiterverteilbare Daten.
- Secrets, Tokens, private Schlüssel, lokale Laufzeitdaten, Datenbanken,
  Caches, Logs und Analyseergebnisse werden nicht versioniert.
- Absolute private Pfade, Benutzernamen und Hostnamen werden nicht in
  Dokumentation, Tests oder Diagnosen übernommen.
- Externe Anfragen übertragen nur die erforderlichen strukturierten Angaben.
- Netzwerkzugriff ist explizit, begrenzt und nachvollziehbar.

## Schreibende Operationen

Read-only-Analyse ist der Ausgangspunkt.

Jeder schreibende Operationstyp benötigt vor seiner Implementierung:

1. eine angenommene technische Entscheidung;
2. genaue Ziel- und Berechtigungsgrenzen;
3. Vorbedingungen und erneute Zustandsprüfung;
4. Vorschau oder prüfbaren Plan;
5. explizite Autorisierung;
6. begrenzte Ausführung über eine unterstützte Schnittstelle;
7. Nachprüfung;
8. Fehler- und Wiederherstellungsverhalten.

Löschen, Verschieben, Umbenennen, Metadatenschreiben und Import sind getrennte
Operationstypen. Eine Freigabe ist nicht übertragbar.

## Artefakt- und Planungsautorität

.ai/artifact_registry.json ist die Registration Authority für dauerhafte
Projektartefakte. Die vollständigen Regeln stehen in
docs/governance/IDENTITY_AND_REGISTRATION.md.

Backlog- oder Roadmap-Dokumente dürfen die Registry später darstellen, werden
aber nicht zu einer konkurrierenden Autorität.

## Git-Arbeitsweise

- main bleibt stabil.
- Änderungen erfolgen über einen Feature-Branch und Pull Request.
- Eine Wave enthält einen zusammenhängenden, überprüfbaren Umfang.
- Unabhängige Änderungen werden nicht vermischt.
- Kein Force-Push auf gemeinsam verwendete Branches.
- Ein Merge erfolgt erst nach den für den Umfang erforderlichen Prüfungen.
- Nicht ausgeführte Prüfungen werden nicht als bestanden dargestellt.
- Projektstatus und Übergabe werden bei geänderten Fortsetzungsfakten
  aktualisiert.

## Dokumentation

Die erklärende Projektdokumentation ist deutsch. Öffentliche Literale,
Schnittstellen, Befehle, Schemanamen und technische Identifikatoren behalten
ihre kanonische Schreibweise.

README ist ein Einstieg und keine Kopie der Governance. Planung,
Implementierungsstand und Validierung bleiben getrennte Aussagen.

## Externe Werkzeuge und Abhängigkeiten

Vor einer Übernahme werden vorhandene gepflegte Fachwerkzeuge geprüft.
Aktuelle Primärquellen bestimmen Lizenz, Wartungsstand, Schnittstelle,
Versionierung, Datenschutz, Netzwerkverhalten und Schreibwirkung.

Ein Werkzeugergebnis ist Evidenz und keine ungeprüfte kanonische Wahrheit.
Ein Werkzeugausfall darf vorhandenen Zustand nicht beschädigen.

## Definition of Done

Eine Änderung ist abgeschlossen, wenn:

- ihr registrierter Umfang und die betroffenen Entscheidungen erfüllt sind;
- Verhalten und Dokumentation übereinstimmen;
- betroffene Tests und statische Prüfungen tatsächlich erfolgreich waren;
- Datenschutz-, Sicherheits- und Lizenzgrenzen eingehalten sind;
- abgeleitete Daten genügend Herkunfts- und Versionsangaben besitzen;
- Projektstatus und Übergabe den tatsächlichen Stand wiedergeben;
- bekannte Restprüfungen und Risiken ausdrücklich benannt sind.
