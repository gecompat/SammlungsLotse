"""Provider-neutral ports for the WI-0011 application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from .model import RecordSnapshotHandoff

if TYPE_CHECKING:
    from sammlungslotse.calibre_inventory.workspace import LibraryWorkspace


@dataclass(frozen=True, slots=True)
class RecordExecution:
    cleanup_complete: bool
    data: bytes | None
    exit_code: int | None
    isolation_verified: bool
    output_sha256: str | None
    output_size_bytes: int | None
    process_started: bool
    state: str


class RecordExecutor(Protocol):
    def execute(self, workspace: "LibraryWorkspace", external_record_id: int) -> RecordExecution: ...


class RecordSnapshotPort(Protocol):
    @property
    def external_record_id(self) -> int: ...

    @property
    def profile_id(self) -> str: ...

    def capture(self, maximum_bytes: int) -> RecordSnapshotHandoff: ...
