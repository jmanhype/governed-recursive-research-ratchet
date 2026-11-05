"""Real public SQLite index fixtures; NOT installed authority or live proof."""
import base64
import copy
import os
import multiprocessing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from common import Failure, canonical, digest
from capstone_backend_index import (open_existing, open_public_fixture, apply_backend_stop,
                                     _domain, _spec)
from capstone_backend_schema import BACKEND_SQL, TABLE_COLUMNS, validate_schema
from unit_capstone_journal import fixture_connection, fixture_start

H = 'a' * 64


def race_intent(root, record, key, barrier, queue):
    ledger = fixture_connection(root)
    try:
        index = open_public_fixture(ledger, Path(root))
        def rendezvous(sql):
            if sql == 'BEGIN IMMEDIATE':
                barrier.wait(timeout=10)
        ledger.db.set_trace_callback(rendezvous)
        index.append_transition('issuance-intent', record, key)
        queue.put('committed')
    except Failure:
        queue.put('refused')
    except BaseException as exc:
        queue.put(type(exc).__name__)
    finally:
        ledger.close()


def crash_intent(root, record, key, cut):
    ledger = fixture_connection(root)
    index = open_public_fixture(ledger, Path(root))
    if cut == 'before-commit':
        ledger.db.set_trace_callback(lambda sql: os._exit(71) if sql == 'COMMIT' else None)
    index.append_transition('issuance-intent', record, key)
    os._exit(72)


def raw(data):
    return base64.b64encode(data).decode('ascii')


def issuance_fixture():
    start, _ = fixture_start()
    grant = start['plan']['grant']
    shared = dict(grant['bindings'])
    shared.pop('invocation_bytes_sha256')
    maximum = dict(currency='USD', money_cents=2, execution_us=2, review_us=2)
    each = dict(currency='USD', money_cents=1, execution_us=1, review_us=1)
    leaves = [dict(index=i, pair_id=H, purpose='corpus', challenge='public-fixture',
                   role=('baseline', 'candidate')[i], attempt=0, maximum=each,
                   predecessor=None if i == 0 else 0, run='fixture-' + str(i)) for i in range(2)]
    skeleton = dict(schema='capstone-campaign-skeleton-v1', campaign_id='public-campaign',
                    shared_bindings=shared, policy=shared['policy'], coverage=H,
                    maximum=maximum, expires_ns=1000, leaves=leaves)
    sh = _domain('campaign-skeleton-v1', skeleton)
    spec = {k: copy.deepcopy(v) for k, v in skeleton.items() if k != 'leaves'}
    spec.update(schema='capstone-campaign-spec-v1', leaves=[])
    for original in leaves:
        leaf = dict(original)
        run = leaf.pop('run')
        scope = _domain('leaf-scope-v1', dict(skeleton=sh, index=leaf['index']))
        invocation = canonical(dict(run=run, scope=scope, maximum=each))
        leaf.update(invocation_raw=raw(invocation), request=dict(schema='capstone-request-v1',
                    run=run, scope=scope, maximum=each,
                    bindings=dict(shared, invocation_bytes_sha256=digest(invocation))))
        leaf['leaf_id'] = _domain('campaign-leaf-v1', leaf)
        spec['leaves'].append(leaf)
    auth = dict(schema='capstone-authorization-v1', action='capstone-execute',
                operator_uid=os.getuid(), campaign_spec_sha256=digest(canonical(spec)),
                baseline_endorsement_sha256=H, installation_sha256=H,
                not_before_ns=0, expires_ns=1000, maximum=maximum,
                leaf_ids=[leaf['leaf_id'] for leaf in spec['leaves']], review_anchor=H)
    row = dict(auth_hash=digest(canonical(auth)), campaign_id=spec['campaign_id'], issuance_id=H,
               spec_hash=digest(canonical(spec)), registry_hash=H, auth_raw=raw(canonical(auth)),
               spec_raw=raw(canonical(spec)), phase='intent', bundle_raw=None, issued_anchor=None)
    return row, spec, auth, grant


class BackendIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='capstone-journal-fixture-', dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = fixture_connection(self.root, create=True)
        self.addCleanup(self.ledger.close)
        self.index = open_public_fixture(self.ledger, self.root, create=True)
        self.row, self.spec, self.auth, self.grant = issuance_fixture()

    def tearDown(self):
        size = sum(p.stat().st_size for p in self.root.iterdir() if p.is_file())
        self.assertLess(size, 2 * 1024 * 1024)

    def intent(self):
        key = _domain('issue-intent-v1', {'authorization': self.row['auth_hash']})
        record = [dict(table='backend_v2_issuance', rows=[self.row])]
        return self.index.append_transition('issuance-intent', record, key), record, key

    def commit_material(self):
        receipt, _, _ = self.intent()
        entries, leaves = [], []
        for leaf in self.spec['leaves']:
            grant = copy.deepcopy(self.grant)
            gid = _domain('issued-leaf-grant-v1', dict(issuance_id=H, authorization=self.row['auth_hash'],
                         spec=self.row['spec_hash'], leaf_id=leaf['leaf_id']))
            grant.update(grant_id=gid, operator_uid=os.getuid(),
                         authorization_bytes_sha256=self.row['auth_hash'],
                         issuance_anchor=receipt['digest'], review_anchor=H, bindings=leaf['request']['bindings'])
            grant['bounds'].update(scope=leaf['request']['scope'], maximum=leaf['maximum'],
                                   not_before_ns=0, expires_ns=1000)
            entries.append(dict(leaf_id=leaf['leaf_id'], grant_raw=raw(canonical(grant))))
            leaves.append(dict(campaign_id=self.row['campaign_id'], leaf_index=leaf['index'],
                               leaf_id=leaf['leaf_id'], grant_id=gid, request_run=leaf['request']['run'],
                               request_hash=digest(canonical(leaf['request']))))
        bundle = dict(schema='capstone-grant-bundle-v1', campaign_spec_sha256=self.row['spec_hash'], grants=entries)
        row = dict(self.row, phase='issued', intent_anchor=receipt['digest'], bundle_raw=raw(canonical(bundle)))
        del row['issued_anchor']
        campaign = dict(campaign_id=self.row['campaign_id'], issuance_id=H,
                        control_run=_domain('campaign-control-v1', dict(issuance_id=H, campaign_id=self.row['campaign_id'])),
                        stopped=0, stop_epoch=0, stop_operation=None, stop_anchor=None)
        record = [dict(table='backend_v2_issuance', rows=[row]),
                  dict(table='backend_v2_campaign', rows=[campaign]), dict(table='backend_v2_leaf', rows=leaves)]
        key = _domain('issue-commit-v1', dict(authorization=self.row['auth_hash']))
        return record, key

    def commit(self):
        record, key = self.commit_material()
        return self.index.append_transition('issuance-commit', record, key)

    def test_empty_open_has_no_authority_or_mutation(self):
        self.assertTrue(all(not rows for rows in self.index.validate().values()))
        self.assertEqual(self.ledger.tip(), '0' * 64)
        self.assertFalse(hasattr(self.index, 'permit'))
        open_public_fixture(self.ledger, self.root)

    def test_exact_schema_and_indexes(self):
        validate_schema(self.ledger.db)
        for table, columns in TABLE_COLUMNS.items():
            actual = tuple(row[1] for row in self.ledger.db.execute('PRAGMA table_info(backend_v2_' + table + ')'))
            self.assertEqual(columns, actual)

    def test_intent_roundtrip_and_cached_retry(self):
        receipt, record, key = self.intent()
        self.assertEqual(self.index.append_transition('issuance-intent', record, key), receipt)
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM events').fetchone(), (1,))
        row = next(iter(self.index.validate()['issuance'].values()))
        self.assertEqual(row['intent_anchor'], receipt['digest'])
        self.assertEqual(row['auth_raw'], canonical(self.auth))
        self.assertIsNone(row['bundle_raw'])

    def test_commit_finite_original_grants_and_reopen(self):
        receipt = self.commit()
        state = open_public_fixture(self.ledger, self.root).validate()
        self.assertEqual(len(state['leaf']), 2)
        self.assertEqual(len(state['binding']), 0)
        self.assertEqual(next(iter(state['issuance'].values()))['issued_anchor'], receipt['digest'])
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM capstone_grants WHERE consumed_by IS NULL').fetchone(), (2,))

    def test_reopened_intent_cannot_resume_or_mint_grants(self):
        record, key = self.commit_material()
        reopened = open_public_fixture(self.ledger, self.root)
        # Even retrying the original intent does not recreate invocation ownership.
        intent_key = _domain('issue-intent-v1', {'authorization': self.row['auth_hash']})
        reopened.append_transition('issuance-intent', [dict(table='backend_v2_issuance', rows=[self.row])], intent_key)
        with self.assertRaises(Failure):
            reopened.append_transition('issuance-commit', record, key)
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM capstone_grants').fetchone(), (0,))

    def test_changed_retry_rejected_without_event(self):
        _, record, key = self.intent()
        record[0]['rows'][0]['registry_hash'] = 'b' * 64
        with self.assertRaises(Failure):
            self.index.append_transition('issuance-intent', record, key)
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM events').fetchone(), (1,))

    def test_commit_extra_missing_or_changed_leaf_rollback(self):
        record, key = self.commit_material()
        for rows in ([], record[2]['rows'][:1], record[2]['rows'] * 2):
            bad = copy.deepcopy(record)
            bad[2]['rows'] = rows
            with self.assertRaises(Failure):
                self.index.append_transition('issuance-commit', bad, key)
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM capstone_grants').fetchone(), (0,))
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM events').fetchone(), (1,))

    def test_sql_commit_failure_rolls_back_grants_and_events(self):
        record, key = self.commit_material()
        def cut(action, arg1, arg2, database, trigger):
            return sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_INSERT and arg1 == 'backend_v2_leaf' else sqlite3.SQLITE_OK
        self.ledger.db.set_authorizer(cut)
        with self.assertRaises(Failure):
            self.index.append_transition('issuance-commit', record, key)
        # Python 3.9 does not support clearing the authorizer with None.
        self.ledger.db.set_authorizer(lambda *args: sqlite3.SQLITE_OK)
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM capstone_grants').fetchone(), (0,))
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM events').fetchone(), (1,))

    def test_unknown_action_denied(self):
        with self.assertRaises(Failure):
            self.index.append_transition('magic', [], H)
        self.assertEqual(self.ledger.tip(), '0' * 64)

    def test_schema_addition_denied(self):
        self.ledger.db.execute('CREATE INDEX extra_leaf ON backend_v2_leaf(request_hash)')
        with self.assertRaises(Failure):
            self.index.validate()

    def test_unknown_namespace_object_denied(self):
        self.ledger.db.execute('CREATE TABLE backend_v2_surprise(x)')
        with self.assertRaises(Failure):
            self.index.validate()

    def test_temp_shadow_denied(self):
        self.ledger.db.execute('CREATE TEMP TABLE backend_v2_campaign(x)')
        with self.assertRaises(Failure):
            self.index.validate()

    def test_mutable_guards_and_delete_guards(self):
        self.commit()
        for sql in ('DELETE FROM backend_v2_issuance', 'DELETE FROM backend_v2_leaf',
                    "UPDATE backend_v2_issuance SET phase='intent'",
                    "UPDATE backend_v2_leaf SET request_run='changed'",
                    'UPDATE backend_v2_campaign SET stopped=0'):
            with self.assertRaises(sqlite3.IntegrityError):
                self.ledger.db.execute(sql)

    def test_missing_event_rows_rejected(self):
        self.intent()
        self.ledger.db.execute('DROP TRIGGER backend_v2_issuance_no_delete')
        self.ledger.db.execute('DELETE FROM backend_v2_issuance')
        self.ledger.db.execute(next(sql for sql in BACKEND_SQL if sql.startswith('CREATE TRIGGER backend_v2_issuance_no_delete')))
        with self.assertRaises(Failure):
            self.index.validate()

    def test_blob_tamper_rejected_after_guard_restoration(self):
        self.intent()
        self.ledger.db.execute('DROP TRIGGER backend_v2_issuance_guard_update')
        self.ledger.db.execute('UPDATE backend_v2_issuance SET auth_raw=?', (b'{}',))
        self.ledger.db.execute(next(sql for sql in BACKEND_SQL if sql.startswith('CREATE TRIGGER backend_v2_issuance_guard_update')))
        with self.assertRaises(Failure):
            self.index.validate()

    def test_stop_unplanned_is_atomic_and_does_not_invent_run(self):
        self.commit()
        campaign = next(iter(self.index.validate()['campaign'].values()))
        stop = dict(schema='capstone-campaign-stop-v2', campaign_id=campaign['campaign_id'],
                    control_run=campaign['control_run'], epoch=1, primary_operation=H,
                    affected_operations=[], run_before_revision=None, run_after=None)
        event = dict(kind='safe-stop', run=campaign['control_run'], epoch=1, operation=H, backend_stop=stop)
        receipt = self.ledger.append_atomic(320, event, self.ledger.tip(), 'public-stop',
                    lambda db, receipt: apply_backend_stop(db, receipt, stop))
        state = self.index.validate()
        self.assertEqual(next(iter(state['campaign'].values()))['stop_anchor'], receipt['digest'])
        self.assertFalse(state['campaign_run'])
        self.assertFalse(state['binding'])
        self.assertEqual(len(state['leaf']), 2)

    def test_stop_without_transaction_refuses(self):
        with self.assertRaises(Failure):
            apply_backend_stop(self.ledger.db, {}, {})

    def test_extra_original_grant_is_not_backend_issuance(self):
        from unit_capstone_journal import install_public_grant
        start, raw_grant = fixture_start()
        install_public_grant(self.ledger.db, start, raw_grant)
        with self.assertRaises(Failure):
            self.index.validate()

    def test_unknown_owned_format_and_version_refuse(self):
        self.ledger.append(320, dict(format='capstone-backend-event-v99'), self.ledger.tip(), H)
        with self.assertRaises(Failure):
            self.index.validate()

    def test_stop_rollback_and_repeat_preserve_original_anchor(self):
        self.commit()
        campaign = next(iter(self.index.validate()['campaign'].values()))
        stop = dict(schema='capstone-campaign-stop-v2', campaign_id=campaign['campaign_id'],
                    control_run=campaign['control_run'], epoch=1, primary_operation=H,
                    affected_operations=[], run_before_revision=None, run_after=None)
        event = dict(kind='safe-stop', run=campaign['control_run'], operation=H, epoch=1, backend_stop=stop)
        def fail_after(db, receipt):
            apply_backend_stop(db, receipt, stop)
            raise Failure('RecoveryRequired', 'explicit after-stop cut')
        before = self.ledger.tip()
        with self.assertRaises(Failure):
            self.ledger.append_atomic(320, event, before, 'stop-cut', fail_after)
        self.assertEqual(self.ledger.tip(), before)
        self.assertEqual(next(iter(self.index.validate()['campaign'].values()))['stopped'], 0)
        first = self.ledger.append_atomic(320, event, before, 'stop-first',
                    lambda db, receipt: apply_backend_stop(db, receipt, stop))
        repeated = dict(event, kind='safe-stop-reference', primary_operation=H, operation='b' * 64)
        self.ledger.append_atomic(320, repeated, self.ledger.tip(), 'stop-second',
                    lambda db, receipt: apply_backend_stop(db, receipt, stop))
        self.assertEqual(next(iter(self.index.validate()['campaign'].values()))['stop_anchor'], first['digest'])

    def test_stop_wrong_core_linkage_rolls_back(self):
        self.commit()
        campaign = next(iter(self.index.validate()['campaign'].values()))
        stop = dict(schema='capstone-campaign-stop-v2', campaign_id=campaign['campaign_id'],
                    control_run=campaign['control_run'], epoch=1, primary_operation=H,
                    affected_operations=[], run_before_revision=None, run_after=None)
        event = dict(kind='safe-stop', run='wrong-campaign', operation=H, epoch=1, backend_stop=stop)
        before = self.ledger.tip()
        with self.assertRaises(Failure):
            self.ledger.append_atomic(320, event, before, 'wrong-stop',
                        lambda db, receipt: apply_backend_stop(db, receipt, stop))
        self.assertEqual(before, self.ledger.tip())

    def test_intent_process_crash_before_commit_retains_no_rows(self):
        record = [dict(table='backend_v2_issuance', rows=[self.row])]
        key = _domain('issue-intent-v1', {'authorization': self.row['auth_hash']})
        ctx = multiprocessing.get_context('spawn')
        worker = ctx.Process(target=crash_intent, args=(str(self.root), record, key, 'before-commit'))
        worker.start()
        worker.join(15)
        if worker.is_alive():
            worker.terminate()
            worker.join(5)
            self.fail('crash worker exceeded bound')
        self.assertEqual(worker.exitcode, 71)
        self.assertFalse(self.index.validate()['issuance'])

    def test_intent_process_crash_after_commit_retains_original_intent(self):
        record = [dict(table='backend_v2_issuance', rows=[self.row])]
        key = _domain('issue-intent-v1', {'authorization': self.row['auth_hash']})
        ctx = multiprocessing.get_context('spawn')
        worker = ctx.Process(target=crash_intent, args=(str(self.root), record, key, 'after-commit'))
        worker.start()
        worker.join(15)
        if worker.is_alive():
            worker.terminate()
            worker.join(5)
            self.fail('crash worker exceeded bound')
        self.assertEqual(worker.exitcode, 72)
        self.assertEqual(next(iter(self.index.validate()['issuance'].values()))['phase'], 'intent')
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM capstone_grants').fetchone(), (0,))

    def test_connection_pragma_drift_refuses(self):
        self.ledger.db.execute('PRAGMA foreign_keys=OFF')
        with self.assertRaises(Failure):
            self.index.validate()

    def test_attached_database_refuses(self):
        self.ledger.db.execute("ATTACH DATABASE ':memory:' AS alternate")
        with self.assertRaises(Failure):
            self.index.validate()

    def test_real_process_race_rejects_stale_fork_inside_callback(self):
        context = multiprocessing.get_context('spawn')
        barrier, queue = context.Barrier(2), context.Queue()
        record = [dict(table='backend_v2_issuance', rows=[self.row])]
        key = _domain('issue-intent-v1', {'authorization': self.row['auth_hash']})
        workers = [context.Process(target=race_intent, args=(str(self.root), record, key, barrier, queue)) for _ in range(2)]
        try:
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(20)
                self.assertFalse(worker.is_alive())
                self.assertEqual(worker.exitcode, 0)
            self.assertEqual(sorted([queue.get(timeout=2), queue.get(timeout=2)]), ['committed', 'refused'])
        finally:
            for worker in workers:
                if worker.is_alive():
                    worker.terminate()
                    worker.join(5)
            queue.close()
            queue.join_thread()
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM events').fetchone(), (1,))
        self.index.validate()

    def test_public_path_rejected_lexically(self):
        with self.assertRaises(Failure):
            open_public_fixture(self.ledger, Path('/Library/GRRR/not-accessed'))

    def test_production_open_rejects_actual_uid(self):
        self.assertNotEqual(os.getuid(), 320)
        with self.assertRaises(Failure):
            open_existing(None)

    def test_create_false_never_installs(self):
        for sql in BACKEND_SQL:
            if sql.startswith('CREATE TRIGGER '):
                name = sql.split()[2]
                self.ledger.db.execute('DROP TRIGGER ' + name)
        for table in reversed(tuple(TABLE_COLUMNS)):
            self.ledger.db.execute('DROP TABLE backend_v2_' + table)
        with self.assertRaises(Failure):
            open_public_fixture(self.ledger, self.root)
        self.assertEqual(self.ledger.db.execute("SELECT count(*) FROM sqlite_master WHERE name LIKE 'backend_%'").fetchone(), (0,))


if __name__ == '__main__':
    unittest.main()
