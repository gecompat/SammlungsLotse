# WI-0012: False-Same-Guardrail für den EPUB-Identitätsbericht umsetzen

Status: ANGENOMMEN — IMPLEMENTIERUNG AUSSTEHEND

Stand: 2026-08-31

Artifact: WI-0012

## Ziel und kleinster Nutzwert

Der bestehende read-only EPUB-Identitätskandidatenbericht soll die in
EXP-0010 belegte False-Same-Kaskade fail-safe stoppen. Überlappende
Identifier, Titel und Creator dürfen bei verschiedener Repräsentation keine
Ausgabengleichheit mehr erzeugen. Dadurch darf auch die Werkebene diese
unqualifizierte Ausgabengleichheit nicht mehr als Werkgleichheit übernehmen.

Die Wave verbessert ausschließlich die Sicherheit der vorhandenen
Kandidatenentscheidung. Sie führt kein vollständiges bibliografisches
Identitätsmodell ein und bestätigt weiterhin keine Dublette.

## Guardrail-Vertrag

Die fünf vorhandenen Ebenen bleiben unverändert:

1. `byte`;
2. `package`;
3. `representation`;
4. `edition`;
5. `work`.

Auf Ausgabenebene gilt nach WI-0012:

- `candidate_same` benötigt gleiche Repräsentation;
- Titel müssen überlappen;
- vorhandene Creator müssen kompatibel sein;
- Sample-/Vollausgaben- und Sprachkonflikte bleiben vorrangige
  Gegenbelege;
- Identifier-Überlappung bleibt sichtbare positive Evidenz, kann eine
  unterschiedliche Repräsentation aber nicht überstimmen;
- bei unterschiedlicher Repräsentation bleibt die Ausgabe `different` oder
  `abstain`.

Die Werkebene darf `candidate_same` nur aus einer nach diesen Bedingungen
qualifizierten Ausgabengleichheit ableiten. Bestehende
`candidate_related`-Hinweise bleiben getrennte, schwächere Kandidatenevidenz
und werden nicht als Gleichheit dargestellt.

## Kompatibilitätsgrenze

Das öffentliche Schema
`sammlungslotse/ebook-identity-candidate-report/v1`, CLI-Parameter,
Prozesscodes, Eingangsgrenzen und die getrennten Evidenzkanäle bleiben
unverändert. Ein geänderter Rule-Code darf die neue strengere Bedingung
sichtbar machen, ohne neue öffentliche Felder einzuführen.

Die strengere Regel kann bisherige `edition_candidate`-Ergebnisse in
`related_work_candidate` oder `abstain` überführen. Diese geringere Abdeckung
ist wegen der hohen False-Same-Kosten ein bewusster, dokumentierter Trade-off.

## Produktqualifikation

Die Implementierungs-Wave erzeugt einen neuen aktuellen, ausschließlich
synthetischen Produktnachweis. Er bindet:

- die fünf vorhandenen WI-0009-/TEST-0001-Paare;
- die acht konformen Qualitätsfälle aus dem unveränderten
  EXP-0010-Fallmanifest;
- zwei tatsächliche JSON-CLI-Wiederholungen je Fall;
- eine deutsche CLI-Ansicht;
- das vollständige aktuelle Produkt- und Qualifikationspreimage;
- unveränderte Eingangs-Hashes, Pfadfreiheit und fehlende Produktwirkungen.

Die drei bisher fehlerhaften EXP-0010-Fälle dürfen auf Ausgabe und Werk kein
`candidate_same` mehr liefern. Der positive Fall mit gleicher Repräsentation
muss seine qualifizierte Ausgaben- und Werkgleichheit behalten. Verbleibende
Abweichungen der noch nicht rollenbewussten Werk- oder Collection-Semantik
werden sichtbar dokumentiert und nicht als durch WI-0012 gelöst bezeichnet.

`experiments/ebook/exp-0010/result.json`, Falloracles und Experimentpreimage
bleiben unverändert. Die bestehende CI-geeignete EXP-0010-Prüfung muss den
eingefrorenen historischen Befund weiterhin erfolgreich validieren.

Der aktuelle Produktnachweis unter
`runtime/ebook-identity/qualification.json` darf auf eine neue interne
Evidenzversion fortgeschrieben werden. Das öffentliche Produktberichtsschema
bleibt davon unberührt; der frühere WI-0009-Nachweis bleibt über die
Git-Historie erhalten.

## Akzeptanzkriterien

WI-0012 ist erst `done`, wenn:

1. `candidate_same` auf Ausgabenebene gleiche Repräsentation, überlappende
   Titel und kompatible vorhandene Creator voraussetzt;
2. Sample-/Vollausgaben- und Sprachkonflikte weiterhin vorrangig
   `different` ergeben;
3. Identifier-Überlappung bei verschiedener Repräsentation keine
   Ausgabengleichheit mehr erzeugt;
4. Werkgleichheit nur aus einer nach dem Guardrail qualifizierten
   Ausgabengleichheit folgt;
5. alle sechs kritischen EXP-0010-False-Same-Befunde entfallen;
6. der EXP-0010-Positivfall mit gleicher Repräsentation weiterhin
   `candidate_same` auf Ausgabe und Werk ergibt;
7. die fünf vorhandenen WI-0009-Produktfälle ihre weiterhin gültigen
   Entscheidungen behalten;
8. öffentliches v1-Schema, CLI, Prozesscodes und fünf Ebenen unverändert
   bleiben;
9. positive, negative und fehlende Evidenz sowie Enthaltung getrennt und
   deterministisch bleiben;
10. zwei tatsächliche JSON-CLI-Wiederholungen je Qualifikationsfall
    byteidentisch sind und die deutsche Ansicht denselben Zustand wiedergibt;
11. Qualifikationsmaterial und Produktoutput synthetisch, pfadfrei und ohne
    reale oder private Medien bleiben;
12. Eingänge unverändert bleiben und Produktcode weder Netzwerk-,
    Persistenz-, Fachsystem- noch Writerfähigkeit erhält;
13. EXP-0010-Ergebnis, Falloracles und Preimage unverändert bleiben und
    `python tools/experiments/validate_exp_0010_result.py` weiterhin
    erfolgreich gegen den gebundenen historischen Git-Commit ist;
14. fokussierte Produkt- und Experimenttests sowie vollständige
    Repository-, Registry-, TEST-0001-, Produktnachweis-, `compileall`,
    `git diff --check`- und Foundation-Regression erfolgreich sind;
15. Projektstatus, Übergabe, Validierungs- und Bedienungsdokumentation den
    tatsächlichen Stand und die ungelösten Modelllücken wiedergeben.

## Nichtziele

Nicht Bestandteil sind ein rollenbewusstes Metadatenmodell v2, eine eigene
Publikationsstufe, Umbenennung von `work_references`, vollständige
Collection-Semantik, Änderung der EXP-0010-Oracles, neue Eingaben oder
Provider, Calibre-Erweiterung, automatische Suche, Verzeichnissuche,
Persistenz, Index, Routing, Browser, REST, Agents, KI-Ähnlichkeit,
bestätigte Dublette oder jede schreibende Bestandsoperation.

## Ausführungsreihenfolge

1. GATE-0010-Auswahl und WI-0012-Vertrag werden getrennt nach `main`
   integriert.
2. Die Implementierungs-Wave startet aus dem danach verifizierten
   `origin/main` in einem eigenen Worktree.
3. Zuerst reproduzieren fokussierte Tests die drei False-Same-Kaskaden; dann
   wird ausschließlich der Guardrail umgesetzt.
4. Das vollständige Produktpreimage wird vor dem tatsächlichen synthetischen
   Qualifikationslauf commitgebunden.
5. Erst nach lokaler Regression, erforderlichen GitHub-Checks, regulärem
   Merge und Post-Merge-Prüfung wird WI-0012 als `done` geführt.
