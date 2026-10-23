"""Read-only replay prerequisite validation. Never provisions or dispatches a guest.

Checkout validation is evidence about bytes only, not privileged authority.
Protected preflight must be repeated under the future reviewed parent lock.
"""
import fcntl
import json
import os
from pathlib import Path
import pwd
import shutil
import stat
import subprocess

from common import Failure, canonical, digest, require, unique_fields
from corpus_execution import CORPUS_FREEZE, PRESERVED, PRESERVED_ROOT
from execution import ASSETS
from trusted_execution import QEMU_MANIFEST, QEMU_EXECUTABLE, QEMU_EXECUTABLE_PATH, protected_bytes
from trusted_install import immutable, record, verify_qemu
from validated_corpus import CORPUS_VERSION, SOURCE_ARCHIVE, SOURCE_COMMIT

POLICY_SHA256 = '355e6f7d9dd0a65817cdc1a6421fba6347f5075c40f4a456ed601e753f14a77a'
MANIFEST_SHA256 = '32fb59c74ea96653c50e3deea0d66474bafdd78caf96c3e9c4c589aba703e354'
REPLAY_ROOT = Path('/Library/GRRR/independent-replay')
LOCK = Path('/Library/GRRR/validated-corpus/v2-launch.lock')


def validate_policy(raw: bytes) -> dict:
    """Require the exact approved canonical policy; reject coercions and additions."""
    require(len(raw) <= 16384 and digest(raw) == POLICY_SHA256,
            'GateBlocked', 'Replay policy differs from operator-approved record')
    value = json.loads(raw, object_pairs_hook=unique_fields)
    require(raw == canonical(value) + b'\n', 'GateBlocked', 'Noncanonical replay policy')
    return value


def inspect_corpus(root: Path, protected: bool = False) -> dict:
    """Validate all frozen corpus/spec bytes, without executing source or probes."""
    def read(name: str, expected: str) -> bytes:
        path = root / name
        if protected:
            immutable(path)
            return protected_bytes(path, expected)
        require(not path.is_symlink() and path.is_file(), 'GateBlocked', 'Unsafe corpus member')
        raw = path.read_bytes()
        require(digest(raw) == expected, 'IntegrityFailure', 'Corpus bytes differ')
        return raw

    manifest = json.loads(read('manifest.json', MANIFEST_SHA256), object_pairs_hook=unique_fields)
    require(manifest['corpus_version'] == CORPUS_VERSION
            and manifest['freeze_digest'] == CORPUS_FREEZE
            and manifest['source']['commit'] == SOURCE_COMMIT
            and manifest['source']['archive_sha256'] == SOURCE_ARCHIVE,
            'IntegrityFailure', 'Replay source/corpus binding differs')
    frozen = {k: v for k, v in manifest.items() if k != 'freeze_digest'}
    require(digest(canonical(frozen)) == CORPUS_FREEZE, 'IntegrityFailure', 'Freeze differs')
    for name, expected in manifest['artifacts'].items():
        read(name, expected)
    return {'manifest': MANIFEST_SHA256, 'freeze': CORPUS_FREEZE,
            'spec': manifest['artifacts']['spec-map.json'], 'source': SOURCE_COMMIT}


def check_idle(process_listing: bytes) -> None:
    """Reject evaluator/runner processes or any QEMU process from a real ps snapshot."""
    lines = process_listing.decode('ascii', 'strict').splitlines()
    require(bool(lines), 'GateBlocked', 'Empty process inventory')
    for line in lines:
        columns = line.split(None, 2)
        require(len(columns) == 3, 'GateBlocked', 'Malformed process inventory')
        # macOS ps represents some service identities as signed UIDs (e.g. -2).
        uid_digits = columns[0][1:] if columns[0].startswith(('+', '-')) else columns[0]
        require(uid_digits.isdigit() and columns[1].isdigit(),
                'GateBlocked', 'Malformed process inventory')
        uid = int(columns[0])
        executable = Path(columns[2]).name.lower()
        require(uid not in (320, 321) and not executable.startswith('qemu'),
                'GateBlocked', 'Replay identity or QEMU process is active')


def check_absent(path: Path) -> None:
    """Reject complete, partial, and dangling-symlink namespaces alike."""
    require(not os.path.lexists(path), 'GateBlocked', 'Existing replay namespace; recovery review required')


def protected_preflight(corpus: Path, vm: Path, archive: Path, policy_path: Path,
                        parent_lock: int = None) -> dict:
    """Inspect actual protected assets; acquire existing lock read-only, never create it.

    A passing snapshot is not execution authority and does not close the review gate.
    Root provisioning must rerun these checks with this lock held across effects.
    """
    immutable(policy_path)
    policy = validate_policy(protected_bytes(policy_path, POLICY_SHA256))
    immutable(corpus, directory=True)
    corpus_binding = inspect_corpus(corpus, protected=True)
    immutable(archive)
    protected_bytes(archive, SOURCE_ARCHIVE)
    immutable(vm, directory=True)
    for name, expected in ASSETS.items():
        path = vm / (name if name.endswith('.iso') else 'boot/' + name)
        immutable(path)
        protected_bytes(path, expected)
    immutable(PRESERVED_ROOT, directory=True)
    require({p.name for p in PRESERVED_ROOT.iterdir()} == set(PRESERVED),
            'IntegrityFailure', 'Preserved corpus inventory differs')
    for name, expected in PRESERVED.items():
        immutable(PRESERVED_ROOT / name)
        protected_bytes(PRESERVED_ROOT / name, expected)
    installation = record(Path('/Library/GRRR/qemu/installation.json'))
    require(digest(canonical(installation)) == QEMU_MANIFEST,
            'IntegrityFailure', 'QEMU manifest differs')
    executable = verify_qemu(installation)
    require(executable == QEMU_EXECUTABLE_PATH and digest(executable.read_bytes()) == QEMU_EXECUTABLE,
            'IntegrityFailure', 'QEMU executable differs')
    for uid in (320, 321):
        account = pwd.getpwuid(uid)
        require(account.pw_uid == uid and account.pw_gid == uid
                and account.pw_dir == '/var/empty'
                and account.pw_shell in ('/usr/bin/false', '/bin/false'),
                'GateBlocked', 'Dedicated identity boundary differs')
    immutable(REPLAY_ROOT.parent, directory=True)
    check_absent(REPLAY_ROOT)
    require(shutil.disk_usage(REPLAY_ROOT.parent).free >= policy['limits']['minimum_host_free_bytes'],
            'BudgetExceeded', 'Approved 15 GiB free-space floor unavailable')
    immutable(LOCK)
    descriptor = os.open(LOCK, os.O_RDONLY | os.O_NOFOLLOW) if parent_lock is None else os.dup(parent_lock)
    with os.fdopen(descriptor, 'rb') as stream:
        info = os.fstat(stream.fileno())
        current = LOCK.lstat()
        require((info.st_dev, info.st_ino) == (current.st_dev, current.st_ino),
                'GateBlocked', 'Parent lock inode differs')
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and info.st_nlink == 1
                and info.st_mode & 0o222 == 0, 'GateBlocked', 'Unsafe launch lock')
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Failure('GateBlocked', 'Corpus/replay parent lock busy') from exc
        processes = subprocess.run(['/bin/ps', '-axo', 'uid=,pid=,comm='],
                                   check=True, capture_output=True, timeout=5,
                                   env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
        check_idle(processes)
        check_absent(REPLAY_ROOT)
    return {'protected_assets': 'validated-read-only', 'corpus': corpus_binding,
            'policy_sha256': POLICY_SHA256, 'execution_authorized': False,
            'root_installation': 'not-run', 'replay_dispatch': 'not-run',
            'independent_review': 'required', 'admission': 'blocked', 'verified': False}
