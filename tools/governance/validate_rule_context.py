#!/usr/bin/env python3
"""Check full governance reachability, independently of semantic read selection."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
CACHE_TOOL = ".ai/foundation/rule_context_cache/rule_context_cache.py"
REQUIRED_SOURCES = frozenset({
    ".ai/artifact_registry.json",
    ".ai/foundation/FOUNDATION_RULESET.md",
    "docs/governance/PROJECT_RULES.md",
    "docs/governance/VALIDATION.md",
    "docs/governance/DOCUMENTATION_STYLE.md",
    "docs/governance/IDENTITY_AND_REGISTRATION.md",
    "docs/governance/THIRD_PARTY_AND_REUSE.md",
    "docs/project/PROJECT_STATUS.md",
    "docs/project/HANDOVER.md",
    "docs/product/PROJECT_CHARTER.md",
    "docs/architecture/BOUNDARIES.md",
    "docs/planning/README.md",
    "docs/decisions/README.md",
    "docs/reference/GLOSSARY.md",
})


def load_cache_tool(repository: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_foundation_cache", repository / CACHE_TOOL
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Foundation cache tool is unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def discovery_inventory(repository: Path, cache_tool: ModuleType | None = None) -> dict:
    """Validate the full graph, independently of host/global configuration.

    Fingerprinting and host instruction discovery remain the Foundation tool's
    responsibility. This project gate checks the actual transitive graph, not
    just the presence of filenames in AGENTS.md. Reachability is not semantic
    applicability: accepted decisions remain required here even when unrelated
    to the caller's task. No cache record or semantic analysis is produced.
    """
    repository = repository.resolve()
    tool = cache_tool or load_cache_tool(repository)
    options = tool.make_options(
        repository, repository, include_global=False,
        fallback_filenames=(), project_doc_max_bytes=32 * 1024,
    )
    chain, reasons = tool._instruction_chain(options)
    locations, _, reference_reasons = tool._discover_sources(options, chain)
    problems = [f"rule-context discovery: {code}" for code in sorted(set(reasons + reference_reasons))]
    required = set(REQUIRED_SOURCES)
    # Detect newly declared authority independently of the links under test.
    # Dropping an entry from the router must not hide an authoritative rule.
    for path in sorted((repository / "docs").rglob("*.md")):
        if re.search(r"(?m)^Status: AUTHORITATIVE\b", path.read_text(encoding="utf-8")):
            required.add(path.relative_to(repository).as_posix())
    registry = json.loads((repository / ".ai/artifact_registry.json").read_text(encoding="utf-8"))
    for reference, record in registry["artifacts"].items():
        if reference.startswith("DEC-") and record.get("status") == "accepted":
            locator = record.get("locator")
            if not isinstance(locator, str):
                problems.append(f"accepted decision lacks a locator: {reference}")
            else:
                required.add(locator)
    for missing in sorted(required - locations.keys()):
        problems.append(f"project rule is outside rule-context discovery: {missing}")
    return {
        "discovery_source_count": len(locations),
        "project_source_count": sum(p.startswith("docs/") for p in locations),
        "required_sources": sorted(required),
        "discovered_sources": sorted(locations),
        "problems": problems,
    }


def discovery_problems(repository: Path, cache_tool: ModuleType | None = None) -> list[str]:
    """Compatibility entrypoint used by the repository's semantic validator."""
    return discovery_inventory(repository, cache_tool)["problems"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="content-free reachability inventory")
    args = parser.parse_args()
    try:
        inventory = discovery_inventory(args.repository)
        problems = inventory["problems"]
    except (OSError, ValueError, KeyError, RuntimeError, ImportError, AttributeError) as exc:
        print(f"[BLOCK] rule-context discovery unavailable: {exc}")
        return 2
    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
        return 2 if problems else 0
    for problem in problems:
        print(f"[BLOCK] {problem}")
    if problems:
        return 2
    print(f"[OK] governance reachable: {inventory['discovery_source_count']} sources, "
          f"{inventory['project_source_count']} under docs/; semantic selection remains task-scoped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
