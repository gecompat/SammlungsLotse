# WI-0013: Rollenbewussten EPUB-Identitätsbericht V2 umsetzen

Status: ACCEPTED — NOT IMPLEMENTED

Stand: 2026-08-31

Artifact: WI-0013

## Auswahl und Zweck

GATE-0012 hat nach der ausdrücklichen Nutzerauswahl Option A angenommen.
WI-0013 überführt deshalb ausschließlich den in EXP-0011 verlustfrei
qualifizierten V2-Kandidaten in einen öffentlichen, explizit aktivierten
JSON-Bericht. Der Nutzwert ist eine zusammenhängende, semantisch korrekte
Darstellung von primären und zusätzlichen Identifiern,
`dcterms:modified`, Collection-Mitgliedschaften und ihrer Provenienz.

Der bestehende V1-Bericht bleibt während dieser Wave der unveränderte
Standard. WI-0013 autorisiert keine V1-Deprecation, keine automatische
Migration bestehender Verbraucher und keine Entfernung des V1-Vertrags.

## Öffentlicher Aufrufvertrag

- Der vorhandene Aufruf ohne Versionsoption bleibt unverändert.
- `--json` erzeugt weiterhin bytegenau den V1-Bericht mit dem Schema
  `sammlungslotse/ebook-identity-candidate-report/v1`.
- V2 wird ausschließlich durch die gemeinsame Angabe
  `--json --report-version v2` aktiviert.
- `--report-version` ohne `--json` wird mit einem stabilen, sichtbaren
  Nutzungsfehler abgelehnt; die deutsche Standardansicht bleibt unverändert.
- Der V2-Bericht verwendet das Schema
  `sammlungslotse/ebook-identity-candidate-report/v2`.
- Unbekannte Versionswerte werden abgelehnt. Es gibt keine implizite
  Versionsumschaltung.

## Gebundener V2-Berichtsvertrag

V2 behält die V1-Top-Level-Felder `assessment`, `effects`, `inputs`, `limits`,
`overall`, `reason_codes`, `schema` und `stages`. Hashes, Größen, Zähler und
`input_index` bleiben unverändert. Ausschließlich die Metadatenprojektion je
Eingang wird rollenbewusst:

```json
{
  "titles": [],
  "creators": [],
  "languages": [],
  "primary_identifier": null,
  "primary_identifier_element_ref": null,
  "additional_identifiers": [],
  "modified": null,
  "collection_memberships": [],
  "provenance": {}
}
```

Der konkrete Vertrag ist an die EXP-0011-V2-Projektion gebunden:

- `primary_identifier` ist `null` oder enthält genau `id` und `value`;
- `primary_identifier_element_ref` erhält den Wert von
  `package@unique-identifier`, auch wenn sein Zielelement fehlt;
- jeder Eintrag unter `additional_identifiers` enthält `id`,
  `identifier_type`, `scheme` und `value`;
- `modified` enthält den beobachteten `dcterms:modified`-Wert oder `null`;
- jeder Eintrag unter `collection_memberships` enthält `id`, `identifier`,
  `name`, `position` und `type`;
- `provenance` ordnet jedem beobachteten oder fehlenden Rollenfeld einen
  stabilen Feldpfad sowie genau `source` und `status` zu;
- `status` ist ausschließlich `observed` oder `missing`;
- Listen folgen der Dokumentreihenfolge, fehlende Listen sind leer und
  fehlende Einzelwerte sind `null`;
- V2 enthält weder das semantisch überdehnte V1-Feld `work_references` noch
  die flache V1-Liste `identifiers`.

Die im eingecheckten EXP-0011-Ergebnis unter `variants.V2.report` sichtbare
Struktur ist der Vergleichsoracle für diese Projektion. Experiment-Oracles
dürfen jedoch keine Produktentscheidung, Regel-ID oder Evidenzbewertung
ersetzen.

## Unveränderte Entscheidungssemantik

V2 enthält weiterhin genau die fünf Stufen `byte`, `package`,
`representation`, `edition` und `work` in dieser Reihenfolge. Für dasselbe
Eingangspaar müssen `decision`, `rule_id`, `positive_evidence`,
`negative_evidence` und `missing_evidence` in V1 und V2 identisch sein.
`overall`, `assessment`, `reason_codes`, Limits und Wirkungsaussagen bleiben
ebenfalls identisch.

Es entsteht keine Stufe `publication`. Insbesondere werden die beiden in
EXP-0011 sichtbaren `candidate_related`-Fälle nicht umklassifiziert und ein
EXP-0011-Oracle wird nicht Teil der Produktlogik.

## Implementierungsgrenze

Die Implementierung darf ausschließlich den bestehenden lokalen,
read-only EPUB-Identitätsweg um eine rollenbewusste interne Projektion und
den expliziten V2-Renderer erweitern. Python 3.12 und die Standardbibliothek
bleiben die enge, reversible Laufzeitwahl dieses bestehenden Produktwegs.

Außerhalb bleiben:

- reale oder private Medien und Produktionsdaten;
- automatische Suche, Kandidatenbildung oder mehrere Bibliotheken;
- Netzwerk, Browser, REST, Agents und externe Metadatenprovider;
- Persistenz, Caches, Datenbanken und Schreiboperationen;
- Änderungen an Originalen, Calibre oder anderen Fachsystemen;
- neue Provider-, Routing-, UI-, Publikations- oder Deploymentverträge;
- Änderungen an eingefrorenen EXP-0009-, EXP-0010- oder EXP-0011-Ergebnissen.

## Qualifikationsvertrag

Die Implementierungswave beginnt erst nach Merge und Post-Merge-Prüfung
dieses Planungsvertrags in einem neuen isolierten Worktree. Sie muss danach
mindestens belegen:

1. Der unveränderte Standardpfad erzeugt auf allen 13 qualifizierten
   TEST-0001- und EXP-0010-Paaren zweimal bytegenau dasselbe V1-JSON wie der
   gebundene Ausgangsstand.
2. Der explizite V2-Pfad erzeugt auf denselben 13 Paaren zweimal semantisch
   identische, pfadfreie Berichte.
3. Die V2-Metadatenprojektion entspricht für diese Paare dem eingecheckten
   EXP-0011-V2-Ergebnis ohne Rollen- oder Provenienzverlust.
4. Die zwei nicht konformen EXP-0010-Kontrollen belegen fehlende
   Primärbindung beziehungsweise fehlendes `dcterms:modified`, werden aber
   weiterhin nicht als positive Produktqualitätsfälle gezählt.
5. V1 und V2 liefern je Paar dieselben fünf Entscheidungen, Regel-IDs und
   positiven, negativen sowie fehlenden Evidenzkanäle.
6. Kein Bericht enthält lokale Pfade; Eingänge und Originale bleiben vor und
   nach jedem Lauf bytegleich.
7. Der abhängige WI-0011-Calibre-Identitätsweg wird gegen den neuen
   Produktpreimage erneut vollständig qualifiziert und bleibt standardmäßig
   auf V1.
8. Die historischen EXP-0009-, EXP-0010- und EXP-0011-Validatoren bleiben
   erfolgreich, ohne ihre Ergebnisse oder Preimages umzuschreiben.
9. Repository-, Registry-, Dokumentations-, Datenschutz- und Foundation-
   Prüfungen bleiben erfolgreich.

Der Produktnachweis muss den vollständigen Git-Preimage, Python-Version,
Eingangshashes, Wiederholungen, Einzelkriterien und Gesamtstatus binden. Eine
grüne Teilprüfung oder ein nicht commitgebundener Lauf genügt nicht.

## Abnahme

WI-0013 kann erst `done` werden, wenn die Implementierung und der vollständige
synthetische Produktnachweis in einem getrennten Pull Request integriert,
alle erforderlichen Checks grün und der exakte Merge-Commit auf `origin/main`
post-merge geprüft sind. Bis dahin bedeutet `accepted` ausschließlich, dass
dieser enge Vertrag zur Umsetzung freigegeben ist.

Eine spätere V1-Deprecation, eine neue Publikationsstufe oder eine weitere
Produktfortsetzung benötigt eine neue ausdrückliche Entscheidung.
