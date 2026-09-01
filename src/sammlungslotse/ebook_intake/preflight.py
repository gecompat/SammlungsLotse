"""Bounded, shallow and extraction-free EPUB preflight."""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import PurePosixPath

from .context import classify_payload
from .model import (
    Evidence,
    ReviewContext,
    Snapshot,
    TriageLimits,
    TriageReport,
    evidence,
)


MARKUP_SUFFIXES = (".xhtml", ".html", ".htm", ".svg", ".opf", ".xml", ".css")
REMOTE_REFERENCE = re.compile(
    rb"(?:href|poster|src)\s*=\s*['\"]\s*https?://|url\(\s*['\"]?\s*https?://",
    re.IGNORECASE,
)


def _append_once(items: list[Evidence], item: Evidence) -> None:
    if item.code not in {current.code for current in items}:
        items.append(item)


def _report(
    *,
    snapshot: Snapshot,
    observations: list[Evidence],
    findings: list[Evidence],
    capability: str,
    action: str,
    limits: TriageLimits,
    review_context: ReviewContext | None = None,
) -> TriageReport:
    return TriageReport(
        snapshot=snapshot,
        observations=tuple(observations),
        findings=tuple(findings),
        format_capability=capability,
        next_action=action,
        deep_read_only_allowed=action == "continue_deep_read_only",
        limits=limits,
        review_context=review_context or ReviewContext.not_applicable(),
    )


def _unsafe_name(raw: str) -> bool:
    normalized = raw.replace("\\", "/")
    logical = PurePosixPath(normalized)
    first = logical.parts[0] if logical.parts else ""
    return (
        logical.is_absolute()
        or ".." in logical.parts
        or normalized.startswith("/")
        or first.endswith(":")
    )


class EpubPreflight:
    """Classifies only whether a deeper read-only EPUB path may be considered."""

    def inspect(self, snapshot: Snapshot, limits: TriageLimits) -> TriageReport:
        observations = [
            evidence("input.size", size_bytes=snapshot.size_bytes),
            evidence("input.sha256", sha256=snapshot.sha256),
            evidence("snapshot.stable"),
        ]
        findings: list[Evidence] = []
        if snapshot.suffix == ".epub":
            observations.append(evidence("filename.extension.epub"))

        signature = snapshot.data[:8]
        if signature.startswith(b"%PDF-"):
            observations.append(evidence("format.signature.pdf"))
            findings.append(evidence("format.pdf_unsupported_for_deep_epub"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )
        if not signature.startswith(b"PK\x03\x04"):
            observations.append(evidence("format.signature_unknown"))
            if snapshot.suffix == ".epub":
                findings.append(evidence("format.extension_mismatch"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unknown",
                action="abstain",
                limits=limits,
            )

        observations.append(evidence("format.signature.zip"))
        try:
            archive = zipfile.ZipFile(io.BytesIO(snapshot.data), mode="r")
        except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile):
            observations.append(evidence("container.open_error"))
            findings.append(evidence("container.corrupt"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )

        with archive:
            return self._inspect_archive(
                archive, snapshot, limits, observations, findings
            )

    def _inspect_archive(
        self,
        archive: zipfile.ZipFile,
        snapshot: Snapshot,
        limits: TriageLimits,
        observations: list[Evidence],
        findings: list[Evidence],
    ) -> TriageReport:
        infos = archive.infolist()
        observations.append(evidence("container.entry_count", count=len(infos)))
        if len(infos) > limits.max_archive_entries:
            findings.append(
                evidence(
                    "resource.entry_limit_exceeded",
                    count=len(infos),
                    limit=limits.max_archive_entries,
                )
            )
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unknown",
                action="stop",
                limits=limits,
            )

        folded_names = [info.filename.replace("\\", "/").casefold() for info in infos]
        if len(folded_names) != len(set(folded_names)):
            findings.append(evidence("security.duplicate_entry"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unknown",
                action="stop",
                limits=limits,
            )

        escapes = sum(_unsafe_name(info.filename) for info in infos)
        if escapes:
            observations.append(
                evidence("container.entry_parent_escape", count=escapes)
            )
            findings.append(evidence("security.path_traversal"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="supported",
                action="stop",
                limits=limits,
            )

        compressed = sum(max(0, info.compress_size) for info in infos)
        expanded = sum(max(0, info.file_size) for info in infos)
        observations.extend(
            [
                evidence("container.compressed_size", size_bytes=compressed),
                evidence("container.expanded_size", size_bytes=expanded),
            ]
        )
        if expanded > limits.max_expanded_bytes:
            findings.append(
                evidence(
                    "resource.expansion_limit_exceeded",
                    expanded_bytes=expanded,
                    limit_bytes=limits.max_expanded_bytes,
                )
            )
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="supported",
                action="stop",
                limits=limits,
            )

        if any(info.flag_bits & 0x1 for info in infos):
            observations.append(evidence("container.zip_encrypted"))
            findings.append(evidence("protection.present"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )

        mimetypes = [info for info in infos if info.filename == "mimetype"]
        if len(mimetypes) != 1:
            observations.append(evidence("container.mimetype_missing_or_ambiguous"))
            findings.append(evidence("format.zip_not_epub"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )
        try:
            with archive.open(mimetypes[0], mode="r") as stream:
                mimetype = stream.read(len(b"application/epub+zip") + 1)
        except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile):
            observations.append(evidence("container.open_error"))
            findings.append(evidence("container.corrupt"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )
        if mimetype != b"application/epub+zip":
            findings.append(evidence("format.zip_not_epub"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )

        observations.append(evidence("container.mimetype.epub"))
        findings.append(evidence("format.epub"))
        if "meta-inf/encryption.xml" in folded_names:
            observations.append(evidence("container.encryption_xml"))
            findings.append(evidence("protection.present"))
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability="unsupported",
                action="stop",
                limits=limits,
            )

        scan = self._scan_markup(archive, infos, limits, observations, findings)
        if scan is not None:
            capability, action, review_context = scan
            return _report(
                snapshot=snapshot,
                observations=observations,
                findings=findings,
                capability=capability,
                action=action,
                limits=limits,
                review_context=review_context,
            )
        return _report(
            snapshot=snapshot,
            observations=observations,
            findings=findings,
            capability="supported",
            action="continue_deep_read_only",
            limits=limits,
        )

    def _scan_markup(
        self,
        archive: zipfile.ZipFile,
        infos: list[zipfile.ZipInfo],
        limits: TriageLimits,
        observations: list[Evidence],
        findings: list[Evidence],
    ) -> tuple[str, str, ReviewContext] | None:
        selected = [
            info
            for info in infos
            if not info.is_dir() and info.filename.casefold().endswith(MARKUP_SUFFIXES)
        ]
        declared_total = sum(info.file_size for info in selected)
        if declared_total > limits.max_markup_total_bytes or any(
            info.file_size > limits.max_markup_entry_bytes for info in selected
        ):
            findings.append(evidence("resource.markup_limit_exceeded"))
            return "supported", "stop", ReviewContext.not_applicable()

        has_script = False
        has_remote = False
        context_classes: set[str] = set()
        context_ambiguous = False
        actual_total = 0
        try:
            for info in selected:
                with archive.open(info, mode="r") as stream:
                    payload = stream.read(limits.max_markup_entry_bytes + 1)
                actual_total += len(payload)
                if (
                    len(payload) > limits.max_markup_entry_bytes
                    or actual_total > limits.max_markup_total_bytes
                ):
                    findings.append(evidence("resource.markup_limit_exceeded"))
                    return "supported", "stop", ReviewContext.not_applicable()
                lowered = payload.lower()
                entry_has_script = b"<script" in lowered
                entry_has_remote = REMOTE_REFERENCE.search(payload) is not None
                has_script = has_script or entry_has_script
                has_remote = has_remote or entry_has_remote
                if entry_has_script or entry_has_remote:
                    suffix = PurePosixPath(info.filename).suffix.casefold()
                    document_type = {
                        ".css": "css",
                        ".opf": "opf",
                        ".svg": "svg",
                        ".htm": "xhtml",
                        ".html": "xhtml",
                        ".xhtml": "xhtml",
                    }.get(suffix)
                    if entry_has_script:
                        context_classes.add("content.active_or_submission")
                    if document_type is None:
                        context_classes.add("ambiguous_or_deceptive")
                        context_ambiguous = True
                    else:
                        classified = classify_payload(document_type, payload)
                        if entry_has_remote:
                            if classified.scheme_group in {"http", "https"}:
                                context_classes.add(classified.context)
                            else:
                                context_classes.add("ambiguous_or_deceptive")
                                context_ambiguous = True
                        if (
                            entry_has_script
                            and classified.context == "reference.local_or_other_scheme"
                        ):
                            context_classes.add(classified.context)
                        if (
                            classified.context == "ambiguous_or_deceptive"
                            and classified.scheme_group != "none"
                        ):
                            context_classes.add("ambiguous_or_deceptive")
                            context_ambiguous = True
        except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile):
            observations.append(evidence("container.open_error"))
            findings.append(evidence("container.corrupt"))
            return "unsupported", "stop", ReviewContext.not_applicable()

        observations.append(evidence("markup.shallow_scan", size_bytes=actual_total))
        if has_script:
            observations.append(evidence("epub.script.present"))
            _append_once(findings, evidence("security.active_content"))
        if has_remote:
            observations.append(evidence("epub.remote_reference.present"))
            _append_once(findings, evidence("security.remote_resource"))
        if has_script or has_remote:
            return (
                "supported",
                "review",
                ReviewContext.for_review(
                    context_classes, ambiguous=context_ambiguous
                ),
            )
        return None
