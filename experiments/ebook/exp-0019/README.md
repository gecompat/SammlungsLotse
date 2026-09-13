# EXP-0019-Ausführung

Status: DONE — METHOD PASSED

Stand: 2026-09-13

Dieser Ordner enthält den ausschließlich synthetischen Nachweis aus
`docs/planning/EBOOK_INBOX_CALIBRE_REVIEW_PLAN_EXPERIMENT.md`. Der Runner
liest weder einen lokalen Eingangsordner noch eine Calibre-Bibliothek und
startet Calibre nicht.

## Enthaltene Nachweise

- `cases.json` bindet genau zehn synthetische Fälle;
- `result.json` enthält nur Klassen, Positionsnummern, externe synthetische
  IDs, Gründe und Snapshot-Digests;
- der Runner erzeugt zwei semantisch identische Wiederholungen und bereinigt
  seinen flüchtigen Bereich vollständig.

Der eingecheckte Lauf bestand die zehn gebundenen Klassen. Er hielt die
Grenzen von drei Bibliotheken, fünf Kandidaten je EPUB und zwölf Kandidaten
je Ordner ein. Die Grenzprobe bleibt als `review_scope_incomplete` sichtbar.
Kein Ergebnis behauptet `same`, `new`, `import` oder eine Zielbibliothek.

## Ergebnisprüfung

```powershell
python tools/experiments/run_exp_0019.py --validate-result
```

Die Prüfung wiederholt keinen Zugriff auf Medien, Calibre oder Netzwerk. Sie
bindet Ergebnis und Fallmatrix, prüft die Orakel, die zwei Wiederholungen,
die Kandidaten- und Bibliotheksgrenzen sowie die Abwesenheit von Quellpfaden
und Projektionsmetadaten im Ergebnis.

Ein methodischer Erfolg qualifiziert nur diese synthetische Matrix. Ein
getrenntes Ergebnisgate entscheidet erst danach über einen möglichen
Produktarbeitsgegenstand.
