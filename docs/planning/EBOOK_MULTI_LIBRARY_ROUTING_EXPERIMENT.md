# EXP-0024: Synthetische Mehrbibliotheks-Routingmatrix für den E-Book-Reviewplan

Status: DONE — METHOD PASSED

Stand: 2026-09-20

Artifact: EXP-0024

## Zweck

EXP-0024 prüft ausschließlich mit vorab gebundenen TEST-0001-nahen
synthetischen Evidenzschlüsseln, ob ein klarer Eingangs-Reviewfall und bis zu
drei minimale Bibliotheksprojektionen deterministisch in sichtbare manuelle
Routinghinweise eingeordnet werden können. Der Nachweis ist kein Produktcode
und führt keine Bibliothek, keinen Provider und kein E-Book-Werkzeug aus.

## Gebundene Matrix und Grenzen

- Die Matrix enthält genau zehn künstliche Fälle, höchstens drei
  Bibliothekspositionen und höchstens vier Hinweise je Eingang.
- Ein passender Evidenzschlüssel erzeugt ausschließlich den Grund
  `bound_evidence_key`; Titel, Autoren, Pfade, Medien, Calibre-IDs und
  Snapshotinhalte werden nicht ausgegeben.
- Genau eine sichtbare Bibliotheksposition kann
  `review_target_candidate` ergeben. Das Literal ist ein nicht ausführbarer
  manueller Hinweis, keine Zielwahl, kein Ranking und keine
  Same-/New-/Importbehauptung.
- Mehrere Positionen bleiben `review_cross_library`; fehlende oder doppelte
  Projektionen sowie Grenzüberschreitungen bleiben
  `review_scope_incomplete`; nicht klare oder nicht beurteilbare Evidenz
  bleibt `not_assessed`.
- Jeder Ergebnisdatensatz bindet `routing-rules/v1` und `test-0001/v0.3`.
  Der eingecheckte Nachweis enthält nur Fallkennung, Klasse, sichtbaren
  Zustand, Kandidatenanzahl, Kandidatengrund und Bibliotheksposition.

## Methodische Akzeptanzkriterien

Der Nachweis besteht nur, wenn alle zehn Fälle zweimal semantisch identisch
ausgewertet werden, jede gebundene Orakelklasse erreicht wird und Konflikt,
Inventarlücke, Kandidatengrenze sowie nicht beurteilbare Evidenz sichtbar
bleiben. Die Matrix muss pfad- und metadatenfrei bleiben, ihre Quellen
hashunverändert lassen und den flüchtigen Arbeitsbereich bereinigen.

Netzwerk, Persistenz, Discovery, Calibre-Ausführung, Docker-, Podman- oder
sonstige Prozessausführung, Produktcode, automatische Zielwahl, Import und
alle Writer-Effekte bleiben null.

## Ergebnis und Folgegrenze

Der Doppellauf besteht für die gebundene Matrix. Er qualifiziert weder eine
reale Bibliothek noch Vollständigkeit, Suchqualität, eine Zielbibliothek oder
eine Produkt- beziehungsweise Schreibwirkung. Nur ein neues getrenntes
Ergebnisgate darf eine mögliche Folge bewerten.
