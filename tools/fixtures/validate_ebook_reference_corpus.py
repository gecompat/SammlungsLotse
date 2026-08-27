#!/usr/bin/env python3
"""Validate TEST-0001 fixture integrity, semantics and reproducibility."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2"
GENERATOR_PATH = ROOT / "tools" / "fixtures" / "generate_ebook_reference_corpus.py"
TEXT_SUFFIXES = {".json", ".opf", ".py", ".svg", ".txt", ".xhtml", ".xml"}
BINARY_FIXTURE_SUFFIXES = {".epub", ".part", ".pdf"}
_WINDOWS_USERS_RE = r"[a-z]:\\u" + r"sers\\[^\\\s]+"
_POSIX_HOME_RE = r"/ho" + r"me/[^/\s]+"
PRIVATE_PATH_RE = re.compile(rf"(?i)(?:{_WINDOWS_USERS_RE}|{_POSIX_HOME_RE})")
SECRET_RE = re.compile(
    r"(?i)(?:gh[pousr]_[A-Za-z0-9_]{20,}|(?:password|api[_-]?key|secret)\s*[:=]\s*[^\s\"']+)"
)
URL_RE = re.compile(r"https?://[^\s\"'<>]+")
ALLOWED_NAMESPACE_URLS = {
    "http://purl.org/dc/elements/1.1/",
    "http://www.idpf.org/2007/opf",
    "http://www.idpf.org/2007/ops",
    "http://www.w3.org/1999/xhtml",
    "http://www.w3.org/2000/svg",
    "http://www.w3.org/2001/04/xmlenc#",
}

REQUIRED_ORACLE_FIELDS = {
    "expected_observations",
    "expected_findings",
    "allowed_results",
    "forbidden_results",
    "forbidden_effects",
    "quality_dimensions",
    "resource_profile",
    "validation",
}
REQUIRED_RESOURCE_FIELDS = {
    "network",
    "max_input_bytes",
    "max_expanded_bytes",
    "timeout_ms",
    "abort_condition",
}
REQUIRED_FORBIDDEN_EFFECTS = {
    "modify_original",
    "network_access",
    "write_domain_system",
}


def load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_test_0001_generator", GENERATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_state(root: Path) -> dict[str, tuple[int, str]]:
    return {
        path.relative_to(root).as_posix(): (path.stat().st_size, sha256_path(path))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def case_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = manifest.get("cases", [])
    if not isinstance(cases, list):
        return {}
    return {
        case.get("case_key"): case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("case_key"), str)
    }


def component_path(corpus_root: Path, case: dict[str, Any], name: str) -> Path:
    for item in case.get("components", []):
        if PurePosixPath(item.get("path", "")).name == name:
            return corpus_root / Path(*PurePosixPath(item["path"]).parts)
    raise KeyError(f"component not found for {case.get('case_key')}: {name}")


def zip_entries(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def normalized_zip_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for name, content in sorted(zip_entries(path).items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def validate_manifest(corpus_root: Path, manifest: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    generator = load_generator()

    if manifest.get("schema_version") != 1:
        problems.append("manifest schema_version must be 1")
    if manifest.get("corpus_ref") != "TEST-0001":
        problems.append("manifest corpus_ref must be TEST-0001")
    if manifest.get("fixture_version") != generator.FIXTURE_VERSION:
        problems.append("manifest fixture_version differs from generator")
    if manifest.get("scope") != "core":
        problems.append("manifest scope must be core")
    if manifest.get("data_class") != "SYNTHETIC_OR_REDISTRIBUTABLE":
        problems.append("manifest data_class is not synthetic/redistributable")
    if manifest.get("license", {}).get("spdx") != "MIT":
        problems.append("manifest license must be MIT")
    profile = manifest.get("generator_profile", {})
    if profile.get("implementation") != "tools/fixtures/generate_ebook_reference_corpus.py":
        problems.append("manifest generator implementation locator is unexpected")
    if profile.get("implementation_digest_algorithm") != "sha256-utf8-lf":
        problems.append("manifest generator digest algorithm is unexpected")
    if profile.get("implementation_sha256") != generator.sha256_portable_text(
        GENERATOR_PATH
    ):
        problems.append("manifest generator implementation hash is stale")
    if profile.get("network") != "not_used":
        problems.append("fixture generation must not use network")
    if profile.get("external_dependencies") != []:
        problems.append("fixture generator must not declare external dependencies")

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        return [*problems, "manifest cases must be a list"]
    keys = [case.get("case_key") for case in cases if isinstance(case, dict)]
    if tuple(keys) != tuple(generator.CORE_CASE_KEYS):
        problems.append("manifest cases do not exactly match ordered core contract")
    if manifest.get("deferred_expansion_case_keys") != list(
        generator.DEFERRED_EXPANSION_CASE_KEYS
    ):
        problems.append("manifest expansion deferrals differ from generator contract")
    if len(keys) != len(set(keys)):
        problems.append("manifest contains duplicate case_key values")

    declared_components: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            problems.append("case entry must be an object")
            continue
        key = case.get("case_key", "<missing>")
        if case.get("stage") != "core":
            problems.append(f"{key}: stage must be core")
        scenarios = case.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            problems.append(f"{key}: scenarios must be a non-empty list")
        provenance = case.get("provenance", {})
        if provenance.get("third_party_material") is not False:
            problems.append(f"{key}: third_party_material must be false")
        if provenance.get("license_spdx") != "MIT":
            problems.append(f"{key}: provenance license must be MIT")

        oracle = case.get("oracle")
        if not isinstance(oracle, dict):
            problems.append(f"{key}: oracle must be an object")
            continue
        missing_oracle = REQUIRED_ORACLE_FIELDS - set(oracle)
        if missing_oracle:
            problems.append(f"{key}: missing oracle fields {sorted(missing_oracle)}")
        for field in (
            "expected_observations",
            "expected_findings",
            "allowed_results",
            "forbidden_results",
            "forbidden_effects",
            "quality_dimensions",
        ):
            if not isinstance(oracle.get(field), list):
                problems.append(f"{key}: oracle.{field} must be a list")
        effects = set(oracle.get("forbidden_effects", []))
        if not REQUIRED_FORBIDDEN_EFFECTS.issubset(effects):
            problems.append(f"{key}: common forbidden effects are incomplete")
        resource = oracle.get("resource_profile", {})
        if not isinstance(resource, dict) or not REQUIRED_RESOURCE_FIELDS.issubset(
            resource
        ):
            problems.append(f"{key}: resource profile is incomplete")
        elif resource.get("network") != "denied":
            problems.append(f"{key}: network must be denied")
        validation = oracle.get("validation", {})
        if not isinstance(validation, dict) or not validation.get("method"):
            problems.append(f"{key}: validation method is missing")
        if validation.get("manual_steps") != []:
            problems.append(f"{key}: core corpus must not claim pending manual steps")

        components = case.get("components")
        if not isinstance(components, list) or not components:
            problems.append(f"{key}: components must be a non-empty list")
            continue
        for item in components:
            if not isinstance(item, dict):
                problems.append(f"{key}: component must be an object")
                continue
            raw_path = item.get("path")
            if not isinstance(raw_path, str):
                problems.append(f"{key}: component path missing")
                continue
            relative = PurePosixPath(raw_path)
            if relative.is_absolute() or ".." in relative.parts or "\\" in raw_path:
                problems.append(f"{key}: unsafe component path {raw_path}")
                continue
            expected_prefix = PurePosixPath("cases") / key
            if relative.parent != expected_prefix and expected_prefix not in relative.parents:
                problems.append(f"{key}: component outside case directory {raw_path}")
            if raw_path in declared_components:
                problems.append(f"duplicate component path: {raw_path}")
            declared_components.add(raw_path)
            target = corpus_root / Path(*relative.parts)
            try:
                target.resolve().relative_to(corpus_root.resolve())
            except ValueError:
                problems.append(f"{key}: component resolves outside corpus {raw_path}")
                continue
            if not target.is_file():
                problems.append(f"{key}: component missing {raw_path}")
                continue
            size = target.stat().st_size
            digest = sha256_path(target)
            if item.get("size_bytes") != size:
                problems.append(f"{key}: size mismatch {raw_path}")
            if item.get("sha256") != digest:
                problems.append(f"{key}: hash mismatch {raw_path}")
            if not item.get("role") or not item.get("media_type"):
                problems.append(f"{key}: component metadata incomplete {raw_path}")

    actual_components = {
        path.relative_to(corpus_root).as_posix()
        for path in corpus_root.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    undeclared = sorted(actual_components - declared_components)
    missing = sorted(declared_components - actual_components)
    if undeclared:
        problems.append(f"undeclared corpus files: {undeclared}")
    if missing:
        problems.append(f"declared corpus files missing: {missing}")

    binary_paths = sorted(
        path
        for path in actual_components
        if PurePosixPath(path).suffix.lower() in BINARY_FIXTURE_SUFFIXES
    )
    if binary_paths:
        repository_paths = [
            (corpus_root.relative_to(ROOT) / Path(*PurePosixPath(path).parts)).as_posix()
            for path in binary_paths
        ]
        try:
            result = subprocess.run(
                ["git", "check-attr", "text", "--", *repository_paths],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            problems.append(f"cannot verify binary fixture attributes: {exc}")
        else:
            for line in result.stdout.splitlines():
                path, separator, value = line.rpartition(": text: ")
                if not separator or value != "unset":
                    problems.append(
                        f"binary fixture is not protected from text conversion: "
                        f"{path or line}"
                    )
    return problems


def validate_privacy(corpus_root: Path) -> list[str]:
    problems: list[str] = []

    def check_text(label: str, value: str) -> None:
        if PRIVATE_PATH_RE.search(value):
            problems.append(f"private absolute path found in {label}")
        if SECRET_RE.search(value):
            problems.append(f"credential-like text found in {label}")
        for url in URL_RE.findall(value):
            if (
                url not in ALLOWED_NAMESPACE_URLS
                and not url.startswith("https://example.invalid/")
            ):
                problems.append(f"unexpected URL in {label}: {url}")

    for path in sorted(corpus_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(corpus_root).as_posix()
        if path.suffix.lower() in TEXT_SUFFIXES:
            try:
                check_text(relative, path.read_text(encoding="utf-8"))
            except UnicodeDecodeError as exc:
                problems.append(f"text fixture is not UTF-8: {path.name}: {exc}")
        if path.suffix.lower() == ".epub" and zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                for entry in archive.infolist():
                    if PurePosixPath(entry.filename).suffix.lower() not in TEXT_SUFFIXES:
                        continue
                    try:
                        value = archive.read(entry).decode("utf-8")
                    except UnicodeDecodeError as exc:
                        problems.append(
                            f"embedded text fixture is not UTF-8: "
                            f"{relative}!{entry.filename}: {exc}"
                        )
                        continue
                    check_text(f"{relative}!{entry.filename}", value)
    return problems


def validate_case_semantics(
    corpus_root: Path, manifest: dict[str, Any], *, execute_timeout: bool
) -> list[str]:
    problems: list[str] = []
    cases = case_map(manifest)

    try:
        first = component_path(corpus_root, cases["ingress-growing-file"], "revision-1.part")
        second = component_path(corpus_root, cases["ingress-growing-file"], "revision-2.part")
        if first.stat().st_size >= second.stat().st_size or sha256_path(first) == sha256_path(second):
            problems.append("ingress-growing-file does not contain two changing revisions")

        corrupt = component_path(corpus_root, cases["container-corrupt"], "corrupt.epub")
        try:
            with zipfile.ZipFile(corrupt) as archive:
                archive.testzip()
        except (zipfile.BadZipFile, EOFError):
            pass
        else:
            problems.append("container-corrupt unexpectedly opens as a complete ZIP")

        traversal = component_path(corpus_root, cases["container-path-traversal"], "traversal.epub")
        with zipfile.ZipFile(traversal) as archive:
            names = archive.namelist()
        if "../escape.txt" not in names:
            problems.append("container-path-traversal lacks the declared escape entry")

        expansion = component_path(corpus_root, cases["container-expansion-limit"], "expansion.epub")
        with zipfile.ZipFile(expansion) as archive:
            expanded_size = sum(item.file_size for item in archive.infolist())
        limit = cases["container-expansion-limit"]["oracle"]["resource_profile"]["max_expanded_bytes"]
        if expanded_size <= limit:
            problems.append("container-expansion-limit does not exceed its declared limit")

        protected = zip_entries(component_path(corpus_root, cases["protected-or-encrypted"], "protected.epub"))
        if "META-INF/encryption.xml" not in protected or b"synthetic:no-decryption" not in protected.get("META-INF/encryption.xml", b""):
            problems.append("protected-or-encrypted lacks its harmless synthetic marker")

        unknown = component_path(corpus_root, cases["format-unknown"], "unknown.epub").read_bytes()
        if unknown.startswith(b"PK"):
            problems.append("format-unknown unexpectedly has a ZIP signature")

        valid = component_path(corpus_root, cases["epub33-valid-reflow"], "valid-reflow.epub")
        with zipfile.ZipFile(valid) as archive:
            infos = archive.infolist()
            entries = {item.filename: archive.read(item.filename) for item in infos}
        if not infos or infos[0].filename != "mimetype" or infos[0].compress_type != zipfile.ZIP_STORED:
            problems.append("epub33-valid-reflow violates deterministic mimetype placement")
        package = entries.get("EPUB/package.opf", b"")
        # EPUB 3.3 publications continue to use OPF package version="3.0".
        if entries.get("mimetype") != b"application/epub+zip" or b'version="3.0"' not in package:
            problems.append("epub33-valid-reflow lacks expected EPUB 3.3 markers")
        if b'properties="cover-image"' not in package or "EPUB/image.svg" not in entries:
            problems.append("epub33-valid-reflow lacks its declared synthetic cover")

        stable = component_path(corpus_root, cases["ingress-stable-minimal"], "stable.epub")
        if not zipfile.is_zipfile(stable) or zip_entries(stable).get("mimetype") != b"application/epub+zip":
            problems.append("ingress-stable-minimal is not a readable EPUB snapshot")

        missing_entries = zip_entries(component_path(corpus_root, cases["epub-missing-resource"], "missing-resource.epub"))
        if b'href="chapter.xhtml"' not in missing_entries.get("EPUB/package.opf", b"") or "EPUB/chapter.xhtml" in missing_entries:
            problems.append("epub-missing-resource does not match its missing-entry oracle")

        nav_entries = zip_entries(component_path(corpus_root, cases["epub-navigation-defect"], "navigation-defect.epub"))
        if b"missing-nav-target.xhtml" not in nav_entries.get("EPUB/nav.xhtml", b"") or "EPUB/missing-nav-target.xhtml" in nav_entries:
            problems.append("epub-navigation-defect does not match its broken-target oracle")

        active_entries = zip_entries(component_path(corpus_root, cases["epub-active-or-remote"], "active-remote.epub"))
        active_chapter = active_entries.get("EPUB/chapter.xhtml", b"")
        if b"<script" not in active_chapter or b"https://example.invalid/" not in active_chapter:
            problems.append("epub-active-or-remote lacks declared active/remote markers")

        auto_entries = zip_entries(component_path(corpus_root, cases["epub-a11y-auto-finding"], "a11y-auto.epub"))
        manual_entries = zip_entries(component_path(corpus_root, cases["epub-a11y-manual-required"], "a11y-manual.epub"))
        if b'<img src="image.svg"/>' not in auto_entries.get("EPUB/chapter.xhtml", b""):
            problems.append("epub-a11y-auto-finding does not omit alt as declared")
        if b'alt="Bild"' not in manual_entries.get("EPUB/chapter.xhtml", b""):
            problems.append("epub-a11y-manual-required lacks its weak alt marker")

        conflict_case = cases["metadata-conflict-title"]
        conflict_epub = zip_entries(component_path(corpus_root, conflict_case, "dateiname-titel.epub"))
        conflict_snapshot = read_json(component_path(corpus_root, conflict_case, "calibre-snapshot.json"))
        if b"Paket-Titel" not in conflict_epub.get("EPUB/package.opf", b""):
            problems.append("metadata-conflict-title lacks its package title")
        if conflict_snapshot.get("title") != "Calibre-Titel":
            problems.append("metadata-conflict-title lacks its Calibre snapshot title")

        roles = zip_entries(component_path(corpus_root, cases["metadata-contributor-roles"], "contributor-roles.epub")).get("EPUB/package.opf", b"")
        for role in (b">aut<", b">trl<", b">edt<"):
            if role not in roles:
                problems.append(f"metadata-contributor-roles lacks role marker {role!r}")

        sample_path = component_path(corpus_root, cases["edition-sample-vs-full"], "sample.epub")
        full_path = component_path(corpus_root, cases["edition-sample-vs-full"], "full.epub")
        sample_chapter = zip_entries(sample_path).get("EPUB/chapter.xhtml", b"")
        full_chapter = zip_entries(full_path).get("EPUB/chapter.xhtml", b"")
        if len(sample_chapter) >= len(full_chapter):
            problems.append("edition-sample-vs-full does not preserve the expected extent difference")

        equal_a = component_path(corpus_root, cases["identity-byte-equal"], "same.epub")
        equal_b = component_path(corpus_root, cases["identity-byte-equal"], "renamed.epub")
        if sha256_path(equal_a) != sha256_path(equal_b):
            problems.append("identity-byte-equal inputs are not byte-equal")

        package_a = component_path(corpus_root, cases["identity-repackaged"], "package-a.epub")
        package_b = component_path(corpus_root, cases["identity-repackaged"], "package-b.epub")
        if sha256_path(package_a) == sha256_path(package_b):
            problems.append("identity-repackaged inputs are unexpectedly byte-equal")
        if normalized_zip_digest(package_a) != normalized_zip_digest(package_b):
            problems.append("identity-repackaged logical ZIP entries differ")

        pdf = component_path(corpus_root, cases["identity-multiformat-edition"], "edition.pdf")
        epub = component_path(corpus_root, cases["identity-multiformat-edition"], "edition.epub")
        if not pdf.read_bytes().startswith(b"%PDF-") or not epub.read_bytes().startswith(b"PK"):
            problems.append("identity-multiformat-edition lacks distinct PDF/EPUB signatures")

        relationship_expectations = {
            "identity-byte-equal": {"file": "same", "representation": "candidate_same", "edition": "candidate_same", "work": "candidate_same"},
            "identity-repackaged": {"file": "different", "representation": "candidate_same", "edition": "candidate_same", "work": "candidate_same"},
            "identity-multiformat-edition": {"file": "different", "representation": "different", "edition": "candidate_same", "work": "candidate_same"},
            "identity-edition-vs-translation": {"file": "different", "representation": "different", "edition": "different", "work": "candidate_related"},
            "identity-title-collision": {"file": "different", "representation": "different", "edition": "different", "work": "different"},
        }
        for case_key, expected in relationship_expectations.items():
            if cases[case_key]["oracle"].get("expected_relationship") != expected:
                problems.append(f"{case_key} relationship oracle differs from TEST-0001")

        translation_en = zip_entries(component_path(corpus_root, cases["identity-edition-vs-translation"], "source-en.epub"))
        translation_de = zip_entries(component_path(corpus_root, cases["identity-edition-vs-translation"], "translation-de.epub"))
        translation_opf_en = translation_en.get("EPUB/package.opf", b"")
        translation_opf_de = translation_de.get("EPUB/package.opf", b"")
        if b"urn:test:work:glass-garden" not in translation_opf_en or b"urn:test:work:glass-garden" not in translation_opf_de:
            problems.append("identity-edition-vs-translation lacks its shared work reference")
        if b"<dc:language>en</dc:language>" not in translation_opf_en or b"<dc:language>de</dc:language>" not in translation_opf_de:
            problems.append("identity-edition-vs-translation lacks distinct languages")

        collision_a = zip_entries(component_path(corpus_root, cases["identity-title-collision"], "work-a.epub"))
        collision_b = zip_entries(component_path(corpus_root, cases["identity-title-collision"], "work-b.epub"))
        collision_opf_a = collision_a.get("EPUB/package.opf", b"")
        collision_opf_b = collision_b.get("EPUB/package.opf", b"")
        if b"Der letzte Schl" not in collision_opf_a or b"Der letzte Schl" not in collision_opf_b:
            problems.append("identity-title-collision inputs do not share the intended title")
        if b"Mara Nord" not in collision_opf_a or b"Jonas S" not in collision_opf_b:
            problems.append("identity-title-collision lacks distinct creators")

        unique = read_json(component_path(corpus_root, cases["routing-unique"], "item.json"))
        ambiguous = read_json(component_path(corpus_root, cases["routing-ambiguous"], "item.json"))
        targets = read_json(component_path(corpus_root, cases["routing-unique"], "targets.json"))
        target_records = targets.get("targets", [])
        if len(target_records) != 2:
            problems.append("routing target snapshot does not contain two libraries")
        for target in target_records:
            snapshot = target.get("read_only_snapshot", {})
            locator = snapshot.get("public_locator", "")
            if snapshot.get("interface") != "synthetic-contract-snapshot/v1":
                problems.append("routing target lacks the versioned snapshot interface")
            if not locator.startswith("target:") or PRIVATE_PATH_RE.search(locator):
                problems.append("routing target exposes an invalid or private locator")
            if not snapshot.get("books") or not snapshot.get("fields"):
                problems.append("routing target snapshot lacks fields or synthetic books")
        if unique.get("observations", {}).get("subjects") != ["technik"]:
            problems.append("routing-unique input is not uniquely classified")
        if set(ambiguous.get("observations", {}).get("subjects", [])) != {"technik", "jugend"}:
            problems.append("routing-ambiguous input does not cover both rules")
        if cases["routing-unique"]["oracle"].get("expected_routing", {}).get("result") != "candidate":
            problems.append("routing-unique oracle does not expect one candidate")
        if cases["routing-ambiguous"]["oracle"].get("expected_routing", {}).get("result") != "abstain":
            problems.append("routing-ambiguous oracle does not require abstention")

        run_one = component_path(corpus_root, cases["run-unchanged-skip"], "run-1.json")
        run_two = component_path(corpus_root, cases["run-unchanged-skip"], "run-2.json")
        if sha256_path(run_one) != sha256_path(run_two):
            problems.append("run-unchanged-skip snapshots are not identical")

        checkpoint = read_json(component_path(corpus_root, cases["run-resume"], "checkpoint.json"))
        resume = read_json(component_path(corpus_root, cases["run-resume"], "expected-resume.json"))
        if checkpoint.get("next_step") != resume.get("resume_from") or resume.get("repeat_steps") != []:
            problems.append("run-resume checkpoint and oracle are inconsistent")

        if execute_timeout:
            helper = component_path(corpus_root, cases["run-tool-timeout"], "slow_tool.py")
            timeout_seconds = cases["run-tool-timeout"]["oracle"]["resource_profile"]["timeout_ms"] / 1000
            tmp_root = ROOT / "tmp"
            tmp_root.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="test-0001-timeout-", dir=tmp_root) as raw_tmp:
                try:
                    subprocess.run(
                        [sys.executable, str(helper)],
                        cwd=raw_tmp,
                        check=False,
                        timeout=timeout_seconds,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env={},
                    )
                except subprocess.TimeoutExpired:
                    pass
                else:
                    problems.append("run-tool-timeout helper did not reach the declared timeout")
                if any(Path(raw_tmp).iterdir()):
                    problems.append("run-tool-timeout produced an undeclared output")
    except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        problems.append(f"case semantic validation could not complete: {exc}")
    return problems


def validate_reproducibility(corpus_root: Path) -> list[str]:
    generator = load_generator()
    problems: list[str] = []
    tmp_root = ROOT / "tmp"
    tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="test-0001-reproduce-", dir=tmp_root) as raw_tmp:
        regenerated = Path(raw_tmp) / "v0.2"
        generator.generate(regenerated)
        expected = tree_state(corpus_root)
        actual = tree_state(regenerated)
        if expected != actual:
            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            changed = sorted(
                path
                for path in set(expected).intersection(actual)
                if expected[path] != actual[path]
            )
            problems.append(
                "reproduced corpus differs "
                f"missing={missing} extra={extra} changed={changed}"
            )
    return problems


def validate(corpus_root: Path = CORPUS_ROOT, *, reproduce: bool = True) -> list[str]:
    problems: list[str] = []
    manifest_path = corpus_root / "manifest.json"
    if not manifest_path.is_file():
        return [f"manifest missing: {manifest_path}"]
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest unreadable: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest root must be an object"]

    before = tree_state(corpus_root)
    problems.extend(validate_manifest(corpus_root, manifest))
    problems.extend(validate_privacy(corpus_root))
    problems.extend(validate_case_semantics(corpus_root, manifest, execute_timeout=True))
    after = tree_state(corpus_root)
    if before != after:
        problems.append("read-only validation changed committed fixture inputs")
    if reproduce:
        problems.extend(validate_reproducibility(corpus_root))
    return problems


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--corpus", type=Path, default=CORPUS_ROOT)
    value.add_argument(
        "--no-reproduce",
        action="store_true",
        help="skip exact regeneration comparison",
    )
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    problems = validate(args.corpus.resolve(), reproduce=not args.no_reproduce)
    for problem in problems:
        print(f"[BLOCK] {problem}")
    if problems:
        return 2
    manifest = read_json(args.corpus / "manifest.json")
    components = sum(len(case["components"]) for case in manifest["cases"])
    print(
        f"[OK] TEST-0001 fixture corpus {manifest['fixture_version']} "
        f"cases={len(manifest['cases'])} components={components} "
        "reproducible=yes inputs_unchanged=yes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
