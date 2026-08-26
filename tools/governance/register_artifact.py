#!/usr/bin/env python3
"""Register one durable project artifact in the canonical v2 registry."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import secrets
import sys
import time
import uuid
from datetime import date
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / ".ai" / "artifact_registry.json"
REGISTRY_TOOL_PATH = (
    ROOT
    / ".ai"
    / "foundation"
    / "artifact_registry_github"
    / "registry_semantic.py"
)


class RegistrationError(RuntimeError):
    """Raised when a project artifact cannot be registered safely."""


def load_registry_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_registry_semantic", REGISTRY_TOOL_PATH
    )
    if spec is None or spec.loader is None:
        raise RegistrationError(f"cannot load registry tool: {REGISTRY_TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REGISTRY_TOOL = load_registry_tool()


def uuid7() -> uuid.UUID:
    """Return an RFC 9562 UUIDv7 without requiring a non-stdlib package."""

    timestamp_ms = (time.time_ns() // 1_000_000) & ((1 << 48) - 1)
    random_bits = secrets.randbits(74)
    rand_a = random_bits >> 62
    rand_b = random_bits & ((1 << 62) - 1)
    value = (
        (timestamp_ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0b10 << 62)
        | rand_b
    )
    return uuid.UUID(int=value)


def normalize_locator(raw: str | None) -> str | None:
    if raw is None:
        return None
    locator = PurePosixPath(raw)
    if locator.is_absolute() or ".." in locator.parts or "\\" in raw:
        raise RegistrationError("locator must be a repository-relative POSIX path")
    return locator.as_posix()


def parse_relation(raw: str) -> dict[str, str]:
    relation_type, separator, target = raw.partition("=")
    if not separator or not relation_type.strip() or not target.strip():
        raise RegistrationError("relation must use TYPE=TARGET")
    return {"type": relation_type.strip(), "target": target.strip()}


def resolve_registry_path(raw: Path) -> Path:
    return raw if raw.is_absolute() else ROOT / raw


def register_artifact(
    *,
    registry_path: Path,
    prefix: str,
    title: str,
    status: str | None = "proposed",
    priority: str | None = None,
    acceptance_criteria: str | None = None,
    aliases: list[str] | None = None,
    relations: list[dict[str, str]] | None = None,
    external_refs: list[dict[str, str]] | None = None,
    locator: str | None = None,
    reserved_refs: set[str] | None = None,
    artifact_uid: str | None = None,
    registration_state: str = "REGISTERED",
    write: bool = True,
) -> tuple[str, dict[str, Any]]:
    registry = REGISTRY_TOOL.load_json(registry_path)
    problems = REGISTRY_TOOL.validate_registry(registry)
    if problems:
        raise RegistrationError("; ".join(problems))

    reference = REGISTRY_TOOL.next_reference(registry, prefix, reserved_refs or set())
    uid = artifact_uid or f"urn:uuid:{uuid7()}"
    uid = REGISTRY_TOOL.normalize_uid(uid)

    record: dict[str, Any] = {
        "aliases": sorted(set(aliases or [])),
        "artifact_uid": uid,
        "created_on": date.today().isoformat(),
        "external_refs": external_refs or [],
        "kind": registry["prefixes"][prefix]["kind"],
        "registration_state": registration_state,
        "relations": relations or [],
        "title": title.strip(),
    }
    if not record["title"]:
        raise RegistrationError("title must not be empty")
    if status is not None:
        record["status"] = status
    if priority is not None:
        record["priority"] = priority
    if acceptance_criteria is not None:
        record["acceptance_criteria"] = acceptance_criteria
    normalized_locator = normalize_locator(locator)
    if normalized_locator is not None:
        record["locator"] = normalized_locator

    candidate = json.loads(json.dumps(registry))
    candidate["artifacts"][reference] = record
    problems = REGISTRY_TOOL.validate_registry(candidate)
    if problems:
        raise RegistrationError("; ".join(problems))

    if write:
        temporary = registry_path.with_name(
            f".{registry_path.name}.{os.getpid()}.tmp"
        )
        try:
            REGISTRY_TOOL.write_json(temporary, candidate)
            os.replace(temporary, registry_path)
        finally:
            temporary.unlink(missing_ok=True)
    return reference, record


def parse_external_ref(raw: str) -> dict[str, str]:
    system, separator, value = raw.partition("=")
    if not separator or not system.strip() or not value.strip():
        raise RegistrationError("external reference must use SYSTEM=VALUE")
    return {"system": system.strip(), "value": value.strip()}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    result.add_argument("--prefix", required=True)
    result.add_argument("--title", required=True)
    result.add_argument("--status", default="proposed")
    result.add_argument("--priority")
    result.add_argument("--acceptance-criteria")
    result.add_argument("--alias", action="append", default=[])
    result.add_argument("--relation", action="append", default=[])
    result.add_argument("--external-ref", action="append", default=[])
    result.add_argument("--locator")
    result.add_argument("--reserved-ref", action="append", default=[])
    result.add_argument("--artifact-uid")
    result.add_argument(
        "--registration-state",
        choices=["DRAFT", "REGISTERED", "RETIRED"],
        default="REGISTERED",
    )
    result.add_argument("--dry-run", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        reference, record = register_artifact(
            registry_path=resolve_registry_path(args.registry),
            prefix=args.prefix,
            title=args.title,
            status=args.status,
            priority=args.priority,
            acceptance_criteria=args.acceptance_criteria,
            aliases=args.alias,
            relations=[parse_relation(value) for value in args.relation],
            external_refs=[
                parse_external_ref(value) for value in args.external_ref
            ],
            locator=args.locator,
            reserved_refs=set(args.reserved_ref),
            artifact_uid=args.artifact_uid,
            registration_state=args.registration_state,
            write=not args.dry_run,
        )
    except (OSError, RegistrationError, REGISTRY_TOOL.RegistryError) as exc:
        print(f"[BLOCK] {exc}", file=sys.stderr)
        return 2

    payload = {"human_ref": reference, **record}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
