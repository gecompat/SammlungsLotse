"""Provider-neutral application port for deep read-only evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from .deep_model import DeepToolResult
from .model import Snapshot

if TYPE_CHECKING:
    from .deep_workspace import TaskWorkspace


@dataclass(frozen=True, slots=True)
class ProcessExecution:
    """Provider-neutral outcome of one bounded external process."""

    cleanup_complete: bool
    exit_code: int | None
    isolation_verified: bool
    observations: tuple[str, ...]
    process_started: bool
    report: bytes | None
    state: str


class ProcessExecutor(Protocol):
    """Runs one configured task without exposing executor details to the core."""

    def execute(self, workspace: TaskWorkspace) -> ProcessExecution: ...


class DeepReadOnlyToolPort(Protocol):
    """Consumes snapshot bytes without exposing the original locator."""

    def inspect(self, snapshot: Snapshot) -> DeepToolResult: ...
