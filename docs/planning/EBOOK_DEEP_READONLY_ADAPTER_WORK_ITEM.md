# WI-0005: Ersten tiefen read-only Werkzeugadapter begrenzen

Status: ACCEPTED — VERTRAG FESTGELEGT, NOCH NICHT IMPLEMENTIERT

Stand: 2026-08-27

Artifact: WI-0005

## Entscheidung

WI-0005 wird als nächster eng begrenzter Produktarbeitsgegenstand angenommen.
Der erste Provider ist EPUBCheck 5.3.0. Er wird ausschließlich als
austauschbarer lokaler Prozessadapter hinter einer providerneutralen
Produktgrenze vorgesehen. Als erster zu implementierender und zu
qualifizierender Ausführungsweg wird ein vorab bereitgestelltes,
digest-gepinntes Linux/amd64-Podman-Profil festgelegt.

Die Annahme entscheidet weder einen allgemeinen Technologie- oder
Deployment-Stack noch eine allgemeine Containerpflicht. Der Produktkern
kennt weder EPUBCheck, Java, Podman, Containerimage, Prozessbefehl noch
Dateipfade. Ein späterer nativer oder anderer isolierter Executor darf hinter
derselben Adaptergrenze ergänzt werden, muss aber zuvor eigenständig
qualifiziert werden.

Produktcode ist in dieser Bewertungs-Wave nicht entstanden. Die
Implementierung darf in einer eigenen Wave auf Basis dieses angenommenen
Vertrags beginnen.

## Aktueller Quellenbefund

Die veränderlichen Werkzeug- und Laufzeitfakten wurden am 2026-08-27 aus
aktuellen Primärquellen neu erhoben:

- Das offizielle W3C-Repository bezeichnet EPUBCheck als
  Konformitätsprüfer für EPUB-Publikationen und unterstützt eine
  Kommandozeilen- sowie eine Java-Bibliotheksschnittstelle:
  <https://github.com/w3c/epubcheck>.
- Die weiterhin aktuelle produktionsreife Veröffentlichung ist EPUBCheck
  `5.3.0`, veröffentlicht am 2025-09-01 für EPUB 3.3. Das Tag ist signiert.
  Das offizielle Release-Artefakt `epubcheck-5.3.0.zip` besitzt laut GitHub
  den SHA-256-Wert
  `6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5`:
  <https://github.com/w3c/epubcheck/releases/tag/v5.3.0>.
- EPUBCheck steht unter der BSD-3-Clause-Lizenz:
  <https://github.com/w3c/epubcheck/blob/v5.3.0/LICENSE.md>.
- Das Repository ist nicht archiviert. Offizielle Releases, offene
  Wartungs-Milestones und aktuelle Issue-Aktivität zeigen einen weiterhin
  gepflegten Upstream. Die öffentliche Repository-Advisory-Schnittstelle
  lieferte zum Stichtag keine veröffentlichten Advisories. Das ersetzt keine
  eigene Prüfung der transitiven Abhängigkeiten:
  <https://github.com/w3c/epubcheck/milestones> und
  <https://api.github.com/repos/w3c/epubcheck/security-advisories>.
- Das in EXP-0005 gebundene Temurin-Profil `21.0.12+8` ist nicht mehr die
  aktuelle Adoptium-21-LTS-Veröffentlichung. Die offizielle Releasequelle
  führt inzwischen `jdk-21.0.12.1+1`; Adoptium veröffentlicht für aktive
  Linien regelmäßig Wartungs- und Sicherheitsupdates:
  <https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1>
  und <https://adoptium.net/support/>.
- Das offizielle Ace-Repository führt `1.4.6` als aktuelle Veröffentlichung
  unter MIT-Lizenz. Ace bezeichnet sich als Accessibility-Prüfer und weist
  selbst darauf hin, dass nur ein Teil der Anforderungen automatisiert
  prüfbar ist. Zusammen mit der negativen EXP-0003-Laufzeitevidenz spricht
  das gegen die Aufnahme in diese erste Wave, nicht gegen eine spätere
  getrennte Bewertung: <https://github.com/daisy/ace>.
- GitHub Dependabot meldete beim PR-Push 11 offene Befunde, zehn `high` und
  einen `moderate`. Alle verweisen ausschließlich auf den eingefrorenen
  Ace/npm-Baum unter `experiments/ebook/exp-0003/package-lock.json`, keiner
  auf einen Produktadapter. Sie werden weder als behoben dargestellt noch
  aus dem historischen Experiment entfernt oder stillschweigend verworfen:
  <https://github.com/gecompat/SammlungsLotse/security/dependabot>.

Damit bleibt die EPUBCheck-Identität und der bereits beobachtete
Maschinenbericht verwendbar. Das frühere EXP-0005-Containerimage ist jedoch
nur historische Evidenz und kein übernehmbares Produktlaufzeitprofil.

## Bewertete Möglichkeiten

| Möglichkeit | Qualitätsbeitrag | Bindung und Risiko | Entscheidung für WI-0005 |
|---|---|---|---|
| EPUBCheck 5.3.0 als externer CLI-Prozess | etablierte EPUB-3.3-Konformitätsbefunde, maschinenlesbarer Rohbericht, bereits synthetisch erprobt | Java-Laufzeit und gepflegtes Isolationsprofil erforderlich; Befund ist keine Gesamtqualitätsaussage | angenommen |
| EPUBCheck als eingebettete Java-Bibliothek | direkter Bibliotheksaufruf | koppelt den Python-Prototyp früh an JVM-Integration und Bibliothekslebenszyklus | für die erste Wave verworfen |
| Ace 1.4.6 | zusätzliche automatisierte Accessibility-Befunde | unvollständige Automatisierung; das erprobte Profil deaktiviert die Chromium-Sandbox, hatte bekannte npm-Befunde und besitzt aktuell 11 offene Dependabot-Meldungen im eingefrorenen Experimentbaum | nicht Teil von WI-0005; neuer Vertrag und neue Qualifikation erforderlich |
| Calibre-Werkzeuge | Metadaten- und Bibliotheksnutzen | beantwortet nicht die erste tiefe EPUB-Konformitätsfrage; zusätzliche große Oberfläche | nicht Teil von WI-0005 |
| nativer Windows-Prozess | geringe lokale Bedienhürde | die geforderte netzwerklose und ressourcenbegrenzte Grenze ist noch nicht empirisch qualifiziert | später austauschbar, zunächst nicht unterstützt |
| digest-gepinntes Podman-Profil | bereits erprobte Netzwerk-, Mount-, UID-, Capability-, Prozess- und Ressourcenbegrenzung | lokale Podman-Voraussetzung und explizite Bereitstellung nötig | zuerst zu implementierender und zu qualifizierender Executor, ohne Kernkopplung |

EPUBCheck prüft EPUB-Konformität. Das Ergebnis wird weder als
Barrierefreiheitsprüfung noch als Aussage über Inhalt, Lesbarkeit,
Metadatenqualität, Authentizität oder Gesamtqualität dargestellt.

## Verbindliche Vertragsgrenze

```text
freigegebener unveränderlicher Snapshot
  -> providerneutraler DeepReadOnlyToolPort
  -> V2: task-private hashgebundene Materialisierung außerhalb des Kerns
  -> austauschbarer, begrenzter ProcessExecutor
  -> EpubCheckProvider
  -> opaker unveränderter Rohbericht plus kleine Evidenzprojektion
  -> Cleanup, Nachprüfung und Recovery
```

Der Kern übergibt nur Snapshot-Bytes, SHA-256, Größe, Freigabezustand und
eine zufällige technische Korrelationskennung. Er erhält einen
providerneutralen Ergebnisumschlag. Original-Locator, temporärer Pfad,
Containerdetail und Werkzeugcode bleiben außerhalb des Kerns.

Die Ports werden in drei getrennten Verantwortungen gehalten:

1. `DeepReadOnlyToolPort` beschreibt Anfrage und Ergebnis aus Produktsicht;
2. die V2-Materialisierung bindet Snapshot-Bytes an einen privaten Task;
3. `ProcessExecutor` begrenzt eine konfigurierte lokale Ausführung. Der
   EPUBCheck-Adapter übersetzt ausschließlich zwischen dem Rohbericht und
   der gemeinsamen Evidenzprojektion.

## Erster Provider- und Laufzeitvertrag

Die Implementierungs-Wave muss vor ihrem ersten Providerlauf einen
vollständigen, eingecheckten Preimage-Vertrag besitzen. Er bindet mindestens:

- EPUBCheck `5.3.0`, offizielles Release-Artefakt und den oben genannten
  SHA-256-Wert;
- ein zum Ausführungszeitpunkt erneut aus Primärquellen geprüftes,
  unterstütztes Temurin-LTS-Artefakt mit Version, URL und SHA-256;
- alle Container-Build-Eingänge sowie den Linux/amd64-Image-Digest;
- kanonische Argumentliste ohne Shell, feste UID/GID und leere oder explizit
  erlaubte Umgebung;
- `network=none`, read-only Root, read-only Input-Mount, getrennten begrenzten
  Outputbereich, Capability-Entzug, `no-new-privileges`, Prozess-, Zeit-,
  CPU-, RAM-, Swap-, Input-, stdout-, stderr- und Reportgrenzen;
- eine explizite EPUBCheck-JSON-Ausgabe und erwartete Provideridentität.

Podman, Image und Provider werden nicht automatisch heruntergeladen,
installiert oder aktualisiert. Fehlen sie oder weichen Version beziehungsweise
Digest ab, bleibt das Ergebnis `not_assessed` und nennt die lokale
Voraussetzung. Ein lokaler Build oder eine Bereitstellung ist ein getrennter,
bewusster Vorgang und kein Nebeneffekt der Medienprüfung.

Die dokumentierten Podman-Schalter können die erforderliche Ausführung
begrenzen; ihre tatsächliche Wirksamkeit muss für das neue exakte Profil
erneut empirisch belegt werden:
<https://docs.podman.io/en/latest/markdown/podman-run.1.html>.

## Task-, Output- und Recovery-Vertrag

- Jeder Aufruf erzeugt unter einem konfigurierbaren nicht versionierten
  SammlungsLotse-Temp-Root einen neuen privaten Taskbereich mit zufälliger
  Kennung und zufälligem Dateinamen. Produktcode kennt keinen Benutzerpfad.
- Nur die bereits freigegebenen Snapshot-Bytes werden geschrieben. Größe und
  SHA-256 werden vor dem Start und nach dem Ende des Providerprozesses
  geprüft. Der Input wird ausschließlich read-only in den Container
  eingebunden.
- Providerreport, stdout und stderr entstehen in getrennten begrenzten
  Taskausgaben. Der vollständige JSON-Rohbericht wird bytegetreu samt
  SHA-256 in den Ergebnisumschlag aufgenommen, bevor der Taskbereich entfernt
  wird. Die maschinenlesbare CLI-Ausgabe kann diesen Umschlag vollständig
  ausgeben; eine dauerhafte Ablage bleibt Sache des aufrufenden Nutzers.
- Die gemeinsame Projektion enthält nur Provider-ID und -Version,
  Profil-ID, Snapshot-SHA-256, Ausführungszustand, eng bezeichnete
  Prüfdomäne, originale Codes, originale Schweregrade, Meldungen und nur
  publikationsrelative Fundstellen. Unbekannte Codes bleiben unverändert und
  unklassifiziert.
- Erfolg ohne EPUBCheck-Fehler heißt ausschließlich
  `no_epubcheck_conformance_errors_reported`. Befunde heißen
  `epubcheck_conformance_findings`. Werkzeugausfall, Timeout, ungültiger oder
  übergroßer Bericht, Hashabweichung und Cleanupfehler heißen
  `not_assessed`; sie werden nie als Medienfehler oder Erfolg umgedeutet.
- Normaler Erfolg, Providerfehler, Timeout und Unterbrechung bereinigen den
  Taskbereich. Ein Cleanupfehler bleibt sichtbar und fail-closed.
- Ein Recovery-Sweep untersucht ausschließlich direkte Kinder des
  konfigurierten Temp-Roots. Er folgt keinen Links, prüft Eigentümermarker,
  Alter und Größenlimit, meldet unbekannte oder zu große Einträge und
  entfernt nur eindeutig eigene abgelaufene Crashreste.

## Kleinste lokale Nutzeroberfläche

Die bestehende Oberfläche `tools/run_ebook_intake.py` bleibt der einzige
lokale Einstieg. Der tiefe Lauf wird durch einen neuen, ausdrücklich
opt-in gesetzten Schalter aktiviert und nur nach
`continue_deep_read_only` gestartet. Ohne diesen Schalter bleibt das
WI-0004-Verhalten byte- und bedeutungsgleich.

Die erste Wave führt nicht ein:

- automatische Providerinstallation oder Downloads;
- Hintergrundprozesse, Watcher oder geplante Läufe;
- Browser, REST, Datenbank oder Suchindex;
- Verarbeitung mehrerer Medien oder einer Sammlung;
- native Windows-Ausführung;
- Ace, Calibre oder einen zweiten Provider;
- Writer, Import, Reparatur oder Transformation.

Die konkrete Benennung des CLI-Schalters und der Konfigurationsparameter ist
Implementierungsdetail, solange Opt-in, Abwärtskompatibilität und diese
Grenzen automatisiert geprüft werden.

## Akzeptanzkriterien der Implementierungs-Wave

WI-0005 ist erst `done`, wenn:

1. nur ein stabiler und ausdrücklich für `continue_deep_read_only`
   freigegebener Snapshot den Adapter erreicht;
2. der Kern keinen Original- oder temporären Pfad erhält;
3. jeder Task einen neuen privaten Bereich und zufälligen technischen
   Dateinamen verwendet;
4. exakt Snapshot-Bytes geschrieben und vor sowie nach dem Providerlauf
   erneut gehasht werden;
5. der Provider nur read-only auf die Materialisierung zugreift;
6. aktuelles Provider-, Laufzeit-, Build- und Image-Preimage vollständig
   gebunden und aus Primärquellen nachvollziehbar ist;
7. Befehl, UID, Umgebung, Netzwerk, Kindprozesse, Zeit, CPU, RAM, Swap,
   Input, stdout, stderr und retained output wirksam begrenzt sind;
8. Erfolg, Fehler, Timeout und Unterbrechung den Taskbereich bereinigen;
9. Crashreste beim nächsten Recovery-Lauf sichtbar, größenbegrenzt und
   sicher entfernbar sind;
10. der vollständige Werkzeugrohbefund provenienzgebunden im zurückgegebenen
    Ergebnis erhalten bleibt;
11. die gemeinsame Evidenzprojektion unbekannte Werkzeugcodes verlustfrei
    bewahrt und keine Gesamtqualitätsaussage erzeugt;
12. Werkzeugausfall, ungültiger Bericht, Hashabweichung und Cleanupfehler
    fail-closed als `not_assessed` enden;
13. synthetische positive, negative, Timeout-, Output-, Hash-, Prozess-,
    Cleanup- und Recovery-Fälle auf Windows sowie am gewählten
    Linux/Podman-Rand ausführbar sind;
14. ein tatsächlicher CLI-End-to-End-Lauf den unveränderten Standardweg, den
    Opt-in-Erfolgsweg, den Befundweg und `not_assessed` sichtbar belegt;
15. kein reales oder privates Medium für Entwicklung oder Abnahme nötig ist;
16. kein Writer, Import, Transformation, dauerhafter Produktspeicher oder
    Fachsystemzugriff entsteht;
17. V1 oder ein anderer Executor später innerhalb der Adaptergrenze ergänzt
    werden kann, ohne den Kernvertrag oder den V2-Standard zu ändern.

## Ausstieg und Neubewertung

Die Implementierungs-Wave wird pausiert oder erneut gehärtet, wenn kein
aktuelles Laufzeitpreimage unter den gebundenen Grenzen reproduzierbar gebaut
und empirisch qualifiziert werden kann, der Providerbericht nicht verlustfrei
begrenzt werden kann oder die erforderliche Isolation auf dem Zielsystem
nicht wirksam ist. WI-0004, EXP-0007 und GATE-0003 bleiben dann unverändert
gültig; es entsteht kein Ersatzprovider durch stillschweigende Ausweitung.

Providerwechsel, Versionssprung, natives Windows-Profil, zweiter Provider,
persistente Reports oder eine neue Nutzeroberfläche benötigen jeweils eine
getrennte Neubewertung. Damit bleibt die Entscheidung reversibel und
manövriert weder Kern noch Produktlinie in die erste technische Lösung ein.
