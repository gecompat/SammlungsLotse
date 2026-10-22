# Projekt- und Foundation-Metadaten

Dieser Bereich verbindet die dauerhafte Projektidentität und
Artefaktregistrierung mit der übertragenen AI Repository Foundation. Er ist
kein Operatorcache und enthält keine privaten Laufzeitprotokolle.

- [AGENTS.md](../AGENTS.md) ist der AI-Einstieg. Er führt zu den aktiven
  [Projektregeln](../docs/governance/PROJECT_RULES.md); der
  [Foundation-Index](foundation/repo_map.yaml) erschließt die übertragenen
  Basisregeln. Diese Links sind Navigation, keine pauschale Lesepflicht.
- [project.json](project.json) hält die unveränderliche Projektidentität.
  [artifact_registry.json](artifact_registry.json) ist die kanonische
  Registration Authority. Schema, Vergabe und Validierung erklärt
  [Identität und Artefaktregistrierung](../docs/governance/IDENTITY_AND_REGISTRATION.md).
- [foundation/installation-provenance.json](foundation/installation-provenance.json)
  bindet die ausgewählten Foundation-Dateien an Manifest und Quellcommit.
  Der [Upgradebericht](../docs/governance/FOUNDATION_UPGRADE_1_25.md) erklärt
  die semantische Auswahl. Die Datei belegt Herkunft, keine Projektrichtigkeit.
- [Validierung](../docs/governance/VALIDATION.md) führt zu Foundation-,
  Projekt-, Registry- und Discoveryprüfungen. Die dort genannten Werkzeuge
  liefern Fehlerdetails; aktueller Stand und historische Prüfevidenz stehen
  getrennt im [Projektstatus](../docs/project/PROJECT_STATUS.md).

Die ausgewählten optionalen Fähigkeiten bleiben `artifact-registry-github`
und `rule-context-cache`. Ihre bloße Präsenz richtet weder ein Modell noch
einen Host, einen persistenten Cache oder eine automatische Ausführung ein.
