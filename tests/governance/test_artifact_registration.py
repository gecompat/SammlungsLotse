from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "tools" / "governance" / "register_artifact.py"


def load_registration_module():
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_register_artifact", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load registration module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REGISTRATION = load_registration_module()


class ArtifactRegistrationTests(unittest.TestCase):
    def registry(self) -> dict:
        return {
            "artifacts": {},
            "prefixes": {"WI": {"kind": "work_item", "width": 4}},
            "profile": "foundation-artifact-registry/v2",
            "schema_version": 2,
        }

    def test_uuid7_is_supported_and_rfc_variant(self) -> None:
        value = REGISTRATION.uuid7()
        self.assertEqual(value.version, 7)
        self.assertEqual(value.variant, "specified in RFC 4122")

    def test_registration_writes_complete_next_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry_path = Path(directory) / "registry.json"
            registry_path.write_text(
                json.dumps(self.registry()), encoding="utf-8"
            )

            reference, record = REGISTRATION.register_artifact(
                registry_path=registry_path,
                prefix="WI",
                title="Synthetic work item",
                locator="docs/planning/synthetic.md",
            )

            self.assertEqual(reference, "WI-0001")
            self.assertEqual(record["kind"], "work_item")
            self.assertEqual(record["registration_state"], "REGISTERED")
            self.assertTrue(record["artifact_uid"].startswith("urn:uuid:"))
            saved = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["artifacts"]["WI-0001"], record)

    def test_reserved_reference_advances_sequence_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry_path = Path(directory) / "registry.json"
            registry_path.write_text(
                json.dumps(self.registry()), encoding="utf-8"
            )

            reference, _ = REGISTRATION.register_artifact(
                registry_path=registry_path,
                prefix="WI",
                title="Synthetic reserved work item",
                reserved_refs={"WI-0001"},
                write=False,
            )

            self.assertEqual(reference, "WI-0002")
            saved = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["artifacts"], {})


if __name__ == "__main__":
    unittest.main()
