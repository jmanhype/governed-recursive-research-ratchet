"""Offline baseline preparation contracts; never execute downloaded source on host.

This profile is deliberately distinct from the registered synthetic-only policy.
Validation is not registration, authorization, license clearance, or a VM receipt.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import tarfile
from common import Failure, canonical, digest, fields, identifier, require
from policy import LIMITS

SOURCE_COMMIT = '129e0b3f15a3bd6af949ee47d76f6855c582ab73'
LICENSE_BLOB = 'c004659349c7a1f6c55e5107b53a0766085e8d2e'
TOOLCHAIN = 'go1.26.10.linux-arm64.tar.gz'
TOOLCHAIN_SHA256 = '3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797'
PERMISSIVE = frozenset(('MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC'))


def git(source: Path, *args: str) -> bytes:
    """Read Git objects without running source hooks or build tooling."""
    result = subprocess.run(['git', '-C', str(source), *args], check=True,
                            capture_output=True, timeout=30,
                            env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty',
                                 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'})
    return result.stdout


def source_inventory(source: Path) -> dict:
    """Verify every tracked byte against the pinned Git object; reject extras."""
    require(git(source, 'rev-parse', 'HEAD').decode().strip() == SOURCE_COMMIT,
            'StaleBinding', 'Source commit differs')
    require(git(source, 'status', '--porcelain', '--untracked-files=all') == b'',
            'IntegrityFailure', 'Source working tree is not clean')
    require(git(source, 'rev-parse', 'HEAD:LICENSE').decode().strip() == LICENSE_BLOB,
            'IntegrityFailure', 'License blob differs')
    inventory = {}
    for entry in git(source, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0'):
        if not entry:
            continue
        header, raw_name = entry.split(b'\t', 1)
        mode, kind, object_id = header.decode().split()
        name = raw_name.decode('utf-8')
        require(kind == 'blob' and mode in ('100644', '100755'),
                'GateBlocked', 'Symlink or submodule source entry')
        path = source / name
        require(not path.is_symlink() and path.is_file(), 'IntegrityFailure', 'Source file missing')
        require(all(not p.is_symlink() for p in path.parents if p != source.parent),
                'IntegrityFailure', 'Source parent symlink')
        data = path.read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(actual == object_id, 'IntegrityFailure', 'Source byte mismatch: ' + name)
        inventory[name] = {'git_blob': actual, 'sha256': digest(data), 'bytes': len(data), 'mode': mode}
    actual_files = {str(p.relative_to(source)) for p in source.rglob('*')
                    if '.git' not in p.relative_to(source).parts and (p.is_file() or p.is_symlink())}
    require(actual_files == set(inventory), 'IntegrityFailure', 'Untracked/ignored source asset')
    require((source / 'go.mod').read_bytes() == b'module github.com/paivot-ai/vlt\n\ngo 1.26\n',
            'GateBlocked', 'Dependency declaration changed')
    return {'commit': SOURCE_COMMIT, 'license_blob': LICENSE_BLOB,
            'origin': 'https://github.com/paivot-ai/vlt', 'files': inventory,
            'tree_sha256': digest(canonical(inventory)),
            'module_dependencies_declared': [],
            'dependency_resolution': 'not-run; offline go list -deps required',
            'behavior_references': {name: inventory[name] for name in
                                    ('README.md', 'index.go', 'main_test.go', 'e2e_test.go', 'Makefile')}}


def toolchain_inventory(path: Path) -> dict:
    """Inspect verified archive members without extracting or running binaries."""
    require(path.is_file() and not path.is_symlink(), 'Unavailable', 'Pinned toolchain missing')
    require(digest(path.read_bytes()) == TOOLCHAIN_SHA256,
            'IntegrityFailure', 'Pinned toolchain archive differs')
    notices = {}
    members = {}
    with tarfile.open(path, 'r:gz') as archive:
        for member in archive:
            parts = Path(member.name).parts
            require(parts and parts[0] == 'go' and '..' not in parts and not Path(member.name).is_absolute(),
                    'IntegrityFailure', 'Unsafe toolchain archive path')
            require(member.isdir() or member.isfile(), 'GateBlocked', 'Toolchain link/device member')
            require(member.name not in members, 'IntegrityFailure', 'Duplicate toolchain member')
            members[member.name] = {'bytes': member.size, 'mode': member.mode}
            if member.isfile():
                data = archive.extractfile(member).read()
                members[member.name]['sha256'] = digest(data)
                if any(word in Path(member.name).name.upper() for word in ('LICENSE', 'NOTICE', 'COPYING', 'PATENTS')):
                    try:
                        content = {'text': data.decode('utf-8', errors='strict')}
                    except UnicodeDecodeError:
                        content = {'hex': data.hex(), 'review_required': 'Non-UTF8 notice-name match'}
                    notices[member.name] = dict(content, sha256=digest(data))
    require('go/LICENSE' in notices and 'go/bin/go' in members, 'IntegrityFailure', 'Incomplete Go archive')
    return {'version': 'go1.26.10', 'platform': 'linux-arm64', 'sha256': TOOLCHAIN_SHA256,
            'origin': 'https://go.dev/dl/' + TOOLCHAIN, 'members': members,
            'notices': notices, 'license': 'BSD-3-Clause plus bundled third-party notices',
            'compliance': 'unreviewed', 'obligations': 'Preserve all bundled licenses and notices; review every component'}


def proposed_profile(operator: int, inventory_digest: str) -> dict:
    """Produce a proposal, never mutate the registered synthetic dispatch policy."""
    identifier(inventory_digest, True)
    require(type(operator) is int and operator not in (0, 320, 321), 'Unauthorized', 'Separate operator required')
    return {'version': 1, 'profile': 'offline-preflight-v1', 'operator_uid': operator,
            'inventory_sha256': inventory_digest, 'source_commit': SOURCE_COMMIT,
            'limits': dict(LIMITS), 'network': False, 'host_shares': False,
            'paid_dispatch': False, 'toolchain_auto_download': False,
            'build_command_seconds': 240, 'per_invocation_seconds': 300,
            'builds': 2, 'independent_fresh_vms': True,
            'approval': 'required', 'build_timeout_basis': 'proposal only; no offline build measured',
            'read_only_asset_transport': 'detached block image; not a host filesystem mount'}


def compliance_gate(inventory: dict) -> None:
    """Structural validation only; caller must verify evidence in protected ledger.

    Unknown obligations/review decisions cannot become implicit clearance.
    This function neither authenticates referenced receipts nor grants authority.
    """
    fields(inventory, {'components', 'complete', 'unresolved'})
    require(inventory['complete'] is True and inventory['unresolved'] == [],
            'GateBlocked', 'Dependency/license inventory incomplete')
    require(isinstance(inventory['components'], list) and inventory['components'],
            'GateBlocked', 'Empty dependency/license inventory')
    for component in inventory['components']:
        fields(component, {'name', 'version', 'sha256', 'origin', 'license', 'notices',
                           'obligations', 'compliance_evidence', 'separate_review'})
        identifier(component['sha256'], True)
        require(all(component[k] for k in ('name', 'version', 'origin', 'license',
                                           'notices', 'obligations', 'compliance_evidence')),
                'GateBlocked', 'Missing compliance evidence')
        if component['license'] not in PERMISSIVE:
            require(isinstance(component['separate_review'], str), 'GateBlocked', 'Separate license review required')
            identifier(component['separate_review'], True)
        identifier(component['compliance_evidence'], True)


def require_profile_approval(path: Path, proposal: dict) -> dict:
    """Check protected approval binding; this does not enable synthetic dispatch.

The root-mediated launcher must provision this after explicit operator approval.
Its existence alone never establishes license clearance or VM integration proof.
"""
    import json
    require(path.is_file() and not path.is_symlink(), 'GateBlocked', 'Offline profile approval absent')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(info.st_uid == 0 and info.st_mode & 0o222 == 0,
                'Unauthorized', 'Approval must be root-owned and read-only')
        require(info.st_size <= 8192, 'InvalidInput', 'Approval record too large')
        raw = stream.read(8193)
        require(len(raw) <= 8192, 'InvalidInput', 'Approval record too large')
    approval = json.loads(raw)
    fields(approval, {'version', 'profile_sha256', 'operator_uid', 'decision', 'authorization_reference'})
    require(approval['version'] == 1 and approval['decision'] == 'approved'
            and approval['operator_uid'] == proposal['operator_uid']
            and approval['profile_sha256'] == digest(canonical(proposal)),
            'StaleBinding', 'Approval does not bind exact offline profile')
    identifier(approval['authorization_reference'], True)
    return approval
