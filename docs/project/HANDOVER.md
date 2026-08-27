# Übergabe

Status: AUTHORITATIVE

Stand: 2026-08-27

## Aktueller Stand

SammlungsLotse ist als eigenständiges Projekt initialisiert. Nach
ergebnisoffener E-Book-Erkundung ist WI-0004 als erster eng begrenzter,
reversibler Produktprototyp implementiert und lokal vollständig abgenommen.
AI Repository Foundation 1.7.0 ist semantisch integriert. Die Bewertung steht
unter docs/governance/FOUNDATION_UPGRADE_1_7.md.

main ist geschützt. Änderungen benötigen die erfolgreichen Checks
repository-quality und registry-integrity.

Die maßgeblichen Produktgrenzen stehen in docs/product/PROJECT_CHARTER.md und
docs/architecture/BOUNDARIES.md. Die Startentscheidungen stehen unter
docs/decisions/.

Der aktuelle E-Book-Brainstorming-Stand steht unter
docs/planning/EBOOK_LANDSCAPE.md. Die weitere Erkenntnisreihenfolge steht
unter docs/planning/EBOOK_EXPLORATION_PLAN.md. WI-0002 ist `done`. Die
Neubewertung unter docs/planning/EBOOK_GATE_0001_COMPARISON.md hat die
Eingangstriage als eng begrenzten ersten read-only E-Book-Vertikalablauf
angenommen; GATE-0001 ist `done`. Bestandsprüfung bleibt ein möglicher
späterer Ast.

WI-0003 ist auf Dokumentationsebene abgeschlossen. Die sechs
Nutzerentscheidungen und Messverträge stehen unter
docs/planning/EBOOK_SCENARIOS_AND_METRICS.md. TEST-0001 ist unter
docs/planning/EBOOK_REFERENCE_CORPUS.md als aktive Fixture-Version `0.2.0` mit allen
26 `Kern`-Fällen, 44 Komponenten, Hashes, Herkunft und Oracles ausführbar und
validiert; `0.1.0` bleibt als historischer Snapshot erhalten. Die vier
`Ausbau`-Fälle bleiben offen. EXP-0005 ist mit elf erfolgreichen
Isolationskriterien abgeschlossen. EXP-0002 ist mit dreizehn erfolgreichen
Calibre-Projektionskriterien abgeschlossen; der direkte read-only Mount ist
als nicht unterstützt und die Copy-on-read-Grenze als erfolgreich belegt.
EXP-0003 ist mit vierzehn erfolgreichen Evidenzkriterien abgeschlossen:
EPUBCheck- und Ace-Rohberichte bleiben getrennt und verlustfrei, unbekannte
Codes sowie manueller Prüfbedarf bleiben sichtbar. Das erprobte Ace-Profil
ist wegen deaktivierter Chromium-Sandbox und offener npm-Advisories nicht
produktqualifiziert. EXP-0004 ist mit fünfzehn erfolgreichen Kriterien
abgeschlossen: Sechs Sollpaare bleiben auf fünf Identitätsebenen getrennt,
Kandidaten zeigen positive und negative Evidenz, fehlende Evidenz bleibt
separat und Leseprobe/Vollausgabe führt auf Ausgabenebene zur Enthaltung. Die
perfekten Werte des kleinen synthetischen Goldstandards sind keine
Produktprognose. EXP-0006 ist mit 16 erfolgreichen Kriterien abgeschlossen:
Alle elf vorab gebundenen Preflight-Zeilen stimmen in zwei semantisch
identischen Wiederholungen überein, acht Fälle bleiben außerhalb des tiefen
Werkzeugwegs, drei positiv gegatete Kontrollen starten ihn und kritische
Fehlfreigaben betragen null. Alle Verträge und Ergebnisgrenzen stehen unter
docs/planning/EBOOK_EXPERIMENTS.md.

GATE-0002, EXP-0007 und GATE-0003 sind `done`. EXP-0007 hat V1 und V2 unter
getrennten Windows- und Linux/Podman-Profilen qualifiziert und V3 wegen
Originalpfadweitergabe und reproduzierter TOCTOU-Lücke abgelehnt. GATE-0003
wählt V2, die task-private hashgebundene Materialisierung, als Standardnaht.
WI-0005 ist nur vorgeschlagen und autorisiert noch keinen Produktcode.

## Fortsetzung

WI-0004 ist `done`. Der Produktcode liegt unter
`src/sammlungslotse/ebook_intake/`, die sichtbare lokale Oberfläche unter
`tools/run_ebook_intake.py`. Die Grenze endet nach stabilem
In-Memory-Snapshot, flachem Preflight und sichtbar begründeter CLI-Folgeaktion
oder Enthaltung. Calibre, tiefe Formatprüfung, Dubletten, Metadaten, Routing,
Persistenz, Browser, REST, Agents und jeder Writer bleiben außerhalb.

Als Nächstes wird WI-0005 getrennt bewertet. Vor einer Annahme sind ein
aktueller Werkzeugkandidat, Lizenz und Wartungsstand, Offline- und
Sicherheitsprofil, providerneutrale Evidenzprojektion, Taskbereich und
Recovery sowie die kleinste lokale Nutzeroberfläche festzulegen. Ohne diese
Bewertung beginnt kein Produktadapter.

## Harte Grenzen

- Fachsysteme bleiben führend.
- Kein FolioTone-Code wird ohne Rechte- und Eignungsprüfung übernommen.
- Kein reales privates Sammlungsmedium gelangt in Git.
- Produktcode wird nicht ohne registrierten Arbeitsgegenstand begonnen.
- Schreibende Fähigkeiten benötigen eine eigene Entscheidung und vollständige
  Sicherheitskette.

## Noch nicht entschieden

- erste vollständige Medienlinie jenseits des WI-0004-Prototyps;
- Annahme oder Ablehnung von WI-0005 und der erste konkrete
  Werkzeugprovider; V2 ist nur die qualifizierte Übergabenaht;
- Programmiersprache und Laufzeit jenseits der reversiblen WI-0004-Auswahl
  Python 3.12 mit Standardbibliothek;
- Persistenz und Suche;
- Deployment und UI;
- konkrete REST- und Agent-Verträge;
- konkrete FolioTone-Wiederverwendung;
- Tiefe der ersten Formatunterstützung und konkrete Qualitätsprofile;
- konkrete Calibre-, Werkzeug- und Metadatenprovider-Adapter;
- konkrete, empirisch qualifizierte Produktprofile; EXP-0002 qualifiziert nur
  den Copy-on-read-Calibre-Zugriff, EXP-0003 nur eine Evidenzprojektion mit
  nicht produktqualifiziertem Ace-Profil, EXP-0004 nur eine kleine
  synthetische Identitätsheuristik, EXP-0005 nur einen wegwerfbaren
  Sicherheitsweg und EXP-0006 nur einen kleinen synthetischen Preflight;
  keiner dieser Versuche wählt eine Produktlaufzeit;
- ein optionales Repository-Continuity-Verfahren mit getrennten Rulesets,
  autorisierten Akteuren und Ausfallschwelle. Bis zu einer angenommenen
  Entscheidung existiert kein Break-Glass-Bypass.

## Validierung

Die aktuellen Prüfergebnisse stehen ausschließlich in
docs/project/PROJECT_STATUS.md.
