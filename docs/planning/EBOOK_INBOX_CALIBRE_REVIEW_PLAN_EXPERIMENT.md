# EXP-0019: Synthetische Evidenz für einen E-Book-Reviewplan prüfen

Status: DONE — METHOD PASSED

Stand: 2026-09-13

Artifact: EXP-0019

## Zweck

EXP-0019 prüft ohne Produktcode und ausschließlich mit synthetischen Daten, ob ein E-Book-Eingangsordner zusammen mit bis zu drei expliziten, unveränderlichen Calibre-Projektionssnapshots zu einer begrenzten, pfadfreien und deterministischen Reviewplanung verbunden werden kann. Der Nachweis entscheidet weder über eine reale Sammlung noch über einen Import.

## Gebundener Gegenstand

- Ein Eingangsordner folgt den WI-0016-Grenzen: reguläre EPUB- und PDF-Eingänge, keine Link- oder Reparse-Point-Verfolgung, höchstens 32 Kandidaten und 256 MiB. PDF bleibt ein sichtbarer Nicht-EPUB-Fall.
- Bibliotheken sind ausschließlich vorab gebundene synthetische Projektionssnapshots. Jeder enthält nur die WI-0007-Felder `id`, `title`, `authors`, `languages` und `formats` sowie anonyme Snapshot-/Profil-/Provider-Provenienz. Es wird weder Calibre gestartet noch eine lokale Bibliothek gelesen.
- Kandidaten entstehen nur aus deterministischen, feldgebundenen Gründen. Je EPUB sind höchstens fünf, je Ordner höchstens zwölf Kandidaten erlaubt. Jeder Kandidat enthält Bibliotheksposition, externe ID, Grundstrategie und Snapshot-Digest.
- Die Kandidatenerzeugung ist nur ein Suchhinweis. Fünfstufige Identitätsevidenz bleibt logisch getrennt; das Experiment behauptet weder `same` noch eine Zielbibliothek oder Importberechtigung.

## Vorab gebundene Matrix

Jeder Fall wird zweimal durchgeführt. Die Resultate müssen nach Ausschluss technischer Laufzeitwerte semantisch identisch sein.

| Fall | Erwartete Reviewklasse |
| --- | --- |
| gültiger neuer EPUB ohne Kandidat | `review_new_candidate` |
| bytegleicher Kandidat in Bibliothek A | `review_candidate_present` |
| abweichende Ausgabe in Bibliothek B | `review_candidate_present` |
| Titelkollision unterschiedlicher Werke | `review_candidate_present` ohne Same-Behauptung |
| Kandidaten in zwei Bibliotheken | `review_cross_library` |
| Kandidatenlimit erreicht | `review_scope_incomplete` |
| bestehender Intake-Reviewfall | `review_ingress_blocked` |
| PDF | `unsupported` |
| fehlender oder inkonsistenter Snapshot | `not_assessed` |
| doppelte Bibliotheksidentität | `not_assessed` |

## Methodische Akzeptanzkriterien

Der Nachweis ist nur bestanden, wenn:

1. die zehn vorab gebundenen Fälle je zweimal vollständig ausgewertet werden;
2. alle Orakelklassen, Kandidatengrenzen und Bibliothekspositionen stimmen;
3. jeder Eingang genau eine sichtbare Klasse erhält und kein Eingang still ausgelassen wird;
4. jeder Kandidat seinen Grund und die Snapshot-Provenienz trägt;
5. Grenztreffer, Mehrbibliothekskonflikte, unvollständige Inventare, nicht beurteilbare Eingänge und Unsicherheit fail-closed sichtbar bleiben;
6. kein Ergebnis `same`, `new`, `import`, `target` oder eine gleichwertige fachliche Schlussfolgerung behauptet;
7. beide Wiederholungen semantisch identisch und Standardausgaben pfad-, namens- und metadatenfrei sind;
8. Quellen und Snapshots hashunverändert bleiben, der flüchtige Bereich vollständig bereinigt wird und Netzwerk, Persistenz, Produktimport, Calibre-Ausführung, Writer und Bestandswirkung null bleiben.

## Ergebnisgrenzen und Folge

Ein bestandener Nachweis qualifiziert nur die gebundene synthetische Matrix. Er beweist keine Kandidatenvollständigkeit, keine reale Calibre-Kompatibilität und keine Qualität einer späteren Routing- oder Importentscheidung. Ein anschließendes Ergebnisgate bewertet getrennt, ob ein eng begrenzter Produktarbeitsgegenstand für einen ephemeren, read-only Reviewplan angenommen wird.

## Ergebnis

Der gebundene Doppellauf ist bestanden. Alle zehn Orakelklassen wurden in
zwei semantisch identischen Wiederholungen erreicht. Kandidatengründe,
Bibliothekspositionen und Snapshot-Digests blieben sichtbar; die sechsfach
gebundene Grenzprobe blieb `review_scope_incomplete`. Der Ergebnisnachweis
enthält keine Eingangs- oder Projektionsmetadaten, Pfade oder private Daten.

Die Ausführung verwendete weder Calibre noch einen Eingangsordner und hatte
keine Netzwerk-, Persistenz-, Produktcode-, Writer- oder Bestandswirkung.
Der prüfbare Nachweis liegt unter `experiments/ebook/exp-0019/`.
