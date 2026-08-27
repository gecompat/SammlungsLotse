"""Task-private V2 materialization and bounded crash recovery."""

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

from .deep_profile import DeepRuntimeProfile
from .model import Snapshot


MARKER_NAME = ".sammlungslotse-deep-task.json"


class TaskCleanupError(RuntimeError):
    """A partial task could not be removed safely after creation failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    safe_to_continue: bool
    observations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TaskWorkspace:
    task_id: str
    root: Path
    input_file: Path
    output_file: Path


class TaskWorkspaceManager:
    """Owns only marked direct children of one explicit dedicated temp root."""

    def __init__(self, temp_root: Path, profile: DeepRuntimeProfile) -> None:
        if any(marker in str(temp_root) for marker in (",", "\x00", "\r", "\n")):
            raise ValueError("temp root cannot be represented safely as a mount")
        self._root = Path(os.path.abspath(temp_root))
        self._profile = profile

    @property
    def root(self) -> Path:
        return self._root

    def prepare(self) -> None:
        created = False
        try:
            self._root.mkdir(parents=True, mode=0o700, exist_ok=False)
            created = True
        except FileExistsError:
            pass
        if self._root.is_symlink() or not self._root.is_dir():
            raise RuntimeError("deep temp root must be a real directory")
        if self._root.resolve(strict=True) != self._root:
            raise RuntimeError("deep temp root may not traverse a link")
        if created:
            try:
                self._root.chmod(0o700)
            except OSError:
                pass
        elif os.name != "nt" and stat.S_IMODE(self._root.stat().st_mode) & 0o077:
            raise RuntimeError("existing deep temp root is not private")

    def recover(self, *, now: float | None = None) -> RecoveryResult:
        self.prepare()
        children = list(self._root.iterdir())
        maximum = int(self._profile.workspace["max_children"])
        if len(children) > maximum:
            return RecoveryResult(False, ("recovery.child_limit_exceeded",))
        observations: list[str] = []
        safe = True
        current = time.time() if now is None else now
        maximum_age = int(self._profile.workspace["max_task_age_seconds"])
        for child in sorted(children, key=lambda item: item.name):
            if child.is_symlink() or not child.is_dir() or not child.name.startswith(
                "task-"
            ):
                observations.append("recovery.unknown_entry")
                safe = False
                continue
            marker = self._read_marker(child)
            if marker is None or marker.get("task_id") != child.name.removeprefix(
                "task-"
            ):
                observations.append("recovery.unowned_task")
                safe = False
                continue
            created = marker.get("created_epoch")
            if not isinstance(created, (int, float)) or created > current:
                observations.append("recovery.invalid_marker")
                safe = False
                continue
            if current - float(created) < maximum_age:
                observations.append("recovery.recent_task_preserved")
                continue
            if not self._owned_tree_is_bounded(child):
                observations.append("recovery.task_requires_review")
                safe = False
                continue
            self._remove_owned_task(child, marker)
            observations.append("recovery.expired_task_removed")
        return RecoveryResult(safe, tuple(observations))

    def create(self, snapshot: Snapshot) -> TaskWorkspace:
        self.prepare()
        task_id = uuid.uuid4().hex
        task = self._root / f"task-{task_id}"
        task.mkdir(mode=0o700)
        marker = {
            "created_epoch": time.time(),
            "profile_id": self._profile.profile_id,
            "schema": self._profile.workspace["marker_schema"],
            "snapshot_sha256": snapshot.sha256,
            "task_id": task_id,
        }
        try:
            marker_path = task / MARKER_NAME
            marker_path.write_bytes(
                json.dumps(marker, separators=(",", ":"), sort_keys=True).encode(
                    "utf-8"
                )
            )
            try:
                marker_path.chmod(0o600)
            except OSError:
                pass
            input_dir = task / "input"
            output_dir = task / "output"
            input_dir.mkdir(mode=0o700)
            output_dir.mkdir(mode=0o700)
            input_file = input_dir / f"{uuid.uuid4().hex}.epub"
            with input_file.open("xb") as stream:
                stream.write(snapshot.data)
                stream.flush()
                os.fsync(stream.fileno())
            if input_file.stat().st_size != snapshot.size_bytes:
                raise RuntimeError("materialized snapshot size differs")
            if sha256_file(input_file) != snapshot.sha256:
                raise RuntimeError("materialized snapshot digest differs")
            try:
                input_file.chmod(0o400)
            except OSError:
                pass
            return TaskWorkspace(
                task_id=task_id,
                root=task,
                input_file=input_file,
                output_file=output_dir / "report.json",
            )
        except (OSError, RuntimeError, ValueError):
            try:
                if self._owned_tree_is_bounded(task):
                    self._remove_owned_task(task, marker)
                else:
                    raise RuntimeError("partial task is outside its cleanup bound")
            except (OSError, RuntimeError, ValueError) as cleanup_error:
                raise TaskCleanupError(
                    "partial task cleanup failed"
                ) from cleanup_error
            raise

    def cleanup(self, workspace: TaskWorkspace) -> None:
        marker = self._read_marker(workspace.root)
        if marker is None or marker.get("task_id") != workspace.task_id:
            raise RuntimeError("task ownership marker differs")
        if not self._owned_tree_is_bounded(workspace.root):
            raise RuntimeError("task tree is unsafe or exceeds its bound")
        self._remove_owned_task(workspace.root, marker)

    def _read_marker(self, task: Path) -> dict[str, object] | None:
        marker = task / MARKER_NAME
        try:
            if marker.is_symlink() or not marker.is_file():
                return None
            if marker.stat().st_size > 4096:
                return None
            value = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return None
        if not isinstance(value, dict):
            return None
        if value.get("schema") != self._profile.workspace["marker_schema"]:
            return None
        if value.get("profile_id") != self._profile.profile_id:
            return None
        return value

    def _owned_tree_is_bounded(self, task: Path) -> bool:
        maximum = int(self._profile.workspace["max_task_bytes"])
        total = 0
        pending = [task]
        while pending:
            current = pending.pop()
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        if entry.is_symlink():
                            return False
                        if entry.is_dir(follow_symlinks=False):
                            pending.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                            if total > maximum:
                                return False
                        else:
                            return False
            except OSError:
                return False
        return True

    def _remove_owned_task(self, task: Path, marker: dict[str, object]) -> None:
        if task.parent != self._root or task.name != f"task-{marker['task_id']}":
            raise RuntimeError("refusing to remove a task outside the dedicated root")

        def make_writable(function, path, exc_info) -> None:
            del exc_info
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            function(path)

        shutil.rmtree(task, onerror=make_writable)
