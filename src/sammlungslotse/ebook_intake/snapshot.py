"""Read-only local-file snapshot adapter."""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

from .model import Snapshot, TriageLimits
from .ports import SnapshotIssue


FILE_ATTRIBUTE_REPARSE_POINT = 0x400


def _identity(value: object) -> tuple[int, int, int, int]:
    return (
        int(getattr(value, "st_dev")),
        int(getattr(value, "st_ino")),
        int(getattr(value, "st_size")),
        int(getattr(value, "st_mtime_ns")),
    )


class LocalFileSnapshotReader:
    """Captures one regular file into bounded immutable memory."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def capture(self, limits: TriageLimits) -> Snapshot:
        try:
            initial = self._path.lstat()
        except OSError as exc:
            raise SnapshotIssue(
                observation_code="input.unavailable",
                finding_code="input.unavailable",
                next_action="stop",
            ) from exc

        if stat.S_ISLNK(initial.st_mode):
            raise SnapshotIssue(
                observation_code="input.symlink",
                finding_code="input.symlink_not_allowed",
                next_action="stop",
            )
        if (
            int(getattr(initial, "st_file_attributes", 0))
            & FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise SnapshotIssue(
                observation_code="input.reparse_point",
                finding_code="input.reparse_not_allowed",
                next_action="stop",
            )
        if not stat.S_ISREG(initial.st_mode):
            raise SnapshotIssue(
                observation_code="input.not_regular_file",
                finding_code="input.not_regular_file",
                next_action="stop",
            )
        if initial.st_size > limits.max_input_bytes:
            raise SnapshotIssue(
                observation_code="input.size_limit_exceeded",
                finding_code="resource.input_limit_exceeded",
                next_action="stop",
                values=(("limit_bytes", limits.max_input_bytes),),
            )

        try:
            with self._path.open("rb") as stream:
                descriptor_before = _identity(os.fstat(stream.fileno()))
                data = stream.read(limits.max_input_bytes + 1)
                descriptor_after = _identity(os.fstat(stream.fileno()))
            path_after = self._path.lstat()
        except OSError as exc:
            raise SnapshotIssue(
                observation_code="input.read_error",
                finding_code="input.unavailable",
                next_action="stop",
            ) from exc

        if len(data) > limits.max_input_bytes:
            raise SnapshotIssue(
                observation_code="input.size_limit_exceeded",
                finding_code="resource.input_limit_exceeded",
                next_action="stop",
                values=(("limit_bytes", limits.max_input_bytes),),
            )

        initial_identity = _identity(initial)
        final_identity = _identity(path_after)
        if (
            descriptor_before != descriptor_after
            or initial_identity != descriptor_before
            or descriptor_after != final_identity
            or len(data) != descriptor_after[2]
        ):
            raise SnapshotIssue(
                observation_code="snapshot.changed",
                finding_code="ingress.unstable",
                next_action="defer",
            )

        return Snapshot(
            data=bytes(data),
            size_bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            suffix=self._path.suffix.casefold(),
        )
