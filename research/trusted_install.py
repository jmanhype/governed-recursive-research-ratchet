"""Verify root-controlled executable closure; never execute Homebrew QEMU."""
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
from common import canonical, digest, fields, identifier, require, unique_fields


def absolute_dependencies(root, dependencies, rpaths, members):
    """No loader search is approved: require exact normalized absolute closure."""
    require(not rpaths, 'IntegrityFailure', 'LC_RPATH search is forbidden')
    for name in dependencies:
        path = Path(name)
        require(path.is_absolute() and str(path) == name and '..' not in path.parts,
                'IntegrityFailure', 'Dependency must be normalized and absolute')
        if name.startswith(('/usr/lib/', '/System/Library/')):
            continue  # Sealed OS cache, bound separately to system_build.
        require(name.startswith(str(root) + '/') and str(path.relative_to(root)) in members,
                'IntegrityFailure', 'Absolute dependency absent from immutable closure')


def immutable(path: Path, *, directory=False):
    require(path.is_absolute() and '..' not in path.parts, 'Unauthorized', 'Absolute normalized path required')
    for ancestor in reversed((path, *path.parents)):
        info = ancestor.lstat()
        require(not stat.S_ISLNK(info.st_mode) and info.st_uid == 0 and info.st_mode & 0o022 == 0,
                'Unauthorized', 'Mutable executable/configuration ancestor')
        # macOS ACL grants are independent of POSIX mode bits.
        output = subprocess.run(['/bin/ls', '-lde', str(ancestor)], capture_output=True,
                                check=True, timeout=2, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
        require(b'+' not in output.split(None, 1)[0], 'Unauthorized', 'ACL-bearing protected path')
    info = path.lstat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
            'Unauthorized', 'Protected path type differs')
    if not directory:
        require(info.st_nlink == 1 and info.st_mode & 0o222 == 0,
                'Unauthorized', 'Protected file must be single-link read-only')


def record(path: Path):
    immutable(path)
    require(path.stat().st_size <= 1048576, 'InvalidInput', 'Protected record too large')
    return json.loads(path.read_bytes(), object_pairs_hook=unique_fields)


def macho_loads(raw: bytes):
    """Read load commands without invoking either the executable or a toolchain."""
    require(len(raw) >= 32 and raw[:4] == b'\xcf\xfa\xed\xfe',
            'IntegrityFailure', 'Only reviewed thin little-endian Mach-O64 supported')
    count, size = struct.unpack_from('<II', raw, 16)
    require(count <= 4096 and 32 + size <= len(raw), 'IntegrityFailure', 'Invalid Mach-O header')
    cursor, dependencies, rpaths = 32, [], []
    for _ in range(count):
        require(cursor + 8 <= 32 + size, 'IntegrityFailure', 'Truncated load command')
        command, length = struct.unpack_from('<II', raw, cursor)
        require(length >= 8 and cursor + length <= 32 + size, 'IntegrityFailure', 'Invalid load command')
        require(command != 0x27, 'IntegrityFailure', 'Embedded dyld environment is forbidden')
        if command == 0xe:
            require(length >= 12, 'IntegrityFailure', 'Invalid dynamic linker command')
            offset = struct.unpack_from('<I', raw, cursor + 8)[0]
            require(12 <= offset < length and raw[cursor + offset:cursor + length].split(b'\0', 1)[0]
                    == b'/usr/lib/dyld', 'IntegrityFailure', 'Unreviewed dynamic linker')
        if command in (0xc, 0x80000018, 0x8000001f, 0x80000023, 0x20, 0x8000001c):
            require(length >= 12, 'IntegrityFailure', 'Invalid library command')
            offset = struct.unpack_from('<I', raw, cursor + 8)[0]
            require(12 <= offset < length, 'IntegrityFailure', 'Invalid library name offset')
            encoded = raw[cursor + offset:cursor + length]
            require(b'\0' in encoded, 'IntegrityFailure', 'Unterminated library path')
            name = encoded.split(b'\0', 1)[0].decode('utf-8')
            (rpaths if command == 0x8000001c else dependencies).append(name)
        cursor += length
    require(cursor == 32 + size, 'IntegrityFailure', 'Unexpected Mach-O command bytes')
    return dependencies, rpaths


def verify_qemu(manifest: dict):
    fields(manifest, {'version', 'root', 'executable', 'files', 'system_build', 'review_reference',
                      'build_record_sha256', 'data_files'})
    require(type(manifest['version']) is int and manifest['version'] == 1,
            'InvalidInput', 'Installation manifest version differs')
    identifier(manifest['review_reference'], True)
    root = Path(manifest['root'])
    require(root.parent == Path('/Library/GRRR') and root.name.startswith('qemu-'),
            'Unauthorized', 'QEMU requires independent protected installation')
    immutable(root, directory=True)
    build = record(root / 'build-record.json')
    require(digest(canonical(build)) == manifest['build_record_sha256'],
            'IntegrityFailure', 'Reviewed build provenance differs')
    fields(build, {'source_sha256', 'executable_sha256', 'configure', 'review_reference', 'version'})
    identifier(build['source_sha256'], True)
    identifier(build['review_reference'], True)
    require(build['version'] == '11.1.2' and isinstance(build['configure'], list) and
            all(value in build['configure'] for value in ('--disable-modules', '--disable-plugins', '--prefix=' + str(root))),
            'IntegrityFailure', 'Immutable installation must disable external module/plugin search')
    require(isinstance(manifest['files'], dict) and 0 < len(manifest['files']) <= 256,
            'InvalidInput', 'Invalid dependency inventory')
    data = {}
    for relative, hashed in manifest['files'].items():
        path = Path(relative)
        require(not path.is_absolute() and '..' not in path.parts, 'InvalidInput', 'Unsafe installation member')
        identifier(hashed, True)
        immutable(root / path)
        raw = (root / path).read_bytes()
        require(digest(raw) == hashed, 'IntegrityFailure', 'Immutable installation bytes changed')
        data[relative] = raw
    require(manifest['executable'] in data, 'IntegrityFailure', 'Executable missing from closure')
    require(digest(data[manifest['executable']]) == build['executable_sha256'],
            'IntegrityFailure', 'Build record does not bind installed executable')
    immutable(root / 'data', directory=True)
    require(isinstance(manifest['data_files'], dict) and len(manifest['data_files']) <= 256,
            'IntegrityFailure', 'Invalid fixed QEMU data inventory')
    for relative, expected in manifest['data_files'].items():
        path = Path(relative)
        require(not path.is_absolute() and '..' not in path.parts, 'IntegrityFailure', 'Unsafe QEMU data path')
        immutable(root / 'data' / path)
        require(digest((root / 'data' / path).read_bytes()) == expected,
                'IntegrityFailure', 'QEMU firmware/data bytes changed')
    data_members = list((root / 'data').rglob('*'))
    require(len(data_members) <= 512 and all(not p.is_symlink() for p in data_members),
            'IntegrityFailure', 'Unbounded or symlinked QEMU data tree')
    for member in data_members:
        if member.is_dir():
            immutable(member, directory=True)
    require({str(p.relative_to(root / 'data')) for p in data_members if not p.is_dir()}
            == set(manifest['data_files']), 'IntegrityFailure', 'Uninventoried QEMU data member')
    actual_build = subprocess.run(['/usr/bin/sw_vers', '-buildVersion'], capture_output=True,
        check=True, timeout=2, env={'PATH': '/usr/bin:/bin'}).stdout.decode().strip()
    require(actual_build == manifest['system_build'], 'StaleBinding', 'Sealed system dependency build changed')
    for relative, raw in data.items():
        dependencies, rpaths = macho_loads(raw)
        absolute_dependencies(root, dependencies, rpaths, data)
    return root / manifest['executable']
