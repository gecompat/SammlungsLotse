# GATE-0002: Fortsetzung nach dem Eingangstriage-Prototyp

Status: AUSGEWERTET — EINE REVERSIBLE ÜBERGABEEVIDENZ-WAVE ANGENOMMEN

Stand: 2026-08-27

Artifact: GATE-0002

## Entscheidung

Nach WI-0004 wird weder eine allgemeine Kern-/CLI-Härtungswave noch ein
Produktadapter begonnen. Stattdessen wird genau eine reversible
Evidenz-Wave angenommen: EXP-0007 vergleicht, wie der unveränderliche
WI-0004-Snapshot an einen tiefen read-only Werkzeugprozess übergeben werden
kann.

EXP-0007 darf nur die Übergabenaht qualifizieren. Ein konkreter
Produktadapter bleibt bis zur getrennten Auswertung durch GATE-0003
unautorisiert. Scheitern alle Übergabeformen an Snapshot-Bindung,
Datenschutz-, Ressourcen- oder Cleanup-Grenzen, wird nicht ersatzweise die
am leichtesten implementierbare Variante gewählt.

## Tatsächliche Ausgangslage

Der Vergleich verwendet den auf `origin/main` belegten Stand und keine
Planannahme als Implementierungsnachweis:

- WI-0004 erzeugt aus genau einer lokalen Datei einen begrenzten
  unveränderlichen In-Memory-Snapshot;
- ein stabiler synthetischer EPUB-Eingang endet sichtbar mit
  `continue_deep_read_only` und `deep_read_only_allowed=true`;
- der Bericht trägt SHA-256 und Größe, aber keinen lokalen Pfad, Dateinamen,
  Inhalt oder Archiveintragsnamen;
- Produktcode besitzt keine Netzwerk-, Subprozess-, Persistenz-,
  Extraktions- oder Schreibfähigkeit;
- 25 fokussierte Produkttests und die sichtbare CLI-Abnahme sind erfolgreich;
- EXP-0003 belegt eine verlustfreie Werkzeug-Evidenzprojektion, qualifiziert
  aber insbesondere Ace nicht für den Produktbetrieb;
- EXP-0005 belegt eine begrenzte netzwerklose EPUBCheck-Ausführung unter
  Podman, jedoch nur als wegwerfbares Experimentprofil mit einem
  read-only Dateimount;
- keines der bestehenden Ergebnisse verbindet den In-Memory-Snapshot aus
  WI-0004 mit einem tiefen Werkzeugprozess.

Die offene Naht ist deshalb nicht bloß ein fehlender Funktionsaufruf. Ein
tiefes Werkzeug benötigt Bytes, Stream oder Datei, während der aktuelle Kern
absichtlich nur den unveränderlichen Snapshot besitzt und keinen Provider,
Prozess oder temporären Dateipfad kennt.

## Bewertungsverfahren

Die Optionen werden nicht zu einer Punktzahl verdichtet. Entscheidend sind:

1. neuer überprüfbarer Nutzwert;
2. schwerster möglicher Restfehler und fail-closed Verhalten;
3. Kopplung an Betriebssystem, Dateisystem, Container oder Werkzeug;
4. Reversibilität und Kosten des Ausstiegs;
5. vorhandene Evidenz und Größe der nächsten unbeantworteten Frage;
6. Datenschutz-, Netzwerk-, Ressourcen- und Schreibwirkung;
7. Fähigkeit, eine spätere Medienlinie oder Oberfläche nicht
   vorzuentscheiden.

## Vergleich

| Option | Mögliche qualitätssteigernde Tätigkeiten | Sinnvoller unmittelbarer Gewinn | Schwerster Restfehler | Kopplung und Ausstieg | Entscheidung |
|---|---|---|---|---|---|
| A — Kern und CLI härten | ZIP-Zentralverzeichnis vorab begrenzen, generative Containerfälle, zusätzliche Abbruch- und Fehlerpfade, Exit-Code-Vertrag, Installation, Hilfe und Bedienbarkeit vertiefen | erhöht Robustheit und Bedienbarkeit des bereits sichtbaren Preflights | viel Härtung ohne neuen Qualitätsbefund; die tiefe Folgeaktion bleibt weiterhin leer | gering; alle Änderungen bleiben lokal im Prototyp | jetzt nicht als eigene Wave gewählt; konkrete entdeckte Defekte dürfen weiterhin fokussiert behoben werden |
| B — tiefen read-only Adapter planen | Snapshot-Übergabe, Prozess- und Outputgrenzen, Providerport, Rohbefundprojektion, Timeout und Cleanup qualifizieren | beantwortet die nächste vollständige Produktfrage hinter `continue_deep_read_only` | ein anderer oder veränderter Eingang erreicht das Werkzeug; Pfad oder Inhalt wird unnötig offengelegt; temporäre Daten bleiben zurück | mittel; ohne vorgeschaltetes Experiment droht Bindung an Dateipfad, Container oder erstes Werkzeug | als EXP-0007 ausgewählt, aber noch ohne Produktadapter |
| C — E-Book-Linie pausieren | Stand einfrieren, offene Fragen erhalten, andere Medienlinie vergleichen | keine weitere Kopplung oder Ausführungskosten | der erste Prototyp bleibt ohne tiefe Qualitätsaussage und liefert keinen neuen Nutzwert | sehr gering und vollständig reversibel | bleibt zulässiges Ergebnis von GATE-0003, wird vor der günstigen Übergabeklärung aber nicht vorgezogen |

## Warum keine allgemeine Härtungswave zuerst

WI-0004 erfüllt seinen engen synthetischen Vertrag auf Windows und in der
Linux-CI. Weitere Härtung ist möglich und teilweise sinnvoll, doch ihr Umfang
kann ohne nächste Verbrauchergrenze beliebig wachsen: Verpackung,
Realdateien, Oberfläche, Performance, Fuzzing und Betrieb wären jeweils
eigene Äste.

Die Übergabe an einen tiefen Prozess legt dagegen eine konkrete Grenze offen,
an der falsche frühe Entscheidungen schwer rücknehmbar wären. EXP-0007 prüft
diese Grenze, ohne eine allgemeine Runtime, Installation oder Oberfläche zu
fordern. Zeigt das Experiment eine Lücke im bestehenden Snapshot, wird nur
diese Lücke als Voraussetzung zurückgeführt; daraus folgt keine pauschale
Härtungsroadmap.

## Warum noch kein Produktadapter

Der bisherige Produktvertrag bestätigt nur, dass eine tiefe read-only Prüfung
erlaubt werden darf. Er definiert nicht:

- ob ein Provider Bytes, einen Stream oder einen Dateipfad erhält;
- wie der Provider beweist, dass er exakt den freigegebenen Snapshot prüft;
- ob und wo eine temporäre Repräsentation entstehen darf;
- wie deren Größe, Berechtigungen, Lebensdauer und Cleanup begrenzt werden;
- wie Timeout, Kindprozesse, stderr und Rohbericht begrenzt werden;
- welche Providerdetails im Adapter enden und welche Evidenz in den
  gemeinsamen Vertrag gelangt.

Eine direkte Implementierung würde mindestens eine dieser Fragen implizit
entscheiden und damit RISK-0001 verschärfen. Deshalb wird zuerst die
Übergabenaht empirisch verglichen.

## Angenommener nächster Erkenntnisschritt

EXP-0007 ist `accepted` und besitzt einen vollständigen Vertrag unter
[EBOOK_DEEP_READONLY_HANDOFF_EXPERIMENT.md](EBOOK_DEEP_READONLY_HANDOFF_EXPERIMENT.md).
Es vergleicht:

1. Byte-Stream an einen Prozess;
2. task-private, hashgebundene temporäre Materialisierung;
3. erneutes read-only Öffnen des ursprünglichen Locators mit
   Zustandsnachprüfung.

Die Varianten sind Untersuchungsobjekte. Keine ist vorab Produktstandard.

## Nicht autorisiert

GATE-0002 autorisiert nicht:

- Änderungen unter `src/sammlungslotse/`;
- einen EPUBCheck-, Ace-, Calibre- oder anderen Produktadapter;
- reale oder private Medien;
- Netzwerkzugriff während der Messläufe;
- dauerhafte Kopien, Cache, Datenbank, Queue oder Hintergrundprozess;
- Browser, REST, Agent, Plugin oder öffentliche API;
- Accessibility-Gesamtaussagen, Metadaten-, Identitäts- oder
  Routingentscheidungen;
- Transformation, Import oder einen anderen Writer.

## Ausstieg und Rückkehr

Nach EXP-0007 wertet GATE-0003 die vollständige Evidenz getrennt aus. Es darf:

- genau eine Übergabeform für einen späteren Planungsgegenstand auswählen;
- eine eng benannte Kernhärtung verlangen und die Adapterplanung vertagen;
- weitere Evidenz verlangen;
- oder die E-Book-Linie pausieren.

Ein Produktarbeitsgegenstand entsteht erst nach dieser Auswertung und einer
neuen Registrierung. EXP-0007 selbst wird nicht stillschweigend zum
Produktunterbau.
