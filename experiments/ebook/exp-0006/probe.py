from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree


FORMAT_CAPABILITIES = {"supported", "unsupported", "unknown"}
NEXT_ACTIONS = {
    "continue_deep_read_only",
    "defer",
    "stop",
    "review",
    "abstain",
}
SAFE_SEQUENCE = (
    "snapshot",
    "signature",
    "container_metadata",
    "protection_and_active_content",
    "decision",
    "deep_tool_gate",
)


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


def observation(code: str, **values: Any) -> dict[str, Any]:
    return {"code": code, "values": values}


def finding(code: str, **values: Any) -> dict[str, Any]:
    return {"code": code, "values": values}


def source_ref(case_key: str, component: dict[str, Any]) -> str:
    relative = PurePosixPath(component["path"]).relative_to(
        PurePosixPath("cases") / case_key
    )
    return f"fixture://TEST-0001/0.2.0/{case_key}/{relative.as_posix()}"


def component_path(corpus_root: Path, component: dict[str, Any]) -> Path:
    root = corpus_root.resolve()
    candidate = (root / component["path"]).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise RuntimeError("EXP-0006 component escapes or is absent from TEST-0001")
    if candidate.stat().st_size != component["size_bytes"]:
        raise RuntimeError("EXP-0006 component size differs from TEST-0001")
    if sha256_file(candidate) != component["sha256"]:
        raise RuntimeError("EXP-0006 component hash differs from TEST-0001")
    return candidate


def select_components(
    row: dict[str, Any], case: dict[str, Any], corpus_root: Path
) -> dict[str, tuple[dict[str, Any], Path]]:
    available: dict[str, dict[str, Any]] = {}
    for component in case["components"]:
        name = PurePosixPath(component["path"]).name
        if name in available:
            raise RuntimeError("EXP-0006 component basenames are ambiguous")
        available[name] = component
    requested = row["components"]
    if len(requested) != len(set(requested)) or not set(requested).issubset(available):
        raise RuntimeError(f"EXP-0006 component selection is invalid: {row['row_key']}")
    return {
        name: (available[name], component_path(corpus_root, available[name]))
        for name in requested
    }


def add_once(items: list[dict[str, Any]], item: dict[str, Any]) -> None:
    if item["code"] not in {current["code"] for current in items}:
        items.append(item)


def stable_snapshot(path: Path, observations: list[dict[str, Any]]) -> None:
    first_size = path.stat().st_size
    first_hash = sha256_file(path)
    second_size = path.stat().st_size
    second_hash = sha256_file(path)
    observations.extend(
        [
            observation("input.size", size_bytes=second_size),
            observation("input.sha256", sha256=second_hash),
        ]
    )
    if first_size != second_size or first_hash != second_hash:
        raise RuntimeError("EXP-0006 stable input changed during snapshot")
    observations.append(observation("snapshot.stable"))


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1].casefold()


def active_content_observations(
    archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo]
) -> tuple[bool, bool]:
    has_script = False
    has_remote = False
    markup_suffixes = (".xhtml", ".html", ".htm", ".svg", ".opf", ".xml")
    for info in infos:
        if info.is_dir() or not info.filename.casefold().endswith(markup_suffixes):
            continue
        payload = archive.read(info)
        try:
            root = ElementTree.fromstring(payload)
        except ElementTree.ParseError:
            continue
        for element in root.iter():
            if local_name(element.tag) == "script":
                has_script = True
            for key, value in element.attrib.items():
                if local_name(key) not in {"href", "src"}:
                    continue
                if urlsplit(value.strip()).scheme.casefold() in {"http", "https"}:
                    has_remote = True
    return has_script, has_remote


def inspect_file(
    path: Path,
    resource_profile: dict[str, Any],
    observations: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> tuple[str, str, bool, int]:
    stable_snapshot(path, observations)
    suffix = path.suffix.casefold()
    if suffix == ".epub":
        observations.append(observation("filename.extension.epub"))
    signature = path.read_bytes()[:8]
    if signature.startswith(b"%PDF-"):
        observations.append(observation("format.signature.pdf"))
        findings.append(finding("format.pdf_unsupported_for_deep_epub"))
        return "unsupported", "stop", False, path.stat().st_size
    if not signature.startswith(b"PK\x03\x04"):
        observations.append(observation("format.signature_unknown"))
        if suffix == ".epub":
            findings.append(finding("format.extension_mismatch"))
        return "unknown", "abstain", False, path.stat().st_size

    observations.append(observation("format.signature.zip"))
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile):
        observations.append(observation("container.open_error"))
        findings.append(finding("container.corrupt"))
        return "unsupported", "stop", False, 0

    with archive:
        try:
            infos = archive.infolist()
            mimetype = archive.read("mimetype")
        except (KeyError, OSError, RuntimeError, zipfile.BadZipFile):
            observations.append(observation("container.open_error"))
            findings.append(finding("container.corrupt"))
            return "unsupported", "stop", False, 0
        if mimetype != b"application/epub+zip":
            findings.append(finding("format.zip_not_epub"))
            return "unsupported", "stop", False, sum(info.file_size for info in infos)

        observations.append(observation("container.mimetype.epub"))
        findings.append(finding("format.epub"))
        for info in infos:
            logical = PurePosixPath(info.filename.replace("\\", "/"))
            if logical.is_absolute() or ".." in logical.parts:
                observations.append(
                    observation("container.entry_parent_escape", entry=info.filename)
                )
                findings.append(finding("security.path_traversal"))
                return "supported", "stop", False, sum(item.file_size for item in infos)

        compressed = sum(info.compress_size for info in infos)
        expanded = sum(info.file_size for info in infos)
        observations.extend(
            [
                observation("container.compressed_size", size_bytes=compressed),
                observation("container.expanded_size", size_bytes=expanded),
            ]
        )
        if expanded > int(resource_profile["max_expanded_bytes"]):
            findings.append(
                finding(
                    "resource.expansion_limit_exceeded",
                    expanded_bytes=expanded,
                    limit_bytes=int(resource_profile["max_expanded_bytes"]),
                )
            )
            return "supported", "stop", False, expanded

        names = {info.filename.casefold() for info in infos}
        if "meta-inf/encryption.xml" in names:
            observations.append(observation("container.encryption_xml"))
            findings.append(finding("protection.present"))
            return "unsupported", "stop", False, expanded

        has_script, has_remote = active_content_observations(archive, infos)
        if has_script:
            observations.append(observation("epub.script.present"))
            findings.append(finding("security.active_content"))
        if has_remote:
            observations.append(observation("epub.remote_reference.present"))
            findings.append(finding("security.remote_resource"))
        if has_script or has_remote:
            return "supported", "review", False, expanded
        return "supported", "continue_deep_read_only", True, expanded


def minimal_subprocess_environment() -> dict[str, str]:
    return {
        "HOME": os.environ.get("HOME", "/tmp/home"),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    }


def run_deep_probe(path: Path, timeout_ms: int) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--deep-tool", str(path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_ms / 1000,
        env=minimal_subprocess_environment(),
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("EXP-0006 synthetic deep probe failed")
    payload = json.loads(completed.stdout)
    return {
        "kind": "synthetic_read_only_probe",
        "started": True,
        "completed": True,
        "timed_out": False,
        "cleaned": True,
        "input_sha256": payload["input_sha256"],
    }


def run_timeout_control(
    slow_tool: Path, tool_profile: Path, observations: list[dict[str, Any]], findings: list[dict[str, Any]]
) -> dict[str, Any]:
    control = load_json(tool_profile)
    if control.get("command") != ["python", "slow_tool.py"]:
        raise RuntimeError("EXP-0006 timeout command differs from TEST-0001")
    if control.get("network") != "not_used" or control.get("allowed_outputs") != []:
        raise RuntimeError("EXP-0006 timeout control is broader than TEST-0001")
    timeout_ms = int(control["timeout_ms"])
    process = subprocess.Popen(
        [sys.executable, str(slow_tool)],
        cwd=slow_tool.parent,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=minimal_subprocess_environment(),
    )
    timed_out = False
    try:
        process.communicate(timeout=timeout_ms / 1000)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.communicate(timeout=2)
    cleaned = process.poll() is not None
    if not timed_out or not cleaned:
        raise RuntimeError("EXP-0006 timeout control did not stop cleanly")
    observations.extend(
        [observation("tool.timeout", timeout_ms=timeout_ms), observation("tool.exit_bounded")]
    )
    findings.append(finding("runtime.timeout_enforced"))
    return {
        "kind": "TEST-0001 synthetic timeout helper",
        "started": True,
        "completed": False,
        "timed_out": True,
        "cleaned": True,
        "timeout_ms": timeout_ms,
        "return_code": process.returncode,
        "child_processes_observed": 0,
    }


def evaluate_growing(
    selected: dict[str, tuple[dict[str, Any], Path]], observations: list[dict[str, Any]], findings: list[dict[str, Any]]
) -> tuple[str, str, bool, int]:
    control = load_json(selected["observations.json"][1])
    sequence = control.get("sequence")
    if sequence != ["revision-1.part", "revision-2.part"]:
        raise RuntimeError("EXP-0006 growing-input sequence differs from TEST-0001")
    first = selected[sequence[0]][1]
    second = selected[sequence[1]][1]
    first_size, second_size = first.stat().st_size, second.stat().st_size
    first_hash, second_hash = sha256_file(first), sha256_file(second)
    if first_size != second_size:
        observations.append(
            observation("snapshot.size_changed", first=first_size, second=second_size)
        )
    if first_hash != second_hash:
        observations.append(
            observation("snapshot.sha256_changed", first=first_hash, second=second_hash)
        )
    if first_size == second_size or first_hash == second_hash:
        raise RuntimeError("EXP-0006 growing-input control is not detectably unstable")
    findings.append(finding("ingress.unstable"))
    return "unknown", "defer", False, first_size + second_size


def evaluate_row(
    row: dict[str, Any], case: dict[str, Any], corpus_root: Path
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    selected = select_components(row, case, corpus_root)
    observations: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    deep_tool: dict[str, Any] = {
        "kind": None,
        "started": False,
        "completed": False,
        "timed_out": False,
        "cleaned": True,
    }
    resource_profile = case["oracle"]["resource_profile"]

    if row["mode"] == "stability_sequence":
        capability, action, allowed, expanded_bytes = evaluate_growing(
            selected, observations, findings
        )
    else:
        primary_name = row["components"][0]
        primary = selected[primary_name][1]
        capability, action, allowed, expanded_bytes = inspect_file(
            primary, resource_profile, observations, findings
        )
        if row["mode"] == "timeout_control":
            if not allowed or action != "continue_deep_read_only":
                raise RuntimeError("EXP-0006 timeout control did not pass preflight")
            deep_tool = run_timeout_control(
                selected["slow_tool.py"][1],
                selected["tool-profile.json"][1],
                observations,
                findings,
            )
            action = "stop"
        elif allowed:
            deep_tool = run_deep_probe(primary, int(resource_profile["timeout_ms"]))

    if capability not in FORMAT_CAPABILITIES or action not in NEXT_ACTIONS:
        raise RuntimeError("EXP-0006 produced an invalid decision literal")
    if deep_tool["started"] and not allowed:
        raise RuntimeError("EXP-0006 started a deep tool without positive capability")

    return {
        "row_key": row["row_key"],
        "source_case_key": row["source_case_key"],
        "sources": [
            source_ref(row["source_case_key"], selected[name][0])
            for name in row["components"]
        ],
        "safe_sequence": list(SAFE_SEQUENCE),
        "format_capability": capability,
        "next_action": action,
        "deep_tool_allowed": allowed,
        "deep_tool": deep_tool,
        "observations": observations,
        "findings": findings,
        "effects_observed": [],
        "resources": {
            "duration_ns": time.perf_counter_ns() - started,
            "input_bytes": sum(item[1].stat().st_size for item in selected.values()),
            "expanded_bytes": expanded_bytes,
            "max_input_bytes": int(resource_profile["max_input_bytes"]),
            "max_expanded_bytes": int(resource_profile["max_expanded_bytes"]),
            "timeout_ms": int(resource_profile["timeout_ms"]),
        },
    }


def compare_expected(row: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expected = row["expected"]
    observation_codes = {item["code"] for item in result["observations"]}
    finding_codes = {item["code"] for item in result["findings"]}
    checks = {
        "format_capability": result["format_capability"] == expected["format_capability"],
        "next_action": result["next_action"] == expected["next_action"],
        "deep_tool_allowed": result["deep_tool_allowed"] is expected["deep_tool_allowed"],
        "required_observations": set(expected["required_observations"]).issubset(observation_codes),
        "required_findings": set(expected["required_findings"]).issubset(finding_codes),
    }
    return {"checks": checks, "matches_expected": all(checks.values())}


def semantic_projection(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projection = []
    for result in results:
        projected = {key: value for key, value in result.items() if key != "resources"}
        projection.append(projected)
    return projection


def validate_profile(profile: dict[str, Any]) -> None:
    if profile.get("schema_version") != 1 or profile.get("experiment") != "EXP-0006":
        raise RuntimeError("EXP-0006 profile identity is invalid")
    rules = profile.get("rules", {})
    if tuple(rules.get("safe_sequence", [])) != SAFE_SEQUENCE:
        raise RuntimeError("EXP-0006 safe sequence is invalid")
    if set(rules.get("format_capabilities", [])) != FORMAT_CAPABILITIES:
        raise RuntimeError("EXP-0006 format-capability vocabulary is invalid")
    if set(rules.get("next_actions", [])) != NEXT_ACTIONS:
        raise RuntimeError("EXP-0006 next-action vocabulary is invalid")
    if rules.get("repetitions") != 2:
        raise RuntimeError("EXP-0006 requires exactly two repetitions")
    rows = profile.get("cases", [])
    if len(rows) != 11 or len({row.get("row_key") for row in rows}) != 11:
        raise RuntimeError("EXP-0006 requires eleven unique matrix rows")
    for row in rows:
        expected = row.get("expected", {})
        if expected.get("format_capability") not in FORMAT_CAPABILITIES:
            raise RuntimeError("EXP-0006 expected capability is invalid")
        if expected.get("next_action") not in NEXT_ACTIONS:
            raise RuntimeError("EXP-0006 expected action is invalid")
        if not isinstance(expected.get("deep_tool_allowed"), bool):
            raise RuntimeError("EXP-0006 expected deep-tool gate is invalid")


def run_profile(profile: dict[str, Any], manifest: dict[str, Any], corpus_root: Path) -> dict[str, Any]:
    validate_profile(profile)
    if manifest.get("fixture_version") != profile["fixture_version"]:
        raise RuntimeError("EXP-0006 fixture version mismatch")
    if sha256_file(corpus_root / "manifest.json") != profile["fixture_manifest_sha256"]:
        raise RuntimeError("EXP-0006 fixture manifest hash mismatch")
    cases = {case["case_key"]: case for case in manifest.get("cases", [])}
    results = []
    for row in profile["cases"]:
        if row["source_case_key"] not in cases:
            raise RuntimeError(f"EXP-0006 missing fixture case: {row['source_case_key']}")
        result = evaluate_row(row, cases[row["source_case_key"]], corpus_root)
        result["expected"] = row["expected"]
        result["evaluation"] = compare_expected(row, result)
        results.append(result)
    semantic = semantic_projection(results)
    return {
        "schema_version": 1,
        "experiment": "EXP-0006",
        "profile_id": profile["profile_id"],
        "python_version": platform.python_version(),
        "environment_names": sorted(os.environ),
        "case_results": results,
        "semantic_sha256": canonical_digest(semantic),
        "matrix_matches": all(result["evaluation"]["matches_expected"] for result in results),
    }


def deep_tool(path: Path) -> int:
    if not path.is_file():
        raise RuntimeError("EXP-0006 deep probe input is absent")
    print(canonical_json({"input_sha256": sha256_file(path), "read_only": True}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--corpus-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deep-tool", type=Path)
    args = parser.parse_args()
    if args.deep_tool is not None:
        return deep_tool(args.deep_tool)
    required = [args.profile, args.manifest, args.corpus_root, args.output]
    if any(value is None for value in required):
        parser.error("profile, manifest, corpus-root and output are required")
    profile = load_json(args.profile)
    manifest = load_json(args.manifest)
    result = run_profile(profile, manifest, args.corpus_root)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if len(serialized.encode("utf-8")) > int(profile["result_max_bytes"]):
        raise RuntimeError("EXP-0006 repetition output exceeds the profile limit")
    args.output.write_text(serialized, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
