#!/usr/bin/env python3
"""Validate the project-owned repository bootstrap contracts."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path, PurePosixPath
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / ".ai" / "artifact_registry.json"
PROJECT_PATH = ROOT / ".ai" / "project.json"
REGISTRY_TOOL_PATH = (
    ROOT
    / ".ai"
    / "foundation"
    / "artifact_registry_github"
    / "registry_semantic.py"
)

REQUIRED_PATHS = [
    "AGENTS.md",
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".gitignore",
    ".editorconfig",
    ".ai/project.json",
    ".ai/artifact_registry.json",
    ".ai/foundation/AI_REPOSITORY_FOUNDATION_NOTICE.md",
    ".ai/foundation/artifact_registry_github/registry_semantic.py",
    "docs/README.md",
    "docs/product/PROJECT_CHARTER.md",
    "docs/architecture/BOUNDARIES.md",
    "docs/governance/PROJECT_RULES.md",
    "docs/governance/VALIDATION.md",
    "docs/governance/IDENTITY_AND_REGISTRATION.md",
    "docs/governance/THIRD_PARTY_AND_REUSE.md",
    "docs/project/PROJECT_STATUS.md",
    "docs/project/HANDOVER.md",
    "docs/planning/README.md",
    "docs/reference/GLOSSARY.md",
]

MEDIA_EXTENSIONS = {
    ".azw",
    ".azw3",
    ".cb7",
    ".cbr",
    ".cbz",
    ".doc",
    ".docx",
    ".epub",
    ".fb2",
    ".flac",
    ".heic",
    ".m4a",
    ".mkv",
    ".mobi",
    ".mov",
    ".mp3",
    ".mp4",
    ".odt",
    ".ogg",
    ".opus",
    ".pdf",
    ".ppt",
    ".pptx",
    ".rar",
    ".tif",
    ".tiff",
    ".wav",
    ".webm",
    ".xls",
    ".xlsx",
    ".zip",
}

TEXT_EXTENSIONS = {
    "",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}

ALLOWED_ARTIFACT_STATUSES = {
    "accepted",
    "blocked",
    "done",
    "in_progress",
    "proposed",
    "ready",
    "rejected",
    "superseded",
}

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_WINDOWS_USERS_RE = r"[a-z]:\\U" + r"sers\\[^\\\s]+"
_POSIX_HOME_RE = r"/ho" + r"me/[^/\s]+"
PRIVATE_PATH_RE = re.compile(
    rf"(?i)(?:{_WINDOWS_USERS_RE}|{_POSIX_HOME_RE})"
)


def load_registry_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_registry_semantic", REGISTRY_TOOL_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load registry tool: {REGISTRY_TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repository_files() -> list[Path]:
    command = [
        "git",
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def check_markdown_link(source: Path, raw_target: str) -> str | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "mailto:")):
        return None
    parsed = urllib.parse.urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    relative = urllib.parse.unquote(parsed.path)
    if not relative:
        return None
    resolved = (source.parent / relative).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return f"{source.relative_to(ROOT)} links outside repository: {target}"
    if not resolved.exists():
        return f"{source.relative_to(ROOT)} has missing link target: {target}"
    return None


def validate() -> list[str]:
    problems: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).is_file():
            problems.append(f"required file missing: {relative}")

    try:
        registry_tool = load_registry_tool()
        registry = registry_tool.load_json(REGISTRY_PATH)
        problems.extend(
            f"artifact registry: {problem}"
            for problem in registry_tool.validate_registry(registry)
        )
    except Exception as exc:
        problems.append(f"artifact registry unavailable: {exc}")
        registry = {"artifacts": {}}
        registry_tool = None

    try:
        project = json.loads(PROJECT_PATH.read_text(encoding="utf-8"))
        if project.get("schema_version") != 1:
            problems.append("project identity requires schema_version 1")
        if project.get("canonical_name") != "SammlungsLotse":
            problems.append("project identity canonical_name must be SammlungsLotse")
        if project.get("repository") != "https://github.com/gecompat/SammlungsLotse":
            problems.append("project identity repository locator is unexpected")
        if registry_tool is not None:
            normalized = registry_tool.normalize_uid(project.get("project_uid", ""))
            if normalized != project.get("project_uid"):
                problems.append("project UID is not canonical")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        problems.append(f"project identity unavailable: {exc}")

    for reference, record in registry.get("artifacts", {}).items():
        status = record.get("status")
        if status is not None and status not in ALLOWED_ARTIFACT_STATUSES:
            problems.append(f"{reference} has unsupported status: {status}")
        locator = record.get("locator")
        if not isinstance(locator, str):
            problems.append(f"{reference} requires a repository locator")
            continue
        path = PurePosixPath(locator)
        if path.is_absolute() or ".." in path.parts or "\\" in locator:
            problems.append(f"{reference} has invalid locator: {locator}")
            continue
        target = ROOT / path
        if not target.is_file():
            problems.append(f"{reference} locator does not exist: {locator}")
            continue
        if target.suffix.lower() == ".md":
            content = target.read_text(encoding="utf-8")
            if reference not in content:
                problems.append(f"{reference} is not named in its locator: {locator}")
            uid = record.get("artifact_uid")
            if reference.startswith("DEC-") and uid not in content:
                problems.append(f"{reference} decision does not state its artifact UID")

    try:
        files = repository_files()
    except (OSError, subprocess.CalledProcessError) as exc:
        problems.append(f"cannot enumerate repository files: {exc}")
        files = []

    for path in files:
        relative = path.relative_to(ROOT)
        posix = relative.as_posix()
        lower_name = path.name.lower()
        if lower_name == ".env" or lower_name.startswith(".env."):
            if lower_name != ".env.example":
                problems.append(f"secret-bearing filename is tracked: {posix}")
        if path.suffix.lower() in MEDIA_EXTENSIONS and not posix.startswith(
            "tests/fixtures/"
        ):
            problems.append(f"media or document file outside fixture scope: {posix}")

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if posix.startswith(".ai/foundation/"):
            continue
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f"text file is not readable UTF-8: {posix}: {exc}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")) and path.suffix.lower() != ".md":
                problems.append(f"trailing whitespace: {posix}:{line_number}")
        if path.resolve() != Path(__file__).resolve() and PRIVATE_PATH_RE.search(text):
            problems.append(f"private user path found: {posix}")
        if path.suffix.lower() == ".md":
            for match in MARKDOWN_LINK_RE.finditer(text):
                problem = check_markdown_link(path, match.group(1))
                if problem:
                    problems.append(problem)

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if "docs/governance/PROJECT_RULES.md" not in agents:
        problems.append("AGENTS.md does not discover project-owned governance")

    return problems


def main() -> int:
    problems = validate()
    for problem in problems:
        print(f"[BLOCK] {problem}")
    if problems:
        return 2
    print("[OK] project bootstrap contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
