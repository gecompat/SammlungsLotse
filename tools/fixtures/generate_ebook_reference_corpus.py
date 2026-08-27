#!/usr/bin/env python3
"""Generate the deterministic synthetic TEST-0001 core fixture corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import zipfile
from dataclasses import dataclass
from html import escape
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.1"
FIXTURE_VERSION = "0.1.0"
CREATED_ON = "2026-08-27"
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)

CORE_CASE_KEYS = (
    "ingress-stable-minimal",
    "ingress-growing-file",
    "container-corrupt",
    "container-path-traversal",
    "container-expansion-limit",
    "protected-or-encrypted",
    "format-unknown",
    "epub33-valid-reflow",
    "epub-missing-resource",
    "epub-navigation-defect",
    "epub-active-or-remote",
    "epub-a11y-auto-finding",
    "epub-a11y-manual-required",
    "metadata-conflict-title",
    "metadata-contributor-roles",
    "edition-sample-vs-full",
    "identity-byte-equal",
    "identity-repackaged",
    "identity-multiformat-edition",
    "identity-edition-vs-translation",
    "identity-title-collision",
    "routing-unique",
    "routing-ambiguous",
    "run-unchanged-skip",
    "run-resume",
    "run-tool-timeout",
)

DEFERRED_EXPANSION_CASE_KEYS = (
    "epub2-valid-minimal",
    "epub33-valid-fixed",
    "metadata-multilingual-rtl",
    "routing-unknown",
)

COMMON_FORBIDDEN_EFFECTS = (
    "modify_original",
    "network_access",
    "write_domain_system",
)


@dataclass(frozen=True)
class Component:
    name: str
    role: str
    content: bytes
    media_type: str


@dataclass(frozen=True)
class Case:
    case_key: str
    scenarios: tuple[str, ...]
    construction: str
    fixture_nature: str
    components: tuple[Component, ...]
    oracle: dict[str, Any]


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_portable_text(path: Path) -> str:
    raw = path.read_bytes().decode("utf-8")
    logical = raw.replace("\r\n", "\n").encode("utf-8")
    return sha256_bytes(logical)


def zip_info(name: str, compression: int = zipfile.ZIP_DEFLATED) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = compression
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def zip_bytes(
    entries: Iterable[tuple[str, bytes, int]], *, comment: bytes = b""
) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content, compression in entries:
            archive.writestr(zip_info(name, compression), content)
        archive.comment = comment
    return buffer.getvalue()


def container_xml() -> bytes:
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def nav_xhtml(target: str = "chapter.xhtml") -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="de">
  <head><title>Navigation</title></head>
  <body><nav epub:type="toc"><ol><li><a href="{escape(target)}">Kapitel</a></li></ol></nav></body>
</html>
""".encode("utf-8")


def chapter_xhtml(
    text: str,
    *,
    body_extra: str = "",
    language: str = "de",
) -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{escape(language)}">
  <head><title>Kapitel</title></head>
  <body><h1>Kapitel</h1><p>{escape(text)}</p>{body_extra}</body>
</html>
""".encode("utf-8")


def image_svg() -> bytes:
    return b"""<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
  <rect width="40" height="40" fill="#334455"/>
</svg>
"""


def package_opf(
    *,
    title: str,
    identifier: str,
    language: str,
    default_creator: str | None = "Alex Beispiel",
    chapter_href: str = "chapter.xhtml",
    include_image: bool = False,
    image_properties: str = "",
    extra_manifest: str = "",
    extra_metadata: str = "",
) -> bytes:
    properties = (
        f' properties="{escape(image_properties)}"' if image_properties else ""
    )
    image_item = (
        f'\n    <item id="image" href="image.svg" media-type="image/svg+xml"{properties}/>'
        if include_image
        else ""
    )
    creator = (
        f"\n    <dc:creator>{escape(default_creator)}</dc:creator>"
        if default_creator is not None
        else ""
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.3" unique-identifier="book-id" xml:lang="{escape(language)}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">{escape(identifier)}</dc:identifier>
    <dc:title>{escape(title)}</dc:title>
    <dc:language>{escape(language)}</dc:language>{creator}{extra_metadata}
    <meta property="dcterms:modified">2020-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter" href="{escape(chapter_href)}" media-type="application/xhtml+xml"/>{image_item}{extra_manifest}
  </manifest>
  <spine><itemref idref="chapter"/></spine>
</package>
""".encode("utf-8")


def epub_bytes(
    *,
    title: str,
    identifier: str,
    language: str = "de",
    default_creator: str | None = "Alex Beispiel",
    text: str = "Dies ist ein vollständig synthetischer Testtext.",
    nav_target: str = "chapter.xhtml",
    chapter_href: str = "chapter.xhtml",
    include_chapter: bool = True,
    include_image: bool = False,
    image_properties: str = "",
    body_extra: str = "",
    extra_entries: tuple[tuple[str, bytes, int], ...] = (),
    extra_manifest: str = "",
    extra_metadata: str = "",
    reverse_payload_order: bool = False,
    comment: bytes = b"",
) -> bytes:
    entries: list[tuple[str, bytes, int]] = [
        ("mimetype", b"application/epub+zip", zipfile.ZIP_STORED),
        ("META-INF/container.xml", container_xml(), zipfile.ZIP_DEFLATED),
        (
            "EPUB/package.opf",
            package_opf(
                title=title,
                identifier=identifier,
                language=language,
                default_creator=default_creator,
                chapter_href=chapter_href,
                include_image=include_image,
                image_properties=image_properties,
                extra_manifest=extra_manifest,
                extra_metadata=extra_metadata,
            ),
            zipfile.ZIP_DEFLATED,
        ),
        ("EPUB/nav.xhtml", nav_xhtml(nav_target), zipfile.ZIP_DEFLATED),
    ]
    if include_chapter:
        entries.append(
            (
                "EPUB/chapter.xhtml",
                chapter_xhtml(text, body_extra=body_extra, language=language),
                zipfile.ZIP_DEFLATED,
            )
        )
    if include_image:
        entries.append(("EPUB/image.svg", image_svg(), zipfile.ZIP_DEFLATED))
    entries.extend(extra_entries)
    if reverse_payload_order:
        entries = [entries[0], *reversed(entries[1:])]
    return zip_bytes(entries, comment=comment)


def minimal_pdf(title: str, text: str) -> bytes:
    safe_title = title.replace("(", "[").replace(")", "]")
    safe_text = text.replace("(", "[").replace(")", "]")
    stream = f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET\n".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Title ({safe_title}) /Producer (SammlungsLotse TEST-0001) >>".encode(
            "ascii"
        ),
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, value in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(value)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info 6 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def component(name: str, role: str, content: bytes, media_type: str) -> Component:
    return Component(name=name, role=role, content=content, media_type=media_type)


def oracle(
    *,
    observations: Iterable[str],
    findings: Iterable[str],
    allowed_results: Iterable[str],
    forbidden_results: Iterable[str],
    quality_dimensions: Iterable[str],
    method: str,
    forbidden_effects: Iterable[str] = (),
    resource_overrides: dict[str, Any] | None = None,
    expected_relationship: dict[str, str] | None = None,
    expected_routing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resource_profile: dict[str, Any] = {
        "network": "denied",
        "max_input_bytes": 262144,
        "max_expanded_bytes": 1048576,
        "timeout_ms": 2000,
        "abort_condition": "declared limit reached or input snapshot changed",
    }
    if resource_overrides:
        resource_profile.update(resource_overrides)
    value: dict[str, Any] = {
        "expected_observations": list(observations),
        "expected_findings": list(findings),
        "allowed_results": list(allowed_results),
        "forbidden_results": list(forbidden_results),
        "forbidden_effects": sorted(
            set(COMMON_FORBIDDEN_EFFECTS).union(forbidden_effects)
        ),
        "quality_dimensions": list(quality_dimensions),
        "resource_profile": resource_profile,
        "validation": {
            "method": method,
            "manual_steps": [],
        },
    }
    if expected_relationship is not None:
        value["expected_relationship"] = expected_relationship
    if expected_routing is not None:
        value["expected_routing"] = expected_routing
    return value


def build_cases() -> tuple[Case, ...]:
    minimal = epub_bytes(
        title="Stabiler Eingang",
        identifier="urn:test:stable-minimal",
    )
    valid_reflow = epub_bytes(
        title="Valides EPUB 3.3",
        identifier="urn:test:epub33-valid-reflow",
        include_image=True,
        image_properties="cover-image",
    )
    base_identity = epub_bytes(
        title="Die stille Karte",
        identifier="urn:test:representation:quiet-map",
        text="Eine synthetische Erzählung über eine stille Karte.",
    )
    contributor_metadata = """
    <dc:creator id="creator-author">Alex Beispiel</dc:creator>
    <meta refines="#creator-author" property="role" scheme="marc:relators">aut</meta>
    <dc:contributor id="contributor-translator">Alex Beispiels</dc:contributor>
    <meta refines="#contributor-translator" property="role" scheme="marc:relators">trl</meta>
    <dc:contributor id="contributor-editor">Alexa Beispiel</dc:contributor>
    <meta refines="#contributor-editor" property="role" scheme="marc:relators">edt</meta>"""
    remote_body = (
        '<script type="application/javascript">document.body.dataset.synthetic="true";</script>'
        '<img src="https://example.invalid/test-0001/remote.svg" alt="Synthetische Remote-Ressource"/>'
    )
    auto_a11y_body = '<img src="image.svg"/>'
    manual_a11y_body = '<img src="image.svg" alt="Bild"/>'
    protection_entries = (
        (
            "META-INF/encryption.xml",
            b"""<?xml version="1.0" encoding="UTF-8"?>
<encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <EncryptedData xmlns="http://www.w3.org/2001/04/xmlenc#">
    <EncryptionMethod Algorithm="urn:sammlungslotse:synthetic:no-decryption"/>
    <CipherData><CipherReference URI="EPUB/encrypted.dat"/></CipherData>
  </EncryptedData>
</encryption>
""",
            zipfile.ZIP_DEFLATED,
        ),
        ("EPUB/encrypted.dat", b"SYNTHETIC-PROTECTED-MARKER\n", zipfile.ZIP_DEFLATED),
    )
    protection_manifest = (
        '\n    <item id="protected" href="encrypted.dat" '
        'media-type="application/octet-stream"/>'
    )
    traversal = zip_bytes(
        (
            ("mimetype", b"application/epub+zip", zipfile.ZIP_STORED),
            ("../escape.txt", b"SYNTHETIC-TRAVERSAL-MARKER\n", zipfile.ZIP_DEFLATED),
            ("META-INF/container.xml", container_xml(), zipfile.ZIP_DEFLATED),
        )
    )
    expansion = zip_bytes(
        (
            ("mimetype", b"application/epub+zip", zipfile.ZIP_STORED),
            ("EPUB/repeated.txt", b"A" * 65536, zipfile.ZIP_DEFLATED),
        )
    )
    corrupt = minimal[: max(80, len(minimal) // 3)]

    sample = epub_bytes(
        title="Die lange Reise — Leseprobe",
        identifier="urn:test:edition:long-journey:sample",
        text="Kurze synthetische Leseprobe.",
    )
    full = epub_bytes(
        title="Die lange Reise",
        identifier="urn:test:edition:long-journey:full",
        text=" ".join(
            f"Synthetischer Vollausgabe-Abschnitt {index:02d} mit Merkmal {index * 17}."
            for index in range(1, 41)
        ),
    )
    translation_de = epub_bytes(
        title="Der gläserne Garten",
        identifier="urn:test:edition:glass-garden:de",
        language="de",
        text="Eine deutsche synthetische Übersetzung.",
        extra_metadata='\n    <meta property="belongs-to-collection">urn:test:work:glass-garden</meta>',
    )
    translation_en = epub_bytes(
        title="The Glass Garden",
        identifier="urn:test:edition:glass-garden:en",
        language="en",
        text="An English synthetic source edition.",
        extra_metadata='\n    <meta property="belongs-to-collection">urn:test:work:glass-garden</meta>',
    )
    collision_a = epub_bytes(
        title="Der letzte Schlüssel",
        identifier="urn:test:work:last-key:a",
        text="Ein synthetischer Text über Kryptografie.",
        default_creator=None,
        extra_metadata="\n    <dc:creator>Mara Nord</dc:creator>",
    )
    collision_b = epub_bytes(
        title="Der letzte Schlüssel",
        identifier="urn:test:work:last-key:b",
        text="Ein synthetischer Text über eine alte Tür.",
        default_creator=None,
        extra_metadata="\n    <dc:creator>Jonas Süd</dc:creator>",
    )

    routing_targets = {
        "schema_version": 1,
        "targets": [
            {
                "target_key": "technical-library",
                "label": "Technikbestand",
                "rules": {"include_subjects": ["technik"], "languages": ["de", "en"]},
                "read_only_snapshot": {
                    "interface": "synthetic-contract-snapshot/v1",
                    "public_locator": "target:technical-library",
                    "fields": ["book_key", "title", "contributors", "languages", "formats", "custom_columns"],
                    "books": [
                        {
                            "book_key": "technical-book-1",
                            "title": "Synthetische Technikfibel",
                            "contributors": [{"name": "Alex Beispiel", "role": "author"}],
                            "languages": ["de"],
                            "formats": ["EPUB", "PDF"],
                            "custom_columns": {"topic": "technik"},
                        }
                    ],
                },
            },
            {
                "target_key": "young-readers-library",
                "label": "Junge Lesende",
                "rules": {"include_subjects": ["jugend"], "languages": ["de"]},
                "read_only_snapshot": {
                    "interface": "synthetic-contract-snapshot/v1",
                    "public_locator": "target:young-readers-library",
                    "fields": ["book_key", "title", "contributors", "languages", "formats", "custom_columns"],
                    "books": [
                        {
                            "book_key": "young-readers-book-1",
                            "title": "Synthetische Abenteuerkarte",
                            "contributors": [{"name": "Robin Muster", "role": "author"}],
                            "languages": ["de"],
                            "formats": ["EPUB"],
                            "custom_columns": {"topic": "jugend"},
                        }
                    ],
                },
            },
        ],
        "write_operations": [],
    }
    unique_item = {
        "item_key": "routing-unique-item",
        "observations": {"subjects": ["technik"], "language": "de"},
    }
    ambiguous_item = {
        "item_key": "routing-ambiguous-item",
        "observations": {"subjects": ["technik", "jugend"], "language": "de"},
    }

    cases = (
        Case(
            "ingress-stable-minimal",
            ("S2",),
            "Deterministisches minimales EPUB mit abgeschlossenem Snapshot.",
            "valid_reference",
            (component("stable.epub", "input", minimal, "application/epub+zip"),),
            oracle(
                observations=("input.size", "input.sha256", "format.signature", "snapshot.stable"),
                findings=("format.epub",),
                allowed_results=("observation", "finding"),
                forbidden_results=("proposal.import",),
                quality_dimensions=("ingress", "provenance"),
                method="Hash, Größe, ZIP-Signatur und zweifache unveränderte Lesung prüfen.",
            ),
        ),
        Case(
            "ingress-growing-file",
            ("S2",),
            "Zwei deterministische Revisionen desselben noch wachsenden Eingangs.",
            "behavioral_simulation",
            (
                component("revision-1.part", "input_revision", b"SYNTHETIC-PART-1\n", "application/octet-stream"),
                component("revision-2.part", "input_revision", b"SYNTHETIC-PART-1\nSYNTHETIC-PART-2\n", "application/octet-stream"),
                component(
                    "observations.json",
                    "snapshot",
                    canonical_json({"logical_locator": "inbox/growing.epub", "sequence": ["revision-1.part", "revision-2.part"]}),
                    "application/json",
                ),
            ),
            oracle(
                observations=("snapshot.size_changed", "snapshot.sha256_changed"),
                findings=("ingress.unstable",),
                allowed_results=("finding", "abstain"),
                forbidden_results=("analysis.deep_completed",),
                quality_dimensions=("ingress", "continuous_quality"),
                method="Revisionen in deklarierter Reihenfolge lesen und unterschiedliche Größe sowie Hash belegen.",
            ),
        ),
        Case(
            "container-corrupt",
            ("S2",),
            "Abgeschnittene Kopie des synthetischen Minimal-EPUB.",
            "intentionally_invalid",
            (component("corrupt.epub", "input", corrupt, "application/epub+zip"),),
            oracle(
                observations=("format.zip_signature", "container.open_error"),
                findings=("container.corrupt",),
                allowed_results=("finding", "unsupported"),
                forbidden_results=("format.valid",),
                quality_dimensions=("integrity", "security"),
                method="Archivöffnung muss begrenzt fehlschlagen; Eingang bleibt bytegleich.",
            ),
        ),
        Case(
            "container-path-traversal",
            ("S2",),
            "ZIP enthält absichtlich den synthetischen Eintrag ../escape.txt.",
            "intentionally_invalid",
            (component("traversal.epub", "input", traversal, "application/epub+zip"),),
            oracle(
                observations=("container.entry_parent_escape",),
                findings=("security.path_traversal",),
                allowed_results=("finding",),
                forbidden_results=("container.safe_to_extract",),
                forbidden_effects=("extract_outside_workspace",),
                quality_dimensions=("integrity", "security"),
                method="Nur Eintragsnamen inspizieren; keine Archivextraktion ausführen.",
            ),
        ),
        Case(
            "container-expansion-limit",
            ("S2",),
            "Kleines ZIP mit 65536 stark komprimierbaren synthetischen Bytes.",
            "resource_limit",
            (component("expansion.epub", "input", expansion, "application/epub+zip"),),
            oracle(
                observations=("container.compressed_size", "container.expanded_size"),
                findings=("resource.expansion_limit_exceeded",),
                allowed_results=("finding", "abstain"),
                forbidden_results=("analysis.unbounded",),
                quality_dimensions=("integrity", "security", "runtime"),
                method="Deklarierte ZIP-Größen gegen das kleine Testlimit prüfen, ohne zu extrahieren.",
                resource_overrides={"max_expanded_bytes": 1024, "abort_condition": "declared expanded size exceeds 1024 bytes"},
            ),
        ),
        Case(
            "protected-or-encrypted",
            ("S2",),
            "EPUB mit ungefährlichem synthetischem Schutzmarker und encryption.xml.",
            "synthetic_protection_marker",
            (
                component(
                    "protected.epub",
                    "input",
                    epub_bytes(
                        title="Synthetisch geschützt",
                        identifier="urn:test:protected",
                        extra_entries=protection_entries,
                        extra_manifest=protection_manifest,
                    ),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("container.encryption_xml", "resource.synthetic_protection_marker"),
                findings=("protection.present",),
                allowed_results=("finding", "unsupported"),
                forbidden_results=("protection.decrypted",),
                forbidden_effects=("bypass_protection",),
                quality_dimensions=("security", "format"),
                method="encryption.xml und Marker erkennen; keine Entschlüsselung versuchen.",
            ),
        ),
        Case(
            "format-unknown",
            ("S2",),
            "Unbekannte synthetische Signatur trotz Dateiendung .epub.",
            "unsupported_format",
            (component("unknown.epub", "input", b"SL-UNKNOWN-FORMAT\x00\x01\n", "application/octet-stream"),),
            oracle(
                observations=("filename.extension.epub", "format.signature_unknown"),
                findings=("format.extension_mismatch",),
                allowed_results=("unknown", "unsupported", "finding"),
                forbidden_results=("format.epub" ,),
                quality_dimensions=("ingress", "format"),
                method="Signatur vor Endung auswerten und tiefe Analyse unterlassen.",
            ),
        ),
        Case(
            "epub33-valid-reflow",
            ("S2",),
            "Minimales deterministisches EPUB 3.3 mit Navigation.",
            "valid_reference",
            (component("valid-reflow.epub", "input", valid_reflow, "application/epub+zip"),),
            oracle(
                observations=("epub.version.3.3", "epub.navigation.present", "epub.cover.present", "epub.spine.complete"),
                findings=(),
                allowed_results=("observation", "not_applicable"),
                forbidden_results=("finding.synthetic_error", "accessibility.conformant"),
                quality_dimensions=("format", "accessibility"),
                method="OCF-, Package-, Manifest-, Spine- und Navigationsstruktur prüfen.",
            ),
        ),
        Case(
            "epub-missing-resource",
            ("S2",),
            "OPF referenziert chapter.xhtml, der Archiveintrag fehlt absichtlich.",
            "intentionally_invalid",
            (
                component(
                    "missing-resource.epub",
                    "input",
                    epub_bytes(title="Fehlende Ressource", identifier="urn:test:missing-resource", include_chapter=False),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("epub.manifest.chapter_declared", "container.entry.chapter_missing"),
                findings=("epub.resource_missing",),
                allowed_results=("finding",),
                forbidden_results=("format.valid",),
                quality_dimensions=("format", "integrity"),
                method="Manifestreferenz gegen Archiveinträge prüfen.",
            ),
        ),
        Case(
            "epub-navigation-defect",
            ("S2",),
            "Navigation verweist absichtlich auf eine nicht vorhandene Ressource.",
            "intentionally_invalid",
            (
                component(
                    "navigation-defect.epub",
                    "input",
                    epub_bytes(title="Defekte Navigation", identifier="urn:test:navigation-defect", nav_target="missing-nav-target.xhtml"),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("epub.navigation.present", "epub.navigation.target_missing"),
                findings=("epub.navigation_defect",),
                allowed_results=("finding",),
                forbidden_results=("epub.navigation_valid",),
                quality_dimensions=("format", "usability"),
                method="Navigationsziele getrennt von Package-Öffnbarkeit prüfen.",
            ),
        ),
        Case(
            "epub-active-or-remote",
            ("S2",),
            "EPUB enthält Skript und eine example.invalid-Remote-Referenz.",
            "intentionally_risky",
            (
                component(
                    "active-remote.epub",
                    "input",
                    epub_bytes(title="Aktiver Inhalt", identifier="urn:test:active-remote", body_extra=remote_body),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("epub.script.present", "epub.remote_reference.present"),
                findings=("security.active_content", "security.remote_resource"),
                allowed_results=("finding", "abstain"),
                forbidden_results=("remote_resource.fetched",),
                forbidden_effects=("execute_embedded_script",),
                quality_dimensions=("security", "format"),
                method="Markup als Daten inspizieren; Skript und URL niemals ausführen oder abrufen.",
            ),
        ),
        Case(
            "epub-a11y-auto-finding",
            ("S2",),
            "EPUB-Bild ohne alt-Attribut für einen automatisierbaren Sollbefund.",
            "intentionally_invalid",
            (
                component(
                    "a11y-auto.epub",
                    "input",
                    epub_bytes(title="A11y automatisch", identifier="urn:test:a11y-auto", include_image=True, body_extra=auto_a11y_body),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("epub.image.present", "epub.image.alt_missing"),
                findings=("accessibility.text_alternative_missing",),
                allowed_results=("finding",),
                forbidden_results=("accessibility.conformant",),
                quality_dimensions=("accessibility",),
                method="img-Element und fehlendes alt-Attribut strukturell prüfen.",
            ),
        ),
        Case(
            "epub-a11y-manual-required",
            ("S2",),
            "EPUB-Bild mit syntaktisch vorhandenem, aber inhaltlich schwachem alt-Text.",
            "manual_review_required",
            (
                component(
                    "a11y-manual.epub",
                    "input",
                    epub_bytes(title="A11y manuell", identifier="urn:test:a11y-manual", include_image=True, body_extra=manual_a11y_body),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("epub.image.present", "epub.image.alt_present"),
                findings=("accessibility.manual_review_required",),
                allowed_results=("finding", "abstain"),
                forbidden_results=("accessibility.conformant", "accessibility.text_alternative_adequate"),
                quality_dimensions=("accessibility",),
                method="Vorhandensein automatisch prüfen; inhaltliche Eignung ausdrücklich offenlassen.",
            ),
        ),
        Case(
            "metadata-conflict-title",
            ("S4",),
            "EPUB-Titel, synthetischer Locator und Calibre-Snapshot widersprechen sich.",
            "metadata_conflict",
            (
                component(
                    "dateiname-titel.epub",
                    "input",
                    epub_bytes(title="Paket-Titel", identifier="urn:test:metadata-conflict-title"),
                    "application/epub+zip",
                ),
                component(
                    "calibre-snapshot.json",
                    "snapshot",
                    canonical_json({"book_key": "synthetic-book-17", "title": "Calibre-Titel", "formats": ["EPUB"]}),
                    "application/json",
                ),
            ),
            oracle(
                observations=("title.package", "title.locator", "title.calibre_snapshot"),
                findings=("metadata.title_conflict",),
                allowed_results=("finding", "candidate", "abstain"),
                forbidden_results=("metadata.title_overwritten",),
                quality_dimensions=("metadata", "provenance"),
                method="Drei Titelbeobachtungen mit getrennter Provenienz erfassen.",
            ),
        ),
        Case(
            "metadata-contributor-roles",
            ("S4",),
            "Ähnliche synthetische Namen mit Autor-, Übersetzer- und Herausgeberrolle.",
            "valid_reference",
            (
                component(
                    "contributor-roles.epub",
                    "input",
                    epub_bytes(title="Rollenbeispiel", identifier="urn:test:contributor-roles", default_creator=None, extra_metadata=contributor_metadata),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("contributor.author", "contributor.translator", "contributor.editor"),
                findings=(),
                allowed_results=("observation", "candidate"),
                forbidden_results=("contributor.roles_collapsed", "person.identities_merged"),
                quality_dimensions=("metadata", "identity", "provenance"),
                method="Personenbeiträge und MARC-Rollencodes getrennt auslesen.",
            ),
        ),
        Case(
            "edition-sample-vs-full",
            ("S3",),
            "Ähnliche Metadaten, aber getrennte synthetische Leseprobe und Vollausgabe.",
            "relationship_pair",
            (
                component("sample.epub", "input", sample, "application/epub+zip"),
                component("full.epub", "input", full, "application/epub+zip"),
            ),
            oracle(
                observations=("edition.metadata_similar", "content.extent_differs"),
                findings=("edition.sample_vs_full",),
                allowed_results=("candidate", "finding", "abstain"),
                forbidden_results=("representation.interchangeable",),
                quality_dimensions=("identity", "completeness"),
                method="Metadatenähnlichkeit und Inhaltsumfang getrennt vergleichen.",
                expected_relationship={"file": "different", "representation": "different", "edition": "different_or_related", "work": "candidate_same"},
            ),
        ),
        Case(
            "identity-byte-equal",
            ("S3",),
            "Exakt dieselben EPUB-Bytes unter zwei synthetischen Locators.",
            "relationship_pair",
            (
                component("source-a/same.epub", "input", base_identity, "application/epub+zip"),
                component("source-b/renamed.epub", "input", base_identity, "application/epub+zip"),
            ),
            oracle(
                observations=("file.sha256_equal", "locator.distinct"),
                findings=("identity.byte_equal",),
                allowed_results=("candidate", "finding"),
                forbidden_results=("locator.merged",),
                forbidden_effects=("merge_identity", "remove_file"),
                quality_dimensions=("identity", "provenance"),
                method="Bytehashes vergleichen und beide Locators erhalten.",
                expected_relationship={"file": "same", "representation": "candidate_same", "edition": "candidate_same", "work": "candidate_same"},
            ),
        ),
        Case(
            "identity-repackaged",
            ("S3",),
            "Gleiche logische EPUB-Einträge mit anderer ZIP-Reihenfolge und Kommentar.",
            "relationship_pair",
            (
                component("package-a.epub", "input", base_identity, "application/epub+zip"),
                component(
                    "package-b.epub",
                    "input",
                    epub_bytes(
                        title="Die stille Karte",
                        identifier="urn:test:representation:quiet-map",
                        text="Eine synthetische Erzählung über eine stille Karte.",
                        reverse_payload_order=True,
                        comment=b"synthetic-repackaging",
                    ),
                    "application/epub+zip",
                ),
            ),
            oracle(
                observations=("file.sha256_different", "package.entries_equal"),
                findings=("identity.representation_candidate",),
                allowed_results=("candidate", "abstain"),
                forbidden_results=("identity.byte_equal",),
                forbidden_effects=("merge_identity", "remove_file"),
                quality_dimensions=("identity",),
                method="Bytehash und normalisierte Eintragsinhalte getrennt vergleichen.",
                expected_relationship={"file": "different", "representation": "candidate_same", "edition": "candidate_same", "work": "candidate_same"},
            ),
        ),
        Case(
            "identity-multiformat-edition",
            ("S3",),
            "Synthetische EPUB- und PDF-Repräsentation derselben Ausgabe.",
            "relationship_pair",
            (
                component(
                    "edition.epub",
                    "input",
                    epub_bytes(title="Mehrformat-Ausgabe", identifier="urn:test:edition:multi-format", text="Gleiche Ausgabe in EPUB."),
                    "application/epub+zip",
                ),
                component("edition.pdf", "input", minimal_pdf("Mehrformat-Ausgabe", "Gleiche Ausgabe in PDF."), "application/pdf"),
                component(
                    "bibliographic-key.json",
                    "snapshot",
                    canonical_json({"edition_key": "urn:test:edition:multi-format", "formats": ["EPUB", "PDF"]}),
                    "application/json",
                ),
            ),
            oracle(
                observations=("format.epub", "format.pdf", "edition.identifier_equal"),
                findings=("identity.edition_candidate",),
                allowed_results=("candidate", "abstain"),
                forbidden_results=("identity.file_equal", "identity.representation_equal"),
                forbidden_effects=("merge_identity", "remove_file"),
                quality_dimensions=("identity", "metadata"),
                method="Format- und Dateiebene getrennt vom gemeinsamen Ausgabenschlüssel bewerten.",
                expected_relationship={"file": "different", "representation": "different", "edition": "candidate_same", "work": "candidate_same"},
            ),
        ),
        Case(
            "identity-edition-vs-translation",
            ("S3",),
            "Synthetische Ausgangsausgabe und Übersetzung desselben Werkbezugs.",
            "relationship_pair",
            (
                component("source-en.epub", "input", translation_en, "application/epub+zip"),
                component("translation-de.epub", "input", translation_de, "application/epub+zip"),
            ),
            oracle(
                observations=("language.different", "edition.identifier_different", "work.reference_equal"),
                findings=("identity.work_candidate", "identity.translation"),
                allowed_results=("candidate", "abstain"),
                forbidden_results=("identity.edition_equal", "representation.interchangeable"),
                forbidden_effects=("merge_identity", "remove_file"),
                quality_dimensions=("identity", "metadata"),
                method="Sprachen und Ausgabenidentifikatoren als negative Evidenz erhalten.",
                expected_relationship={"file": "different", "representation": "different", "edition": "different", "work": "candidate_related"},
            ),
        ),
        Case(
            "identity-title-collision",
            ("S3",),
            "Zwei verschiedene synthetische Werke mit identischem Titel.",
            "negative_relationship_pair",
            (
                component("work-a.epub", "input", collision_a, "application/epub+zip"),
                component("work-b.epub", "input", collision_b, "application/epub+zip"),
            ),
            oracle(
                observations=("title.equal", "creator.different", "content.different", "work.identifier_different"),
                findings=("identity.title_collision",),
                allowed_results=("finding", "abstain"),
                forbidden_results=("identity.work_equal",),
                forbidden_effects=("merge_identity", "remove_file"),
                quality_dimensions=("identity", "metadata"),
                method="Gleichen Titel als positives, übrige Merkmale als negative Evidenz ausweisen.",
                expected_relationship={"file": "different", "representation": "different", "edition": "different", "work": "different"},
            ),
        ),
        Case(
            "routing-unique",
            ("S6",),
            "Zwei synthetische Zielregeln und ein eindeutig passender Technik-Eingang.",
            "routing_scenario",
            (
                component("targets.json", "snapshot", canonical_json(routing_targets), "application/json"),
                component("item.json", "input", canonical_json(unique_item), "application/json"),
            ),
            oracle(
                observations=("routing.target_rules", "item.subject.technik", "item.language.de"),
                findings=("routing.single_candidate",),
                allowed_results=("candidate",),
                forbidden_results=("proposal.import",),
                forbidden_effects=("choose_target_as_write", "execute_writer"),
                quality_dimensions=("routing", "provenance"),
                method="Regeln als reine Daten auswerten; genau einen Kandidaten erwarten.",
                expected_routing={"result": "candidate", "target_key": "technical-library", "executed": False},
            ),
        ),
        Case(
            "routing-ambiguous",
            ("S6",),
            "Zwei synthetische Zielregeln passen gleichzeitig zum Eingang.",
            "routing_scenario",
            (
                component("targets.json", "snapshot", canonical_json(routing_targets), "application/json"),
                component("item.json", "input", canonical_json(ambiguous_item), "application/json"),
            ),
            oracle(
                observations=("routing.target_rules", "item.subject.technik", "item.subject.jugend"),
                findings=("routing.conflict",),
                allowed_results=("abstain",),
                forbidden_results=("routing.single_candidate", "proposal.import"),
                forbidden_effects=("choose_default_target", "execute_writer"),
                quality_dimensions=("routing", "provenance"),
                method="Alle passenden Ziele ermitteln und bei Mehrdeutigkeit Enthaltung erwarten.",
                expected_routing={"result": "abstain", "candidate_target_keys": ["technical-library", "young-readers-library"], "executed": False},
            ),
        ),
        Case(
            "run-unchanged-skip",
            ("S1", "S2"),
            "Zwei semantisch identische Lauf-Snapshots desselben Eingangs und Profils.",
            "behavioral_simulation",
            (
                component("input.epub", "input", minimal, "application/epub+zip"),
                component("run-1.json", "snapshot", canonical_json({"input": "input.epub", "profile": "synthetic-profile/v1", "revision": "same"}), "application/json"),
                component("run-2.json", "snapshot", canonical_json({"input": "input.epub", "profile": "synthetic-profile/v1", "revision": "same"}), "application/json"),
            ),
            oracle(
                observations=("snapshot.input_equal", "snapshot.profile_equal"),
                findings=("analysis.reusable",),
                allowed_results=("finding", "not_applicable"),
                forbidden_results=("analysis.recomputed_without_reason",),
                quality_dimensions=("continuous_quality", "runtime"),
                method="Lauf-Snapshots und Eingangs-Hash vergleichen; keine Analyse ausführen.",
            ),
        ),
        Case(
            "run-resume",
            ("S1", "S2"),
            "Kontrollierter synthetischer Checkpoint nach einem bekannten Schritt.",
            "behavioral_simulation",
            (
                component("input.epub", "input", minimal, "application/epub+zip"),
                component("checkpoint.json", "snapshot", canonical_json({"completed_steps": ["snapshot", "hash"], "next_step": "format", "result_keys": ["input.size", "input.sha256"]}), "application/json"),
                component("expected-resume.json", "control", canonical_json({"resume_from": "format", "repeat_steps": [], "preserve_result_keys": ["input.size", "input.sha256"]}), "application/json"),
            ),
            oracle(
                observations=("checkpoint.valid", "checkpoint.input_hash_equal"),
                findings=("run.resumable",),
                allowed_results=("finding",),
                forbidden_results=("result.duplicated", "result.lost"),
                quality_dimensions=("continuous_quality", "runtime"),
                method="Checkpoint und erwarteten Fortsetzungsschritt strukturell vergleichen.",
            ),
        ),
        Case(
            "run-tool-timeout",
            ("S2",),
            "Synthetischer Python-Helfer überschreitet absichtlich ein kleines Zeitlimit.",
            "resource_limit",
            (
                component("input.epub", "input", minimal, "application/epub+zip"),
                component("slow_tool.py", "synthetic_tool", b"import time\ntime.sleep(5)\n", "text/x-python"),
                component("tool-profile.json", "control", canonical_json({"command": ["python", "slow_tool.py"], "timeout_ms": 100, "network": "not_used", "allowed_outputs": []}), "application/json"),
            ),
            oracle(
                observations=("tool.timeout", "tool.exit_bounded"),
                findings=("runtime.timeout_enforced",),
                allowed_results=("finding", "abstain"),
                forbidden_results=("tool.completed",),
                forbidden_effects=("leave_child_process", "write_outside_temporary_area"),
                quality_dimensions=("runtime", "security", "integrity"),
                method="Helfer in isoliertem temporärem Arbeitsordner mit 100-ms-Timeout ausführen.",
                resource_overrides={"timeout_ms": 100, "abort_condition": "synthetic helper exceeds 100 ms"},
            ),
        ),
    )
    if tuple(case.case_key for case in cases) != CORE_CASE_KEYS:
        raise RuntimeError("generator case order does not match CORE_CASE_KEYS")
    return cases


def safe_relative_component(case_key: str, name: str) -> PurePosixPath:
    relative = PurePosixPath("cases") / case_key / name
    if relative.is_absolute() or ".." in relative.parts or "\\" in relative.as_posix():
        raise ValueError(f"unsafe component path: {relative}")
    return relative


def generate(output: Path) -> dict[str, Any]:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(
            f"output already exists; choose an empty new path: {output}"
        )
    output.mkdir(parents=True)

    source_path = Path(__file__).resolve()
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "corpus_ref": "TEST-0001",
        "fixture_version": FIXTURE_VERSION,
        "created_on": CREATED_ON,
        "scope": "core",
        "data_class": "SYNTHETIC_OR_REDISTRIBUTABLE",
        "license": {
            "spdx": "MIT",
            "locator": "LICENSE",
        },
        "generator_profile": {
            "id": "sammlungslotse-test-0001-generator",
            "version": FIXTURE_VERSION,
            "implementation": "tools/fixtures/generate_ebook_reference_corpus.py",
            "implementation_digest_algorithm": "sha256-utf8-lf",
            "implementation_sha256": sha256_portable_text(source_path),
            "runtime_contract": "Python 3.12+ standard library",
            "network": "not_used",
            "external_dependencies": [],
        },
        "deferred_expansion_case_keys": list(DEFERRED_EXPANSION_CASE_KEYS),
        "cases": [],
    }

    for case in build_cases():
        component_records: list[dict[str, Any]] = []
        for item in case.components:
            relative = safe_relative_component(case.case_key, item.name)
            target = output / Path(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(item.content)
            component_records.append(
                {
                    "path": relative.as_posix(),
                    "role": item.role,
                    "media_type": item.media_type,
                    "size_bytes": len(item.content),
                    "sha256": sha256_bytes(item.content),
                }
            )
        manifest["cases"].append(
            {
                "case_key": case.case_key,
                "stage": "core",
                "scenarios": list(case.scenarios),
                "construction": case.construction,
                "fixture_nature": case.fixture_nature,
                "components": component_records,
                "provenance": {
                    "source": "independently generated from repository-owned literal synthetic content",
                    "generator": "sammlungslotse-test-0001-generator",
                    "third_party_material": False,
                    "license_spdx": "MIT",
                },
                "oracle": case.oracle,
            }
        )

    (output / "manifest.json").write_bytes(canonical_json(manifest))
    return manifest


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="new output directory; an existing path is rejected",
    )
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        manifest = generate(args.output)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[BLOCK] TEST-0001 generation failed: {exc}", file=sys.stderr)
        return 2
    component_count = sum(len(case["components"]) for case in manifest["cases"])
    print(
        f"[OK] generated TEST-0001 {manifest['fixture_version']} "
        f"cases={len(manifest['cases'])} components={component_count} "
        f"path={args.output.resolve()}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
