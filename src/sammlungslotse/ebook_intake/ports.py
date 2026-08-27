"""Ports used by the WI-0004 application service."""

from __future__ import annotations

from typing import Protocol

from .model import Scalar, Snapshot, TriageLimits


class SnapshotIssue(RuntimeError):
    """A bounded, path-free input rejection that produces a normal report."""

    def __init__(
        self,
        *,
        observation_code: str,
        finding_code: str,
        next_action: str,
        values: tuple[tuple[str, Scalar], ...] = (),
    ) -> None:
        super().__init__(finding_code)
        self.observation_code = observation_code
        self.finding_code = finding_code
        self.next_action = next_action
        self.values = values


class SnapshotReader(Protocol):
    """Captures exactly one immutable input without exposing its locator."""

    def capture(self, limits: TriageLimits) -> Snapshot: ...
