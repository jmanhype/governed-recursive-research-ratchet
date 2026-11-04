"""Public real-SQLite fixtures. NOT evaluator identity or issuance evidence."""
import copy
import dataclasses
import multiprocessing
import os
from pathlib import Path
import pickle
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from common import EVALUATOR, Failure, canonical, digest
from capstone_contract import content_digest, operation_id
from capstone_journal import DispatchPermit, open_existing, open_public_fixture
from capstone_journal_schema import CORE_SQL, JOURNAL_SQL
from ledger import Ledger
from unit_capstone_contract import bound_plan

UID = os.getuid()
H = 'b' * 64


def fixture_connection(root, create=False):
    """No Ledger constructor and no identity patch; actual Ledger methods only."""
    root = Path(root)
    if root.parent != Path('/private/tmp') or not root.name.startswith('capstone-journal-fixture-'):
        raise ValueError('Fixture path rejected before I/O')
    obj = Ledger.__new__(Ledger)
    obj.root, obj.lock = root, threading.RLock()
    obj.db = sqlite3.connect('file:' + str(root / 'ledger.sqlite')
                            + ('?mode=rwc' if create else '?mode=rw'), uri=True,
                            check_same_thread=False, isolation_level=None, timeout=5)
    obj.db.execute('PRAGMA foreign_keys=ON')
    obj.db.execute('PRAGMA journal_mode=DELETE')
    obj.db.execute('PRAGMA synchronous=FULL')
    if create:
        for sql in CORE_SQL + JOURNAL_SQL:
            obj.db.execute(sql)
    return obj


def fixture_start(index=0):
    plan, raw, _ = bound_plan()
    if index:
        gid = digest(str(index).encode())
        plan['grant']['grant_id'] = plan['observation']['grant_id'] = gid
        raw = canonical(plan['grant']) + b'\n'
        plan['grant_bytes_sha256'] = plan['observation']['grant_bytes_sha256'] = digest(raw)
        plan['observation']['receipt_sha256'] = content_digest(plan['observation'], 'receipt_sha256')
        plan['plan_sha256'] = content_digest(plan, 'plan_sha256')
    return dict(action='start', version=1, plan=plan,
                operation_id=operation_id(plan['grant']['grant_id'], plan['plan_sha256'])), raw


def install_public_grant(db, start, raw):
    g = start['plan']['grant']
    db.execute('INSERT INTO capstone_grants VALUES(?,?,?,?,?,NULL)',
               (g['grant_id'], raw, digest(raw), g['authorization_bytes_sha256'], g['operator_uid']))


def crash_worker(root, start, cut, pending):
    ledger = fixture_connection(root)
    journal = open_public_fixture(ledger, Path(root))
    if pending:
        journal.claim(start, UID)
        journal.record_reserved(start['operation_id'], H)
    if cut == 'before':
        ledger.db.set_trace_callback(lambda sql: os._exit(71) if sql == 'COMMIT' else None)
    if pending:
        journal.mark_dispatch_pending(start['operation_id'])
    else:
        journal.claim(start, UID)
    os._exit(72)


def race_worker(root, start, barrier, queue, action):
    ledger = fixture_connection(root)
    try:
        journal = open_public_fixture(ledger, Path(root))
        # Real SQLite instrumentation pauses AFTER Ledger's outside-tx tip check.
        def rendezvous(sql):
            if sql == 'BEGIN IMMEDIATE':
                barrier.wait(timeout=10)
        ledger.db.set_trace_callback(rendezvous)
        if action == 'claim':
            record = journal.claim(start, UID)
            result = record.state
        elif action == 'stop':
            result = str(journal.request_stop(start['operation_id'], UID).stop_requested)
        else:
            result = str(journal.mark_dispatch_pending(start['operation_id'])[1] is not None)
        queue.put(('ok', result))
    except Failure as exc:
        queue.put(('refused', exc.record['code']))
    finally:
        ledger.close()


class JournalTests(unittest.TestCase):
    fixture_bytes = []

    def measure_fixture(self, root):
        size = sum(path.stat().st_size for path in Path(root).iterdir() if path.is_file())
        self.assertLess(size, 25 * 1024 * 1024)
        self.fixture_bytes.append(size)

    def tearDown(self):
        self.measure_fixture(self.root)

    @classmethod
    def tearDownClass(cls):
        print('PUBLIC_FIXTURE_MAX_OBSERVED_BYTES=%d; not runtime/UID320 evidence' % max(cls.fixture_bytes))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='capstone-journal-fixture-', dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = fixture_connection(self.root, True)
        self.addCleanup(self.ledger.close)
        self.start, self.raw = fixture_start()
        self.oid = self.start['operation_id']
        install_public_grant(self.ledger.db, self.start, self.raw)
        self.journal = open_public_fixture(self.ledger, self.root)

    def reopen(self):
        ledger = fixture_connection(self.root)
        self.addCleanup(ledger.close)
        return open_public_fixture(ledger, self.root)

    def counts(self):
        return tuple(self.ledger.db.execute('SELECT count(*) FROM ' + t).fetchone()[0]
                     for t in ('events', 'capstone_operations', 'idempotency'))

    def test_claim_exact_replay_and_frozen_record(self):
        record = self.journal.claim(self.start, UID)
        self.assertEqual(record, self.journal.claim(copy.deepcopy(self.start), UID))
        self.assertEqual(record, self.reopen().status(self.oid, UID))
        self.assertEqual(self.counts(), (1, 1, 1))
        self.assertEqual(self.ledger.db.execute('SELECT raw FROM capstone_grants').fetchone()[0], self.raw)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            record.state = 'running'

    def test_changed_consumed_start_and_wrong_operator(self):
        self.journal.claim(self.start, UID)
        changed = copy.deepcopy(self.start)
        changed['plan']['request']['run'] = 'other'
        changed['plan']['plan_sha256'] = content_digest(changed['plan'], 'plan_sha256')
        changed['operation_id'] = operation_id(changed['plan']['grant']['grant_id'], changed['plan']['plan_sha256'])
        for start, uid in ((changed, UID), (self.start, UID + 1), (self.start, True)):
            with self.assertRaises(Failure): self.journal.claim(start, uid)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_counterfeit_and_changed_original_bytes(self):
        fake, _ = fixture_start(99)
        with self.assertRaises(Failure): self.journal.claim(fake, UID)
        changed = copy.deepcopy(self.start)
        for v in (changed['plan'], changed['plan']['observation']):
            v['grant_bytes_sha256'] = digest(canonical(changed['plan']['grant']))
        changed['plan']['observation']['receipt_sha256'] = content_digest(changed['plan']['observation'], 'receipt_sha256')
        changed['plan']['plan_sha256'] = content_digest(changed['plan'], 'plan_sha256')
        changed['operation_id'] = operation_id(changed['plan']['grant']['grant_id'], changed['plan']['plan_sha256'])
        with self.assertRaises(Failure): self.journal.claim(changed, UID)
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_production_denies_before_effect_and_fixture_lexical_guard(self):
        self.assertNotEqual(UID, EVALUATOR, 'This suite requires its actual unprivileged host UID')
        with patch.object(Path, 'stat', side_effect=AssertionError('metadata forbidden')):
            with self.assertRaises(Failure): open_existing(object())
            for path in ('/Library/GRRR', '/private/tmp/../GRRR', '/tmp/other'):
                with self.assertRaises(Failure): open_public_fixture(object(), Path(path))

    def test_missing_changed_extra_schema_refused_without_repair(self):
        for sql in ('DROP TRIGGER capstone_grants_update',
                    'CREATE INDEX capstone_extra ON capstone_operations(grant_id)',
                    'CREATE TRIGGER extra BEFORE INSERT ON events BEGIN SELECT 1; END',
                    'ALTER TABLE capstone_operations ADD COLUMN unexpected TEXT',
                    'CREATE TEMP TABLE events(x)', 'DROP TABLE capstone_operations'):
            with self.subTest(sql=sql):
                self.ledger.db.execute('SAVEPOINT corruption')
                self.ledger.db.execute(sql)
                before = self.ledger.db.total_changes
                # Factory correctly refuses active transactions; validate snapshot separately.
                from capstone_journal_schema import validate_schema
                with self.assertRaises(Failure): validate_schema(self.ledger.db)
                self.assertEqual(before, self.ledger.db.total_changes)
                self.ledger.db.execute('ROLLBACK TO corruption')
                self.ledger.db.execute('RELEASE corruption')
        self.ledger.db.execute('DROP TRIGGER capstone_grants_update')
        with self.assertRaises(Failure): self.reopen()
        self.assertIsNone(self.ledger.db.execute("SELECT name FROM sqlite_master WHERE name='capstone_grants_update'").fetchone())

    def test_corrupt_rows_and_settings_refused(self):
        self.journal.claim(self.start, UID)
        original = self.ledger.db.execute('SELECT record FROM capstone_operations').fetchone()[0]
        for raw in (b'{}', b'garbage', original.replace(b'claimed', b'unknown')):
            self.ledger.db.execute('UPDATE capstone_operations SET record=?', (raw,))
            with self.assertRaises(Failure): self.reopen()
        self.ledger.db.execute('UPDATE capstone_operations SET record=?', (original,))
        self.ledger.db.execute('DELETE FROM idempotency')
        with self.assertRaises(Failure): self.reopen()

    def test_corrupt_grant_refused_even_with_restored_schema(self):
        self.ledger.db.execute('DROP TRIGGER capstone_grants_update')
        self.ledger.db.execute('UPDATE capstone_grants SET raw=?', (self.raw + b" ",))
        self.ledger.db.execute(JOURNAL_SQL[2])
        with self.assertRaises(Failure): self.reopen()

    def test_corrupt_core_chain_refused(self):
        self.journal.claim(self.start, UID)
        self.ledger.db.execute('DROP TRIGGER immutable_update')
        self.ledger.db.execute('UPDATE events SET prior=?', (H,))
        self.ledger.db.execute(CORE_SQL[2])
        with self.assertRaises(Failure): self.reopen()

    def test_boolean_event_version_refused_despite_consistent_hash(self):
        body = canonical(dict(format='public-fixture', idempotency_key='version-check', version=True))
        prior = '0' * 64
        hashed = digest(prior.encode() + body)
        self.ledger.db.execute('INSERT INTO events VALUES(1,?,?,?)', (prior, hashed, body))
        self.ledger.db.execute('INSERT INTO idempotency VALUES(?,1,?,?,?)',
                               ('version-check', prior, hashed, body))
        with self.assertRaises(Failure): self.reopen()

    def test_durability_settings_and_attached_database_refused(self):
        for pragma in ('PRAGMA foreign_keys=OFF', 'PRAGMA synchronous=OFF',
                       "ATTACH DATABASE ':memory:' AS unrelated"):
            ledger = fixture_connection(self.root)
            try:
                ledger.db.execute(pragma)
                with self.assertRaises(Failure): open_public_fixture(ledger, self.root)
            finally:
                ledger.close()

    def test_reservation_immutable_stop_monotonic_status_select_only(self):
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        with self.assertRaises(Failure): self.journal.record_reserved(self.oid, 'c' * 64)
        self.journal.request_stop(self.oid, UID)
        before = self.ledger.db.total_changes
        trace = []
        self.ledger.db.set_trace_callback(trace.append)
        self.assertTrue(self.journal.status(self.oid, UID).stop_requested)
        self.assertTrue(self.journal.request_stop(self.oid, UID).stop_requested)
        with self.assertRaises(Failure): self.journal.mark_dispatch_pending(self.oid)
        self.ledger.db.set_trace_callback(None)
        self.assertEqual(before, self.ledger.db.total_changes)
        self.assertFalse(any(sql.startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'COMMIT')) for sql in trace))
        for uid in (UID + 1, True):
            with self.assertRaises(Failure): self.journal.request_stop(self.oid, uid)
            with self.assertRaises(Failure): self.journal.status(self.oid, uid)

    def test_unknown_operations_and_invalid_pending(self):
        for call in (lambda: self.journal.status(H, UID), lambda: self.journal.request_stop(H, UID),
                     lambda: self.journal.record_reserved(H, H), lambda: self.journal.mark_dispatch_pending(H)):
            with self.assertRaises(Failure): call()
        self.journal.claim(self.start, UID)
        with self.assertRaises(Failure): self.journal.mark_dispatch_pending(self.oid)
        self.journal.request_stop(self.oid, UID)
        with self.assertRaises(Failure): self.journal.record_reserved(self.oid, H)

    def test_permit_single_use_nonserializable_and_no_reopen_renewal(self):
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        record, permit = self.journal.mark_dispatch_pending(self.oid)
        self.assertEqual(record.state, 'dispatch-pending')
        self.assertIsInstance(permit, DispatchPermit)
        for copier in (copy.copy, copy.deepcopy, pickle.dumps):
            with self.assertRaises(TypeError): copier(permit)
        successes = []
        def consume():
            try:
                permit.consume()
                successes.append(True)
            except Failure:
                return
        threads = [threading.Thread(target=consume) for _ in range(8)]
        for t in threads: t.start()
        for t in threads: t.join(5); self.assertFalse(t.is_alive())
        self.assertEqual(successes, [True])
        self.assertIsNone(self.journal.mark_dispatch_pending(self.oid)[1])
        self.assertIsNone(self.reopen().mark_dispatch_pending(self.oid)[1])

    def test_cached_ledger_append_does_not_invoke_callback(self):
        # Actual Ledger cache path, not a mocked successful append.
        event = dict(format='public-cache-fixture')
        receipt = self.ledger.append_atomic(EVALUATOR, event, '0' * 64, 'cache')
        def forbidden(db, receipt):
            self.fail('Cached callback must not execute')
        self.assertEqual(receipt, self.ledger.append_atomic(EVALUATOR, event, '0' * 64, 'cache', forbidden))
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        self.assertIsNotNone(self.journal.mark_dispatch_pending(self.oid)[1])
        self.assertIsNone(self.journal.mark_dispatch_pending(self.oid)[1])

    def test_actual_cached_pending_append_cannot_mint(self):
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        self.journal.mark_dispatch_pending(self.oid)
        seq, prior, raw = self.ledger.db.execute('SELECT seq,prior,body FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        import json
        value = json.loads(raw)['record']
        # Force a stale preparation into the private helper, exercising the REAL
        # Ledger cached append (which skips callback). No storage is mocked.
        def stale_prepare(grants, records, tip, count):
            return value, True, prior, seq - 1
        before = self.counts()
        with self.assertRaises(Failure) as caught:
            self.journal._change('pending', stale_prepare)
        self.assertEqual(caught.exception.record['code'], 'RecoveryRequired')
        self.assertEqual(self.counts(), before)
        self.assertIsNone(self.reopen().mark_dispatch_pending(self.oid)[1])

    def test_persisted_unknown_never_repairs_or_renews(self):
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        self.journal.mark_dispatch_pending(self.oid)
        import json
        raw = self.ledger.db.execute('SELECT record FROM capstone_operations').fetchone()[0]
        value = json.loads(raw)
        value['state'] = 'unknown'
        self.ledger.db.execute('UPDATE capstone_operations SET record=?', (canonical(value),))
        before = self.ledger.db.total_changes
        with self.assertRaises(Failure): self.reopen()
        with self.assertRaises(Failure): self.journal.mark_dispatch_pending(self.oid)
        self.assertEqual(before, self.ledger.db.total_changes)

    def test_permit_refuses_after_real_fork(self):
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        _, permit = self.journal.mark_dispatch_pending(self.oid)
        pid = os.fork()
        if pid == 0:
            try:
                permit.consume()
            except Failure:
                os._exit(0)
            os._exit(1)
        _, status = os.waitpid(pid, 0)
        self.assertEqual(status, 0)
        permit.consume()

    def test_real_rollback_and_crash_cuts(self):
        ctx = multiprocessing.get_context('spawn')
        for pending in (False, True):
            for cut in ('before', 'after'):
                with self.subTest(pending=pending, cut=cut):
                    with tempfile.TemporaryDirectory(prefix='capstone-journal-fixture-', dir='/private/tmp') as root:
                        ledger = fixture_connection(root, True)
                        install_public_grant(ledger.db, self.start, self.raw)
                        ledger.close()
                        process = ctx.Process(target=crash_worker, args=(root, self.start, cut, pending))
                        process.start(); process.join(15)
                        if process.is_alive(): process.kill(); process.join(); self.fail('Crash child timed out')
                        self.assertEqual(process.exitcode, 71 if cut == 'before' else 72)
                        self.measure_fixture(root)
                        ledger = fixture_connection(root)
                        try:
                            journal = open_public_fixture(ledger, Path(root))
                            if not pending and cut == 'before':
                                self.assertEqual(ledger.db.execute('SELECT count(*) FROM events').fetchone()[0], 0)
                                self.assertIsNone(ledger.db.execute('SELECT consumed_by FROM capstone_grants').fetchone()[0])
                                self.assertEqual(journal.claim(self.start, UID).state, 'claimed')
                            else:
                                expected = 'reserved' if cut == 'before' else ('dispatch-pending' if pending else 'claimed')
                                self.assertEqual(journal.claim(self.start, UID).state, expected)
                                if pending and cut == 'after':
                                    self.assertIsNone(journal.mark_dispatch_pending(self.oid)[1])
                        finally:
                            ledger.close()

    def run_race(self, starts, actions, processes):
        if processes:
            ctx = multiprocessing.get_context('spawn')
            barrier, queue = ctx.Barrier(2), ctx.Queue()
            workers = [ctx.Process(target=race_worker, args=(str(self.root), s, barrier, queue, a))
                       for s, a in zip(starts, actions)]
        else:
            import queue as queues
            barrier, queue = threading.Barrier(2), queues.Queue()
            workers = [threading.Thread(target=race_worker, args=(str(self.root), s, barrier, queue, a))
                       for s, a in zip(starts, actions)]
        for worker in workers: worker.start()
        for worker in workers:
            worker.join(15)
            if processes and worker.is_alive(): worker.kill(); worker.join()
            self.assertFalse(worker.is_alive())
            if processes: self.assertEqual(worker.exitcode, 0)
        results = [queue.get(timeout=2) for _ in workers]
        if processes: queue.close(); queue.join_thread()
        self.assertEqual(sum(r[0] == 'ok' for r in results), 1, results)
        return results

    def test_same_grant_separate_process_race(self):
        self.run_race([self.start] * 2, ['claim'] * 2, True)
        self.assertEqual(self.reopen().status(self.oid, UID).state, 'claimed')
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_same_grant_separate_connection_thread_race(self):
        self.run_race([self.start] * 2, ['claim'] * 2, False)
        self.assertEqual(self.counts(), (1, 1, 1))
        self.reopen()

    def test_shared_connection_thread_claims_are_status_only_after_first(self):
        records, errors = [], []
        def claim():
            try:
                records.append(self.journal.claim(self.start, UID))
            except BaseException as exc:
                errors.append(exc)
        threads = [threading.Thread(target=claim) for _ in range(6)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(5); self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(len(records), 6)
        self.assertEqual(len(set(records)), 1)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_different_grants_separate_process_stale_tip_race(self):
        other, raw = fixture_start(1)
        install_public_grant(self.ledger.db, other, raw)
        self.run_race([self.start, other], ['claim'] * 2, True)
        for start in (self.start, other): self.journal.claim(start, UID)
        self.assertEqual(self.counts(), (2, 2, 2))
        self.reopen()

    def test_different_grants_separate_connection_thread_race(self):
        other, raw = fixture_start(2)
        install_public_grant(self.ledger.db, other, raw)
        self.run_race([self.start, other], ['claim'] * 2, False)
        for start in (self.start, other): self.journal.claim(start, UID)
        self.reopen()
        self.assertEqual(self.counts(), (2, 2, 2))

    def test_stop_pending_separate_process_race(self):
        self.journal.claim(self.start, UID)
        self.journal.record_reserved(self.oid, H)
        self.run_race([self.start] * 2, ['stop', 'pending'], True)
        current = self.reopen().status(self.oid, UID)
        self.assertTrue(current.stop_requested or current.state == 'dispatch-pending')
        self.journal.request_stop(self.oid, UID)
        if current.state == 'dispatch-pending':
            self.assertIsNone(self.journal.mark_dispatch_pending(self.oid)[1])
        else:
            with self.assertRaises(Failure): self.journal.mark_dispatch_pending(self.oid)

    def test_suite_rejects_empty_skipped_and_failed(self):
        from unit_capstone_journal_suite import failed
        class Cases(unittest.TestCase):
            @unittest.skip('deliberate runner negative test')
            def test_skip(self): self.fail('skip decorator did not run')
            def test_failure(self): self.fail('deliberate runner negative test')
            def test_error(self): raise ValueError('deliberate runner negative error')
        suites = [unittest.TestSuite()] + [unittest.TestSuite([Cases(name)])
                  for name in ('test_skip', 'test_failure', 'test_error')]
        for suite in suites:
            result = unittest.TestResult()
            suite.run(result)
            self.assertTrue(failed(result))
