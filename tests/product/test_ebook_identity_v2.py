from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sammlungslotse.ebook_identity import IdentityCandidateService  # noqa: E402
from sammlungslotse.ebook_identity.cli import render_json  # noqa: E402
from sammlungslotse.ebook_intake.snapshot import LocalFileSnapshotReader  # noqa: E402


EXP_RUNNER_PATH = ROOT / "tools" / "experiments" / "run_exp_0010.py"
SPEC = importlib.util.spec_from_file_location("run_exp_0010_v2_tests", EXP_RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("EXP-0010 runner cannot be loaded")
EXP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXP)

MANIFEST = EXP.validate_manifest(
    json.loads(
        (
            ROOT / "experiments" / "ebook" / "exp-0010" / "case-manifest.json"
        ).read_text(encoding="utf-8")
    )
)
CASES = {case["case_key"]: case for case in MANIFEST["cases"]}
EXP0011_CASES = {
    case["case_key"]: case
    for case in json.loads(
        (ROOT / "experiments" / "ebook" / "exp-0011" / "result.json").read_text(
            encoding="utf-8"
        )
    )["cases"]
}
CLI = ROOT / "tools" / "run_ebook_identity.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EbookIdentityV2Tests(unittest.TestCase):
    def materialize(self, case_key: str) -> tuple[Path, Path]:
        temporary = tempfile.TemporaryDirectory(prefix=f"wi-0013-{case_key}-")
        self.addCleanup(temporary.cleanup)
        return EXP.materialize_pair(
            MANIFEST,
            CASES[case_key],
            Path(temporary.name) / "pair",
        )

    def compare(self, case_key: str):
        left, right = self.materialize(case_key)
        return IdentityCandidateService().compare(
            LocalFileSnapshotReader(left), LocalFileSnapshotReader(right)
        )

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )

    def test_v1_default_and_explicit_projection_are_byte_identical(self) -> None:
        report = self.compare("shared-typed-additional-different-primary")

        self.assertEqual(render_json(report), render_json(report, "v1"))
        value = json.loads(render_json(report))
        self.assertEqual(
            "sammlungslotse/ebook-identity-candidate-report/v1", value["schema"]
        )
        self.assertEqual(
            {"creators", "identifiers", "languages", "titles", "work_references"},
            set(value["inputs"][0]["metadata"]),
        )

    def test_v2_matches_bound_exp0011_projection_and_keeps_five_stages(self) -> None:
        for case_key in (
            "shared-typed-additional-different-primary",
            "multiple-collections-partial-overlap",
            "invalid-missing-primary-binding",
            "invalid-missing-modified",
        ):
            with self.subTest(case=case_key):
                actual = self.compare(case_key).to_dict_v2()
                expected = EXP0011_CASES[case_key]["variants"]["V2"]["report"]
                expected = {**expected, "schema": actual["schema"]}

                self.assertEqual(expected, actual)
                self.assertEqual(
                    ["byte", "package", "representation", "edition", "work"],
                    [stage["stage"] for stage in actual["stages"]],
                )
                self.assertNotIn("publication", {item["stage"] for item in actual["stages"]})
                for item in actual["inputs"]:
                    self.assertNotIn("identifiers", item["metadata"])
                    self.assertNotIn("work_references", item["metadata"])

    def test_actual_v2_cli_is_opt_in_deterministic_path_free_and_read_only(self) -> None:
        left, right = self.materialize("multiple-collections-partial-overlap")
        before = (sha256(left), sha256(right))
        arguments = ("--json", "--report-version", "v2", str(left), str(right))

        first = self.run_cli(*arguments)
        second = self.run_cli(*arguments)

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        value = json.loads(first.stdout)
        self.assertEqual(
            "sammlungslotse/ebook-identity-candidate-report/v2", value["schema"]
        )
        self.assertEqual(2, len(value["inputs"][0]["metadata"]["collection_memberships"]))
        serialized = first.stdout + first.stderr + second.stdout + second.stderr
        for forbidden in (str(left), str(right), left.name, right.name, str(ROOT)):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(before, (sha256(left), sha256(right)))

    def test_report_version_requires_json_and_rejects_unknown_values(self) -> None:
        left, right = self.materialize("same-primary-minor-revision")

        without_json = self.run_cli(
            "--report-version", "v2", str(left), str(right)
        )
        unknown = self.run_cli(
            "--json", "--report-version", "v3", str(left), str(right)
        )

        for completed in (without_json, unknown):
            self.assertEqual(2, completed.returncode)
            self.assertEqual("", completed.stdout)
            self.assertEqual("Eingabeparameter sind ungültig.\n", completed.stderr)
            self.assertNotIn(str(left), completed.stderr)
            self.assertNotIn(str(right), completed.stderr)


if __name__ == "__main__":
    unittest.main()
