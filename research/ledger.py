"""Evaluator-owned SQLite journal; content objects precede reference commits."""
import json
import os
from pathlib import Path
import sqlite3
import threading
from common import EVALUATOR, canonical, digest, require


class Ledger:
    def __init__(self, root: Path) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Evaluator-owned ledger only')
        self.root = root
        self.objects = root / 'objects'
        self.objects.mkdir(exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(root / 'ledger.sqlite', check_same_thread=False)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, prior TEXT NOT NULL, hash TEXT UNIQUE NOT NULL, body BLOB NOT NULL)')
        self.db.execute('CREATE TRIGGER IF NOT EXISTS immutable_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,"immutable"); END')
        self.db.execute('CREATE TRIGGER IF NOT EXISTS immutable_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,"immutable"); END')
        self.db.commit()

    def object(self, content: bytes) -> str:
        hashed = digest(content)
        path = self.objects / hashed
        if not path.exists():
            with path.open('xb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            fd = os.open(self.objects, os.O_RDONLY)
            os.fsync(fd)
            os.close(fd)
        require(path.read_bytes() == content, 'IntegrityFailure', 'Object changed')
        return hashed

    def tip(self) -> str:
        row = self.db.execute('SELECT hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        return row[0] if row else '0' * 64

    def append(self, principal: int, event: dict, expectedTip: str, key: str) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Journal is evaluator-only')
        with self.lock:
            require(self.tip() == expectedTip, 'StaleBinding', 'Journal tip changed')
            event = dict(event, idempotency_key=key, version=1)
            body = canonical(event)
            hashed = digest(expectedTip.encode() + body)
            with self.db:
                cursor = self.db.execute('INSERT INTO events(prior,hash,body) VALUES(?,?,?)',
                                         (expectedTip, hashed, body))
            return {'sequence': cursor.lastrowid, 'digest': hashed, 'prior': expectedTip}

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
