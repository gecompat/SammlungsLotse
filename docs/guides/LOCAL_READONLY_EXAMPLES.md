# Lokale read-only-Beispiele

Diese Anleitung richtet sich an Personen, die die vorhandenen E-Book-Verträge
mit ausdrücklich gewählten, synthetischen Eingängen kennenlernen wollen. Sie
startet keine Hintergrundsuche, schreibt keine Berichte und übernimmt keine
angezeigte Folgeaktion. Eine vollständige Medienlinie oder freigegebene
Verarbeitung privater Sammlungen folgt daraus nicht.

## Vorbereitung

Arbeite im Repository-Root mit einer verfügbaren Python-Laufzeit. Für die
einfachen Beispiele sind die eingecheckten synthetischen TEST-0001-Fixtures
ausreichend; zusätzliche Downloads oder eine Calibre-Installation sind dafür
nicht nötig. Prüfe bei einer anderen Python-Version die tatsächliche
Kompatibilität für den gewählten Vertrag; die ursprüngliche Python-3.12-Wahl
war auf den WI-0004-Prototyp begrenzt.

## Eingangstriage ansehen

Der erste Befehl zeigt eine lesbare Folgeaktion oder Enthaltung für genau ein
synthetisches EPUB. Der zweite liefert denselben read-only-Vertrag als JSON:

    python tools/run_ebook_intake.py tests/fixtures/ebook/test-0001/v0.3/cases/ingress-stable-minimal/stable.epub

    python tools/run_ebook_intake.py --json tests/fixtures/ebook/test-0001/v0.3/cases/ingress-stable-minimal/stable.epub

Mehrere ausdrücklich gewählte Dateien erzeugen einen gemeinsamen,
positionsgebundenen und pfadfreien Bericht:

    python tools/run_ebook_intake.py --json DATEI_A DATEI_B

Ein ausdrücklich gewählter lokaler Ordner kann rekursiv und read-only
inventarisiert werden. Nur reguläre EPUB- und PDF-Dateien innerhalb der
32-Kandidaten- und 256-MiB-Grenze werden erfasst; die Standardausgabe bleibt
pfad- und namensfrei:

    python tools/run_ebook_intake.py --input-directory ORDNER

Relative lokale Dateilabels erscheinen nur durch ausdrückliches Human-Opt-in
und nie im JSON-Vertrag:

    python tools/run_ebook_intake.py --show-local-labels --input-directory ORDNER

Die schnelle Prüfung ist Standard. Der Ordnermodus startet keine tiefe
Prüfung. `--deep-read-only` ist nur für explizite Dateieingänge vorgesehen und
benötigt einen zuvor konfigurierten WI-0005-Task-Root. Der Lauf verändert
weder Eingänge noch Zielbestände.

## Getrennte Bestands- und Identitätsansichten

Die Calibre-Bestandsprojektion benötigt ein vorab bereitgestelltes, exakt
gebundenes lokales Profil. Sie verarbeitet genau eine ausdrücklich angegebene
Bibliothek über eine wegwerfbare Copy-on-read-Arbeitskopie. Details zur
Bereitstellung und zu ihren Sicherheitsgrenzen stehen im
[read-only-Calibre-Arbeitsgegenstand](../planning/CALIBRE_READ_ONLY_PROJECTION_WORK_ITEM.md).
Nach dessen Vorbereitung lauten die bestehenden Beispielaufrufe:

    python tools/provision_calibre_readonly_profile.py --cache-root C:\rep\cache\SammlungsLotse\calibre-readonly

    python tools/run_calibre_inventory.py --json --temp-root C:\rep\tmp\SammlungsLotse\calibre-readonly CALIBRE_BIBLIOTHEK

Die stdout-Ausgabe enthält Calibre-ID, Titel, Autoren, Sprachen und Formate.
Sie kann private Metadaten enthalten und wird nicht persistiert. Mehrere
Bibliotheken, automatische Erkennung, Content Server und schreibende
Calibre-Operationen bleiben außerhalb dieses Vertrags.

Zwei ausdrücklich ausgewählte EPUB-Dateien lassen sich getrennt read-only auf
fünf Identitätsebenen vergleichen:

    python tools/run_ebook_identity.py --json DATEI_1.epub DATEI_2.epub

Der Bericht bezeichnet Eingänge nur als Position 1 und 2. Positive, negative
und fehlende Evidenz bleiben getrennt; Enthaltung ist sichtbar. Der Vergleich
sucht keine Dateien, fragt Calibre nicht ab und löst keine Bestandsaktion aus.

## Ergebnis und Abweichungen

Ein Bericht ist eine begründete Empfehlung oder Enthaltung, keine ausgeführte
Bestandsänderung. Die kanonischen [Produktgrenzen](../architecture/BOUNDARIES.md)
und die [Validierungswege](../governance/VALIDATION.md) erklären, was darüber
hinaus tatsächlich qualifiziert wurde. Bei fehlendem Profil, nicht
unterstützter Eingabe oder einer Sicherheitsablehnung den im Bericht genannten
Grund prüfen; keinen Bestandsimport oder eine tiefe Prüfung daraus ableiten.
Für Entwicklung und reproduzierbare Prüfungen gilt [CONTRIBUTING.md](../../CONTRIBUTING.md).
