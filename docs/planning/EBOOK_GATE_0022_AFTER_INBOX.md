# GATE-0022: Nächste sichere E-Book-Fortsetzung nach dem Eingangsordner bewerten

Status: DONE — OPTION A AUTONOM AUSGEWÄHLT

Stand: 2026-09-13

Artifact: GATE-0022

## Ausgangslage

WI-0016 hat den ausdrücklich ausgewählten, begrenzten und read-only
E-Book-Eingangsordner mit ausschließlich synthetischer Abnahme abgeschlossen.
Die Ordnerübersicht inventarisiert reguläre EPUB- und PDF-Eingänge, wahrt die
bestehenden Grenzen und löst weder eine tiefe Prüfung noch eine
Bestandswirkung aus. Sie beantwortet jedoch noch nicht, ob ihre aggregierten
Ergebnisse für eine sichere spätere manuelle Priorisierung ausreichend
erklärbar und stabil sind.

Die aktuelle Nutzerautorisierung verlangt autonome Projektfortsetzung. Sie
ersetzt weder die Produktgrenzen noch die Regel, dass Produktcode einen
eigenen registrierten und angenommenen Arbeitsgegenstand benötigt.

## Bewertungsmaßstab

Jede Option wird getrennt nach unmittelbarem Nutzerwert, Evidenzreife,
Datenschutz, Sicherheitsgrenzen, Kopplung, Reversibilität und
Validierbarkeit bewertet. Ein Ergebnis dieses Gates darf keine reale/private
Eingabe, Netzwerk-, Persistenz-, Fachsystem- oder Schreibwirkung begründen.

## Optionen

### A — Synthetische Erklärung der Ordneraggregate erproben

Ein produktcodefreies Experiment prüft mit dem bestehenden TEST-0001-Korpus,
ob eine kleine, pfadfreie und deterministische Aggregation der bereits
sichtbaren Ordnerergebnisse eine manuelle Priorisierung erklären kann. Es
ändert weder die CLI noch bestehende Entscheidungen und kann bei einem
negativen Befund ohne Produktwirkung beendet werden.

- Nutzen: beantwortet die nächste konkrete Erklärbarkeitsfrage am neuen
  Eingangsweg.
- Risiko: ein zu enger Korpus kann keine Aussage über reale Sammlungen
  tragen; dies bleibt als Grenze sichtbar.
- Kopplung: gering, da nur bestehende synthetische Verträge ausgewertet
  werden.

### B — Neue sichtbare Ordneroberfläche implementieren

Eine zusätzliche Human- oder JSON-Projektion könnte die Ordnerübersicht
erweitern. Sie verändert jedoch den öffentlichen Vertrag und benötigt zuerst
eine nachweisbare Erklärung, genaue Kompatibilitätsregeln und einen eigenen
angenommenen Produktarbeitsgegenstand.

- Nutzen: potenziell direkt sichtbar.
- Risiko: öffentliche Vertragsfläche ohne zuvor gebundenen Evidenzgewinn.
- Entscheidung: nicht vor Option A.

### C — Calibre-Bestandsqualität beginnen

Eine Bestandsqualitätsprojektion wäre fachlich wertvoll, verbindet aber
Feldsemantik, mehrere Qualitätsdimensionen und Folgeentscheidungen. Sie ist
nicht die kleinste Fortsetzung nach dem ausdrücklich begrenzten Eingangsordner.

- Nutzen: hoch, aber nicht unmittelbar an WI-0016 anschlussfähig.
- Risiko: zu breite neue Domänen- und Architekturfläche.
- Entscheidung: nicht auswählen.

### K — Ergebnis konservieren

WI-0016 bleibt historisch prüfbar; es wird keine Folgearbeit begonnen.

## Auswahl

Option A wird unter der aktuellen ausdrücklichen Autonomie-Autorisierung
ausgewählt. Sie ist die kleinste reversible Fortsetzung und führt ausschließlich
eine getrennte, synthetische Erkenntniswave ein. GATE-0022 autorisiert keinen
Produktcode. Die Folgearbeit wird separat als EXP-0018 registriert und muss
ihren eigenen Vertrag erfüllen.

## Harte Grenzen

- keine reale oder private E-Book-Analyse;
- keine Änderung bestehender CLI-, V1- oder V2-Berichtsverträge;
- keine Lockerung von `review` oder `deep_read_only_allowed`;
- kein Netzwerk, keine Persistenz, kein Fachsystemzugriff und keine
  Schreib- oder Bestandswirkung;
- keine automatische Priorisierung, Sortierung, Routing- oder
  Importentscheidung.
