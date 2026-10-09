# DEC-0005: Lokalen Rule-Context-Cache selektiv einführen

Status: ACCEPTED

Datum: 2026-09-20

Artifact: DEC-0005

Artifact UID: urn:uuid:01a0bc3a-5288-7a54-88c6-3c248eb9d144

## Entscheidung

Die unveränderte Foundation-Referenzfähigkeit `rule-context-cache` wird
selektiv installiert. Sie darf ausschließlich operatorbereitgestellte,
nicht versionierte lokale Cacheziele verwenden.

## Grenzen

Native `AGENTS.md`-Discovery bleibt bei jeder Sitzung aktiv. Cache-Treffer
ersetzen weder Repositoryregeln noch Validierung und dürfen nur vorhandene
Sitzungsanalysen mit passendem Schlüssel wiederverwenden. Cacheinhalte,
absolute Pfade, Regeltexte und Zusammenfassungen werden nicht versioniert.

## Fortschreibung am 2026-10-09 durch WI-0023

Der ausdrücklich autorisierte Governanceauftrag erweitert die ursprüngliche
Entscheidung um die Foundation-1.20-Sessionbasis. Die Wahl von 2026-09-20
und ihre persistenten Grenzen bleiben als Historie bestehen.

Sichere Sessionwiederverwendung benötigt keinen persistenten Operatorcache
und keinen Record. Die unveränderte Core-Referenz
`.ai/foundation/runtime/processing_efficiency.py` darf tatsächlich vorhandene
Analysen ausschließlich im Speicher halten. Ein Client kann den gleichen
Vertrag implementieren; Python oder ein zusätzlicher Reader sind keine Pflicht.

Vollständige Auffindbarkeit und semantische Auswahl sind getrennte Verträge:
Alle maßgeblichen Projektquellen und alle angenommenen Entscheidungen müssen
auffindbar bleiben. Gelesen und für Wiederverwendung gebunden werden die für
den Auftrag relevanten Quellen samt transitiven semantischen Abhängigkeiten.
Ein Indexlink ist nicht automatisch eine semantische Abhängigkeit. Die
Auswahl darf keine für den Auftrag maßgebliche Regel ausschließen.

Vor Wiederverwendung sind aktuelle native Instruction-Reihenfolge und Inhalte,
effektive Discoveryeinstellungen, Repositoryidentität, Scope, ausgewählte
Working-Tree-Inhalte einschließlich dirty/untracked Quellen und vollständige
Abhängigkeiten zu prüfen. Die Auswahl und Abhängigkeiten werden sitzungslokal
geführt. Analysen stehen nur am exakten aktuellen Schlüssel zur Verfügung.
Geänderte Regeln invalidieren sich und alle transitiven semantischen
Abhängigen; geänderte Instructions oder Discoveryeinstellungen invalidieren
abhängige Analysen. Neue Scope-/Topologie-/Quellbindungen werden vollständig
geprüft. Bei unvollständiger Discovery oder verlorener Analyse wird gelesen.
Compaction stellt verlorene Analysen nicht wieder her.

Ein neuer Git-Commit oder Worktree erfordert einen frischen Autoritäts- und
Bindungsabgleich, verwirft nachgewiesen äquivalente Sessionanalyse aber nicht
allein wegen des Locators. Die separat ausgewählte persistente Fähigkeit
`rule-context-cache` behält dagegen ihren strengeren vollständigen Record-,
Git- und Worktreevertrag mit `CACHE_HIT`, `PARTIAL_INVALIDATION` und
`CACHE_MISS`. Persistente Ziele bleiben ausdrücklich operatorbereitgestellt,
lokal und nicht versioniert; es wird kein Defaultziel eingerichtet.

Der Projektvalidator bleibt ein Auffindbarkeitsgate für beide Wege. Sein
vollständiger Graph ist weder eine Leseliste noch eine Bescheinigung der
nativen Clientdiscovery oder der semantischen Analyse. Discoveryfehler
sperren Wiederverwendung; maßgebliche Quellen werden nicht entfernt, um das
Gate grün zu machen. Die Prüfverfahren stehen unter
[Validierung](../governance/VALIDATION.md).
