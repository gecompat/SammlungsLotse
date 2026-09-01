# EXP-0017 Ausführung

Status: ACCEPTED — PREIMAGE IN PREPARATION, NOT EXECUTED

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
