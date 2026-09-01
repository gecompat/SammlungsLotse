from __future__ import annotations

import importlib.util
import io
import json
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "qualify_ebook_intake_context.py"
SPEC = importlib.util.spec_from_file_location("qualify_ebook_intake_context", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
qualification = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qualification)


class EbookIntakeContextQualificationTests(unittest.TestCase):
    def test_profile_binds_baseline_cases_taxonomy_and_schemas(self) -> None:
        profile = qualification.validate_profile(
            json.loads(qualification.PROFILE_PATH.read_text(encoding="utf-8"))
        )

        self.assertEqual("WI-0014", profile["artifact"])
        self.assertEqual(48, profile["case_sources"]["classifier"]["count"])
        self.assertEqual(12, profile["case_sources"]["public_cli"]["count"])
        self.assertEqual(6, len(profile["public_contract"]["context_classes"]))
        self.assertEqual(2, profile["repetitions"])

    def test_materializer_is_deterministic_bounded_and_minimal_epub(self) -> None:
        snippet = '<html><body><a href="https://example.invalid/x">x</a></body></html>'
        first = qualification.materialize_epub("xhtml", snippet)
        second = qualification.materialize_epub("xhtml", snippet)

        self.assertEqual(first, second)
        self.assertLess(len(first), 16 * 1024)
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            self.assertEqual(
                ["mimetype", "OEBPS/case.xhtml"], archive.namelist()
            )
            self.assertEqual(b"application/epub+zip", archive.read("mimetype"))
            self.assertEqual(snippet.encode("utf-8"), archive.read("OEBPS/case.xhtml"))

    def test_classifier_matrix_recomputes_all_oracles_without_mismatch(self) -> None:
        cases = qualification._load_cases(qualification.EXP0016_CASES, "EXP-0016", 48)
        result = qualification._classify_matrix(cases)

        self.assertEqual(48, result["case_count"])
        self.assertEqual(96, result["parser_runs"])
        self.assertEqual(0, result["mismatches"])
        self.assertTrue(result["repetitions_identical"])
        self.assertEqual(
            set(qualification.CONTEXT_CLASSES),
            set(result["class_counts_per_repetition"]),
        )

    def test_execution_requires_explicit_green_preimage_confirmation(self) -> None:
        with self.assertRaisesRegex(
            qualification.QualificationError, "green preimage CI confirmation"
        ):
            qualification.execute(
                temp_root=Path(r"C:\rep\tmp\SammlungsLotse\must-not-exist"),
                result_path=Path(
                    r"C:\rep\artifacts\SammlungsLotse\must-not-exist.json"
                ),
                confirm_green_preimage_ci=False,
            )

    def test_privacy_guard_rejects_raw_values_and_accepts_coarse_output(self) -> None:
        inputs = (Path(r"C:\rep\tmp\SammlungsLotse\task\input-00.epub"),)
        safe = b'{"classes":["content.user_activated_hyperlink"]}'
        raw_url = b'{"value":"https://example.invalid/private"}'
        raw_path = str(inputs[0]).encode("utf-8")

        self.assertFalse(qualification._contains_private_or_raw_value(safe, inputs))
        self.assertTrue(
            qualification._contains_private_or_raw_value(raw_url, inputs)
        )
        self.assertTrue(
            qualification._contains_private_or_raw_value(raw_path, inputs)
        )

    def test_preimage_binding_covers_complete_intake_runtime(self) -> None:
        locators = set(qualification._bound_locators())

        self.assertIn("src/sammlungslotse/ebook_intake/context.py", locators)
        self.assertIn("src/sammlungslotse/ebook_intake/cli.py", locators)
        self.assertIn("tools/qualify_ebook_intake_context.py", locators)
        self.assertIn("tests/product/test_ebook_intake_v2.py", locators)

    def test_result_validator_rejects_claims_with_changed_metrics(self) -> None:
        result = {
            field: None for field in qualification.RESULT_FIELDS
        }
        result.update(
            {
                "acceptance": {
                    key: True for key in qualification.ACCEPTANCE_KEYS
                },
                "artifact": "WI-0014",
                "classifier": {
                    **qualification.EXPECTED_CLASSIFIER,
                    "mismatches": 1,
                },
                "cleanup_complete": True,
                "effects": qualification.EXPECTED_EFFECTS,
                "profile": qualification.PROFILE_ID,
                "public_cli": qualification.EXPECTED_PUBLIC_CLI,
                "schema": qualification.SCHEMA,
                "status": "pass",
                "surfaces": qualification.EXPECTED_SURFACES,
            }
        )

        with self.assertRaisesRegex(
            qualification.QualificationError, "classifier metrics"
        ):
            qualification.validate_result_dict(result)


if __name__ == "__main__":
    unittest.main()
