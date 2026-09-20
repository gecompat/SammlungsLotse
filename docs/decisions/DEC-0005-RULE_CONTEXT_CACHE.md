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
