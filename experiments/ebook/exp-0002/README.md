# EXP-0002: Read-only Calibre-Bestandsprojektion

Status: AUSGEFÜHRT — PASS

Stand: 2026-08-27

## Ergebnis

Calibre `9.13.0` wurde unter Podman gegen zwei ausschließlich synthetisch
materialisierte Bibliotheken ausgeführt. Alle dreizehn Akzeptanzprüfungen in
[result.json](result.json) sind erfolgreich. Die zwei Wiederholungsläufe je
Ziel erzeugten jeweils dieselbe semantische Projektion; Custom Columns,
fehlende Werte, Pagination und unbekannte Felder blieben sichtbar. Die
Standardprojektion enthält weder absolute Bibliothekspfade noch interne
Calibre-Tabellen.

Das Experiment qualifiziert keinen Produktadapter. Es belegt einen engen,
wegwerfbaren Zugriffspfad für genau Calibre `9.13.0` und TEST-0001 `0.2.0`.

## Entscheidender Negativbefund

Ein direkter read-only Bind-Mount der lokalen Bibliothek ist mit
`calibredb list` nicht funktionsfähig. Calibre prüft beim Öffnen die
Groß-/Kleinschreibung des Bibliotheksdateisystems über die temporäre Datei
`calibre_test_case_sensitivity.txt`; unter einem read-only Mount endet dies
reproduzierbar mit `EROFS`.

Der erfolgreiche lokale Versuch verwendet deshalb eine explizite
Copy-on-read-Grenze:

1. Der synthetische Quell-Snapshot wird vor dem Leselauf gehasht.
2. Für jeden Wiederholungslauf entsteht eine neue wegwerfbare Arbeitskopie.
3. Nur diese Kopie wird für Calibre schreibbar eingehängt.
4. Quell-Snapshot und Arbeitskopie werden nach dem Lauf erneut gehasht.

Alle Vorher-/Nachher-Digests waren identisch. Eine spätere Architektur darf
diesen Befund nicht als Eignung eines direkten read-only Calibre-Mounts
umdeuten.

## Werkzeug- und Ausführungsprofil

- Profil `exp-0002-podman-calibre-9.13.0/v1`;
- Calibre `9.13.0`, GPL-3.0-only, offizielles Linux-Artefakt mit SHA-512
  `c018cb47805040a9a83dc16986db618c539a7dc62f85da2760b7e22e0e8ada7533a01be797cdbd04a5d5f66c8efa2b0ac2db4819700e561351267cb4842a3fc6`;
- digest-gepinnte Python-Basis für den wegwerfbaren Versuch;
- Podman `6.1.0`, Linux/amd64, unprivilegierter Benutzer `65532:65532`;
- read-only Root, keine hinzugefügten Capabilities, `no-new-privileges` und
  `network=none`;
- 64 Prozesse, eine CPU, 1 GiB Speicher ohne zusätzlichen Swap, 30 Sekunden
  Laufzeitgrenze und 1 MiB Dateigrößenlimit;
- minimierte, vollständig im Profil erlaubte Prozessumgebung.

Der Image-Build ist der einzige Schritt mit Netzabruf. Er prüft das offizielle
Calibre-Artefakt gegen den fest hinterlegten SHA-512-Wert. Die Lizenzquelle
wird getrennt festgehalten, weil das Binärarchiv keine Top-Level-Lizenzdatei
enthält. Die eigentlichen Bibliotheksläufe sind netzwerklos.

Primärquellen:

- [Calibre 9.13.0](https://download.calibre-ebook.com/9.13.0/);
- [offizielle Calibre-Signaturen](https://calibre-ebook.com/signatures/);
- [calibredb-Handbuch](https://manual.calibre-ebook.com/generated/en/calibredb.html);
- [Calibre-Lizenzhinweis](https://manual.calibre-ebook.com/develop.html).

## Empirische Befunde

| Vertrag | Beobachtung |
|---|---|
| getrennte Ziele | `technical-library` und `young-readers-library` bleiben getrennt |
| minimale Projektion | Titel, Autoren, Sprachen, Tags, Identifikatoren, Formate und genau eine freigegebene Custom Column |
| Wiederholbarkeit | beide Projektionen je Ziel haben denselben semantischen SHA-256-Digest |
| unbekanntes Feld | `not_registered` wird sichtbar als `unsupported` klassifiziert |
| Pfadgrenze | rohe breite Formatfelder enthalten `/library/`; die Standardprojektion enthält nur Formaterweiterungen |
| Quellzustand | beide Quellbibliotheken bleiben über direkten Negativtest und erfolgreiche Copy-on-read-Läufe bytegleich |
| Arbeitskopie | auch die wegwerfbaren Kopien sind nach dem Calibre-Lauf bytegleich; ein temporärer Schreibversuch bleibt dennoch Voraussetzung |

Unveränderte maschinenlesbare Rohantworten liegen nur im lokalen
Artifact-Bereich. `result.json` enthält ihre Hashes und bereinigte
Projektionen, jedoch keine privaten Hostpfade.

## Grenzen

Der Content-Server-Zugang wurde nicht ausgeführt. Das Ergebnis gilt nur für
kleine synthetische Bibliotheken, nicht für private oder große reale
Sammlungen. Calibre meldet über `calibredb --version` verkürzt `9.13`; der
geprüfte Archiv-Hash bindet den Versuch an das Release `9.13.0`. Andere
Versionen bleiben ohne neues Profil `unsupported`.

## Reproduktion

Der vollständige lokale Provisionierungs- und Experimentlauf lautet:

    python tools/experiments/run_exp_0002.py

CI lädt Calibre nicht und startet keinen Container. Sie prüft den
eingecheckten Ergebnisvertrag:

    python tools/experiments/run_exp_0002.py --validate-result
