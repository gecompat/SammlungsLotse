# E-Book-Möglichkeitenraum

Status: BRAINSTORMING — KEINE PRODUKT- ODER ARCHITEKTURENTSCHEIDUNG

Stand: 2026-08-27

Artifacts: CAP-0002, REQ-0001

## Zweck

Dieses Dokument hält den ergebnisoffenen Möglichkeitenraum der E-Book-Linie
fest. Es beschreibt denkbare qualitätssteigernde Tätigkeiten, trennt sie nach
Gegenstand und Wirkung und kennzeichnet erste Untersuchungshypothesen.

Die Aufnahme einer Möglichkeit bedeutet weder Annahme noch Priorisierung. Die
E-Book-Linie ist weiterhin nicht als erste Implementierungslinie ausgewählt.
Technologie, Laufzeit, Persistenz, Benutzeroberfläche, Suchtechnik, konkrete
Werkzeuge und schreibende Operationen bleiben offen.

Der zugehörige Erkenntnis- und Experimentplan steht in
[EBOOK_EXPLORATION_PLAN.md](EBOOK_EXPLORATION_PLAN.md).

## Bereits geltende Grenzen

Die folgenden Punkte stammen aus bereits angenommener Projektgovernance und
sind keine neuen Ergebnisse dieses Brainstormings:

- Calibre bleibt für produktive E-Book-Bestände führend.
- Mehrere Calibre-Bibliotheken müssen als getrennte Ziele darstellbar sein.
- SammlungsLotse hält Beobachtungen, Evidenz, Ableitungen, Vorschläge und
  Ablaufzustände, bildet aber nicht die interne Calibre-Datenbank als
  Kernmodell nach.
- Analyse ist standardmäßig read-only.
- Import, Metadatenschreiben, Coveränderung, Verschieben und Löschen sind
  getrennte Operationstypen mit eigener Freigabe- und Sicherheitskette.
- Originalwerte werden durch Normalisierung oder Anreicherung nicht
  vernichtet.
- Externe Werkzeug-, Provider- und KI-Ergebnisse sind Evidenz und nicht
  ungeprüfte kanonische Wahrheit.
- Lokale und netzwerklose Verarbeitung bleibt der Ausgangspunkt.

## Zwei unabhängige Ordnungen

Eine Tätigkeit muss sowohl einem fachlichen Gegenstand als auch einer
Wirkungsstufe zugeordnet werden. Dadurch wird beispielsweise verhindert, dass
ein Dublettenkandidat mit einer Löschfreigabe oder ein Metadatenvorschlag mit
einer Calibre-Änderung gleichgesetzt wird.

### Fachliche Gegenstände

1. Quelle und Eingang;
2. Datei und Container;
3. Repräsentation eines E-Books;
4. bibliografische Ausgabe;
5. Werk;
6. Person und Beitrag oder Rolle;
7. Zielbibliothek und Sammlung;
8. Analyse-, Review- und Operationsablauf.

Eine Datei ist keine Ausgabe, eine Ausgabe ist kein Werk, ein Dateihash ist
keine Werkidentität und eine Calibre-ID ist eine externe Referenz oder ein
Locator.

### Wirkungsstufen

1. entdecken und beobachten;
2. prüfen und Befunde erzeugen;
3. Kandidaten, Bewertungen oder Vorschläge ableiten;
4. eine Änderung simulieren oder planen;
5. eine abgeleitete Datei in einem getrennten Arbeitsbereich erzeugen;
6. eine einzelne autorisierte Fachsystemoperation ausführen;
7. das Ergebnis unabhängig nachprüfen;
8. gegebenenfalls eine definierte Wiederherstellung durchführen.

Eine Freigabe oder Evidenz auf einer Stufe berechtigt nicht automatisch zur
nächsten Stufe.

## Mehrdimensionale Qualität

REQ-0001 hält als vorgeschlagene Anforderung fest, dass Qualität nicht auf
eine einzige Zahl reduziert wird. Mindestens folgende Dimensionen sind
voneinander zu unterscheiden:

- Integrität und Sicherheit;
- Format- und Standardkonformität;
- Darstellungs- und Reader-Kompatibilität;
- Barrierefreiheit;
- bibliografische Korrektheit;
- inhaltliche Vollständigkeit;
- technische und visuelle Lesbarkeit;
- Auffindbarkeit und Erschließung;
- Konsistenz mit Zielbibliothek und Sammlung;
- Sicherheit und Reversibilität einer vorgeschlagenen Änderung.

Ein Befund sollte, soweit anwendbar, enthalten:

- Qualitätsdimension und betroffenen Gegenstand;
- Status, Schweregrad und Gültigkeitsbereich;
- beobachtete Rohwerte;
- Evidenzquelle und Methode;
- Werkzeug, Profil und Version;
- Zeitpunkt und Eingangsrevision;
- Unsicherheit oder Konfidenz;
- Einschränkungen und notwendige manuelle Prüfung.

Geeignete Zustände können `pass`, `warning`, `fail`, `unknown` und
`not_applicable` sein. Ein späterer Gesamtscore wäre nur eine konfigurierbare
Ansicht. Er darf Einzelbefunde, Herkunft oder Nutzerentscheidung nicht
ersetzen.

## Möglichkeiten entlang des Lebenszyklus

### Eingang, Erfassung und Provenienz

- konfigurierte Ordner und Unterordner rekursiv erfassen;
- noch wachsende, temporäre oder unvollständige Dateien erkennen;
- Dateityp über Inhalt, Signatur und Struktur statt nur über die Endung
  bestimmen;
- Größe, relevante Zeitpunkte, kryptografische Hashes und Herkunft erfassen;
- Original, Kopie, Derivat und Fachsystemrepräsentation unterscheiden;
- Begleitdateien, Cover, Metadatendateien und Paketbeziehungen erkennen;
- Eingang, Quarantäne, Arbeitsbereich und Zielbibliothek getrennt halten;
- wiederholte Läufe inkrementell und unterbrechbar gestalten;
- Herkunfts-, Lizenz- oder Erwerbshinweise als Evidenz erfassen, ohne daraus
  automatisch Nutzungsrechte abzuleiten.

### Sicherheit und Schutzmechanismen

- DRM, Verschlüsselung, Signaturen und Font-Obfuskation erkennen;
- geschützte und nicht unterstützte Inhalte klassifizieren, ohne Schutz zu
  umgehen;
- ZIP-Bombs, übermäßige Expansion, Path Traversal und ungewöhnliche
  Paketstrukturen erkennen;
- Skripte, aktive Inhalte, externe Links und Remote-Ressourcen erfassen;
- XML-Entitäten, Parser-Risiken und unerwartete eingebettete Dateien prüfen;
- Werkzeugausführung durch Zeit-, Speicher-, Dateigrößen-, Prozess- und
  Netzwerkgrenzen isolieren;
- unbekannte oder risikoreiche Dateien ohne Bestandsänderung in eine
  Review- oder Quarantäneentscheidung führen.

### EPUB-Struktur und Standardkonformität

- ZIP- und OCF-Struktur, `mimetype` und `container.xml` prüfen;
- Package Document, Manifest, Spine und Fallbacks prüfen;
- fehlende, doppelte, unreferenzierte oder falsch typisierte Ressourcen
  erkennen;
- XHTML, SVG, CSS, MathML, Navigation und Media Overlays prüfen;
- Inhaltsverzeichnis, Lesereihenfolge, Seitenliste und Landmarks bewerten;
- Zeichenkodierung, interne Links und Fragmentverweise prüfen;
- Reflowable und Fixed Layout unterscheiden;
- EPUB-Version, veraltete Merkmale und Mehrfachrenditionen erkennen;
- Skripting, Remote-Ressourcen und Sicherheitsmerkmale gesondert ausweisen;
- formale Konformität von praktischer Lesbarkeit und Barrierefreiheit
  getrennt halten.

### Weitere Formate

Für PDF, MOBI, AZW, AZW3, KEPUB, FB2, CBZ und weitere Formate sind
formatbezogene Fähigkeitsprofile denkbar. Mögliche Prüfungen umfassen:

- Parser- und Öffnungserfolg;
- Formatvariante, Verschlüsselung und Schutzstatus;
- eingebetteten oder extrahierbaren Text;
- Seiten, Bilder, Fonts und Ressourcen;
- behauptete PDF/A- oder PDF/UA-Konformität;
- Textabdeckung und Scancharakter;
- vorhandene Navigation und Inhaltsstruktur;
- erwartbaren Informationsverlust einer Konvertierung;
- bekannte Grenzen des jeweiligen Analysewerkzeugs.

Ein Format, für das noch keine tiefe Analyse existiert, soll trotzdem als
erkanntes, inventarisiertes und ausdrücklich nicht tief unterstütztes Objekt
sichtbar bleiben.

### Darstellung und Lesbarkeit

- Dateien in repräsentativen Readern öffnen;
- Cover, erste Seite, Kapitelanfänge und Kapitelübergänge prüfen;
- Inhaltsverzeichnis, Links, Fußnoten und Querverweise testen;
- Tabellen, Code, Formeln, Bilder, Audio und Video prüfen;
- Reflow, Schriftgrößen, Themes und Seitenumbrüche bewerten;
- RTL, vertikalen Text und nichtlateinische Schriften prüfen;
- Reader- und Gerätematrizen mit klar begrenztem Zielprofil verwenden;
- automatisierte Screenshots oder Rendervergleiche erzeugen;
- automatisch nicht prüfbare Darstellungsmerkmale einem manuellen Review
  zuführen.

### Barrierefreiheit

- Titel, Sprache, Überschriftenstruktur und Landmarks prüfen;
- Navigation und Lesereihenfolge bewerten;
- Alternativtexte, Bildbeschreibungen und dekorative Bilder unterscheiden;
- Tabellen, Formeln, Fußnoten und erweiterte Beschreibungen prüfen;
- Accessibility-Metadaten und Konformitätsbehauptungen erfassen;
- Tastaturbedienung, Screenreader und Text-to-Speech manuell prüfen;
- maschinelle und manuelle Accessibility-Evidenz getrennt ausweisen;
- eine bestandene automatische Prüfung nicht als vollständige
  Barrierefreiheitskonformität darstellen.

### Inhaltliche Vollständigkeit

- fehlende, doppelte oder falsch sortierte Kapitel erkennen;
- abrupten Anfang oder Schluss sowie auffällige Längenabweichungen erkennen;
- Leseproben, Auszüge, Platzhalter und Werbeinhalte klassifizieren;
- beschädigte oder fehlende Abbildungen erkennen;
- Zeichensalat, Kodierungsfehler und OCR-Artefakte bewerten;
- wiederholte Kopf- und Fußzeilen, harte Umbrüche und Trennfehler erkennen;
- Verluste bei Tabellen, Formeln, Fußnoten und Referenzen feststellen;
- Kapitel- und Textstruktur mit anderen Repräsentationen oder Ausgaben
  vergleichen;
- Scanauflösung, Schieflage, Kontrast und OCR-Abdeckung bewerten;
- deterministische Befunde, statistische Auffälligkeiten und modellbasierte
  Einschätzungen sichtbar trennen.

### Bibliografische Metadaten

- eingebettete Werte, Dateinamen, Calibre-Werte und externe Quellen getrennt
  beobachten;
- Titel, Untertitel, Sortiertitel und alternative Titel auflösen;
- Personen, Körperschaften, Beiträge und Rollen unterscheiden;
- Anzeigename, Namensbestandteile, Sortiername und Normdatenreferenzen
  getrennt halten;
- ISBN, DOI und andere Identifikatoren syntaktisch prüfen und als Kandidaten
  auflösen;
- Werk, Ausgabe, Übersetzung, Bearbeitung und Repräsentation unterscheiden;
- Verlag, Publikationsdatum, Sprache, Reihe und Serienposition prüfen;
- Schlagwörter, Fachgebiete, Zielgruppen und Altersklassen vorschlagen;
- Cover einer konkreten Ausgabe zuordnen;
- widersprüchliche Quellen samt Herkunft, Aktualität und Konfidenz anzeigen;
- Nutzerbestätigungen erhalten, ohne frühere Beobachtungen zu überschreiben.

### Identität und Dubletten

- byteidentische Dateien anhand kryptografischer Hashes erkennen;
- inhaltsgleiche Pakete trotz anderer ZIP-Reihenfolge oder Metadaten finden;
- gleiche Ausgabe in mehreren Formaten gruppieren;
- gleiches Werk in verschiedenen Ausgaben, Übersetzungen oder Bearbeitungen
  erkennen;
- Leseprobe und Vollausgabe unterscheiden;
- Text-, Kapitel- und Bildfingerprints einsetzen;
- ISBN-, Titel-, Personen- und Serienmerkmale kombinieren;
- Kandidaten mit positiver und negativer Evidenz erklären;
- Schwellenwerte, Enthaltung und manuelle Entscheidungen unterstützen;
- die beste Repräsentation pro Qualitätsdimension vergleichen;
- eine Dublettenentscheidung nicht mit Löschung oder Formatentfernung
  gleichsetzen.

### Suche und Erschließung

- strukturierte Metadatensuche anbieten;
- Volltext mit nachvollziehbaren Fundstellen durchsuchen;
- Facetten nach Sprache, Format, Zielbibliothek, Person, Reihe und Befund
  bilden;
- fehlertolerante Suche, Transliteration und Synonyme untersuchen;
- Werke, Ausgaben, Personen und Themen als getrennte Suchobjekte behandeln;
- ähnliche Werke oder alternative Ausgaben finden;
- gezielt nach Qualitätsproblemen suchen;
- gespeicherte Review- und Prüfansichten bereitstellen;
- lokale semantische und mehrsprachige Suche erproben;
- KI-gestützte Fragen, Zusammenfassungen und Klassifikationen als optionale,
  ableitbare Evidenz behandeln.

### Routing und Review

- mehrere Calibre-Bibliotheken als eigenständige Ziele erfassen;
- Zielvorschläge über versionierte Regeln und Evidenz erklären;
- Fachbuch-, Kinderbuch- und weitere Bestandsklassen unterstützen;
- Ambiguität und Enthaltung als reguläres Ergebnis zulassen;
- Nutzerkorrekturen und Ablehnungsgründe nachvollziehbar erhalten;
- Einzel- und Sammelreview mit Stichproben und Begrenzungen unterstützen;
- vor jeder schreibenden Aktion den aktuellen Zielzustand erneut prüfen;
- Routingentscheidung und Schreibfreigabe getrennt halten.

### Reparatur und Transformation

- Metadatenpatches vorschlagen;
- Cover ersetzen, zuschneiden oder optimieren;
- Navigation, Links, Encoding, XHTML und CSS reparieren;
- Bilder komprimieren oder skalieren;
- OCR, Drehen, Entzerren und Bereinigen für Scan-PDFs erproben;
- zusätzliche EPUB-, KEPUB-, AZW3- oder PDF-Repräsentationen erzeugen;
- barriereärmere Ableitungen herstellen;
- Inhaltsverzeichnis oder Accessibility-Metadaten ergänzen;
- Übersetzung, Zusammenfassung oder Text-to-Speech als gesonderte
  Produktoption untersuchen.

Transformationen sollen niemals das einzige Original überschreiben. Ein
Derivat benötigt mindestens Eingangs- und Ausgangshash, Rezept, Parameter,
Werkzeugprofil, Zeitpunkt, Validierung und Herkunftsbeziehung.

### Calibre-Orchestrierung

Folgende Operationen sind technisch denkbar, bleiben aber getrennte
Operationstypen:

- neues Buch importieren;
- Format zu einem bestehenden Buch hinzufügen;
- vorhandenes Format ersetzen;
- Metadaten ändern;
- Cover ändern;
- Tags oder Custom Columns schreiben;
- zwischen Bibliotheken übertragen;
- Format entfernen;
- Buch entfernen.

Eine spätere Ausführung darf nur über dokumentierte und unterstützte
Calibre-Schnittstellen erfolgen. Calibre-interne Tabellen oder Verzeichnisse
werden nicht direkt geschrieben.

### Kontinuierliche Bestandsqualität

- neue Eingänge und relevante Bestandsänderungen erkennen;
- unveränderte Dateien nicht ohne Grund erneut analysieren;
- veraltete Befunde nach Werkzeug-, Regel- oder Modellwechsel markieren;
- Fixity und Erreichbarkeit von Repräsentationen überwachen;
- Suchindex, Evidenzbestand und Fachsystem-Snapshot auf Drift prüfen;
- abgebrochene Läufe sicher fortsetzen;
- Ressourcenverbrauch, Laufzeit und Fehlerraten messen;
- Stichproben und manuelle Nachprüfungen planen;
- reproduzierbare Berichte und Auditverläufe bereitstellen.

### Benutzer- und Automationszugänge

- Review-Warteschlangen und begründete Befundkarten;
- Vergleichsansichten für Dubletten und Metadatenkonflikte;
- Vorschau von Änderungen und Nachprüfungsergebnisse;
- CLI, Browser, REST und Agents über dieselben Anwendungsverträge;
- getrennte lesende und schreibende Fähigkeiten;
- versionierte Schemas, Pagination und stabile Fehlerverträge;
- operationstypische Berechtigungen und Idempotenz;
- keine Sonderrechte für Agents oder einen bestimmten Zugangskanal.

## Denkbare Produktrollen

Die E-Book-Linie kann aus mehreren unabhängig kombinierbaren Produktrollen
bestehen:

1. Bestandsprüfer für vorhandene Calibre-Bibliotheken;
2. Eingangstriage für neue Dateien;
3. Identitäts- und Metadatenklärer;
4. Such- und Erschließungsschicht;
5. Review- und Reparaturwerkbank;
6. kontrollierter Calibre-Orchestrator;
7. kontinuierlicher Bestandswächter.

Diese Rollen müssen nicht gemeinsam oder in dieser Reihenfolge umgesetzt
werden.

## Vorläufige Untersuchungshypothesen

Besonders hohen Erkenntnisgewinn bei geringer früher Bindung versprechen:

- ein synthetischer Referenzbestand mit bekannten Sollbefunden;
- eine allgemeine Formathülle mit zunächst tiefer EPUB-Analyse;
- read-only Calibre-Inventar über unterstützte Schnittstellen;
- exakte Dateihashes und nachvollziehbare Dublettenkandidaten;
- standardisierte, aber verlustfreie Aufnahme von EPUBCheck- und Ace-Berichten;
- getrennte Rohmetadaten und Konflikte mit Provenienz;
- mehrere synthetische Zielbibliotheken und begründetes Routing;
- inkrementelle, unterbrechbare Analyse;
- eine Review-Oberfläche auf gemeinsamen Anwendungsverträgen.

Erst mit einem Goldstandard sinnvoll bewertbar sind insbesondere:

- unscharfes Werk- und Ausgabenmatching;
- Erkennung von Leseproben und inhaltlicher Unvollständigkeit;
- externe Metadatenanreicherung und Normdatenauflösung;
- PDF- und OCR-Qualität;
- Volltext- und semantische Suche;
- automatische Routingvorschläge;
- Reader- und Renderingmatrizen;
- reproduzierbare Reparaturen und Transformationen.

Als später offen zu haltende, eigenständige Produktideen gelten unter anderem:

- ein eigener E-Book-Reader;
- Lesefortschritt, Notizen und Markierungen;
- Geräte- oder Cloud-Synchronisierung;
- Erwerbungs-, Store- oder Leihintegration;
- Empfehlungen und persönliche Leselisten;
- generative Übersetzung, Inhaltskorrektur, Cover- oder Hörbucherzeugung;
- unbeaufsichtigte Reparatur oder Integration.

## Aktueller Werkzeug- und Standardhorizont

Die folgenden Angaben sind Quellenbefunde vom 2026-08-27 und keine
Abhängigkeitsentscheidungen:

- EPUB 3.3 ist seit 2026-01-13 eine W3C Recommendation. EPUB 3.4 befindet sich
  als nachfolgender Entwurf in Arbeit. Prüfverträge benötigen daher
  versionierte Standardprofile.
- EPUBCheck bezeichnet Version 5.3.0 als aktuelle produktionsreife Version und
  prüft EPUB 2 sowie EPUB 3 gegen EPUB 3.3.
- Ace by DAISY ergänzt automatisierbare Accessibility-Prüfungen. Die
  DAISY-Dokumentation weist ausdrücklich darauf hin, dass automatische
  Ergebnisse manuelle Accessibility-Prüfungen nicht ersetzen.
- `calibredb` stellt unter anderem maschinenlesbares `list`, `add`,
  `add_format`, `remove_format`, `show_metadata` und `set_metadata` bereit.
  Diese Befehle besitzen unterschiedliche Schreibwirkungen.
- Apache Tika, veraPDF, OCRmyPDF und Tesseract sind mögliche Kandidaten für
  Extraktion, PDF-Profilprüfung und OCR. Ihre Eignung ist je Vertrag,
  Formatvariante und Lizenz getrennt zu prüfen.
- DNB und GND, Open Library, Crossref und Google Books sind mögliche
  Metadatenquellen. Netzwerknutzung, Datenminimierung, Lizenz, Limits,
  Abdeckung und Ausstiegsweg sind providerbezogen zu bewerten.

Primärquellen:

- W3C, EPUB 3.3: https://www.w3.org/TR/epub-33/
- W3C, EPUB 3.4: https://www.w3.org/TR/epub-34/
- W3C, EPUB-Testrepository: https://github.com/w3c/epub-tests
- W3C/DAISY, EPUBCheck: https://github.com/w3c/epubcheck
- DAISY, Ace: https://kb.daisy.org/publishing/docs/epub/validation/ace.html
- DAISY, Ace SMART:
  https://smart.daisy.org/user-guide/overview.html
- calibre, `calibredb`:
  https://manual.calibre-ebook.com/generated/en/calibredb.html
- calibre, unterstützte Konvertierungsformate:
  https://manual.calibre-ebook.com/faq.html
- Apache Tika: https://tika.apache.org/
- veraPDF: https://docs.verapdf.org/validation/
- OCRmyPDF: https://ocrmypdf.readthedocs.io/en/stable/
- Tesseract: https://tesseract-ocr.github.io/tessdoc/
- Open Library: https://openlibrary.org/developers
- Crossref: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- Google Books: https://developers.google.com/books/docs/v1/using

## Bewusst offene Entscheidungen

- Auswahl der ersten Medienlinie;
- erster vollständiger Nutzerablauf;
- Umfang der zunächst tief unterstützten Formate;
- Programmiersprache, Runtime und Paketstruktur;
- Persistenz, Volltext- und Vektorsuche;
- Browser-, Desktop-, CLI- oder Plugin-Oberfläche;
- lokales Betriebs- und Deploymentmodell;
- konkrete Calibre-Adapterform;
- konkrete Metadatenprovider;
- Gewichtung oder Darstellung von Qualitätsdimensionen;
- erste Transformation oder erste produktive Schreiboperation;
- konkrete FolioTone-Wiederverwendung.
