# EXP-0013: Private WI-0011-Nichtabschlussgründe produktcodefrei diagnostizieren

Status: DONE — EXECUTED, 16/16 METHOD CRITERIA PASSED; RESULT NOT_QUALIFIED

Stand: 2026-08-31

Artifact: EXP-0013

## Auswahl und Zweck

Der Nutzer hat in GATE-0015 am 2026-08-31 ausdrücklich Option A ausgewählt.
EXP-0013 diagnostiziert ausschließlich, warum im getrennten privaten
EXP-0012-Praxissmoke keiner der drei nachgelagerten WI-0011-Vergleiche den
Status `completed` erreichte.

Die Auswahl autorisiert diesen Experimentvertrag und seine getrennte
Ausführung nach Merge und Post-Merge-Prüfung. Sie autorisiert keine
Produktkorrektur, keine Suchstrategie und keinen Produktcode. Das Ergebnis
öffnet ein neues getrenntes Ergebnisgate.

## Gebundene Ausgangslage

- EXP-0012 bestand synthetisch 16/16 Methodenkriterien. Sein privater Smoke
  materialisierte drei EPUB-Kopien, führte vier Suchläufe aus und endete bei
  0/3 abgeschlossenen WI-0011-Vergleichen mit vollständigem Cleanup.
- Der private EXP-0012-Summary bewahrte absichtlich nur Zählwerte. Der
  vorhandene WI-0011-JSON-Vertrag liefert bei `not_assessed` bereits
  pfadfreie `handoff_reason_codes`; EXP-0012 übernahm sie nicht in seine
  Aggregation.
- WI-0011 bleibt unverändert auf dem Profil
  `wi-0011-calibre-identity-handoff/v1` und verwendet standardmäßig den
  bytekompatiblen V1-Identitätsbericht.
- WI-0007 bindet Calibre 9.13.0, das exakte Linux/amd64-Image
  `sha256:9aa46b7581aa647bb9000caff53b227694fc8ea28c0271eb83666f916b21c0a5`
  und eine task-private Copy-on-read-Bibliothek ohne Netzwerk.
- Private Pfade, Hashes, Werte und Rohoutputs des ersten Smoke wurden
  absichtlich nicht aufbewahrt. Die drei Dateien müssen deshalb beim Lauf
  erneut explizit und als derselbe Eingangssatz bestätigt werden.

EXP-0012 und sein historischer Nachweis werden nicht verändert.

## Private Eingangsgrenze

Der auswertbare Hauptlauf akzeptiert genau drei wiederholte
`--private-epub`-Argumente und die ausdrückliche Bestätigung, dass es dieselben
drei Eingänge wie im EXP-0012-Praxissmoke sind.

Für jeden Eingang gilt:

- reguläre vorhandene Datei mit Endung `.epub`;
- kein Symlink, Reparse Point oder anderer indirekter Locator;
- größer als null und höchstens 4 MiB;
- alle drei Dateien zusammen höchstens 12 MiB;
- ausschließlich read-only geöffnet;
- keine Verzeichnis-, Glob-, Index- oder rekursive Suche.

Weniger oder mehr als drei Eingänge, doppelte Locators, ein Verzeichnis oder
eine verletzte Dateigrenze brechen vor jeder Materialisierung fail-closed ab.
Fehlermeldungen geben keinen Locator aus.

Die SHA-256-Werte werden nur im Prozessspeicher vor und nach dem Lauf zur
Unverändertheitsprüfung verwendet. Sie erscheinen weder in stdout oder
stderr noch in eingecheckter oder lokaler Ergebnisevidenz.

## Diagnoseablauf

Nach bestandener Eingangskontrolle gilt genau diese Reihenfolge:

1. Jede Datei wird unter einem positionsgebundenen neutralen Namen in einen
   neuen task-privaten Tempbereich kopiert und bytegleich geprüft.
2. Aus ausschließlich diesen drei Kopien wird über die unterstützte
   Calibre-CLI genau eine task-private Bibliothek materialisiert.
3. Die im EXP-0012-Smoke verwendeten feldgebundenen V1- und V2-Suchen werden
   nur dort ausgeführt, wo ihre benötigten Felder vorhanden sind. Der eigene
   materialisierte Datensatz muss weiterhin gefunden werden; private Querys
   und Treffer-IDs werden nicht ausgegeben.
4. Jeder Eingang wird genau einmal gegen seinen eigenen materialisierten
   Calibre-Datensatz über den unveränderten Befehl
   `tools/run_ebook_calibre_identity.py --json` bewertet.
5. Erst nachdem alle drei Vergleiche beendet und Quelle, Taskbereich sowie
   Containerzustand nachgeprüft wurden, wird eine gemeinsame Aggregation
   erzeugt.

Der Lauf verwendet keine Oracles für eine Produktentscheidung. Er untersucht
nur den Eintrittspunkt des vorhandenen `completed`- beziehungsweise
`not_assessed`-Vertrags.

## Aggregationsvertrag

Die einzige zulässige private Ausgabe besitzt folgende gruppenbezogenen
Felder:

- Schema und Experimentreferenz;
- feste Eingangsanzahl `3`;
- Anzahl der Such- und WI-0011-Läufe;
- `assessment_counts` für `completed` und `not_assessed`;
- alphabetisch sortierte `reason_code_counts`;
- feste `entry_stage_counts`;
- boolesche Nachweise für Quellunverändertheit, Pfadfreiheit und Cleanup;
- Gesamtstatus `pass`, `not_qualified` oder `inconclusive`.

Es gibt keine Einzelausgabe und keine stabile Eingangskennung. Insbesondere
fehlen Position, Calibre-ID, Titel, Autor, Identifier, Sprache, Format,
Entscheidungsstufen, Pfad, Hash, Query, Rohbericht und Zeitstempel.

Die Eintrittsstufen sind fest gebunden:

- `completed`: WI-0011 erreichte `completed`;
- `ingress_preflight`: Reason-Code `ingress.preflight_gate_not_open`;
- `record_handoff`: bekannter Provider-, Executor-, Workspace-, Library-
  oder Konfigurationsfehler vor der Identitätsbewertung;
- `identity_analysis`: Reason-Code `identity.not_assessed`;
- `unclassified`: jeder neue oder nicht eindeutig zuordenbare Reason-Code.

Reason-Codes werden nicht umbenannt oder zusammengezogen. Ein unbekannter
Code bleibt als pfadfreies Literal gezählt, setzt `unclassified` und macht
den Lauf `inconclusive`. Eine Teilaggregation wird bei Abbruch oder
unvollständigem Cleanup nicht ausgegeben.

## Synthetische Kontrollen

Vor dem privaten Lauf bindet das Ausführungspreimage ausschließlich
synthetische Kontrollen:

1. drei erfolgreiche tatsächliche WI-0011-Vergleiche über TEST-0001-Material;
2. eine vorab gebundene pfadfreie Aggregationsmatrix für `completed`,
   `ingress_preflight`, `record_handoff`, `identity_analysis` und einen
   unbekannten Code;
3. Negativkontrollen für zwei oder vier Eingänge, doppelte Eingänge,
   Verzeichnisse, Links, Größenüberschreitung, Teilabbruch, private Felder und
   unvollständiges Cleanup;
4. zwei semantisch identische Aggregationswiederholungen.

Die synthetischen Kontrollen belegen Methode und Datenschutzgrenzen. Sie
ersetzen den ausdrücklich ausgewählten privaten Diagnoselauf nicht.

## Harte Grenzen

- genau drei erneut explizit bestätigte private EPUBs im Hauptlauf;
- genau eine task-private Calibre-Bibliothek;
- genau ein WI-0011-Vergleich je Eingang;
- unveränderte WI-0007- und WI-0011-Profile, Image-, Prozess-, Zeit-, CPU-,
  RAM-, PID-, Umgebungs- und Outputgrenzen;
- V1 bleibt der WI-0011-Standard; kein V2-Default und keine V1-Deprecation;
- kein Netzwerk und keine direkte `metadata.db`-Nutzung;
- keine Persistenz und keine Aufbewahrung privater Arbeitskopien;
- keine privaten Metadaten, Locators, Hashes, Querys, Treffer-IDs oder
  Rohoutputs;
- keine Änderung unter `src/sammlungslotse/`;
- keine neue öffentliche CLI-, API-, UI-, Agent-, Such-, Routing- oder
  Writerfläche;
- keine Bestandsänderung im führenden Fachsystem.

## Methodische Akzeptanzkriterien

EXP-0013 ist methodisch nur bestanden, wenn alle folgenden 16 Kriterien
erfüllt sind:

1. Git-Preimage, EXP-0012, WI-0007- und WI-0011-Profile sowie die exakte
   Calibre-Image-ID sind gebunden;
2. der Hauptlauf akzeptiert ausschließlich genau drei explizite
   `--private-epub`-Argumente und keine Verzeichnisse;
3. alle drei Eingänge wurden vom Nutzer als derselbe EXP-0012-Eingangssatz
   bestätigt;
4. Dateityp, Link-, Reparse-, Einzel- und Summengrenzen werden vor dem Kopieren
   geprüft;
5. ausschließlich positionsgebundene task-private Kopien werden verarbeitet;
6. die Bibliothek entsteht nur aus diesen Kopien über unterstützte
   Calibre-Befehle;
7. jeder Eingang durchläuft genau einmal den unveränderten WI-0011-V1-Weg;
8. Reason-Codes und Eintrittsstufen werden ohne per-Datei-Zuordnung gezählt;
9. unbekannte Codes bleiben sichtbar und führen zu `inconclusive`;
10. die Ausgabe enthält nur den gebundenen Gruppenvertrag;
11. private Werte, Pfade, Hashes, Querys, IDs und Rohoutputs fehlen;
12. die synthetischen Positiv-, Aggregations- und Negativkontrollen bestehen;
13. beide Aggregationswiederholungen sind semantisch identisch;
14. alle drei Quellen bleiben bytegleich unverändert;
15. Netzwerk, direkte Datenbanknutzung, Persistenz, Produktcode und
    Bestandswirkungen fehlen;
16. Taskmaterial, Bibliothekskopie und Container sind vollständig bereinigt.

Ein methodischer `pass` ist keine Produktfreigabe. Der fachliche Befund darf
`not_qualified` oder `inconclusive` sein und wird nicht in einen Erfolg
umgedeutet.

## Ergebnis

Der Hauptlauf wurde am 2026-09-01 gegen das saubere Preimage
`6d32f5dad32481ef9ec163e742acb1ae77aaf226` ausgeführt. Der Nutzer bestätigte
ausdrücklich dieselben drei EXP-0012-Eingänge und für den zunächst als PDF
genannten ersten Locator die exakt gleichnamige EPUB-Alternative. Es fand
keine Verzeichnis-, Glob-, Index- oder rekursive Suche statt.

EXP-0013 bestand alle 16 methodischen Kriterien:

- drei synthetische tatsächliche WI-0011-Vergleiche, neun Negativkontrollen
  und beide Aggregationswiederholungen bestanden;
- genau drei private EPUBs, eine task-private Bibliothek, vier Suchläufe und
  genau drei WI-0011-Läufe wurden verarbeitet;
- `assessment_counts` lautet `completed=0`, `not_assessed=3`;
- `reason_code_counts` enthält ausschließlich
  `ingress.preflight_gate_not_open=3`;
- `entry_stage_counts` enthält ausschließlich `ingress_preflight=3`; es gab
  keine unbekannte beziehungsweise `unclassified` Stufe;
- Quellen, Tempbereich und Container blieben unverändert beziehungsweise
  wurden vollständig bereinigt;
- das Ergebnis ist pfadfrei und enthält keine privaten Einzelwerte,
  Metadaten, Locators, Hashes, Querys, IDs oder Rohoutputs.

Der Ergebnisstatus ist fachlich `not_qualified`, weil kein WI-0011-Vergleich
`completed` erreichte. Der Befund lokalisiert alle drei Nichtabschlüsse vor
dem Record-Handoff in der Ingress-Vorprüfung; er erklärt noch nicht den
konkreten Intake-Grund und autorisiert keine Reparatur. GATE-0016 bewertet die
Fortsetzung getrennt.

## Ausführungsfolge

1. Die Auswahl- und Vertragswave wurde validiert, gemergt und auf
   `origin/main` post-merge geprüft.
2. Profil, Runner, synthetische Kontrollen und Tests wurden ohne Produktcode
   implementiert und als Preimage `6d32f5d` committed.
3. Gegen dieses Commit wurde der private Eingangssatz erneut explizit
   bestätigt und lokal ausgeführt.
4. Der historische Validator bindet ausschließlich die zulässige Aggregation
   an das Preimage; private Arbeits- oder Rohdaten bleiben außerhalb von Git.
5. GATE-0016 bewertet das Ergebnis getrennt; EXP-0013 wählt keine
   Produktfortsetzung.

## Nicht-Ziele

- keine Reparatur von WI-0011 oder der Identitätsheuristik;
- keine neue Kandidatensuche oder Bewertung von V1, V2 oder V3;
- keine Aussage über Inhalt, Qualität oder bibliografische Identität der drei
  privaten EPUBs;
- keine Erweiterung auf weitere Dateien oder Bibliotheken;
- keine dauerhafte private Diagnosedatenbank;
- keine Produkt-, Architektur-, Provider-, UI- oder Writerentscheidung.
