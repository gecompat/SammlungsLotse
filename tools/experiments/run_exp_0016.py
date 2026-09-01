#!/usr/bin/env python3
"""Run the product-code-free EXP-0016 synthetic navigation safety matrix."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "ebook" / "exp-0016"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
CASE_MANIFEST_PATH = EXPERIMENT / "cases.json"
RESULT_PATH = EXPERIMENT / "result.json"
RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0016.py"

WINDOWS_TEMP_BASE = Path(r"C:\rep\tmp\SammlungsLotse\exp-0016")
WINDOWS_ARTIFACT_BASE = Path(r"C:\rep\artifacts\SammlungsLotse\exp-0016")

PROFILE_SCHEMA = "sammlungslotse/exp-0016-execution-profile/v1"
MANIFEST_SCHEMA = "sammlungslotse/exp-0016-case-manifest/v1"
RESULT_SCHEMA = "sammlungslotse/exp-0016-navigation-safety-result/v1"

CONTEXT_CLASSES = (
    "ambiguous_or_deceptive",
    "content.active_or_submission",
    "content.user_activated_hyperlink",
    "package.optional_linked_resource",
    "publication.automatic_remote_resource",
    "reference.local_or_other_scheme",
)
SCHEME_GROUPS = (
    "data_or_file",
    "helper_or_other",
    "http",
    "https",
    "local_relative_or_fragment",
    "network_path_reference",
    "none",
)
STRATEGIES = (
    "review_all_http_s",
    "classify_and_keep_review",
    "strict_navigation_candidate",
)
ACTIONS = (
    "abstain",
    "candidate_continue_deep_read_only",
    "not_remote",
    "review",
)
DOCUMENT_TYPES = ("css", "nav", "opf", "svg", "xhtml")
EXPECTED_DISTRIBUTION = {
    "ambiguous_or_deceptive": 10,
    "content.active_or_submission": 6,
    "content.user_activated_hyperlink": 8,
    "package.optional_linked_resource": 6,
    "publication.automatic_remote_resource": 10,
    "reference.local_or_other_scheme": 8,
}
EXPECTED_CASE_COUNT = 48
EXPECTED_REPETITIONS = 2
METRIC_KEYS = (
    "abstention",
    "conservative_review",
    "context_false_negative",
    "context_mismatch",
    "critical_false_continue",
)
ACCEPTANCE_KEYS = (
    "preimage_and_dependencies_bound",
    "exact_case_matrix",
    "single_oracle_per_case",
    "taxonomy_coverage",
    "document_surface_coverage",
    "scheme_groups_separate",
    "deception_controls_present",
    "ambiguous_fails_closed",
    "three_strategies_complete",
    "metrics_separate",
    "zero_critical_and_false_negative_required",
    "repetitions_identical",
    "result_recomputed_and_bound",
    "focused_controls_passed",
    "forbidden_effects_absent",
    "product_unchanged_and_cleanup_complete",
)
RESULT_FIELDS = frozenset(
    {
        "acceptance",
        "artifact",
        "bindings",
        "case_count",
        "class_counts",
        "cleanup_complete",
        "effects",
        "parser_runs",
        "path_free",
        "preimage_commit",
        "repetitions",
        "runs_semantically_identical",
        "schema",
        "scheme_counts",
        "status",
        "strategies",
    }
)
PREIMAGE_FILES = (
    "docs/planning/EBOOK_GATE_0018_AFTER_EXP0015.md",
    "docs/planning/EBOOK_PRIVATE_REMOTE_REFERENCE_CONTEXT_EXPERIMENT.md",
    "docs/planning/EBOOK_SYNTHETIC_NAVIGATION_SAFETY_MATRIX_EXPERIMENT.md",
    "experiments/ebook/exp-0016/cases.json",
    "experiments/ebook/exp-0016/execution-profile.json",
    "src/sammlungslotse/ebook_intake/preflight.py",
    "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
    "tools/experiments/run_exp_0016.py",
)
RUNTIME_LOCATORS = tuple(
    value
    for value in PREIMAGE_FILES
    if value != "experiments/ebook/exp-0016/execution-profile.json"
)

URL_LITERAL = re.compile(r"(?i)(?:https?:)?//[^\s\"'<>]+|(?:data|file|mailto|tel|ftp|urn):[^\s\"'<>]+")
REFERENCE_ATTRIBUTES = frozenset(
    {"action", "data", "formaction", "href", "poster", "src", "srcset"}
)
PRIVATE_POSIX_HOME_PREFIX = b"/ho" + b"me/"
RESOURCE_LINK_REL = frozenset(
    {"icon", "modulepreload", "preload", "stylesheet"}
)
HYPERLINK_REL = frozenset(
    {"alternate", "author", "bookmark", "external", "help", "license", "next", "prev", "search", "tag"}
)


class ExperimentError(RuntimeError):
    """Raised when an EXP-0016 contract or execution boundary is violated."""


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ExperimentError("invalid EXP-0016 arguments")


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def git_output(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise ExperimentError("read-only Git preimage check failed")
    return completed.stdout


def current_preimage() -> str:
    value = git_output("rev-parse", "HEAD").decode("ascii").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ExperimentError("invalid Git preimage")
    return value


def require_committed_preimage() -> str:
    if git_output("status", "--porcelain", "--untracked-files=all"):
        raise ExperimentError("EXP-0016 execution requires a clean preimage")
    commit = current_preimage()
    for locator in PREIMAGE_FILES:
        path = ROOT / locator
        if not path.is_file():
            raise ExperimentError("bound preimage file is missing")
        committed = git_output("show", f"{commit}:{locator}")
        if committed != path.read_bytes():
            raise ExperimentError("bound preimage differs from the worktree")
    return commit


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
) -> dict[str, str]:
    if not references:
        literal = URL_LITERAL.search(html.unescape(fallback_text))
        if literal is None:
            return {
                "context": "ambiguous_or_deceptive",
                "scheme_group": "none",
            }
        scheme_group, _ = _scheme_group(literal.group(0))
        return {
            "context": "ambiguous_or_deceptive",
            "scheme_group": scheme_group,
        }
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
        return {
            "context": "ambiguous_or_deceptive",
            "scheme_group": scheme_group,
        }
    context = references[0][0]
    if scheme_group not in {"http", "https", "network_path_reference"}:
        context = "reference.local_or_other_scheme"
    return {"context": context, "scheme_group": scheme_group}


def _classify_html(snippet: str) -> dict[str, str]:
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


def _classify_xml(snippet: str, document_type: str) -> dict[str, str]:
    try:
        root = ElementTree.fromstring(snippet)
    except ElementTree.ParseError:
        return _finalize_references([], fallback_text=snippet, forced_ambiguous=True)
    references: list[tuple[str, str, bool]] = []
    for element in root.iter():
        tag = _local_name(element.tag)
        attributes = {_local_name(name): value for name, value in element.attrib.items()}
        reference_values = [
            value
            for name, value in attributes.items()
            if name in REFERENCE_ATTRIBUTES
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


def _classify_css(snippet: str) -> dict[str, str]:
    without_comments = re.sub(r"/\*.*?\*/", "", snippet, flags=re.DOTALL)
    values = [
        match.group("value").strip(" \t\r\n\"'")
        for match in re.finditer(
            r"(?is)url\(\s*(?P<value>[^)]*?)\s*\)", without_comments
        )
    ]
    references = [
        ("publication.automatic_remote_resource", value, False)
        for value in values
    ]
    return _finalize_references(references, fallback_text=without_comments)


def classify_snippet(document_type: str, snippet: str) -> dict[str, str]:
    if document_type not in DOCUMENT_TYPES or not isinstance(snippet, str):
        raise ExperimentError("unsupported synthetic case surface")
    if not snippet or len(snippet.encode("utf-8")) > 4096:
        raise ExperimentError("synthetic snippet violates the size contract")
    if document_type == "css":
        result = _classify_css(snippet)
    elif document_type in {"opf", "svg"}:
        result = _classify_xml(snippet, document_type)
    else:
        result = _classify_html(snippet)
    if result["context"] not in CONTEXT_CLASSES:
        raise ExperimentError("parser emitted an unknown context")
    if result["scheme_group"] not in SCHEME_GROUPS:
        raise ExperimentError("parser emitted an unknown scheme group")
    return result


def strategy_action(strategy: str, context: str, scheme_group: str) -> str:
    if strategy not in STRATEGIES:
        raise ExperimentError("unknown comparison strategy")
    if context not in CONTEXT_CLASSES or scheme_group not in SCHEME_GROUPS:
        raise ExperimentError("unknown strategy input")
    if context == "ambiguous_or_deceptive" or scheme_group in {
        "network_path_reference",
        "none",
    }:
        return "abstain"
    if scheme_group == "local_relative_or_fragment":
        return "not_remote"
    if (
        strategy == "strict_navigation_candidate"
        and context == "content.user_activated_hyperlink"
        and scheme_group in {"http", "https"}
    ):
        return "candidate_continue_deep_read_only"
    return "review"


def validate_manifest(manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    if set(manifest) != {
        "artifact",
        "cases",
        "distribution",
        "schema",
        "standards_date",
    }:
        raise ExperimentError("case manifest fields differ from the contract")
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["artifact"] != "EXP-0016":
        raise ExperimentError("case manifest identity differs from the contract")
    if manifest["standards_date"] != "2026-09-01":
        raise ExperimentError("case manifest standards date differs")
    cases = manifest["cases"]
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ExperimentError("case manifest must contain exactly 48 cases")
    identifiers: set[str] = set()
    distribution: Counter[str] = Counter()
    normalized: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "case_id",
            "document_type",
            "expected_actions",
            "expected_context",
            "expected_scheme_group",
            "snippet",
        }:
            raise ExperimentError("synthetic case fields differ from the contract")
        case_id = case["case_id"]
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z]{3}-\d{3}", case_id):
            raise ExperimentError("invalid synthetic case identifier")
        if case_id in identifiers:
            raise ExperimentError("duplicate synthetic case identifier")
        identifiers.add(case_id)
        if case["document_type"] not in DOCUMENT_TYPES:
            raise ExperimentError("invalid synthetic document type")
        if case["expected_context"] not in CONTEXT_CLASSES:
            raise ExperimentError("invalid context oracle")
        if case["expected_scheme_group"] not in SCHEME_GROUPS:
            raise ExperimentError("invalid scheme oracle")
        if not isinstance(case["snippet"], str) or not case["snippet"]:
            raise ExperimentError("invalid synthetic snippet")
        if len(case["snippet"].encode("utf-8")) > 4096:
            raise ExperimentError("synthetic snippet exceeds the bound")
        actions = case["expected_actions"]
        if not isinstance(actions, dict) or set(actions) != set(STRATEGIES):
            raise ExperimentError("strategy oracle is incomplete")
        for strategy in STRATEGIES:
            expected = strategy_action(
                strategy,
                case["expected_context"],
                case["expected_scheme_group"],
            )
            if actions[strategy] != expected or expected not in ACTIONS:
                raise ExperimentError("strategy oracle differs from the bound rule")
        distribution[case["expected_context"]] += 1
        normalized.append(case)
    if dict(sorted(distribution.items())) != EXPECTED_DISTRIBUTION:
        raise ExperimentError("case distribution differs from the contract")
    if manifest["distribution"] != EXPECTED_DISTRIBUTION:
        raise ExperimentError("declared case distribution differs")
    return tuple(normalized)


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    required = {
        "artifact",
        "case_manifest",
        "cost_order",
        "execution_gate",
        "implementation",
        "output_contract",
        "parser",
        "profile_id",
        "repetitions",
        "runtime_bindings",
        "schema",
        "standards",
        "strategies",
    }
    if set(profile) != required:
        raise ExperimentError("execution profile fields differ from the contract")
    if profile["schema"] != PROFILE_SCHEMA or profile["artifact"] != "EXP-0016":
        raise ExperimentError("execution profile identity differs")
    if profile["profile_id"] != "exp-0016-navigation-safety-matrix/v1":
        raise ExperimentError("execution profile id differs")
    if profile["repetitions"] != EXPECTED_REPETITIONS:
        raise ExperimentError("execution profile repetition count differs")
    if profile["strategies"] != list(STRATEGIES):
        raise ExperimentError("execution profile strategies differ")
    if profile["cost_order"] != [
        "critical_false_continue",
        "context_false_negative",
        "context_mismatch",
        "conservative_review",
        "abstention",
    ]:
        raise ExperimentError("execution profile cost order differs")
    if profile["execution_gate"] != {
        "confirmation_flag": "--confirm-green-preimage-ci",
        "green_preimage_ci_required": True,
    }:
        raise ExperimentError("execution profile CI gate differs")
    parser = profile["parser"]
    if set(parser) != {
        "context_classes",
        "document_types",
        "implementation",
        "oracle_fields_used_for_classification",
        "scheme_groups",
    }:
        raise ExperimentError("execution profile parser fields differ")
    if parser.get("context_classes") != list(CONTEXT_CLASSES):
        raise ExperimentError("execution profile context classes differ")
    if parser.get("scheme_groups") != list(SCHEME_GROUPS):
        raise ExperimentError("execution profile scheme groups differ")
    if parser.get("document_types") != list(DOCUMENT_TYPES):
        raise ExperimentError("execution profile document types differ")
    if parser.get("implementation") != "python-3.12-standard-library":
        raise ExperimentError("execution profile parser implementation differs")
    if parser.get("oracle_fields_used_for_classification") is not False:
        raise ExperimentError("execution profile allows oracle leakage")
    implementation = profile["implementation"]
    if set(implementation) != {
        "analysis_subprocess_execution",
        "deep_tool_execution",
        "direct_database_access",
        "git_preimage_read_only_process",
        "network_access",
        "persistence",
        "private_input_access",
        "product_code_changes",
        "product_code_imports",
        "writer_surface",
    }:
        raise ExperimentError("execution profile implementation fields differ")
    if implementation.get("git_preimage_read_only_process") is not True:
        raise ExperimentError("read-only Git preimage binding is missing")
    for key, value in implementation.items():
        if key != "git_preimage_read_only_process" and value is not False:
            raise ExperimentError("execution profile permits a forbidden effect")
    manifest_binding = profile["case_manifest"]
    if manifest_binding != {
        "case_count": EXPECTED_CASE_COUNT,
        "locator": "experiments/ebook/exp-0016/cases.json",
        "sha256": sha256_file(CASE_MANIFEST_PATH),
    }:
        raise ExperimentError("case manifest binding differs")
    bindings = profile["runtime_bindings"].get("files")
    if not isinstance(bindings, list) or len(bindings) != len(RUNTIME_LOCATORS):
        raise ExperimentError("runtime binding count differs")
    for binding, locator in zip(bindings, RUNTIME_LOCATORS, strict=True):
        if binding != {"locator": locator, "sha256": sha256_file(ROOT / locator)}:
            raise ExperimentError("runtime binding differs")
    output = profile["output_contract"]
    if output.get("schema") != RESULT_SCHEMA:
        raise ExperimentError("result schema differs")
    if output.get("allowed_fields") != sorted(RESULT_FIELDS):
        raise ExperimentError("result field contract differs")
    if output.get("statuses") != ["inconclusive", "pass"]:
        raise ExperimentError("result status contract differs")
    if output.get("strategy_classifications") != [
        "eligible_with_tradeoffs",
        "not_qualified",
    ]:
        raise ExperimentError("strategy classification contract differs")
    if profile["standards"] != [
        {
            "id": "w3c-epub-33",
            "published_on": "2026-01-13",
            "url": "https://www.w3.org/TR/2026/REC-epub-33-20260113/",
        },
        {
            "id": "w3c-epub-rs-33",
            "published_on": "2024-10-17",
            "url": "https://www.w3.org/TR/2024/REC-epub-rs-33-20241017/",
        },
        {
            "id": "whatwg-html",
            "retrieved_on": "2026-09-01",
            "url": "https://html.spec.whatwg.org/",
        },
    ]:
        raise ExperimentError("standards binding differs")
    return profile


def load_contract() -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    profile = validate_profile(load_json(PROFILE_PATH))
    cases = validate_manifest(load_json(CASE_MANIFEST_PATH))
    return profile, cases


def _run_repetition(cases: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    for case in cases:
        actual = classify_snippet(case["document_type"], case["snippet"])
        actions = {
            strategy: strategy_action(
                strategy, actual["context"], actual["scheme_group"]
            )
            for strategy in STRATEGIES
        }
        outcomes.append(
            {
                "case_id": case["case_id"],
                "context": actual["context"],
                "scheme_group": actual["scheme_group"],
                "actions": actions,
            }
        )
    return outcomes


def _strategy_metrics(
    strategy: str,
    cases: tuple[dict[str, Any], ...],
    outcomes: list[dict[str, Any]],
) -> dict[str, int]:
    by_id = {outcome["case_id"]: outcome for outcome in outcomes}
    metrics = {key: 0 for key in METRIC_KEYS}
    for case in cases:
        actual = by_id[case["case_id"]]
        actual_action = actual["actions"][strategy]
        expected_action = case["expected_actions"][strategy]
        mismatch = (
            actual["context"] != case["expected_context"]
            or actual["scheme_group"] != case["expected_scheme_group"]
            or actual_action != expected_action
        )
        if mismatch:
            metrics["context_mismatch"] += 1
        if (
            case["expected_scheme_group"] != "none"
            and actual["scheme_group"] == "none"
        ) or (
            expected_action in {"review", "candidate_continue_deep_read_only"}
            and actual_action == "not_remote"
        ):
            metrics["context_false_negative"] += 1
        if (
            actual_action == "candidate_continue_deep_read_only"
            and expected_action != "candidate_continue_deep_read_only"
        ):
            metrics["critical_false_continue"] += 1
        if (
            case["expected_context"] == "content.user_activated_hyperlink"
            and case["expected_scheme_group"] in {"http", "https"}
            and actual_action == "review"
        ):
            metrics["conservative_review"] += 1
        if actual_action == "abstain":
            metrics["abstention"] += 1
    return metrics


def _strategy_result(metrics: dict[str, int]) -> dict[str, Any]:
    qualified = (
        metrics["critical_false_continue"] == 0
        and metrics["context_false_negative"] == 0
        and metrics["context_mismatch"] == 0
    )
    return {
        "classification": (
            "eligible_with_tradeoffs" if qualified else "not_qualified"
        ),
        "metrics": metrics,
    }


def build_result(
    *,
    preimage_commit: str,
    profile: dict[str, Any],
    cases: tuple[dict[str, Any], ...],
    repetitions: list[list[dict[str, Any]]],
    cleanup_complete: bool,
    green_preimage_ci_confirmed: bool,
) -> dict[str, Any]:
    identical = len(repetitions) == EXPECTED_REPETITIONS and all(
        canonical_bytes(value) == canonical_bytes(repetitions[0])
        for value in repetitions[1:]
    )
    first = repetitions[0] if repetitions else []
    strategy_results = {
        strategy: _strategy_result(_strategy_metrics(strategy, cases, first))
        for strategy in STRATEGIES
    }
    class_counts = dict(
        sorted(Counter(case["expected_context"] for case in cases).items())
    )
    scheme_counts = dict(
        sorted(Counter(case["expected_scheme_group"] for case in cases).items())
    )
    effects = {
        "deep_tool_execution": False,
        "domain_system_writes": False,
        "network_access": False,
        "persistence": False,
        "private_inputs": False,
        "product_code_imported": False,
        "product_code_modified": False,
    }
    all_metrics_present = all(
        set(value["metrics"]) == set(METRIC_KEYS)
        for value in strategy_results.values()
    )
    hard_thresholds_applied = all(
        (value["classification"] == "eligible_with_tradeoffs")
        == (
            value["metrics"]["critical_false_continue"] == 0
            and value["metrics"]["context_false_negative"] == 0
            and value["metrics"]["context_mismatch"] == 0
        )
        for value in strategy_results.values()
    )
    acceptance = {
        "preimage_and_dependencies_bound": bool(profile["runtime_bindings"]["files"]),
        "exact_case_matrix": len(cases) == EXPECTED_CASE_COUNT,
        "single_oracle_per_case": all(
            case["expected_context"] in CONTEXT_CLASSES
            and case["expected_scheme_group"] in SCHEME_GROUPS
            for case in cases
        ),
        "taxonomy_coverage": set(class_counts) == set(CONTEXT_CLASSES)
        and set(scheme_counts) == set(SCHEME_GROUPS) - {"none"},
        "document_surface_coverage": set(case["document_type"] for case in cases)
        == set(DOCUMENT_TYPES),
        "scheme_groups_separate": len(scheme_counts) == 6,
        "deception_controls_present": class_counts.get("ambiguous_or_deceptive") == 10,
        "ambiguous_fails_closed": all(
            outcome["actions"][strategy] == "abstain"
            for case, outcome in zip(cases, first, strict=True)
            if case["expected_context"] == "ambiguous_or_deceptive"
            for strategy in STRATEGIES
        ),
        "three_strategies_complete": set(strategy_results) == set(STRATEGIES),
        "metrics_separate": all_metrics_present,
        "zero_critical_and_false_negative_required": hard_thresholds_applied,
        "repetitions_identical": identical,
        "result_recomputed_and_bound": all(
            profile["case_manifest"][key]
            == {
                "case_count": EXPECTED_CASE_COUNT,
                "locator": "experiments/ebook/exp-0016/cases.json",
                "sha256": sha256_file(CASE_MANIFEST_PATH),
            }[key]
            for key in ("case_count", "locator", "sha256")
        ),
        "focused_controls_passed": green_preimage_ci_confirmed,
        "forbidden_effects_absent": not any(effects.values()),
        "product_unchanged_and_cleanup_complete": cleanup_complete
        and effects["product_code_modified"] is False,
    }
    status = "pass" if all(acceptance.values()) else "inconclusive"
    return {
        "acceptance": acceptance,
        "artifact": "EXP-0016",
        "bindings": {
            "case_manifest_sha256": sha256_file(CASE_MANIFEST_PATH),
            "execution_profile_sha256": sha256_file(PROFILE_PATH),
            "runner_sha256": sha256_file(RUNNER_PATH),
        },
        "case_count": len(cases),
        "class_counts": class_counts,
        "cleanup_complete": cleanup_complete,
        "effects": effects,
        "parser_runs": len(cases) * len(repetitions),
        "path_free": True,
        "preimage_commit": preimage_commit,
        "repetitions": len(repetitions),
        "runs_semantically_identical": identical,
        "schema": RESULT_SCHEMA,
        "scheme_counts": scheme_counts,
        "status": status,
        "strategies": strategy_results,
    }


def validate_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    if set(result) != RESULT_FIELDS:
        raise ExperimentError("result fields differ from the contract")
    if result["schema"] != RESULT_SCHEMA or result["artifact"] != "EXP-0016":
        raise ExperimentError("result identity differs from the contract")
    if not re.fullmatch(r"[0-9a-f]{40}", result["preimage_commit"]):
        raise ExperimentError("result preimage is invalid")
    if result["case_count"] != EXPECTED_CASE_COUNT:
        raise ExperimentError("result case count differs")
    if result["repetitions"] != EXPECTED_REPETITIONS:
        raise ExperimentError("result repetition count differs")
    if result["parser_runs"] != EXPECTED_CASE_COUNT * EXPECTED_REPETITIONS:
        raise ExperimentError("result parser run count differs")
    if result["class_counts"] != EXPECTED_DISTRIBUTION:
        raise ExperimentError("result class counts differ")
    manifest = validate_manifest(load_json(CASE_MANIFEST_PATH))
    expected_scheme_counts = dict(
        sorted(Counter(case["expected_scheme_group"] for case in manifest).items())
    )
    if result["scheme_counts"] != expected_scheme_counts:
        raise ExperimentError("result scheme counts differ")
    expected_bindings = {
        "case_manifest_sha256": sha256_file(CASE_MANIFEST_PATH),
        "execution_profile_sha256": sha256_file(PROFILE_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
    }
    if result["bindings"] != expected_bindings:
        raise ExperimentError("result bindings differ")
    if result["effects"] != {
        "deep_tool_execution": False,
        "domain_system_writes": False,
        "network_access": False,
        "persistence": False,
        "private_inputs": False,
        "product_code_imported": False,
        "product_code_modified": False,
    }:
        raise ExperimentError("result effects differ")
    if set(result["acceptance"]) != set(ACCEPTANCE_KEYS):
        raise ExperimentError("result acceptance keys differ")
    if any(type(value) is not bool for value in result["acceptance"].values()):
        raise ExperimentError("result acceptance value differs")
    if not isinstance(result["strategies"], dict) or set(result["strategies"]) != set(
        STRATEGIES
    ):
        raise ExperimentError("result strategies differ")
    for strategy in STRATEGIES:
        strategy_result = result["strategies"][strategy]
        if not isinstance(strategy_result, dict) or set(strategy_result) != {
            "classification",
            "metrics",
        }:
            raise ExperimentError("result strategy fields differ")
        metrics = strategy_result["metrics"]
        if not isinstance(metrics, dict) or set(metrics) != set(METRIC_KEYS):
            raise ExperimentError("result strategy metric fields differ")
        if any(
            type(value) is not int or value < 0 or value > EXPECTED_CASE_COUNT
            for value in metrics.values()
        ):
            raise ExperimentError("result strategy metric value differs")
        if strategy_result != _strategy_result(metrics):
            raise ExperimentError("result strategy classification differs")
    expected_status = "pass" if all(result["acceptance"].values()) else "inconclusive"
    if result["status"] != expected_status:
        raise ExperimentError("result method status differs")
    for field in ("cleanup_complete", "path_free"):
        if result[field] is not True:
            raise ExperimentError("result boundary proof is incomplete")
    if (
        result["runs_semantically_identical"]
        is not result["acceptance"]["repetitions_identical"]
    ):
        raise ExperimentError("result repetition proof differs")
    if (
        b"C:\\" in canonical_bytes(result)
        or PRIVATE_POSIX_HOME_PREFIX in canonical_bytes(result)
    ):
        raise ExperimentError("result contains a host path")
    return result


def validate_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    return validate_result_dict(load_json(path))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _prepare_execution_paths(temp_root: Path, result_path: Path) -> tuple[Path, Path]:
    if os.name == "nt":
        resolved_temp = temp_root.resolve()
        resolved_result = result_path.resolve()
        allowed_temp = WINDOWS_TEMP_BASE.resolve()
        allowed_artifact = WINDOWS_ARTIFACT_BASE.resolve()
        if resolved_temp != allowed_temp and not _is_within(resolved_temp, allowed_temp):
            raise ExperimentError("temp root is outside the EXP-0016 project boundary")
        if not _is_within(resolved_result, allowed_artifact):
            raise ExperimentError("result is outside the EXP-0016 artifact boundary")
    if result_path.exists():
        raise ExperimentError("result target already exists")
    temp_root.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    task_root = temp_root / f"task-{secrets.token_hex(12)}"
    task_root.mkdir(mode=0o700)
    return task_root, result_path


def _cleanup_task(task_root: Path, temp_root: Path) -> bool:
    resolved_task = task_root.resolve()
    resolved_root = temp_root.resolve()
    if resolved_task.parent != resolved_root or not task_root.name.startswith("task-"):
        raise ExperimentError("refusing to clean an unowned task path")
    shutil.rmtree(task_root)
    return not task_root.exists()


def _write_result_once(path: Path, result: dict[str, Any]) -> None:
    payload = canonical_bytes(result)
    if len(payload) > 16384:
        raise ExperimentError("result exceeds the output limit")
    with path.open("xb") as stream:
        stream.write(payload)


def execute(
    *,
    temp_root: Path,
    result_path: Path,
    green_preimage_ci_confirmed: bool,
    preimage_commit: str | None = None,
) -> dict[str, Any]:
    if not green_preimage_ci_confirmed:
        raise ExperimentError("green preimage CI confirmation is required")
    profile, cases = load_contract()
    commit = preimage_commit or require_committed_preimage()
    task_root, output = _prepare_execution_paths(temp_root, result_path)
    repetitions: list[list[dict[str, Any]]] = []
    cleanup_complete = False
    try:
        repetitions = [
            _run_repetition(cases) for _ in range(profile["repetitions"])
        ]
    finally:
        cleanup_complete = _cleanup_task(task_root, temp_root)
    result = build_result(
        preimage_commit=commit,
        profile=profile,
        cases=cases,
        repetitions=repetitions,
        cleanup_complete=cleanup_complete,
        green_preimage_ci_confirmed=green_preimage_ci_confirmed,
    )
    validate_result_dict(result)
    _write_result_once(output, result)
    return result


def parser() -> SafeArgumentParser:
    result = SafeArgumentParser(description=__doc__)
    mode = result.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-profile", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--validate-result", action="store_true")
    result.add_argument("--temp-root", type=Path)
    result.add_argument("--result", type=Path, default=RESULT_PATH)
    result.add_argument("--confirm-green-preimage-ci", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        if args.validate_profile:
            profile, cases = load_contract()
            commit = require_committed_preimage()
            print(
                "EXP-0016 profile valid: "
                f"preimage={commit} cases={len(cases)} strategies={len(profile['strategies'])}"
            )
            return 0
        if args.validate_result:
            result = validate_result(args.result)
            print(
                "EXP-0016 result valid: "
                f"preimage={result['preimage_commit']} cases={result['case_count']} "
                f"status={result['status']}"
            )
            return 0
        if args.temp_root is None:
            raise ExperimentError("EXP-0016 execution requires --temp-root")
        result = execute(
            temp_root=args.temp_root,
            result_path=args.result,
            green_preimage_ci_confirmed=args.confirm_green_preimage_ci,
        )
        print(
            "EXP-0016 executed: "
            f"cases={result['case_count']} repetitions={result['repetitions']} "
            f"status={result['status']}"
        )
        return 0
    except (ExperimentError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
