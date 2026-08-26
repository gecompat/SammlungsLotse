# Identität und Artefaktregistrierung

Status: AUTHORITATIVE

Governed by: DEC-0003

## Projektidentität

Die dauerhafte Projektidentität steht in .ai/project.json. Repositoryname,
Repository-URL und lokaler Pfad sind veränderbare Locators und nicht die
Projektidentität.

## Artefaktidentität

SammlungsLotse verwendet das Foundation-Standardprofil für neue Projekte:

- maschinenlesbare Identität als RFC-9562-UUIDv7 in URN-Form;
- stabile menschenlesbare Referenz in der Form PREFIX-SEQUENZ;
- Status, Priorität, Phase, Elternbeziehung und Dateipfad sind Metadaten;
- veröffentlichte Referenzen und UIDs werden nicht wiederverwendet.

## Registration Authority

Die kanonische Registration Authority ist:

.ai/artifact_registry.json

Profil:

foundation-artifact-registry/v2

Das Werkzeug tools/governance/register_artifact.py erzeugt vollständige
Einträge. Menschen und AI-Systeme verwenden dieselbe Registry und dasselbe
Verfahren.

## Präfixe

- CAP: dauerhafte Fähigkeit oder Ergebnis;
- REQ: Anforderung oder dauerhafte Einschränkung;
- WI: Arbeitsgegenstand;
- DEC: dauerhafte Entscheidung;
- GATE: Entscheidungs-, Sicherheits- oder Freigabegate;
- RISK: Risiko;
- EXP: Experiment oder Spike;
- OPS: betrieblicher Gegenstand oder Kontrollmechanismus;
- INC: Vorfall;
- REL: Release;
- TEST: dauerhafter Testvertrag.

Die Bedeutung eines veröffentlichten Präfixes wird nicht geändert.

## Statuswerte

registration_state beschreibt ausschließlich die Registrierungsidentität:
DRAFT, REGISTERED oder RETIRED.

Der fachliche Lebenszyklus steht getrennt im Feld status. Zulässige
Ausgangswerte sind:

- proposed;
- accepted;
- ready;
- in_progress;
- blocked;
- done;
- rejected;
- superseded.

Weitere Werte benötigen eine dokumentierte semantische Erweiterung. Ein
RETIRED-Eintrag wird nicht reaktiviert.

## Git- und Pull-Request-Verfahren

Der Registry-Stand auf main ist kanonisch.

Eine in einem offenen Pull Request neu verwendete Referenz ist bis zum Merge
eine vorläufige Reservierung. Vor der Erzeugung ist der Branch gegen
origin/main zu aktualisieren. Bekannte Reservierungen anderer offener Pull
Requests werden dem Registrierungswerkzeug mit --reserved-ref übergeben.

Die GitHub-Prüfung erkennt konkurrierende Referenzen, UIDs, Aliase und
überlappende Änderungen. Sie prüft außerdem, dass das tatsächliche
textbasierte Git-Merge-Ergebnis dem objektbasierten semantischen Merge
entspricht.

Wird ein Pull Request ohne Merge geschlossen, darf seine ausschließlich
vorläufige und nie auf main registrierte Referenz erneut reserviert werden.
Eine auf main registrierte oder als RETIRED gespeicherte Referenz bleibt
dauerhaft belegt.

## Allocation

Das Werkzeug leitet die nächste Sequenz ausschließlich aus der kanonischen
Registry und den ausdrücklich übergebenen Reservierungen ab. Markdown,
Dateinamen, Chatverläufe und Modellgedächtnis sind keine Allocation Authority.

Beispiel:

    python tools/governance/register_artifact.py \
      --prefix WI \
      --title "Ersten vertikalen E-Book-Ablauf planen" \
      --status proposed \
      --locator docs/planning/example.md

Die erzeugte Referenz wird erst durch den Merge nach main kanonisch.

## Relationen

Mindestens folgende Relationstypen sind vorgesehen:

- parent;
- depends_on;
- implements;
- verifies;
- blocks;
- governed_by;
- supersedes;
- derived_from;
- related_to.

Relationen verweisen auf kanonische Referenzen, UIDs oder eindeutige Aliase.
parent und depends_on dürfen keine Zyklen bilden.

## GitHub-Administration

Die Workflow-Datei allein erzwingt keinen Branchschutz. Der Statuscheck für
Registry-Integrität und der allgemeine Repository-Qualitätscheck sind nach
ihren ersten erfolgreichen Läufen als erforderliche Checks für main
konfiguriert. Der aktive Zustand und die zugeordneten Check-Anbieter wurden
getrennt über die GitHub-API geprüft. Der aktuelle Nachweis steht in
docs/project/PROJECT_STATUS.md.
