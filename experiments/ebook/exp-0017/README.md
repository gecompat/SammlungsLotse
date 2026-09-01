# EXP-0017 Ausführung

Status: ACCEPTED — CORRECTED PREIMAGE IN PREPARATION

Stand: 2026-09-01

Dieser Ordner bindet die ausschließlich synthetische Ausführung aus
`docs/planning/EBOOK_SYNTHETIC_DOWNSTREAM_ISOLATION_EXPERIMENT.md`.

Enthalten sind zunächst:

- `cases.json`: genau zwölf aus EXP-0016 abgeleitete Orakelfälle;
- `execution-profile.json`: exakte Fall-, Produkt-, Runtime-, Isolations-,
  Threat-Model-, Ausführungs- und Ausgabegrenzen;
- dieser Ausführungshinweis.

Ein `result.json` existiert absichtlich noch nicht. Der Hauptlauf ist erst
zulässig, nachdem der vollständige lokale Repositorytest einmal auf dem
sauberen Ausführungspreimage bestanden hat und beide GitHub-Pflichtchecks
exakt denselben Commit grün melden.

## Preimage-Prüfung

```powershell
python tools/experiments/run_exp_0017.py --validate-profile
```

Die Prüfung liest ausschließlich Vertrag, Manifest, Produkt- und
Runtime-Bindungen sowie das saubere Git-Preimage. Sie startet keinen
Container und materialisiert kein EPUB.

## Gebundener Hauptlauf

Nach grüner Preimage-CI darf genau ein vollständiger Lauf mit neuen,
begrenzten Pfaden unter `C:\rep` erfolgen:

```powershell
python tools/experiments/run_exp_0017.py `
  --execute `
  --confirm-green-preimage-ci `
  --temp-root C:\rep\tmp\SammlungsLotse\exp-0017\qualification `
  --result C:\rep\artifacts\SammlungsLotse\exp-0017\qualification\result.json
```

Der Runner erzeugt die EPUB-Bytes ausschließlich im Speicher. Eine
kurzlebige Kanarie lauscht nur auf IPv4-Loopback; ihr Port, ihre Zielwerte und
alle Payloads bleiben aus dem Ergebnis. Nach genau einer lokalen
Sensitivitätsverbindung wird der Zähler zurückgesetzt. Anschließend laufen
die zwölf Fälle zweimal über den unveränderten `EpubCheckProvider` und
`PodmanExecutor` mit `network=none`.

Der Ergebnisvertrag enthält nur Aggregate und öffentliche Providercodes,
keine EPUBs, Rohberichte, Meldungstexte, URLs, Ports, Container- oder
Tasknamen, Hostdaten, Zeitstempel oder absolute Pfade. Produktcode,
WI-0004-Gate und WI-0005-Profil bleiben unverändert.

Ein methodischer `pass` ist keine Produktfreigabe. Unabhängig vom Ausgang
öffnet die spätere Ergebnisbindungswave ein neues, getrenntes Gate.

## Nicht autoritativer erster Lauf

Das erste grüne Ausführungspreimage
`2bb29e0ac2b4dd45ac452364ece0f9addbb1572a` wurde genau einmal ausgeführt.
Alle 24 Matrixaufrufe waren `completed`, pro Wiederholung wurden alle zwölf
Providerprozesse gestartet, isoliert und bereinigt. Orakelmismatches,
Kanarientreffer und verbotene Wirkungen waren null; Assessments und
Providercode-Häufigkeiten waren identisch. Der Bericht blieb dennoch korrekt
`inconclusive`, weil der Harness die um zwei Byte abweichende
Rohbericht-Gesamtgröße fälschlich als Teil der semantischen Gleichheit
behandelte.

Dieser 4.439-Byte-Bericht mit SHA-256
`42e36e7680c512b39006e9ae5ba582bfe4916525c336db6118987d594095c728`
bleibt unverändert außerhalb von Git und wird nicht als EXP-0017-Ergebnis
übernommen. Die Korrektur entfernt ausschließlich Rohbericht-Größenrauschen
aus der Semantikprojektion; die getrennten Größenaggregate bleiben sichtbar.
Ein neuer vollständiger Lauf ist erst nach neuem sauberem Preimage und erneut
grüner exakter CI zulässig.
