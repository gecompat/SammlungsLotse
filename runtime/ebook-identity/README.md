# Aktuelle EPUB-Identitätsproduktqualifikation

Dieses Verzeichnis enthält den eingecheckten, ausschließlich synthetischen
Produktnachweis für den read-only Identitätskandidatenbericht. Der Nachweis
bindet seit WI-0012 fünf TEST-0001-Paare und acht konforme Qualitätsfälle aus
dem unveränderten EXP-0010-Fallmanifest. Jeder der dreizehn JSON-Fälle läuft
zweimal über den tatsächlichen CLI-Prozess. Zusätzlich werden deutsche
Ansicht, öffentliches v1-Berichtsschema, Pfadfreiheit, unveränderte Eingänge,
Cleanup und das commitgebundene vollständige Produktpreimage geprüft.

Der v2-Nachweis erfüllt 19/19 Guardrail-Kriterien. Die sechs historischen
kritischen False Same sind auf null reduziert. Zwei weiterhin sichtbare
Werk-Oracledifferenzen liefern `candidate_related` statt `different` oder
`abstain`; sie gehören zu den ausdrücklich nicht gelösten rollenbewussten
Metadaten- und Collection-Fragen. Der Guardrail ist damit qualifiziert, nicht
das vollständige bibliografische Identitätsmodell.

Die Qualifikation erzeugt weder Netzwerkzugriff noch Produktpersistenz. Das
Schreiben der Ergebnisdatei durch das getrennte Qualifikationswerkzeug ist
Evidenzerzeugung und keine Wirkung des Produktvertrags.

Ausführen und Ergebnis validieren:

    python tools/qualify_ebook_identity.py \
      --temp-root C:\rep\tmp\SammlungsLotse\wi-0012-qualification
    python tools/qualify_ebook_identity.py --validate-result

Der frühere WI-0009-v1-Nachweis bleibt in der Git-Historie erhalten. Der
aktuelle Nachweis qualifiziert keine realen Bestände, keine automatische
Suche, keinen Calibre-Abgleich, keine weiteren Medienformate, keine
vollständige Identifier-/Collection-Semantik und keine schreibende
Folgeaktion.
