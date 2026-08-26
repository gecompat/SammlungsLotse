from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = (
    ROOT
    / ".ai"
    / "foundation"
    / "artifact_registry_github"
    / "registry_semantic.py"
)


def load_registry_module():
    spec = importlib.util.spec_from_file_location(
        "sammlungslotse_registry_semantic_tests", TOOL_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load registry semantic module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REGISTRY = load_registry_module()


class RegistrySemanticTests(unittest.TestCase):
    def registry(self) -> dict:
        return {
            "artifacts": {},
            "prefixes": {"WI": {"kind": "work_item", "width": 4}},
            "profile": "foundation-artifact-registry/v2",
            "schema_version": 2,
        }

    def record(self, uid: str, title: str) -> dict:
        return {
            "aliases": [],
            "artifact_uid": uid,
            "external_refs": [],
            "kind": "work_item",
            "registration_state": "REGISTERED",
            "relations": [],
            "title": title,
        }

    def test_independent_additions_merge_by_json_object(self) -> None:
        base = self.registry()
        main = copy.deepcopy(base)
        head = copy.deepcopy(base)
        main["artifacts"]["WI-0001"] = self.record(
            "urn:uuid:01900000-0000-7000-8000-000000000001",
            "Main work item",
        )
        head["artifacts"]["WI-0002"] = self.record(
            "urn:uuid:01900000-0000-7000-8000-000000000002",
            "Head work item",
        )

        merged, conflicts = REGISTRY.semantic_merge(base, main, head)

        self.assertEqual(conflicts, [])
        self.assertEqual(
            set(merged["artifacts"]),
            {"WI-0001", "WI-0002"},
        )

    def test_concurrent_same_reference_is_blocked(self) -> None:
        base = self.registry()
        main = copy.deepcopy(base)
        head = copy.deepcopy(base)
        main["artifacts"]["WI-0001"] = self.record(
            "urn:uuid:01900000-0000-7000-8000-000000000001",
            "Main work item",
        )
        head["artifacts"]["WI-0001"] = self.record(
            "urn:uuid:01900000-0000-7000-8000-000000000002",
            "Head work item",
        )

        _, conflicts = REGISTRY.semantic_merge(base, main, head)

        self.assertTrue(
            any("CONCURRENT_ADD artifacts.WI-0001" in value for value in conflicts)
        )


if __name__ == "__main__":
    unittest.main()
