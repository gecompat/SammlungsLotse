# GATE-0005: Nächsten read-only Nutzwert nach WI-0008 auswählen

Status: AUSGEWERTET — WI-0009 AUSGEWÄHLT

Stand: 2026-08-28

Artifact: GATE-0005

## Entscheidung

Als nächste Wave wird WI-0009 ausgewählt: ein erklärbarer read-only
Identitätskandidatenbericht für genau zwei ausdrücklich angegebene lokale
EPUB-Dateien. Er vergleicht unveränderliche Snapshots, trennt positive,
negative und fehlende Evidenz und löst keine Bestandswirkung aus.

Die Wave greift die im Projektauftrag ausdrücklich genannte Erkennung von
Dubletten vor einer Zielintegration auf. EXP-0004 hat dafür fünf
Identitätsebenen, Enthaltung und asymmetrische False-Positive-Kosten an sechs
kleinen synthetischen Paaren belegt. Das Experiment ist keine
Produktfreigabe; WI-0009 übernimmt deshalb nur den kleinsten lokal
erklärbaren Paarvergleich und qualifiziert ihn neu gegen TEST-0001 `0.3.0`.

## Bewertete Optionen

| Option | Nutzwert | Schwerstes Risiko | Entscheidung |
|---|---|---|---|
| A — zwei explizite EPUB-Dateien vergleichen | Unterstützt eine konkrete Dublettenprüfung vor Integration und nutzt vorhandene Snapshot- sowie EXP-0004-Evidenz. | Falsche Gleichsetzung könnte zu einer späteren falschen Bestandsaktion verleiten. | Ausgewählt, aber nur als erklärbarer Kandidatenbericht mit Enthaltung und ohne Aktion. |
| B — eine Datei gegen den Calibre-Bestand vergleichen | Wäre näher am Zielbestand. | WI-0007 gibt absichtlich keine Dateilocators, Hashes oder bibliografisch ausreichenden Identitätsfelder aus; eine Kopplung würde dessen Grenze umgehen. | Vertagt, bis ein eigener read-only Evidenzvertrag begründet ist. |
| C — mehrere Bibliotheken, externe Metadaten oder Accessibility-Provider | Kann später größere fachliche Reichweite liefern. | Erweitert Provider-, Datenschutz-, Ziel- oder Betriebsfläche und besitzt noch keinen ausreichend kleinen Produktvertrag. | Getrennt neu bewerten. |

## Auswahlmaßstab

Bewertet wurden unmittelbarer Nutzwert, vorhandene empirische Grundlage,
False-Positive-Kosten, Datenschutz, Kopplung, Reversibilität und bestehende
Autorisierung. Option A benötigt weder einen neuen externen Provider noch
Calibre-, Netzwerk- oder Persistenzzugriff. Die Eingänge sind explizit, die
Analyse bleibt lokal und ein Kandidat kann keine Folgeaktion auslösen.

Option B würde die bewusst minimale Calibre-Projektion fachlich überdehnen.
Option C bündelt mehrere weiterhin offene Entscheidungen und ist nicht die
kleinste sichere Anschlusswave.

## Gate-Folgen

- GATE-0005 ist mit dieser dokumentierten Auswahl `done`.
- WI-0009 ist als eigener Arbeitsgegenstand `accepted`.
- Produktcode beginnt erst nach Merge dieser Planungs-Wave nach `main`.
- EXP-0004-Heuristiken werden nicht blind kopiert; nur neu dokumentierte und
  gegen aktive Fixtures getestete Regeln dürfen in den Produktpfad gelangen.
- Ein Kandidat ist Evidenz, keine Dublettenwahrheit und keine Lösch-, Import-,
  Formatentfernungs- oder Metadatenfreigabe.

## Nicht autorisiert

Nicht autorisiert sind Verzeichnissuche, mehr als zwei Eingänge, andere
Formate als EPUB, Vergleich gegen Calibre, Zugriff auf Bibliotheksdateien,
Persistenz, Index, Cache, Netzwerk, externe Metadaten, statistische oder
modellbasierte Ähnlichkeit, Browser, REST, Agents und jeder Writer.
