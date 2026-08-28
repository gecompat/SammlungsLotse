"""Provider-neutral ports for the Calibre inventory application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from .model import CalibreInventoryReport

if TYPE_CHECKING:
    from .workspace import LibraryWorkspace


@dataclass(frozen=True, slots=True)
class InventoryExecution:
    cleanup_complete: bool
    exit_code: int | None
    isolation_verified: bool
    process_started: bool
    raw_output: bytes | None
    state: str


class InventoryExecutor(Protocol):
    def execute(self, workspace: "LibraryWorkspace") -> InventoryExecution: ...


class CalibreInventoryPort(Protocol):
    def project(self) -> CalibreInventoryReport: ...
