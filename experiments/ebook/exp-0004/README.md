# EXP-0004 — Gestufte E-Book-Identitätskandidaten

Status: RUNTIME_EMPIRICAL PASSED — KEINE PRODUKTQUALIFIKATION

Stand: 2026-08-27

Artifact: EXP-0004

## Ergebnis

Das Profil `exp-0004-identity-heuristic/v1` hat alle 15 Akzeptanzkriterien
gegen TEST-0001 `0.2.0` erfüllt. Sechs synthetische Beziehungspaare wurden in
zwei Wiederholungen auf fünf strikt getrennten Ebenen bewertet:

| Sollpaar | Byte | Paket | Repräsentation | Ausgabe | Werk |
|---|---|---|---|---|---|
| Leseprobe / Vollausgabe | verschieden | verschieden | verschieden | Enthaltung | Kandidat gleich |
| bytegleich, andere Locators | Kandidat gleich | Kandidat gleich | Kandidat gleich | Kandidat gleich | Kandidat gleich |
| neuverpacktes EPUB | verschieden | Kandidat gleich | Kandidat gleich | Kandidat gleich | Kandidat gleich |
| EPUB / PDF derselben Ausgabe | verschieden | nicht anwendbar | verschieden | Kandidat gleich | Kandidat gleich |
| Ausgabe / Übersetzung | verschieden | verschieden | verschieden | verschieden | Kandidat verwandt |
| gleicher Titel, verschiedene Werke | verschieden | verschieden | verschieden | verschieden | verschieden |

Alle ausgegebenen Kandidaten enthalten sowohl positive als auch negative
Evidenz. Fehlende Evidenz wird separat geführt. Kein Ergebnis wurde zu einer
booleschen Dublette verdichtet; kein Kandidat löste Zusammenführung,
Entfernung, Verschieben, Schreiben oder eine andere Bestandswirkung aus.

## Messwerte

Precision und Recall betrugen auf allen fünf Ebenen im kleinen synthetischen
Goldstandard jeweils 1,0. Es gab keine False Positives. Die selektive
Genauigkeit betrug je Ebene 1,0. Die Abdeckung war auf Byte-, Paket-,
Repräsentations- und Werkebene 1,0. Auf Ausgabenebene betrug sie 5/6, weil
Leseprobe und Vollausgabe wegen ähnlicher Werkmetadaten bei gleichzeitig
verschiedenen Ausgabenidentifikatoren und unterschiedlichem Inhaltsumfang
begründet zur Enthaltung führten. Diese Enthaltung entsprach dem Oracle.

Die perfekten Werte sind keine Schätzung für reale Sammlungen. Der
Goldstandard umfasst nur sechs gezielt konstruierte Paare und testet die
vorab festgelegten Grenzen, nicht Robustheit gegenüber realem Metadatenrauschen.

## Profil und Methode

Der Runner nutzt ausschließlich Python 3.12 aus der Standardbibliothek und
führt keinen Netzwerkzugriff aus. Er liest die manifestgebundenen Fixtures
read-only und schreibt nur das versionierte Experimentergebnis.

1. `byte` vergleicht SHA-256 und behält beide Locators bei.
2. `package` hasht sortierte logische ZIP-Eintragsnamen, Inhalte und Größen;
   ZIP-Reihenfolge, Kompression und Kommentar sind keine logische Identität.
3. `representation` vergleicht nur formatgleiche logische
   Repräsentationsdigests. Das Profil normalisiert Verpackungsreihenfolge,
   aber keine semantisch äquivalenten XML- oder Inhaltsumschreibungen.
4. `edition` kombiniert Repräsentations-, Identifikator-, Sprach-,
   Titel-/Creator- und fallgebundene bibliografische Evidenz.
5. `work` erhält Ausgaben- und Sprachunterschiede und kann zwischen
   `candidate_same`, `candidate_related`, `different` und `abstain`
   unterscheiden.

TEST-0001 definiert keine eigene Paketbeziehung. Deshalb bindet das
Ausführungsprofil vor dem Lauf einen separaten Paket-Oracle an alle sechs
Fälle: nur Bytegleichheit und Neuverpackung sind Paketkandidaten; der
formatübergreifende Fall ist nicht anwendbar. Die Klassifikatoren lesen die
Beziehungsoracles nicht. Ein Unit-Test verändert das Beziehungsoracle und
bestätigt, dass die berechneten Entscheidungen unverändert bleiben, während
die Sollvergleiche erwartungsgemäß wechseln.

## Reproduzieren und validieren

Vollständiger lokaler Lauf:

    python tools/experiments/run_exp_0004.py

CI-geeignete Prüfung des eingecheckten Ergebnisvertrags:

    python tools/experiments/run_exp_0004.py --validate-result

Fokussierte Tests:

    python -m unittest tests.experiments.test_exp_0004

Der vollständige Lauf erzeugt zwei unabhängige Bewertungen. Laufzeiten und
verarbeitete Byteumfänge bleiben als Ressourcenevidenz je Stufe sichtbar;
der semantische Digest schließt variable Laufzeiten aus. Beide semantischen
Wiederholungsdigests müssen identisch sein. Vorher-/Nachher-Hashes binden die
Unverändertheit aller Eingänge. Das Ergebnis hält zusätzlich den SHA-256 des
ausführenden Runners fest.

## Grenzen

- Nur kleine, synthetische und eigenständig erzeugte TEST-0001-Fälle wurden
  verarbeitet; reale oder private Sammlungsdaten waren nicht beteiligt.
- Die Titelqualifikator-Regel kennt ausschließlich den synthetischen Begriff
  `Leseprobe`; sie ist kein Produktvokabular.
- Der EPUB/PDF-Fall nutzt einen fallgebundenen synthetischen
  Ausgabenschlüssel. Vertrauen, Konflikte und Provenienz realer Provider sind
  nicht qualifiziert.
- Fehlende eingebettete Werkreferenzen bleiben sichtbar. Eine echte
  Werkautorität oder globale bibliografische Auflösung wurde nicht gebaut.
- Statistische Ähnlichkeit, externe Provider, Persistenz, UI, API, Writer und
  Bestandsänderungen liegen außerhalb des Versuchs.
- Das Profil ist ein wegwerfbarer Erkenntnisnachweis. Es wählt weder
  Produktmodell noch Technologie-Stack oder ersten Vertikalablauf.

## Ableitbare nächste Frage

Der synthetische Nachweis spricht dafür, Datei-, Paket-, Repräsentations-,
Ausgaben- und Werkbeziehungen auch in einer späteren Lösung getrennt zu
untersuchen und Enthaltung als normales Ergebnis zu behandeln. Vor einer
Produktentscheidung fehlen mindestens größere adversarielle Sollmengen,
Metadatenrauschen, echte Provider-Provenienz und Nutzerreview-Messungen.
Diese offenen Punkte werden nicht durch den 15/15-Nachweis geschlossen.
