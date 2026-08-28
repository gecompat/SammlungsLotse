"""Bounded in-memory EPUB evidence adapter and conservative identity rules."""

from __future__ import annotations

import hashlib
import io
import json
import re
import unicodedata
import zipfile
from pathlib import PurePosixPath
from xml.etree import ElementTree

from sammlungslotse.ebook_intake.model import Snapshot

from .model import EmbeddedMetadata, IdentityLimits, InputObservation, StageResult


SAMPLE_TERMS = ("leseprobe", "sample", "excerpt")


def _canonical_digest(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _unsafe_name(raw: str) -> bool:
    normalized = raw.replace("\\", "/")
    logical = PurePosixPath(normalized)
    first = logical.parts[0] if logical.parts else ""
    return logical.is_absolute() or ".." in logical.parts or normalized.startswith("/") or first.endswith(":")


def _xml_values(root: ElementTree.Element, name: str) -> tuple[str, ...]:
    namespace = "http://purl.org/dc/elements/1.1/"
    return tuple(
        value
        for element in root.findall(f".//{{{namespace}}}{name}")
        if (value := " ".join("".join(element.itertext()).split()))
    )


def _resolve_member(base: PurePosixPath, href: str) -> str:
    candidate = PurePosixPath(base, href.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("EPUB manifest locator escapes package")
    return candidate.as_posix()


def _read_epub(snapshot: Snapshot, index: int, limits: IdentityLimits) -> InputObservation:
    try:
        archive = zipfile.ZipFile(io.BytesIO(snapshot.data), mode="r")
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise ValueError("EPUB package cannot be opened") from exc
    with archive:
        infos = archive.infolist()
        if len(infos) > limits.max_archive_entries:
            raise ValueError("EPUB entry limit exceeded")
        folded = [item.filename.replace("\\", "/").casefold() for item in infos]
        if len(folded) != len(set(folded)):
            raise ValueError("EPUB duplicate logical entry")
        if any(_unsafe_name(item.filename) for item in infos):
            raise ValueError("EPUB path traversal")
        if any(item.flag_bits & 0x1 for item in infos):
            raise ValueError("EPUB encrypted ZIP entry")
        expanded = sum(max(0, item.file_size) for item in infos)
        if expanded > limits.max_expanded_bytes:
            raise ValueError("EPUB expanded-byte limit exceeded")
        entries: dict[str, bytes] = {}
        try:
            for info in infos:
                if info.is_dir():
                    continue
                payload = archive.read(info)
                if len(payload) != info.file_size:
                    raise ValueError("EPUB entry size differs")
                entries[info.filename.replace("\\", "/")] = payload
        except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile) as exc:
            raise ValueError("EPUB entry cannot be read") from exc

    try:
        container = ElementTree.fromstring(entries["META-INF/container.xml"])
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("EPUB package locator missing")
        package_name = PurePosixPath(rootfile.get("full-path", "")).as_posix()
        if _unsafe_name(package_name) or package_name not in entries:
            raise ValueError("EPUB package locator invalid")
        package = ElementTree.fromstring(entries[package_name])
    except (KeyError, ElementTree.ParseError) as exc:
        raise ValueError("EPUB package metadata invalid") from exc

    package_base = PurePosixPath(package_name).parent
    manifest: dict[str, tuple[str, str]] = {}
    for item in package.findall(".//{http://www.idpf.org/2007/opf}manifest/{http://www.idpf.org/2007/opf}item"):
        item_id, href = item.get("id"), item.get("href")
        if not item_id or not href or item_id in manifest:
            raise ValueError("EPUB manifest differs")
        manifest[item_id] = (_resolve_member(package_base, href), item.get("media-type", ""))
    spine_ids = [
        value
        for item in package.findall(".//{http://www.idpf.org/2007/opf}spine/{http://www.idpf.org/2007/opf}itemref")
        if (value := item.get("idref"))
    ]
    if not spine_ids or any(item_id not in manifest for item_id in spine_ids):
        raise ValueError("EPUB spine differs")
    representation = {
        "manifest": [
            {"media_type": media_type, "name": name}
            for name, media_type in sorted(manifest.values())
        ],
        "spine": [],
    }
    content = []
    for item_id in spine_ids:
        name, media_type = manifest[item_id]
        if name not in entries:
            raise ValueError("EPUB spine resource missing")
        try:
            root = ElementTree.fromstring(entries[name])
        except ElementTree.ParseError as exc:
            raise ValueError("EPUB spine markup invalid") from exc
        text = _normalized(" ".join(root.itertext()))
        representation["spine"].append(
            {"media_type": media_type, "name": name, "text": text}
        )
        content.append(text)

    package_projection = [
        {"name": name, "sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)}
        for name, payload in sorted(entries.items())
    ]
    work_references = tuple(
        value
        for item in package.findall(".//{http://www.idpf.org/2007/opf}meta")
        if item.get("property") == "belongs-to-collection"
        if (value := " ".join("".join(item.itertext()).split()))
    )
    metadata = EmbeddedMetadata(
        titles=_xml_values(package, "title"),
        creators=_xml_values(package, "creator"),
        languages=_xml_values(package, "language"),
        identifiers=_xml_values(package, "identifier"),
        work_references=work_references,
    )
    return InputObservation(
        input_index=index,
        sha256=snapshot.sha256,
        size_bytes=snapshot.size_bytes,
        package_sha256=_canonical_digest(package_projection),
        representation_sha256=_canonical_digest(representation),
        content_sha256=_canonical_digest(content),
        entry_count=len(infos),
        expanded_bytes=expanded,
        metadata=metadata,
    )


def _normalized_set(values: tuple[str, ...]) -> set[str]:
    return {_normalized(value) for value in values if _normalized(value)}


def _metadata_evidence(first: EmbeddedMetadata, second: EmbeddedMetadata) -> tuple[list[str], list[str], list[str], dict[str, bool]]:
    positive: list[str] = []
    negative: list[str] = []
    missing: list[str] = []
    flags: dict[str, bool] = {}
    for field in ("titles", "creators", "languages", "identifiers", "work_references"):
        left = _normalized_set(getattr(first, field))
        right = _normalized_set(getattr(second, field))
        flags[f"{field}_present"] = bool(left and right)
        flags[f"{field}_overlap"] = bool(left & right)
        flags[f"{field}_equal"] = bool(left and right and left == right)
        if not left or not right:
            missing.append(f"metadata.{field}_missing")
        elif left & right:
            positive.append(f"metadata.{field}_overlap")
        else:
            negative.append(f"metadata.{field}_conflict")
    left_titles = _normalized_set(first.titles)
    right_titles = _normalized_set(second.titles)
    flags["sample_conflict"] = any(term in title for title in left_titles for term in SAMPLE_TERMS) != any(
        term in title for title in right_titles for term in SAMPLE_TERMS
    )
    if flags["sample_conflict"]:
        negative.append("metadata.sample_full_conflict")
    return positive, negative, missing, flags


def analyze_pair(first: Snapshot, second: Snapshot, limits: IdentityLimits) -> tuple[tuple[InputObservation, InputObservation], tuple[StageResult, ...], str]:
    if first.size_bytes + second.size_bytes > limits.max_total_input_bytes:
        raise ValueError("pair input limit exceeded")
    observed = (_read_epub(first, 1, limits), _read_epub(second, 2, limits))
    left, right = observed
    byte_equal = left.sha256 == right.sha256
    package_equal = left.package_sha256 == right.package_sha256
    representation_equal = left.representation_sha256 == right.representation_sha256
    stages = [
        StageResult("byte", "candidate_same" if byte_equal else "different", "identity.byte.sha256", ("byte.sha256_equal",) if byte_equal else (), ("byte.sha256_differs",) if not byte_equal else ()),
        StageResult("package", "candidate_same" if package_equal else "different", "identity.package.canonical_entries", ("package.entries_equal",) if package_equal else (), ("package.entries_differ",) if not package_equal else ()),
        StageResult("representation", "candidate_same" if representation_equal else "different", "identity.representation.spine_text", ("representation.spine_text_equal",) if representation_equal else (), ("representation.spine_text_differs",) if not representation_equal else ()),
    ]
    positive, negative, missing, flags = _metadata_evidence(left.metadata, right.metadata)
    if flags["sample_conflict"]:
        edition_decision, edition_rule = "different", "identity.edition.sample_full_conflict"
    elif flags["languages_present"] and not flags["languages_overlap"]:
        edition_decision, edition_rule = "different", "identity.edition.language_conflict"
    elif flags["identifiers_overlap"] and not flags["titles_present"]:
        edition_decision, edition_rule = "abstain", "identity.edition.identifier_without_title"
    elif flags["identifiers_overlap"] and flags["titles_overlap"] and (flags["creators_overlap"] or not flags["creators_present"]):
        edition_decision, edition_rule = "candidate_same", "identity.edition.identifier_title"
    elif representation_equal and flags["titles_overlap"] and (flags["creators_overlap"] or not flags["creators_present"]):
        edition_decision, edition_rule = "candidate_same", "identity.edition.representation_metadata"
    else:
        edition_decision, edition_rule = "abstain", "identity.edition.insufficient_evidence"
    edition = StageResult("edition", edition_decision, edition_rule, tuple(sorted(positive)), tuple(sorted(negative)), tuple(sorted(missing)))
    stages.append(edition)

    if edition_decision == "candidate_same":
        work_decision, work_rule = "candidate_same", "identity.work.same_edition"
    elif flags["work_references_overlap"]:
        work_decision, work_rule = "candidate_related", "identity.work.explicit_reference"
    elif flags["titles_overlap"] and flags["creators_overlap"]:
        work_decision, work_rule = "candidate_related", "identity.work.title_creator"
    elif flags["titles_overlap"] and flags["creators_present"] and not flags["creators_overlap"]:
        work_decision, work_rule = "different", "identity.work.title_collision"
    else:
        work_decision, work_rule = "abstain", "identity.work.insufficient_evidence"
    work = StageResult("work", work_decision, work_rule, tuple(sorted(positive)), tuple(sorted(negative)), tuple(sorted(missing)))
    stages.append(work)

    if byte_equal:
        overall = "exact_byte_match"
    elif representation_equal:
        overall = "representation_candidate"
    elif edition_decision == "candidate_same":
        overall = "edition_candidate"
    elif work_decision == "candidate_related":
        overall = "related_work_candidate"
    elif edition_decision == "different" and work_decision == "different":
        overall = "no_candidate"
    else:
        overall = "abstain"
    return observed, tuple(stages), overall
