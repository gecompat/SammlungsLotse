# Projektregeln

Status: AUTHORITATIVE

Diese Regeln ergänzen die AI Repository Foundation. Bei einem echten Konflikt
mit einer erforderlichen Foundation-Mindestregel ist der Konflikt vor der
Arbeit zu lösen.

## Auffindbarkeit und scopeabhängige Lektüre

Die vollständige Governance bleibt vom Root-Einstieg transitiv auffindbar.
Der Discoveryvalidator prüft alle kanonischen Quellen und angenommenen
Entscheidungen lokal. Das verlangt keine semantische Lektüre jeder verlinkten
Datei und keine Erfassung aller Entscheidungen im Modellkontext.

Zu Beginn einer Sitzung gelten die aktuelle native Instruction-Kette, das
kurze Foundation-Ruleset und diese Projektregeln. Für den konkreten Auftrag
werden die betroffenen Quellen und ihre transitiven semantischen Abhängigkeiten
ausgewählt. Bei Unklarheit wird die Auswahl erweitert. Lesereihenfolge nach
betroffener Grenze:

1. relevante aktuelle Abschnitte aus [Projektstatus](../project/PROJECT_STATUS.md)
   und [Übergabe](../project/HANDOVER.md) bei Fortsetzungs- oder Statusfragen;
2. [Projektauftrag](../product/PROJECT_CHARTER.md) bei Auftrags-/Produktumfang;
3. [Produkt- und Systemgrenzen](../architecture/BOUNDARIES.md) bei Produkt-,
   Adapter-, Datenschutz- oder Wirkungsgrenzen;
4. [Planungseinstieg](../planning/README.md) und
   [Artefaktregistry](../../.ai/artifact_registry.json) bei Planung;
5. betroffene Entscheidungen aus dem [Entscheidungsindex](../decisions/README.md)
   und den Registry-Relationen; angenommener Status allein begründet keine
   Relevanz für jede Bearbeitung;
6. [Dokumentationsstil](DOCUMENTATION_STYLE.md) bei Dokumentation;
7. [Validierung](VALIDATION.md) vor Auswahl oder Ausführung von Prüfungen;
8. [Glossar](../reference/GLOSSARY.md) bei Fachbegriffen;
9. [Drittmaterial und Wiederverwendung](THIRD_PARTY_AND_REUSE.md) bei
   Übernahme, Abhängigkeiten oder
   externer Software.

Das [Dokumentationsinventar](../README.md) ist zusätzlich vollständig
auffindbar; seine Links sind keine pauschale Lesepflicht.

Unveränderte, tatsächlich verfügbare Sitzungsanalysen dürfen nach
[DEC-0005](../decisions/DEC-0005-RULE_CONTEXT_CACHE.md) und der Foundation-
Processing-Efficiency-Policy wiederverwendet werden. Vor Wiederverwendung
werden aktuelle native Autorität, effektive Discoverykonfiguration, Scope,
ausgewählte Working-Tree-Bytes und die vollständige semantische
Abhängigkeitsinventur geprüft. Neue Links, Instructions oder maßgebliche
Quellen lösen erneut den vollständigen Auffindbarkeitscheck aus.
Ein Commit-/Worktreewechsel benötigt eine neue Bindungsprüfung; nur nach
belegter Äquivalenz bleiben identische Analysen nutzbar. Fehlende Discovery-
Evidenz oder verlorene Analyse bedeutet Lesen statt Wiederverwendung.

Eine zusammenhängende Wave hat einen Implementierungsverantwortlichen,
einen endlichen Umfang und vor Beginn eine Grenze mit Stoppverhalten. Ohne
zuverlässige Verbrauchsmessung werden begrenzte Aufgaben und Agentanzahl
statt behaupteter Geld-/Tokenlimits verwendet. Der konkrete Waveumfang und
seine Abschlussgrenze werden im registrierten Arbeitsgegenstand festgehalten.
Weitere Reviews benötigen eine konkrete offene Frage und Akzeptanzkriterien.
Wiederholbare mechanische Prüfungen erfolgen lokal; bereits grüne Prüfungen
werden nur bei geänderten Eingängen, neuen Befunden oder Pflichtbindung erneut
ausgeführt. Vorgeschriebene unabhängige Reviews und Pflicht-CI bleiben erhalten.

## Projektphase

Das Projekt besitzt mit WI-0004 einen ersten eng begrenzten, reversiblen
Produktprototyp. Es existiert weiterhin keine freigegebene allgemeine
Produktarchitektur, technische Roadmap oder vollständige Medienlinie.

Weiterer Produktcode, Laufzeitabhängigkeiten und Infrastruktur werden erst
nach einem registrierten und angenommenen Arbeitsgegenstand eingeführt. Ein
Experimentnachweis autorisiert keine Produktübernahme.

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
[IDENTITY_AND_REGISTRATION.md](IDENTITY_AND_REGISTRATION.md).

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
