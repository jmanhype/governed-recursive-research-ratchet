"""Fail-closed runner for an operator-authorized TypeSafe Jev measurement.

Repository implementation and injected-transport tests never start a real
measurement.  A real run additionally requires an exact authorization record
and a separate environment opt-in.  The runner deliberately has no retry loop:
each adapter challenge is attempted at most once and an adapter failure leaves
an incomplete run with no selector result.
"""

import argparse
import datetime as _datetime
import hashlib
import json
import os
import stat
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import jev_adapter
import selector_comparison


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_ROOT = ROOT / "corpus"
REAL_RUN_ENV = "GRRR_JEV_REAL_SELECTOR_MEASUREMENT"
EVENT_SCHEMA_VERSION = 1
REPORT_SCHEMA_VERSION = 1
MAX_AUTHORIZATION_BYTES = 64 * 1024
PROTECTED_PATH_ROOT = Path("/Library/GRRR")

CORPUS_FREEZE_DIGEST = (
    "dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529"
)
AUTHORIZATION_FIELDS = frozenset({
    "schema_version",
    "authorized_by",
    "action",
    "corpus_freeze_digest",
    "max_calls",
    "selected_budget",
    "retries_allowed",
    "measured_usage",
    "credential_echo_fail_closed",
    "approval_quote",
    "approval_time",
})


class MeasurementRefused(RuntimeError):
    """A gate refused before any adapter availability probe."""


class AuthorizationError(MeasurementRefused):
    """The exact authorization schema did not match."""


class OutputError(MeasurementRefused):
    """The output location was unsafe or already present."""


class PostCallEvidenceError(RuntimeError):
    """Evidence could not be finalized after one or more attempted calls."""

    def __init__(self, report: Dict[str, Any]):
        self.report = report
        super().__init__(
            "measurement evidence is unknown/incomplete after an attempted call"
        )


class CallLimitExceeded(RuntimeError):
    """The adapter attempted to exceed the authorized call ceiling."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _utc_now() -> str:
    return (
        _datetime.datetime.now(_datetime.timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _approval_time_is_valid(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = _datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return parsed.utcoffset() == _datetime.timedelta(0)


def _exact_int(value: Any) -> bool:
    return type(value) is int


def _authorization_matches_exact_schema(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == AUTHORIZATION_FIELDS
        and _exact_int(value["schema_version"])
        and value["schema_version"] == 1
        and value["authorized_by"] == "operator-speed"
        and value["action"] == "typesafe-jev-selector-measurement"
        and value["corpus_freeze_digest"] == CORPUS_FREEZE_DIGEST
        and _exact_int(value["max_calls"])
        and value["max_calls"] == 32
        and _exact_int(value["selected_budget"])
        and value["selected_budget"] == 8
        and value["retries_allowed"] is False
        and value["measured_usage"] == "token-only"
        and value["credential_echo_fail_closed"] is True
        and isinstance(value["approval_quote"], str)
        and 0 < len(value["approval_quote"]) <= 512
        and _approval_time_is_valid(value["approval_time"])
    )


def _absolute_path_or_refuse(path: Path) -> Path:
    """Return a lexical absolute path before any target filesystem syscall."""
    try:
        raw = os.fspath(path)
    except TypeError:
        raise OutputError("path is not a safe absolute path") from None
    if not isinstance(raw, str) or "\0" in raw:
        raise OutputError("path is not a safe absolute path") from None
    if raw.startswith("//"):
        raise OutputError("double-leading-slash paths are not allowed")
    supplied = Path(raw)
    if ".." in supplied.parts:
        raise OutputError("path traversal is not allowed")
    try:
        absolute = Path(os.path.abspath(raw))
    except (OSError, ValueError):
        raise OutputError("path is not a safe absolute path") from None
    if ".." in absolute.parts or (
        absolute == PROTECTED_PATH_ROOT or PROTECTED_PATH_ROOT in absolute.parents
    ):
        raise OutputError("protected path is not allowed")
    return absolute


def _directory_flags() -> int:
    required = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    if not hasattr(os, "O_NOFOLLOW"):
        raise OutputError("safe path traversal requires O_NOFOLLOW")
    return required | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


class _SafeDirectory:
    def __init__(self, descriptor: int, path: Path):
        self._descriptor = descriptor
        self.path = path

    @property
    def descriptor(self) -> int:
        return self._descriptor

    def open(self, name: str, flags: int, mode: int = 0o777) -> int:
        if (not isinstance(name, str) or not name or name in (".", "..")
                or "/" in name or "\0" in name):
            raise OutputError("evidence filename is unsafe")
        try:
            return os.open(name, flags, mode, dir_fd=self._descriptor)
        except OSError:
            raise OutputError("could not open evidence relative to safe directory") from None

    def close(self) -> None:
        if self._descriptor >= 0:
            try:
                os.close(self._descriptor)
            finally:
                self._descriptor = -1


def _root_directory() -> _SafeDirectory:
    try:
        descriptor = os.open("/", _directory_flags())
    except OSError:
        raise OutputError("could not open safe filesystem root") from None
    return _SafeDirectory(descriptor, Path("/"))


def _advance_directory(
    parent: _SafeDirectory,
    component: str,
    *,
    create: bool,
) -> Tuple[_SafeDirectory, bool]:
    flags = _directory_flags()
    created = False
    try:
        descriptor = os.open(component, flags, dir_fd=parent.descriptor)
    except FileNotFoundError:
        if not create:
            raise OutputError("path component is unavailable") from None
        created = True
        try:
            os.mkdir(component, 0o700, dir_fd=parent.descriptor)
            descriptor = os.open(component, flags, dir_fd=parent.descriptor)
        except OSError:
            raise OutputError("could not create exclusive safe directory") from None
    except OSError:
        raise OutputError("path component is not a real directory") from None

    try:
        opened_metadata = os.fstat(descriptor)
        named_metadata = os.stat(
            component, dir_fd=parent.descriptor, follow_symlinks=False
        )
    except OSError:
        os.close(descriptor)
        raise OutputError("could not verify safe directory identity") from None
    if (not stat.S_ISDIR(opened_metadata.st_mode)
            or stat.S_ISLNK(named_metadata.st_mode)
            or (opened_metadata.st_dev, opened_metadata.st_ino)
            != (named_metadata.st_dev, named_metadata.st_ino)):
        os.close(descriptor)
        raise OutputError("path component is not a real directory") from None
    return _SafeDirectory(descriptor, parent.path / component), created


def _open_existing_directory(path: Path) -> _SafeDirectory:
    absolute = _absolute_path_or_refuse(path)
    directory = _root_directory()
    try:
        for component in absolute.parts[1:]:
            parent = directory
            directory, _ = _advance_directory(parent, component, create=False)
            parent.close()
    except Exception:
        directory.close()
        raise
    return directory


def _create_exclusive_directory(path: Path) -> _SafeDirectory:
    absolute = _absolute_path_or_refuse(path)
    if not absolute.parts[1:]:
        raise OutputError("output directory must be a new non-root path")
    directory = _root_directory()
    try:
        components = absolute.parts[1:]
        for index, component in enumerate(components):
            parent = directory
            try:
                directory, created = _advance_directory(parent, component, create=True)
            except Exception:
                parent.close()
                raise
            parent.close()
            if index == len(components) - 1:
                if not created:
                    raise OutputError("output directory must not already exist")
    except Exception:
        directory.close()
        raise
    return directory


def _read_regular_file(path: Path) -> bytes:
    absolute = _absolute_path_or_refuse(path)
    parent = _open_existing_directory(absolute.parent)
    descriptor = -1
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    else:
        parent.close()
        raise OutputError("safe file open requires O_NOFOLLOW")
    try:
        descriptor = parent.open(absolute.name, flags)
        metadata = os.fstat(descriptor)
        if (stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode)
                or metadata.st_size > MAX_AUTHORIZATION_BYTES):
            os.close(descriptor)
            raise AuthorizationError("authorization record is invalid")
        chunks = []
        remaining = MAX_AUTHORIZATION_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(4096, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        os.close(descriptor)
        descriptor = -1
    except (AuthorizationError, OutputError):
        raise
    except OSError:
        raise AuthorizationError("authorization record is invalid") from None
    finally:
        parent.close()
        if descriptor >= 0:
            os.close(descriptor)
    if len(raw) > MAX_AUTHORIZATION_BYTES:
        raise AuthorizationError("authorization record is invalid")
    return raw


def load_authorization(path: Path) -> Tuple[Dict[str, Any], str]:
    """Load only the exact operator authorization schema and hash it."""
    try:
        raw = _read_regular_file(path)
        value = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (AuthorizationError, OutputError):
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise AuthorizationError("authorization record is invalid") from None

    fixed = _authorization_matches_exact_schema(value)
    if not fixed:
        raise AuthorizationError("authorization record is invalid")
    return value, _sha256(value)


def _safe_output_directory(path: Path) -> _SafeDirectory:
    return _create_exclusive_directory(path)


class EventLog:
    """Append-only writer for small, fixed-shape sanitized JSONL events."""

    def __init__(self, directory: _SafeDirectory, run_id: str):
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_EXCL
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            self._fd = directory.open("events.jsonl", flags, 0o600)
        except OutputError:
            raise OutputError("could not create exclusive append-only event log") from None
        self._file = os.fdopen(self._fd, "wb", buffering=0)
        self.run_id = run_id
        self.sequence = 0
        self.write_failed = False

    def append(self, event: str, **fields) -> None:
        self.sequence += 1
        record = {
            "schema_version": EVENT_SCHEMA_VERSION,
            "sequence": self.sequence,
            "run_id": self.run_id,
            "recorded_at": _utc_now(),
            "event": event,
            **fields,
        }
        raw = _canonical(record) + b"\n"
        try:
            self._file.write(raw)
            self._file.flush()
        except OSError:
            self.write_failed = True
            raise OutputError("event log append failed") from None

    def close(self) -> None:
        if not self._file.closed:
            try:
                self._file.flush()
                os.fsync(self._fd)
            finally:
                self._file.close()


def _safe_usage(response: Any) -> Optional[Dict[str, int]]:
    if not isinstance(response, Mapping) or not isinstance(response.get("usage"), Mapping):
        return None
    usage = response["usage"]
    if set(usage) != {"input_tokens", "output_tokens"}:
        return None
    result = {}
    for name in ("input_tokens", "output_tokens"):
        value = usage[name]
        if (not isinstance(value, int) or isinstance(value, bool)
                or not 0 <= value <= 10**12):
            return None
        result[name] = value
    return result


class CallRecorder:
    """One-shot transport wrapper that emits sanitized before/after events."""

    def __init__(self, transport, event_log: EventLog, max_calls: int):
        self._transport = transport
        self._event_log = event_log
        self._max_calls = max_calls
        self.attempted_calls = 0
        self.returned_responses = 0
        self.usage_complete = True
        self.known_usage = {"input_tokens": 0, "output_tokens": 0}

    def __call__(self, url: str, api_key: str, body: Dict, timeout: float):
        if self.attempted_calls >= self._max_calls:
            raise CallLimitExceeded("authorized call limit exceeded")
        self.attempted_calls += 1
        state = body.get("state") if isinstance(body, Mapping) else None
        state = state if isinstance(state, Mapping) else {}
        challenge_ref = state.get("challenge_ref")
        category = state.get("category")
        self._event_log.append(
            "call_attempt_started",
            attempt=self.attempted_calls,
            max_calls=self._max_calls,
            challenge_ref=challenge_ref if isinstance(challenge_ref, str) else None,
            category=category if isinstance(category, str) else None,
        )
        try:
            response = self._transport(url, api_key, body, timeout)
        except Exception:
            self.usage_complete = False
            self._event_log.append(
                "call_attempt_finished",
                attempt=self.attempted_calls,
                max_calls=self._max_calls,
                outcome="transport-exception",
                usage=None,
                usage_valid=False,
            )
            raise
        self.returned_responses += 1
        usage = _safe_usage(response)
        if usage is None:
            self.usage_complete = False
        else:
            self.known_usage["input_tokens"] += usage["input_tokens"]
            self.known_usage["output_tokens"] += usage["output_tokens"]
        self._event_log.append(
            "call_attempt_finished",
            attempt=self.attempted_calls,
            max_calls=self._max_calls,
            outcome="transport-returned",
            usage=usage,
            usage_valid=usage is not None,
        )
        return response


def _exclusive_json_write(directory: _SafeDirectory, name: str, value: Dict) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = directory.open(name, flags, 0o600)
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            json.dump(value, stream, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(fd)
    except OSError:
        raise OutputError("could not write exclusive final report") from None


def _mapping_for_result(result: Dict, freeze_digest: str):
    mapping = []
    for ranked in result.get("ranking", []):
        challenge = ranked.get("challenge")
        if isinstance(challenge, str):
            mapping.append({
                "challenge": challenge,
                "challenge_ref": jev_adapter.external_challenge_ref(
                    challenge, freeze_digest
                ),
            })
    return sorted(mapping, key=lambda item: item["challenge"])


def _attempt_selection(
    catalog,
    selected_budget: int,
    recorder: CallRecorder,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Attempt the reviewed selector once and classify only fixed failures."""
    try:
        candidate = selector_comparison.jev_select(
            catalog,
            selected_budget,
            transport=recorder,
        )
    except CallLimitExceeded:
        return None, "authorized-call-limit-exceeded"
    except jev_adapter.JevError:
        return None, "jev-adapter-failed"
    except selector_comparison.SelectorError:
        return None, "selector-validation-failed"
    except Exception:
        return None, "runner-internal-error"
    if not candidate.get("available"):
        return None, "jev-unavailable"
    if not recorder.usage_complete:
        return None, "usage-observation-incomplete"
    if candidate.get("usage") != recorder.known_usage:
        return None, "usage-integrity-failed"
    return candidate, None


def _build_report(
    *,
    authorization: Dict[str, Any],
    authorization_sha256: str,
    run_id: str,
    started_at: str,
    completed_at: str,
    result: Optional[Dict[str, Any]],
    failure_code: Optional[str],
    recorder: Optional[CallRecorder],
    event_log: Optional[EventLog],
    event_log_complete: bool,
) -> Dict[str, Any]:
    complete = result is not None and failure_code is None and event_log_complete
    usage_complete = bool(
        recorder and recorder.attempted_calls and recorder.usage_complete
    )
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "run_id": run_id,
        "status": "complete" if complete else "incomplete",
        "adapter_outcome": (
            "complete"
            if complete
            else "no-call-pre-call-refusal"
            if recorder is not None and not recorder.attempted_calls
            else "unknown-or-incomplete-after-attempted-call"
        ),
        "started_at": started_at,
        "completed_at": completed_at,
        "authorization": {
            "sha256": authorization_sha256,
            "action": authorization["action"],
            "authorized_by": authorization["authorized_by"],
            "corpus_freeze_digest": authorization["corpus_freeze_digest"],
            "approval_time": authorization["approval_time"],
            "approval_quote_sha256": _sha256(authorization["approval_quote"]),
            "max_calls": authorization["max_calls"],
            "selected_budget": authorization["selected_budget"],
            "retries_allowed": authorization["retries_allowed"],
            "measured_usage": authorization["measured_usage"],
            "credential_echo_fail_closed": authorization["credential_echo_fail_closed"],
        },
        "attempts": {
            "attempted_calls": recorder.attempted_calls if recorder else 0,
            "returned_responses": recorder.returned_responses if recorder else 0,
            "retry_count": 0,
        },
        "usage": {
            "unit": "tokens",
            "input_tokens": recorder.known_usage["input_tokens"] if recorder else 0,
            "output_tokens": recorder.known_usage["output_tokens"] if recorder else 0,
            "observation_complete": usage_complete,
            "incomplete_reason": None if usage_complete else (
                "no calls were attempted"
                if recorder and not recorder.attempted_calls
                else "one or more transport outcomes did not provide valid usage"
            ),
        },
        "cost": {
            "usd": None,
            "status": "unknown-until-independent-receipt",
            "receipt": None,
        },
        "event_log": {
            "append_only": True,
            "complete": bool(
                event_log_complete
                and event_log is not None
                and not event_log.write_failed
            ),
        },
        "selector_result": result if complete else None,
        "local_challenge_mapping": _mapping_for_result(
            result, CORPUS_FREEZE_DIGEST
        ) if complete else [],
        "failure_code": failure_code,
        "next_action": "operator-review-required; do not automatically rerun",
    }


def execute_measurement(
    authorization: Dict[str, Any],
    authorization_sha256: str,
    output_path: Path,
    *,
    transport=None,
) -> Dict[str, Any]:
    """Execute one authorized run; injected transport is for offline tests."""
    if not _authorization_matches_exact_schema(authorization):
        raise AuthorizationError("authorization record is invalid")
    _absolute_path_or_refuse(output_path)
    catalog = selector_comparison.load_catalog(DEFAULT_CORPUS_ROOT)
    if len(catalog) > authorization["max_calls"]:
        raise MeasurementRefused("frozen catalog exceeds the authorized call ceiling")
    if authorization["selected_budget"] > len(catalog):
        raise MeasurementRefused("selected budget exceeds the frozen catalog")

    output = _safe_output_directory(output_path)
    run_id = uuid.uuid4().hex
    started_at = _utc_now()
    event_log: Optional[EventLog] = None
    recorder: Optional[CallRecorder] = None
    result: Optional[Dict[str, Any]] = None
    failure_code: Optional[str] = None
    event_log_complete = False

    try:
        event_log = EventLog(output, run_id)
        effective_transport = (
            transport if transport is not None else jev_adapter._http_post_json
        )
        recorder = CallRecorder(effective_transport, event_log, authorization["max_calls"])
        result, failure_code = _attempt_selection(
            catalog,
            authorization["selected_budget"],
            recorder,
        )
    except OutputError:
        failure_code = "event-log-write-failed"
    finally:
        if event_log is not None:
            try:
                event_log.close()
                event_log_complete = True
            except OSError:
                event_log_complete = False

    completed_at = _utc_now()
    report = _build_report(
        authorization=authorization,
        authorization_sha256=authorization_sha256,
        run_id=run_id,
        started_at=started_at,
        completed_at=completed_at,
        result=result,
        failure_code=failure_code,
        recorder=recorder,
        event_log=event_log,
        event_log_complete=event_log_complete,
    )
    try:
        _exclusive_json_write(output, "report.json", report)
    except OutputError:
        if recorder is not None and recorder.attempted_calls:
            raise PostCallEvidenceError(report) from None
        raise
    finally:
        output.close()
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one fail-closed, operator-authorized TypeSafe Jev selector measurement."
    )
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def main(argv=None, environ=None) -> int:
    """CLI gate; default/offline invocation never probes adapter availability."""
    environment = os.environ if environ is None else environ
    args = _parser().parse_args(argv)
    if environment.get(REAL_RUN_ENV) != "1":
        print(
            "REFUSED: explicit " + REAL_RUN_ENV + "=1 is required; "
            "no availability probe or network attempt was made",
            file=sys.stderr,
        )
        return 2

    try:
        authorization, authorization_sha256 = load_authorization(args.authorization)
    except (AuthorizationError, OutputError):
        print(
            "REFUSED: authorization record is missing, malformed, or unauthorized; "
            "no availability probe or network attempt was made",
            file=sys.stderr,
        )
        return 2

    try:
        report = execute_measurement(
            authorization,
            authorization_sha256,
            args.output_dir,
        )
    except PostCallEvidenceError as error:
        attempted = error.report["attempts"]["attempted_calls"]
        print(
            "INCOMPLETE/UNKNOWN: final report write failed after "
            f"{attempted} attempted adapter call(s); preserve partial events and "
            "do not automatically rerun",
            file=sys.stderr,
        )
        return 4
    except (MeasurementRefused, OutputError):
        print(
            "REFUSED: measurement output could not be prepared safely; "
            "no adapter call was made",
            file=sys.stderr,
        )
        return 2
    print(json.dumps({
        "run_id": report["run_id"],
        "status": report["status"],
        "report": str((args.output_dir / "report.json").resolve()),
        "next_action": report["next_action"],
    }, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "complete" else 4


if __name__ == "__main__":
    raise SystemExit(main())
