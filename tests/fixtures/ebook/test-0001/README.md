# TEST-0001-Fixtures

Status: EXECUTABLE SYNTHETIC COMPLETE CORPUS

Diese Fixtures sind die vollständig materialisierte Fassung des registrierten
Testvertrags TEST-0001. Sie enthalten ausschließlich unabhängig erzeugte,
minimale synthetische Daten unter der Projektlizenz MIT.

Der Generator ist
`tools/fixtures/generate_ebook_reference_corpus.py`. Die aktuelle versionierte
Fassung `0.3.0` liegt unter `v0.3/`; ihr `manifest.json` enthält alle 26
`Kern`- und vier `Ausbau`-Fälle:

- Eingänge und Ablauf-Snapshots;
- SHA-256 und Größe jeder Komponente;
- Konstruktions- und Herkunftsangaben;
- erlaubte Ergebnisse und erwartete Beobachtungs- und Befundschlüssel;
- verbotene Ergebnisse und Wirkungen;
- Qualitätsdimension, Ressourcenprofil und Prüfmethode.

`v0.1/` und `v0.2/` bleiben als unveränderbare historische Snapshots
erhalten. `v0.1/` verwendet im OPF ein durch EXP-0005 als nicht konform
erkanntes `version="3.3"` und ist nicht mehr die aktive Experimentbasis.

Die vier `Ausbau`-Fälle materialisieren minimales EPUB 2, EPUB 3 Fixed
Layout, mehrsprachigen RTL-Inhalt und Routing ohne passende Regel.
Absichtlich ungültige oder riskante Dateien sind im Manifest als
solche gekennzeichnet und dürfen nicht als allgemeine Referenzqualität
verwendet werden.

Die kanonische Prüfung lautet:

    python tools/fixtures/validate_ebook_reference_corpus.py

Sie prüft Manifest und Hashes, zentrale Sollbeziehungen, Datenschutz,
Netzwerkgrenze, bytegenaue Reproduzierbarkeit und die Unverändertheit aller
Fixture-Eingänge während der read-only Prüfung. Der Generator verweigert ein
bereits vorhandenes Ausgabeverzeichnis; eine Regeneration erfolgt in einem
neuen temporären Pfad und überschreibt die versionierte Fassung nicht.
