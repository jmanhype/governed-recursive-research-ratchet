"""Open-only installation boundary. Production authority is NOT available.

Private fixture reads enforce actual descriptor metadata/ACLs and copy bytes;
they never establish immutable topology, reviewed runtime closure or provenance.
No flag, descriptor hash, chmod, same-UID recheck or advisory lock can turn this
fixture facility into installed authority. Production needs a separately
authorized and qualified protected installer/exclusion/provenance boundary.
"""
import ctypes
import errno
import os
import stat
import sys
from types import MappingProxyType

from common import Failure, digest, require
from capstone_installation_inventory import (
    _fixture_root, _safe_relative_path, _read_file, validate_inventory,
    encode_inventory, MAX_NODES, MAX_INVENTORY_BYTES, RESERVED_UIDS,
)


def open_installed(role):
    """Fail BEFORE metadata access; there is no runtime enable switch.

    Role is not caller identity. No installation/provisioning, filesystem
    probe, schema creation/upgrade, environment override or fallback occurs.
    """
    raise Failure('Unavailable', 'Protected installation boundary is not qualified')


def _empty_acl(fd):
    """Inspect the actual opened Darwin inode; unknown ACLs fail closed.

    Conservatively reject ALL extended entries, including benign deny entries.
    This is not the production IPC ACL policy. Never use path-based ls/chmod.
    """
    require(sys.platform == 'darwin', 'Unavailable', 'Darwin ACL inspection required')
    libc = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    libc.acl_get_fd_np.argtypes = (ctypes.c_int, ctypes.c_int)
    libc.acl_get_fd_np.restype = ctypes.c_void_p
    libc.acl_to_text.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ssize_t))
    libc.acl_to_text.restype = ctypes.c_void_p
    libc.acl_free.argtypes = (ctypes.c_void_p,)
    libc.acl_free.restype = ctypes.c_int
    acl = libc.acl_get_fd_np(fd, 0x100)  # Darwin ACL_TYPE_EXTENDED
    if not acl and ctypes.get_errno() == errno.ENOENT:
        # Darwin reports a missing extended ACL with ENOENT even for an
        # existing opened inode. This is an FD-only call, never a pathname
        # ENOENT fallback. Confirm the descriptor still denotes a linked inode.
        require(os.fstat(fd).st_nlink > 0, 'Unavailable', 'Descriptor is unlinked')
        return
    require(bool(acl), 'Unavailable',
            'Descriptor ACL cannot be inspected (errno=%d)' % ctypes.get_errno())
    text = None
    try:
        length = ctypes.c_ssize_t()
        text = libc.acl_to_text(acl, ctypes.byref(length))
        require(bool(text) and 0 <= length.value <= 65536,
                'Unavailable', 'Descriptor ACL cannot be decoded')
        raw = ctypes.string_at(text, length.value)
        require(raw == b'!#acl 1\n', 'Unauthorized', 'Extended ACL is not empty')
    finally:
        if text:
            libc.acl_free(text)
        libc.acl_free(acl)


def _open(name, parent=None):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
    try:
        return os.open(name, flags, dir_fd=parent)
    except OSError as exc:
        raise Failure('Unavailable', 'No-follow installation fixture access refused') from exc


def _check(fd, *, uid, directory, mode):
    info = os.fstat(fd)
    kind = stat.S_ISDIR if directory else stat.S_ISREG
    require(kind(info.st_mode) and info.st_uid == uid
            and stat.S_IMODE(info.st_mode) == mode,
            'Unauthorized', 'Descriptor kind, actual owner or mode differs')
    if not directory:
        require(info.st_nlink == 1, 'Unauthorized', 'Fixture file has alternate hard links')
    _empty_acl(fd)
    return info


def open_public_fixture(root, records):
    """Capture immutable *copies* under a validated private temporary root.

    root/private ancestors must actually be root-owned, non-writable, no-ACL
    directories; /private/tmp must be root-owned 01777/no-ACL. Sticky tmp plus
    actual caller-owned 0700 root exclude other ordinary UIDs, NOT same-UID
    writers, root or privileged operators. Return values are NONPRODUCTION
    data only, checked against a caller inventory, never trusted provenance.
    Source names are not safe to reopen; consume only returned contents.
    """
    _, name = _fixture_root(root)  # lexical guard before ANY metadata
    expected = validate_inventory(records)
    uid = os.getuid()
    require(uid == os.geteuid() and uid not in RESERVED_UIDS,
            'Unauthorized', 'Actual unprivileged non-setuid fixture caller required')
    files = {item['relative_path']: item for item in expected}
    directories = set()
    for path in files:
        parts = path.split('/')
        directories.update('/'.join(parts[:i]) for i in range(1, len(parts)))
    contents, seen_dirs = {}, set()
    total, nodes = 0, 0

    def visit(fd, prefix):
        nonlocal total, nodes
        _check(fd, uid=uid, directory=True, mode=0o700)
        names = os.listdir(fd)
        require(len(names) <= MAX_NODES, 'InvalidInput', 'Fixture entry limit exceeded')
        for entry in sorted(names):
            _safe_relative_path(entry)
            nodes += 1
            require(nodes <= MAX_NODES, 'InvalidInput', 'Fixture node limit exceeded')
            path = prefix + '/' + entry if prefix else entry
            require(path in directories or path in files, 'IntegrityFailure',
                    'Unexpected fixture entry')
            child = _open(entry, fd)
            try:
                if path in directories:
                    seen_dirs.add(path)
                    visit(child, path)
                else:
                    before = _check(child, uid=uid, directory=False, mode=0o444)
                    data, size = _read_file(child, before, MAX_INVENTORY_BYTES - total)
                    require(digest(data) == files[path]['sha256'], 'IntegrityFailure',
                            'Fixture content hash differs')
                    _check(child, uid=uid, directory=False, mode=0o444)
                    total += size
                    contents[path] = data
            finally:
                os.close(child)

    fds = []
    try:
        fds.append(_open('/'))
        for component, mode in ((None, 0o755), ('private', 0o755), ('tmp', 0o1777)):
            if component:
                fds.append(_open(component, fds[-1]))
            info = _check(fds[-1], uid=0, directory=True, mode=mode)
            require(info.st_gid == 0, 'Unauthorized', 'Ancestor group is not wheel')
        fds.append(_open(name, fds[-1]))
        visit(fds[-1], '')
        require(set(contents) == set(files) and seen_dirs == directories,
                'IntegrityFailure', 'Fixture inventory is incomplete')
        raw, hashed = encode_inventory(expected)
        return MappingProxyType(dict(environment='NONPRODUCTION',
            assurance='DETACHED_FIXTURE_BYTES_ONLY', stable_installation=False,
            trusted_provenance=False, actual_uid=uid,
            inventory_raw=raw, inventory_sha256=hashed,
            contents=MappingProxyType(contents)))
    except OSError as exc:
        raise Failure('Unavailable', 'Fixture filesystem inspection failed') from exc
    finally:
        pending = sys.exc_info()[0] is not None
        close_error = None
        for fd in reversed(fds):
            try:
                os.close(fd)
            except OSError as exc:
                # Do not retry close: the descriptor number may have been
                # released and reused even when close reported an error.
                close_error = close_error or exc
        if close_error is not None and not pending:
            raise Failure('Unavailable', 'Fixture descriptor cleanup failed') from close_error
