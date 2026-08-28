# EXP-0009: Identitäts- und Enthaltungsevidenz verbreitern

Status: DONE — METHODE 12/12, PRODUKTQUALITÄT NOT_QUALIFIED

Stand: 2026-08-28

Artifact: EXP-0009

## Gate-Entscheidung

Der Nutzer hat am 2026-08-28 in GATE-0008 ausdrücklich Option A gewählt.
Damit ist genau dieses Evidenzexperiment angenommen. Die Wahl nimmt keine
Produktänderung, Kandidatensuche, Architektur, Provider-, Persistenz-, UI-,
API-, Agent- oder Writerentscheidung vorweg. Die Alternativen B bis K bleiben
als möglicher späterer Optionsraum erhalten.

## Entscheidungsfrage

Welche Qualitätsaussage trägt der unveränderte WI-0009-Identitätsdienst auf
einer breiteren, vorab gebundenen und adversariellen synthetischen Paarmatrix,
wenn Treffer, Fehler und Enthaltung je Identitätsebene getrennt gemessen
werden?

EXP-0009 soll insbesondere klären:

- ob `candidate_same` und `candidate_related` nur dort erscheinen, wo das
  fallbezogene Oracle sie zulässt;
- wo echte Beziehungen übersehen oder nur mit Enthaltung beantwortet werden;
- ob fehlende, widersprüchliche und normalisierbare Metadaten getrennt und
  nachvollziehbar bleiben;
- ob Reason-Codes und Evidenzkanäle jede Entscheidung erklären;
- ob zwei vollständige Wiederholungen semantisch identisch bleiben.

## Untersuchungsgegenstand

Der Versuch ruft ausschließlich den auf dem Experimentpreimage vorhandenen
`IdentityCandidateService` auf. Produktmodule unter
`src/sammlungslotse/ebook_identity/` werden in dieser Wave weder verändert
noch durch experimentelle Klassifikationslogik ersetzt. Der Runner darf nur:

1. ein versioniertes Manifest mit Generatorparametern und Oracles lesen;
2. kleine EPUB-Paare in einem expliziten temporären Verzeichnis unter
   `C:\rep\tmp\SammlungsLotse\exp-0009` erzeugen;
3. jedes Paar über zwei getrennte In-Memory-Snapshots auswerten;
4. zwei unabhängige Wiederholungen vergleichen;
5. einen pfadfreien Ergebnisvertrag in Git schreiben;
6. sämtliche temporären Dateien nach dem Lauf entfernen.

Netzwerk, externe Werkzeuge, Calibre, reale oder private Medien, persistente
Sammlungsdaten, Bestandsaktionen und Produktcode liegen außerhalb.

## Vorab gebundene Fallmatrix

Die Ausführungswave materialisiert genau 18 kleine synthetische Paare. Das
Manifest bindet je Fall die erlaubten Entscheidungen auf allen fünf Ebenen,
die erwartete Assessment-Art sowie verbotene Wirkungen. Mehrdeutige
bibliografische Beziehungen dürfen mehrere konservative Entscheidungen
zulassen; sie werden nicht künstlich auf eine einzige Wahrheit reduziert.

| Gruppe | Fälle | Zu prüfende Grenze |
|---|---|---|
| positive Dateievidenz | bytegleich mit anderem Locator; ZIP neu gepackt; nur OPF-Verpackung geändert | Byte-, Paket- und Repräsentationsgleichheit bleiben getrennt. |
| Normalisierung | Unicode-Komposition; Groß-/Kleinschreibung und Leerraum | Normalisierung erzeugt Evidenz, aber keine neue bibliografische Wahrheit. |
| Ausgabenbezug | gleicher Identifier mit passender Ausgabe; wiederverwendeter Identifier bei Titelkonflikt; Leseprobe gegen Vollausgabe | Identifier, Inhalt und Metadatenkonflikte bleiben sichtbar. |
| Werkbezug | Übersetzung mit gemeinsamer Werkreferenz; revidierte Ausgabe mit gemeinsamer Werkreferenz; explizite Sammlung und Bestandteil | Ausgabe und Werkbezug werden nicht zusammengezogen. |
| harte Negative | Titelkollision mit verschiedenen Creators; gleichlautende Metadaten mit ausdrücklich widersprüchlichen Werkreferenzen | Falsche Gleichheits- und Verwandtschaftskandidaten werden messbar. |
| fehlende Evidenz | beide Seiten ohne bibliografische Metadaten; einseitig fehlender Identifier und Creator | Enthaltung und fehlende Evidenz bleiben eigene Ergebnisse. |
| nicht bewertbar | beschädigtes ZIP; unsicherer Paketpfad; doppelte logische ZIP-Einträge | Preflight oder Parser schließt fail-closed mit `not_assessed`. |

Die konkreten Feldwerte, Inhalte, ZIP-Parameter, erlaubten Entscheidungen und
Generatorversionen werden vor dem ersten Lauf im Manifest eingefroren. Der
Klassifikator darf dieses Oracle nicht lesen.

## Messvertrag

Für `byte`, `package`, `representation`, `edition` und `work` werden getrennt
erhoben:

- vollständige Oracle-gegen-Entscheidung-Matrix;
- True Positives, False Positives und False Negatives für
  `candidate_same` sowie auf Werkebene zusätzlich `candidate_related`;
- Precision, Recall, selektive Genauigkeit, Abdeckung und Enthaltungsrate;
- korrekte und unerwartete Enthaltungen;
- kritische False Positives: unzulässiges `candidate_same` auf Ausgabe- oder
  Werkebene sowie unzulässiger positiver Datei-, Paket- oder
  Repräsentationstreffer;
- Erklärungsvollständigkeit aus `rule_id`, positiver, negativer und fehlender
  Evidenz;
- `not_assessed`-Gründe, Pfadfreiheit, Originalunverändertheit und Wirkungen;
- semantischer Digest und Ressourcenwerte je Wiederholung.

Eine Metrik mit Nenner null wird als `not_applicable` ausgewiesen und nicht
als perfekte Qualität dargestellt. Die Ergebniszusammenfassung trennt
Messvertragsstatus und beobachtete Produktqualität.

## Akzeptanzkriterien für den Versuch

EXP-0009 ist methodisch ausgeführt, wenn:

1. Manifest, Runner, vollständiger Identitäts-Produktpreimage und Ergebnis
   durch SHA-256 gebunden sind;
2. genau 18 manifestierte Paare ausgeführt werden, davon 15 vollständig und
   drei erwartbar `not_assessed`;
3. jede vollständige Bewertung genau fünf geordnete Ebenen enthält;
4. alle Entscheidungen gegen die vorab erlaubte Oracle-Menge geprüft werden;
5. sämtliche vereinbarten Metriken aus den Rohentscheidungen neu berechenbar
   sind;
6. kritische False Positives weder verdeckt noch durch Mittelwerte
   relativiert werden;
7. positive, negative und fehlende Evidenz sowie `rule_id` pro Ebene
   erhalten bleiben;
8. zwei unabhängige Wiederholungen denselben semantischen Digest besitzen;
9. generierte Eingänge während der Bewertung unverändert bleiben und danach
   vollständig entfernt werden;
10. Ergebnis und Fehlertexte keine absoluten Pfade, privaten Inhalte oder
    Hostidentität enthalten;
11. Netzwerk-, Fachsystem-, Persistenz- und Bestandswirkungen null bleiben;
12. ein Validator den eingecheckten Ergebnisvertrag ohne erneute Ausführung
    des Experiments vollständig nachrechnet.

Die beobachtete Produktqualität darf `qualified`, `qualified_with_findings`
oder `not_qualified` lauten. Gefundene Fehlklassifikationen lassen den
methodisch korrekten Versuch nicht verschwinden. Sie werden als Befund und
Eingang eines späteren Gates dokumentiert.

## Fail- und Stoppkriterien

Der Versuch ist nicht vertrauenswürdig und wird nicht als ausgeführt
dargestellt, wenn:

- Oracles nach Kenntnis der Ergebnisse angepasst werden;
- Experimentcode eigene Identitätsentscheidungen anstelle des Produktdienstes
  liefert;
- ein Fall ungebunden, nicht reproduzierbar oder nur manuell interpretierbar
  bleibt;
- Pfade, temporäre Eingänge oder andere nicht vereinbarte Daten im Ergebnis
  erscheinen;
- ein kritischer False Positive nicht einzeln sichtbar ist;
- die zweite Wiederholung semantisch abweicht;
- Produktcode, TEST-0001 oder ein produktiver Bestand verändert wird.

Nach der Ergebnisintegration endet die autonome Arbeit an einem neuen Gate.
EXP-0009 autorisiert keine Korrektur der gefundenen Produktlücken und keine
weitere Produktwave.

## Ausführungsergebnis

Der getrennte synthetische Lauf auf Preimage
`2ef2de0395e485283f3be4ca339ab5fed8657fee` hat alle 12 methodischen
Kriterien erfüllt. Genau 15 Paare wurden vollständig und drei erwartbar
`not_assessed` bewertet. Zwei unabhängige Materialisierungen lieferten
denselben semantischen Digest; Eingänge, Pfadfreiheit, Wirkungsfreiheit und
Cleanup blieben vollständig gebunden.

Die breitere Produktqualität ist `not_qualified`. Im adversariellen Fall
`metadata-collision-work-conflict` überwogen gleicher Titel, Creator,
Identifier und Sprache die gleichzeitig sichtbare negative Evidenz
`metadata.work_references_conflict`. Der Dienst lieferte deshalb
`candidate_same` zunächst auf Ausgaben- und anschließend auf Werkebene,
obwohl das vorab gebundene Oracle nur `different` oder `abstain` erlaubt.
Dies sind zwei einzeln sichtbare kritische False-Same-Befunde. Byte-, Paket-
und Repräsentationsebene hatten keine False Positives oder False Negatives.

Der vollständige Ergebnis-, Profil-, Manifest- und Methodennachweis steht
unter [experiments/ebook/exp-0009](../../experiments/ebook/exp-0009/README.md).
Er ist keine Aussage über reale Häufigkeiten und autorisiert keine
Produktkorrektur.

## Nachweise

Vollständiger lokaler Lauf der getrennten Ausführungswave:

    python tools/experiments/run_exp_0009.py \
      --temp-root C:\rep\tmp\SammlungsLotse\exp-0009

CI-geeignete Ergebnisprüfung ohne neue Materialisierung:

    python tools/experiments/run_exp_0009.py --validate-result

Fokussierte Tests:

    python -m unittest tests.experiments.test_exp_0009

Die Befehle sind im gebundenen Ausführungsstand vorhanden. Der vollständige
Lauf und die anschließende Ergebnisvalidierung wurden am 2026-08-28
ausschließlich mit synthetischen Daten ausgeführt.
