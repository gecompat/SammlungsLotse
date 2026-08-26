# DEC-0001: SammlungsLotse als eigenständiges Projekt

Status: ACCEPTED

Datum: 2026-08-26

Artifact UID: urn:uuid:01a03e7f-489c-7472-880b-a749eab5f316

## Kontext

Die ursprünglichen Ziele von FolioTone bleiben relevant. Die vorhandene
Implementierung und Planung haben sich jedoch von der gewünschten Rolle eines
unterstützenden Systems entfernt.

Eine Fortsetzung im bestehenden Repository würde Produktkorrektur,
Architekturrückbau, historische Planung und neue Entwicklung vermischen.

## Entscheidung

SammlungsLotse ist ein neues, eigenständiges Projekt mit eigener
Projektidentität, eigener Planung und eigenem Repository.

FolioTone ist Referenz und mögliche Spenderquelle. SammlungsLotse ist kein
FolioTone-Fork und übernimmt weder dessen Backlog noch dessen
Implementierungsstatus.

## Folgen

- Produktgrenzen werden vor der Entwicklungsplanung neu festgelegt.
- Komponenten werden einzeln statt als Gesamtarchitektur bewertet.
- FolioTone-Identifikatoren werden nicht als SammlungsLotse-Identifikatoren
  weitergeführt.
- Übernahmen benötigen Rechte-, Herkunfts-, Kopplungs- und Testprüfung.
- Gewonnene Erkenntnisse und Fehlerbilder dürfen als fachliche Evidenz
  verwendet werden.
