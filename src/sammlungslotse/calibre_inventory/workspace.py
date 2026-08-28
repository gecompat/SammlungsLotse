"""Bounded source snapshot and task-private Calibre working copy."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .profile import CalibreRuntimeProfile


MARKER_NAME = ".sammlungslotse-calibre-task.json"


@dataclass(frozen=True, slots=True)
class FileRecord:
    relative_path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class LibrarySnapshot:
    digest: str
    files: tuple[FileRecord, ...]
    total_bytes: int


@dataclass(frozen=True, slots=True)
class LibraryWorkspace:
    task_id: str
    root: Path
    library: Path
    output: Path
    source_snapshot: LibrarySnapshot


def _is_reparse(info: os.stat_result) -> bool:
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(info, "st_file_attributes", 0) & flag)


def _file_digest(path: Path, maximum: int) -> tuple[int, str]:
    before = path.stat(follow_symlinks=False)
    if before.st_size > maximum:
        raise ValueError("library.file_limit_exceeded")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            if size > maximum:
                raise ValueError("library.file_limit_exceeded")
            digest.update(chunk)
    after = path.stat(follow_symlinks=False)
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or size != after.st_size:
        raise RuntimeError("library.source_unstable")
    return size, digest.hexdigest()


def snapshot_library(source: Path, profile: CalibreRuntimeProfile) -> LibrarySnapshot:
    source = Path(os.path.abspath(source))
    if source.is_symlink() or not source.is_dir() or source.resolve(strict=True) != source:
        raise ValueError("library.invalid_root")
    limits = profile.workspace
    pending: list[tuple[Path, int]] = [(source, 0)]
    records: list[FileRecord] = []
    total = 0
    while pending:
        current, depth = pending.pop()
        if depth > int(limits["max_depth"]):
            raise ValueError("library.depth_limit_exceeded")
        with os.scandir(current) as entries:
            ordered = sorted(entries, key=lambda item: item.name)
        for entry in ordered:
            info = entry.stat(follow_symlinks=False)
            if entry.is_symlink() or _is_reparse(info):
                raise ValueError("library.link_not_allowed")
            path = Path(entry.path)
            relative = path.relative_to(source).as_posix()
            if len(relative.encode("utf-8")) > int(limits["max_relative_path_bytes"]):
                raise ValueError("library.path_limit_exceeded")
            if entry.is_dir(follow_symlinks=False):
                pending.append((path, depth + 1))
            elif entry.is_file(follow_symlinks=False):
                size, digest = _file_digest(path, int(limits["max_file_bytes"]))
                total += size
                if len(records) + 1 > int(limits["max_files"]):
                    raise ValueError("library.file_count_exceeded")
                if total > int(limits["max_total_bytes"]):
                    raise ValueError("library.total_limit_exceeded")
                records.append(FileRecord(relative, size, digest))
            else:
                raise ValueError("library.special_file_not_allowed")
    records.sort(key=lambda item: item.relative_path)
    if not any(item.relative_path == "metadata.db" for item in records):
        raise ValueError("library.metadata_missing")
    canonical = json.dumps(
        [[item.relative_path, item.size_bytes, item.sha256] for item in records],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return LibrarySnapshot(hashlib.sha256(canonical).hexdigest(), tuple(records), total)


class LibraryWorkspaceManager:
    """Owns only marked task directories below one explicit root."""

    def __init__(self, source: Path, temp_root: Path, profile: CalibreRuntimeProfile) -> None:
        if any(value in str(temp_root) for value in (",", "\x00", "\r", "\n")):
            raise ValueError("configuration.invalid_temp_root")
        self.source = Path(os.path.abspath(source))
        self.root = Path(os.path.abspath(temp_root))
        self.profile = profile

    def prepare_root(self) -> None:
        self.root.mkdir(parents=True, mode=0o700, exist_ok=True)
        if self.root.is_symlink() or not self.root.is_dir() or self.root.resolve(strict=True) != self.root:
            raise RuntimeError("workspace.invalid_root")

    def recover(self, now: float | None = None) -> bool:
        self.prepare_root()
        children = list(self.root.iterdir())
        if len(children) > int(self.profile.workspace["max_children"]):
            return False
        current = time.time() if now is None else now
        for child in children:
            marker = self._marker(child)
            if marker is None:
                return False
            created = marker.get("created_epoch")
            if not isinstance(created, (int, float)) or created > current:
                return False
            if current - float(created) >= int(self.profile.workspace["max_task_age_seconds"]):
                self._remove(child, str(marker["task_id"]))
        return True

    def create(self) -> LibraryWorkspace:
        self.prepare_root()
        before = snapshot_library(self.source, self.profile)
        task_id = uuid.uuid4().hex
        task = self.root / f"task-{task_id}"
        task.mkdir(mode=0o700)
        marker = {
            "created_epoch": time.time(),
            "profile_id": self.profile.profile_id,
            "schema": self.profile.workspace["marker_schema"],
            "task_id": task_id,
        }
        try:
            (task / MARKER_NAME).write_text(
                json.dumps(marker, separators=(",", ":"), sort_keys=True), encoding="utf-8"
            )
            library = task / "library"
            output = task / "output"
            library.mkdir()
            output.mkdir()
            for record in before.files:
                source_file = self.source / Path(record.relative_path)
                target = library / Path(record.relative_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                with source_file.open("rb") as incoming, target.open("xb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing, 1024 * 1024)
            if snapshot_library(self.source, self.profile) != before:
                raise RuntimeError("library.source_changed_during_copy")
            if snapshot_library(library, self.profile) != before:
                raise RuntimeError("library.copy_mismatch")
            return LibraryWorkspace(task_id, task, library, output, before)
        except BaseException:
            if task.exists():
                self._remove(task, task_id)
            raise

    def source_unchanged(self, workspace: LibraryWorkspace) -> bool:
        return snapshot_library(self.source, self.profile) == workspace.source_snapshot

    def cleanup(self, workspace: LibraryWorkspace) -> None:
        marker = self._marker(workspace.root)
        if marker is None or marker.get("task_id") != workspace.task_id:
            raise RuntimeError("workspace.ownership_mismatch")
        self._remove(workspace.root, workspace.task_id)

    def _marker(self, task: Path) -> dict[str, object] | None:
        if task.parent != self.root or task.is_symlink() or not task.is_dir() or not task.name.startswith("task-"):
            return None
        path = task / MARKER_NAME
        try:
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
                return None
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return None
        if not isinstance(value, dict):
            return None
        if value.get("schema") != self.profile.workspace["marker_schema"] or value.get("profile_id") != self.profile.profile_id:
            return None
        if task.name != f"task-{value.get('task_id')}":
            return None
        return value

    def _remove(self, task: Path, task_id: str) -> None:
        if task.parent != self.root or task.name != f"task-{task_id}":
            raise RuntimeError("workspace.cleanup_outside_root")
        if not self._tree_is_bounded(task):
            raise RuntimeError("workspace.cleanup_tree_unsafe")

        def writable(function, path, exc_info) -> None:
            del exc_info
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            function(path)

        shutil.rmtree(task, onerror=writable)

    def _tree_is_bounded(self, task: Path) -> bool:
        maximum_bytes = int(self.profile.workspace["max_total_bytes"]) + int(
            self.profile.execution["raw_report_max_bytes"]
        ) + 1024 * 1024
        maximum_files = int(self.profile.workspace["max_files"]) + 16
        count = 0
        total = 0
        pending = [task]
        while pending:
            current = pending.pop()
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        info = entry.stat(follow_symlinks=False)
                        if entry.is_symlink() or _is_reparse(info):
                            return False
                        if entry.is_dir(follow_symlinks=False):
                            pending.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            count += 1
                            total += info.st_size
                            if count > maximum_files or total > maximum_bytes:
                                return False
                        else:
                            return False
            except OSError:
                return False
        return True
