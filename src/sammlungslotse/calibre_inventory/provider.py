"""Calibre CLI anti-corruption adapter."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .executor import CalibrePodmanExecutor
from .model import CalibreBook, CalibreEffects, CalibreInventoryReport
from .ports import InventoryExecutor
from .profile import CalibreRuntimeProfile
from .workspace import LibraryWorkspaceManager


FORMAT = re.compile(r"^[a-z0-9][a-z0-9+_-]{0,15}$")


def _list_value(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, list):
        values = raw
    elif isinstance(raw, str):
        values = [item.strip() for item in raw.split(",") if item.strip()]
    else:
        raise ValueError("unexpected list field")
    if any(not isinstance(item, str) or len(item) > 4096 for item in values):
        raise ValueError("invalid list field")
    return tuple(values)


def _formats(raw: Any) -> tuple[str, ...]:
    result = set()
    for value in _list_value(raw):
        suffix = Path(value).suffix.lower().removeprefix(".")
        normalized = suffix or value.lower()
        if not FORMAT.fullmatch(normalized):
            raise ValueError("invalid format projection")
        result.add(normalized)
    return tuple(sorted(result))


def parse_calibre_output(raw: bytes) -> tuple[CalibreBook, ...]:
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, list):
        raise ValueError("Calibre report root must be a list")
    books = []
    for record in value:
        if not isinstance(record, dict):
            raise ValueError("Calibre record must be an object")
        allowed = {"id", "_source_id", "title", "authors", "languages", "formats"}
        if not set(record).issubset(allowed):
            raise ValueError("Calibre report contains an unrequested field")
        source_id = record.get("id", record.get("_source_id"))
        title = record.get("title", "")
        if isinstance(source_id, bool) or not isinstance(source_id, int) or source_id < 0:
            raise ValueError("invalid Calibre record ID")
        if not isinstance(title, str) or len(title) > 16384:
            raise ValueError("invalid title")
        books.append(
            CalibreBook(
                external_record_id=source_id,
                title=title,
                authors=_list_value(record.get("authors")),
                languages=_list_value(record.get("languages")),
                formats=_formats(record.get("formats")),
            )
        )
    books.sort(key=lambda item: item.external_record_id)
    if len(books) > 100000:
        raise ValueError("record limit exceeded")
    return tuple(books)


class CalibreCliProvider:
    def __init__(
        self,
        *,
        source: Path,
        temp_root: Path,
        profile: CalibreRuntimeProfile,
        executor: InventoryExecutor | None = None,
    ) -> None:
        self.profile = profile
        self.workspace = LibraryWorkspaceManager(source, temp_root, profile)
        self.executor = executor or CalibrePodmanExecutor(profile)

    def project(self) -> CalibreInventoryReport:
        workspace = None
        process_started = False
        state = "failed"
        result: CalibreInventoryReport
        try:
            if not self.workspace.recover():
                return self._failed("failed", "workspace.recovery_requires_review")
            workspace = self.workspace.create()
            execution = self.executor.execute(workspace)
            process_started = execution.process_started
            state = execution.state
            if not self.workspace.source_unchanged(workspace):
                state = "source_changed"
                result = self._failed(
                    state,
                    "library.source_changed",
                    snapshot=workspace.source_snapshot.digest,
                    process_started=process_started,
                    task_materialized=True,
                    original_modified=True,
                )
            elif execution.state != "completed" or execution.exit_code != 0 or not execution.isolation_verified or execution.raw_output is None:
                reason = {
                    "unavailable": "executor.unavailable_or_changed",
                    "timeout": "executor.timeout",
                    "cleanup_failed": "executor.cleanup_failed",
                    "invalid_report": "executor.invalid_report",
                }.get(execution.state, "executor.failed")
                failure_state = execution.state if execution.state != "completed" else "failed"
                result = self._failed(
                    failure_state,
                    reason,
                    snapshot=workspace.source_snapshot.digest,
                    process_started=process_started,
                    task_materialized=True,
                    cleanup_complete=execution.cleanup_complete,
                )
            else:
                try:
                    books = parse_calibre_output(execution.raw_output)
                    result = CalibreInventoryReport(
                        books=books,
                        effects=CalibreEffects(True, False, False, True, True),
                        execution_state="completed",
                        library_snapshot_sha256=workspace.source_snapshot.digest,
                        profile_id=self.profile.profile_id,
                        provider_version=self.profile.provider["version"],
                        raw_output_sha256=hashlib.sha256(execution.raw_output).hexdigest(),
                        raw_output_size_bytes=len(execution.raw_output),
                    )
                except (UnicodeError, json.JSONDecodeError, ValueError):
                    result = self._failed(
                        "invalid_report",
                        "provider.output_contract_invalid",
                        snapshot=workspace.source_snapshot.digest,
                        process_started=True,
                        task_materialized=True,
                    )
        except KeyboardInterrupt:
            if workspace is not None:
                self.workspace.cleanup(workspace)
            raise
        except (OSError, RuntimeError, ValueError):
            result = self._failed(
                state,
                "library.not_safely_snapshot",
                process_started=process_started,
                task_materialized=workspace is not None,
            )
        if workspace is not None:
            try:
                self.workspace.cleanup(workspace)
            except (OSError, RuntimeError):
                return self._failed(
                    "cleanup_failed",
                    "workspace.cleanup_failed",
                    snapshot=workspace.source_snapshot.digest,
                    process_started=process_started,
                    task_materialized=True,
                    cleanup_complete=False,
                    original_modified=result.effects.original_modified,
                )
        return result

    def _failed(
        self,
        state: str,
        reason: str,
        *,
        snapshot: str | None = None,
        process_started: bool = False,
        task_materialized: bool = False,
        cleanup_complete: bool = True,
        original_modified: bool = False,
    ) -> CalibreInventoryReport:
        return CalibreInventoryReport.not_assessed(
            state=state,
            reason=reason,
            profile_id=self.profile.profile_id,
            provider_version=self.profile.provider["version"],
            snapshot_sha256=snapshot,
            process_started=process_started,
            task_materialized=task_materialized,
            cleanup_complete=cleanup_complete,
            original_modified=original_modified,
        )
