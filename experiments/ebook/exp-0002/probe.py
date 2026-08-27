#!/usr/bin/env python3
"""Container-side materialization and read-only probes for EXP-0002."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


OUTPUT = Path("/output")


def write_json(name: str, value: object) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_calibre(arguments: list[str], *, expected: set[int] = {0}) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["/opt/calibre/calibredb", *arguments],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=25,
        check=False,
    )
    if len(completed.stdout.encode("utf-8")) > 1024 * 1024:
        raise RuntimeError("calibredb output exceeded the experiment limit")
    if completed.returncode not in expected:
        raise RuntimeError(
            f"calibredb returned {completed.returncode} for {arguments[:2]}: {completed.stdout[-1000:]}"
        )
    return completed


def add_book(arguments: list[str]) -> int:
    completed = run_calibre(["add", "--with-library", "/library", *arguments])
    match = re.search(r"Added book ids:\s*([0-9]+)", completed.stdout)
    if match is None:
        raise RuntimeError(f"could not derive added calibre id: {completed.stdout}")
    return int(match.group(1))


def provision(target: str) -> int:
    commands: list[list[str]] = []
    if target == "technical-library":
        first = add_book(
            [
                "--title",
                "Synthetische Systemanalyse",
                "--authors",
                "Ada Beispiel",
                "--languages",
                "de",
                "--tags",
                "Technik,Review",
                "--identifier",
                "sltest:edition-001",
                "/fixtures/edition.epub",
            ]
        )
        commands.append(["add", "edition.epub"])
        run_calibre(["add_format", "--with-library", "/library", str(first), "/fixtures/edition.pdf"])
        commands.append(["add_format", str(first), "edition.pdf"])
        run_calibre(
            ["add_custom_column", "--with-library", "/library", "review_state", "Reviewstatus", "text"]
        )
        commands.append(["add_custom_column", "review_state", "text"])
        run_calibre(["set_custom", "--with-library", "/library", "review_state", str(first), "offen"])
        commands.append(["set_custom", "review_state", str(first), "offen"])
        second = add_book(
            [
                "--title",
                "Rollen und Beiträge",
                "--authors",
                "Bea Beispiel",
                "--languages",
                "de",
                "--tags",
                "Technik",
                "/fixtures/contributor-roles.epub",
            ]
        )
        commands.append(["add", "contributor-roles.epub"])
        ids = [first, second]
    elif target == "young-readers-library":
        run_calibre(
            ["add_custom_column", "--with-library", "/library", "audience", "Zielgruppe", "text"]
        )
        commands.append(["add_custom_column", "audience", "text"])
        first = add_book(
            [
                "--title",
                "Synthetisches Abenteuer (Leseprobe)",
                "--authors",
                "Chris Beispiel",
                "--languages",
                "de",
                "--tags",
                "Jugend,Leseprobe",
                "/fixtures/sample.epub",
            ]
        )
        commands.append(["add", "sample.epub"])
        run_calibre(["set_custom", "--with-library", "/library", "audience", str(first), "jugend"])
        commands.append(["set_custom", "audience", str(first), "jugend"])
        second = add_book(
            [
                "--title",
                "Synthetisches Abenteuer (Vollausgabe)",
                "--authors",
                "Chris Beispiel",
                "--languages",
                "de",
                "--tags",
                "Jugend,Vollausgabe",
                "--identifier",
                "sltest:edition-002",
                "/fixtures/full.epub",
            ]
        )
        commands.append(["add", "full.epub"])
        ids = [first, second]
    else:
        raise RuntimeError(f"unknown target: {target}")
    write_json(
        "provision.json",
        {
            "target_key": target,
            "record_ids": ids,
            "commands": commands,
            "source": "supported calibredb write commands used only for synthetic experiment materialization",
        },
    )
    return 0


def tool_version() -> int:
    completed = run_calibre(["--version"])
    write_json("tool-version.json", {"exit_code": completed.returncode, "output": completed.stdout.strip()})
    return 0


def project(target: str, custom_field: str) -> int:
    base_fields = ["title", "authors", "languages", "tags", "identifiers", "formats"]
    fields = ",".join([*base_fields, f"*{custom_field}"])
    common = [
        "list",
        "--with-library",
        "/library",
        "--for-machine",
        "--sort-by",
        "id",
        "--ascending",
    ]
    minimal = run_calibre([*common, "--fields", fields])
    (OUTPUT / "raw-minimal.json").write_text(minimal.stdout, encoding="utf-8")
    broad = run_calibre([*common, "--fields", "all"])
    (OUTPUT / "raw-broad.json").write_text(broad.stdout, encoding="utf-8")
    limited = run_calibre([*common, "--fields", fields, "--limit", "1"])
    (OUTPUT / "raw-limited.json").write_text(limited.stdout, encoding="utf-8")
    unknown = run_calibre([*common, "--fields", "title,*not_registered"], expected={0, 1})
    write_json(
        "control.json",
        {
            "target_key": target,
            "minimal_fields": base_fields,
            "custom_fields": [custom_field],
            "sort": "id ascending",
            "unknown_field": {
                "field": "not_registered",
                "exit_code": unknown.returncode,
                "classification": "unsupported" if unknown.returncode != 0 else "bounded_projection",
            },
        },
    )
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "tool-version" and len(sys.argv) == 2:
        return tool_version()
    if sys.argv[1] == "provision" and len(sys.argv) == 3:
        return provision(sys.argv[2])
    if sys.argv[1] == "project" and len(sys.argv) == 4:
        return project(sys.argv[2], sys.argv[3])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
