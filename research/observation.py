"""Strict data validation, not an authority upgrade for the legacy root guest.

Candidate text is never evaluated, imported, executed or interpreted as a verdict.
The legacy command output may establish its bounded synthetic assertion only.
Race/locking observation remains blocked until a separate profile is approved.
"""
import math
import os
from pathlib import Path
import stat
from common import Failure, canonical, digest, fields, identifier, require

MAX_OUTPUT = 1048576


def bounded_hex(value: object, maximum: int = MAX_OUTPUT) -> bytes:
    """Decode a strictly bounded byte representation without lossy repair."""
    require(isinstance(value, str) and len(value) <= maximum * 2 and len(value) % 2 == 0,
            'InvalidInput', 'Malformed or oversized observation')
    try:
        result = bytes.fromhex(value)
    except ValueError as exc:
        raise Failure('InvalidInput', 'Nonhex observation') from exc
    require(result.hex() == value, 'InvalidInput', 'Noncanonical hex observation')
    return result


def regular_artifact(root: Path, name: str, maximum: int = MAX_OUTPUT) -> bytes:
    """Read opaque artifacts by descriptor; reject links, devices and traversal."""
    identifier(name, True)
    require(not root.is_symlink(), 'InvalidInput', 'Artifact root symlink')
    directory = os.open(root, os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY)
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        with os.fdopen(descriptor, 'rb') as stream:
            info = os.fstat(stream.fileno())
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                    and not info.st_mode & 0o111 and info.st_size <= maximum,
                    'InvalidInput', 'Artifact is linked, executable, nonregular or oversized')
            data = stream.read(maximum + 1)
            require(len(data) <= maximum and digest(data) == name,
                    'IntegrityFailure', 'Artifact bytes do not bind digest')
            return data
    except OSError as exc:
        raise Failure('InvalidInput', 'Artifact unavailable or symlink') from exc
    finally:
        os.close(directory)


def validate_observation(value: dict, run: str) -> dict:
    """Validate the exact legacy executor envelope before touching its fields."""
    fields(value, {'run', 'command', 'qemu_version', 'assets', 'assets_unchanged',
                   'observation', 'exit_code', 'raw', 'isolation', 'termination',
                   'seconds', 'error', 'transport_complete', 'isolation_verified'})
    require(value['run'] == identifier(run), 'StaleBinding', 'Observation run mismatch')
    require(isinstance(value['command'], list) and len(value['command']) <= 40
            and all(isinstance(v, str) and len(v) <= 1024 for v in value['command']),
            'InvalidInput', 'Malformed command metadata')
    require(isinstance(value['qemu_version'], str) and len(value['qemu_version']) <= 200,
            'InvalidInput', 'Malformed version metadata')
    fields(value['assets'], {'alpine-virt-3.22.6-aarch64.iso', 'vmlinuz-virt', 'initramfs-virt'})
    for hashed in value['assets'].values():
        identifier(hashed, True)
    for key in ('assets_unchanged', 'transport_complete', 'isolation_verified'):
        require(type(value[key]) is bool, 'InvalidInput', 'Malformed observation flag')
    for key in ('observation', 'raw', 'isolation'):
        bounded_hex(value[key])
    require(value['exit_code'] is None or type(value['exit_code']) is int
            and 0 <= value['exit_code'] <= 255, 'InvalidInput', 'Invalid exit status')
    require(type(value['seconds']) in (float, int) and math.isfinite(value['seconds'])
            and 0 <= value['seconds'] <= 310, 'InvalidInput', 'Unknown execution usage')
    fields(value['termination'], {'run', 'ceased', 'seconds', 'fenced'})
    termination = value['termination']
    require(termination['run'] == run and type(termination['ceased']) is bool
            and termination['fenced'] is True and type(termination['seconds']) in (float, int)
            and math.isfinite(termination['seconds']) and 0 <= termination['seconds'] <= 8,
            'InvalidInput', 'Malformed termination observation')
    if value['error'] is not None:
        fields(value['error'], {'code', 'message', 'operation', 'retryable', 'receipt'})
        require(value['error']['code'] in ('Stopped', 'Unavailable', 'GateBlocked', 'RecoveryRequired')
                and isinstance(value['error']['message'], str) and len(value['error']['message']) <= 1024
                and value['error']['retryable'] is False,
                'InvalidInput', 'Unknown execution error')
    require(value['transport_complete'] == (value['error'] is None)
            and (not value['transport_complete'] or value['exit_code'] is not None),
            'InvalidInput', 'Incomplete observation marked complete')
    return value


def gate(value: dict) -> dict:
    """Fail malformed/incomplete output; never promote root guest logs to trust."""
    evidence = digest(canonical(value))
    return {'state': 'fail' if not value.get('transport_complete') else 'not-run',
            'evidence': evidence,
            'reason': 'candidate-inaccessible supervisor profile requires approval and real guest proof'}
