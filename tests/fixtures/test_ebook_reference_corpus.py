from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = (
    ROOT / "tools" / "fixtures" / "validate_ebook_reference_corpus.py"
)
CORPUS_ROOT = (
    ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.1"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_test_0001_validator", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EbookReferenceCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()
        cls.manifest = json.loads(
            (CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8")
        )

    def test_core_contract_is_complete_and_semantically_valid(self) -> None:
        self.assertEqual(
            [],
            self.validator.validate(CORPUS_ROOT, reproduce=False),
        )

    def test_regeneration_is_byte_exact(self) -> None:
        self.assertEqual(
            [],
            self.validator.validate_reproducibility(CORPUS_ROOT),
        )

    def test_validation_preserves_fixture_tree(self) -> None:
        before = self.validator.tree_state(CORPUS_ROOT)
        problems = self.validator.validate_case_semantics(
            CORPUS_ROOT,
            self.manifest,
            execute_timeout=True,
        )
        after = self.validator.tree_state(CORPUS_ROOT)
        self.assertEqual([], problems)
        self.assertEqual(before, after)

    def test_only_contractual_core_cases_are_materialized(self) -> None:
        generator = self.validator.load_generator()
        actual = tuple(case["case_key"] for case in self.manifest["cases"])
        self.assertEqual(tuple(generator.CORE_CASE_KEYS), actual)
        self.assertEqual(
            list(generator.DEFERRED_EXPANSION_CASE_KEYS),
            self.manifest["deferred_expansion_case_keys"],
        )
        self.assertTrue(
            set(actual).isdisjoint(self.manifest["deferred_expansion_case_keys"])
        )

    def test_generator_digest_is_portable_across_lf_and_crlf(self) -> None:
        generator = self.validator.load_generator()
        source = (
            ROOT / "tools" / "fixtures" / "generate_ebook_reference_corpus.py"
        )
        logical = source.read_bytes().replace(b"\r\n", b"\n")
        tmp_root = ROOT / "tmp"
        tmp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="test-0001-eol-", dir=tmp_root
        ) as raw_tmp:
            crlf_path = Path(raw_tmp) / "generator-crlf.py"
            crlf_path.write_bytes(logical.replace(b"\n", b"\r\n"))
            self.assertEqual(
                generator.sha256_portable_text(source),
                generator.sha256_portable_text(crlf_path),
            )


if __name__ == "__main__":
    unittest.main()
