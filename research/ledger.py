"""Evaluator-owned SQLite journal; content objects precede reference commits."""
import json
import os
from pathlib import Path
import sqlite3
import threading
from common import EVALUATOR, GATES, Failure, canonical, digest, fields, identifier, require, unique_fields

DURABLE_FORMAT = 'grrr-durable-evidence-v1'
DURABLE_FIELDS = {'version', 'format', 'run', 'experiment', 'arm', 'event_type', 'actor',
                  'started_ns', 'completed_ns', 'base_commit', 'candidate_commit',
                  'built_digests', 'evaluator', 'vm', 'toolchain', 'policy', 'specification',
                  'corpus', 'input', 'selector', 'gates', 'measurements', 'usage',
                  'reservations', 'finding', 'review_target', 'action_target', 'objects',
                  'recovery_outcome'}
GATE_STATES = {'pass', 'fail', 'not-run', 'error'}


class Ledger:
    def __init__(self, root: Path) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Evaluator-owned ledger only')
        require(root.is_absolute() and '..' not in root.parts and not root.is_symlink(),
                'InvalidInput', 'Ledger root must be normalized absolute path')
        self.root = root
        self.objects = root / 'objects'
        root.mkdir(mode=0o700, exist_ok=True)
        require(root.stat().st_uid == EVALUATOR and not root.stat().st_mode & 0o077,
                'Unauthorized', 'Ledger root is not private evaluator storage')
        self.objects.mkdir(exist_ok=True, mode=0o700)
        require(self.objects.stat().st_uid == EVALUATOR
                and not self.objects.stat().st_mode & 0o077 and not self.objects.is_symlink(),
                'Unauthorized', 'Object store is not private evaluator storage')
        self.lock = threading.RLock()
        self.db = sqlite3.connect(root / 'ledger.sqlite', check_same_thread=False, isolation_level=None)
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, prior TEXT NOT NULL, hash TEXT UNIQUE NOT NULL, body BLOB NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS idempotency(key TEXT PRIMARY KEY NOT NULL, seq INTEGER NOT NULL REFERENCES events(seq), prior TEXT NOT NULL, hash TEXT NOT NULL, body BLOB NOT NULL)')
        self.db.execute('CREATE TRIGGER IF NOT EXISTS immutable_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,"immutable"); END')
        self.db.execute('CREATE TRIGGER IF NOT EXISTS immutable_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,"immutable"); END')
        self.db.execute('PRAGMA foreign_keys=ON')

    def close(self) -> None:
        self.db.close()

    def object(self, content: bytes) -> str:
        hashed = digest(content)
        path = self.objects / hashed
        if not path.exists():
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
            descriptor = os.open(path, flags, 0o600)
            try:
                with os.fdopen(descriptor, 'wb', closefd=False) as stream:
                    stream.write(content)
                    stream.flush()
                    os.fchmod(descriptor, 0o600)
                    os.fsync(descriptor)
            finally:
                os.close(descriptor)
            directory = os.open(self.objects, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        require(path.read_bytes() == content, 'IntegrityFailure', 'Object changed')
        return hashed

    def tip(self) -> str:
        row = self.db.execute('SELECT hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        return row[0] if row else '0' * 64

    def _append(self, principal: int, event: dict, expectedTip: str, key: str,
                callback=None) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Journal is evaluator-only')
        identifier(expectedTip, True)
        identifier(key)
        event = dict(event, idempotency_key=key, version=1)
        if event.get('format') == DURABLE_FORMAT:
            validate_durable_event(event)
        with self.lock:
            body = canonical(event)
            previous = self.db.execute(
                'SELECT seq,prior,hash,body FROM idempotency WHERE key=?', (key,)).fetchone()
            if previous is not None:
                sequence, prior, hashed, prior_body = previous
                require(prior == expectedTip and bytes(prior_body) == body,
                        'StaleBinding', 'Idempotency key changed tip or payload')
                return {'sequence': sequence, 'digest': hashed, 'prior': prior}
            require(self.tip() == expectedTip, 'StaleBinding', 'Journal tip changed')
            hashed = digest(expectedTip.encode() + body)
            try:
                self.db.execute('BEGIN IMMEDIATE')
                cursor = self.db.execute('INSERT INTO events(prior,hash,body) VALUES(?,?,?)',
                                         (expectedTip, hashed, body))
                sequence = cursor.lastrowid
                self.db.execute('INSERT INTO idempotency VALUES(?,?,?,?,?)',
                                (key, sequence, expectedTip, hashed, body))
                receipt = {'sequence': sequence, 'digest': hashed, 'prior': expectedTip}
                if callback is not None:
                    callback(self.db, receipt)
                self.db.commit()
                return receipt
            except BaseException as exc:
                self.db.rollback()
                if isinstance(exc, (sqlite3.Error, OSError)):
                    raise Failure('RecoveryRequired', 'Ledger transaction failed; inspect objects and tip') from exc
                raise

    def append(self, principal: int, event: dict, expectedTip: str, key: str) -> dict:
        return self._append(principal, event, expectedTip, key)

    def append_atomic(self, principal: int, event: dict, expectedTip: str, key: str,
                      callback=None) -> dict:
        """Append and apply caller state changes in one SQLite transaction."""
        return self._append(principal, event, expectedTip, key, callback)

    def snapshot(self, event: dict, key: str) -> dict:
        with self.lock:
            receipt = self.append(EVALUATOR, event, self.tip(), key)
            rows = [{'sequence': n, 'prior': p, 'digest': h, 'event': json.loads(b)}
                    for n, p, h, b in self.db.execute('SELECT * FROM events ORDER BY seq')]
            objects = {h: (self.objects / h).read_bytes().hex()
                       for row in rows for h in row['event'].get('objects', [])}
            snapshot = {'version': 1, 'receipt': receipt, 'events': rows, 'objects': objects}
            snapshot['snapshot_id'] = digest(canonical(snapshot))
            self.object(canonical(snapshot))
            return snapshot


def validate_durable_event(event: dict) -> None:
    fields(event, DURABLE_FIELDS, {'idempotency_key', 'version'})
    require(event['version'] == 1 and event['format'] == DURABLE_FORMAT,
            'InvalidInput', 'Durable event format differs')
    for name in ('run', 'experiment', 'arm', 'event_type'):
        identifier(event[name])
    require(event['actor'] == 'evaluator', 'Unauthorized', 'Durable actor differs')
    for name in ('base_commit', 'candidate_commit', 'evaluator', 'vm', 'toolchain',
                 'policy', 'specification', 'corpus', 'input'):
        identifier(event[name], True)
    require(type(event['started_ns']) is int and type(event['completed_ns']) is int
            and 0 <= event['started_ns'] <= event['completed_ns'],
            'InvalidInput', 'Durable event times differ')
    built = event['built_digests']
    require(isinstance(built, dict) and len(built) <= 128, 'InvalidInput', 'Built digest inventory differs')
    for name, value in built.items():
        identifier(name)
        identifier(value, True)
    selector = event['selector']
    fields(selector, {'version', 'seed'})
    identifier(selector['version'])
    require(isinstance(selector['seed'], str) and 1 <= len(selector['seed']) <= 128
            and all(32 <= ord(character) < 127 for character in selector['seed']),
            'InvalidInput', 'Selector seed differs')
    gates = event['gates']
    require(isinstance(gates, dict) and set(gates) == set(GATES),
            'InvalidInput', 'Gate inventory incomplete')
    for result in gates.values():
        fields(result, {'state', 'evidence'})
        require(result['state'] in GATE_STATES, 'InvalidInput', 'Gate state differs')
        identifier(result['evidence'], True)
    measurements = event['measurements']
    require(isinstance(measurements, list) and len(measurements) <= 256,
            'InvalidInput', 'Measurement inventory differs')
    for measurement in measurements:
        fields(measurement, {'name', 'value', 'unit'})
        identifier(measurement['name'])
        require(measurement['unit'] in ('bytes', 'seconds', 'count', 'ratio', 'usd_cents')
                and type(measurement['value']) in (int, float) and measurement['value'] >= 0,
                'InvalidInput', 'Measurement value/unit differs')
    usage = event['usage']
    fields(usage, {'currency', 'money_cents', 'execution_us', 'review_us'})
    require(usage['currency'] == 'USD' and all(type(usage[name]) is int and usage[name] >= 0
            for name in ('money_cents', 'execution_us', 'review_us')),
            'InvalidInput', 'Usage vector differs')
    require(isinstance(event['reservations'], list) and len(event['reservations']) <= 64,
            'InvalidInput', 'Reservation inventory differs')
    for reservation in event['reservations']:
        fields(reservation, {'id', 'maximum'})
        identifier(reservation['id'], True)
        maximum = reservation['maximum']
        fields(maximum, {'currency', 'money_cents', 'execution_us', 'review_us'})
        require(maximum['currency'] == 'USD'
                and all(type(maximum[name]) is int and maximum[name] >= 0
                        for name in ('money_cents', 'execution_us', 'review_us')),
                'InvalidInput', 'Reservation maximum differs')
    finding = event['finding']
    fields(finding, {'state', 'object'})
    require(finding['state'] in ('verified', 'not-reproduced', 'ambiguous', 'not-run'),
            'InvalidInput', 'Finding state differs')
    identifier(finding['object'], True)
    for name in ('review_target', 'action_target'):
        target = event[name]
        fields(target, {'kind', 'id'})
        identifier(target['kind'])
        identifier(target['id'], True)
    require(isinstance(event['objects'], list) and len(event['objects']) <= 1024
            and all(identifier(value, True) is not None for value in event['objects']),
            'InvalidInput', 'Object references differ')
    require(event['recovery_outcome'] in ('none', 'interrupted', 'recovery-required', 'recovered-verified'),
            'InvalidInput', 'Recovery outcome differs')


def experiment_event(**values) -> dict:
    zero = '0' * 64
    event = {
        'version': 1, 'format': DURABLE_FORMAT,
        'run': values['run'], 'experiment': values['experiment'], 'arm': values['arm'],
        'event_type': values.get('event_type', 'experiment-record'), 'actor': 'evaluator',
        'started_ns': values['started_ns'], 'completed_ns': values['completed_ns'],
        'base_commit': values['base_commit'], 'candidate_commit': values['candidate_commit'],
        'built_digests': values.get('built_digests', {}), 'evaluator': values['evaluator'],
        'vm': values['vm'], 'toolchain': values['toolchain'], 'policy': values['policy'],
        'specification': values['specification'], 'corpus': values['corpus'], 'input': values['input'],
        'selector': {'version': values['selector_version'], 'seed': values['selector_seed']},
        'gates': {gate: {'state': state, 'evidence': values.get('gate_evidence', zero)}
                  for gate, state in values['gates'].items()},
        'measurements': values.get('measurements', []), 'usage': values.get('usage', {
            'currency': 'USD', 'money_cents': 0, 'execution_us': 0, 'review_us': 0}),
        'reservations': values.get('reservations', []), 'finding': values['finding'],
        'review_target': values['review_target'], 'action_target': values['action_target'],
        'objects': values.get('objects', []), 'recovery_outcome': values.get('recovery_outcome', 'none'),
    }
    validate_durable_event(event)
    return event


def _exclusive(path: Path, raw: bytes, mode: int = 0o444) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    descriptor = os.open(path, flags, mode)
    try:
        with os.fdopen(descriptor, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fchmod(descriptor, mode)
            os.fsync(descriptor)
    finally:
        os.close(descriptor)


def export_snapshot(snapshot: dict, destination: Path) -> dict:
    verifySnapshot(snapshot, snapshot['receipt']['digest'])
    require(destination.is_absolute() and '..' not in destination.parts and not destination.exists(),
            'InvalidInput', 'Export destination differs')
    require(not destination.parent.is_symlink(), 'InvalidInput', 'Symlinked export parent')
    destination.mkdir(mode=0o700)
    objects = destination / 'objects'
    objects.mkdir(mode=0o700)
    hashes = {}
    snapshot_raw = canonical(snapshot)
    _exclusive(destination / 'snapshot.json', snapshot_raw)
    hashes['snapshot.json'] = digest(snapshot_raw)
    for hashed, encoded in snapshot['objects'].items():
        content = bytes.fromhex(encoded)
        _exclusive(objects / hashed, content, 0o400)
        hashes['objects/' + hashed] = digest(content)
    manifest = {'version': 1, 'snapshot_id': snapshot['snapshot_id'],
                'trusted_anchor': snapshot['receipt']['digest'],
                'events': len(snapshot['events']), 'objects': len(snapshot['objects']),
                'files': hashes,
                'verifier': 'Verify with independently retained trusted_anchor via verify_export.'}
    _exclusive(destination / 'MANIFEST.json', canonical(manifest))
    instructions = ('# Durable evidence verification\n\n'
                    '1. Retain the trusted anchor independently of this export.\n'
                    '2. Run verify_export(export_root, trusted_anchor).\n'
                    '3. Reject missing objects, altered bytes, truncation, or anchor mismatch.\n'
                    '4. Do not infer success from report generation or cleanup.\n').encode('ascii')
    _exclusive(destination / 'VERIFY.md', instructions)
    for path in (destination, objects):
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    return manifest


def verify_export(destination: Path, trusted_anchor: str) -> dict:
    identifier(trusted_anchor, True)
    require(destination.is_absolute() and '..' not in destination.parts,
            'InvalidInput', 'Export root differs')
    require(not destination.parent.is_symlink()
            and not (destination / 'objects').is_symlink(),
            'IntegrityFailure', 'Symlinked export path')
    manifest_raw = (destination / 'MANIFEST.json').read_bytes()
    manifest = json.loads(manifest_raw, object_pairs_hook=unique_fields,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    fields(manifest, {'version', 'snapshot_id', 'trusted_anchor', 'events', 'objects', 'files', 'verifier'})
    require(manifest['version'] == 1 and manifest['trusted_anchor'] == trusted_anchor
            and type(manifest['events']) is int and type(manifest['objects']) is int,
            'IntegrityFailure', 'Export manifest differs')
    snapshot_raw = (destination / 'snapshot.json').read_bytes()
    require(digest(snapshot_raw) == manifest['files'].get('snapshot.json'),
            'IntegrityFailure', 'Snapshot bytes differ')
    snapshot = json.loads(snapshot_raw, object_pairs_hook=unique_fields,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    verifySnapshot(snapshot, trusted_anchor)
    require(manifest['snapshot_id'] == snapshot['snapshot_id']
            and manifest['events'] == len(snapshot['events'])
            and manifest['objects'] == len(snapshot['objects']),
            'IntegrityFailure', 'Manifest counts differ')
    for hashed, encoded in snapshot['objects'].items():
        object_path = destination / 'objects' / hashed
        require(object_path.is_file() and not object_path.is_symlink(),
                'IntegrityFailure', 'Export object path differs')
        content = object_path.read_bytes()
        require(digest(content) == manifest['files'].get('objects/' + hashed) == hashed
                and content == bytes.fromhex(encoded),
                'IntegrityFailure', 'Export object missing or altered')
    require((destination / 'VERIFY.md').read_bytes(), 'IntegrityFailure', 'Verifier instructions absent')
    return {'snapshot_id': snapshot['snapshot_id'], 'trusted_anchor': trusted_anchor,
            'events': len(snapshot['events']), 'objects': len(snapshot['objects']), 'verified': True}


def recovery_state(snapshot: dict) -> dict:
    verifySnapshot(snapshot, snapshot['receipt']['digest'])
    reservations = []
    interrupted_keys = []
    unresolved_objects = []
    for row in snapshot['events']:
        event = row['event']
        if event.get('format') != DURABLE_FORMAT:
            continue
        if event['recovery_outcome'] in ('interrupted', 'recovery-required'):
            interrupted_keys.append(event['idempotency_key'])
            unresolved_objects.extend(event['objects'])
            reservations.extend(event['reservations'])
    unresolved = bool(interrupted_keys)
    return {'status': 'RecoveryRequired' if unresolved else 'NoUnresolvedInterruption',
            'reservation_ids': [reservation['id'] for reservation in reservations],
            'reservations_preserved': bool(reservations) if unresolved else True,
            'interrupted_keys': interrupted_keys, 'unresolved_objects': unresolved_objects,
            'retry_authorized': False, 'promotion_authorized': False}


def verifySnapshot(snapshot: dict, trustedAnchor: str) -> dict:
    expected = dict(snapshot)
    sid = expected.pop('snapshot_id')
    require(digest(canonical(expected)) == sid, 'IntegrityFailure', 'Snapshot identity mismatch')
    prior = '0' * 64
    for sequence, row in enumerate(snapshot['events'], 1):
        require(row['sequence'] == sequence and row['prior'] == prior,
                'IntegrityFailure', 'Journal gap or prior mismatch')
        prior = digest(prior.encode() + canonical(row['event']))
        require(prior == row['digest'], 'IntegrityFailure', 'Event altered')
        for hashed in row['event'].get('objects', []):
            require(hashed in snapshot['objects'] and
                    digest(bytes.fromhex(snapshot['objects'][hashed])) == hashed,
                    'IntegrityFailure', 'Missing or altered object')
    require(prior == trustedAnchor == snapshot['receipt']['digest'],
            'IntegrityFailure', 'Truncated or untrusted snapshot')
    return snapshot
