"""Path-free local CLI for WI-0009."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sammlungslotse.ebook_intake.cli import PathFreeArgumentParser
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader

from .application import IdentityCandidateService
from .model import IdentityReport


def _configure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def render_json(report: IdentityReport, report_version: str = "v1") -> str:
    if report_version == "v1":
        value = report.to_dict()
    elif report_version == "v2":
        value = report.to_dict_v2()
    else:
        raise ValueError("unsupported identity report version")
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if len(payload.encode("utf-8")) > report.limits.max_report_bytes:
        raise RuntimeError("identity report exceeds output limit")
    return payload


def render_human(report: IdentityReport) -> str:
    lines = [
        "SammlungsLotse EPUB-Identitätskandidatenbericht",
        f"Bewertung: {report.assessment}",
        f"Gesamthinweis: {report.overall}",
    ]
    if report.assessment != "completed":
        lines.append(f"Gründe: {', '.join(report.reason_codes)}")
    else:
        for item in report.inputs:
            lines.extend(
                [
                    "",
                    f"Eingang {item.input_index}",
                    f"Snapshot: {item.size_bytes} Bytes | SHA-256 {item.sha256}",
                    f"Paket: {item.package_sha256}",
                    f"Repräsentation: {item.representation_sha256}",
                ]
            )
        lines.append("")
        for stage in report.stages:
            lines.extend(
                [
                    f"Ebene {stage.stage}: {stage.decision}",
                    f"  Regel: {stage.rule_id}",
                    f"  Positiv: {', '.join(stage.positive_evidence) or 'keine'}",
                    f"  Negativ: {', '.join(stage.negative_evidence) or 'keine'}",
                    f"  Fehlend: {', '.join(stage.missing_evidence) or 'keine'}",
                ]
            )
    lines.append("Wirkungen: Netzwerk=nein | Schreiben=nein | Original verändert=nein")
    output = "\n".join(lines)
    if len(output.encode("utf-8")) > report.limits.max_report_bytes:
        raise RuntimeError("identity report exceeds output limit")
    return output


def parser() -> argparse.ArgumentParser:
    result = PathFreeArgumentParser(
        prog="sammlungslotse-ebook-identity",
        description="Genau zwei lokale EPUB-Dateien read-only vergleichen.",
    )
    result.add_argument("input", nargs=2, type=Path, help="zwei lokale EPUB-Dateien")
    result.add_argument("--json", action="store_true", help="pfadfreien JSON-Vertrag ausgeben")
    result.add_argument(
        "--report-version",
        choices=("v1", "v2"),
        help="explizite JSON-Vertragsversion",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_streams()
    argument_parser = parser()
    args = argument_parser.parse_args(argv)
    if args.report_version is not None and not args.json:
        argument_parser.error("--report-version requires --json")
    try:
        first = args.input[0].resolve(strict=False)
        second = args.input[1].resolve(strict=False)
        if first == second:
            raise ValueError("identity inputs must differ")
        report = IdentityCandidateService().compare(
            LocalFileSnapshotReader(args.input[0]), LocalFileSnapshotReader(args.input[1])
        )
        output = (
            render_json(report, args.report_version or "v1")
            if args.json
            else render_human(report)
        )
    except KeyboardInterrupt:
        print("Identitätsvergleich wurde abgebrochen.", file=sys.stderr)
        return 130
    except Exception:
        print("Identitätsvergleich konnte nicht sicher ausgeführt werden.", file=sys.stderr)
        return 3
    print(output)
    return 0 if report.assessment == "completed" else 4


if __name__ == "__main__":
    raise SystemExit(main())
