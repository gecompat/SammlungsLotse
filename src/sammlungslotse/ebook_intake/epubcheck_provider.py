"""EPUBCheck adapter behind the provider-neutral deep read-only port."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path, PurePosixPath

from .deep_model import DeepEffects, DeepFinding, DeepLocation, DeepToolResult
from .deep_ports import ProcessExecution, ProcessExecutor
from .deep_profile import DeepRuntimeProfile
from .deep_workspace import (
    TaskCleanupError,
    TaskWorkspace,
    TaskWorkspaceManager,
    sha256_file,
)
from .model import Snapshot
from .podman_executor import PodmanExecutor


def _publication_path(value: object) -> str | None:
    if not isinstance(value, str) or not value or len(value) > 1024:
        return None
    if "\\" in value or "\x00" in value:
        return None
    logical = PurePosixPath(value)
    if logical.is_absolute() or ".." in logical.parts:
        return None
    return logical.as_posix()


def _optional_position(value: object) -> int | None:
    return value if isinstance(value, int) and value >= 0 else None


class EpubCheckProvider:
    """Materializes V2, invokes the bounded executor and projects evidence."""

    def __init__(
        self,
        *,
        profile: DeepRuntimeProfile,
        temp_root: Path,
        executor: ProcessExecutor | None = None,
    ) -> None:
        self._profile = profile
        self._workspace = TaskWorkspaceManager(temp_root, profile)
        self._executor = executor or PodmanExecutor(profile)

    def inspect(self, snapshot: Snapshot) -> DeepToolResult:
        provider = self._profile.provider
        common = {
            "profile_id": self._profile.profile_id,
            "provider_id": provider["id"],
            "provider_version": provider["version"],
        }
        if snapshot.size_bytes != len(snapshot.data) or snapshot.sha256 != hashlib.sha256(
            snapshot.data
        ).hexdigest():
            return DeepToolResult.not_assessed(
                execution_state="hash_mismatch",
                reason_code="snapshot.preimage_mismatch",
                snapshot_sha256=snapshot.sha256,
                **common,
            )
        if snapshot.size_bytes > int(self._profile.execution["input_max_bytes"]):
            return DeepToolResult.not_assessed(
                execution_state="unavailable",
                reason_code="resource.input_limit_exceeded",
                snapshot_sha256=snapshot.sha256,
                **common,
            )
        try:
            recovery = self._workspace.recover()
        except TaskCleanupError:
            result = DeepToolResult.not_assessed(
                execution_state="cleanup_failed",
                reason_code="workspace.partial_cleanup_failed",
                snapshot_sha256=snapshot.sha256,
                observations=recovery.observations,
                task_materialized=True,
                cleanup_complete=False,
                **common,
            )
        except (OSError, RuntimeError, ValueError):
            return DeepToolResult.not_assessed(
                execution_state="failed",
                reason_code="recovery.failed",
                snapshot_sha256=snapshot.sha256,
                **common,
            )
        if not recovery.safe_to_continue:
            return DeepToolResult.not_assessed(
                execution_state="failed",
                reason_code="recovery.review_required",
                snapshot_sha256=snapshot.sha256,
                observations=recovery.observations,
                **common,
            )

        workspace: TaskWorkspace | None = None
        result: DeepToolResult | None = None
        try:
            workspace = self._workspace.create(snapshot)
            if sha256_file(workspace.input_file) != snapshot.sha256:
                result = DeepToolResult.not_assessed(
                    execution_state="hash_mismatch",
                    reason_code="materialization.pre_run_hash_mismatch",
                    snapshot_sha256=snapshot.sha256,
                    observations=recovery.observations,
                    task_materialized=True,
                    **common,
                )
            else:
                execution = self._executor.execute(workspace)
                result = self._result_from_execution(
                    snapshot=snapshot,
                    execution=execution,
                    observations=recovery.observations,
                )
                if sha256_file(workspace.input_file) != snapshot.sha256:
                    result = DeepToolResult.not_assessed(
                        execution_state="hash_mismatch",
                        reason_code="materialization.post_run_hash_mismatch",
                        snapshot_sha256=snapshot.sha256,
                        observations=result.observations,
                        process_started=execution.process_started,
                        task_materialized=True,
                        raw_report=execution.report,
                        **common,
                    )
        except (OSError, RuntimeError, ValueError):
            result = DeepToolResult.not_assessed(
                execution_state="failed",
                reason_code="workspace.or_provider_failure",
                snapshot_sha256=snapshot.sha256,
                observations=recovery.observations,
                task_materialized=workspace is not None,
                **common,
            )
        finally:
            if workspace is not None:
                try:
                    self._workspace.cleanup(workspace)
                except (OSError, RuntimeError, ValueError):
                    prior = result
                    result = DeepToolResult.not_assessed(
                        execution_state="cleanup_failed",
                        reason_code="workspace.cleanup_failed",
                        snapshot_sha256=snapshot.sha256,
                        observations=(
                            prior.observations if prior is not None else recovery.observations
                        ),
                        process_started=(
                            prior.effects.process_started if prior is not None else False
                        ),
                        task_materialized=True,
                        cleanup_complete=False,
                        raw_report=(prior.raw_report if prior is not None else None),
                        **common,
                    )
                else:
                    if result is not None and not result.effects.cleanup_complete:
                        result = replace(
                            result,
                            execution_state="cleanup_failed",
                            assessment="not_assessed",
                            findings=(),
                            reason_codes=("executor.container_cleanup_failed",),
                        )
        if result is None:
            return DeepToolResult.not_assessed(
                execution_state="failed",
                reason_code="provider.no_result",
                snapshot_sha256=snapshot.sha256,
                observations=recovery.observations,
                **common,
            )
        return result

    def _result_from_execution(
        self,
        *,
        snapshot: Snapshot,
        execution: ProcessExecution,
        observations: tuple[str, ...],
    ) -> DeepToolResult:
        provider = self._profile.provider
        combined_observations = observations + execution.observations
        common = {
            "profile_id": self._profile.profile_id,
            "provider_id": provider["id"],
            "provider_version": provider["version"],
        }
        if execution.state == "completed" and not execution.isolation_verified:
            return DeepToolResult.not_assessed(
                execution_state="failed",
                reason_code="executor.isolation_not_verified",
                snapshot_sha256=snapshot.sha256,
                observations=combined_observations,
                process_started=execution.process_started,
                task_materialized=True,
                cleanup_complete=execution.cleanup_complete,
                raw_report=execution.report,
                **common,
            )
        if execution.state == "completed" and (
            not execution.process_started or execution.exit_code not in {0, 1}
        ):
            return DeepToolResult.not_assessed(
                execution_state="failed",
                reason_code="executor.invalid_completion_state",
                snapshot_sha256=snapshot.sha256,
                observations=combined_observations,
                process_started=execution.process_started,
                task_materialized=True,
                cleanup_complete=execution.cleanup_complete,
                raw_report=execution.report,
                **common,
            )
        if execution.state != "completed":
            return DeepToolResult.not_assessed(
                execution_state=execution.state,
                reason_code=f"executor.{execution.state}",
                snapshot_sha256=snapshot.sha256,
                observations=combined_observations,
                process_started=execution.process_started,
                task_materialized=True,
                cleanup_complete=execution.cleanup_complete,
                raw_report=execution.report,
                **common,
            )
        try:
            findings = self._parse_report(execution.report)
        except (UnicodeError, json.JSONDecodeError, TypeError, ValueError):
            return DeepToolResult.not_assessed(
                execution_state="invalid_report",
                reason_code="provider.invalid_report",
                snapshot_sha256=snapshot.sha256,
                observations=combined_observations,
                process_started=True,
                task_materialized=True,
                cleanup_complete=execution.cleanup_complete,
                raw_report=execution.report,
                **common,
            )
        assessment = (
            "epubcheck_conformance_findings"
            if findings
            else "no_epubcheck_conformance_errors_reported"
        )
        return DeepToolResult(
            assessment=assessment,
            effects=DeepEffects(
                cleanup_complete=execution.cleanup_complete,
                network_access=False,
                original_modified=False,
                process_started=True,
                task_materialized=True,
            ),
            execution_state="completed",
            findings=findings,
            observations=combined_observations + ("isolation.verified",),
            profile_id=self._profile.profile_id,
            provider_id=provider["id"],
            provider_version=provider["version"],
            reason_codes=(),
            snapshot_sha256=snapshot.sha256,
            raw_report=execution.report,
        )

    def _parse_report(self, content: bytes | None) -> tuple[DeepFinding, ...]:
        if content is None:
            raise ValueError("missing report")
        if len(content) > int(self._profile.execution["raw_report_max_bytes"]):
            raise ValueError("report exceeds bound")
        value = json.loads(content.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("report root must be an object")
        checker = value.get("checker")
        messages = value.get("messages")
        if not isinstance(checker, dict) or checker.get("checkerVersion") != "5.3.0":
            raise ValueError("provider identity differs")
        if not isinstance(messages, list) or len(messages) > 2048:
            raise ValueError("invalid finding collection")
        projected: list[DeepFinding] = []
        for item in messages:
            if not isinstance(item, dict):
                raise ValueError("invalid finding")
            code = item.get("ID")
            severity = item.get("severity")
            message = item.get("message")
            if not all(isinstance(part, str) and part for part in (code, severity, message)):
                raise ValueError("incomplete finding")
            raw_locations = item.get("locations")
            if not isinstance(raw_locations, list):
                raise ValueError("invalid locations")
            locations: list[DeepLocation] = []
            for raw in raw_locations:
                if not isinstance(raw, dict):
                    raise ValueError("invalid location")
                path = _publication_path(raw.get("path"))
                if path is not None:
                    locations.append(
                        DeepLocation(
                            path=path,
                            line=_optional_position(raw.get("line")),
                            column=_optional_position(raw.get("column")),
                        )
                    )
            projected.append(
                DeepFinding(
                    code=code,
                    severity=severity,
                    message=message,
                    locations=tuple(locations),
                )
            )
        return tuple(projected)
