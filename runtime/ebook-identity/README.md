# WI-0009-Produktqualifikation

Dieses Verzeichnis enthält den eingecheckten, ausschließlich synthetischen
Produktnachweis für den read-only Identitätskandidatenbericht. Der Nachweis
bindet fünf TEST-0001-Paare und das vollständige Produktpreimage, führt jeden
JSON-Fall zweimal über den tatsächlichen CLI-Prozess aus und prüft zusätzlich
die deutsche Ansicht, Pfadfreiheit sowie unveränderte Fixture-Hashes.

Die Qualifikation erzeugt weder Netzwerkzugriff noch Produktpersistenz. Das
Schreiben der Ergebnisdatei durch das getrennte Qualifikationswerkzeug ist
Evidenzerzeugung und keine Wirkung des Produktvertrags.

Ausführen und Ergebnis validieren:

    python tools/qualify_ebook_identity.py
    python tools/qualify_ebook_identity.py --validate-result

Der Nachweis qualifiziert keine realen Bestände, keine automatische Suche,
keinen Calibre-Abgleich, keine weiteren Medienformate und keine schreibende
Folgeaktion.
