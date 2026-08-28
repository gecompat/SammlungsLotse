# WI-0009: Read-only Identitätskandidatenbericht für zwei EPUB-Dateien

Status: DONE — SYNTHETISCH QUALIFIZIERT

Stand: 2026-08-28

Artifact: WI-0009

## Ziel und kleinster Nutzwert

Ein Nutzer gibt genau zwei lokale EPUB-Dateien ausdrücklich an und erhält
einen pfadfreien, erklärbaren Bericht dazu, welche Identitätsevidenz für oder
gegen Gleichheit beziehungsweise Beziehung spricht und wo SammlungsLotse
sich enthält. Der Bericht unterstützt manuelle Prüfung vor einer möglichen
Integration, löst aber keine Folgeaktion aus.

Die erste Wave verarbeitet keine Verzeichnisse, Listen, Calibre-Bestände oder
anderen Formate. Beide Dateien bleiben unverändert und werden ausschließlich
aus getrennten begrenzten In-Memory-Snapshots analysiert.

## Eingangs- und Snapshotvertrag

- genau zwei erforderliche Positionsargumente, keine Globs oder automatische
  Erkennung;
- zwei verschiedene lokale, reguläre, symlink- und reparsefreie Dateien;
- je Datei höchstens 32 MiB, gemeinsam höchstens 64 MiB;
- Suffix `.epub` und bestätigte sichere EPUB/ZIP-Struktur;
- je Eingang ein stabiler Snapshot mit Größe und SHA-256; nach dem Snapshot
  wird der Originallokator nicht erneut für die Analyse geöffnet;
- instabile, wachsende, unlesbare, zu große oder strukturell unsichere
  Eingänge führen fail-closed zu `not_assessed` oder Grenzfehler;
- ZIP-Pfadtraversal, doppelte logische Namen, Verschlüsselung, Spezialfälle,
  mehr als 512 Einträge oder mehr als 128 MiB expandierte Bytes je EPUB
  werden abgelehnt.

Die vorhandene WI-0004-Preflight-Grenze bleibt vorgeschaltet. Nur zwei
einzeln positiv für tiefe read-only Analyse gegatete EPUB-Snapshots dürfen in
den Identitätsvergleich gelangen.

## Evidenzebenen

Der Bericht führt fünf getrennte Ebenen in fester Reihenfolge:

1. `byte`: Gleichheit der vollständigen Snapshot-Bytes über SHA-256;
2. `package`: Gleichheit einer kanonischen Projektion aus logischem
   ZIP-Eintragsnamen, Größe und Inhaltshash, unabhängig von ZIP-Reihenfolge
   und Containerzeitstempeln;
3. `representation`: Vergleich von Manifest-/Spine-Struktur und
   normalisiertem sichtbarem XHTML-Inhalt in Lesereihenfolge;
4. `edition`: vorsichtige Evidenz aus Titeln, Urhebern, Sprachen und
   Identifikatoren der eingebetteten OPF-Metadaten;
5. `work`: ausschließlich explizite Werkreferenzen und klar getrennte
   Ausgabe-/Übersetzungsindizien.

Jede Ebene enthält:

- eine Entscheidung aus `candidate_same`, `candidate_related`, `different`,
  `abstain` oder `not_applicable`;
- getrennte positive, negative und fehlende Evidenzcodes;
- eine kurze begründende Regel-ID;
- keine Konfidenzzahl, wenn kein empirisch kalibriertes Modell existiert.

Fehlende Evidenz ist nicht negativ. Gleicher Titel allein erzeugt keinen
Werk- oder Ausgabekandidaten. Leseprobe und Vollausgabe dürfen nicht als
gleiche Ausgabe freigegeben werden; Übersetzungen dürfen nicht als
austauschbare Ausgabe erscheinen. Bytegleichheit verschmilzt weder Quellen
noch Locators. Ein Ebenenkandidat löst keine automatische Gesamtaussage oder
Bestandsaktion aus.

## Ausgabe- und CLI-Vertrag

Die Implementierungs-Wave führt eine getrennte lokale Oberfläche ein:

```text
python tools/run_ebook_identity.py DATEI_1.epub DATEI_2.epub
python tools/run_ebook_identity.py --json DATEI_1.epub DATEI_2.epub
```

Die deutsche Ansicht und JSON erscheinen ausschließlich auf stdout. Die
JSON-Schema-ID lautet `sammlungslotse/ebook-identity-candidate-report/v1`.
Eingänge werden nur als Position `1` und `2` bezeichnet; Pfade und Dateinamen
erscheinen weder in Ergebnis noch Diagnose. Zwei Läufe über dieselben stabilen
Snapshots müssen byteidentisches JSON erzeugen.

Der Bericht darf Snapshot-Hash und -Größe, abgeleitete kanonische Digests,
minimale eingebettete Metadaten und Evidenzcodes enthalten. Diese Werte
können private Sammlungs- oder Inhaltsinformation sein und werden weder
protokolliert noch persistiert.

Prozesscodes:

- `0` für einen vollständig bewerteten Paarbericht, auch wenn einzelne
  Ebenen `abstain` oder `not_applicable` melden;
- `4` für `not_assessed`, insbesondere bei nicht positivem Preflight oder
  unvollständiger sicherer Analyse;
- `3` für verletzte Ressourcen-, Struktur- oder Ausgabegrenzen sowie
  unerwartete interne Fehler;
- `130` für ausdrückliche Unterbrechung ohne Restdaten.

## Architektur- und Wirkungsgrenze

Der Anwendungskern erhält ausschließlich zwei unveränderliche Snapshot-
Verträge. EPUB-/ZIP- und OPF-Details enden in einem lokalen
Standardbibliotheksadapter. Modell und Ausgabe enthalten nur pfadfreie
Beobachtungen, Digests und Evidenzentscheidungen.

Die Implementierung darf Python 3.12 und ausschließlich die
Standardbibliothek verwenden. Sie erzeugt keine Arbeitsdatei, keinen Cache,
keinen Index und keinen Container. Calibre, EPUBCheck und andere Provider
werden nicht aufgerufen.

## Akzeptanzkriterien

WI-0009 ist erst `done`, wenn:

1. genau zwei verschiedene explizite EPUB-Dateien akzeptiert werden;
2. beide Eingänge getrennt stabil, begrenzt und unveränderlich gesnapshottet
   werden;
3. die vorhandene Preflight-Grenze beide Snapshots positiv gattet;
4. ZIP-, Expansion-, Eintrags-, Pfad-, Duplikat- und Verschlüsselungsgrenzen
   fail-closed wirken;
5. Byte-, Paket-, Repräsentations-, Ausgabe- und Werkebene getrennt bleiben;
6. positive, negative und fehlende Evidenz sowie Enthaltung maschinenlesbar
   getrennt sind;
7. Bytegleichheit, Neuverpackung, Titelkollision, Übersetzung,
   Leseprobe/Vollausgabe und fehlende Metadaten korrekt behandelt werden;
8. deutsche und JSON-Ausgabe keine Pfade, Dateinamen, Rohbytes oder
   unerlaubten Diagnosen enthalten;
9. JSON-Sortierung und Wiederholung byteidentisch sind;
10. Originale vor und nach tatsächlichen CLI-Läufen bytegleich bleiben und
    keinerlei Netzwerk-, Fachsystem- oder Dateisystemschreibwirkung entsteht;
11. mindestens zwei semantisch identische Wiederholungen über die gebundenen
    TEST-0001-Identitätspaare den erwarteten Ebenenentscheidungen entsprechen;
12. False Positives in den gebundenen negativen Fällen null sind und perfekte
    synthetische Werte nicht als Realbestandsprognose dargestellt werden;
13. Registry-, Dokument-, Fixture-, Experiment-, WI-0005-, WI-0008-,
    Produkt-, Foundation-, `compileall`- und `git diff --check`-Regression
    erfolgreich sind;
14. Projektstatus und Übergabe die tatsächliche enge Qualifikation und
    Restgrenzen wiedergeben.

## Nichtziele

Nicht Bestandteil sind mehr als zwei Dateien, Verzeichnissuche, PDF, MOBI,
AZW3 oder andere Formate, Vergleich mit Calibre, mehrere Bibliotheken,
persistente Kandidaten, Index, Volltextsuche, statistische Ähnlichkeit,
externe Metadaten, KI-Modelle, Routing, Browser, REST, Agents, Import,
Löschen, Formatentfernung, Verschieben, Umbenennen, Metadatenänderung oder
sonstige Writes.

## Ausführungsreihenfolge

1. GATE-0005 und diesen angenommenen Vertrag ohne Produktcode nach
   `origin/main` mergen.
2. Modell, Snapshot-Komposition, sicherer EPUB-Adapter, Evidenzregeln,
   getrennte CLI und automatisierte Verträge in einer eigenen
   Implementierungs-Wave ergänzen.
3. Synthetische tatsächliche CLI-Wiederholungen und vollständige Regression
   ausführen.
4. Erst nach exakten erforderlichen GitHub-Checks mergen und WI-0009 auf
   `done` setzen.

Die Benutzeranweisung vom 2026-08-28 autorisiert die autonome Fortsetzung
über Planung, Registrierung, ausschließlich synthetische Implementierung und
Abnahme, Pull Requests, exakte CI-Prüfung und Merge nach `origin/main`.

## Umsetzung und Ergebnis

Der Vertrag ist unter `src/sammlungslotse/ebook_identity/` umgesetzt. Die
getrennte Oberfläche liegt unter `tools/run_ebook_identity.py`; sie verwendet
den vorhandenen stabilen Snapshot- und Preflight-Vertrag, hält ZIP-/OPF-
Parsing im lokalen Adapter und gibt ausschließlich den pfadfreien
Anwendungsvertrag aus.

Der eingecheckte Nachweis unter `runtime/ebook-identity/qualification.json`
bindet das vollständige Produktpreimage und fünf TEST-0001-Paare. Je zwei
tatsächliche JSON-CLI-Läufe sowie eine deutsche Ansicht bestanden 16/16
Kriterien. Bytegleichheit, Neuverpackung, Titelkollision, Übersetzung und
Leseprobe/Vollausgabe blieben auf den fünf Ebenen getrennt; die gebundenen
Negativfälle erzeugten keinen falschen Gleichheitskandidaten. Fixture-Hashes
blieben unverändert, sämtliche Produktwirkungen auf Netzwerk, Dateisystem,
Fachsysteme und Originale waren `false`.

Die Qualifikation gilt ausschließlich für die kleinen synthetischen Paare.
Sie ist keine Aussage über Genauigkeit oder Recall in realen Beständen und
autorisiert keine automatische Zusammenführung oder andere Bestandsaktion.
