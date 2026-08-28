"""German and deterministic JSON CLI for WI-0007."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .application import CalibreInventoryService
from .model import CalibreInventoryReport
from .profile import CalibreRuntimeProfile
from .provider import CalibreCliProvider


class PathFreeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.exit(2, "Eingabeparameter sind ungültig.\n")


def default_profile() -> Path:
    return Path(__file__).resolve().parents[3] / "runtime" / "calibre-readonly" / "profile.json"


def parser() -> argparse.ArgumentParser:
    result = PathFreeParser(prog="sammlungslotse-calibre-inventory")
    result.add_argument("library", type=Path, help="eine explizite lokale Calibre-Bibliothek")
    result.add_argument("--json", action="store_true", help="stabilen JSON-Vertrag ausgeben")
    result.add_argument("--profile", type=Path, help="optionaler exakter WI-0007-Profilpfad")
    result.add_argument("--temp-root", type=Path, help="dedizierter nicht versionierter Task-Root")
    return result


def render_json(report: CalibreInventoryReport, maximum: int = 8 * 1024 * 1024) -> str:
    output = json.dumps(report.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if len(output.encode("utf-8")) > maximum:
        raise RuntimeError("report output limit exceeded")
    return output


def render_human(report: CalibreInventoryReport) -> str:
    lines = [
        "SammlungsLotse Calibre-Bestandsprojektion",
        f"Ausführungsstatus: {report.execution_state}",
        f"Provider: Calibre {report.provider_version}",
        f"Datensätze: {len(report.books)}",
    ]
    if report.reason_codes:
        lines.append(f"Gründe: {', '.join(report.reason_codes)}")
    for book in report.books:
        lines.extend(
            [
                "",
                f"Calibre-ID {book.external_record_id}: {book.title}",
                f"  Autoren: {', '.join(book.authors) or 'keine Angabe'}",
                f"  Sprachen: {', '.join(book.languages) or 'keine Angabe'}",
                f"  Formate: {', '.join(book.formats) or 'keine'}",
            ]
        )
    lines.append(
        "Wirkungen: Netzwerk=nein | Original verändert="
        f"{'ja' if report.effects.original_modified else 'nein'} | "
        f"Cleanup vollständig={'ja' if report.effects.cleanup_complete else 'nein'}"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    temp_root = args.temp_root or (
        Path(os.environ["SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT"])
        if os.environ.get("SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT")
        else None
    )
    if temp_root is None:
        report = CalibreInventoryReport.not_assessed(state="unavailable", reason="configuration.temp_root_missing")
    else:
        try:
            profile = CalibreRuntimeProfile.load(args.profile or default_profile())
            report = CalibreInventoryService().project(
                CalibreCliProvider(source=args.library, temp_root=temp_root, profile=profile)
            )
        except KeyboardInterrupt:
            print("Calibre-Bestandsprojektion wurde abgebrochen.", file=sys.stderr)
            return 130
        except Exception:
            print("Calibre-Bibliothek konnte nicht sicher geprüft werden.", file=sys.stderr)
            return 3
    try:
        print(render_json(report) if args.json else render_human(report))
    except Exception:
        print("Calibre-Bestandsprojektion überschreitet ihre Ausgabegrenze.", file=sys.stderr)
        return 3
    if not report.effects.cleanup_complete or report.effects.original_modified:
        return 3
    return 0 if report.assessed else 4
