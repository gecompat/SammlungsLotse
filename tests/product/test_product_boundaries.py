from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "src" / "sammlungslotse"
BANNED_IMPORT_ROOTS = {
    "dbm",
    "ftplib",
    "html",
    "http",
    "requests",
    "shelve",
    "shutil",
    "smtplib",
    "socket",
    "sqlite3",
    "subprocess",
    "tempfile",
    "urllib",
    "xml",
}
BANNED_CALLS = {
    "extract",
    "extractall",
    "mkdir",
    "remove",
    "rename",
    "rmdir",
    "unlink",
    "write",
    "write_bytes",
    "write_text",
    "writelines",
}
ADAPTER_IMPORT_ALLOWLIST = {
    "deep_workspace.py": {"shutil"},
    "podman_executor.py": {"subprocess"},
}
ADAPTER_WRITE_ALLOWLIST = {"deep_workspace.py"}


class ProductBoundaryTests(unittest.TestCase):
    def test_product_code_has_no_network_persistence_or_parser_imports(
        self,
    ) -> None:
        violations: list[str] = []
        for path in sorted(PRODUCT_ROOT.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.partition(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = {node.module.partition(".")[0]}
                else:
                    continue
                blocked = (roots & BANNED_IMPORT_ROOTS) - ADAPTER_IMPORT_ALLOWLIST.get(
                    path.name, set()
                )
                if blocked:
                    violations.append(f"{path.name}:{node.lineno}:{sorted(blocked)}")
        self.assertEqual([], violations)

    def test_product_code_has_no_write_or_extraction_calls(self) -> None:
        violations: list[str] = []
        for path in sorted(PRODUCT_ROOT.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in BANNED_CALLS
                    and path.name not in ADAPTER_WRITE_ALLOWLIST
                ):
                    violations.append(f"{path.name}:{node.lineno}:{node.func.attr}")
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id == "open"
                    and path.name not in ADAPTER_WRITE_ALLOWLIST
                ):
                    mode = node.args[1] if len(node.args) > 1 else None
                    if isinstance(mode, ast.Constant) and any(
                        marker in mode.value for marker in "wax+"
                    ):
                        violations.append(
                            f"{path.name}:{node.lineno}:open({mode.value})"
                        )
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "open"
                    and path.name not in ADAPTER_WRITE_ALLOWLIST
                ):
                    mode_nodes = list(node.args[1:2])
                    mode_nodes.extend(
                        keyword.value
                        for keyword in node.keywords
                        if keyword.arg == "mode"
                    )
                    for mode in mode_nodes:
                        if isinstance(mode, ast.Constant) and any(
                            marker in mode.value for marker in "wax+"
                        ):
                            violations.append(
                                f"{path.name}:{node.lineno}:open({mode.value})"
                            )
        self.assertEqual([], violations)
