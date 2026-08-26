# DEC-0003: Zentrale Artefaktregistrierung

Status: ACCEPTED

Datum: 2026-08-26

Artifact UID: urn:uuid:01a03e7f-489c-7d11-9dba-f39bbfb207c6

## Kontext

Die Entwicklungsplanung wird von Menschen und mehreren AI-Systemen bearbeitet.
Dauerhafte Anforderungen, Entscheidungen und Arbeitsgegenstände benötigen
stabile Identitäten und kollisionsfreie Referenzen.

Das Repository enthält AI Repository Foundation 1.6.0 und verwendet GitHub
mit Pull Requests.

## Entscheidung

.ai/artifact_registry.json ist die zentrale Registration Authority im Profil
foundation-artifact-registry/v2.

Artefakte verwenden UUIDv7 und flache typisierte Referenzen. Die nächste
Sequenz wird aus der Registry und bekannten offenen Reservierungen abgeleitet.
Die Registry speichert weder next_sequence noch registry_revision.

Die optionale Foundation-Fähigkeit artifact-registry-github wird aus dem
geprüften Foundation-Quellcommit
2892b6656933e735b8ab3684af1327ae5a8afc86 übernommen. Ihr semantisches
Registry-Werkzeug bleibt unverändert. Der Workflow besitzt eine
projektspezifische Bootstrap-Behandlung für den ersten Registry-Pull-Request.

## Folgen

- Markdown-Dateien und Chatverläufe vergeben keine Referenzen.
- Registry-Änderungen werden semantisch und gegen das tatsächliche
  Git-Merge-Ergebnis geprüft.
- Offene Pull Requests können Referenzen vorläufig reservieren.
- Eine auf main registrierte oder stillgelegte Referenz wird nie
  wiederverwendet.
- Workflow-Dateien allein belegen keinen aktiven GitHub-Branchschutz.
