"""Bounded context classification for the additive WI-0014 projection."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from xml.etree import ElementTree


CONTEXT_CLASSES = frozenset(
    {
        "ambiguous_or_deceptive",
        "content.active_or_submission",
        "content.user_activated_hyperlink",
        "package.optional_linked_resource",
        "publication.automatic_remote_resource",
        "reference.local_or_other_scheme",
    }
)
SCHEME_GROUPS = frozenset(
    {
        "data_or_file",
        "helper_or_other",
        "http",
        "https",
        "local_relative_or_fragment",
        "network_path_reference",
        "none",
    }
)
DOCUMENT_TYPES = frozenset({"css", "nav", "opf", "svg", "xhtml"})
URL_LITERAL = re.compile(
    r"(?i)(?:https?:)?//[^\s\"'<>]+|"
    r"(?:data|file|mailto|tel|ftp|urn):[^\s\"'<>]+"
)
REFERENCE_ATTRIBUTES = frozenset(
    {"action", "data", "formaction", "href", "poster", "src", "srcset"}
)
RESOURCE_LINK_REL = frozenset(
    {"icon", "modulepreload", "preload", "stylesheet"}
)
HYPERLINK_REL = frozenset(
    {
        "alternate",
        "author",
        "bookmark",
        "external",
        "help",
        "license",
        "next",
        "prev",
        "search",
        "tag",
    }
)


@dataclass(frozen=True, slots=True)
class ContextClassification:
    """One path- and value-free document-level context projection."""

    context: str
    scheme_group: str

    def __post_init__(self) -> None:
        if self.context not in CONTEXT_CLASSES:
            raise ValueError("unknown context class")
        if self.scheme_group not in SCHEME_GROUPS:
            raise ValueError("unknown scheme group")


def _local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1].rsplit(":", 1)[-1].lower()


def _scheme_group(value: str) -> tuple[str, bool]:
    decoded = html.unescape(value)
    surrounding_whitespace = decoded != decoded.strip()
    stripped = decoded.strip()
    control_present = any(character in stripped for character in "\r\n\t")
    normalized = stripped.replace("\r", "").replace("\n", "").replace("\t", "")
    if not normalized:
        return "none", surrounding_whitespace or control_present
    if normalized.startswith("//"):
        return "network_path_reference", True
    if normalized.startswith("#") or normalized.startswith(("./", "../", "/")):
        return "local_relative_or_fragment", surrounding_whitespace or control_present
    match = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", normalized)
    if match is None:
        return "local_relative_or_fragment", surrounding_whitespace or control_present
    scheme = match.group(1).lower()
    if scheme in {"http", "https"}:
        return scheme, surrounding_whitespace or control_present
    if scheme in {"data", "file"}:
        return "data_or_file", surrounding_whitespace or control_present
    return "helper_or_other", surrounding_whitespace or control_present


class _MarkupCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, list[tuple[str, str | None]]]] = []
        self.comments: list[str] = []
        self.script_literals: list[str] = []
        self._script_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        lowered = tag.lower()
        self.elements.append((lowered, [(name.lower(), value) for name, value in attrs]))
        if lowered == "script":
            self._script_depth += 1

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() == "script":
            self._script_depth -= 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._script_depth:
            self._script_depth -= 1

    def handle_comment(self, data: str) -> None:
        self.comments.append(data)

    def handle_data(self, data: str) -> None:
        if self._script_depth:
            self.script_literals.append(data)


def _markup_reference(
    tag: str, attributes: list[tuple[str, str | None]]
) -> tuple[str, str, bool] | None:
    values: dict[str, list[str]] = {}
    for name, value in attributes:
        local = _local_name(name)
        if value is not None:
            values.setdefault(local, []).append(value)
    reference_values = [
        value
        for name, items in values.items()
        if name in REFERENCE_ATTRIBUTES
        for value in items
    ]
    if not reference_values:
        return None
    if len(reference_values) != 1:
        return "ambiguous_or_deceptive", reference_values[0], True
    reference = reference_values[0]
    local_tag = _local_name(tag)
    if ":" in tag:
        return "ambiguous_or_deceptive", reference, True
    if local_tag in {"a", "area"} and "href" in values:
        return "content.user_activated_hyperlink", reference, False
    if local_tag == "link" and "href" in values:
        rel = {
            token.lower()
            for item in values.get("rel", [])
            for token in item.split()
        }
        if rel & RESOURCE_LINK_REL and rel & HYPERLINK_REL:
            return "ambiguous_or_deceptive", reference, True
        if rel & RESOURCE_LINK_REL:
            return "publication.automatic_remote_resource", reference, False
        if rel and rel <= HYPERLINK_REL:
            return "content.user_activated_hyperlink", reference, False
        return "ambiguous_or_deceptive", reference, True
    automatic = {
        "audio": {"src"},
        "iframe": {"src"},
        "img": {"src", "srcset"},
        "object": {"data"},
        "source": {"src", "srcset"},
        "track": {"src"},
        "video": {"poster", "src"},
    }
    active = {
        "button": {"formaction"},
        "embed": {"src"},
        "form": {"action"},
        "input": {"formaction"},
        "script": {"src"},
    }
    if local_tag in automatic and set(values) & automatic[local_tag]:
        return "publication.automatic_remote_resource", reference, False
    if local_tag in active and set(values) & active[local_tag]:
        return "content.active_or_submission", reference, False
    return "ambiguous_or_deceptive", reference, True


def _finalize_references(
    references: list[tuple[str, str, bool]],
    *,
    fallback_text: str,
    forced_ambiguous: bool = False,
) -> ContextClassification:
    if not references:
        literal = URL_LITERAL.search(html.unescape(fallback_text))
        if literal is None:
            return ContextClassification("ambiguous_or_deceptive", "none")
        scheme_group, _ = _scheme_group(literal.group(0))
        return ContextClassification("ambiguous_or_deceptive", scheme_group)
    groups = [_scheme_group(reference) for _, reference, _ in references]
    distinct_groups = {group for group, _ in groups}
    scheme_group = next(iter(distinct_groups)) if len(distinct_groups) == 1 else "none"
    ambiguous = (
        forced_ambiguous
        or len(references) != 1
        or any(marker for _, _, marker in references)
        or any(marker for _, marker in groups)
        or scheme_group == "network_path_reference"
    )
    if ambiguous:
        return ContextClassification("ambiguous_or_deceptive", scheme_group)
    context = references[0][0]
    if scheme_group not in {"http", "https", "network_path_reference"}:
        context = "reference.local_or_other_scheme"
    return ContextClassification(context, scheme_group)


def _classify_html(snippet: str) -> ContextClassification:
    malformed = snippet.count("<") != snippet.count(">")
    collector = _MarkupCollector()
    try:
        collector.feed(snippet)
        collector.close()
    except (AssertionError, TypeError, ValueError):
        malformed = True
    references = [
        reference
        for tag, attributes in collector.elements
        if (reference := _markup_reference(tag, attributes)) is not None
    ]
    literal_ambiguity = any(
        URL_LITERAL.search(value) is not None
        for value in (*collector.comments, *collector.script_literals)
    )
    return _finalize_references(
        references,
        fallback_text=snippet,
        forced_ambiguous=malformed or literal_ambiguity,
    )


def _classify_xml(snippet: str, document_type: str) -> ContextClassification:
    try:
        root = ElementTree.fromstring(snippet)
    except ElementTree.ParseError:
        return _finalize_references([], fallback_text=snippet, forced_ambiguous=True)
    references: list[tuple[str, str, bool]] = []
    for element in root.iter():
        tag = _local_name(element.tag)
        attributes = {_local_name(name): value for name, value in element.attrib.items()}
        reference_values = [
            value for name, value in attributes.items() if name in REFERENCE_ATTRIBUTES
        ]
        if not reference_values:
            continue
        if len(reference_values) != 1:
            references.append(("ambiguous_or_deceptive", reference_values[0], True))
            continue
        reference = reference_values[0]
        if document_type == "opf":
            if tag == "link" and "href" in attributes:
                context = "package.optional_linked_resource"
            elif tag == "item" and "href" in attributes:
                context = "publication.automatic_remote_resource"
            else:
                context = "ambiguous_or_deceptive"
        else:
            if tag == "a" and "href" in attributes:
                context = "content.user_activated_hyperlink"
            elif tag in {"image", "use"} and "href" in attributes:
                context = "publication.automatic_remote_resource"
            elif tag == "script" and "href" in attributes:
                context = "content.active_or_submission"
            else:
                context = "ambiguous_or_deceptive"
        references.append((context, reference, context == "ambiguous_or_deceptive"))
    return _finalize_references(references, fallback_text=snippet)


def _classify_css(snippet: str) -> ContextClassification:
    without_comments = re.sub(r"/\*.*?\*/", "", snippet, flags=re.DOTALL)
    values = [
        match.group("value").strip(" \t\r\n\"'")
        for match in re.finditer(
            r"(?is)url\(\s*(?P<value>[^)]*?)\s*\)", without_comments
        )
    ]
    references = [
        ("publication.automatic_remote_resource", value, False) for value in values
    ]
    return _finalize_references(references, fallback_text=without_comments)


def classify_document(document_type: str, snippet: str) -> ContextClassification:
    """Classify one bounded document without retaining its source values."""

    if document_type not in DOCUMENT_TYPES or not isinstance(snippet, str) or not snippet:
        return ContextClassification("ambiguous_or_deceptive", "none")
    try:
        if document_type == "css":
            return _classify_css(snippet)
        if document_type in {"opf", "svg"}:
            return _classify_xml(snippet, document_type)
        return _classify_html(snippet)
    except (AssertionError, TypeError, ValueError):
        return ContextClassification("ambiguous_or_deceptive", "none")


def classify_payload(document_type: str, payload: bytes) -> ContextClassification:
    """Decode already-bounded bytes; decoding failure remains explicitly ambiguous."""

    try:
        snippet = payload.decode("utf-8-sig", errors="strict")
    except UnicodeError:
        return ContextClassification("ambiguous_or_deceptive", "none")
    return classify_document(document_type, snippet)
