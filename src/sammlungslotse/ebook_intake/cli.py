"""Local visible CLI projection for WI-0004."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .application import TriageService
from .model import Evidence, TriageLimits, TriageReport
from .snapshot import LocalFileSnapshotReader


class PathFreeArgumentParser(argparse.ArgumentParser):
    """Keeps parser failures independent of user-provided locators."""

    def error(self, message: str) -> None:
        del message
        self.exit(2, "Eingabeparameter sind ungültig.\n")


def _configure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _format_evidence(item: Evidence) -> str:
    if not item.values:
        return item.code
    values = ", ".join(f"{key}={value}" for key, value in item.values)
    return f"{item.code} ({values})"


def render_human(report: TriageReport) -> str:
    snapshot = "nicht stabil verfügbar"
    if report.snapshot is not None:
        snapshot = (
            f"{report.snapshot.size_bytes} Bytes | "
            f"SHA-256 {report.snapshot.sha256}"
        )
    observations = "\n".join(
        f"  - {_format_evidence(item)}" for item in report.observations
    ) or "  - keine"
    findings = (
        "\n".join(f"  - {_format_evidence(item)}" for item in report.findings)
        or "  - keine"
    )
    deep = "ja" if report.deep_read_only_allowed else "nein"
    return "\n".join(
        [
            "SammlungsLotse E-Book-Eingangstriage",
            f"Formatfähigkeit: {report.format_capability}",
            f"Nächste Aktion: {report.next_action}",
            f"Tiefe read-only Prüfung erlaubt: {deep}",
            f"Snapshot: {snapshot}",
            "Beobachtungen:",
            observations,
            "Befunde:",
            findings,
            "Wirkungen: Netzwerk=nein | Schreiben=nein | "
            "tiefes Werkzeug gestartet=nein",
        ]
    )


def render_json(report: TriageReport) -> str:
    payload = json.dumps(
        report.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    if len(payload.encode("utf-8")) > report.limits.max_report_bytes:
        raise RuntimeError("bounded report exceeds its output limit")
    return payload


def parser() -> argparse.ArgumentParser:
    result = PathFreeArgumentParser(
        prog="sammlungslotse-ebook-intake",
        description="Eine lokale Datei flach und ausschließlich read-only triagieren.",
    )
    result.add_argument("input", type=Path, help="lokale Eingabedatei")
    result.add_argument(
        "--json", action="store_true", help="pfadbereinigten JSON-Vertrag ausgeben"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_streams()
    args = parser().parse_args(argv)
    try:
        report = TriageService().triage(
            LocalFileSnapshotReader(args.input), TriageLimits()
        )
        output = render_json(report) if args.json else render_human(report)
    except KeyboardInterrupt:
        print("Eingangstriage wurde abgebrochen.", file=sys.stderr)
        return 130
    except Exception:
        print("Eingang konnte nicht sicher geprüft werden.", file=sys.stderr)
        return 3
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
