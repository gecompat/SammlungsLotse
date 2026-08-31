# Validierung

Status: AUTHORITATIVE

Validierung wird nach betroffenem Vertrag ausgewählt. Ein grüner
Foundation-Check belegt nicht die Projektrichtigkeit.

## FOUNDATION_INTEGRITY

Die Foundation-Quellversion besitzt den kanonischen Validator. Für die
installierte Foundation 1.7.0 und die ausgewählte Fähigkeit
artifact-registry-github lautet der allgemeine Aufruf:

    python tools/foundation_validator.py \
      --target <SammlungsLotse-Worktree> \
      --adapters default \
      --capabilities artifact-registry-github \
      --profile full

Der Befehl wird im ausgecheckten Foundation-Quellrepository des dokumentierten
Quellcommits ausgeführt. Der Validator wird gemäß Foundation-Manifest nicht in
dieses Zielrepository kopiert.

Der installierte Quellstand ist
`d49f978f33001fcc098998ff7c04ffb209b28033`. Die vollständige semantische
Upgrade-Bewertung steht in
[FOUNDATION_UPGRADE_1_7.md](FOUNDATION_UPGRADE_1_7.md).

## PROJECT_SEMANTIC

Die aktuelle Projektinitialisierung besitzt folgende lokale Prüfungen:

    python tools/governance/validate_repository.py

    python .ai/foundation/artifact_registry_github/registry_semantic.py \
      validate --registry .ai/artifact_registry.json

Die erste Prüfung kontrolliert erforderliche Projektquellen, interne
Dokumentlinks, Projektidentität, Registry-Locators und Repository-Hygiene. Die
zweite Prüfung kontrolliert die v2-Registry-Semantik.

## RUNTIME_EMPIRICAL

Für Produkt-, Governance- und Fixture-Code gelten:

    python tools/run_repository_tests.py

Der Repository-Testadapter entdeckt weiterhin die vollständige Testsuite. Er
ersetzt ausschließlich die drei eingefrorenen Ergebnisprüfungen von EXP-0009,
EXP-0010 und EXP-0011, die absichtlich den jeweils damaligen aktuellen
Produktstand erwarten, durch drei gleichzählige Prüfungen gegen deren
historisches Git-Preimage. Er bricht ab, falls einer der sechs expliziten
Test-IDs fehlt oder mehrfach vorkommt; alle übrigen entdeckten Tests laufen
unverändert.

    python -m compileall -q \
      src/sammlungslotse \
      .ai/foundation/artifact_registry_github \
      tools/run_ebook_intake.py \
      tools/run_calibre_inventory.py \
      tools/run_ebook_identity.py \
      tools/run_ebook_calibre_identity.py \
      tools/provision_calibre_readonly_profile.py \
      tools/qualify_calibre_readonly_profile.py \
      tools/qualify_ebook_identity.py \
      tools/qualify_ebook_calibre_identity.py \
      tools/run_repository_tests.py \
      tools/governance \
      tools/fixtures \
      tools/experiments \
      experiments/ebook/exp-0002 \
      experiments/ebook/exp-0003 \
      experiments/ebook/exp-0004 \
      experiments/ebook/exp-0005 \
      experiments/ebook/exp-0006 \
      experiments/ebook/exp-0007

Für die ausführbare synthetische TEST-0001-Kernfassung gilt zusätzlich:

    python tools/fixtures/validate_ebook_reference_corpus.py

Die Prüfung validiert Manifest, Hashes, Herkunft, zentrale Fallorakel,
Datenschutzgrenzen, einen kontrollierten Timeout, bytegenaue Regeneration und
die Unverändertheit aller Fixture-Eingänge. Sie führt keine externen
E-Book-Werkzeuge und keines der getrennten Experimente aus.

Für den eingecheckten empirischen EXP-0002-Nachweis gilt:

    python tools/experiments/run_exp_0002.py --validate-result

Die CI-geeignete Prüfung wiederholt weder Calibre-Download noch Containerlauf.
Sie bindet das Ergebnis an Profil und TEST-0001-Version und prüft alle
dreizehn Akzeptanzwerte, beide getrennten Zielbibliotheken sowie unveränderte
Quell-Snapshots. Der explizite lokale Lauf ist unter
`experiments/ebook/exp-0002/` dokumentiert.

Für den eingecheckten empirischen EXP-0003-Nachweis gilt:

    python tools/experiments/run_exp_0003.py --validate-result

Die CI-geeignete Prüfung wiederholt weder externe Downloads, den
netzwerkabhängigen `npm audit` noch Containerläufe. Sie prüft Profilbindung,
alle vierzehn Akzeptanzwerte, sieben Fälle mit je zwei Wiederholungen,
Rohbericht-Referenzen, Pfadgrenzen, Eingangs-Hashes und die sichtbare offene
Ace-Risikoklassifikation. Der vollständige lokale Lauf ist unter
`experiments/ebook/exp-0003/` dokumentiert.

Für den eingecheckten empirischen EXP-0004-Nachweis gilt:

    python tools/experiments/run_exp_0004.py --validate-result

Die CI-geeignete Prüfung wiederholt nicht die Identitätsbewertung. Sie prüft
Profil- und Fixture-Bindung, alle fünfzehn Akzeptanzwerte, sechs Sollpaare auf
fünf getrennten Ebenen, zwei identische semantische Wiederholungen,
Metrikvollständigkeit, getrennte positive, negative und fehlende Evidenz,
Null-Schreibwirkung sowie unveränderte Eingänge. Der vollständige lokale Lauf
ist unter `experiments/ebook/exp-0004/` dokumentiert.

Für den eingecheckten empirischen EXP-0005-Nachweis gilt:

    python tools/experiments/run_exp_0005.py --validate-result

Diese CI-geeignete Prüfung wiederholt keinen Containerlauf und keinen
Download. Sie prüft das enge Profil, den vollständigen `pass`-Ergebnisvertrag,
alle elf Akzeptanzwerte und unveränderte Eingangs-Hashes. Der tatsächliche
Podman-Lauf ist ein separater expliziter lokaler Provisionierungs- und
Experimentbefehl, dokumentiert unter `experiments/ebook/exp-0005/`.

Für den eingecheckten empirischen EXP-0006-Nachweis gilt:

    python tools/experiments/run_exp_0006.py --validate-result

Diese CI-geeignete Prüfung baut oder startet keinen Container. Sie bindet das
Ergebnis an Profil, Probe, Runner und TEST-0001-Manifest und prüft alle
sechzehn Akzeptanzwerte, elf Matrixzeilen, zwei semantisch identische
Wiederholungen, null kritische Fehlfreigaben sowie die protokollierten
Netzwerk-, Dateisystem-, Prozess-, Ressourcen- und Umgebungsgrenzen. Der
vollständige lokale Podman-Lauf ist als eigener expliziter Befehl unter
`experiments/ebook/exp-0006/` dokumentiert.

Für den eingecheckten empirischen EXP-0007-Nachweis gilt:

    python tools/experiments/run_exp_0007.py --validate-result

Diese CI-geeignete Prüfung wiederholt weder Windows-Prozesse, Containerläufe
noch die optionale EPUBCheck-Kompatibilitätsprüfung. Sie bindet das Ergebnis
an Profil, Probe, Driver, Runner, Containerdefinition, TEST-0001-Manifest und
den kanonischen Planungsstand. Sie berechnet alle sechzehn Akzeptanzwerte aus
den getrennten Windows- und Linux-Evidenzen neu und prüft insbesondere
Snapshot-Bindung, Negativkontrollen, Output- und Timeoutgrenzen, Kindprozess-
und Temp-Cleanup, Originalunverändertheit, V3-Ablehnung sowie die
zurückgelesene Podman-Isolation. Der vollständige lokale Lauf ist unter
`experiments/ebook/exp-0007/` dokumentiert.

Für den eingecheckten empirischen EXP-0008-Nachweis gilt:

    python tools/experiments/run_exp_0008.py --validate-result

Diese CI-geeignete Prüfung materialisiert keine Bibliothek und startet keinen
Container. Sie bindet den Nachweis an das vollständige Experimentpreimage,
das exakte Calibre-9.13.0-Profil und die synthetische
TEST-0001-Qualifikationsbibliothek. Sie berechnet 16 Kriterien für genau eine
explizite ID und EPUB, Bytegleichheit, unterstützte CLI-Nutzung,
Copy-on-read, Containerisolation, Negativfälle, Ressourcenlimits,
Wiederholbarkeit sowie vollständiges Cleanup neu. Der tatsächliche lokale
Lauf ist unter `experiments/ebook/exp-0008/` dokumentiert.

Für den eingecheckten empirischen EXP-0009-Nachweis gilt:

    python tools/experiments/validate_exp_0009_result.py

Diese CI-geeignete Prüfung materialisiert keine EPUBs neu. Sie bindet Profil,
Manifest und Runner an das historische Git-Preimage und prüft die
unveränderten eingefrorenen Experimentdateien. Danach berechnet der
eingefrorene Validator alle Metriken und 12 methodischen Akzeptanzkriterien
aus den zwei gespeicherten Wiederholungen neu und erzwingt die sichtbare
Trennung zwischen methodisch bestandenem Experiment und
`not_qualified`-Produktqualität. Der vollständige synthetische Lauf ist unter
`experiments/ebook/exp-0009/` dokumentiert. Der ursprüngliche Aufruf
`python tools/experiments/run_exp_0009.py --validate-result` bleibt nur im
eingefrorenen Produktpreimage selbst grün, weil er absichtlich den damals
aktuellen Produktcode bindet.

Für den eingecheckten empirischen EXP-0010-Nachweis gilt:

    python tools/experiments/validate_exp_0010_result.py

Diese CI-geeignete Prüfung materialisiert keine EPUBs und startet weder
Container noch Netzwerkzugriffe. Sie liest das vollständige historische
Produktpreimage aus dem gebundenen Git-Commit, prüft die unveränderten
Experimentdateien und verwendet danach den eingefrorenen EXP-0010-Validator.
Damit bleiben zehn vorab gebundene Paare, EPUBCheck-5.3.0-Profil, zwölf
methodische Kriterien, Konformitätserwartungen, fünfstufige Oraclematrix,
Metriken, sechs historische False Same und drei getrennte semantische
Fähigkeitslücken auch nach späteren Produktänderungen prüfbar. Der
vollständige lokale Lauf ist unter `experiments/ebook/exp-0010/`
dokumentiert. Der ursprüngliche Aufruf
`python tools/experiments/run_exp_0010.py --validate-result` bleibt nur im
eingefrorenen Produktpreimage selbst grün, weil er absichtlich den damals
aktuellen Produktcode bindet.

Für den eingecheckten empirischen EXP-0011-Nachweis gilt:

    python tools/experiments/validate_exp_0011_result.py

Diese CI-geeignete Prüfung erzeugt keine Medien und startet weder Container
noch Netzwerkzugriff oder Experimentwiederholung. Sie liest das vollständige
historische Preimage aus dem gebundenen Git-Commit
`a5aeb0196d8d6a32fc90da46ca158ba693c6a0db`, prüft die unveränderten
Experimentdateien und lässt den eingefrorenen Runner Ergebnisbindung,
Messvektoren und alle 14 Akzeptanzwerte neu berechnen. Damit bleiben genau 15
synthetische Paare, drei Varianten, zwei identische semantische
Wiederholungen, null Rollenverlust, vollständige Provenienz, unveränderte fünf
Produktstufen, Publikationslücke beziehungsweise V3-Ausdruck und die zwei
sichtbaren Restfälle auch nach späteren Produktänderungen prüfbar. Der
vollständige Nachweis liegt unter `experiments/ebook/exp-0011/`.

Der Aufruf

    python tools/experiments/run_exp_0011.py --validate-result

bleibt für das eingefrorene Ausführungspreimage gültig. Die historische
Prüfung ist der dauerhafte CI-Vertrag und führt den Experimentlauf nicht neu
aus.

Für den WI-0004-Produktvertrag gelten zusätzlich:

    python -m unittest discover -s tests/product -p "test_*.py"

Die Tests prüfen die Gate-Matrix, stabile und instabile Snapshots,
Ressourcenobergrenzen, Pfadbereinigung, byteidentische JSON-Ausgabe,
unveränderte Eingaben sowie die Abwesenheit von Netzwerk-, Persistenz-,
Subprozess-, Extraktions- und Schreibfähigkeiten im WI-0004-Kern. Die
ausdrücklich isolierten WI-0005-Adaptermodule besitzen nur die separat
getesteten Prozess- und task-privaten Schreibwirkungen.

Die sichtbare synthetische CLI-Abnahme verwendet mindestens:

    python tools/run_ebook_intake.py tests/fixtures/ebook/test-0001/v0.3/cases/ingress-stable-minimal/stable.epub

    python tools/run_ebook_intake.py --json tests/fixtures/ebook/test-0001/v0.3/cases/epub-active-or-remote/active-remote.epub

    python tools/run_ebook_intake.py --json tests/fixtures/ebook/test-0001/v0.3/cases/container-corrupt/corrupt.epub

    python tools/run_ebook_intake.py --json tests/fixtures/ebook/test-0001/v0.3/cases/format-unknown/unknown.epub

Vor und nach der Matrix werden die SHA-256-Werte der Eingänge verglichen.
Zwei JSON-Läufe über den stabilen Eingang müssen byteidentisch sein. Die
Abnahme qualifiziert nur den lokalen synthetischen Prototyp; sie startet kein
tiefes Werkzeug und verwendet keine realen oder privaten Medien.

Für den eingecheckten WI-0005-Produktnachweis gilt zusätzlich:

    python tools/qualify_ebook_deep_profile.py --validate-result

Diese CI-geeignete Prüfung startet keinen Container und lädt keine
Abhängigkeit. Sie bindet zwölf erfüllte Akzeptanzwerte an das aktive Profil,
die exakte Image-ID, drei aktuelle TEST-0001-Hashes, die zurückgelesene
Isolation, das Outputlimit sowie Timeout- und Cleanupbelege.

Die bewusste lokale Provisionierung und tatsächliche Podman-Qualifikation
verwenden ausschließlich Pfade unter `C:\rep`:

    python tools/provision_ebook_deep_profile.py --cache-root C:\rep\cache\SammlungsLotse\ebook-deep-readonly

    python tools/qualify_ebook_deep_profile.py --temp-root C:\rep\tmp\SammlungsLotse\wi-0005-qualification --result C:\rep\artifacts\SammlungsLotse\wi-0005-qualification.json

Der tatsächliche Lauf muss den unveränderten Standardweg, Opt-in-Erfolg,
einen Providerbefund, geschlossenes Gate, `not_assessed`, effektive
Prestart-Isolation, Input- und Originalunverändertheit, Outputlimit, Timeout
sowie vollständiges Container- und Task-Cleanup belegen. Unbekannte Codes,
ungültige Berichte, Pre- und Post-Hashabweichung, Cleanupfehler und Recovery
werden zusätzlich durch synthetische Produktverträge erzwungen.

Für den eingecheckten WI-0007-Produktnachweis gilt zusätzlich:

    python tools/qualify_calibre_readonly_profile.py --validate-result

Diese CI-geeignete Prüfung startet keinen Container und lädt kein Artefakt.
Sie bindet 17 erfüllte Kriterien an das exakte Profil, die reproduzierbare
Image-ID und das vollständige Produktpreimage.

Die bewusste lokale Bereitstellung und tatsächliche synthetische
Produktqualifikation verwenden ausschließlich Pfade unter `C:\rep`:

    python tools/provision_calibre_readonly_profile.py --cache-root C:\rep\cache\SammlungsLotse\calibre-readonly

    python tools/qualify_calibre_readonly_profile.py --library C:\rep\tmp\SammlungsLotse\wi-0007-qualification\library --temp-root C:\rep\tmp\SammlungsLotse\wi-0007-qualification\tasks --result C:\rep\artifacts\SammlungsLotse\wi-0007-qualification.json

Die Bibliothek wird vor der Qualifikation ausschließlich mit TEST-0001-
Material und unterstützten Calibre-Befehlen erzeugt. Der Lauf prüft
Imagebindung, echte deutsche und wiederholte JSON-Ausgabe, tatsächlichen
Timeout und tatsächliche Rohoutput-Grenze, minimale
Projektion, Pfadfreiheit, unveränderten Quellsnapshot sowie vollständiges
Task- und Container-Cleanup. Fehler-, Grenz-, Instabilitäts- und
Recoveryverträge werden zusätzlich durch fokussierte synthetische
Produkttests erzwungen.

Für den aktuellen, mit WI-0013 fortgeschriebenen EPUB-Identitäts-
Produktnachweis gilt zusätzlich:

    python tools/qualify_ebook_identity.py --validate-result

Die CI-geeignete Prüfung startet keinen Container und benötigt kein Netzwerk.
Sie bindet 29 erfüllte Kriterien und den Preimage-Commit an fünf
TEST-0001-Paare, acht konforme Qualitätsfälle und zwei getrennte ungültige
Kontrollen aus dem unveränderten EXP-0010-Fallmanifest. Der zugrunde liegende
tatsächliche Qualifikationslauf lautet:

    python tools/qualify_ebook_identity.py \
      --temp-root C:\rep\tmp\SammlungsLotse\wi-0013-qualification

Er führt jeden der dreizehn qualifizierten Fälle je zweimal über den
tatsächlichen V1- und V2-CLI-Pfad aus. Er prüft bytekompatibles V1, die
gebundene rollenbewusste V2-Projektion, fünf identische Stufen,
241 Provenienzeinträge, Determinismus, Pfadfreiheit, unveränderte Eingänge,
vollständiges Task-Cleanup, fehlende Produktwirkungen und null kritische
False Same. Zwei verbleibende `candidate_related`-Werkabweichungen bleiben im
Nachweis ausdrücklich sichtbar.

Für den eingecheckten WI-0011-Produktnachweis gilt zusätzlich:

    python tools/qualify_ebook_calibre_identity.py --validate-result

Die CI-geeignete Prüfung startet keinen Container. Sie bindet 23 erfüllte
Kriterien an das vollständige Produktpreimage, das exakte Calibre-9.13.0-
Image, die synthetische Qualifikationsbibliothek und TEST-0001-Fixtures. Der
zugrunde liegende tatsächliche Lauf führt positive, neu gepackte, negative,
fehlende, formatlose, ungültige, mehrfache und übergroße Fälle sowie
Outputlimit, Timeout, Unterbrechung und Recovery aus. Er prüft Pfadfreiheit,
Bytegleichheit, Rollen, fünf Identitätsebenen, Quellunverändertheit und
vollständiges Task- und Container-Cleanup.

Nach WI-0013 wurde dieser abhängige Produktweg gegen den neuen
Analyzer-Preimage-Commit
`dde132646f9e578f582231c2a7be946134490184` erneut tatsächlich qualifiziert.
Der aktuelle eingecheckte Nachweis mit SHA-256
`90fbe6856aeb09f89e382c59312f7035ac9777de57a316fc336bb81fcf5a7d4e`
bestand weiterhin 23/23 Kriterien.

Der tatsächliche ausschließlich synthetische Podman-Lauf verwendet neue
kontrollierte Pfade unter `C:\rep`:

    python tools/qualify_ebook_calibre_identity.py \
      --qualification-root C:\rep\tmp\SammlungsLotse\wi-0013-wi0011-requalification \
      --evidence-root C:\rep\artifacts\SammlungsLotse\wi-0013-wi0011-requalification

Qualifikations- und Evidenzziel müssen neue strikte Unterpfade sein. Die
Taskwurzel wird vollständig entfernt; die 22 pfadfreien stdout-/stderr-
Rohbelege bleiben außerhalb von Git für die manuelle Nachprüfung erhalten.

## Pull-Request-Prüfungen

Repository Quality führt die lokalen Projekt- und Governance-Prüfungen unter
Python 3.12 aus.

Artifact Registry Integrity validiert Registry-Änderungen, offene
Pull-Request-Kollisionen, den objektbasierten Merge und die Gleichheit mit dem
tatsächlichen Git-Textmerge.

Beim ersten Pull Request, der die Registry einführt, existiert kein
Registry-Basisstand. In diesem einmaligen Bootstrap-Fall wird der Head
vollständig validiert. Merge- und Cross-PR-Vergleiche beginnen mit dem ersten
nachfolgenden Pull Request.

## Verfügbarkeit verpflichtender Prüfungen

Ein ausgeführter Check mit fachlichem Fehler ist `VALIDATION_FAILURE` und darf
nicht umgangen werden. Kann ein Check wegen nachgewiesener externer
Infrastrukturstörung kein vertrauenswürdiges Ergebnis erzeugen, ist er
`INFRASTRUCTURE_UNAVAILABLE`. Ist die Ursache ungeklärt, lautet die
Klassifikation `UNKNOWN`.

SammlungsLotse besitzt derzeit kein autorisiertes Break-Glass-Verfahren.
Deshalb bleiben fehlende erforderliche Checks unabhängig von der
Klassifikation merge-blockierend. Eine spätere Einführung benötigt eine
angenommene Projektentscheidung, einen weiterhin prüfbaren Pull Request,
begrenzte Berechtigungen und verpflichtende Nachvalidierung nach der
Wiederherstellung. Ein fehlendes Ergebnis wird niemals als `validated`
dargestellt.

## Evidenz

Ein Prüfbericht nennt:

- Scope;
- betroffenen Vertrag;
- Plattform und relevante Version;
- Befehl oder Verfahren;
- Ergebnis;
- Datum;
- Einschränkungen und ausstehende Prüfungen.

CI-Ergebnisse gelten nur für den exakten geprüften Commit.
