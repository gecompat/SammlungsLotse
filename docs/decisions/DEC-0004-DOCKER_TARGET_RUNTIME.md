# DEC-0004: Docker als Zielruntime mit optionalem Podman-Paralleladapter

Status: ACCEPTED

Datum: 2026-09-20

Artifact: DEC-0004

Artifact UID: urn:uuid:01a0bc0c-b17e-7272-a872-9778c5904d76

## Entscheidung

Docker ist die Zielruntime für neue E-Book-Produktwege. Podman bleibt ein
optionaler Paralleladapter, nie eine stillschweigende Austauschbarkeit.

## Grenzen

Jede Runtime bindet separat Client/Server, Plattform, Image-Provenienz,
Isolation und Inspect-Projektion. EXP-0022 bleibt als `not_qualified`-
Evidenz sichtbar. Eine Docker-Implementierung benötigt einen eigenen
Arbeitsgegenstand und eine End-to-End-Qualifikation; bestehende Podman-Profile
und öffentliche Verträge bleiben bis dahin unverändert.
