# WI-0005: Ersten tiefen read-only Werkzeugadapter begrenzen

Status: PROPOSED — NICHT ZUR IMPLEMENTIERUNG ANGENOMMEN

Stand: 2026-08-27

Artifact: WI-0005

## Ziel

WI-0005 soll einen ersten tiefen read-only Werkzeugadapter so begrenzen, dass
der unveränderliche WI-0004-Snapshot über die an GATE-0003 ausgewählte
V2-Naht verarbeitet werden kann, ohne Originalpfad, Produktkern,
Fachsystembestand oder allgemeine Produktarchitektur an ein konkretes
Werkzeug zu koppeln.

Dieser Gegenstand ist nur vorgeschlagen. Weder Produktimplementierung noch
die Auswahl eines konkreten Providers sind damit freigegeben.

## Vorläufige Vertragsgrenze

```text
freigegebener unveränderlicher Snapshot
  -> providerneutraler Handoff-Port
  -> aufgabeneigene hashgebundene Materialisierung außerhalb des Kerns
  -> begrenzter read-only Providerprozess
  -> unveränderter Rohbefund plus minimierte Evidenzprojektion
  -> Cleanup und Nachprüfung
```

Der Kern kennt nur Snapshot-Bytes, SHA-256, Größe, Freigabezustand und eine
technische Korrelationskennung. Er kennt weder Original-Locator noch
temporären Pfad, Prozessbefehl, Containerdetail oder Werkzeugcode.

## Vor einer Annahme zu entscheiden

1. Welcher gepflegte Fachwerkzeugkandidat den ersten Produktnutzen mit der
   kleinsten zusätzlichen Abhängigkeit liefert.
2. Ob dessen aktuelle Primärquellen, Lizenz, Wartungsstand, Offlineverhalten,
   Schnittstelle und reproduzierbare Version die Übernahme rechtfertigen.
3. Ob der erste Adapter nativ, in einem vorhandenen isolierten Laufzeitprofil
   oder hinter einem austauschbaren Prozessport ausgeführt wird.
4. Welche Rohbefunde unverändert erhalten bleiben und welche kleine
   providerneutrale Evidenzprojektion der gemeinsame Vertrag benötigt.
5. Wo Taskbereiche entstehen, wie ihre Berechtigungen gesetzt werden und wie
   ein Recovery-Sweep begrenzte Crashreste erkennt und entfernt.
6. Welche Installation, Bedienung und Fehlermeldung für einen ersten lokalen
   Nutzer erforderlich ist, ohne bereits Browser, REST oder Hintergrundläufe
   einzuführen.

Das in EXP-0007 kompatibel ausgeführte EPUBCheck-5.3.0-Profil ist Evidenz,
aber keine automatische Provider- oder Versionsentscheidung. Vor einer
Produktübernahme sind aktuelle Primärquellen erneut zu prüfen.

## Akzeptanzkriterien für eine spätere Annahme

Ein angenommener WI-0005-Vertrag muss mindestens festlegen, dass:

1. nur ein stabiler und ausdrücklich für `continue_deep_read_only`
   freigegebener Snapshot den Adapter erreicht;
2. der Kern keinen Original- oder temporären Pfad erhält;
3. jeder Task einen neuen privaten Bereich und zufälligen technischen
   Dateinamen verwendet;
4. exakt Snapshot-Bytes geschrieben und vor sowie nach dem Providerlauf
   erneut gehasht werden;
5. der Provider nur read-only auf die Materialisierung zugreift;
6. Befehl, UID, Umgebung, Netzwerk, Kindprozesse, Zeit, CPU, RAM, Input,
   stdout, stderr und retained output vor Implementierung begrenzt sind;
7. Erfolg, Fehler, Timeout und Unterbrechung den Taskbereich bereinigen;
8. Crashreste beim nächsten Recovery-Lauf sichtbar, größenbegrenzt und
   sicher entfernbar sind;
9. der vollständige Werkzeugrohbefund provenienzgebunden erhalten bleibt;
10. die gemeinsame Evidenzprojektion unbekannte Werkzeugcodes verlustfrei
    bewahrt und keine Gesamtqualitätsaussage erzeugt;
11. Werkzeugausfall, ungültiger Bericht und Cleanupfehler fail-closed enden;
12. synthetische positive, negative, Timeout-, Output- und Cleanup-Fälle auf
    Windows und der gewählten Linux-/CI-Grenze ausführbar sind;
13. kein reales oder privates Medium für Entwicklung oder Abnahme nötig ist;
14. kein Writer, Import, Transformation, Persistenz- oder Fachsystemzugriff
    entsteht;
15. V1 später innerhalb eines Provideradapters ergänzt werden kann, ohne den
    Kernvertrag oder den V2-Standard zu ändern.

## Ausstieg

Ist kein aktueller Werkzeugkandidat unter diesen Grenzen wartbar,
reproduzierbar und lokal sinnvoll betreibbar, wird WI-0005 nicht angenommen.
EXP-0007 und WI-0004 bleiben dann ohne Produktadapter gültig; die E-Book-Linie
kann pausiert oder mit einer engeren Härtungsfrage fortgesetzt werden.

