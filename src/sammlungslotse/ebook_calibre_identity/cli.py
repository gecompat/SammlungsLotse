"""Path-free local CLI for WI-0011."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sammlungslotse.ebook_intake.cli import PathFreeArgumentParser
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader

from .application import EbookCalibreIdentityService
from .model import ComparisonEffects, EbookCalibreIdentityReport, RecordHandoffEffects
from .profile import PROFILE_ID, CalibreIdentityProfile
from .provider import CalibreRecordSnapshotProvider


DEFAULT_MAX_REPORT_BYTES = 512 * 1024


def _configure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def default_profile() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "runtime"
        / "ebook-calibre-identity"
        / "profile.json"
    )


def default_runtime_profile() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "runtime"
        / "calibre-readonly"
        / "profile.json"
    )


def _external_record_id(value: str) -> str:
    if not value.isascii() or not value.isdecimal() or value.startswith("0"):
        raise argparse.ArgumentTypeError("invalid external record ID")
    parsed = int(value)
    if parsed < 1 or parsed > 999999999:
        raise argparse.ArgumentTypeError("invalid external record ID")
    return value


def parser() -> argparse.ArgumentParser:
    result = PathFreeArgumentParser(
        prog="sammlungslotse-ebook-calibre-identity",
        description=(
            "Ein lokales EPUB mit genau einem ausdrücklich gewählten "
            "Calibre-Datensatz read-only vergleichen."
        ),
    )
    result.add_argument("input", type=Path, help="ein lokales Eingangs-EPUB")
    result.add_argument("library", type=Path, help="eine lokale Calibre-Bibliothek")
    result.add_argument("external_record_id", type=_external_record_id, help="eine Calibre-ID")
    result.add_argument("--json", action="store_true", help="pfadfreien JSON-Vertrag ausgeben")
    result.add_argument("--profile", type=Path, help="optionales exaktes WI-0011-Profil")
    result.add_argument("--runtime-profile", type=Path, help="optionales exaktes WI-0007-Profil")
    result.add_argument("--temp-root", type=Path, help="dedizierter nicht versionierter Task-Root")
    return result


def _not_assessed(
    *, external_record_id: int, reason: str, provider_version: str = "not_available"
) -> EbookCalibreIdentityReport:
    effects = RecordHandoffEffects(True, False, False, False, False)
    return EbookCalibreIdentityReport(
        assessment="not_assessed",
        effects=ComparisonEffects.from_handoff(effects),
        external_record_id=external_record_id,
        handoff_reason_codes=(reason,),
        identity=None,
        library_snapshot_sha256=None,
        profile_id=PROFILE_ID,
        provider_version=provider_version,
    )


def render_json(
    report: EbookCalibreIdentityReport, maximum: int = DEFAULT_MAX_REPORT_BYTES
) -> str:
    output = json.dumps(
        report.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    if len(output.encode("utf-8")) > maximum:
        raise RuntimeError("comparison report exceeds output limit")
    return output


def render_human(report: EbookCalibreIdentityReport) -> str:
    lines = [
        "SammlungsLotse EPUB-Calibre-Identitätskandidatenbericht",
        f"Bewertung: {report.assessment}",
        f"Calibre-ID: {report.external_record_id}",
        "Rollen: Eingang 1=ingress_epub | Eingang 2=calibre_record_epub",
    ]
    if report.handoff_reason_codes:
        lines.append(f"Gründe: {', '.join(report.handoff_reason_codes)}")
    if report.identity is not None:
        lines.append(f"Gesamthinweis: {report.identity.overall}")
        for item in report.identity.inputs:
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
        for stage in report.identity.stages:
            lines.extend(
                [
                    f"Ebene {stage.stage}: {stage.decision}",
                    f"  Regel: {stage.rule_id}",
                    f"  Positiv: {', '.join(stage.positive_evidence) or 'keine'}",
                    f"  Negativ: {', '.join(stage.negative_evidence) or 'keine'}",
                    f"  Fehlend: {', '.join(stage.missing_evidence) or 'keine'}",
                ]
            )
    effects = report.effects
    lines.append(
        "Wirkungen: Netzwerk="
        f"{'ja' if effects.network_access else 'nein'} | "
        f"Quelle verändert={'ja' if effects.source_modified else 'nein'} | "
        f"Container gestartet={'ja' if effects.container_started else 'nein'} | "
        f"Cleanup vollständig={'ja' if effects.cleanup_complete else 'nein'}"
    )
    output = "\n".join(lines)
    if len(output.encode("utf-8")) > DEFAULT_MAX_REPORT_BYTES:
        raise RuntimeError("comparison report exceeds output limit")
    return output


def _safety_failure(report: EbookCalibreIdentityReport) -> bool:
    if not report.effects.cleanup_complete or report.effects.source_modified:
        return True
    return any(
        reason
        in {
            "executor.cleanup_failed",
            "library.source_changed",
            "provider.output_contract_invalid",
            "workspace.cleanup_failed",
        }
        for reason in report.handoff_reason_codes
    )


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_streams()
    args = parser().parse_args(argv)
    external_record_id = int(args.external_record_id)
    maximum = DEFAULT_MAX_REPORT_BYTES
    try:
        profile = CalibreIdentityProfile.load(
            args.profile or default_profile(),
            args.runtime_profile or default_runtime_profile(),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        report = _not_assessed(
            external_record_id=external_record_id,
            reason="configuration.profile_invalid",
        )
    else:
        maximum = profile.limits["max_report_bytes"]
        if args.temp_root is None:
            report = _not_assessed(
                external_record_id=external_record_id,
                reason="configuration.temp_root_missing",
                provider_version=profile.runtime.provider["version"],
            )
        else:
            try:
                provider = CalibreRecordSnapshotProvider(
                    source=args.library,
                    temp_root=args.temp_root,
                    external_record_id=args.external_record_id,
                    profile=profile,
                )
                report = EbookCalibreIdentityService(profile).compare(
                    LocalFileSnapshotReader(args.input), provider
                )
            except KeyboardInterrupt:
                print("EPUB-Calibre-Vergleich wurde abgebrochen.", file=sys.stderr)
                return 130
            except Exception:
                print("EPUB-Calibre-Vergleich konnte nicht sicher ausgeführt werden.", file=sys.stderr)
                return 3
    try:
        print(render_json(report, maximum) if args.json else render_human(report))
    except Exception:
        print("EPUB-Calibre-Vergleich überschreitet seine Ausgabegrenze.", file=sys.stderr)
        return 3
    if _safety_failure(report):
        return 3
    return 0 if report.assessment == "completed" else 4


if __name__ == "__main__":
    raise SystemExit(main())
