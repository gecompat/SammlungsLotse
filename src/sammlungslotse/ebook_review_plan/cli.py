"""Separate deterministic CLI for the WI-0019 review plan."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile
from sammlungslotse.calibre_inventory.provider import CalibreCliProvider

from .application import ReviewPlanService
from .model import ReviewPlanReport


class PathFreeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.exit(2, "Eingabeparameter sind ungültig.\n")


def _profile() -> Path:
    return Path(__file__).resolve().parents[3] / "runtime" / "calibre-readonly" / "profile.json"


def parser() -> argparse.ArgumentParser:
    result = PathFreeParser(prog="sammlungslotse-ebook-review-plan")
    result.add_argument("inbox", type=Path)
    result.add_argument("library", type=Path)
    result.add_argument("--json", action="store_true")
    result.add_argument("--profile", type=Path)
    result.add_argument("--temp-root", type=Path)
    return result


def render_json(report: ReviewPlanReport, maximum: int = 48 * 1024 * 1024) -> str:
    value = json.dumps(report.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if len(value.encode("utf-8")) > maximum:
        raise RuntimeError("review plan exceeds output limit")
    return value


def render_human(report: ReviewPlanReport) -> str:
    lines = ["SammlungsLotse E-Book-Reviewplan", f"Status: {report.state}"]
    if report.reason_codes:
        lines.append(f"Gründe: {', '.join(report.reason_codes)}")
    for item in report.items:
        lines.extend(["", f"Eingang {item.input_index + 1}", f"Reviewklasse: {item.review_class}"])
        for candidate in item.candidates:
            lines.append(f"  Kandidat {candidate.library_position + 1}: Calibre-ID {candidate.external_record_id}; Gründe: {', '.join(candidate.reason_strategies)}")
    lines.append("Wirkungen: Netzwerk=nein | Persistenz=nein | Import=nein | Schreiben=nein")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if callable(getattr(stream, "reconfigure", None)):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    temp_root = args.temp_root or (Path(os.environ["SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT"]) if os.environ.get("SAMMLUNGSLOTSE_CALIBRE_TEMP_ROOT") else None)
    if temp_root is None:
        report = ReviewPlanReport("not_assessed", (), None, ("configuration.temp_root_missing",))
    else:
        try:
            profile = CalibreRuntimeProfile.load(args.profile or _profile())
            report = ReviewPlanService().build(args.inbox, CalibreCliProvider(source=args.library, temp_root=temp_root, profile=profile))
        except KeyboardInterrupt:
            print("E-Book-Reviewplan wurde abgebrochen.", file=sys.stderr)
            return 130
        except Exception:
            print("E-Book-Reviewplan konnte nicht sicher erstellt werden.", file=sys.stderr)
            return 3
    try:
        print(render_json(report) if args.json else render_human(report))
    except Exception:
        print("E-Book-Reviewplan überschreitet seine Ausgabegrenze.", file=sys.stderr)
        return 3
    return 0 if report.state == "completed" else 4
