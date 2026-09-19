# WI-0019: Ephemeren read-only E-Book-Reviewplan umsetzen

Status: DONE

Stand: 2026-09-19

Artifact: WI-0019

## Zweck

WI-0019 verbindet genau einen ausdrücklich ausgewählten lokalen
E-Book-Eingangsordner mit genau einer ausdrücklich ausgewählten lokalen
Calibre-Bibliothek zu einem deterministischen, ephemeren und read-only
Reviewplan. Der Plan unterstützt ausschließlich die manuelle Prüfung. Er
schreibt weder in den Eingang noch in die Bibliothek und trifft keine
Dublett-, Neuheits-, Ziel- oder Importentscheidung.

## Vertrag

- Der Eingangsordner wird ausschließlich über die bestehenden WI-0016-
  Grenzen inventarisiert: reguläre EPUB- und PDF-Eingänge, keine Link- oder
  Reparse-Point-Verfolgung, höchstens 32 Kandidaten und 256 MiB.
- Die Calibre-Bibliothek wird ausschließlich über die bestehende WI-0007-
  Copy-on-read-Projektion gelesen. Ein nicht erfolgreich abgeschlossener,
  veränderter oder nicht bereinigter Projektionslauf erzeugt keinen
  Reviewplan.
- Jeder inventarisierte Eingang erhält genau eine pfadfreie Planposition mit
  einer sichtbaren Reviewklasse. Nicht-EPUBs, Ingress-Reviewfälle,
  unvollständige Inventare und nicht beurteilbare Zustände bleiben
  fail-closed sichtbar.
- Für EPUBs mit offenem Ingress-Gate entstehen höchstens fünf deterministische
  Kandidaten aus Titel-, Autoren- und Sprachgleichheit gegen die eine
  Projektion. Kandidaten enthalten nur anonyme Position, externe Calibre-ID,
  Grundstrategie und anonyme Projektionsprovenienz.
- Ein fehlender, begrenzter oder vorhandener Kandidat beweist weder
  Vollständigkeit noch Same, New, Target oder Import. Kandidaten ändern weder
  die bestehende fünfstufige Identitätsbewertung noch das Deep-Read-Gate.
- Der öffentliche JSON- und Human-CLI-Vertrag wird als neuer, separater
  Befehl eingeführt; vorhandene Intake-, Calibre- und Identitäts-CLIs bleiben
  bytekompatibel. Ausgabe ist begrenzt, stabil und frei von lokalen Pfaden,
  Dateinamen, privaten Medieninhalten und unverhältnismäßigen Rohdaten.

## Ausdrücklich außerhalb

Import, Verschieben, Umbenennen, Löschen, Metadatenschreiben, Persistenz,
Index, Berichtdatei, Watcher, Netzwerk, automatische Bibliotheksentdeckung,
mehrere Bibliotheken, Zielwahl, Browser, REST und Agents sind nicht Teil von
WI-0019.

## Akzeptanzkriterien

1. Synthetische Tests belegen den vollständigen begrenzten Einzelbibliothek-
   Ablauf, deterministische Ausgabe, Kandidatengrenzen, fail-closed Klassen,
   Pfadfreiheit und die Unverändertheit von Eingang und Quelle.
2. Nicht beurteilbare Calibre-Projektionen, Ingress-Reviews, PDFs,
   Inventargrenzen und interne Fehler erzeugen keinen Kandidaten- oder
   Importhinweis.
3. Die bestehende WI-0016-, WI-0007- und Identitätsfunktionalität bleibt
   unverändert; der neue Befehl benötigt weder Netzwerk noch eine Schreib-
   oder Bestandswirkung.
4. Die betroffenen Governance-, Registry- und Projekttests sind tatsächlich
   erfolgreich; Status und Übergabe beschreiben den erreichten Zustand.

## Ergebnis

Die getrennte Produktwave ist abgeschlossen. Der neue Befehl
`tools/run_ebook_review_plan.py` verbindet ausschließlich die bestehende
Ordnerinventur mit der Copy-on-read-Projektion einer expliziten Bibliothek.
Fünf fokussierte synthetische Tests belegen Kandidatengrenze,
Determinismus, Pfadfreiheit und die geschlossenen Fehlerpfade. Die vollständige
lokale Python-3.13-Prüfung führte 277 Tests erfolgreich aus (vier
fähigkeitsbedingte Symlink-Skips). Netzwerk, Persistenz, Import, Writer und
Bestandswirkung bleiben außerhalb.
