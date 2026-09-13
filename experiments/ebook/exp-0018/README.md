# EXP-0018-Ausführung

Der Runner erzeugt nur flüchtige Verzeichnisse mit vorhandenen TEST-0001-
EPUBs und minimalen synthetischen Bytes. Er ruft den bestehenden JSON-
Ordnerweg je Fall zweimal auf und schreibt bei `--result` ausschließlich eine
pfadfreie Zusammenfassung.

Ein empirischer Ergebnislauf ist erst auf einem sauberen Preimage mit den
erforderlichen grünen Repository-Checks zulässig. Die lokale Ausführung
unterstützt die Vertragsprüfung und ersetzt diese Freigabe nicht.

    python tools/experiments/run_exp_0018.py --temp-root C:\rep\tmp\SammlungsLotse\exp-0018 --result C:\rep\artifacts\SammlungsLotse\exp-0018.json

Der spätere eingecheckte Nachweis wird über folgenden Aufruf geprüft:

    python tools/experiments/run_exp_0018.py --validate-result
