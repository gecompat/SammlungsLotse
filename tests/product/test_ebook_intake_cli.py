from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools" / "run_ebook_intake.py"
CASES = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.2" / "cases"


def run_cli(
    relative: str, *, as_json: bool = False
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RUNNER)]
    if as_json:
        command.append("--json")
    command.append(str(CASES / relative))
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


class EbookIntakeCliTests(unittest.TestCase):
    def test_visible_human_projection_is_german_and_path_free(self) -> None:
        relative = "ingress-stable-minimal/stable.epub"
        result = run_cli(relative)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Formatfähigkeit: supported", result.stdout)
        self.assertIn("Nächste Aktion: continue_deep_read_only", result.stdout)
        self.assertIn("Wirkungen: Netzwerk=nein", result.stdout)
        self.assertNotIn(str(CASES / relative), result.stdout)
        self.assertNotIn("stable.epub", result.stdout)

    def test_actual_processes_cover_all_visible_gate_outcomes(self) -> None:
        matrix = {
            "ingress-stable-minimal/stable.epub": "continue_deep_read_only",
            "epub-active-or-remote/active-remote.epub": "review",
            "container-corrupt/corrupt.epub": "stop",
            "format-unknown/unknown.epub": "abstain",
        }

        for relative, expected in matrix.items():
            with self.subTest(relative=relative):
                result = run_cli(relative, as_json=True)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(expected, json.loads(result.stdout)["next_action"])

    def test_repeated_json_processes_are_byte_identical(self) -> None:
        relative = "ingress-stable-minimal/stable.epub"
        first = run_cli(relative, as_json=True)
        second = run_cli(relative, as_json=True)

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(0, second.returncode, second.stderr)
        self.assertEqual(first.stdout.encode("utf-8"), second.stdout.encode("utf-8"))

    def test_cli_does_not_modify_any_processed_input(self) -> None:
        relatives = [
            "ingress-stable-minimal/stable.epub",
            "epub-active-or-remote/active-remote.epub",
            "container-corrupt/corrupt.epub",
            "format-unknown/unknown.epub",
        ]
        paths = [CASES / relative for relative in relatives]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}

        for relative in relatives:
            result = run_cli(relative, as_json=True)
            self.assertEqual(0, result.returncode, result.stderr)

        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)

    def test_argument_error_does_not_echo_a_private_locator(self) -> None:
        private_locator = "C:/private-library/secret-title.epub"
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--unknown", private_locator],
            cwd=ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("Eingabeparameter sind ungültig.\n", result.stderr)
        self.assertNotIn(private_locator, result.stderr)
