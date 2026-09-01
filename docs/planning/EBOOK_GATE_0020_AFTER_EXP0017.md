# GATE-0020: EXP-0017-Ergebnis und sichere Produktfortsetzung bewerten

Status: DONE — OPTION B / WI-0014 AUSGEWÄHLT

Stand: 2026-09-01

Artifact: GATE-0020

## Zweck

Dieses Gate bewertet den methodisch bestandenen EXP-0017-Befund. Es trennt
den Nachweis für den exakt gebundenen WI-0005-Provider- und Executorstand von
jeder Produktentscheidung. Ohne ausdrückliche Auswahl werden weder ein
weiteres Experiment noch ein Produktarbeitsgegenstand registriert oder
begonnen.

## Auswahl

Der Nutzer hat am 2026-09-01 ausdrücklich Option B ausgewählt. GATE-0020 ist
damit abgeschlossen und WI-0014 als angenommener, getrennt gebundener
Produktarbeitsgegenstand registriert. A, C, K und P bleiben nicht ausgewählt.
Die Auswahl autorisiert den WI-0014-Vertrag und nach dessen Merge eine
getrennte Implementierungswave. Sie autorisiert weder eine Lockerung des
WI-0004-Review-Gates noch erneute private Analyse.

## Verifizierte Evidenz

- Das maßgebliche saubere Ausführungspreimage ist Commit
  `53a1e2dbefd03c7d770e949490ea1ec7783bfe98`; der vollständige lokale
  Repositorytest und beide erforderlichen GitHub-Checks bestanden vor dem
  Lauf auf exakt diesem Commit.
- Genau zwölf ausschließlich im Speicher materialisierte synthetische EPUBs
  aus den drei Gruppen S3-Navigation, Ressourcen beziehungsweise Aktivität
  und mehrdeutig beziehungsweise täuschend wurden je zweimal verarbeitet.
  Alle 24 Aufrufe erreichten den unveränderten `EpubCheckProvider` und
  `PodmanExecutor`.
- Alle Kontext-, Schemagruppen- und S3-Orakel stimmten. Beide Wiederholungen
  waren nach Ausschluss technischer Rohbericht-Größenwerte semantisch
  identisch; alle Providerbefunde und Codes blieben getrennt aggregiert.
- Die Kontrollverbindung der IPv4-Loopback-Kanarie wurde genau einmal
  erkannt. Die 24 Deep-Path-Aufrufe erzeugten zusammen null
  Kanarientreffer. Der Executor bestätigte vor Prozessstart unter anderem
  `network=none`, read-only Root und Input, begrenzte Ressourcen und
  fehlende Privilegien.
- Timeout und Outputgrenze endeten fail-closed. Alle Tasks und Container
  wurden entfernt; Eingänge, Produktcode, WI-0004-Gate, Fachsystem und
  Sammlung blieben unverändert. Private Eingänge, externes Netzwerk,
  Persistenz und Writes fehlten.
- Alle 18 methodischen Akzeptanzkriterien bestanden. Das 4.429-Byte-Ergebnis
  ist mit SHA-256
  `ffb748bc7429b4362392c1464b6268bf404df74625420a8498d405558c88db61`
  an das historische Preimage gebunden.

## Transparenz zum ersten Lauf

Ein erster vollständiger Lauf auf Commit
`2bb29e0ac2b4dd45ac452364ece0f9addbb1572a` blieb korrekt
`inconclusive`: Der Harness hatte zwei Byte laufzeitabhängiges
Rohbericht-Größenrauschen irrtümlich in die semantische
Wiederholungsidentität einbezogen. Der Bericht blieb unverändert außerhalb
von Git. Nach einer eng begrenzten, getrennt getesteten Korrektur wurde nicht
derselbe Preimage-Lauf wiederholt, sondern ein neuer sauberer und erneut
vollständig grüner Commit genau einmal ausgeführt. Die Größenaggregate
bleiben im maßgeblichen Ergebnis sichtbar; nur ihre fachlich falsche
Gleichheitswirkung entfiel.

## Interpretation

EXP-0017 belegt für die gebundene synthetische Matrix und den exakten
Runtime-Stand, dass der tiefe EPUBCheck-Pfad netzwerklos, begrenzt,
fail-closed und vollständig bereinigt lief. Er belegt außerdem, dass die
EXP-0016-Klassifikation neben den davon unabhängigen Providerbefunden stabil
blieb.

Der Befund belegt keine allgemeine Sicherheit von EPUB-Lesesystemen, kein
Vertrauen in ein Linkziel, keine Nutzerabsicht, keine vollständige reale
EPUB-Abdeckung und keine Zulässigkeit automatischer Navigation. EPUBCheck-
Konformitätsbefunde sind keine Sicherheitsklassifikation. Das bestehende
WI-0004-Review-Gate bleibt deshalb unverändert.

## Optionen

### A — Weitere synthetische Lesesystem- und Aktivierungsevidenz qualifizieren

Ein neues, separat zu registrierendes Experiment könnte eine kleine
vorab gebundene Auswahl weiterer öffentlich reproduzierbarer Engines oder
Lesesystemoberflächen ausschließlich mit synthetischen Fällen untersuchen.
Es müsste Netzwerk-, Prozess-, UI-, Temp-, Output- und Cleanupgrenzen je
Engine separat binden und dürfte keine Produktregel auswählen.

- Vorteil: erweitert die Evidenz über EPUBCheck hinaus;
- Risiko: höherer Tool- und Plattformaufwand, ohne Zielvertrauen oder
  vollständige Lesesystemsicherheit beweisen zu können;
- Einordnung: nur sinnvoll, wenn eine spätere Reviewlockerung weiterhin
  ernsthaft erwogen wird.

### B — Review-beibehaltende Kontexterklärung als Arbeitsgegenstand auswählen

**Ausgewählt als WI-0014.**

Ein neuer, separat anzunehmender Produktarbeitsgegenstand könnte `review`
unverändert lassen und ausschließlich eine grobe, pfadfreie Erklärung der
bereits qualifizierten Kontextklasse ergänzen. Vor Implementierung müssten
öffentlicher Ausgabevertrag, unbekannte Klassen, V1-Kompatibilität,
Datenschutz, synthetische Produktqualifikation und Rückfallverhalten exakt
gebunden werden.

- Vorteil: liefert Nutzwert und Erklärbarkeit, ohne das Sicherheitsgate zu
  öffnen;
- Risiko: führt neue öffentliche Produktsemantik ein und senkt den
  manuellen Reviewbedarf nicht automatisch.

### C — Strikte Navigationsausnahme als Produktarbeitsgegenstand auswählen

Ein neuer, separat anzunehmender Produktarbeitsgegenstand könnte die in
EXP-0016 untersuchte strikte S3-Navigationsprojektion als eng begrenzte
Ausnahme vor dem tiefen read-only Pfad umsetzen. Er müsste unbekannte und
mehrdeutige Kontexte weiterhin fail-closed behandeln und eine vollständige
adversarielle Produktqualifikation besitzen.

- Vorteil: könnte konservative Reviews in genau qualifizierten Fällen
  reduzieren;
- Risiko: eine Fehlklassifikation könnte eine aktive oder automatisch
  verarbeitete Referenz fälschlich freigeben; EXP-0017 allein schließt
  dieses Produktrisiko nicht.

### K — Evidenz konservieren und bestehendes Review beibehalten

EXP-0017 bleibt historisch prüfbar. Es wird kein Folgeartefakt registriert;
der aktuelle konservative WI-0004-Weg und die bisherigen Produktverträge
bleiben unverändert.

### P — E-Book-Identitätszweig pausieren

Der Zweig wird ausdrücklich pausiert. Andere SammlungsLotse-Themen bleiben
unberührt.

## Empfehlung

B ist die kleinste entwickelbare Produktfortsetzung mit begrenzter Wirkung:
Sie nutzt die vorhandene Kontextklassifikation zur Erklärung, ohne `review`
zu lockern. K ist die sichere Endposition, wenn diese zusätzliche
Erklärbarkeit keinen ausreichenden Wert bietet. A sollte nur gewählt werden,
wenn tatsächlich noch auf eine spätere Reviewdifferenzierung hingearbeitet
wird; sonst würde es weitere Methodenevidenz ohne unmittelbaren Produktnutzen
erzeugen. C bleibt die risikoreichste Option und ist durch den methodischen
EXP-0017-Pass nicht automatisch gerechtfertigt.

Die Empfehlung wurde durch die ausdrückliche Auswahl B angenommen. A, C, K
und P bleiben nicht ausgewählt. Die Implementierung ist ausschließlich im
gebundenen WI-0014-Vertrag zulässig.

## Harte Grenzen

- methodischer `pass` ist keine Produktfreigabe;
- keine automatische Lockerung oder Umgehung des WI-0004-Review-Gates;
- keine erneute private Analyse ohne neuen engen Vertrag und ausdrückliche
  Bestätigung;
- keine Aufbewahrung privater Werte, Locators, Pfade, Hashwerte oder
  Rohoutputs;
- kein Produktcode ohne getrennt registrierten und angenommenen
  Arbeitsgegenstand;
- keine Bestandswirkung oder Änderung im führenden Fachsystem.

## Gate-Stand

- EXP-0017 ist `done`; Methode und Ergebnis sind historisch gebunden.
- GATE-0020 ist `done`; Option B ist ausgewählt.
- WI-0014 ist inzwischen `done` und bestand 16/16 commitgebundene
  Produktkriterien; die damaligen Optionen A, C, K und P bleiben nicht
  ausgewählt.
- GATE-0021 ist als getrenntes Ergebnisgate `proposed`; dort ist keine Option
  ausgewählt.
- Das WI-0004-Review-Gate bleibt unverändert.
