# GATE-0013: Ergebnis nach WI-0013 und V2-Opt-in bewerten

Status: DONE — OPTION A / DUALEN VERTRAG STABIL HALTEN

Stand: 2026-08-31

Artifact: GATE-0013

## Auswahlentscheidung

Der Nutzer hat am 2026-08-31 ausdrücklich Option A ausgewählt. Damit ist
GATE-0013 `done`. Der aktuelle duale Aufrufvertrag wird stabil gehalten:
V1 bleibt der bytekompatible Standard, V2 bleibt ausschließlich über
`--json --report-version v2` aktivierbar.

Diese Auswahl registriert keinen neuen Produktarbeitsgegenstand und startet
keine Produkt-, Migrations-, Deprecation-, Experiment- oder
Publikationswave. Sie schließt die Ergebnisbewertung nach WI-0013 ab und
bewahrt den qualifizierten Stand, bis neue Verbraucher- oder Fachevidenz eine
erneute ausdrückliche Entscheidung rechtfertigt.

## Gebundener Ergebnisstand

WI-0013 ist über Pull Request 55 als Merge-Commit
`cebbfe2d64a93b20f5e19236ab38a2420d192677` in `main` integriert und danach
lokal erneut geprüft. Der Produktnachweis bindet das vollständige Preimage
`dde132646f9e578f582231c2a7be946134490184` und erfüllt 29/29 Kriterien auf
fünf TEST-0001-Paaren, acht konformen EXP-0010-Qualitätsfällen und zwei
getrennten ungültigen Kontrollen.

Der aktuelle Vertrag belegt:

- `--json` erzeugt weiterhin bytegenau den V1-Bericht;
- nur `--json --report-version v2` erzeugt den rollenbewussten V2-Bericht;
- beide Versionen treffen dieselben fünf Entscheidungen mit denselben
  Regel-IDs und Evidenzkanälen;
- V2 erhält primäre und zusätzliche Identifier, `dcterms:modified`,
  Collection-Mitgliedschaften und 241/241 Provenienzeinträge;
- beide Versionen bleiben pfadfrei, deterministisch und read-only;
- null kritische False Same und zwei sichtbare
  `candidate_related`-Werkabweichungen bleiben belegt;
- der abhängige WI-0011-Calibre-Weg ist auf demselben Analyzer-Preimage
  erneut 23/23 qualifiziert und verwendet standardmäßig weiterhin V1.

Der Nachweis qualifiziert ausschließlich den gebundenen synthetischen
Produktvertrag. Er belegt keine Nutzung realer oder privater Medien, keine
automatische Migration vorhandener Verbraucher und keine Produktreife
jenseits dieses engen Ablaufs.

## Entscheidungskriterien

Die Fortsetzung wird ohne gewichteten Gesamtscore bewertet nach:

1. Stabilität für bestehende V1-Verbraucher;
2. direktem read-only Nutzwert des bereits verfügbaren V2-Opt-ins;
3. vorhandener Verbraucher- und Migrationsevidenz;
4. Reife einer fachlichen Publikationsregel;
5. Fehlerwirkung der zwei verbleibenden `candidate_related`-Hinweise;
6. Kopplung an Schema, CLI, Tests und Qualifikationsnachweise;
7. Reversibilität und Risiko vorzeitiger Architekturfestlegung.

## Mögliche Fortsetzungen

### A — Dualen Vertrag stabil halten

V1 bleibt Standard, V2 bleibt explizites Opt-in. Es entsteht kein neuer
Arbeitsgegenstand. Eine erneute Bewertung erfolgt erst bei konkreter
Verbrauchernachfrage, gemessener Migrationslast oder neuer fachlicher
Evidenz.

- unmittelbarer Nutzwert: der rollenbewusste Bericht ist bereits verfügbar;
- Kompatibilität: maximal für bestehende V1-Verbraucher;
- Kopplung: keine neue;
- Reversibilität: sehr hoch;
- Einordnung: **ausgewählt**.

### B — V2 als künftigen Standard vorbereiten

Eine spätere getrennte Entscheidung könnte Verbraucher inventarisieren,
Kompatibilitäts- und Migrationsanforderungen binden und erst danach einen
eigenen Arbeitsgegenstand für einen möglichen Defaultwechsel registrieren.

- potenzieller Nutzwert: rollenbewusste Ausgabe ohne Versionsoption;
- aktuelle Evidenzlücke: keine gebundene Verbraucherinventur oder
  Migrationsabnahme;
- Kopplung: hoch durch CLI-, Dokumentations- und Verbraucherwirkung;
- Einordnung: derzeit nicht proportional belegt.

### C — Publikationsregel produktcodefrei untersuchen

Ein neues enges Experiment könnte klären, welche beobachtbare Evidenz eine
eigene Publikationsentscheidung trägt und wann Enthaltung erforderlich
bleibt.

- Erkenntniswert: hoch für die weiterhin fehlende Publikationsstufe;
- unmittelbare Produktwirkung: keine;
- aktuelle Priorität: nicht durch neuen Nutzer- oder Fehlernachweis belegt;
- Einordnung: valide spätere Evidenzoption.

### D — Verbleibende Werkhinweise weiter härten

Eine weitere Regelwave könnte die zwei `candidate_related`-Abweichungen
adressieren, müsste aber zuerst zusätzliche Evidenz gegen Überanpassung und
False Negatives binden.

- Fehlerwirkung: manuelle Review-Hinweise, keine Gleichheitsfreigaben;
- Evidenzreife: zwei synthetische Restfälle reichen nicht für eine neue
  Produktregel;
- Einordnung: ohne weitere Evidenz nicht ausgewählt.

### F — Unabhängigen read-only Ast neu bewerten

Der Identitätsvertrag bleibt stabil, während ein getrenntes Gate eine andere
read-only Nutzerfrage bewertet. Diese Option überträgt keine Autorisierung
aus WI-0013 auf eine neue Produktfläche.

### K — Pausieren

Keine neue Wave und keine aktive Beobachtungsfrage. Der qualifizierte duale
Vertrag bleibt unverändert verfügbar.

## Vergleich

| Option | unmittelbarer Nutzwert | Evidenzreife | Kopplung | Reversibilität | zentrale Last |
|---|---:|---:|---:|---:|---|
| A — stabil halten | vorhanden | hoch | keine neue | sehr hoch | spätere Trigger beobachten |
| B — V2-Default vorbereiten | potenziell mittel | niedrig für Verbraucher | hoch | mittel | Inventur und Migration |
| C — Publikationsregel untersuchen | mittelbar | offen | niedrig | sehr hoch | neues Experiment |
| D — Werkhinweise härten | niedrig bis mittel | niedrig | mittel | mittel | Überanpassungsrisiko |
| F — unabhängiger Ast | getrennt | offen | niedrig bis mittel | hoch | neue Ergebnisfrage |
| K — pausieren | keine neue Wirkung | ausreichend zum Stoppen | keine | vollständig | kein neuer Nutzwert |

## Gate-Bewertung

WI-0013 hat den ausgewählten Rollen- und Provenienznutzen innerhalb seines
engen Vertrags vollständig geliefert. Der bisherige V1-Standard verhindert
eine unbelegte Verbraucherumstellung, während V2 bereits explizit nutzbar
ist. Für einen Defaultwechsel, eine Deprecation, eine Publikationsregel oder
eine weitere Regelhärtung liegt derzeit keine zusätzliche gebundene
Verbraucher- oder Fachevidenz vor.

Option A bewahrt daher den erreichten Nutzwert mit der kleinsten neuen
Kopplung. B, C, D, F und K bleiben nicht ausgewählt. Insbesondere entstehen
kein WI-0014 und keine neue Produktwave. Eine spätere Fortsetzung benötigt
ein neues getrenntes Gate und eine erneute ausdrückliche Nutzerauswahl.

## Kanten, die nicht überschritten werden

- V1 bleibt Standard; V2 bleibt Opt-in.
- Keine V1-Deprecation, -Entfernung oder automatische Verbrauchermigration.
- Keine neue Stufe `publication` und keine Publikationsregel.
- Die zwei `candidate_related`-Restfälle werden nicht umklassifiziert.
- Ein Standards-valider EPUB ist kein bibliografisches Identitätsorakel.
- Keine automatische Suche, mehrere Dateien, IDs oder Bibliotheken, neue
  Calibre-Felder, externe Metadaten, Persistenz, Routing, Browser, REST,
  Agents oder Writes.
- Fachsysteme bleiben führend; SammlungsLotse wirkt unterstützend und
  read-only.

## Gate-Folgen

- GATE-0013 ist mit der ausdrücklichen Auswahl von A `done`.
- Kein neuer Produktarbeitsgegenstand ist registriert.
- Produktcode, öffentlicher Vertrag, Fixtures und Nachweise bleiben
  unverändert.
- Ein V2-Default, eine V1-Deprecation, eine Publikationsstufe oder eine andere
  Produktfunktion benötigt eine neue ausdrückliche Ergebnisentscheidung.
