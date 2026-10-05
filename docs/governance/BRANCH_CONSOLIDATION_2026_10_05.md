# Branch-Konsolidierung am 2026-10-05

Artifact: WI-0022

## Umfang und Vergleichsstand

Nutzerauftrag: Alle vorhandenen Branches prüfen, sinnvolle Änderungen auf
origin/main übernehmen und erledigte oder ungeeignete Branches und Pull
Requests aufräumen. Vergleichsstand ist
`81a2cbc3f13df3581355bf982477f4a14d22db9c` auf origin/main.

Die Prüfung umfasst sämtliche 20 lokalen Arbeitsbranches und vier
entfernten Dependabot-Branches. Es gibt keine weiteren Worktrees oder
ungespeicherten Arbeitsbaumänderungen. GitHub lieferte vollständig genau
vier offene PRs und fünf Remote-Branches einschließlich main.

## Bereits übernommene lokale Arbeit

Für jeden Branch bestätigten `git merge-base --is-ancestor` beziehungsweise
der identische Merge-Base-/Tip-Commit und ein leerer Commitbereich gegen
origin/main die vollständige Aufnahme in die Historie. Es gibt keine
zusätzlichen Commits oder noch zu übernehmenden Patches. Nach erneuter
Ancestor- und Worktree-Prüfung wurden diese 20 Branchreferenzen mit
`git branch -d` entfernt. Die folgenden Commits bleiben in main erreichbar.

| Branch | Geprüfter Tip |
|---|---|
| `codex/autonomous-next-wave` | `630ccd2600e99d2f3ffaea37fecee40382d479d4` |
| `codex/close-exp-0023` | `e6cc1731e721d900b58804756ba38331fe0c0688` |
| `codex/docker-calibre-adapter` | `677cf3d0ad0a776e67989b27c77a8e1d1654ac63` |
| `codex/docker-calibre-preimage` | `3d6e5745b4b2ddb04b863fa0c8c00dfd428da0f8` |
| `codex/docker-calibre-work-item` | `6dc83294fef03680c1d1b4007c50654967f5e545` |
| `codex/docker-config-env-contract` | `5a94493d104b91c4cc1c57ec7c9e0ae698ed34c1` |
| `codex/docker-multilibrary-gate` | `6460523a2012deae070f40292a469adcf78896ab` |
| `codex/docker-podman-equivalence-runner` | `61d7039ef6eabc7d8b43cebb3390fabb74aaf41b` |
| `codex/docker-runtime-gate` | `fb3a5d3bc11949472c727584f367fef7fa3d6313` |
| `codex/ebook-routing-gate` | `84461d7b20e72dac36f672348c999ec71257286e` |
| `codex/exp0019-review-plan` | `6cd27f51d7c2cf05b59b763ab666a011512f1b5e` |
| `codex/exp0024-routing-matrix` | `79e3e1c0f070156ceb94133f5d9dee1c34decbc5` |
| `codex/exp0025-docker-multilibrary` | `937694ba76fe0208c028e83642ec5ca80a47ebb2` |
| `codex/fix-exp0023-registry` | `973be591d98e2873a64c958d94b3b9c23ef5a66f` |
| `codex/frozen-symlink-capability` | `f860524cc0e684bd59faa7029185195a0337314f` |
| `codex/inbox-calibre-review-evidence` | `774dc264c29d27cb44453f0e4d1bc55f0d979413` |
| `codex/rule-context-cache` | `c4e95c77b25b900c778476f6d360f4efcdfafcd6` |
| `codex/status-handover-20260913` | `d582edde7a6691042a05b414416cd2342b6d9ae8` |
| `codex/validation-portability` | `b5caf81219ca8b647a533cefa96c0de09be320a4` |
| `codex/zip-evidence-portability` | `d8ba3b28454ea1305ab9333429de4a4b0fa5c815` |

## Nicht geeignete historische Lockfile-Updates

Alle vier offenen PRs verändern ausschließlich
`experiments/ebook/exp-0003/package-lock.json`. Das aktuelle
[Ausführungsprofil](../../experiments/ebook/exp-0003/execution-profile.json)
bindet den Lock an SHA-256
`f1b20f79e0c1c5b7cb5aae2f3890bafe5f455a352a311476d2f6f8578f1f3074`.

Die reine lokale Prüfung verwendet den bestehenden
`validate_profile`-Vertrag aus `tools/experiments/run_exp_0003.py` und
substituiert nur dessen Lock-Pfad auf je eine temporäre Datei mit dem
unveränderten Git-Blob des jeweiligen PR-Heads. Alle vier Kandidaten ergeben
`EXP-0003 package-lock digest mismatch`. Der unveränderte main-Vertrag
besteht; `--validate-result` bestätigt weiterhin 14/14 Kriterien. Es werden
keine npm-Pakete installiert, Container gestartet oder Experimente wiederholt.

| PR | Änderung | Geprüfter Head | Entscheidung |
|---|---|---|---|
| [#96](https://github.com/gecompat/SammlungsLotse/pull/96) | `qs`, `express` | `e01ea840f962e6f20b9e448d06b17cb7f5c4809a` | Ohne Merge geschlossen |
| [#123](https://github.com/gecompat/SammlungsLotse/pull/123) | `undici` 7.30.0 | `4fb678e4903c3315b1a507b1ac27b7d7f2a51a71` | Ohne Merge geschlossen |
| [#124](https://github.com/gecompat/SammlungsLotse/pull/124) | `ip-address` 10.7.2 | `749fbd469aea444040d9d9f936bf16413a30b9de` | Ohne Merge geschlossen |
| [#127](https://github.com/gecompat/SammlungsLotse/pull/127) | `brace-expansion` 1.1.21 | `752a9a11efd678fbed4c5d793593014346aba3ff` | Ohne Merge geschlossen |

Die PRs und ihre Heads bleiben über GitHubs `refs/pull/<Nummer>/head`
nachprüfbar; alle vier Ref-/Head-Zuordnungen wurden vor dem Aufräumen
bestätigt. GitHub entfernte beim Schließen die vier zugehörigen
Remote-Branchreferenzen; `git ls-remote --heads origin` und GraphQL
bestätigten danach ausschließlich main. Die PRs sind weiterhin geschlossen
und ihre Inhalte bleiben nachprüfbar.

## Dauerhafte Anpassung

Die sinnvolle neue Änderung liegt außerhalb der eingefrorenen
Experimentdateien: `.github/dependabot.yml` ignoriert npm-Abhängigkeiten
ausschließlich im exakten EXP-0003-Verzeichnis. `open-pull-requests-limit: 0`
unterbindet Versionsupdate-PRs; `ignore` mit `dependency-name: "*"`
verhindert dort auch Sicherheitsupdate-PRs. Es wird kein `target-branch`
gesetzt. Die vorhandene GitHub-Actions-Konfiguration bleibt erhalten.

GitHub dokumentiert, dass
[Ignore-Regeln Versions- und Sicherheitsupdates verhindern](https://docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/vulnerability-detection),
[Namensmuster den Stern-Wildcard unterstützen](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
und [Sicherheitsupdate-Konfigurationen das konkrete Manifestverzeichnis verwenden](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/customizing-dependabot-security-prs).
Quellenprüfung: 2026-10-05.

Die Ausnahme entfernt oder dismissiert keine Sicherheitswarnungen. Sie
behebt keine Schwachstellen und macht Ace nicht produktqualifiziert. Das
[historische Experiment](../../experiments/ebook/exp-0003/README.md)
dokumentiert seine damaligen offenen Befunde und deaktivierte interne
Browser-Sandbox unverändert. Ein neuer Ace-Einsatz benötigt ein eigenes
aktuelles Profil und getrennte Qualifikation. Die verbindliche Abgrenzung
steht unter [Validierung](VALIDATION.md).

## Abschlussprüfung

Lokal erfolgreich am 2026-10-05 unter Windows/Python 3.13.15:

- `python tools/governance/validate_repository.py`: Projekt- und Discovery-Verträge;
- `python .ai/foundation/artifact_registry_github/registry_semantic.py validate --registry .ai/artifact_registry.json`: 90 Artefakte;
- `python tools/experiments/run_exp_0003.py --validate-result`: 14/14 Kriterien;
- `python -m unittest tests.experiments.test_exp_0003`: alle vier Regressionstests;
- vier negative Profilkontrollen mit den exakten PR-Lockfiles;
- `git diff --check`; unverändertes EXP-0003-Verzeichnis gegenüber dem Vergleichsstand.

Die YAML-Konfiguration wurde anhand der offiziellen Syntax und der engen
Verzeichnisbindung geprüft; ein zusätzlicher YAML-Parser ist in der lokalen
Python-Toolchain nicht installiert. Die serverseitige Anwendung der
Dependabot-Regel erfolgt nach Übernahme auf den Default-Branch. Das
Schließen bestehender PRs ersetzt keinen Nachweis dieser späteren Anwendung.

Der Merge benötigt die Pflichtchecks `repository-quality` und
`registry-integrity` auf dem exakten Konsolidierungs-Head. Danach werden
origin/main, der saubere lokale main-Checkout, null offene Pull Requests und
das Fehlen weiterer lokaler oder entfernter Arbeitsbranches nachgeprüft.
Künftige Produktplanung wird durch diesen Branch-Aufräumauftrag nicht
abgeschlossen oder automatisch ausgeführt.
