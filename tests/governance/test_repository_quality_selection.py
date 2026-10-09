from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.governance import select_repository_quality as selector


class RepositoryQualitySelectionTests(unittest.TestCase):
    def test_both_status_documents_need_only_repository_contracts(self) -> None:
        self.assertFalse(selector.runtime_required(sorted(selector.STATUS_ONLY_PATHS)))

    def test_product_or_test_change_requires_full_checks(self) -> None:
        for path in (
            "src/sammlungslotse/intake.py",
            "tests/product/test_intake.py",
            "tests/fixtures/ebook/test-0001/v0.3/manifest.json",
        ):
            with self.subTest(path=path):
                self.assertTrue(selector.runtime_required(["docs/project/HANDOVER.md", path]))

    def test_common_governance_or_unknown_input_requires_full_checks(self) -> None:
        for paths in (
            None,
            [],
            ["AGENTS.md"],
            [".ai/foundation/VALIDATION_POLICY.md"],
            ["tools/governance/validate_repository.py"],
            [".github/workflows/repository-quality.yml"],
            ["docs/governance/VALIDATION.md"],
            ["docs/decisions/DEC-0006-CI_VALIDATION_SCOPE.md"],
            ["docs/project/PROJECT_STATUS.md", "unknown/new-file"],
        ):
            with self.subTest(paths=paths):
                self.assertTrue(selector.runtime_required(paths))

    def test_missing_revision_or_diff_error_falls_back_to_full(self) -> None:
        self.assertIsNone(selector.changed_paths("0" * 40, "a" * 40))
        with mock.patch.object(selector.subprocess, "run", side_effect=OSError("git unavailable")):
            self.assertIsNone(selector.changed_paths("a" * 40, "b" * 40))

    def test_scope_is_based_on_exact_git_diff_including_deletions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            import subprocess

            def git(*args: str) -> str:
                return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()

            git("init", "-q")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            doc = root / "docs" / "project" / "HANDOVER.md"
            doc.parent.mkdir(parents=True)
            doc.write_text("first\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            doc.write_text("second\n", encoding="utf-8")
            git("commit", "-qam", "status")
            head = git("rev-parse", "HEAD")
            self.assertFalse(selector.runtime_required(selector.changed_paths(base, head, root)))
            doc.unlink()
            git("commit", "-qam", "delete")
            deleted_head = git("rev-parse", "HEAD")
            self.assertFalse(selector.runtime_required(selector.changed_paths(head, deleted_head, root)))


if __name__ == "__main__":
    unittest.main()
