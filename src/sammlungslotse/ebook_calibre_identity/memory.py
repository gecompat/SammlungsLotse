"""Immutable in-memory SnapshotReader used after bounded provider capture."""

from __future__ import annotations

import hashlib

from sammlungslotse.ebook_intake.model import Snapshot, TriageLimits
from sammlungslotse.ebook_intake.ports import SnapshotIssue


class ImmutableSnapshotReader:
    def __init__(self, snapshot: Snapshot) -> None:
        if snapshot.size_bytes != len(snapshot.data):
            raise ValueError("snapshot size differs")
        if snapshot.sha256 != hashlib.sha256(snapshot.data).hexdigest():
            raise ValueError("snapshot digest differs")
        if snapshot.suffix != ".epub":
            raise ValueError("snapshot suffix differs")
        self._snapshot = snapshot

    def capture(self, limits: TriageLimits) -> Snapshot:
        if self._snapshot.size_bytes > limits.max_input_bytes:
            raise SnapshotIssue(
                observation_code="input.size_limit_exceeded",
                finding_code="resource.input_limit_exceeded",
                next_action="stop",
                values=(("limit_bytes", limits.max_input_bytes),),
            )
        return self._snapshot
