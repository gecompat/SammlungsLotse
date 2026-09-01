# EXP-0017 Ausführung

Status: DONE — METHOD PASSED

Stand: 2026-09-01

Dieser Ordner bindet die ausschließlich synthetische Ausführung aus
`docs/planning/EBOOK_SYNTHETIC_DOWNSTREAM_ISOLATION_EXPERIMENT.md`.

Enthalten sind:

- `cases.json`: genau zwölf aus EXP-0016 abgeleitete Orakelfälle;
- `execution-profile.json`: exakte Fall-, Produkt-, Runtime-, Isolations-,
  Threat-Model-, Ausführungs- und Ausgabegrenzen;
- `result.json`: ausschließlich pfadfreie Aggregate des maßgeblichen Laufs;
- dieser Ausführungshinweis.

## Historische Ergebnisprüfung

```powershell
python tools/experiments/validate_exp_0017_result.py
```

Die dauerhafte Prüfung bindet Ergebnis, Profil, Fallmanifest und Runner an
das historische Git-Preimage
`53a1e2dbefd03c7d770e949490ea1ec7783bfe98`. Sie startet weder Container noch
EPUBCheck und materialisiert kein EPUB. Der ursprüngliche Aufruf
`python tools/experiments/run_exp_0017.py --validate-profile` bleibt für das
eingefrorene Ausführungspreimage gültig; spätere Dokumentations- und
Ergebnisänderungen werden absichtlich nicht als neuer Laufpreimage
umgedeutet.

## Gebundener Hauptlauf

Nach grüner Preimage-CI erfolgte genau ein maßgeblicher vollständiger Lauf
mit neuen, begrenzten Pfaden unter `C:\rep`:

```powershell
python tools/experiments/run_exp_0017.py `
  --execute `
  --confirm-green-preimage-ci `
  --temp-root C:\rep\tmp\SammlungsLotse\exp-0017\qualification-corrected `
  --result C:\rep\artifacts\SammlungsLotse\exp-0017\qualification-corrected\result.json
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

Ein methodischer `pass` ist keine Produktfreigabe. Die Ergebnisbindungswave
öffnet deshalb ein neues, getrenntes Gate.

## Maßgebliches Ergebnis

Der Hauptlauf bestand alle 18 methodischen Kriterien:

- zwölf Fälle, zwei Wiederholungen und genau 24 Providerläufe;
- null Kontext-, Schemagruppen- oder S3-Orakelmismatches;
- semantisch identische Wiederholungen bei vollständig bewahrten
  Providercode-Häufigkeiten;
- genau eine Kontrollverbindung und null Deep-Path-Kanarientreffer;
- effektiv zurückgelesenes `network=none` und vollständige
  Isolationsübereinstimmung;
- fail-closed Timeout- und Outputprobe;
- vollständiges Task- und Container-Cleanup;
- unveränderte Eingänge und null Produkt-, Bestands-, Persistenz-, externe
  Netzwerk- oder private Wirkung.

Das eingecheckte 4.429-Byte-Ergebnis besitzt SHA-256
`ffb748bc7429b4362392c1464b6268bf404df74625420a8498d405558c88db61`.
Es ist byteidentisch mit dem zunächst unter `C:\rep\artifacts` erzeugten und
vor der Übernahme geprüften Bericht. GATE-0020 ist als getrenntes offenes
Ergebnisgate registriert; keine Produktfortsetzung ist ausgewählt.

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
Der danach korrigierte Commit
`53a1e2dbefd03c7d770e949490ea1ec7783bfe98` bestand den vollständigen lokalen
Repositorytest und beide exakten Pflichtchecks. Nur dieser neue Preimage
wurde anschließend genau einmal vollständig ausgeführt und liefert das oben
gebundene Ergebnis. Kein weiterer Lauf ist für die Ergebnisbindung nötig
oder vorgesehen.
