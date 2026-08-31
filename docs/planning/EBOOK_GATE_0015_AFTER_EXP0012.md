# GATE-0015: Ergebnis nach EXP-0012 und private Praxisevidenz bewerten

Status: DONE — OPTION A / EXP-0013 AUSGEWÄHLT

Stand: 2026-08-31

Artifact: GATE-0015

## Zweck

GATE-0015 trennt das positive Methodenergebnis von EXP-0012 von einer
Produktentscheidung. Es bewertet die drei Suchstrategien, deren fachliche
Grenzen und den anonymen privaten Praxissmoke. Ohne ausdrückliche Auswahl wird
weder ein weiteres Experiment noch ein Produktarbeitsgegenstand registriert.

## Auswahlentscheidung

Der Nutzer hat Option A am 2026-08-31 ausdrücklich ausgewählt. GATE-0015 ist
damit abgeschlossen und ausschließlich EXP-0013 als akzeptiertes, noch nicht
ausgeführtes Experiment registriert.

Die Auswahl autorisiert die getrennte Planung und Ausführung der
produktcodefreien Diagnose nach Merge und Post-Merge-Prüfung. Sie autorisiert
keine Produktkorrektur und keine Suchstrategie. Die Optionen B bis E und K
bleiben nicht ausgewählt.

Da private Pfade und Rohdaten des ersten Smoke absichtlich nicht gespeichert
wurden, müssen genau dieselben drei EPUBs für den späteren Hauptlauf erneut
explizit übergeben und als derselbe Eingangssatz bestätigt werden. EXP-0013
führt keine Verzeichnis- oder Dateisuche aus.

## Verifizierte Evidenz

EXP-0012 bestand auf dem Preimage `deddef0` 16/16 methodische Kriterien in
zwei semantisch identischen Wiederholungen. Alle 48 Strategie-/Aufgaben-
Kombinationen blieben auf genau eine synthetische Bibliothek, höchstens fünf
IDs und den getrennten WI-0011-Vergleich jedes Kandidaten begrenzt.

| Strategie | anwendbar | Kandidaten | Recall | Precision | Misses | Extras | Einordnung |
|---|---:|---:|---:|---:|---:|---:|---|
| V1 Identifier exakt | 3/8 | 4 | 1,0 | 0,75 | 0 | 1 | `eligible_with_tradeoffs` |
| V2 Titel+Autor exakt | 8/8 | 8 | 0,8889 | 1,0 | 1 | 0 | `not_qualified` |
| V3 Titel+Autor Contains | 8/8 | 10 | 1,0 | 0,9 | 0 | 1 | `eligible_with_tradeoffs` |

Es gab null unerwartete Kandidaten, null kritische False Same und keine
erreichte Fünfergrenze. Diese kleine synthetische Matrix belegt weder
allgemeine Recall-Werte noch Vollständigkeit oder Rankingqualität.

Der getrennte private Smoke nutzte genau drei EPUB-Kopien, materialisierte
eine lokale Bibliothek und führte vier Suchläufe aus. Quellen blieben
unverändert und alle Kopien sowie Container wurden bereinigt. Der Smoke blieb
`not_qualified`, weil 0/3 WI-0011-Vergleiche `completed` erreichten. Nur diese
Aggregation ist bekannt; Titel, Autoren, Pfade, Hashes, Rohoutputs und
Nichtabschlussgründe wurden absichtlich nicht aufbewahrt.

## Optionen

### A — Private Nichtabschlussgründe produktcodefrei diagnostizieren

**Ausgewählt als EXP-0013.**

Ein enges Folgeexperiment würde dieselben Grenzen beibehalten und höchstens
dieselben drei privaten EPUBs erneut kopieren. Es dürfte ausschließlich
pfadfreie WI-0011-Reason-Code-Häufigkeiten, Eintrittsstufen und Cleanup
aggregieren, ergänzt um synthetische Positivkontrollen. Es würde weder neue
private Dateien auswählen noch Metadaten oder Rohberichte speichern.

- Vorteil: schließt die größte Diskrepanz zwischen synthetischem Method-pass
  und privatem 0/3-Nachlauf;
- Risiko: auch Reason-Code-Aggregate benötigen eine strikte
  Vertraulichkeits- und Mindestmengenprüfung;
- Einordnung: **Empfehlung vor jeder Produktwave**.

### B — V1 als optionale Identifier-Suche für einen Produktvertrag prüfen

Ein neuer Arbeitsgegenstand könnte ausschließlich den exakten typisierten
Identifierweg betrachten. Fehlender Identifier bliebe `not_applicable`, und
mehrere Treffer müssten sichtbar ohne Ranking an WI-0011 übergeben werden.

- Vorteil: synthetisch vollständiger Recall in den drei anwendbaren Fällen;
- Nachteil: für 5/8 Aufgaben nicht anwendbar und beim wiederverwendeten
  Identifier nicht eindeutig;
- Einordnung: begrenzter möglicher Produktpfad, aber private Anschlussreife
  noch unbelegt.

### C — V3 als begrenzte Titel-/Autor-Kandidatensuche prüfen

Ein neuer Produktvertrag könnte die Contains-Suche mit maximal fünf IDs,
sichtbarer Sättigung und zwingendem WI-0011-Nachlauf untersuchen.

- Vorteil: synthetisch 1,0 Recall;
- Nachteil: Zusatzkandidaten und unbekannte reale Precision; kein Ranking und
  keine Vollständigkeit;
- Einordnung: nützlich, aber vor privater Ursachenklärung verfrüht.

### D — Einen mehrstufigen Suchvertrag weiter experimentieren

Ein weiteres produktcodefreies Experiment könnte Identifier, exakten
Titel/Autor und Contains als getrennte, nachvollziehbare Stufen vergleichen.
Es dürfte Treffer weder verdecken noch ranken und müsste Abbruch- sowie
Enthaltungsregeln vorab binden.

- Vorteil: könnte Anwendbarkeit und Zusatzkandidaten besser austarieren;
- Nachteil: neue Orchestrierungs- und Erklärkopplung;
- Einordnung: erst nach Klärung des privaten 0/3-Befunds.

### E — Nur die synthetische Evidenz konservieren

Keine neue Ausführung und kein Produktcode. EXP-0012 bleibt historisch
prüfbar; weitere Arbeit beginnt nur bei einem konkreten Nutzertrigger.

### K — Pausieren

Keine neue Wave. V1/V2 des Identitätsvertrags und alle bisherigen Nachweise
bleiben unverändert verfügbar.

## Empfehlung

Option A ist der kleinste belastbare nächste Schritt. Der Suchmechanismus
lieferte im privaten Smoke vier begrenzte Suchläufe, aber die entscheidende
nachgelagerte Identitätsbewertung blieb in allen drei Fällen unvollständig.
Eine Produktsuche auf Basis ausschließlich der synthetischen Matrix würde
diese reale Anschlusslücke überspringen.

Die Empfehlung nahm A für sich noch nicht an. Der Nutzer hat A inzwischen
ausdrücklich ausgewählt. EXP-0013 bindet deshalb genau die produktcodefreie
Diagnose; eine spätere Produktübernahme benötigt unabhängig vom Ergebnis ein
neues getrenntes Gate.

## Harte Grenzen

- Method-pass ist keine Produktfreigabe.
- Suchtreffer sind keine Identitäts-, Ziel- oder Schreibentscheidung.
- V2 `not_qualified` wird nicht durch V3-Recall verdeckt.
- Private 0/3 sind ein offener Befund, keine Aussage über die Bücher selbst.
- Keine weiteren privaten Dateien ohne neue ausdrückliche Grenze.
- Keine privaten Metadaten, Pfade, Hashes oder Rohoutputs in Git.
- Keine direkte `metadata.db`-Nutzung, kein Netzwerk und keine Persistenz.
- Mehrere Bibliotheken, Ranking, UI, API, Agents und Writes bleiben außerhalb.

## Gate-Stand

- GATE-0015 ist `done`.
- EXP-0013 ist `accepted`, aber noch nicht ausgeführt.
- Kein Produktarbeitsgegenstand ist registriert; Produktcode bleibt
  unverändert.
- Die Ausführung beginnt erst in einer neuen isolierten Wave vom gemergten
  `origin/main` und benötigt die erneute explizite Übergabe derselben drei
  privaten EPUBs.
