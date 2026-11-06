"""Canonical installation inventories and a private-temp fixture verifier.

This module is deliberately data/mechanics only. It has no installed
installation factory, production UID/ACL claim, authority resolver, enrollment
surface, or effect. The fixture verifier accepts only actual-UID-owned
``/private/tmp/grrr-backend-fixture-*`` trees and regular files with the base
design's required file mode 0444 (not an immutability boundary). Production directory ownership, ACLs, and
exhaustive runtime-closure selection remain intentionally unresolved here.
"""
import hashlib
import os
import stat
from types import MappingProxyType

from common import Failure, MAX_WIRE, canonical, digest, require


SCHEMA = 'capstone-installation-inventory-v1'
FIXTURE_PREFIX = 'grrr-backend-fixture-'
FIXTURE_FILE_MODE = 0o444
FIXTURE_DIRECTORY_MODE = 0o700
MAX_RECORDS = 256
MAX_NODES = 512
MAX_INVENTORY_BYTES = 1024 * 1024
RECORD_FIELDS = frozenset(('relative_path', 'mode', 'sha256'))
RESERVED_UIDS = (0, 320, 321, 322)
_OPEN_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
_PATH_CHARS = frozenset(chr(value) for value in range(32, 127))


def _safe_relative_path(value):
    """Return an exact safe ASCII relative path without metadata access."""
    require(type(value) is str and 0 < len(value) <= 4096 and value.isascii(),
            'InvalidInput', 'Inventory path is not bounded ASCII text')
    require(all(character in _PATH_CHARS for character in value),
            'InvalidInput', 'Inventory path has unsafe characters')
    require('\\' not in value, 'InvalidInput', 'Inventory path has a backslash')
    components = value.split('/')
    require(all(component and component not in ('.', '..') for component in components),
            'InvalidInput', 'Inventory path is not a canonical relative path')
    require(all(len(component) <= 255 for component in components),
            'InvalidInput', 'Inventory path component is too long')
    return value


def _protected_absolute(value):
    return value == '/Library/GRRR' or value.startswith('/Library/GRRR/')


def _fixture_root(root):
    """Lexically constrain a fixture root before any filesystem syscall."""
    require(type(root) is str and 0 < len(root) <= 4096 and root.isascii(),
            'InvalidInput', 'Fixture root is not bounded ASCII text')
    require(all(character in _PATH_CHARS for character in root),
            'InvalidInput', 'Fixture root has unsafe characters')
    require('\\' not in root, 'InvalidInput', 'Fixture root has a backslash')
    require(not _protected_absolute(root), 'Unauthorized', 'Protected installation path')
    components = root.split('/')
    require(len(components) == 4 and components[:3] == ['', 'private', 'tmp']
            and components[3].startswith(FIXTURE_PREFIX) and components[3] not in ('.', '..'),
            'InvalidInput', 'Fixture root is not directly parented by /private/tmp')
    return root, components[3]


def validate_inventory(records):
    """Validate exact sorted unique records and return detached copies.

    Ordering is by the exact relative path. The only mode accepted here is the
    base design's required regular-file mode 0444; ambiguous alternatives are
    rejected rather than interpreted.
    """
    require(type(records) is list and 0 < len(records) <= MAX_RECORDS,
            'InvalidInput', 'Inventory record count differs')
    normalized, paths = [], set()
    for record in records:
        require(type(record) is dict and set(record) == RECORD_FIELDS,
                'InvalidInput', 'Inventory record fields differ')
        path = _safe_relative_path(record['relative_path'])
        require(path not in paths, 'InvalidInput', 'Inventory paths are not unique')
        require(type(record['mode']) is int and record['mode'] == FIXTURE_FILE_MODE,
                'InvalidInput', 'Inventory file mode differs')
        value = record['sha256']
        require(type(value) is str and len(value) == 64 and value.isascii()
                and all(character in '0123456789abcdef' for character in value),
                'InvalidInput', 'Inventory SHA-256 differs')
        paths.add(path)
        normalized.append(dict(relative_path=path, mode=FIXTURE_FILE_MODE, sha256=value))
    require([record['relative_path'] for record in normalized]
            == sorted(record['relative_path'] for record in normalized),
            'InvalidInput', 'Inventory records are not canonically sorted')
    require(len(canonical(normalized)) <= MAX_WIRE,
            'InvalidInput', 'Inventory canonical bytes exceed bound')
    return normalized


def encode_inventory(records):
    """Return exact canonical inventory bytes and their SHA-256."""
    normalized = validate_inventory(records)
    raw = canonical(normalized)
    return raw, digest(raw)


def inventory_sha256(records):
    return encode_inventory(records)[1]


def _open(name, directory=None):
    flags = _OPEN_FLAGS
    try:
        if directory is None:
            return os.open(name, flags)
        return os.open(name, flags, dir_fd=directory)
    except OSError as exc:
        raise Failure('Unavailable', 'No-follow fixture access refused') from exc


def _fstat(descriptor):
    try:
        return os.fstat(descriptor)
    except OSError as exc:
        raise Failure('Unavailable', 'Fixture identity unavailable') from exc


def _close(descriptor):
    try:
        os.close(descriptor)
    except OSError:
        pass


def _fixture_fd(root, name):
    """Open root and every ancestor without following a symlink."""
    current = _open('/')
    try:
        for component in ('private', 'tmp', name):
            child = _open(component, current)
            _close(current)
            current = child
            info = _fstat(current)
            require(stat.S_ISDIR(info.st_mode), 'IntegrityFailure',
                    'Fixture ancestor is not a directory')
        return current
    except BaseException:
        _close(current)
        raise


def _read_file(descriptor, before, remaining):
    require(before.st_size >= 0 and before.st_size <= remaining,
            'InvalidInput', 'Inventory content size exceeds bound')
    data = bytearray()
    try:
        while len(data) < before.st_size:
            chunk = os.read(descriptor, min(65536, before.st_size - len(data)))
            require(bool(chunk), 'IntegrityFailure', 'Fixture file changed while reading')
            data.extend(chunk)
        require(os.read(descriptor, 1) == b'', 'IntegrityFailure',
                'Fixture file grew while reading')
    except OSError as exc:
        raise Failure('Unavailable', 'Fixture file read failed') from exc
    after = _fstat(descriptor)
    identity = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_uid', 'st_size')
    require(all(getattr(before, name) == getattr(after, name) for name in identity),
            'IntegrityFailure', 'Fixture file identity changed while reading')
    return bytes(data), before.st_size


def _identity(info):
    names = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_uid', 'st_size')
    return tuple(getattr(info, name) for name in names)


def _list_directory(descriptor):
    try:
        names = os.listdir(descriptor)
    except OSError as exc:
        raise Failure('Unavailable', 'Fixture directory listing failed') from exc
    require(len(names) <= MAX_RECORDS and all(type(entry) is str for entry in names),
            'InvalidInput', 'Fixture directory entries exceed bounds')
    return tuple(sorted(names))


def _recheck_namespace(directory_fds, directory_names, identities, expected, uid):
    """Diagnose observed changes; never certify namespace stability.

    This is a real second no-follow namespace pass, not a cached snapshot. It
    re-lists every retained directory, re-opens every current entry, compares
    inode identity/metadata, and re-reads regular bytes. A final listing pass
    only adds another observation. A hostile same-UID process may change an
    already-checked entry, or rebind root, during or after any pass. Retaining
    directory descriptors does not freeze their contents or the root binding.
    """
    expected_by_path = {record['relative_path']: record for record in expected}
    for path, descriptor in sorted(directory_fds.items()):
        require(_list_directory(descriptor) == directory_names[path],
                'IntegrityFailure', 'Fixture namespace changed during verification')
        require(_identity(_fstat(descriptor)) == identities[path],
                'IntegrityFailure', 'Fixture directory identity changed during verification')
        for entry in directory_names[path]:
            child = entry if not path else path + '/' + entry
            current = _open(entry, directory=descriptor)
            try:
                before = _fstat(current)
                require(_identity(before) == identities[child],
                        'IntegrityFailure', 'Fixture namespace entry was replaced')
                if stat.S_ISDIR(before.st_mode):
                    require(child in directory_fds, 'IntegrityFailure',
                            'Fixture directory changed during verification')
                    require(before.st_uid == uid and stat.S_IMODE(before.st_mode)
                            == FIXTURE_DIRECTORY_MODE, 'Unauthorized',
                            'Fixture directory owner/mode differs')
                else:
                    record = expected_by_path.get(child)
                    require(record is not None, 'IntegrityFailure',
                            'Fixture namespace changed during verification')
                    require(stat.S_ISREG(before.st_mode), 'IntegrityFailure',
                            'Fixture leaf is not a regular file')
                    require(before.st_uid == uid and stat.S_IMODE(before.st_mode)
                            == FIXTURE_FILE_MODE and before.st_nlink == 1,
                            'Unauthorized', 'Fixture file identity differs')
                    data, _ = _read_file(current, before, MAX_INVENTORY_BYTES)
                    require(hashlib.sha256(data).hexdigest() == record['sha256'],
                            'IntegrityFailure', 'Fixture bytes changed during verification')
            finally:
                _close(current)
    for path, descriptor in sorted(directory_fds.items()):
        require(_list_directory(descriptor) == directory_names[path],
                'IntegrityFailure', 'Fixture namespace changed during recheck')
        require(_identity(_fstat(descriptor)) == identities[path],
                'IntegrityFailure', 'Fixture directory identity changed during recheck')


def open_public_fixture(root, records, *, require_stable_installation=False):
    """Capture bounded detached fixture bytes; explicit NONPRODUCTION only.

    The input is not installed and never becomes authority. All traversal is
    performed from retained no-follow directory descriptors; every directory
    and regular leaf must be owned by the actual unprivileged invoking UID.
    Exact expected topology, bytes, mode, link count, and SHA-256 are checked.
    Successful return certifies ONLY the returned immutable byte copies against
    the caller's inventory. Consume ``contents``, never reopen the source paths.
    It does not certify a simultaneous filesystem snapshot or stable namespace:
    a same-UID writer can replace any name, including root, after a recheck.

    Stable installation authority requires a trusted exclusion or immutable
    snapshot boundary extending through consumption. This fixture implementation
    has neither and therefore rejects that request before filesystem access.
    A caller assertion, 0444 mode, advisory lock, or further recheck cannot grant
    that authority. No caller-supplied capability enables it here.
    """
    require(type(require_stable_installation) is bool, 'InvalidInput',
            'Stable installation request must be boolean')
    require(not require_stable_installation, 'Unavailable',
            'Stable installation authority requires an effective trusted boundary')
    root, name = _fixture_root(root)
    expected = validate_inventory(records)
    uid = os.getuid()
    require(uid not in RESERVED_UIDS, 'Unauthorized', 'Actual unprivileged fixture UID required')
    expected_paths = {record['relative_path'] for record in expected}
    expected_directories = set()
    for path in expected_paths:
        components = path.split('/')
        for depth in range(1, len(components)):
            expected_directories.add('/'.join(components[:depth]))
    root_fd = _fixture_fd(root, name)
    actual, total, nodes = [], 0, 1
    contents = {}
    directory_fds, directory_names, identities = {}, {}, {}

    def visit(directory, prefix):
        nonlocal total, nodes
        directory_names[prefix] = _list_directory(directory)
        for entry in directory_names[prefix]:
            nodes += 1
            require(nodes <= MAX_NODES, 'InvalidInput', 'Fixture node count exceeds bound')
            try:
                _safe_relative_path(entry)
            except Failure:
                raise Failure('InvalidInput', 'Fixture directory entry is unsafe') from None
            child = entry if not prefix else prefix + '/' + entry
            descriptor = _open(entry, directory=directory)
            try:
                before = _fstat(descriptor)
                identities[child] = _identity(before)
                if stat.S_ISDIR(before.st_mode):
                    require(child in expected_directories, 'InvalidInput',
                            'Fixture has extra directory topology')
                    require(before.st_uid == uid and stat.S_IMODE(before.st_mode)
                            == FIXTURE_DIRECTORY_MODE, 'Unauthorized',
                            'Fixture directory owner/mode differs')
                    directory_fds[child] = descriptor
                    visit(descriptor, child)
                    descriptor = None
                else:
                    require(child in expected_paths, 'InvalidInput', 'Fixture has extra files')
                    require(stat.S_ISREG(before.st_mode), 'IntegrityFailure',
                            'Fixture leaf is not a regular file')
                    require(before.st_uid == uid and stat.S_IMODE(before.st_mode)
                            == FIXTURE_FILE_MODE and before.st_nlink == 1,
                            'Unauthorized', 'Fixture file identity differs')
                    data, consumed = _read_file(descriptor, before, MAX_INVENTORY_BYTES - total)
                    total += consumed
                    contents[child] = data
                    actual.append(dict(relative_path=child, mode=FIXTURE_FILE_MODE,
                                       sha256=hashlib.sha256(data).hexdigest()))
            finally:
                if descriptor is not None:
                    _close(descriptor)

    try:
        root_info = _fstat(root_fd)
        require(stat.S_ISDIR(root_info.st_mode) and root_info.st_uid == uid
                and stat.S_IMODE(root_info.st_mode) == FIXTURE_DIRECTORY_MODE,
                'Unauthorized', 'Fixture root is not actual-UID private')
        directory_fds[''], identities[''] = root_fd, _identity(root_info)
        visit(root_fd, '')
        actual.sort(key=lambda record: record['relative_path'])
        missing = [record for record in expected if record not in actual]
        extra = [record for record in actual if record not in expected]
        require(not missing and not extra, 'IntegrityFailure',
                'Fixture inventory has missing, extra, or changed records')
        require([record['relative_path'] for record in actual]
                == sorted(record['relative_path'] for record in actual),
                'IntegrityFailure', 'Actual fixture traversal is not canonical')
        raw, hashed = encode_inventory(expected)
        _recheck_namespace(directory_fds, directory_names, identities, expected, uid)
        return dict(schema=SCHEMA, environment='NONPRODUCTION', actual_uid=uid,
                    assurance='DETACHED_FIXTURE_BYTES_ONLY', stable_installation=False,
                    contents=MappingProxyType(contents),
                    inventory_raw=raw, inventory_sha256=hashed,
                    records=[dict(record) for record in expected])
    finally:
        for descriptor in directory_fds.values():
            _close(descriptor)
