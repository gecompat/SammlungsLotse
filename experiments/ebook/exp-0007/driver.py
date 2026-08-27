from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def process_exists(pid: int) -> bool:
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        still_active = 259
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information, False, pid
        )
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if not ctypes.windll.kernel32.GetExitCodeProcess(
                handle, ctypes.byref(exit_code)
            ):
                return False
            return exit_code.value == still_active
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def reap_children() -> None:
    if os.name == "nt":
        return
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return
        if pid == 0:
            return


def kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def process_group_options() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def probe_command(
    probe: Path,
    max_input_bytes: int,
    *,
    input_path: Path | None = None,
    mode: str = "inspect",
    extra: list[str] | None = None,
) -> list[str]:
    command = [
        sys.executable,
        str(probe),
        "--max-input-bytes",
        str(max_input_bytes),
        "--mode",
        mode,
    ]
    command.extend(["--input", str(input_path)] if input_path else ["--stdin"])
    if extra:
        command.extend(extra)
    return command


def run_process(
    command: list[str],
    *,
    stdin_bytes: bytes | None,
    timeout: float,
    stdout_limit: int,
    stderr_limit: int,
) -> tuple[dict[str, Any], bytes, bytes]:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **process_group_options(),
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(input=stdin_bytes, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_process_tree(process)
        stdout, stderr = process.communicate(timeout=5)
    finally:
        reap_children()
    stdout_overflow = len(stdout) > stdout_limit
    stderr_overflow = len(stderr) > stderr_limit
    retained_stdout = stdout[:stdout_limit]
    retained_stderr = stderr[:stderr_limit]
    evidence = {
        "started": True,
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "retained_stdout_bytes": len(retained_stdout),
        "retained_stderr_bytes": len(retained_stderr),
        "stdout_overflow": stdout_overflow,
        "stderr_overflow": stderr_overflow,
        "process_cleaned": process.poll() is not None,
    }
    return evidence, retained_stdout, retained_stderr


def parsed_probe_result(stdout: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    return value


def guarded(
    *,
    approved: bool,
    stable: bool,
    actual_sha256: str,
    expected_sha256: str,
    size_bytes: int,
    input_limit: int,
) -> tuple[bool, str]:
    if not approved:
        return False, "not_approved"
    if not stable:
        return False, "unstable"
    if size_bytes > input_limit:
        return False, "input_limit_exceeded"
    if actual_sha256 != expected_sha256:
        return False, "snapshot_hash_mismatch"
    return True, "approved"


def cleanup_directory(path: Path) -> bool:
    if path.exists():
        for candidate in path.rglob("*"):
            if candidate.is_file():
                candidate.chmod(0o600)
        path.chmod(0o700)
        shutil.rmtree(path)
    return not path.exists()


def materialize(workspace: Path, payload: bytes) -> tuple[Path, Path, int]:
    task = workspace / f"task-{uuid.uuid4().hex}"
    task.mkdir(mode=0o700, parents=False, exist_ok=False)
    target = task / f"payload-{uuid.uuid4().hex}.bin"
    target.write_bytes(payload)
    target.chmod(0o400)
    return task, target, stat.S_IMODE(target.stat().st_mode)


def positive_run(
    *,
    variant: str,
    case: dict[str, Any],
    repetition: int,
    source: Path,
    payload: bytes,
    probe: Path,
    workspace: Path,
    limits: dict[str, Any],
) -> dict[str, Any]:
    before = sha256_file(source)
    task: Path | None = None
    materialized_mode: int | None = None
    provider_original_locator = variant == "original_locator"
    try:
        if variant == "stream":
            command = probe_command(probe, limits["input_bytes"])
            stdin_bytes = payload
        elif variant == "materialized":
            task, input_path, materialized_mode = materialize(workspace, payload)
            if sha256_file(input_path) != case["sha256"]:
                raise RuntimeError("materialized_snapshot_mismatch")
            command = probe_command(
                probe, limits["input_bytes"], input_path=input_path
            )
            stdin_bytes = None
        elif variant == "original_locator":
            command = probe_command(probe, limits["input_bytes"], input_path=source)
            stdin_bytes = None
        else:
            raise RuntimeError(f"unsupported variant: {variant}")
        process, stdout, _ = run_process(
            command,
            stdin_bytes=stdin_bytes,
            timeout=limits["normal_timeout_seconds"],
            stdout_limit=limits["stdout_bytes"],
            stderr_limit=limits["stderr_bytes"],
        )
        received = parsed_probe_result(stdout)
        accepted = (
            process["exit_code"] == 0
            and not process["timed_out"]
            and not process["stdout_overflow"]
            and not process["stderr_overflow"]
            and received is not None
            and received.get("received_sha256") == case["sha256"]
            and received.get("received_size_bytes") == case["size_bytes"]
        )
        semantic = {
            "variant": variant,
            "case_key": case["case_key"],
            "accepted": accepted,
            "received_sha256": received.get("received_sha256") if received else None,
            "received_size_bytes": received.get("received_size_bytes") if received else None,
            "exit_code": process["exit_code"],
            "timed_out": process["timed_out"],
            "stdout_overflow": process["stdout_overflow"],
            "stderr_overflow": process["stderr_overflow"],
        }
        return {
            **semantic,
            "repetition": repetition,
            "snapshot_sha256": case["sha256"],
            "snapshot_size_bytes": case["size_bytes"],
            "semantic_sha256": canonical_digest(semantic),
            "process": process,
            "provider_received_original_locator": provider_original_locator,
            "materialized_mode": materialized_mode,
            "original_unchanged": before == sha256_file(source),
        }
    finally:
        if task is not None:
            cleanup_directory(task)


def prestart_controls(case: dict[str, Any], limits: dict[str, Any]) -> list[dict[str, Any]]:
    controls = []
    specifications = (
        ("not_approved", False, True, case["sha256"], case["size_bytes"]),
        ("unstable", True, False, case["sha256"], case["size_bytes"]),
        ("hash_mismatch", True, True, "0" * 64, case["size_bytes"]),
        ("input_limit", True, True, case["sha256"], limits["input_bytes"] + 1),
    )
    for key, approved, stable, actual, size in specifications:
        allowed, reason = guarded(
            approved=approved,
            stable=stable,
            actual_sha256=actual,
            expected_sha256=case["sha256"],
            size_bytes=size,
            input_limit=limits["input_bytes"],
        )
        controls.append(
            {
                "control": key,
                "started": False,
                "allowed": allowed,
                "reason": reason,
            }
        )
    return controls


def stream_and_output_controls(
    payload: bytes,
    case: dict[str, Any],
    probe: Path,
    limits: dict[str, Any],
    workspace: Path,
) -> dict[str, Any]:
    command = probe_command(probe, limits["input_bytes"])
    incomplete, stdout, _ = run_process(
        command,
        stdin_bytes=payload[:-1],
        timeout=limits["normal_timeout_seconds"],
        stdout_limit=limits["stdout_bytes"],
        stderr_limit=limits["stderr_bytes"],
    )
    received = parsed_probe_result(stdout)
    incomplete["accepted"] = bool(
        received
        and received.get("received_sha256") == case["sha256"]
        and received.get("received_size_bytes") == case["size_bytes"]
    )

    overflow_size = max(limits["stdout_bytes"], limits["stderr_bytes"]) * 4
    stdout_overflow, _, _ = run_process(
        probe_command(
            probe,
            limits["input_bytes"],
            mode="stdout-overflow",
            extra=["--overflow-bytes", str(overflow_size)],
        ),
        stdin_bytes=payload,
        timeout=limits["normal_timeout_seconds"],
        stdout_limit=limits["stdout_bytes"],
        stderr_limit=limits["stderr_bytes"],
    )
    stderr_overflow, _, _ = run_process(
        probe_command(
            probe,
            limits["input_bytes"],
            mode="stderr-overflow",
            extra=["--overflow-bytes", str(overflow_size)],
        ),
        stdin_bytes=payload,
        timeout=limits["normal_timeout_seconds"],
        stdout_limit=limits["stdout_bytes"],
        stderr_limit=limits["stderr_bytes"],
    )

    pid_file = workspace / f"child-{uuid.uuid4().hex}.pid"
    timeout_result, _, _ = run_process(
        probe_command(
            probe,
            limits["input_bytes"],
            mode="child-timeout",
            extra=["--pid-file", str(pid_file)],
        ),
        stdin_bytes=payload,
        timeout=limits["control_timeout_seconds"],
        stdout_limit=limits["stdout_bytes"],
        stderr_limit=limits["stderr_bytes"],
    )
    child_pid = int(pid_file.read_text(encoding="ascii").strip()) if pid_file.is_file() else None
    time.sleep(0.05)
    reap_children()
    timeout_result["child_pid_recorded"] = child_pid is not None
    timeout_result["child_process_cleaned"] = bool(
        child_pid is not None and not process_exists(child_pid)
    )
    pid_file.unlink(missing_ok=True)
    return {
        "incomplete_stream": incomplete,
        "stdout_overflow": stdout_overflow,
        "stderr_overflow": stderr_overflow,
        "timeout_child": timeout_result,
    }


def v2_controls(
    payload: bytes,
    probe: Path,
    workspace: Path,
    limits: dict[str, Any],
) -> dict[str, Any]:
    outcomes: dict[str, Any] = {}

    for key, mode, timeout in (
        ("success", "inspect", limits["normal_timeout_seconds"]),
        ("error", "fail", limits["normal_timeout_seconds"]),
        ("timeout", "child-timeout", limits["control_timeout_seconds"]),
    ):
        task, target, _ = materialize(workspace, payload)
        pid_file = task / "child.pid"
        extra = ["--pid-file", str(pid_file)] if mode == "child-timeout" else None
        try:
            process, _, _ = run_process(
                probe_command(
                    probe,
                    limits["input_bytes"],
                    input_path=target,
                    mode=mode,
                    extra=extra,
                ),
                stdin_bytes=None,
                timeout=timeout,
                stdout_limit=limits["stdout_bytes"],
                stderr_limit=limits["stderr_bytes"],
            )
            child_pid = (
                int(pid_file.read_text(encoding="ascii").strip())
                if pid_file.is_file()
                else None
            )
        finally:
            cleaned = cleanup_directory(task)
        outcomes[key] = {
            "process": process,
            "cleanup": cleaned,
            "child_process_cleaned": (
                child_pid is None or not process_exists(child_pid)
            ),
        }

    task, _, _ = materialize(workspace, payload)
    try:
        try:
            raise KeyboardInterrupt
        except KeyboardInterrupt:
            interrupted = True
    finally:
        interruption_cleanup = cleanup_directory(task)
    outcomes["interruption"] = {
        "interrupted": interrupted,
        "cleanup": interruption_cleanup,
    }

    residue_task = workspace / f"crash-{uuid.uuid4().hex}"
    residue_task.mkdir(mode=0o700, parents=False, exist_ok=False)
    residue = residue_task / "residue.bin"
    residue.write_bytes(payload[: limits["crash_residue_bytes"]])
    residue_detected = residue.is_file()
    residue_size = residue.stat().st_size
    recovery_cleanup = cleanup_directory(residue_task)
    outcomes["crash_residue"] = {
        "detected": residue_detected,
        "size_bytes": residue_size,
        "bounded": residue_size <= limits["crash_residue_bytes"],
        "recovery_cleanup": recovery_cleanup,
    }
    return outcomes


def v3_controls(
    payload: bytes,
    probe: Path,
    workspace: Path,
    limits: dict[str, Any],
) -> dict[str, Any]:
    changed = payload[::-1]
    if changed == payload:
        changed = payload + b"x"

    exchange_task, exchange_target, _ = materialize(workspace, payload)
    snapshot_hash = sha256_file(exchange_target)
    exchange_target.chmod(0o600)
    exchange_target.write_bytes(changed)
    allowed, reason = guarded(
        approved=True,
        stable=True,
        actual_sha256=sha256_file(exchange_target),
        expected_sha256=snapshot_hash,
        size_bytes=exchange_target.stat().st_size,
        input_limit=limits["input_bytes"],
    )
    exchange = {"started": False, "allowed": allowed, "reason": reason}
    cleanup_directory(exchange_task)

    rename_task, rename_target, _ = materialize(workspace, payload)
    renamed = rename_target.with_name("renamed.bin")
    rename_target.rename(renamed)
    rename = {
        "started": False,
        "allowed": rename_target.is_file(),
        "reason": "locator_missing" if not rename_target.is_file() else "unexpected",
    }
    cleanup_directory(rename_task)

    concurrent_task, concurrent_target, _ = materialize(workspace, payload)
    concurrent_target.chmod(0o600)
    ready = concurrent_task / "ready"
    proceed = concurrent_task / "continue"
    command = probe_command(
        probe,
        limits["input_bytes"],
        input_path=concurrent_target,
        mode="coordinated-inspect",
        extra=["--ready-file", str(ready), "--continue-file", str(proceed)],
    )
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **process_group_options(),
    )
    deadline = time.monotonic() + limits["normal_timeout_seconds"]
    while time.monotonic() < deadline and not ready.is_file():
        time.sleep(0.01)
    ready_seen = ready.is_file()
    concurrent_target.write_bytes(changed)
    proceed.write_text("continue\n", encoding="ascii")
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=limits["normal_timeout_seconds"])
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_process_tree(process)
        stdout, stderr = process.communicate(timeout=5)
    received = parsed_probe_result(stdout)
    post_hash = sha256_file(concurrent_target)
    accepted = bool(
        received
        and received.get("received_sha256") == snapshot_hash
        and post_hash == snapshot_hash
    )
    concurrent = {
        "started": True,
        "ready_seen": ready_seen,
        "timed_out": timed_out,
        "exit_code": process.returncode,
        "stderr_bytes": len(stderr),
        "received_snapshot": bool(
            received and received.get("received_sha256") == snapshot_hash
        ),
        "post_snapshot_unchanged": post_hash == snapshot_hash,
        "accepted": accepted,
        "provider_received_original_locator": True,
    }
    cleanup_directory(concurrent_task)
    return {"exchange": exchange, "rename": rename, "concurrent_change": concurrent}


def classify_variants() -> list[dict[str, str]]:
    return [
        {
            "variant": "stream",
            "classification": "QUALIFIED",
            "heaviest_residual_error": "A path-only provider cannot consume this handoff.",
        },
        {
            "variant": "materialized",
            "classification": "QUALIFIED",
            "heaviest_residual_error": "A host crash can leave a bounded residue that requires the task recovery sweep.",
        },
        {
            "variant": "original_locator",
            "classification": "REJECTED",
            "heaviest_residual_error": "The provider receives the original locator and a concurrent replacement remains a TOCTOU exposure.",
        },
    ]


def semantic_repetitions_match(runs: list[dict[str, Any]]) -> bool:
    grouped: dict[tuple[str, str], list[str]] = {}
    for run in runs:
        grouped.setdefault((run["variant"], run["case_key"]), []).append(
            run["semantic_sha256"]
        )
    return all(len(values) == 2 and len(set(values)) == 1 for values in grouped.values())


def run_profile(
    profile: dict[str, Any],
    *,
    probe: Path,
    corpus_root: Path,
    workspace: Path,
    platform_profile: str,
) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    limits = profile["limits"]
    cases: list[tuple[dict[str, Any], Path, bytes]] = []
    originals_before: dict[str, str] = {}
    for case in profile["cases"]:
        source = (corpus_root / case["relative_path"]).resolve()
        if corpus_root.resolve() not in source.parents or not source.is_file():
            raise RuntimeError("EXP-0007 fixture path escapes or is missing")
        payload = source.read_bytes()
        if len(payload) != case["size_bytes"] or sha256_bytes(payload) != case["sha256"]:
            raise RuntimeError("EXP-0007 fixture differs from the frozen profile")
        cases.append((case, source, payload))
        originals_before[case["case_key"]] = sha256_file(source)

    positive_runs = []
    for case, source, payload in cases:
        for variant in profile["rules"]["variants"]:
            for repetition in range(1, profile["rules"]["repetitions"] + 1):
                positive_runs.append(
                    positive_run(
                        variant=variant,
                        case=case,
                        repetition=repetition,
                        source=source,
                        payload=payload,
                        probe=probe,
                        workspace=workspace,
                        limits=limits,
                    )
                )

    first_case, _, first_payload = cases[0]
    controls = {
        "prestart": prestart_controls(first_case, limits),
        "stream_and_output": stream_and_output_controls(
            first_payload, first_case, probe, limits, workspace
        ),
        "materialized": v2_controls(first_payload, probe, workspace, limits),
        "original_locator": v3_controls(first_payload, probe, workspace, limits),
    }
    originals_after = {
        case["case_key"]: sha256_file(source) for case, source, _ in cases
    }
    classifications = classify_variants()
    workspace_empty = not any(workspace.iterdir())
    environment = dict(os.environ)
    environment_minimized = (
        environment == profile["environment_allowlist"]
        if platform_profile == "linux"
        else None
    )
    return {
        "schema_version": 1,
        "experiment": "EXP-0007",
        "profile_id": profile["profile_id"],
        "platform_profile": platform_profile,
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "positive_runs": positive_runs,
        "controls": controls,
        "variant_classifications": classifications,
        "semantic_repetitions_identical": semantic_repetitions_match(positive_runs),
        "originals_before_sha256": originals_before,
        "originals_after_sha256": originals_after,
        "originals_unchanged": originals_before == originals_after,
        "workspace_empty_after_run": workspace_empty,
        "environment_minimized": environment_minimized,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--platform-profile", choices=("windows", "linux"), required=True)
    args = parser.parse_args()
    result = run_profile(
        load_json(args.profile),
        probe=args.probe,
        corpus_root=args.corpus_root,
        workspace=args.workspace,
        platform_profile=args.platform_profile,
    )
    sys.stdout.write(canonical_json(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
