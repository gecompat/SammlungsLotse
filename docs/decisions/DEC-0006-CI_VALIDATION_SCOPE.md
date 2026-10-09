# DEC-0006: Vertragsbezogene CI-Prüfungen ohne doppelte Validatorläufe

Status: ACCEPTED

Datum: 2026-10-09

Artifact: DEC-0006

Artifact UID: urn:uuid:01a120e0-9c38-730e-a19d-0ecd7ee1104f

## Kontext

`Repository Quality` führte bei jedem PR-Head und nach jedem Merge die volle
Testsuite und zahlreiche direkte historische Ergebnisvalidatoren aus. Die
Suite validiert TEST-0001 und die direkt doppelt ausgeführten EXP-0002 bis
EXP-0007 sowie EXP-0009 bis EXP-0017 bereits mit zusätzlichen
Regressionen. Reine Änderungen an Projektstatus oder Übergabe beeinflussen
weder deren Eingänge noch Produkt- oder Fixturecode. Ein grüner alter Head darf
trotzdem keinen erforderlichen aktuellen CI-Check ersetzen.

## Entscheidung

Beide erforderlichen CI-Statuskontexte bleiben auf jedem PR-Head aktiv. Die
Projekt- und Registryprüfung laufen in `Repository Quality` immer. Nur wenn
der exakte Git-Diff ausschließlich
`docs/project/PROJECT_STATUS.md` und/oder `docs/project/HANDOVER.md` enthält,
entfallen dort Runtime-Suite, aktuelle Ergebnisqualifikationen und
Kompilierung. Der Projektvalidator prüft in diesem Fall weiterhin Quellen,
Links, Locators, Registry und Governance-Discovery. Inhaltliche Statusaussagen
bleiben an überprüfbare Repository-/GitHub-Evidenz und Review gebunden.

Jeder andere Pfad, ein leerer oder nicht ermittelbarer Diff, ungültige
Commitbindung oder ein Git-Fehler führt zur vollständigen Prüfung. Der
Statuspfad ist eine exakte Allowlist, keine allgemeine `docs/`-Ausnahme.
Produkt-, Experiment-, Fixture-, Tool-, Regel-, Workflow- und unbekannte
Änderungen behalten den vollen bestehenden Gateumfang. Die getrennte
`Artifact Registry Integrity`-Prüfung mit Cross-PR- und Mergevergleich bleibt
unverändert erforderlich.

Die direkt im Workflow wiederholten TEST-0001-, EXP-0002-bis-EXP-0007-
und EXP-0009-bis-EXP-0017-Ergebnisvalidatoren werden durch ihre vorhandenen
Suite-Prüfungen abgedeckt.
Zusätzliche Negativ- und Semantiktests der Suite bleiben bestehen. Die
aktuellen WI-Produktqualifikationsvalidatoren bleiben eigene Schritte, weil
die Suite deren vollständigen gespeicherten Ergebnisvertrag nicht abdeckt.
Ein neuer Validator erhält erst nach belegter Suite-Abdeckung dieselbe
Behandlung. Experimentläufe, historische Preimages, Hashes und Oracles werden
nicht verändert.

## Folgen und Kontrolle

Lokale Entwicklung beginnt mit den betroffenen Prüfungen; die erforderliche
CI validiert den stabilen Head. Der Selektor wird mit positiven Statusfällen,
Produkt-/Test-/gemeinsamen Abhängigkeitsänderungen sowie ungültiger und
fehlender Diff-Evidenz geprüft. CI meldet die gewählte Route. Ein Skip ist
`not applicable` für den begrenzten Status-Diff und nie eine Behauptung, die
Runtime-Prüfung sei frisch ausgeführt. Bei späteren neuen Abhängigkeiten des
Status oder der Übergabe ist die Allowlist vor deren Integration anzupassen.
