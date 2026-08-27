"""Local visible CLI projection for WI-0004."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path

from .application import TriageService
from .batch import BatchIntakeService, BatchLimits, BatchReport
from .deep_application import DeepReadOnlyService
from .deep_model import CombinedIntakeReport, DeepToolResult
from .deep_profile import DeepRuntimeProfile
from .epubcheck_provider import EpubCheckProvider
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


def render_deep_human(report: DeepToolResult) -> str:
    shown = report.findings[:20]
    findings = [
        f"  - {item.severity} {item.code}: {item.message}" for item in shown
    ]
    if len(report.findings) > len(shown):
        findings.append(
            f"  - {len(report.findings) - len(shown)} weitere Befunde nur in JSON"
        )
    if not findings:
        findings.append("  - keine")
    raw = "nicht vorhanden"
    if report.raw_report is not None:
        import hashlib

        raw = (
            f"{len(report.raw_report)} Bytes | "
            f"SHA-256 {hashlib.sha256(report.raw_report).hexdigest()}"
        )
    reasons = ", ".join(report.reason_codes) or "keine"
    return "\n".join(
        [
            "Tiefe EPUB-Konformitätsprüfung",
            f"Ausführungsstatus: {report.execution_state}",
            f"Bewertung: {report.assessment}",
            f"Provider: {report.provider_id} {report.provider_version}",
            f"Gründe: {reasons}",
            f"Rohbericht: {raw}",
            "Befunde:",
            *findings,
            "Wirkungen: Netzwerk=nein | Original verändert=nein | "
            f"Prozess gestartet={'ja' if report.effects.process_started else 'nein'} | "
            f"Cleanup vollständig={'ja' if report.effects.cleanup_complete else 'nein'}",
        ]
    )


def render_combined_json(
    report: CombinedIntakeReport, *, max_bytes: int
) -> str:
    payload = json.dumps(
        report.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    if len(payload.encode("utf-8")) > max_bytes:
        raise RuntimeError("bounded combined report exceeds its output limit")
    return payload


def render_batch_json(report: BatchReport) -> str:
    payload = json.dumps(
        report.to_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    if len(payload.encode("utf-8")) > report.limits.max_report_bytes:
        raise RuntimeError("bounded batch report exceeds its output limit")
    return payload


def render_batch_human(report: BatchReport) -> str:
    lines = [
        "SammlungsLotse E-Book-Mehrdatei-Eingangsbericht",
        f"Batch-Status: {report.batch_status}",
        f"Eingänge: {report.input_count}",
        f"Snapshot-Summe: {report.total_snapshot_bytes} Bytes",
    ]
    for item in report.items:
        lines.extend(["", f"Eingang {item.input_index + 1}"])
        if item.status != "completed" or item.triage is None:
            reasons = ", ".join(item.reason_codes) or "keine"
            lines.extend([f"Status: {item.status}", f"Gründe: {reasons}"])
            continue
        single = render_human(item.triage)
        lines.extend(single.splitlines()[1:])
        if item.deep_read_only is not None:
            lines.append("")
            lines.extend(render_deep_human(item.deep_read_only).splitlines())

    summary = report.to_dict()["summary"]
    assert isinstance(summary, dict)
    actions = summary["next_actions"]
    assert isinstance(actions, dict)
    action_text = " | ".join(
        f"{key}={value}" for key, value in sorted(actions.items())
    )
    lines.extend(["", f"Zusammenfassung Folgeaktionen: {action_text}"])
    output = "\n".join(lines)
    if len(output.encode("utf-8")) > report.limits.max_report_bytes:
        raise RuntimeError("bounded batch report exceeds its output limit")
    return output


def _default_deep_profile() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "runtime"
        / "ebook-deep-readonly"
        / "profile.json"
    )


def parser() -> argparse.ArgumentParser:
    result = PathFreeArgumentParser(
        prog="sammlungslotse-ebook-intake",
        description="Eine lokale Datei flach und ausschließlich read-only triagieren.",
    )
    result.add_argument(
        "input", nargs="+", type=Path, help="eine oder mehrere lokale Eingabedateien"
    )
    result.add_argument(
        "--json", action="store_true", help="pfadbereinigten JSON-Vertrag ausgeben"
    )
    result.add_argument(
        "--deep-read-only",
        action="store_true",
        help="nach positiver Triage explizit EPUBCheck ausführen",
    )
    result.add_argument(
        "--deep-profile",
        type=Path,
        help="optionaler lokaler WI-0005-Profilpfad",
    )
    result.add_argument(
        "--deep-temp-root",
        type=Path,
        help="dedizierter nicht versionierter Task-Root",
    )
    return result


def _deep_inspector(
    args: argparse.Namespace,
) -> tuple[Callable[[TriageReport], DeepToolResult], DeepRuntimeProfile | None]:
    profile: DeepRuntimeProfile | None = None
    temp_value = args.deep_temp_root or (
        Path(os.environ["SAMMLUNGSLOTSE_TEMP_ROOT"])
        if os.environ.get("SAMMLUNGSLOTSE_TEMP_ROOT")
        else None
    )
    profile_invalid = False
    if temp_value is not None:
        try:
            profile = DeepRuntimeProfile.load(
                args.deep_profile or _default_deep_profile()
            )
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            profile_invalid = True

    def inspect(report: TriageReport) -> DeepToolResult:
        if not report.deep_read_only_allowed or report.snapshot is None:
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="gate.not_open",
                snapshot_sha256=(
                    report.snapshot.sha256 if report.snapshot is not None else None
                ),
            )
        if temp_value is None:
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="configuration.temp_root_missing",
                snapshot_sha256=report.snapshot.sha256,
            )
        if profile_invalid or profile is None:
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="configuration.profile_invalid",
                snapshot_sha256=report.snapshot.sha256,
            )
        return DeepReadOnlyService().inspect(
            report,
            EpubCheckProvider(profile=profile, temp_root=temp_value),
        )

    return inspect, profile


def _run_single(args: argparse.Namespace) -> tuple[str, int]:
    report = TriageService().triage(
        LocalFileSnapshotReader(args.input[0]), TriageLimits()
    )
    if not args.deep_read_only:
        return (render_json(report) if args.json else render_human(report), 0)

    inspector, profile = _deep_inspector(args)
    deep = inspector(report)
    combined = CombinedIntakeReport(report, deep)
    maximum = (
        int(profile.execution["cli_json_max_bytes"])
        if profile is not None
        else 3 * 1024 * 1024
    )
    output = (
        render_combined_json(combined, max_bytes=maximum)
        if args.json
        else f"{render_human(report)}\n\n{render_deep_human(deep)}"
    )
    return output, (4 if deep.assessment == "not_assessed" else 0)


def _run_batch(args: argparse.Namespace) -> tuple[str, int]:
    limits = BatchLimits()
    if len(args.input) > limits.max_inputs:
        raise ValueError("batch input count exceeds its limit")
    inspector = None
    if args.deep_read_only:
        inspector, _profile = _deep_inspector(args)
    report = BatchIntakeService().inspect(
        tuple(LocalFileSnapshotReader(path) for path in args.input),
        limits=limits,
        deep_inspector=inspector,
    )
    output = render_batch_json(report) if args.json else render_batch_human(report)
    if report.has_internal_error:
        return output, 3
    if report.has_unassessed_deep_result:
        return output, 4
    return output, 0


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_streams()
    args = parser().parse_args(argv)
    try:
        if len(args.input) == 1:
            output, exit_code = _run_single(args)
        else:
            output, exit_code = _run_batch(args)
    except KeyboardInterrupt:
        print("Eingangstriage wurde abgebrochen.", file=sys.stderr)
        return 130
    except Exception:
        print("Eingang konnte nicht sicher geprüft werden.", file=sys.stderr)
        return 3
    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
