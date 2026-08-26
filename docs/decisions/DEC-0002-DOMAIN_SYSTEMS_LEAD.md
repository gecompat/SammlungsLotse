# DEC-0002: Führende Fachsysteme

Status: ACCEPTED

Datum: 2026-08-26

Artifact UID: urn:uuid:01a03e7f-489c-7586-9d57-b79976c69765

## Kontext

Spezialisierte Systeme besitzen Fachmodelle, Arbeitsabläufe und
Bestandsverwaltung, die ein domänenübergreifendes System nicht ohne hohen
Aufwand gleichwertig ersetzen kann.

Calibre ist das führende System für die E-Book-Sammlung. Entsprechende Rollen
können andere Fachsysteme für Musik, Bilder, Videos, Scans und Dokumente
übernehmen.

## Entscheidung

Das spezialisierte Fachsystem bleibt für seinen produktiven Fachbestand
führend. SammlungsLotse unterstützt durch Analyse, Qualitätsbewertung, Suche,
Vorschläge und kontrollierte Orchestrierung.

SammlungsLotse darf eigene Evidenz-, Provenienz-, Such-, Regel- und
Ablaufzustände führen. Es bildet die interne Datenbank eines Fachsystems nicht
als eigenes Kernmodell nach.

Schreibende Änderungen erfolgen nur über dokumentierte unterstützte
Schnittstellen und operationstypbezogene Freigaben.

## Folgen

- Adapter bilden eine klare Anti-Corruption Boundary.
- Fachsysteminterne IDs sind Locators oder externe Referenzen.
- Mehrere Zielbibliotheken derselben Domäne werden als getrennte Ziele
  unterstützt.
- REST-, Browser-, CLI- und Agent-Zugänge teilen dieselben
  Anwendungsverträge.
- Ein Provider-, Werkzeug- oder KI-Ergebnis reicht allein nicht für eine
  schreibende Entscheidung.
