# Aktuelle EPUB-Identitätsproduktqualifikation

Dieses Verzeichnis enthält den eingecheckten, ausschließlich synthetischen
Produktnachweis für den read-only Identitätskandidatenbericht. Der aktuelle
v3-Nachweis bindet seit WI-0013 fünf TEST-0001-Paare, acht konforme
Qualitätsfälle und zwei getrennte ungültige Kontrollen aus dem unveränderten
EXP-0010-Fallmanifest. Jeder der dreizehn qualifizierten Fälle läuft zweimal
über den tatsächlichen V1- und V2-CLI-Pfad. Zusätzlich werden deutsche
Ansicht, explizite Versionswahl, Pfadfreiheit, unveränderte Eingänge, Cleanup
und das commitgebundene vollständige Produktpreimage geprüft.

Der v3-Nachweis erfüllt 29/29 Kriterien. V1 bleibt bytekompatibler Standard;
V2 wird nur mit `--json --report-version v2` aktiviert und bewahrt die fünf
Entscheidungsstufen unverändert. Die gebundene rollenbewusste Projektion ist
verlustfrei und besitzt 241/241 Provenienzeinträge. Die sechs historischen
kritischen False Same bleiben auf null reduziert. Zwei weiterhin sichtbare
Werk-Oracledifferenzen liefern `candidate_related` statt `different` oder
`abstain`; sie sind nicht als gelöst dargestellt. Qualifiziert ist damit der
enge V1/V2-Vertrag, nicht das vollständige bibliografische Identitätsmodell.

Die Qualifikation erzeugt weder Netzwerkzugriff noch Produktpersistenz. Das
Schreiben der Ergebnisdatei durch das getrennte Qualifikationswerkzeug ist
Evidenzerzeugung und keine Wirkung des Produktvertrags.

Ausführen und Ergebnis validieren:

    python tools/qualify_ebook_identity.py \
      --temp-root C:\rep\tmp\SammlungsLotse\wi-0013-qualification
    python tools/qualify_ebook_identity.py --validate-result

Der frühere WI-0009-v1-Nachweis bleibt in der Git-Historie erhalten. Der
aktuelle Nachweis qualifiziert keine realen Bestände, keine automatische
Suche, keinen Calibre-Abgleich, keine weiteren Medienformate, keine
Publikationsstufe, keine V1-Deprecation und keine schreibende
Folgeaktion.
