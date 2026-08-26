# Projektauftrag

Status: AUTHORITATIVE

Artifact: CAP-0001

## Zweck

SammlungsLotse reduziert den manuellen Aufwand für Aufbau, Prüfung, Pflege,
Suche und kontrollierte Erweiterung großer digitaler Sammlungen.

Das Projekt verbindet domänenübergreifende Verfahren mit spezialisierten
Fachsystemen. Es ersetzt diese Fachsysteme nicht.

## Nutzerproblem

Digitale Sammlungen enthalten häufig:

- identische oder inhaltlich gleiche Dateien;
- beschädigte oder unvollständige Medien;
- uneinheitliche, unvollständige oder falsche Metadaten;
- nicht erkannte Sprachen und Inhaltsklassen;
- technisch oder inhaltlich unterschiedlich hochwertige Ausgaben;
- unklare Ablage- und Zuordnungsentscheidungen;
- Bestände, die mit den Suchmöglichkeiten eines einzelnen Fachsystems nicht
  ausreichend erschließbar sind;
- neue Eingänge, deren sichere Integration viele manuelle Einzelschritte
  erfordert.

## Erwartete Fähigkeiten

SammlungsLotse soll:

1. Sammlungen und Eingangsbereiche rekursiv erfassen.
2. Dateiintegrität und Formatverwendbarkeit prüfen.
3. Dublettenkandidaten erzeugen, bewerten und nachvollziehbar entscheiden.
4. Metadaten beobachten, normalisieren, anreichern und zur Prüfung vorlegen.
5. Personen, Rollen, Sprachen, Werke, Ausgaben und weitere Fachentitäten
   korrekt unterscheiden.
6. technische und inhaltliche Qualitätsmerkmale getrennt bewerten.
7. strukturierte, inhaltliche, semantische und KI-gestützte Suche anbieten.
8. Zielbestände und Fachsysteme anhand dokumentierter Regeln auswählen.
9. Integrationen planen, autorisieren, ausführen und anschließend verifizieren.
10. alle wesentlichen Befunde und Entscheidungen mit Herkunft und Version
    erklären.

## Medienlinien

Der gemeinsame Kern unterstützt getrennte Medienlinien für:

- E-Books;
- Musik;
- Bilder;
- Videos;
- Scans;
- Dokumente.

Medienlinien dürfen gemeinsame Infrastruktur verwenden. Fachmodelle und
Fachregeln werden nicht künstlich vereinheitlicht.

## E-Book-Beispiel

Ein Eingangsordner kann E-Books in beliebigen Unterordnern enthalten.
SammlungsLotse erfasst die Dateien, prüft Format und Qualität, erkennt
Dubletten, bewertet Metadaten und Sprache und schlägt die passende
Calibre-Bibliothek vor. Die Zielauswahl kann Fachbücher, Kinderbücher und
weitere getrennte Bibliotheken berücksichtigen.

Eine Integration erfolgt erst über eine freigegebene Calibre-Schnittstelle und
wird anschließend gegen den geplanten Zustand geprüft.

## Zugänge

REST-Schnittstellen und Zugänge für KI-Systeme oder Agents sind
gleichberechtigte Anwendungseingänge. Sie umgehen keine Autorisierung,
Datenschutzregel oder Fachsystemgrenze.

Ein bestimmtes Agent-Protokoll, KI-Modell oder Anbieter ist noch nicht
festgelegt.

## Nichtziele

SammlungsLotse ist nicht:

- ein Ersatz für Calibre oder andere führende Fachsysteme;
- eine monolithische Datenbank, die alle Fachmodelle erzwingt;
- ein ungeprüfter automatischer Dateiverschieber oder Metadatenwriter;
- ein Grund, stabile Funktionen gepflegter Spezialsoftware neu zu
  implementieren;
- ein Beleg dafür, dass aus FolioTone stammender Code automatisch geeignet
  oder rechtlich übertragbar ist.

## Erfolgskriterien

Das Projekt ist erfolgreich, wenn es bei wachsenden Sammlungen nachweisbar:

- manuellen Prüf- und Integrationsaufwand reduziert;
- Dubletten und beschädigte Medien vor der Zielintegration erkennt;
- fachliche Entscheidungen erklärt und überprüfbar macht;
- führende Fachsysteme konsistent hält;
- Such- und Analysefragen beantwortet, die ein einzelnes Fachsystem nicht
  ausreichend abdeckt;
- lokale Daten und Schreiboperationen kontrolliert behandelt.

## Noch nicht entschiedene Punkte

Die Entwicklungsplanung muss mindestens festlegen:

- erste vollständige Medienlinie und erster vertikaler Ablauf;
- Laufzeit, Programmiersprache und Paketstruktur;
- Persistenz-, Index- und Suchtechnologie;
- lokales Betriebs- und Deploymentmodell;
- Benutzeroberfläche und öffentliche API-Versionierung;
- Agent- und Automationsschnittstellen;
- Freigabegrenzen für schreibende Operationen;
- konkrete FolioTone-Komponenten, die geprüft oder neu implementiert werden.
