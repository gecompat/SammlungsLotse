# WI-0016: Read-only E-Book-Eingangsordner transparent erfassen

Status: DONE — IMPLEMENTIERT UND SYNTHETISCH ABGENOMMEN

Stand: 2026-09-04

Artifact: WI-0016

## Zweck

Dieser angenommene Arbeitsgegenstand bildet den ersten sichtbaren
Eingangsablauf über einen ausdrücklich gewählten lokalen E-Book-Ordner vor.
Er verbindet die vorhandene Einzel- und Mehrdatei-Triage zu einer für einen
Menschen nachvollziehbaren, weiterhin rein read-only Ordnerübersicht. Er
macht aus einem Ordner weder eine Bibliothek noch einen verwalteten Bestand.

Die Annahme autorisierte ausschließlich die Implementierungswave innerhalb
dieses Vertrags. Sie wählt weder eine allgemeine Produktarchitektur
noch Persistenz, Suche, Routing, Calibre-Zugriff oder einen Writer.

## Kleinster Nutzwert

Eine Person wählt genau einen lokalen Eingangsordner aus und erhält eine
begrenzt vollständige Übersicht darüber,

- wie viele reguläre EPUB- und PDF-Eingänge gefunden wurden;
- welche innerhalb der bestehenden Triagegrenzen geprüft werden konnten;
- welche Eingänge `review`, `stop`, `abstain` oder `unsupported` benötigen;
- ob die fest gebundene Ordner- oder Bytegrenze eine vollständige Prüfung
  verhindert hat.

EPUBs verwenden unverändert die bestehende WI-0004-/WI-0006-Triage. PDF wird
sichtbar als nicht unterstütztes Format geführt; dieser Arbeitsgegenstand
führt keine PDF-Inhalts- oder Qualitätsprüfung ein. Identitäts-, Dubletten-,
Metadaten- und Routingkandidaten bleiben außerhalb.

## Vorgeschlagener Ablauf

```text
ausdrücklich gewählter lokaler Ordner
  -> begrenzte rekursive Inventarisierung ohne Linkverfolgung
  -> deterministische Auswahl regulärer EPUB- und PDF-Eingänge
  -> bestehende sequenzielle read-only Triage
  -> lokale Übersicht, Review und Enthaltung
```

Die Oberfläche soll ausschließlich eine Erweiterung von
`tools/run_ebook_intake.py` sein. Ein möglicher späterer Vertrag lautet:

```text
python tools/run_ebook_intake.py --input-directory ORDNER
python tools/run_ebook_intake.py --show-local-labels --input-directory ORDNER
```

Die erste Variante bleibt pfad- und namensfrei. Die zweite Variante wäre ein
ausdrücklicher lokaler Human-Opt-in: Sie darf nur relative Labels zum gewählten
Ordner auf stdout zeigen, niemals absolute Pfade, JSON-Werte, Logs, Caches,
Berichtsdateien, Netzwerkdaten oder Git-Inhalte erzeugen. Der lokale Nutzer
entscheidet damit bewusst, ob die Positionsberichte mit privaten
Dateibezeichnungen verknüpft werden.

## Feste Schutz- und Ressourcenabsicht

Eine Annahme dieses Arbeitsgegenstands bindet mindestens folgende Grenzen:

- genau ein expliziter lokaler Ordner; kein Default, keine Globs, kein
  Watcher und keine konfigurations- oder umgebungsgetriebene Entdeckung;
- rekursive Erfassung nur regulärer Dateien; symbolische Links, Reparse Points
  und nicht reguläre Dateisystemobjekte werden nicht verfolgt;
- höchstens 32 EPUB- oder PDF-Eingänge und höchstens 256 MiB summierte
  Snapshot-Bytes, entsprechend den bestehenden WI-0006-Batchgrenzen;
- stabile deterministische Reihenfolge; bei Überschreitung keine teilweise
  versteckte Auswahl und kein tiefer Werkzeuglauf;
- der tiefe EPUBCheck-Weg bleibt ein bestehendes explizites Opt-in und startet
  nie wegen der Ordnerauswahl allein;
- keine Netzwerk-, Persistenz-, Fachsystem-, Datei- oder Bestandswirkung und
  kein neues Containerprofil; insbesondere kein Verschieben, Umbenennen,
  Importieren, Extrahieren oder Metadatenschreiben;
- keine tatsächlichen privaten Ordner, Dateinamen, Pfade, Hashes, Inhalte oder
  Rohberichte als Repository-, Test-, PR- oder dauerhaftes Artefakt.

Eine spätere reale Ausführung außerhalb der verbindlichen Projektpfade
erfordert eine eigene ausdrückliche Run-Freigabe. Die Implementierung und
synthetische Abnahme bleiben davon getrennt.

## Akzeptanzkriterien für eine spätere Implementierungswave

WI-0016 wäre erst `done`, wenn:

1. WI-0016 vor Produktcode ausdrücklich als `accepted` auf `origin/main`
   registriert ist.
2. Genau ein expliziter Ordner ohne Linkverfolgung rekursiv und mit festen
   Grenzen inventarisiert wird; fehlende, nicht zugängliche oder instabile
   Eingänge bleiben sichtbar und fail-closed.
3. Die bestehende Einzel- und Mehrdatei-CLI ohne `--input-directory` byte- und
   bedeutungsgleich bleibt.
4. EPUB und PDF getrennt gezählt und positionell berichtet werden; PDF wird
   nicht über einen neuen Parser geöffnet oder als EPUB behandelt.
5. Anzahl-, Byte-, Link-, Reparse- und Laufzeitgrenzen verhindert jede
   verdeckte Teilverarbeitung sowie jeden automatischen tiefen Werkzeuglauf.
6. Die Standardausgabe und jeder JSON-Vertrag weiterhin keine lokalen Pfade,
   Dateinamen oder relativen Locators enthalten. Der optionale Human-Opt-in
   zeigt nur relative Labels, schreibt nichts und wird gesondert getestet.
7. Der Ablauf bleibt sequenziell, deterministisch und vollständig read-only;
   Netzwerk-, Persistenz-, Original-, Fachsystem- und sonstige
   Dateischreibwirkungen sind null.
8. Ausschließlich synthetische Fixtures belegen positive und negative
   Erfassung, Grenzen, Enthaltung, Datenschutz und unveränderte Originale.
9. Projekt-, Registry-, Produkt- und Fixture-Regressionen sowie `compileall`
   und `git diff --check` sind tatsächlich erfolgreich; Projektstatus,
   Übergabe und CLI-Dokumentation zeigen die verbleibenden Grenzen an.

## Nichtziele

Nicht Bestandteil sind eine allgemeine Medienlinie, vollständige
Verzeichnissuche, PDF-Analyse, Dublettensuche, Werk- oder Ausgabenentscheidung,
Metadatenanreicherung, Calibre-Integration, Browser, REST, Agents,
Persistenz, Index, Hintergrundverarbeitung, Quarantäne oder irgendeine
schreibende Operation.

## Implementierung und synthetische Abnahme

Die sichtbare Oberfläche bleibt `tools/run_ebook_intake.py`. Der neue Modus
ist ausschließlich über einen expliziten Ordnerparameter erreichbar:

```text
python tools/run_ebook_intake.py --input-directory ORDNER
python tools/run_ebook_intake.py --show-local-labels --input-directory ORDNER
```

Der Produktcode erfasst genau einen regulären, nicht verlinkten und nicht als
Reparse Point markierten Ordner rekursiv. Er nimmt nur reguläre `.epub`- und
`.pdf`-Dateien in eine stabile relative Reihenfolge auf. Bei einer
Kandidatenüberschreitung markiert der Bericht das Inventar ausdrücklich als
nicht vollständig. Vor jeder Triage
stoppt er ohne versteckte Teil-Auswahl, wenn mehr als 32 Kandidaten oder mehr
als 256 MiB deklarierte Eingangsbytes vorliegen. Die Snapshot-Summe wird beim
Lesen erneut begrenzt. Nicht zugängliche Ordner, Link-/Reparse-Eingänge und
instabile einzelne Dateien bleiben über pfadfreie Status- beziehungsweise
Triagecodes sichtbar und führen nicht zu einer Schreibwirkung.

Der Standardbericht enthält nur Zähler, Positionen und die bestehenden
pfadfreien Einzelberichte. `--show-local-labels` ist ein Human-Opt-in für
relative Labels auf stdout; er ist mit JSON unvereinbar. Der Ordnermodus
startet keinen tiefen Werkzeuglauf; der vorhandene `--deep-read-only`-Weg
bleibt für die bisherigen expliziten Dateieingänge getrennt.

Ausschließlich synthetische Produktverträge prüfen die rekursive EPUB/PDF-
Erfassung, Zähler, Positionsfolge, fehlende Ordner, Link-Sperre,
Kandidaten- und Bytegrenzen, die unveränderte Standardausgabe, den lokalen
Label-Opt-in, die fehlende Tiefenautomatik und unveränderte Originale.
Weil die gemeinsame CLI erweitert wurde, ist auch das bestehende
WI-0005-EPUBCheck-Profil mit denselben synthetischen Eingängen erneut
qualifiziert: 12/12 Kriterien, `network=none`, entfernter Container und
bereinigter Timeout-Task. Es wurde kein neuer Containervertrag eingeführt.

## Annahmeentscheidung

Am 2026-09-04 ausdrücklich angenommen. Der lokale Label-Opt-in, die festen
Ordnergrenzen und der Nutzen gegenüber der bestehenden expliziten
Mehrdatei-CLI sind damit für diese Wave bestätigt. Die Annahme autorisiert
ausschließlich die hier beschriebene read-only Implementierungswave; reale
private Eingänge, weitere Formate und jede Bestandswirkung bleiben getrennte
Entscheidungen.
