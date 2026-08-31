# GATE-0014: Nächsten read-only Nutzwert nach WI-0013 bewerten

Status: PROPOSED — AUSWAHL OFFEN

Stand: 2026-08-31

Artifact: GATE-0014

## Zweck

Der Nutzer hat am 2026-08-31 mit „Dann los“ die nächste ausdrücklich
getrennte Entscheidungswave angestoßen. Diese Anweisung autorisiert die
ergebnisoffene Bewertung, aber noch keine der hier verglichenen
Produkt-, Experiment- oder Maintenance-Fortsetzungen.

GATE-0014 bestimmt den kleinsten sinnvollen nächsten read-only Nutzwert nach
dem stabilisierten Identitätsvertrag. Es hält fachlich unterschiedliche
Fragen getrennt und registriert ohne weitere ausdrückliche Nutzerauswahl
weder Experiment noch Arbeitsgegenstand.

## Verifizierte Ausgangslage

GATE-0013 hält den aktuellen Vertrag stabil:

- V1 bleibt bytekompatibler Standard;
- V2 bleibt über `--json --report-version v2` explizites Opt-in;
- WI-0013 ist 29/29 synthetisch qualifiziert;
- der abhängige WI-0011-Vergleich ist erneut 23/23 qualifiziert;
- null kritische False Same und zwei sichtbare
  `candidate_related`-Werkabweichungen bleiben belegt;
- keine Publikationsstufe, Deprecation, Migration oder weitere Produktwave
  ist angenommen.

Der derzeit engste Calibre-Identitätsablauf benötigt weiterhin genau eine
vom Nutzer vorab angegebene externe Calibre-ID aus genau einer expliziten
Bibliothek. Er bewertet keine Suchvollständigkeit, erzeugt keine
Kandidatenmenge und untersucht keine weiteren Bibliotheken. Das ist die
größte noch offene Bedienlücke innerhalb des bereits qualifizierten
read-only Identitätsablaufs.

## Entscheidungskriterien

Die Optionen werden ohne gewichteten Gesamtscore bewertet nach:

1. direktem Nutzen in einem konkreten Nutzerablauf;
2. vorhandenen fachlichen und synthetischen Voraussetzungen;
3. Schutz vor falscher Sicherheit und hochpreisigen Fehlentscheidungen;
4. neuer Kopplung an Provider, Modell, Schema, Laufzeit und Infrastruktur;
5. lokaler, synthetischer und kostenarmer Prüfbarkeit;
6. Reversibilität vor einer allgemeinen Produktarchitektur;
7. klarer Trennung von Beobachtung, Vorschlag und Bestandswirkung.

## Mögliche Fortsetzungen

### A — Begrenzte Kandidatensuche produktcodefrei evidenzieren

Ein getrenntes Experiment würde für genau ein explizites Eingangs-EPUB und
genau eine explizite synthetische Calibre-Bibliothek vergleichen, welche
unterstützten read-only Such- und Projektionswege eine kleine, hart begrenzte
und erklärbare Kandidatenmenge liefern. Erst danach würde jeder Kandidat
einzeln über den bestehenden WI-0011-Vertrag bewertet.

Der Experimentvertrag müsste Suchaufgaben, vorab gebundene Recall-Oracles,
Feld- und Rollenprojektion, Kandidaten-, Zeit- und Outputgrenzen,
Determinismus, Quellenunverändertheit, sichtbaren Suchumfang und Enthaltung
festlegen. Er dürfte weder direkte `metadata.db`-Nutzung noch Produktcode,
Persistenz oder automatische Dublettenbehauptungen einführen.

- unmittelbarer Nutzwert: hoch, weil keine externe Calibre-ID mehr vorab
  bekannt sein müsste;
- Evidenzreife: mittel; Identitätsbewertung und Rollenmodell sind vorhanden,
  der Such- und Recallvertrag fehlt noch;
- neue Kopplung: niedrig bis mittel in einem produktcodefreien Experiment;
- Reversibilität: sehr hoch;
- Hauptrisiko: eine begrenzte Suche wird als vollständige Bestandsprüfung
  missverstanden;
- Einordnung: **Empfehlung**.

### B — Read-only Bestandsqualitätsbefunde definieren

Ein Mess- und Befundvertrag würde auf der bestehenden WI-0007-Projektion
leere, widersprüchliche oder auffällige Titel-, Autoren-, Sprach- und
Formatwerte als getrennte Beobachtungen für manuelle Prüfung untersuchen.

- unmittelbarer Nutzwert: mittel bis hoch für vorhandene Bestände;
- Evidenzreife: niedrig bis mittel, weil feldbezogene Nutzerprioritäten und
  Oracles fehlen;
- neue Kopplung: niedrig bis mittel;
- Hauptrisiko: ungewöhnlich oder leer wird fälschlich als falsch bewertet;
- Einordnung: gute unabhängige Alternative, aber weniger anschlussnah an den
  gerade qualifizierten Identitätsablauf.

### C — Bibliografische Konflikte read-only erklären

Die rollenbewussten EPUB-Metadaten aus V2 und die minimale
Calibre-Projektion würden als getrennte Beobachtungsquellen verglichen.
Feldweise Kandidaten, Gegenbelege, Provenienz und Enthaltung blieben
sichtbar; keine Quelle würde automatisch kanonisch.

- unmittelbarer Nutzwert: hoch bei tatsächlichen Metadatenkonflikten;
- Evidenzreife: mittel für EPUB-Rollen, niedriger für weitere Calibre-Felder;
- neue Kopplung: mittel durch Feld-, Rollen- und Gegenstandsmodell;
- Hauptrisiko: Normalisierung oder Fachsystemwert wird zur unbelegten
  bibliografischen Wahrheit;
- Einordnung: sinnvoll nach einem eigenen Konflikt- und Fehlerkostenvertrag.

### D — Mehrbibliotheks-Routing experimentieren

Mehrere synthetische Calibre-Bibliotheken könnten als getrennte Zielbestände
mit eindeutigen, mehrdeutigen und nicht passenden Routingfällen untersucht
werden.

- unmittelbarer Nutzwert: potenziell hoch für Szenario S6;
- Evidenzreife: niedrig bis mittel;
- neue Kopplung: hoch durch Bibliotheksidentität, Zielregeln, Konflikte und
  Klassifikation;
- Hauptrisiko: Bestandsfundstelle, Routingvorschlag und Importfreigabe werden
  vermischt;
- Einordnung: eigenständiges späteres Experiment, nicht mit Kandidatensuche
  oder Writer bündeln.

### E — V2-Verbraucher- und Migrationsevidenz erheben

Eine produktcodefreie Bestandsaufnahme könnte konkrete V1-Verbraucher,
Kompatibilitätsanforderungen und messbare Migrationslast binden, ohne den
Default zu ändern.

- unmittelbarer Nutzwert: gering, solange kein konkreter Migrationsbedarf
  vorliegt;
- Evidenzreife: niedrig, weil derzeit kein gebundener Verbraucherbedarf
  dokumentiert ist;
- neue Kopplung: niedrig für die Bestandsaufnahme, hoch für jede spätere
  Umstellung;
- Einordnung: erst bei einem tatsächlichen Verbrauchertrigger priorisieren.

### F — Nur Maintenance und Requalifikation fortsetzen

Keine neue Produktfläche wird geöffnet. Profile, Abhängigkeiten,
Nachweise, Dokumentation und Sicherheitsbefunde werden bei konkretem Drift
erneut geprüft.

- unmittelbarer Nutzwert: Erhalt der Verlässlichkeit;
- neue Kopplung: keine;
- Reversibilität: vollständig;
- Einordnung: valide Betriebsoption ohne neue Nutzerfunktion.

### K — Pausieren

Keine neue Wave. Der bestehende V1-/V2-Vertrag und alle historischen
Nachweise bleiben verfügbar.

## Vergleich

| Option | direkter Nutzwert | Evidenzreife | Kopplung | Reversibilität | nächster belastbarer Schritt |
|---|---:|---:|---:|---:|---|
| A — Kandidatensuche | hoch | mittel | niedrig–mittel | sehr hoch | produktcodefreies Experiment |
| B — Bestandsqualität | mittel–hoch | niedrig–mittel | niedrig–mittel | hoch | Befund- und Messvertrag |
| C — Metadatenkonflikte | hoch im Konfliktfall | mittel | mittel | hoch | Konflikt- und Fehlerkostenvertrag |
| D — Routing | potenziell hoch | niedrig–mittel | hoch | mittel | eigenständiges Routingexperiment |
| E — V2-Migrationsevidenz | derzeit gering | niedrig | zunächst niedrig | hoch | konkreten Verbrauchertrigger binden |
| F — Maintenance | erhaltend | hoch | keine | vollständig | nur bei Drift handeln |
| K — pausieren | keine neue Wirkung | ausreichend zum Stoppen | keine | vollständig | kein neuer Schritt |

## Empfehlung

Option A ist die kleinste Fortsetzung mit hohem direktem Nutzerwert. Die
vorherigen Waves haben die fünf Identitätsstufen, False-Same-Grenzen,
Identifier-Rollen, Collection-Provenienz und den Einzelrecord-Handoff bereits
synthetisch gebunden. Damit ist jetzt nicht eine weitere Identitätsregel,
sondern die sichere Erzeugung einer begrenzten Kandidatenmenge der nächste
offene Engpass.

Die Empfehlung nimmt A nicht an. Erst eine ausdrückliche Nutzerauswahl darf
GATE-0014 schließen und ein getrennt registriertes Experiment autorisieren.
B bis F und K bleiben echte Alternativen.

## Kanten, die nicht überschritten werden

- Kandidatensuche ist keine vollständige Dublettenprüfung.
- Ein Suchtreffer ist keine bestätigte Identität, kein Ziel und keine
  Bestandsaktion.
- Keine Option autorisiert direkte `metadata.db`-Nutzung.
- Mehrere Bibliotheken werden nicht als Schleife über einen
  Einzelbibliotheksvertrag eingeführt.
- Leere oder ungewöhnliche Metadaten sind nicht automatisch Fehler.
- Ein Score ersetzt keine einzelnen Befunde, Gegenbelege oder Enthaltung.
- Keine reale oder private Bibliothek und kein Sammlungsinventar gelangt in
  Git oder einen externen Dienst.
- V1 bleibt Standard und V2 bleibt Opt-in.
- Persistenz, Routingprodukt, Browser, REST, Agents und Writes bleiben ohne
  getrennte Entscheidung außerhalb.
- Fachsysteme bleiben führend; SammlungsLotse wirkt unterstützend und
  read-only.

## Gate-Stand

- GATE-0014 bleibt `proposed`.
- A ist empfohlen, aber nicht ausgewählt.
- Kein Experiment und kein Produktarbeitsgegenstand ist registriert.
- Eine Antwort mit A, B, C, D, E, F oder K ist die nächste erforderliche
  ausdrückliche Entscheidung.
