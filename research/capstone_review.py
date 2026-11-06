"""Independent review storage: original bytes, irreversible intent, exact replay.

No approval importer and no evaluator-writable production path. An intent whose
result was not durably indexed is recovery-required; retries never remint a
review or extend its timestamps. Storage provenance is established by the
review service's kernel principal, not by possession of copied result JSON.
"""
import base64
import json
import os
from pathlib import Path
import sqlite3
import stat
import threading

from common import (Failure, MAX_WIRE, canonical, digest, fields, identifier,
                    require, unique_fields)

REVIEWER = 322
ROOT = Path('/Library/GRRR/capstone-v1/reviewer')
_OPEN = object()
SCHEMA = (
    'CREATE TABLE review_events(seq INTEGER PRIMARY KEY, prior TEXT NOT NULL, hash TEXT UNIQUE NOT NULL, body BLOB NOT NULL)',
    'CREATE TABLE review_requests(request_hash TEXT PRIMARY KEY NOT NULL, request_raw BLOB NOT NULL, intent_hash TEXT NOT NULL, review_hash TEXT, review_raw BLOB, CHECK(typeof(request_raw)=\'blob\'), CHECK((review_hash IS NULL)=(review_raw IS NULL)), CHECK(review_raw IS NULL OR typeof(review_raw)=\'blob\'))',
    "CREATE TRIGGER review_events_update BEFORE UPDATE ON review_events BEGIN SELECT RAISE(ABORT,'immutable'); END",
    "CREATE TRIGGER review_events_delete BEFORE DELETE ON review_events BEGIN SELECT RAISE(ABORT,'immutable'); END",
    "CREATE TRIGGER review_requests_delete BEFORE DELETE ON review_requests BEGIN SELECT RAISE(ABORT,'immutable'); END",
    "CREATE TRIGGER review_requests_update BEFORE UPDATE ON review_requests WHEN NEW.request_hash IS NOT OLD.request_hash OR NEW.request_raw IS NOT OLD.request_raw OR NEW.intent_hash IS NOT OLD.intent_hash OR OLD.review_hash IS NOT NULL OR NEW.review_hash IS NULL BEGIN SELECT RAISE(ABORT,'immutable'); END",
)


def _hash(tag, value):
    return digest(tag.encode('ascii') + b'\0' + canonical(value))


def _decode(raw):
    require(type(raw) is bytes and len(raw) <= MAX_WIRE, 'InvalidInput', 'Review wire bound differs')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed review JSON') from exc
    require(canonical(value) == raw, 'InvalidInput', 'Review bytes are noncanonical')
    return value


def request_hash(request):
    fields(request, {'action', 'version', 'campaign_operation_id', 'leaf_id',
                     'campaign_plan_raw', 'actual_plan_raw', 'request_sha256'})
    require(request['action'] == 'review-plan' and type(request['version']) is int
            and request['version'] == 2, 'InvalidInput', 'Wrong review action/version')
    for name in ('campaign_operation_id', 'leaf_id', 'request_sha256'):
        identifier(request[name], True)
    for name in ('campaign_plan_raw', 'actual_plan_raw'):
        raw = request[name]
        require(type(raw) is str and len(raw) <= MAX_WIRE, 'InvalidInput', 'Review raw bound differs')
        try:
            decoded = base64.b64decode(raw, validate=True)
        except (ValueError, TypeError) as exc:
            raise Failure('InvalidInput', 'Review raw encoding differs') from exc
        require(base64.b64encode(decoded).decode('ascii') == raw,
                'InvalidInput', 'Review raw is not canonical base64')
    expected = _hash('jit-review-request-v2', {k: v for k, v in request.items() if k != 'request_sha256'})
    require(expected == request['request_sha256'], 'StaleBinding', 'Review request hash differs')
    return expected


def _fixture_root(root):
    root = Path(root)
    # Lexical rejection is BEFORE ANY metadata/content operation.
    require(root.is_absolute() and root.parent == Path('/private/tmp')
            and root.name.startswith('grrr-backend-fixture-') and '..' not in root.parts
            and os.getuid() not in (0, 320, 321, REVIEWER),
            'Unauthorized', 'Not an unprivileged public fixture root')
    st = root.lstat()
    require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid()
            and stat.S_IMODE(st.st_mode) == 0o700, 'Unauthorized', 'Fixture root is not private')
    return root


class ReviewStore:
    def __init__(self, root, token, nonproduction):
        require(token is _OPEN, 'Unauthorized', 'Use explicit reviewer store factory')
        self.root, self.nonproduction = root, nonproduction
        self.objects = root / 'objects'
        self.pid, self.lock = os.getpid(), threading.RLock()
        uid = os.getuid() if nonproduction else REVIEWER
        for path, mode in ((root, 0o700), (self.objects, 0o700)):
            st = path.lstat()
            require(stat.S_ISDIR(st.st_mode) and st.st_uid == uid
                    and stat.S_IMODE(st.st_mode) == mode, 'Unauthorized', 'Reviewer directory differs')
        st = (root / 'index.sqlite').lstat()
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_uid == uid
                and stat.S_IMODE(st.st_mode) == 0o600, 'Unauthorized', 'Reviewer index identity differs')
        self.db = sqlite3.connect('file:' + str(root / 'index.sqlite') + '?mode=rw',
                                 uri=True, isolation_level=None, check_same_thread=False, timeout=2)
        # Connection-local durability settings, never runtime schema creation.
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA foreign_keys=ON')
        try:
            self._snapshot()
        except BaseException:
            self.db.close()
            raise

    @classmethod
    def open_existing(cls):
        require(os.getuid() == REVIEWER, 'Unauthorized', 'Actual independent reviewer UID required')
        return cls(ROOT, _OPEN, False)

    @classmethod
    def open_public_fixture(cls, root, *, create=False):
        root = _fixture_root(root)
        directory = root / 'reviewer'
        if create:
            directory.mkdir(mode=0o700)  # exclusive; never adopt/repair a previous store
            (directory / 'objects').mkdir(mode=0o700)
            path = directory / 'index.sqlite'
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            os.close(fd)
            db = sqlite3.connect(path, isolation_level=None)
            try:
                db.execute('PRAGMA journal_mode=DELETE')
                db.execute('PRAGMA synchronous=FULL')
                for sql in SCHEMA:
                    db.execute(sql)
            finally:
                db.close()
        return cls(directory, _OPEN, True)

    def _object(self, raw):
        hashed = digest(raw)
        path = self.objects / hashed
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError:
            require(self._read_object(hashed) == raw, 'IntegrityFailure', 'Review object bytes changed')
            return hashed
        try:
            with os.fdopen(fd, 'wb', closefd=False) as stream:
                stream.write(raw)
                stream.flush()
            os.fsync(fd)
        finally:
            os.close(fd)
        directory = os.open(self.objects, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return hashed

    def _read_object(self, hashed):
        identifier(hashed, True)
        fd = os.open(self.objects / hashed, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            st = os.fstat(fd)
            require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_uid == os.getuid()
                    and stat.S_IMODE(st.st_mode) == 0o600 and st.st_size <= MAX_WIRE,
                    'IntegrityFailure', 'Review object metadata differs')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read(MAX_WIRE + 1)
            require(digest(raw) == hashed and len(raw) <= MAX_WIRE,
                    'IntegrityFailure', 'Review object hash differs')
            return raw
        finally:
            os.close(fd)

    def _schema(self):
        actual = set(self.db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master'))
        sql = {row[3] for row in actual if row[3] is not None}
        indexes = {row[:3] for row in actual if row[3] is None}
        require(sql == set(SCHEMA) and indexes == {
            ('index', 'sqlite_autoindex_review_events_1', 'review_events'),
            ('index', 'sqlite_autoindex_review_requests_1', 'review_requests')},
            'IntegrityFailure', 'Review store schema differs')
        require(not self.db.execute('SELECT name FROM sqlite_temp_master').fetchall()
                and all(r[1] in ('main', 'temp') for r in self.db.execute('PRAGMA database_list'))
                and self.db.execute('PRAGMA journal_mode').fetchone() == ('delete',)
                and self.db.execute('PRAGMA synchronous').fetchone() == (2,),
                'IntegrityFailure', 'Review store durability/shadow differs')

    def _replay(self):
        require(self.pid == os.getpid(), 'Unauthorized', 'Inherited reviewer connection')
        self._schema()
        expected, prior, sequence = {}, '0' * 64, 0
        for seq, parent, hashed, raw in self.db.execute('SELECT * FROM review_events ORDER BY seq'):
            sequence += 1
            require(seq == sequence and parent == prior and hashed == digest(parent.encode() + raw),
                    'IntegrityFailure', 'Review index chain differs')
            event = _decode(raw)
            fields(event, {'action', 'request_hash', 'request_object', 'review_object'})
            key = identifier(event['request_hash'], True)
            original = self._read_object(event['request_object'])
            require(request_hash(_decode(original)) == key, 'IntegrityFailure', 'Indexed request differs')
            if event['action'] == 'intent':
                require(key not in expected and event['review_object'] is None,
                        'IntegrityFailure', 'Duplicate reviewer intent')
                expected[key] = (key, original, hashed, None, None)
            elif event['action'] == 'commit':
                require(key in expected and expected[key][3] is None
                        and expected[key][1] == original, 'IntegrityFailure', 'Invalid reviewer commit')
                review_raw = self._read_object(event['review_object'])
                # The store checks the exact typed bytes as well as their hash.
                from capstone_backend_contract import decode_record
                decode_record(review_raw, 'ReviewV2')
                expected[key] = expected[key][:3] + (event['review_object'], review_raw)
            else:
                raise Failure('IntegrityFailure', 'Unknown reviewer index action')
            prior = hashed
        actual = {r[0]: tuple(r) for r in self.db.execute('SELECT * FROM review_requests')}
        require(actual == expected, 'IntegrityFailure', 'Reviewer index rows differ from full replay')
        return expected, prior, sequence

    def _snapshot(self):
        with self.lock:
            require(not self.db.in_transaction, 'RecoveryRequired', 'Unexpected reviewer transaction')
            self.db.execute('BEGIN')
            try:
                return self._replay()
            finally:
                self.db.rollback()

    def _append(self, action, original, review_raw=None):
        request = _decode(original)
        key = request_hash(request)
        request_object = self._object(original)
        review_object = self._object(review_raw) if review_raw is not None else None
        event = dict(action=action, request_hash=key, request_object=request_object, review_object=review_object)
        raw = canonical(event)
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                rows, prior, count = self._replay()
                hashed = digest(prior.encode() + raw)
                if action == 'intent':
                    require(key not in rows, 'RecoveryRequired', 'Reviewer request already exists')
                    self.db.execute('INSERT INTO review_requests VALUES(?,?,?,NULL,NULL)', (key, original, hashed))
                else:
                    require(key in rows and rows[key][1] == original and rows[key][3] is None,
                            'RecoveryRequired', 'Reviewer result already exists or intent differs')
                    self.db.execute('UPDATE review_requests SET review_hash=?,review_raw=? WHERE request_hash=?',
                                    (review_object, review_raw, key))
                self.db.execute('INSERT INTO review_events VALUES(?,?,?,?)', (count + 1, prior, hashed, raw))
                self._replay()
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise

    def review(self, request, verifier):
        # Freeze caller bytes; verifier is trusted service wiring, never payload.
        original = canonical(request)
        key = request_hash(_decode(original))
        rows, _, _ = self._snapshot()
        if key in rows:
            require(rows[key][1] == original, 'StaleBinding', 'Same review key changed request')
            return self.get(key)
        self._append('intent', original)
        # No database transaction or evaluator/launch gate across callback RPC.
        review_raw = verifier(_decode(original))
        from capstone_backend_contract import decode_record
        decode_record(review_raw, 'ReviewV2')
        self._append('commit', original, review_raw)
        return self.get(key)

    def get(self, key):
        identifier(key, True)
        rows, _, _ = self._snapshot()
        require(key in rows, 'Unavailable', 'Review request is unknown')
        row = rows[key]
        require(row[3] is not None, 'RecoveryRequired', 'Review intent has no committed result; never remint')
        return dict(request_sha256=key, review_sha256=row[3],
                    review_raw=base64.b64encode(row[4]).decode('ascii'))

    def close(self):
        self.db.close()
