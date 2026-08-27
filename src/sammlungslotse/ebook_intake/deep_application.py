"""Application gate for one explicit deep read-only tool call."""

from __future__ import annotations

from .deep_model import DeepToolResult
from .deep_ports import DeepReadOnlyToolPort
from .model import TriageReport


class DeepReadOnlyService:
    """Starts a tool only for the already approved immutable snapshot."""

    def inspect(
        self, triage: TriageReport, tool: DeepReadOnlyToolPort
    ) -> DeepToolResult:
        if not triage.deep_read_only_allowed or triage.snapshot is None:
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="gate.not_open",
                snapshot_sha256=(
                    triage.snapshot.sha256 if triage.snapshot is not None else None
                ),
            )
        return tool.inspect(triage.snapshot)
