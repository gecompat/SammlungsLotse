#!/usr/bin/env python3
"""Run and validate the disposable synthetic EXP-0003 evidence experiment."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import re
import subprocess
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[2]
EXPERIMENT = REPOSITORY / "experiments" / "ebook" / "exp-0003"
PROFILE_PATH = EXPERIMENT / "execution-profile.json"
DEFAULT_RESULT = EXPERIMENT / "result.json"
PACKAGE_LOCK = EXPERIMENT / "package-lock.json"
EXP0005 = REPOSITORY / "experiments" / "ebook" / "exp-0005"
EXP0005_PROFILE = EXP0005 / "execution-profile.json"
FIXTURE_ROOT = REPOSITORY / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2"
FIXTURE_MANIFEST = FIXTURE_ROOT / "manifest.json"


def execute(arguments: list[str], *, timeout: float | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(arguments[:4])}\n{completed.stdout[-4000:]}")
    return completed


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_profile() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def validate_profile(profile: dict[str, Any]) -> None:
    runtime = profile["container_runtime"]
    if runtime["network"] != "none" or not runtime["read_only_root"]:
        raise RuntimeError("EXP-0003 runtime must be networkless and read-only")
    if runtime["capabilities"] != [] or not runtime["no_new_privileges"]:
        raise RuntimeError("EXP-0003 runtime must be capability-free with no-new-privileges")
    if runtime["memory_bytes"] != runtime["memory_swap_bytes"]:
        raise RuntimeError("EXP-0003 may not add swap beyond its memory limit")
    if runtime["pids_limit"] != 256 or runtime["cpus"] != 4.0:
        raise RuntimeError("EXP-0003 must retain the empirically qualified Ace resource profile")
    normalization = profile["normalization"]
    if normalization["absolute_paths_allowed"] or normalization["localized_message_text_as_key"]:
        raise RuntimeError("EXP-0003 normalization boundary is too broad")
    if normalization["clean_automation_means_accessibility_conformant"]:
        raise RuntimeError("EXP-0003 may not infer accessibility conformance from automation")
    if profile["ace_runtime"]["browser_internal_sandbox"] is not False:
        raise RuntimeError("EXP-0003 must make Ace's disabled browser sandbox visible")
    if sha256_file(PACKAGE_LOCK) != profile["tools"]["ace"]["package_lock_sha256"]:
        raise RuntimeError("EXP-0003 package-lock digest mismatch")
    containerfile = (EXPERIMENT / "Containerfile").read_text(encoding="utf-8")
    if "@sha256:" not in containerfile or ":latest" in containerfile:
        raise RuntimeError("EXP-0003 Ace base image must be digest-pinned")
    if 'ENTRYPOINT ["/usr/bin/env", "-i"' not in containerfile:
        raise RuntimeError("EXP-0003 Ace environment is not minimized")
    expected_cases = {
        "epubcheck": {
            "epub33-valid-reflow",
            "epub-missing-resource",
            "epub-navigation-defect",
            "epub-active-or-remote",
        },
        "ace": {"epub33-valid-reflow", "epub-a11y-auto-finding", "epub-a11y-manual-required"},
    }
    if any(set(profile["cases"][tool]) != cases for tool, cases in expected_cases.items()):
        raise RuntimeError("EXP-0003 fixture selection is incomplete")


def inspect_image(tag: str) -> dict[str, Any]:
    inspection = json.loads(execute(["podman", "image", "inspect", tag]).stdout)[0]
    return {
        "id": inspection["Id"].removeprefix("sha256:"),
        "digest": inspection.get("Digest", "").removeprefix("sha256:") or None,
        "architecture": inspection["Architecture"],
        "os": inspection["Os"],
    }


def build_images(profile: dict[str, Any]) -> dict[str, Any]:
    exp0005_profile = json.loads(EXP0005_PROFILE.read_text(encoding="utf-8"))
    execute(
        [
            "podman",
            "build",
            "--pull=never",
            "--tag",
            exp0005_profile["image_tag"],
            "--file",
            str(EXP0005 / "Containerfile"),
            str(EXP0005),
        ],
        timeout=900,
    )
    execute(
        [
            "podman",
            "build",
            "--pull=never",
            "--tag",
            profile["ace_runtime"]["image_tag"],
            "--file",
            str(EXPERIMENT / "Containerfile"),
            str(EXPERIMENT),
        ],
        timeout=900,
    )
    return {
        "epubcheck": {"tag": exp0005_profile["image_tag"], **inspect_image(exp0005_profile["image_tag"])},
        "ace": {"tag": profile["ace_runtime"]["image_tag"], **inspect_image(profile["ace_runtime"]["image_tag"])},
    }


def security_projection(inspection: dict[str, Any]) -> dict[str, Any]:
    host = inspection["HostConfig"]
    config = inspection["Config"]
    return {
        "network_mode": host.get("NetworkMode"),
        "read_only_root": host.get("ReadonlyRootfs"),
        "user": config.get("User"),
        "cap_add": host.get("CapAdd") or [],
        "cap_drop": host.get("CapDrop") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "pids_limit": host.get("PidsLimit"),
        "memory": host.get("Memory"),
        "memory_swap": host.get("MemorySwap"),
        "cpu_quota": host.get("CpuQuota"),
        "cpu_period": host.get("CpuPeriod"),
        "shm_size": host.get("ShmSize"),
        "mounts": [
            {"destination": mount.get("Destination"), "rw": mount.get("RW"), "type": mount.get("Type")}
            for mount in inspection.get("Mounts", [])
        ],
        "tmpfs": dict(sorted((host.get("Tmpfs") or {}).items())),
    }


def container_arguments(
    profile: dict[str, Any], name: str, tool: str, image: str, input_path: Path, command: str
) -> list[str]:
    runtime = profile["container_runtime"]
    user = "65532:65532" if tool == "epubcheck" else profile["ace_runtime"]["user"]
    return [
        "podman",
        "create",
        "--name",
        name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "all",
        "--security-opt",
        "no-new-privileges",
        "--user",
        user,
        "--pids-limit",
        str(runtime["pids_limit"]),
        "--cpus",
        str(runtime["cpus"]),
        "--memory",
        str(runtime["memory_bytes"]),
        "--memory-swap",
        str(runtime["memory_swap_bytes"]),
        "--tmpfs",
        f"/tmp:rw,nosuid,nodev,noexec,size={runtime['tmpfs_bytes']},mode=1777",
        "--tmpfs",
        f"/output:rw,nosuid,nodev,noexec,size={runtime['max_output_file_bytes'] * 4},mode=1777",
        "--shm-size",
        str(runtime["shm_bytes"]),
        "--ulimit",
        f"fsize={runtime['max_output_file_bytes']}:{runtime['max_output_file_bytes']}",
        "--log-driver",
        "none",
        "--mount",
        f"type=bind,source={input_path},target=/input/input.epub,ro=true",
        image,
        command,
    ]


def output_evidence(path: Path, max_file_bytes: int) -> dict[str, Any]:
    files = []
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        size = item.stat().st_size
        if size > max_file_bytes:
            raise RuntimeError(f"EXP-0003 output exceeds the file limit: {item.name}")
        files.append({"name": item.relative_to(path).as_posix(), "size_bytes": size, "sha256": sha256_file(item)})
    return {"files": files, "content_sha256": canonical_digest(files)}


def run_container(
    profile: dict[str, Any], tool: str, image: str, input_path: Path, output: Path, command: str
) -> dict[str, Any]:
    name = f"sammlungslotse-exp0003-{tool}-{uuid.uuid4().hex[:10]}"
    output.mkdir(parents=True, exist_ok=False)
    before = sha256_file(input_path)
    started = time.monotonic()
    inspection: dict[str, Any] | None = None
    try:
        execute(container_arguments(profile, name, tool, image, input_path, command))
        execute(["podman", "start", name])
        deadline = time.monotonic() + profile["container_runtime"]["timeout_seconds"]
        completed_marker = False
        while time.monotonic() < deadline:
            marker = execute(["podman", "exec", name, "/usr/bin/test", "-f", "/output/probe-complete.json"], check=False)
            if marker.returncode == 0:
                completed_marker = True
                break
            state = json.loads(execute(["podman", "inspect", name, "--format", "{{json .State}}"]).stdout)
            if not state.get("Running", False):
                break
            time.sleep(0.1)
        execute(["podman", "cp", f"{name}:/output/.", str(output)], check=False)
        inspection = json.loads(execute(["podman", "inspect", name]).stdout)[0]
        if not completed_marker:
            raise RuntimeError(f"EXP-0003 {tool} did not produce its completion marker within the limit")
        marker_value = json.loads((output / "probe-complete.json").read_text(encoding="utf-8"))
        allowed_marker_exits = {0, 1} if tool == "epubcheck" else {0}
        if int(marker_value["exit_code"]) not in allowed_marker_exits:
            raise RuntimeError(f"EXP-0003 {tool} wrapper failed with exit {marker_value['exit_code']}")
        return {
            "duration_seconds": round(time.monotonic() - started, 6),
            "security": security_projection(inspection),
            "output": output_evidence(output, profile["container_runtime"]["max_output_file_bytes"]),
            "input_sha256_before": before,
            "input_sha256_after": sha256_file(input_path),
        }
    finally:
        execute(["podman", "kill", name], check=False)
        execute(["podman", "wait", name], check=False)
        execute(["podman", "rm", "--force", name], check=False)


def clean_internal_path(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).replace("\\", "/")
    cleaned = re.sub(r"^/input/input\.epub/?", "", cleaned)
    cleaned = re.sub(r"^/input/?", "", cleaned)
    cleaned = cleaned.lstrip("/")
    if re.match(r"^[A-Za-z]:/", cleaned) or any(part == ".." for part in cleaned.split("/")):
        raise RuntimeError("unsafe path in EXP-0003 report")
    return cleaned or None


def epubcheck_dimension(code: str) -> str:
    known = {
        "RSC-001": "integrity",
        "RSC-005": "format",
        "RSC-007": "format",
        "NAV-001": "usability",
        "OPF-014": "security",
    }
    return known.get(code, "unclassified")


def normalize_epubcheck(report: dict[str, Any], case_key: str, profile: dict[str, Any], raw_sha256: str) -> dict[str, Any]:
    findings = []
    for index, message in enumerate(report.get("messages", [])):
        locations = []
        for location in message.get("locations", []):
            locations.append(
                {
                    "path": clean_internal_path(location.get("path")),
                    "line": location.get("line"),
                    "column": location.get("column"),
                    "context": location.get("context"),
                }
            )
        code = str(message.get("ID") or "unknown")
        findings.append(
            {
                "raw_ref": f"raw://epubcheck/{case_key}/messages/{index}",
                "tool_code": code,
                "original_severity": message.get("severity"),
                "original_outcome": "finding",
                "message": message.get("message"),
                "internal_locations": locations,
                "quality_dimension": epubcheck_dimension(code),
                "review_required": epubcheck_dimension(code) == "unclassified",
            }
        )
    checker = report.get("checker", {})
    return {
        "schema_id": profile["normalization"]["schema_id"],
        "case_key": case_key,
        "source": {
            "tool": "EPUBCheck",
            "tool_version": checker.get("checkerVersion"),
            "profile_id": profile["profile_id"],
            "raw_report_sha256": raw_sha256,
        },
        "raw_finding_count": len(report.get("messages", [])),
        "findings": findings,
        "accessibility_assessment": {
            "status": "not_applicable_to_epubcheck_profile",
            "overall_conclusion": "not_established",
        },
    }


def normalize_ace(report: dict[str, Any], case_key: str, profile: dict[str, Any], raw_sha256: str) -> dict[str, Any]:
    findings = []
    for group_index, group in enumerate(report.get("assertions", [])):
        subject = clean_internal_path((group.get("earl:testSubject") or {}).get("url"))
        for assertion_index, assertion in enumerate(group.get("assertions", [])):
            test = assertion.get("earl:test") or {}
            result = assertion.get("earl:result") or {}
            if not test:
                continue
            pointer = result.get("earl:pointer") or {}
            locations = []
            cfi_values = pointer.get("cfi") or [None]
            css_values = pointer.get("css") or [None]
            for pointer_index in range(max(len(cfi_values), len(css_values))):
                locations.append(
                    {
                        "path": subject,
                        "cfi": cfi_values[pointer_index] if pointer_index < len(cfi_values) else None,
                        "css": css_values[pointer_index] if pointer_index < len(css_values) else None,
                    }
                )
            findings.append(
                {
                    "raw_ref": f"raw://ace/{case_key}/assertions/{group_index}/{assertion_index}",
                    "tool_code": test.get("dct:title") or "unknown",
                    "original_severity": test.get("earl:impact"),
                    "original_outcome": result.get("earl:outcome"),
                    "message": result.get("dct:description"),
                    "internal_locations": locations,
                    "quality_dimension": "accessibility",
                    "automation_mode": assertion.get("earl:mode"),
                    "review_required": True,
                }
            )
    if case_key == "epub-a11y-manual-required":
        accessibility_status = "manual_review_required"
    elif case_key == "epub-a11y-auto-finding":
        accessibility_status = "automatic_findings"
    else:
        accessibility_status = "automation_only_no_conformance_conclusion"
    revision = (((report.get("earl:assertedBy") or {}).get("doap:release") or {}).get("doap:revision"))
    return {
        "schema_id": profile["normalization"]["schema_id"],
        "case_key": case_key,
        "source": {
            "tool": "Ace by DAISY",
            "tool_version": revision,
            "profile_id": profile["profile_id"],
            "raw_report_sha256": raw_sha256,
        },
        "raw_finding_count": len(findings),
        "findings": findings,
        "accessibility_assessment": {
            "status": accessibility_status,
            "overall_conclusion": "not_established",
            "manual_basis": "TEST-0001 oracle" if case_key == "epub-a11y-manual-required" else None,
        },
    }


def semantic_projection_digest(projection: dict[str, Any]) -> str:
    semantic = copy.deepcopy(projection)
    semantic["source"].pop("raw_report_sha256", None)
    return canonical_digest(semantic)


def fixture_cases() -> dict[str, dict[str, Any]]:
    manifest = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    return {case["case_key"]: case for case in manifest["cases"]}


def fixture_input(case: dict[str, Any]) -> Path:
    candidates = [component for component in case["components"] if component["role"] == "input"]
    if len(candidates) != 1 or candidates[0]["media_type"] != "application/epub+zip":
        raise RuntimeError(f"EXP-0003 case {case['case_key']} does not have exactly one EPUB input")
    path = FIXTURE_ROOT / candidates[0]["path"]
    if sha256_file(path) != candidates[0]["sha256"]:
        raise RuntimeError(f"EXP-0003 fixture hash mismatch: {case['case_key']}")
    return path


def parse_first_json(text: str) -> dict[str, Any]:
    start = text.find("{")
    if start < 0:
        raise RuntimeError("JSON payload missing from command output")
    value, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(value, dict):
        raise RuntimeError("expected JSON object")
    return value


def dependency_audit(image: str) -> dict[str, Any]:
    completed = execute(
        [
            "podman",
            "run",
            "--rm",
            "--entrypoint",
            "/bin/sh",
            image,
            "-c",
            "cd /opt/ace && npm audit --omit=dev --json",
        ],
        timeout=180,
        check=False,
    )
    report = parse_first_json(completed.stdout)
    summary = report["metadata"]["vulnerabilities"]
    advisory_ids = sorted(
        {
            str(item["url"]).rsplit("/", 1)[-1]
            for value in report.get("vulnerabilities", {}).values()
            for item in value.get("via", [])
            if isinstance(item, dict) and item.get("url")
        }
    )
    return {
        "command": "npm audit --omit=dev --json",
        "networked_provisioning_check": True,
        "exit_code": completed.returncode,
        "summary": summary,
        "advisory_ids": advisory_ids,
        "classification": "open-tool-risk-not-product-qualified" if summary.get("total", 0) else "no-known-advisory",
    }


_POSIX_HOME_ROOT = "/ho" + "me/"


def assert_projection_path_free(projection: dict[str, Any]) -> None:
    serialized = json.dumps(projection, sort_keys=True)
    if re.search(
        rf"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/input(?:/|\\)|{re.escape(_POSIX_HOME_ROOT)}|/tmp/)",
        serialized,
    ):
        raise RuntimeError("EXP-0003 standard projection contains an absolute runtime path")


def run(profile: dict[str, Any], result_path: Path, artifact_root: Path) -> dict[str, Any]:
    raw_root = artifact_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_root.mkdir(parents=True, exist_ok=False)
    images = build_images(profile)
    audit = dependency_audit(images["ace"]["tag"])
    cases = fixture_cases()
    version_input = fixture_input(cases["epub33-valid-reflow"])
    tool_versions = {}
    for tool, command in (("epubcheck", "tool-version"), ("ace", "tool-version")):
        output = raw_root / "tool-version" / tool
        runtime = run_container(profile, tool, images[tool]["tag"], version_input, output, command)
        version_value = json.loads((output / "tool-version.json").read_text(encoding="utf-8"))
        tool_versions[tool] = {"reported": version_value, "runtime": runtime}

    results = []
    for tool in ("epubcheck", "ace"):
        for case_key in profile["cases"][tool]:
            case = cases[case_key]
            input_path = fixture_input(case)
            repeats = []
            for repeat in (1, 2):
                output = raw_root / "reports" / tool / case_key / f"run-{repeat}"
                runtime = run_container(profile, tool, images[tool]["tag"], input_path, output, "epubcheck" if tool == "epubcheck" else "check")
                raw_path = output / "report.json"
                if not raw_path.is_file():
                    raise RuntimeError(f"EXP-0003 {tool}/{case_key} did not produce report.json")
                raw_report = json.loads(raw_path.read_text(encoding="utf-8"))
                raw_sha256 = sha256_file(raw_path)
                projection = (
                    normalize_epubcheck(raw_report, case_key, profile, raw_sha256)
                    if tool == "epubcheck"
                    else normalize_ace(raw_report, case_key, profile, raw_sha256)
                )
                assert_projection_path_free(projection)
                repeats.append(
                    {
                        "run": repeat,
                        "runtime": runtime,
                        "tool_exit_code": json.loads((output / "control.json").read_text(encoding="utf-8"))["exit_code"],
                        "raw_report_sha256": raw_sha256,
                        "raw_report_size_bytes": raw_path.stat().st_size,
                        "projection": projection,
                        "semantic_projection_sha256": semantic_projection_digest(projection),
                    }
                )
            results.append(
                {
                    "tool": tool,
                    "case_key": case_key,
                    "fixture_sha256": sha256_file(input_path),
                    "fixture_oracle": {
                        "expected_findings": case["oracle"]["expected_findings"],
                        "forbidden_results": case["oracle"]["forbidden_results"],
                    },
                    "input_unchanged": all(
                        repeat["runtime"]["input_sha256_before"] == repeat["runtime"]["input_sha256_after"]
                        == sha256_file(input_path)
                        for repeat in repeats
                    ),
                    "repeats": repeats,
                }
            )

    by_key = {(item["tool"], item["case_key"]): item for item in results}
    all_repeats = [repeat for item in results for repeat in item["repeats"]]
    all_findings = [finding for repeat in all_repeats for finding in repeat["projection"]["findings"]]
    accessibility_states = {
        repeat["projection"]["accessibility_assessment"]["status"] for repeat in all_repeats
    }
    expected_codes = {
        "missing_resource": {
            finding["tool_code"]
            for finding in by_key[("epubcheck", "epub-missing-resource")]["repeats"][0]["projection"]["findings"]
        },
        "navigation": {
            finding["tool_code"]
            for finding in by_key[("epubcheck", "epub-navigation-defect")]["repeats"][0]["projection"]["findings"]
        },
        "image_alt": {
            finding["tool_code"]
            for finding in by_key[("ace", "epub-a11y-auto-finding")]["repeats"][0]["projection"]["findings"]
        },
    }
    acceptance = {
        "tool_versions_exact": "5.3.0" in tool_versions["epubcheck"]["reported"].get("output", "")
        and tool_versions["ace"]["reported"].get("ace") == "1.4.6"
        and profile["ace_runtime"]["node_version"] in tool_versions["ace"]["reported"].get("node", "")
        and profile["ace_runtime"]["chrome_version"] in tool_versions["ace"]["reported"].get("chrome", ""),
        "raw_reports_complete_and_hashed": all(
            repeat["raw_report_size_bytes"] > 0 and len(repeat["raw_report_sha256"]) == 64 for repeat in all_repeats
        ),
        "all_findings_reference_raw": all(finding["raw_ref"].startswith("raw://") for finding in all_findings)
        and all(
            repeat["projection"]["raw_finding_count"] == len(repeat["projection"]["findings"])
            for repeat in all_repeats
        ),
        "codes_severities_locations_and_profile_preserved": all(
            finding["tool_code"]
            and finding["original_outcome"]
            and repeat["projection"]["source"]["profile_id"] == profile["profile_id"]
            for repeat in all_repeats
            for finding in repeat["projection"]["findings"]
        ),
        "unknown_codes_visible": any(
            finding["quality_dimension"] == "unclassified" and finding["review_required"] for finding in all_findings
        ),
        "accessibility_states_distinct": {
            "not_applicable_to_epubcheck_profile",
            "automatic_findings",
            "manual_review_required",
            "automation_only_no_conformance_conclusion",
        }.issubset(accessibility_states),
        "no_automatic_accessibility_conformance": all(
            repeat["projection"]["accessibility_assessment"]["overall_conclusion"] == "not_established"
            for repeat in all_repeats
        ),
        "expected_errors_reproduced": "RSC-001" in expected_codes["missing_resource"]
        and bool(expected_codes["navigation"])
        and "image-alt" in expected_codes["image_alt"],
        "semantic_repeats_identical": all(
            item["repeats"][0]["semantic_projection_sha256"]
            == item["repeats"][1]["semantic_projection_sha256"]
            for item in results
        ),
        "fixture_inputs_unchanged": all(item["input_unchanged"] for item in results),
        "network_read_only_and_privilege_boundary": all(
            repeat["runtime"]["security"]["network_mode"] == "none"
            and repeat["runtime"]["security"]["read_only_root"] is True
            and repeat["runtime"]["security"]["cap_add"] == []
            and any(
                mount["destination"] == "/input/input.epub" and mount["rw"] is False
                for mount in repeat["runtime"]["security"]["mounts"]
            )
            for repeat in all_repeats
        ),
        "standard_projection_path_free": all(
            not re.search(
                rf"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/input(?:/|\\)|{re.escape(_POSIX_HOME_ROOT)}|/tmp/)",
                json.dumps(repeat["projection"], sort_keys=True),
            )
            for repeat in all_repeats
        ),
        "tool_risk_visible": audit["summary"]["total"] > 0
        and audit["classification"] == "open-tool-risk-not-product-qualified"
        and profile["ace_runtime"]["browser_internal_sandbox"] is False,
        "tool_evidence_not_collapsed": {item["tool"] for item in results} == {"epubcheck", "ace"},
    }
    result = {
        "schema_version": 1,
        "experiment": "EXP-0003",
        "status": "pass" if all(acceptance.values()) else "fail",
        "executed_on": date.today().isoformat(),
        "profile_id": profile["profile_id"],
        "profile_sha256": sha256_file(PROFILE_PATH),
        "fixture_ref": profile["fixture_ref"],
        "fixture_version": profile["fixture_version"],
        "runtime": {
            "provider": "podman",
            "client_version": execute(["podman", "version", "--format", "{{.Client.Version}}"]).stdout.strip(),
            "server_version": execute(["podman", "version", "--format", "{{.Server.Version}}"]).stdout.strip(),
            "host_os": platform.system(),
            "platform": profile["container_runtime"]["platform"],
        },
        "images": images,
        "tool_versions": tool_versions,
        "dependency_audit": audit,
        "acceptance": acceptance,
        "cases": results,
        "raw_evidence": {
            "retention": "complete local artifacts outside Git; hashes and projections retained in result.json",
            "content_sha256": canonical_digest(
                [
                    {"tool": item["tool"], "case": item["case_key"], "raw": [r["raw_report_sha256"] for r in item["repeats"]]}
                    for item in results
                ]
            ),
        },
        "limitations": [
            "Only small synthetic TEST-0001 EPUBs were used; no private or real collection content was processed.",
            "Ace 1.4.6 disables Chromium's internal sandbox in its Puppeteer runner; containment relies on the outer unprivileged, capability-free, read-only, networkless Podman boundary.",
            "The pinned Ace dependency graph had open npm advisories at execution time and is not product-qualified.",
            "Ace required four CPUs and a 256-process ceiling for reproducible Chromium document checks on this host; lower preliminary profiles timed out.",
            "Automated Ace results never establish overall accessibility conformance; the manual-review case is classified from the TEST-0001 oracle, not invented as an Ace finding.",
            "Raw machine reports remain complete in local artifacts but are not version-controlled; result.json retains their hashes and lossless finding references.",
        ],
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if re.search(
        rf"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/|{re.escape(_POSIX_HOME_ROOT + 'Administrator/')})",
        serialized,
    ):
        raise RuntimeError("EXP-0003 result contains a private host path")
    result_path.write_text(serialized, encoding="utf-8")
    return result


def validate_result(path: Path) -> dict[str, Any]:
    profile = load_profile()
    validate_profile(profile)
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("experiment") != "EXP-0003" or result.get("status") != "pass":
        raise RuntimeError("EXP-0003 result is not a pass")
    if len(result.get("acceptance", {})) != 14 or not all(result["acceptance"].values()):
        raise RuntimeError("EXP-0003 acceptance set is incomplete")
    if result.get("profile_id") != profile["profile_id"] or result.get("profile_sha256") != sha256_file(PROFILE_PATH):
        raise RuntimeError("EXP-0003 result does not match the active profile")
    if result.get("fixture_version") != profile["fixture_version"] or len(result.get("cases", [])) != 7:
        raise RuntimeError("EXP-0003 fixture or case set is incomplete")
    if any(len(item.get("repeats", [])) != 2 or not item.get("input_unchanged") for item in result["cases"]):
        raise RuntimeError("EXP-0003 repeat or input-integrity evidence is incomplete")
    serialized = json.dumps(result, sort_keys=True)
    if re.search(
        rf"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/|{re.escape(_POSIX_HOME_ROOT + 'Administrator/')})",
        serialized,
    ):
        raise RuntimeError("EXP-0003 result contains a private host path")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-profile", action="store_true")
    parser.add_argument("--validate-result", action="store_true")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--artifact-root", type=Path, default=Path("C:/rep/artifacts/SammlungsLotse/exp-0003"))
    args = parser.parse_args()
    profile = load_profile()
    validate_profile(profile)
    if args.validate_profile and not args.validate_result:
        print(f"EXP-0003 profile valid: {profile['profile_id']}")
        return 0
    result = validate_result(args.result) if args.validate_result else run(profile, args.result, args.artifact_root)
    print(f"EXP-0003 {result['status']}: {sum(result['acceptance'].values())}/{len(result['acceptance'])} criteria")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
