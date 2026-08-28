from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
TOOLS = ROOT / "tools"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load_tool(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MATERIALIZER = load_tool(
    "sammlungslotse_calibre_materializer",
    "materialize_calibre_qualification_library.py",
)
QUALIFIER = load_tool(
    "sammlungslotse_calibre_qualifier",
    "qualify_calibre_readonly_profile.py",
)

from sammlungslotse.calibre_inventory.profile import CalibreRuntimeProfile  # noqa: E402


class CalibreQualificationMaterializerTests(unittest.TestCase):
    def test_manifest_binds_three_targeted_records(self) -> None:
        manifest = MATERIALIZER.load_manifest()
        projection = MATERIALIZER.expected_projection(manifest)
        self.assertEqual([1, 2, 3], [item["external_record_id"] for item in projection])
        self.assertTrue(any(len(item["authors"]) > 1 for item in projection))
        self.assertTrue(any(len(item["languages"]) > 1 for item in projection))
        self.assertTrue(any(len(item["formats"]) > 1 for item in projection))
        self.assertTrue(any(not item["formats"] for item in projection))

    def test_target_must_be_new_strict_child(self) -> None:
        configured = Path(r"C:\rep\tmp\SammlungsLotse")
        if os.name == "nt":
            configured.mkdir(parents=True, exist_ok=True)
            context = tempfile.TemporaryDirectory(dir=configured)
        else:
            context = tempfile.TemporaryDirectory()
        with context as raw:
            allowed = Path(raw)
            target = allowed / "new-library"
            self.assertEqual(target.resolve(), MATERIALIZER.validate_new_target(target, allowed))
            target.mkdir()
            with self.assertRaises(MATERIALIZER.MaterializationError):
                MATERIALIZER.validate_new_target(target, allowed)
            with self.assertRaises(MATERIALIZER.MaterializationError):
                MATERIALIZER.validate_new_target(allowed.parent / "outside", allowed)

    def test_container_arguments_are_networkless_and_fixture_read_only(self) -> None:
        profile = CalibreRuntimeProfile.load(MATERIALIZER.PROFILE_PATH)
        fixture = ROOT / "tests" / "fixtures" / "ebook" / "test-0001" / "v0.3" / "cases" / "metadata-multilingual-rtl" / "multilingual-rtl.epub"
        arguments = MATERIALIZER._create_arguments(
            "sammlungslotse-wi0008-materialize-test",
            Path(r"C:\rep\tmp\SammlungsLotse\test-library"),
            profile,
            ["add", "--with-library", "/library", "/input/book.epub"],
            fixture,
        )
        joined = "\n".join(str(value) for value in arguments)
        self.assertIn("--network\nnone", joined)
        self.assertIn("--cap-drop\nall", joined)
        self.assertIn("target=/library,rw=true", joined)
        self.assertIn("target=/input/book.epub,ro=true", joined)
        self.assertIn(profile.image["id"], arguments)
        self.assertNotIn(profile.image["tag"], arguments)

    def test_qualification_preimage_binds_materializer_and_oracle(self) -> None:
        bound = QUALIFIER.preimage()
        self.assertIn("tools/materialize_calibre_qualification_library.py", bound)
        self.assertIn("tools/qualify_calibre_readonly_profile.py", bound)
        self.assertIn("runtime/calibre-readonly/qualification-library.json", bound)
        self.assertEqual(29, len(QUALIFIER.ACCEPTANCE_NAMES))

    def test_qualification_result_must_stay_outside_disposable_root(self) -> None:
        root = Path(r"C:\rep\tmp\SammlungsLotse\qualification")
        with self.assertRaises(QUALIFIER.materializer.MaterializationError):
            QUALIFIER.validate_result_outside_root(root / "result.json", root)
        outside = Path(r"C:\rep\artifacts\SammlungsLotse\qualification.json")
        self.assertEqual(outside.resolve(strict=False), QUALIFIER.validate_result_outside_root(outside, root))


if __name__ == "__main__":
    unittest.main()
