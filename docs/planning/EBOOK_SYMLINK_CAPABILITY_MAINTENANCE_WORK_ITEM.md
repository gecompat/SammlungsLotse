# WI-0017: Fehlende Windows-Symlink-Fähigkeit in synthetischen Kontrollen sichtbar behandeln

Status: DONE — IMPLEMENTED AND VALIDATED

Stand: 2026-09-13

Artifact: WI-0017

## Zweck

WI-0017 vereinheitlicht zwei optionale synthetische Windows-Symlink-
Negativkontrollen mit dem bereits verwendeten Projektmuster: Kann das
Betriebssystem keinen Symlink erzeugen, wird die Fähigkeit als nicht
verfügbar sichtbar übersprungen. Ist sie verfügbar, bleibt die bestehende
Sicherheitsbehauptung unverändert ausführbar.

## Grenzen

- ausschließlich Test- und Experimentharnesses;
- keine Änderung unter `src/sammlungslotse/`;
- keine Änderung von TEST-0001-Fixtures, Hashes, Oracles oder historischen
  Ergebnissen;
- kein Netzwerk, keine Persistenz, kein Fachsystemzugriff und keine
  Produktwirkung.

## Akzeptanzkriterien

1. Genau die zwei nachweislich betroffenen Symlink-Testpfade fangen nur den
   Fehler fehlender Symlink-Berechtigung ab und überspringen dann sichtbar.
2. Jeder andere Fehler bleibt ein Testfehler.
3. Bei verfügbarer Symlink-Fähigkeit laufen die bestehenden Assertions
   unverändert.
4. Fokussierte Tests, Registry-/Projektprüfung, `compileall` und
   `git diff --check` sind tatsächlich erfolgreich.

## Ergebnis

Die zwei betroffenen Testpfade überspringen nun ausschließlich eine nicht
verfügbare Symlink-Fähigkeit. Alle übrigen Fehler bleiben sichtbar. Die
fokussierten 18 Tests bestanden unter Windows mit zwei erwarteten Skips.
