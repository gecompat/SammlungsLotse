from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import time
import unicodedata
import zipfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = Path(__file__).resolve()
CORPUS_ROOT = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2"
MANIFEST_PATH = CORPUS_ROOT / "manifest.json"
PROFILE_PATH = ROOT / "experiments" / "ebook" / "exp-0004" / "execution-profile.json"
DEFAULT_RESULT = ROOT / "experiments" / "ebook" / "exp-0004" / "result.json"

STAGES = ("byte", "package", "representation", "edition", "work")
DECISIONS = {"candidate_same", "candidate_related", "different", "abstain", "not_applicable"}
RELATION_KEYS = {
    "byte": "file",
    "representation": "representation",
    "edition": "edition",
    "work": "work",
}
EXPECTED_TO_DECISION = {
    "same": "candidate_same",
    "candidate_same": "candidate_same",
    "candidate_related": "candidate_related",
    "different": "different",
    "different_or_related": "abstain",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_profile(profile: dict[str, Any]) -> None:
    if profile.get("schema_version") != 1 or profile.get("experiment") != "EXP-0004":
        raise RuntimeError("EXP-0004 profile identity is invalid")
    if tuple(profile.get("stages", [])) != STAGES:
        raise RuntimeError("EXP-0004 stage order is invalid")
    if set(profile.get("decisions", [])) != DECISIONS:
        raise RuntimeError("EXP-0004 decision vocabulary is invalid")
    if profile.get("fixture_version") != "0.2.0":
        raise RuntimeError("EXP-0004 requires TEST-0001 fixture version 0.2.0")
    if profile.get("fixture_manifest_sha256") != sha256_file(MANIFEST_PATH):
        raise RuntimeError("EXP-0004 profile does not match the active fixture manifest")
    cases = profile.get("cases", [])
    if len(cases) != 6 or len(set(cases)) != 6:
        raise RuntimeError("EXP-0004 requires six distinct relationship cases")
    if set(profile.get("package_oracle", {})) != set(cases):
        raise RuntimeError("EXP-0004 package oracle is incomplete")
    rules = profile.get("rules", {})
    if rules.get("repetitions") != 2:
        raise RuntimeError("EXP-0004 requires two repetitions")
    if rules.get("missing_evidence_is_negative") is not False:
        raise RuntimeError("EXP-0004 must keep missing evidence separate")
    if rules.get("candidate_triggers_action") is not False:
        raise RuntimeError("EXP-0004 candidates may not trigger actions")
    if profile.get("implementation", {}).get("external_dependencies") != []:
        raise RuntimeError("EXP-0004 empirical profile must use no external dependency")


def load_profile() -> dict[str, Any]:
    profile = load_json(PROFILE_PATH)
    validate_profile(profile)
    return profile


def load_cases(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    manifest = load_json(MANIFEST_PATH)
    if manifest.get("fixture_version") != profile["fixture_version"]:
        raise RuntimeError("EXP-0004 fixture version mismatch")
    all_cases = {item["case_key"]: item for item in manifest.get("cases", [])}
    missing = sorted(set(profile["cases"]) - set(all_cases))
    if missing:
        raise RuntimeError(f"EXP-0004 fixture cases are missing: {missing}")
    return {key: all_cases[key] for key in profile["cases"]}


def component_path(component: dict[str, Any]) -> Path:
    path = (CORPUS_ROOT / component["path"]).resolve()
    root = CORPUS_ROOT.resolve()
    if root not in path.parents or not path.is_file():
        raise RuntimeError("EXP-0004 component escapes or is absent from TEST-0001")
    if sha256_file(path) != component["sha256"] or path.stat().st_size != component["size_bytes"]:
        raise RuntimeError("EXP-0004 component differs from its manifest")
    return path


def source_ref(case_key: str, component: dict[str, Any]) -> str:
    suffix = PurePosixPath(component["path"]).relative_to(PurePosixPath("cases") / case_key)
    return f"fixture://TEST-0001/0.2.0/{case_key}/{suffix.as_posix()}"


def normalized_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def title_key(value: str | None, qualifier_terms: list[str]) -> str | None:
    if not value:
        return None
    normalized = normalized_text(value)
    for term in qualifier_terms:
        normalized = re.sub(
            rf"\s*(?:[-—:]\s*)?\b{re.escape(normalized_text(term))}\b\s*$",
            "",
            normalized,
        )
    return normalized or None


def safe_zip_entries(path: Path, max_expanded_bytes: int) -> tuple[dict[str, bytes], int]:
    entries: dict[str, bytes] = {}
    expanded_bytes = 0
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            logical = PurePosixPath(info.filename.replace("\\", "/"))
            if logical.is_absolute() or ".." in logical.parts:
                raise RuntimeError("EXP-0004 rejected an unsafe package entry")
            expanded_bytes += info.file_size
            if expanded_bytes > max_expanded_bytes:
                raise RuntimeError("EXP-0004 package exceeds the expanded-byte limit")
            if not info.is_dir():
                entries[logical.as_posix()] = archive.read(info)
    return entries, expanded_bytes


def xml_texts(root: ElementTree.Element, name: str) -> list[str]:
    namespace = "http://purl.org/dc/elements/1.1/"
    return [
        value
        for element in root.findall(f".//{{{namespace}}}{name}")
        if (value := " ".join("".join(element.itertext()).split()))
    ]


def parse_xhtml_text(payload: bytes) -> str:
    try:
        root = ElementTree.fromstring(payload)
        return " ".join(" ".join(root.itertext()).split())
    except ElementTree.ParseError:
        return " ".join(re.sub(r"<[^>]+>", " ", payload.decode("utf-8", "replace")).split())


def read_epub(path: Path, limits: dict[str, int]) -> dict[str, Any]:
    entries, expanded_bytes = safe_zip_entries(path, limits["max_expanded_bytes"])
    container = ElementTree.fromstring(entries["META-INF/container.xml"])
    rootfile = container.find(".//{*}rootfile")
    if rootfile is None or not rootfile.get("full-path"):
        raise RuntimeError("EXP-0004 EPUB lacks a package locator")
    package_path = PurePosixPath(rootfile.get("full-path", "")).as_posix()
    package = ElementTree.fromstring(entries[package_path])
    work_references = [
        value
        for meta in package.findall(".//{http://www.idpf.org/2007/opf}meta")
        if meta.get("property") == "belongs-to-collection"
        if (value := " ".join("".join(meta.itertext()).split()))
    ]
    content_items = {
        name: parse_xhtml_text(payload)
        for name, payload in entries.items()
        if name.casefold().endswith((".xhtml", ".html", ".htm")) and not name.casefold().endswith("nav.xhtml")
    }
    entry_projection = [
        {"name": name, "sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)}
        for name, payload in sorted(entries.items())
    ]
    content_projection = [
        {"name": name, "text": normalized_text(value)} for name, value in sorted(content_items.items())
    ]
    return {
        "format": "EPUB",
        "package_digest": canonical_digest(entry_projection),
        "representation_digest": canonical_digest(entry_projection),
        "content_digest": canonical_digest(content_projection),
        "content_extent": sum(len(value) for value in content_items.values()),
        "expanded_bytes": expanded_bytes,
        "entry_count": len(entries),
        "metadata": {
            "identifiers": xml_texts(package, "identifier"),
            "titles": xml_texts(package, "title"),
            "languages": xml_texts(package, "language"),
            "creators": xml_texts(package, "creator"),
            "work_references": work_references,
        },
    }


def pdf_literal(payload: bytes, field: bytes) -> str | None:
    match = re.search(rb"/" + field + rb"\s*\(([^)]*)\)", payload)
    return match.group(1).decode("ascii", "replace") if match else None


def read_pdf(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    text_items = [item.decode("ascii", "replace") for item in re.findall(rb"\(([^)]*)\)\s*Tj", payload)]
    normalized_content = normalized_text(" ".join(text_items))
    title = pdf_literal(payload, b"Title")
    return {
        "format": "PDF",
        "package_digest": None,
        "representation_digest": hashlib.sha256(payload).hexdigest(),
        "content_digest": hashlib.sha256(normalized_content.encode("utf-8")).hexdigest(),
        "content_extent": len(normalized_content),
        "expanded_bytes": len(payload),
        "entry_count": 1,
        "metadata": {
            "identifiers": [],
            "titles": [title] if title else [],
            "languages": [],
            "creators": [],
            "work_references": [],
        },
    }


def inspect_component(case_key: str, component: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    path = component_path(component)
    if path.stat().st_size > profile["rules"]["max_input_bytes"]:
        raise RuntimeError("EXP-0004 input exceeds the byte limit")
    if component["media_type"] == "application/epub+zip":
        details = read_epub(path, profile["rules"])
    elif component["media_type"] == "application/pdf":
        details = read_pdf(path)
    else:
        raise RuntimeError("EXP-0004 encountered an unsupported pair input")
    return {
        "source_ref": source_ref(case_key, component),
        "media_type": component["media_type"],
        "sha256": component["sha256"],
        "size_bytes": component["size_bytes"],
        **details,
    }


def evidence(code: str, **values: Any) -> dict[str, Any]:
    return {"code": code, "values": values}


def missing_metadata(left: dict[str, Any], right: dict[str, Any], key: str) -> list[str]:
    missing = []
    if not left["metadata"][key]:
        missing.append(f"left.metadata.{key}")
    if not right["metadata"][key]:
        missing.append(f"right.metadata.{key}")
    return missing


def lower_level_negative(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    if left["sha256"] != right["sha256"]:
        return evidence("file.sha256_different", left=left["sha256"], right=right["sha256"])
    return evidence("locator.distinct", left=left["source_ref"], right=right["source_ref"])


def stage_payload(
    decision: str,
    positive: list[dict[str, Any]],
    negative: list[dict[str, Any]],
    missing: list[str],
    method: str,
    *,
    abstention_reason: str | None = None,
    not_applicable_reason: str | None = None,
) -> dict[str, Any]:
    if decision not in DECISIONS:
        raise RuntimeError(f"EXP-0004 produced an invalid decision: {decision}")
    return {
        "decision": decision,
        "positive_evidence": positive,
        "negative_evidence": negative,
        "missing_evidence": sorted(set(missing)),
        "method": method,
        "abstention_reason": abstention_reason,
        "not_applicable_reason": not_applicable_reason,
    }


def decide_byte(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    if left["sha256"] == right["sha256"]:
        return stage_payload(
            "candidate_same",
            [evidence("file.sha256_equal", sha256=left["sha256"])],
            [evidence("locator.distinct", left=left["source_ref"], right=right["source_ref"])],
            [],
            "Compare SHA-256 while retaining both source locators.",
        )
    return stage_payload(
        "different",
        [],
        [evidence("file.sha256_different", left=left["sha256"], right=right["sha256"])],
        [],
        "Compare SHA-256 while retaining both source locators.",
    )


def decide_package(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    if left["package_digest"] is None or right["package_digest"] is None:
        return stage_payload(
            "not_applicable",
            [],
            [],
            [],
            "Compare normalized logical package entries only for package-compatible formats.",
            not_applicable_reason="At least one input has no comparable package-entry model.",
        )
    if left["package_digest"] == right["package_digest"]:
        return stage_payload(
            "candidate_same",
            [evidence("package.entries_equal", digest=left["package_digest"])],
            [lower_level_negative(left, right)],
            [],
            "Hash sorted logical entry names, contents and sizes; ignore ZIP order, compression and comment.",
        )
    return stage_payload(
        "different",
        [evidence("format.equal", format=left["format"])] if left["format"] == right["format"] else [],
        [evidence("package.entries_different", left=left["package_digest"], right=right["package_digest"])],
        [],
        "Hash sorted logical entry names, contents and sizes; ignore ZIP order, compression and comment.",
    )


def decide_representation(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    if left["format"] == right["format"] and left["representation_digest"] == right["representation_digest"]:
        return stage_payload(
            "candidate_same",
            [
                evidence("format.equal", format=left["format"]),
                evidence("representation.logical_digest_equal", digest=left["representation_digest"]),
            ],
            [lower_level_negative(left, right)],
            [],
            "Compare format-scoped logical representation digests without crossing format boundaries.",
        )
    negative = [
        evidence("representation.logical_digest_different", left=left["representation_digest"], right=right["representation_digest"])
    ]
    if left["format"] != right["format"]:
        negative.append(evidence("format.different", left=left["format"], right=right["format"]))
    return stage_payload(
        "different",
        [evidence("format.equal", format=left["format"])] if left["format"] == right["format"] else [],
        negative,
        [],
        "Compare format-scoped logical representation digests without crossing format boundaries.",
    )


def shared_values(left: dict[str, Any], right: dict[str, Any], key: str) -> set[str]:
    return set(left["metadata"][key]) & set(right["metadata"][key])


def distinct_values(left: dict[str, Any], right: dict[str, Any], key: str) -> bool:
    return bool(left["metadata"][key] and right["metadata"][key] and not shared_values(left, right, key))


def decide_edition(
    left: dict[str, Any],
    right: dict[str, Any],
    representation: dict[str, Any],
    snapshot: dict[str, Any] | None,
    profile: dict[str, Any],
) -> dict[str, Any]:
    missing = missing_metadata(left, right, "identifiers")
    if representation["decision"] == "candidate_same":
        return stage_payload(
            "candidate_same",
            [evidence("representation.candidate_same")],
            [lower_level_negative(left, right)],
            missing,
            "Promote exact representation evidence only to an edition candidate, never to a merged identity.",
        )

    identifiers = set(left["metadata"]["identifiers"]) | set(right["metadata"]["identifiers"])
    if snapshot and snapshot.get("edition_key") in identifiers:
        declared_formats = set(snapshot.get("formats", []))
        observed_formats = {left["format"], right["format"]}
        if observed_formats.issubset(declared_formats):
            return stage_payload(
                "candidate_same",
                [
                    evidence("edition.snapshot_key_applies", edition_key=snapshot["edition_key"]),
                    evidence("edition.snapshot_formats_cover_inputs", formats=sorted(observed_formats)),
                ],
                [
                    evidence("format.different", left=left["format"], right=right["format"]),
                    evidence("representation.different"),
                ],
                missing,
                "Use the case-scoped bibliographic snapshot as edition evidence while preserving format and representation differences.",
            )

    common_identifiers = shared_values(left, right, "identifiers")
    if common_identifiers:
        return stage_payload(
            "candidate_same",
            [evidence("edition.identifier_equal", identifiers=sorted(common_identifiers))],
            [evidence("representation.different")],
            missing,
            "Use a shared edition identifier only as candidate evidence at the edition stage.",
        )

    left_title = left["metadata"]["titles"][0] if left["metadata"]["titles"] else None
    right_title = right["metadata"]["titles"][0] if right["metadata"]["titles"] else None
    same_title_key = title_key(left_title, profile["rules"]["title_qualifier_terms"]) == title_key(
        right_title, profile["rules"]["title_qualifier_terms"]
    ) and bool(title_key(left_title, profile["rules"]["title_qualifier_terms"]))
    common_creators = shared_values(left, right, "creators")
    common_languages = shared_values(left, right, "languages")
    positive = []
    if same_title_key:
        positive.append(evidence("title.normalized_equal", key=title_key(left_title, profile["rules"]["title_qualifier_terms"])))
    if common_creators:
        positive.append(evidence("creator.equal", creators=sorted(common_creators)))
    if common_languages:
        positive.append(evidence("language.equal", languages=sorted(common_languages)))
    common_work_refs = shared_values(left, right, "work_references")
    if common_work_refs:
        positive.append(evidence("work.reference_equal", references=sorted(common_work_refs)))

    negative = [evidence("edition.identifier_different")]
    if distinct_values(left, right, "languages"):
        negative.append(evidence("language.different", left=left["metadata"]["languages"], right=right["metadata"]["languages"]))
    if distinct_values(left, right, "creators"):
        negative.append(evidence("creator.different", left=left["metadata"]["creators"], right=right["metadata"]["creators"]))
    if left["content_digest"] != right["content_digest"]:
        negative.append(evidence("content.different", left=left["content_digest"], right=right["content_digest"]))
    if left["content_extent"] != right["content_extent"]:
        negative.append(evidence("content.extent_differs", left=left["content_extent"], right=right["content_extent"]))

    if same_title_key and common_creators and common_languages:
        return stage_payload(
            "abstain",
            positive,
            negative,
            missing + (["work.reference"] if not common_work_refs else []),
            "Retain metadata similarity and extent/identifier conflicts without declaring editions interchangeable.",
            abstention_reason="Similar work-level metadata conflicts with distinct edition identifiers or content extent.",
        )
    if distinct_values(left, right, "languages") or distinct_values(left, right, "creators"):
        return stage_payload(
            "different",
            positive,
            negative,
            missing,
            "Treat conflicting language or creator evidence as edition-level distinction.",
        )
    return stage_payload(
        "abstain",
        positive,
        negative,
        missing,
        "Abstain when neither a shared edition key nor sufficient conflict evidence is available.",
        abstention_reason="Edition evidence is incomplete or contradictory.",
    )


def decide_work(
    left: dict[str, Any],
    right: dict[str, Any],
    edition: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    common_work_refs = shared_values(left, right, "work_references")
    missing = [] if common_work_refs else ["work.reference"]
    if common_work_refs:
        negative = [evidence("edition.different")] if edition["decision"] == "different" else [lower_level_negative(left, right)]
        if distinct_values(left, right, "languages"):
            negative.append(evidence("language.different", left=left["metadata"]["languages"], right=right["metadata"]["languages"]))
        return stage_payload(
            "candidate_related" if edition["decision"] == "different" else "candidate_same",
            [evidence("work.reference_equal", references=sorted(common_work_refs))],
            negative,
            missing,
            "Use an explicit shared work reference as relation evidence while retaining edition and language differences.",
        )

    if edition["decision"] == "candidate_same":
        negative = [lower_level_negative(left, right)]
        if left["format"] != right["format"]:
            negative.append(evidence("format.different", left=left["format"], right=right["format"]))
        return stage_payload(
            "candidate_same",
            [evidence("edition.candidate_same")],
            negative,
            missing,
            "Carry a same-edition candidate upward only as a same-work candidate.",
        )

    left_title = left["metadata"]["titles"][0] if left["metadata"]["titles"] else None
    right_title = right["metadata"]["titles"][0] if right["metadata"]["titles"] else None
    left_key = title_key(left_title, profile["rules"]["title_qualifier_terms"])
    right_key = title_key(right_title, profile["rules"]["title_qualifier_terms"])
    common_creators = shared_values(left, right, "creators")
    common_languages = shared_values(left, right, "languages")
    if left_key and left_key == right_key and common_creators and common_languages:
        return stage_payload(
            "candidate_same",
            [
                evidence("title.normalized_equal", key=left_key),
                evidence("creator.equal", creators=sorted(common_creators)),
                evidence("language.equal", languages=sorted(common_languages)),
            ],
            [
                evidence("edition.identifier_different"),
                evidence("content.extent_differs", left=left["content_extent"], right=right["content_extent"]),
            ],
            missing,
            "Generate a work candidate from convergent title, creator and language evidence while retaining edition and extent differences.",
        )

    exact_title_equal = bool(left_title and right_title and normalized_text(left_title) == normalized_text(right_title))
    if exact_title_equal and (distinct_values(left, right, "creators") or distinct_values(left, right, "identifiers")):
        return stage_payload(
            "different",
            [evidence("title.equal", title=left_title)],
            [
                evidence("creator.different", left=left["metadata"]["creators"], right=right["metadata"]["creators"]),
                evidence("work.identifier_different", left=left["metadata"]["identifiers"], right=right["metadata"]["identifiers"]),
                evidence("content.different", left=left["content_digest"], right=right["content_digest"]),
            ],
            missing,
            "Reject title-only identity when creators, identifiers or content conflict.",
        )
    return stage_payload(
        "abstain",
        [],
        [evidence("edition.not_candidate_same", decision=edition["decision"])],
        missing + missing_metadata(left, right, "titles") + missing_metadata(left, right, "creators"),
        "Abstain without a shared work reference or convergent work-level metadata.",
        abstention_reason="Work evidence is insufficient.",
    )


def timed_stage(name: str, callback: Callable[[], dict[str, Any]], objects: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter_ns()
    result = callback()
    result["stage"] = name
    result["resources"] = {
        "duration_ns": time.perf_counter_ns() - started,
        "input_bytes": sum(item["size_bytes"] for item in objects),
        "expanded_bytes": sum(item["expanded_bytes"] for item in objects),
    }
    return result


def expected_decision(case: dict[str, Any], stage: str, profile: dict[str, Any]) -> str:
    if stage == "package":
        return profile["package_oracle"][case["case_key"]]
    raw = case["oracle"]["expected_relationship"][RELATION_KEYS[stage]]
    if raw not in EXPECTED_TO_DECISION:
        raise RuntimeError(f"EXP-0004 has no decision mapping for oracle value {raw}")
    return EXPECTED_TO_DECISION[raw]


def read_snapshot(case_key: str, case: dict[str, Any]) -> dict[str, Any] | None:
    snapshots = [item for item in case["components"] if item["role"] == "snapshot"]
    if not snapshots:
        return None
    if len(snapshots) != 1 or snapshots[0]["media_type"] != "application/json":
        raise RuntimeError("EXP-0004 supports one case-scoped JSON snapshot")
    return load_json(component_path(snapshots[0]))


def evaluate_case(case_key: str, case: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    input_components = [item for item in case["components"] if item["role"] == "input"]
    if len(input_components) != 2:
        raise RuntimeError("EXP-0004 requires exactly two pair inputs")
    objects = [inspect_component(case_key, item, profile) for item in input_components]
    left, right = objects
    snapshot = read_snapshot(case_key, case)

    stages: list[dict[str, Any]] = []
    byte = timed_stage("byte", lambda: decide_byte(left, right), objects)
    stages.append(byte)
    package = timed_stage("package", lambda: decide_package(left, right), objects)
    stages.append(package)
    representation = timed_stage("representation", lambda: decide_representation(left, right), objects)
    stages.append(representation)
    edition = timed_stage(
        "edition",
        lambda: decide_edition(left, right, representation, snapshot, profile),
        objects,
    )
    stages.append(edition)
    work = timed_stage("work", lambda: decide_work(left, right, edition, profile), objects)
    stages.append(work)

    for stage in stages:
        stage["expected_decision"] = expected_decision(case, stage["stage"], profile)
        stage["matches_oracle"] = stage["decision"] == stage["expected_decision"]
    return {
        "case_key": case_key,
        "fixture_nature": case["fixture_nature"],
        "sources": [item["source_ref"] for item in objects],
        "observations": [
            {
                "source_ref": item["source_ref"],
                "format": item["format"],
                "sha256": item["sha256"],
                "size_bytes": item["size_bytes"],
                "package_digest": item["package_digest"],
                "representation_digest": item["representation_digest"],
                "content_digest": item["content_digest"],
                "content_extent": item["content_extent"],
                "metadata": item["metadata"],
            }
            for item in objects
        ],
        "candidate_generation": [
            "byte prefilter",
            "package comparison when applicable",
            "format-scoped representation comparison",
            "edition evidence resolution",
            "work evidence resolution",
        ],
        "stages": stages,
        "effects_observed": [],
    }


def semantic_repeat_projection(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projection = []
    for case in cases:
        projection.append(
            {
                "case_key": case["case_key"],
                "sources": case["sources"],
                "observations": case["observations"],
                "stages": [
                    {key: value for key, value in stage.items() if key != "resources"}
                    for stage in case["stages"]
                ],
                "effects_observed": case["effects_observed"],
            }
        )
    return projection


def ratio(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def stage_metrics(cases: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    metrics = {}
    for stage_name in STAGES:
        rows = [next(stage for stage in case["stages"] if stage["stage"] == stage_name) for case in cases]
        eligible = [row for row in rows if row["expected_decision"] != "not_applicable"]
        positives = set(profile["measurement"]["positive_labels"][stage_name])
        predicted_positive = [row for row in eligible if row["decision"] in positives]
        expected_positive = [row for row in eligible if row["expected_decision"] in positives]
        true_positive = [
            row for row in predicted_positive if row["decision"] == row["expected_decision"]
        ]
        decided = [row for row in eligible if row["decision"] not in {"abstain", "not_applicable"}]
        expected_abstain = [row for row in eligible if row["expected_decision"] == "abstain"]
        metrics[stage_name] = {
            "precision": ratio(len(true_positive), len(predicted_positive)),
            "recall": ratio(len(true_positive), len(expected_positive)),
            "selective_accuracy": ratio(sum(row["matches_oracle"] for row in decided), len(decided)),
            "coverage": ratio(len(decided), len(eligible)),
            "correct_abstention": ratio(
                sum(row["decision"] == "abstain" for row in expected_abstain),
                len(expected_abstain),
            ),
            "false_positive_count": sum(
                row["decision"] in positives and row["expected_decision"] not in positives for row in eligible
            ),
            "eligible_cases": len(eligible),
        }
    return metrics


def stage_map(case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {stage["stage"]: stage for stage in case["stages"]}


def acceptance_contract(
    repetitions: list[dict[str, Any]],
    metrics: dict[str, Any],
    input_hashes_before: dict[str, str],
    input_hashes_after: dict[str, str],
    profile: dict[str, Any],
) -> dict[str, bool]:
    first = {case["case_key"]: case for case in repetitions[0]["cases"]}
    all_stages = [stage for case in first.values() for stage in case["stages"]]
    candidates = [stage for stage in all_stages if stage["decision"].startswith("candidate_")]
    missing_codes_separate = all(
        not (set(stage["missing_evidence"]) & {item["code"] for item in stage["negative_evidence"]})
        for stage in all_stages
    )
    byte_equal = stage_map(first["identity-byte-equal"])
    repackaged = stage_map(first["identity-repackaged"])
    multiformat = stage_map(first["identity-multiformat-edition"])
    translation = stage_map(first["identity-edition-vs-translation"])
    sample = stage_map(first["edition-sample-vs-full"])
    collision = stage_map(first["identity-title-collision"])
    return {
        "fixture_and_oracles_bound": len(first) == 6
        and profile["fixture_manifest_sha256"] == sha256_file(MANIFEST_PATH)
        and all(stage["matches_oracle"] for stage in all_stages),
        "five_identity_stages_separate": all(tuple(stage["stage"] for stage in case["stages"]) == STAGES for case in first.values()),
        "byte_equality_preserves_locators": byte_equal["byte"]["decision"] == "candidate_same"
        and first["identity-byte-equal"]["sources"][0] != first["identity-byte-equal"]["sources"][1],
        "repackaging_not_byte_equality": repackaged["byte"]["decision"] == "different"
        and repackaged["package"]["decision"] == "candidate_same"
        and repackaged["representation"]["decision"] == "candidate_same",
        "multiformat_edition_stays_layered": multiformat["byte"]["decision"] == "different"
        and multiformat["representation"]["decision"] == "different"
        and multiformat["edition"]["decision"] == "candidate_same",
        "translation_not_interchangeable_edition": translation["edition"]["decision"] == "different"
        and translation["work"]["decision"] == "candidate_related",
        "sample_full_conflict_abstains_at_edition": sample["representation"]["decision"] == "different"
        and sample["edition"]["decision"] == "abstain"
        and sample["work"]["decision"] == "candidate_same",
        "title_collision_not_work_candidate": collision["work"]["decision"] == "different",
        "candidate_evidence_has_both_polarities": bool(candidates)
        and all(stage["positive_evidence"] and stage["negative_evidence"] for stage in candidates),
        "missing_evidence_not_negative": missing_codes_separate
        and any(stage["missing_evidence"] for stage in all_stages),
        "no_action_or_writer_effect": all(case["effects_observed"] == [] for case in first.values())
        and profile["rules"]["candidate_triggers_action"] is False,
        "metrics_complete_without_false_positives": all(
            stage_metrics["precision"]["value"] == 1.0
            and stage_metrics["recall"]["value"] == 1.0
            and stage_metrics["selective_accuracy"]["value"] == 1.0
            and stage_metrics["false_positive_count"] == 0
            for stage_metrics in metrics.values()
        ),
        "semantic_repetitions_identical": len(repetitions) == 2
        and repetitions[0]["semantic_sha256"] == repetitions[1]["semantic_sha256"],
        "fixture_inputs_unchanged": input_hashes_before == input_hashes_after,
        "resource_and_provenance_evidence_complete": all(
            stage["resources"]["duration_ns"] >= 0
            and stage["resources"]["input_bytes"] > 0
            and stage["resources"]["expanded_bytes"] > 0
            for stage in all_stages
        )
        and all(source.startswith("fixture://TEST-0001/0.2.0/") for case in first.values() for source in case["sources"]),
    }


def all_input_paths(cases: dict[str, dict[str, Any]]) -> list[Path]:
    return sorted(
        {
            component_path(component)
            for case in cases.values()
            for component in case["components"]
        },
        key=lambda path: path.as_posix(),
    )


def run(profile: dict[str, Any], result_path: Path) -> dict[str, Any]:
    cases = load_cases(profile)
    paths = all_input_paths(cases)
    input_hashes_before = {path.relative_to(CORPUS_ROOT).as_posix(): sha256_file(path) for path in paths}
    repetitions = []
    for repetition in range(1, profile["rules"]["repetitions"] + 1):
        started = time.perf_counter_ns()
        evaluated = [evaluate_case(case_key, cases[case_key], profile) for case_key in profile["cases"]]
        semantic_projection = semantic_repeat_projection(evaluated)
        repetitions.append(
            {
                "repetition": repetition,
                "duration_ns": time.perf_counter_ns() - started,
                "semantic_sha256": canonical_digest(semantic_projection),
                "cases": evaluated,
            }
        )
    input_hashes_after = {path.relative_to(CORPUS_ROOT).as_posix(): sha256_file(path) for path in paths}
    metrics = stage_metrics(repetitions[0]["cases"], profile)
    acceptance = acceptance_contract(repetitions, metrics, input_hashes_before, input_hashes_after, profile)
    result = {
        "schema_version": 1,
        "experiment": "EXP-0004",
        "status": "pass" if all(acceptance.values()) else "fail",
        "executed_on": date.today().isoformat(),
        "profile_id": profile["profile_id"],
        "profile_sha256": sha256_file(PROFILE_PATH),
        "runner_sha256": sha256_file(RUNNER_PATH),
        "fixture_ref": profile["fixture_ref"],
        "fixture_version": profile["fixture_version"],
        "fixture_manifest_sha256": profile["fixture_manifest_sha256"],
        "runtime": {
            "implementation": profile["implementation"]["runtime"],
            "python_version": platform.python_version(),
            "network": profile["implementation"]["network"],
            "input_access": profile["implementation"]["input_access"],
            "external_dependencies": profile["implementation"]["external_dependencies"],
        },
        "metrics": metrics,
        "acceptance": acceptance,
        "repetitions": repetitions,
        "input_integrity": {
            "before_sha256": input_hashes_before,
            "after_sha256": input_hashes_after,
            "unchanged": input_hashes_before == input_hashes_after,
        },
        "limitations": [
            "The gold standard contains only six small synthetic pairs; perfect metrics do not establish real-collection quality.",
            "The package-stage oracle is fixed in the execution profile because TEST-0001 records file and representation relations but no separate package relation.",
            "Representation equality compares format-scoped logical entry bytes; semantically equivalent XML or content rewrites are not normalized by this profile.",
            "The tested title qualifier vocabulary contains only the synthetic German term 'Leseprobe' and is not a product vocabulary.",
            "The multiformat candidate relies on a case-scoped synthetic bibliographic snapshot; trust and conflict resolution for real providers remain untested.",
            "No statistical similarity, external metadata provider, product persistence, merge, removal, move or writer was implemented.",
        ],
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if re.search(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/)", serialized):
        raise RuntimeError("EXP-0004 result contains an absolute host path")
    result_path.write_text(serialized, encoding="utf-8")
    return result


def validate_result(path: Path) -> dict[str, Any]:
    profile = load_profile()
    result = load_json(path)
    if result.get("experiment") != "EXP-0004" or result.get("status") != "pass":
        raise RuntimeError("EXP-0004 result is not a pass")
    if result.get("profile_id") != profile["profile_id"] or result.get("profile_sha256") != sha256_file(PROFILE_PATH):
        raise RuntimeError("EXP-0004 result does not match the active profile")
    if result.get("runner_sha256") != sha256_file(RUNNER_PATH):
        raise RuntimeError("EXP-0004 result does not match the active runner")
    if result.get("fixture_manifest_sha256") != sha256_file(MANIFEST_PATH):
        raise RuntimeError("EXP-0004 result does not match the active fixture manifest")
    if len(result.get("acceptance", {})) != 15 or not all(result["acceptance"].values()):
        raise RuntimeError("EXP-0004 acceptance set is incomplete")
    repetitions = result.get("repetitions", [])
    if len(repetitions) != 2 or repetitions[0].get("semantic_sha256") != repetitions[1].get("semantic_sha256"):
        raise RuntimeError("EXP-0004 repetition evidence is incomplete")
    if any(len(repetition.get("cases", [])) != 6 for repetition in repetitions):
        raise RuntimeError("EXP-0004 case evidence is incomplete")
    if any(
        tuple(stage["stage"] for stage in case.get("stages", [])) != STAGES
        for repetition in repetitions
        for case in repetition["cases"]
    ):
        raise RuntimeError("EXP-0004 stage evidence is incomplete")
    if result.get("input_integrity", {}).get("unchanged") is not True:
        raise RuntimeError("EXP-0004 fixture integrity evidence is incomplete")
    serialized = canonical_json(result)
    if re.search(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/)", serialized):
        raise RuntimeError("EXP-0004 result contains an absolute host path")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    profile = load_profile()
    if args.validate_profile and not args.validate_result:
        print(f"EXP-0004 profile valid: {profile['profile_id']}")
        return 0
    result = validate_result(args.result) if args.validate_result else run(profile, args.result)
    print(f"EXP-0004 {result['status']}: {sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
