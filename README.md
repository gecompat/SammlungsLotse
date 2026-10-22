# SammlungsLotse

SammlungsLotse ist ein geplantes, domänenübergreifendes Assistenzsystem für
digitale Sammlungen. Es soll wiederkehrende Prüf-, Bereinigungs-, Such- und
Integrationsarbeiten übernehmen, die ohne Automatisierung einen hohen
manuellen Aufwand verursachen.

## Projektstatus

Das Repository besitzt mit WI-0004 einen vollständig begrenzten read-only
E-Book-Eingangstriage-Prototyp, mit WI-0005 einen optionalen tiefen
EPUBCheck-Adapter, mit WI-0006 einen kleinen Mehrdatei-Bericht, mit WI-0007
eine eng begrenzte read-only Calibre-Bestandsprojektion und mit WI-0009 einen
synthetisch qualifizierten Zwei-EPUB-Identitätskandidatenbericht. WI-0011
verbindet beide Verträge für genau ein explizites Eingangs-EPUB und genau
einen expliziten Calibre-Datensatz read-only, providerneutral und ohne
Bestandswirkung. Dies ist keine vollständige Medienlinie und legt weder das
allgemeine Laufzeitmodell noch eine technische Roadmap fest. Weitere
Entwicklung beginnt weiterhin nur auf Grundlage der hier dokumentierten
Produkt- und Governance-Verträge.

## Produktauftrag

SammlungsLotse soll unter anderem:

- vorhandene Sammlungen inventarisieren;
- Dubletten und beschädigte Dateien erkennen;
- Metadatenfehler und uneinheitliche Schreibweisen ermitteln;
- Sprache, technische Qualität und inhaltliche Merkmale bestimmen;
- inhaltliche, semantische und KI-gestützte Suchen ermöglichen;
- neue Dateien aus überwachten Ordnern einschließlich Unterordnern prüfen;
- geeignete Zielbestände oder Teilbibliotheken vorschlagen;
- geprüfte Integrationen in bestehende Sammlungen orchestrieren;
- Entscheidungen, Quellen, Versionen und Prüfergebnisse nachvollziehbar
  erhalten.

Der Auftrag gilt für E-Books, Musik, Bilder, Videos, Scans und Dokumente.
Weitere Medientypen können über getrennte Medienlinien ergänzt werden.

## Führende Fachsysteme

Das fachlich spezialisierte System bleibt für seine Domäne führend.
Beispielsweise verwaltet Calibre die produktive E-Book-Sammlung.
SammlungsLotse ersetzt Calibre nicht. Es analysiert, bewertet, sucht, plant und
orchestriert über dokumentierte Schnittstellen.

Eine E-Book-Integration kann mehrere Calibre-Bibliotheken berücksichtigen,
beispielsweise getrennte Bibliotheken für Fachbücher, Kinderbücher und weitere
Bestandsklassen.

## Grundsätze

- Fachsysteme bleiben führend.
- Beobachtungen, Ableitungen und bestätigte Werte bleiben unterscheidbar.
- Lesen und Analysieren sind von schreibenden Operationen getrennt.
- Schreibende Operationen benötigen eine definierte Autorisierung,
  Vorprüfung, Verifikation und Wiederherstellungsstrategie.
- Lokale und datensparsame Verarbeitung ist der Ausgangspunkt.
- Netzwerkeinsatz ist explizit und nachvollziehbar.
- REST-Schnittstellen und Agent-Zugänge verwenden dieselben
  Anwendungsverträge wie eine spätere Benutzeroberfläche.
- Externe Werkzeuge bleiben austauschbare Adapter.
- Große Sammlungen werden inkrementell und mit begrenztem Ressourcenverbrauch
  verarbeitet.

## Verhältnis zu FolioTone

SammlungsLotse ist ein eigenständiges Projekt. FolioTone bleibt eine
Referenz- und mögliche Spenderquelle. Quellcode wird nicht pauschal
übernommen. Jede Wiederverwendung benötigt eine fachliche Eignungsprüfung,
Rechtenachweis, Herkunftsdokumentation und eigene Tests im neuen Projekt.

## Dokumentation

- [Lokale read-only-Beispiele mit synthetischen Eingängen](docs/guides/LOCAL_READONLY_EXAMPLES.md)
- [Dokumentationsübersicht](docs/README.md)
- [Projektauftrag](docs/product/PROJECT_CHARTER.md)
- [Produkt- und Systemgrenzen](docs/architecture/BOUNDARIES.md)
- [Projektregeln](docs/governance/PROJECT_RULES.md)
- [Aktueller Projektstatus](docs/project/PROJECT_STATUS.md)
- [Ursprüngliche Produktabsicht](docs/ideas/owner-notes/ORIGINAL_PRODUCT_INTENT.md)

## Entwicklung

Beiträge mit Produktcode setzen einen registrierten und angenommenen
Arbeitsgegenstand voraus. Die Python-3.12-Standardbibliothekswahl gilt nur für
WI-0004 und ist keine allgemeine Stackentscheidung. Weitere Regeln stehen in
[CONTRIBUTING.md](CONTRIBUTING.md).

Für den ersten nachvollziehbaren Lauf führt die [Anleitung für lokale
read-only-Beispiele](docs/guides/LOCAL_READONLY_EXAMPLES.md) von den
Voraussetzungen über synthetische Eingänge und Berichtsausgabe bis zu Grenzen
und Fehlerhinweisen. Aktuelle Prüf- und Projektstände stehen getrennt im
[Projektstatus](docs/project/PROJECT_STATUS.md).

Die AI-Instruktionen beginnen in [AGENTS.md](AGENTS.md). Die [Übersicht zum
`.ai`-Bereich](.ai/README.md) erklärt für Menschen Projektidentität, Registry,
Foundation-Transfer und die zugehörigen Prüfwege; sie ersetzt keine dieser
kanonischen Quellen.

## Lizenz

Der eigenständig entwickelte Inhalt dieses Repositorys steht unter der
[MIT-Lizenz](LICENSE). Übertragene Foundation-Bestandteile besitzen ihren
gesonderten Herkunftsnachweis unter
.ai/foundation/AI_REPOSITORY_FOUNDATION_NOTICE.md.
