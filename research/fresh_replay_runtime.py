"""Source-only proposals and explicit offline fixtures. Never an execution authority."""
from dataclasses import dataclass
import json
import os
import re
import stat

from common import GATES, canonical, digest, fields, identifier, require

RECOVERY = '8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb'
PREDECESSOR = '/Library/GRRR/independent-replay'
BINDINGS = ('source', 'inputs', 'vm', 'policy', 'prior_evidence', 'accounting')


def check(ok: bool, message: str) -> None:
    require(ok, 'InvalidInput', message)


def json_value(value: object) -> None:
    """Exact JSON types; reject coercible tuples, non-string keys and subclasses."""
    if type(value) is dict:
        check(all(type(k) is str for k in value), 'Non-string key')
        for item in value.values():
            json_value(item)
    elif type(value) is list:
        for item in value:
            json_value(item)
    else:
        check(type(value) in (str, int, bool, type(None)), 'Noncanonical value')


@dataclass(frozen=True)
class Proposal:
    canonical_bytes: bytes
    sha256: str

    def __post_init__(self) -> None:
        check(type(self.canonical_bytes) is bytes, 'Canonical bytes')
        check(type(self.sha256) is str, 'Proposal digest')

    def record(self) -> dict:
        """A detached copy, not mutable proposal state."""
        return json.loads(self.canonical_bytes)


def prepare(request: dict, expected_request_hash: str) -> Proposal:
    """Validate caller-supplied archived facts, NOT their currency or authority.

    Manifest payloads are opaque canonical JSON objects, except accounting's
    explicit v4 preservation fields. Hashes identify content, not signatures.
    """
    check(type(expected_request_hash) is str, 'Expected request digest')
    json_value(request)
    fields(request, {'version', 'namespace', 'target_state', 'used_namespaces',
                     'predecessor', 'bindings', 'identities'})
    check(type(request['version']) is int and request['version'] == 1, 'Version')
    identifier(expected_request_hash, hashed=True)
    check(digest(canonical(request)) == expected_request_hash, 'Stale request hash')
    namespace = request['namespace']
    check(type(namespace) is str and re.fullmatch(r'[0-9a-f]{32}', namespace), 'Namespace')
    check(type(request['used_namespaces']) is list, 'Namespace inventory')
    for used in request['used_namespaces']:
        check(type(used) is str and re.fullmatch(r'[0-9a-f]{32}', used), 'Inventory entry')
    check(namespace not in request['used_namespaces'], 'Reused target')
    check(request['target_state'] == 'absent', 'Target must be absent in supplied evidence')
    predecessor = request['predecessor']
    fields(predecessor, {'identity', 'target', 'replay_state', 'replay_count'})
    identifier(predecessor['identity'], hashed=True)
    check(predecessor['target'] == PREDECESSOR, 'Predecessor target')
    check(predecessor['replay_state'] in ('consumed', 'unused', 'unknown', 'stopped', 'pending'),
          'Predecessor state')
    check(predecessor['replay_count'] is None or
          (type(predecessor['replay_count']) is int and predecessor['replay_count'] >= 0), 'Count')
    fields(request['bindings'], set(BINDINGS))
    fields(request['identities'], set(BINDINGS) | {'predecessor'})
    check(request['identities']['predecessor'] == predecessor['identity'], 'Stale predecessor')
    for name in BINDINGS:
        entry = request['bindings'][name]
        fields(entry, {'identity', 'sha256', 'payload'})
        identifier(entry['identity'], hashed=True)
        identifier(entry['sha256'], hashed=True)
        check(entry['identity'] == request['identities'][name], 'Stale identity: ' + name)
        check(type(entry['payload']) is dict and bool(entry['payload']), 'Missing evidence: ' + name)
        identifier(entry['payload'].get('archive_sha256'), hashed=True)
        check(digest(canonical(entry['payload'])) == entry['sha256'], 'Stale binding: ' + name)
    accounting = request['bindings']['accounting']['payload']
    fields(accounting, {'version', 'recovery_receipt', 'unknowns', 'holds', 'archive_sha256'})
    check(type(accounting['version']) is int and accounting['version'] == 4, 'Accounting version')
    check(accounting['recovery_receipt'] == RECOVERY, 'Recovery receipt')
    check(type(accounting['unknowns']) is dict and type(accounting['holds']) is list,
          'Accounting preservation fields')
    value = {'version': 1, 'status': 'prepared_not_issued',
             'request_sha256': expected_request_hash, 'request': request,
             'proposed_target': '/Library/GRRR/replay-proposals/' + namespace,
             'authorizations': {name: False for name in
                                ('review', 'installation', 'replay', 'promotion', 'admission')},
             'live_gates': {name: 'not-run' for name in GATES},
             'runtime_readiness': 'not_asserted', 'accounting_action': 'none',
             'spendability': 'not_inferred'}
    encoded = canonical(value)
    return Proposal(encoded, digest(encoded))


def validate_proposal(proposal: Proposal, request: dict, expected_request_hash: str) -> None:
    check(type(proposal) is Proposal and proposal == prepare(request, expected_request_hash),
          'Proposal differs from immutable request')


def lexical(path: str) -> list[str]:
    """No metadata or normalization: reject aliases, traversal and protected roots."""
    check(type(path) is str and path.startswith('/private/tmp/'), 'Fixture paths only')
    check('\x00' not in path and '\\' not in path, 'Invalid path')
    parts = path.split('/')[1:]
    check(all(p and p not in ('.', '..') for p in parts), 'Noncanonical path')
    return parts


def directory(parts: list[str]) -> int:
    """Anchor each open to a pinned parent; never follow an ancestor symlink."""
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def fixture_preflight(request: dict, expected_request_hash: str, *,
                      sandbox: str, target: str, evidence: dict) -> Proposal:
    """Read-only offline check. Explicit evidence maps all bindings to path/hash.

    The caller owns a quiescent temporary fixture. No live freshness is proven;
    hashes of SQLite fixture bytes bind the file, not semantic ledger authority.
    No SQL is run and no file or namespace is created, including absent targets.
    """
    json_value(evidence)
    proposal = prepare(request, expected_request_hash)
    root_parts = lexical(sandbox)
    target_parts = lexical(target)
    check(target == sandbox + '/replay-' + request['namespace'], 'Candidate root/name')
    fields(evidence, set(BINDINGS))
    paths = []
    # Validate EVERY bound path before opening even the sandbox root.
    for name in BINDINGS:
        entry = evidence[name]
        fields(entry, {'path', 'sha256'})
        parts = lexical(entry['path'])
        check(parts[:len(root_parts)] == root_parts and len(parts) > len(root_parts), 'Escape')
        identifier(entry['sha256'], hashed=True)
        check(entry['sha256'] == request['bindings'][name]['payload']['archive_sha256'],
              'Unbound fixture hash')
        paths.append((parts, entry['sha256']))
    root_fd = directory(root_parts)
    try:
        target_absent = False
        try:
            os.stat(target_parts[-1], dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            target_absent = True
        else:
            target_absent = False
        if not target_absent:
            check(False, 'Target exists (including dangling symlink)')
        for parts, expected in paths:
            parent = os.dup(root_fd)
            try:
                for part in parts[len(root_parts):-1]:
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                    os.close(parent)
                    parent = child
                fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
                try:
                    info = os.fstat(fd)
                    check(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'Not a unique regular file')
                    check(info.st_size <= 3 * 1024 * 1024, 'Fixture too large')
                    chunks = []
                    remaining = 3 * 1024 * 1024 + 1
                    while remaining:
                        chunk = os.read(fd, min(65536, remaining))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        remaining -= len(chunk)
                    check(digest(b''.join(chunks)) == expected, 'Stale fixture bytes')
                finally:
                    os.close(fd)
            finally:
                os.close(parent)
    finally:
        os.close(root_fd)
    return proposal
