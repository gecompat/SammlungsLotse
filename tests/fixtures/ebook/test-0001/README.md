# TEST-0001-Fixtures

Status: EXECUTABLE SYNTHETIC CORE CORPUS

Diese Fixtures sind die erste ausführbare Fassung des registrierten
Testvertrags TEST-0001. Sie enthalten ausschließlich unabhängig erzeugte,
minimale synthetische Daten unter der Projektlizenz MIT.

Der Generator ist
`tools/fixtures/generate_ebook_reference_corpus.py`. Die versionierte Fassung
liegt unter `v0.1/`; ihr `manifest.json` enthält für alle 26 `Kern`-Fälle:

- Eingänge und Ablauf-Snapshots;
- SHA-256 und Größe jeder Komponente;
- Konstruktions- und Herkunftsangaben;
- erlaubte Ergebnisse und erwartete Beobachtungs- und Befundschlüssel;
- verbotene Ergebnisse und Wirkungen;
- Qualitätsdimension, Ressourcenprofil und Prüfmethode.

Die vier `Ausbau`-Fälle aus dem Testvertrag sind nicht Bestandteil dieser
Fassung. Absichtlich ungültige oder riskante Dateien sind im Manifest als
solche gekennzeichnet und dürfen nicht als allgemeine Referenzqualität
verwendet werden.

Die kanonische Prüfung lautet:

    python tools/fixtures/validate_ebook_reference_corpus.py

Sie prüft Manifest und Hashes, zentrale Sollbeziehungen, Datenschutz,
Netzwerkgrenze, bytegenaue Reproduzierbarkeit und die Unverändertheit aller
Fixture-Eingänge während der read-only Prüfung. Der Generator verweigert ein
bereits vorhandenes Ausgabeverzeichnis; eine Regeneration erfolgt in einem
neuen temporären Pfad und überschreibt die versionierte Fassung nicht.
