# Foundation-Upgrade 1.7

Status: AUTHORITATIVE ASSESSMENT

Artifact: WI-0001

## Vergleichsstand

- installierte Foundation-Version: 1.6.0;
- bisheriger Foundation-Quellcommit:
  `2892b6656933e735b8ab3684af1327ae5a8afc86`;
- neue Foundation-Version: 1.7.0;
- neuer Foundation-Quellcommit:
  `d49f978f33001fcc098998ff7c04ffb209b28033`;
- ausgewählte Adapter: GitHub Copilot, Claude Code und Gemini;
- ausgewählte optionale Fähigkeit: `artifact-registry-github`.

## Vollständige Feature-Bewertung

### `layered-validation`: `APPLY_DEFAULT`

SammlungsLotse trennt bereits `FOUNDATION_INTEGRITY`, `PROJECT_SEMANTIC` und
`RUNTIME_EMPIRICAL`. Foundation 1.7 ergänzt die portable Gleichwertigkeit von
UTF-8-Text mit LF beziehungsweise CRLF und unterscheidet einen fachlichen
`VALIDATION_FAILURE` von `INFRASTRUCTURE_UNAVAILABLE` und `UNKNOWN`.

Die neuen Mindestregeln werden übernommen. Die projektspezifischen Prüfer und
GitHub-Checks bleiben unter `PROJECT_SEMANTIC` und `RUNTIME_EMPIRICAL`
führend. Die Überschneidung ist `COMPLEMENTARY`.

### `repository-continuity-break-glass`: `RECOMMENDED`

Die Empfehlung ist anwendbar:

- `main` ist geschützt;
- `repository-quality` und `registry-integrity` sind strikt erforderliche
  GitHub-Actions-Checks;
- die Regeln gelten auch für Administratoren;
- GitHub Actions ist damit eine externe Verfügbarkeitsabhängigkeit für den
  dauerhaften Pull-Request-Kanal;
- es existieren keine Repository-Rulesets und kein autorisierter
  Break-Glass-Bypass.

Der aktuelle No-Bypass-Zustand bleibt als `PROJECT_STRONGER` für Integrität
erhalten. Empfohlen wird eine spätere eigene Entscheidung über getrennte
Core-Safety- und CI-Gates-Rulesets mit eng begrenztem Pull-Request-only-Bypass
ausschließlich für nachgewiesene `INFRASTRUCTURE_UNAVAILABLE`-Fälle.

Dieses Upgrade wählt keine Bypass-Akteure, keine Ausfallschwelle und ändert
keine GitHub-Administration. `VALIDATION_FAILURE` und `UNKNOWN` bleiben stets
nicht übergehbar. Bis zu einer angenommenen Projektentscheidung existiert kein
Break-Glass-Verfahren.

## Semantischer Dateiplan

- `CREATE`: `.ai/foundation/REPOSITORY_CONTINUITY_POLICY.md`;
- Upgrade auf die manifestierten 1.7-Quellen:
  `FOUNDATION_RULESET.md`, `VALIDATION_POLICY.md`, `feature_catalog.json` und
  `repo_map.yaml`;
- `EQUIVALENT`: Der verwaltete Foundation-Block in `AGENTS.md` ist unverändert;
  die projekt-eigene Discovery bleibt erhalten;
- `PROJECT_STRONGER`: Der angepasste Registry-Workflow mit Bootstrap-Behandlung
  bleibt erhalten;
- `UNCHANGED`: `artifact_registry.json` bleibt Registration Authority im
  Profil `foundation-artifact-registry/v2`; historische IDs und die
  Registrierungssemantik werden nicht migriert;
- `PROJECT_SELECTABLE_OVERRIDE`: Die vorhandene `.gitattributes`-Regel bleibt
  als projekt-eigene Byte-Stabilitätsregel erhalten. Foundation 1.7 erfordert
  keine neue EOL-Regel.

## Validierungsumfang

- `FOUNDATION_INTEGRITY`: Foundation-Validator 1.7 mit der ausgewählten
  GitHub-Registry-Fähigkeit;
- `PROJECT_SEMANTIC`: Repository- und v2-Registry-Validierung;
- `RUNTIME_EMPIRICAL`: synthetische Unit-Tests und `compileall` für die
  Governance-Werkzeuge;
- GitHub: die erforderlichen Checks für den exakten Pull-Request-Head und eine
  Post-Merge-Prüfung von `origin/main`.
