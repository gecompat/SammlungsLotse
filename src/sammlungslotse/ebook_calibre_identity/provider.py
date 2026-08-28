"""Calibre adapter behind the provider-neutral WI-0011 record snapshot port."""

from __future__ import annotations

import hashlib
from pathlib import Path

from sammlungslotse.calibre_inventory.workspace import LibraryWorkspaceManager
from sammlungslotse.ebook_intake.model import Snapshot

from .executor import CalibreRecordPodmanExecutor
from .model import RecordHandoffEffects, RecordSnapshotHandoff
from .ports import RecordExecutor
from .profile import CalibreIdentityProfile


REASONS = {
    "unavailable": "executor.unavailable_or_changed",
    "failed": "executor.failed",
    "timeout": "executor.timeout",
    "invalid_report": "provider.output_contract_invalid",
    "selection_unavailable": "provider.selection_unavailable",
    "cleanup_failed": "executor.cleanup_failed",
}


class CalibreRecordSnapshotProvider:
    def __init__(
        self,
        *,
        source: Path,
        temp_root: Path,
        external_record_id: str,
        profile: CalibreIdentityProfile,
        executor: RecordExecutor | None = None,
    ) -> None:
        self.source = source
        self._external_record_id = profile.validate_external_record_id(external_record_id)
        self.profile = profile
        self.workspace = LibraryWorkspaceManager(source, temp_root, profile.runtime)
        self.executor = executor or CalibreRecordPodmanExecutor(profile)

    @property
    def external_record_id(self) -> int:
        return self._external_record_id

    @property
    def profile_id(self) -> str:
        return self.profile.profile_id

    def capture(self, maximum_bytes: int) -> RecordSnapshotHandoff:
        if maximum_bytes != self.profile.limits["max_input_bytes"]:
            return self._failed("failed", "configuration.input_limit_differs")
        workspace = None
        execution = None
        state = "failed"
        reasons = ("provider.failed",)
        snapshot: Snapshot | None = None
        library_snapshot: str | None = None
        source_modified = False
        interrupted: KeyboardInterrupt | None = None
        try:
            if not self.workspace.recover():
                reasons = ("workspace.recovery_requires_review",)
            else:
                workspace = self.workspace.create()
                library_snapshot = workspace.source_snapshot.digest
                execution = self.executor.execute(workspace, self.external_record_id)
                if not self.workspace.source_unchanged(workspace):
                    state = "source_changed"
                    reasons = ("library.source_changed",)
                    source_modified = True
                elif (
                    execution.state == "completed"
                    and execution.cleanup_complete
                    and execution.isolation_verified
                    and execution.exit_code == 0
                    and execution.data is not None
                    and execution.output_size_bytes == len(execution.data)
                    and execution.output_sha256 == hashlib.sha256(execution.data).hexdigest()
                    and 0 < len(execution.data) <= maximum_bytes
                ):
                    state = "completed"
                    reasons = ()
                    snapshot = Snapshot(
                        data=bytes(execution.data),
                        size_bytes=len(execution.data),
                        sha256=execution.output_sha256,
                        suffix=".epub",
                    )
                else:
                    state = execution.state if execution.state in REASONS else "failed"
                    reasons = (REASONS.get(state, "executor.failed"),)
        except KeyboardInterrupt as exc:
            interrupted = exc
            state = "failed"
            reasons = ("provider.interrupted",)
        except (OSError, RuntimeError, ValueError):
            state = "failed"
            reasons = ("workspace.failed",)

        task_cleanup = True
        if workspace is not None:
            try:
                self.workspace.cleanup(workspace)
            except (OSError, RuntimeError, ValueError):
                task_cleanup = False
        container_cleanup = execution.cleanup_complete if execution is not None else True
        cleanup = task_cleanup and container_cleanup
        if interrupted is not None:
            if not cleanup:
                raise RuntimeError("provider interruption cleanup failed") from interrupted
            raise interrupted
        effects = RecordHandoffEffects(
            cleanup_complete=cleanup,
            network_access=False,
            process_started=execution.process_started if execution is not None else False,
            source_modified=source_modified,
            task_materialized=workspace is not None,
        )
        if not cleanup:
            state = "cleanup_failed"
            reasons = ("workspace.cleanup_failed",)
            snapshot = None
        return RecordSnapshotHandoff(
            effects=effects,
            external_record_id=self.external_record_id,
            library_snapshot_sha256=library_snapshot,
            profile_id=self.profile_id,
            provider_version=self.profile.runtime.provider["version"],
            reason_codes=reasons,
            snapshot=snapshot,
            state=state,
        )

    def _failed(self, state: str, reason: str) -> RecordSnapshotHandoff:
        return RecordSnapshotHandoff(
            effects=RecordHandoffEffects(True, False, False, False, False),
            external_record_id=self.external_record_id,
            library_snapshot_sha256=None,
            profile_id=self.profile_id,
            provider_version=self.profile.runtime.provider["version"],
            reason_codes=(reason,),
            snapshot=None,
            state=state,
        )
