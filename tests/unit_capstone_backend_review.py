"""Public independent-store/RPC mechanics, never installed review approval."""
import base64
import copy
import json
import multiprocessing
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

from common import Failure, canonical, digest
from capstone_contract import content_digest, operation_id
from capstone_review import ReviewStore, request_hash, _hash
from capstone_review_service import ReviewClient, ReviewContext, ReviewHandler, ReviewServer, review_call
from unit_capstone_contract import bound_plan

H = 'a' * 64


def raw64(raw):
    return base64.b64encode(raw).decode('ascii')


def fixture_review():
    plan, _, _ = bound_plan()
    now = time.time_ns()
    plan['grant']['bounds'].update(not_before_ns=now - 1_000_000, expires_ns=now + 60_000_000_000,
                                 receipt_max_age_ns=60_000_000_000)
    grant_raw = canonical(plan['grant'])
    plan['grant_bytes_sha256'] = plan['observation']['grant_bytes_sha256'] = digest(grant_raw)
    observation = plan['observation']
    observation.update(observed_ns=now, anchor=dict(ledger_sequence=0, ledger_tip='0' * 64,
                       accounting_snapshot=H, grant_registry_snapshot=H, installation=H))
    observation['receipt_sha256'] = content_digest(observation, 'receipt_sha256')
    plan['plan_sha256'] = content_digest(plan, 'plan_sha256')
    # Opaque root bytes here test storage/transport, not full campaign joins.
    # Full root/static approvals MUST be resolved by the integrated verifier.
    request = dict(action='review-plan', version=2, campaign_operation_id='c' * 64,
                   leaf_id='d' * 64, campaign_plan_raw=raw64(b'{}'), actual_plan_raw=raw64(canonical(plan)))
    request['request_sha256'] = _hash('jit-review-request-v2', request)
    review = dict(schema='capstone-jit-review-v2', phase='actual-plan-prelaunch', verdict='pass',
                  reviewer_identity=H, verifier_inventory=H, policy_sha256=H, source_review_sha256=H,
                  static_review_sha256=H, authorization_bytes_sha256=plan['authorization_bytes_sha256'],
                  campaign_spec_sha256=H, campaign_plan_sha256=H, leaf_id=request['leaf_id'],
                  grant_bytes_sha256=digest(grant_raw),
                  operation_id=operation_id(plan['grant']['grant_id'], plan['plan_sha256']),
                  actual_plan_sha256=plan['plan_sha256'], actual_plan_bytes_sha256=digest(canonical(plan)),
                  observation_sha256=digest(canonical(observation)), service_epoch=observation['service_epoch'],
                  anchor=observation['anchor'], reviewed_ns=now, expires_ns=now + 30_000_000_000,
                  evidence=[H], blockers=[])
    return plan, request, review


def expected(review):
    omit = {'schema', 'phase', 'verdict', 'reviewed_ns', 'expires_ns', 'blockers'}
    return {k: v for k, v in review.items() if k not in omit}


def review_process(root, request, review, pipe):
    store, server = None, None
    try:
        root = Path(root)
        store = ReviewStore.open_public_fixture(root)

        def verifier(incoming):
            if incoming != request:
                raise Failure('StaleBinding', 'Fixture finite request differs')
            plan = json.loads(base64.b64decode(incoming['actual_plan_raw']))
            receipt = plan['observation']
            response = review_call(root / 'context.sock', dict(action='review-context', version=2,
                campaign_operation_id=incoming['campaign_operation_id'], leaf_id=incoming['leaf_id'],
                actual_plan_bytes_sha256=digest(canonical(plan)), nonce=receipt['nonce'],
                service_epoch=receipt['service_epoch']), expected_uid=os.getuid(), timeout=2)
            if response['observation_raw'] != raw64(canonical(receipt)) or response['anchor'] != receipt['anchor']:
                raise Failure('StaleBinding', 'Independent retained context differs')
            return canonical(review)

        server = ReviewServer.open_public_fixture(root, ReviewHandler(store, verifier), role='reviewer')
        pipe.send('ready')
        pipe.recv()
    except BaseException as exc:
        pipe.send(('error', type(exc).__name__, str(exc)))
    finally:
        if server:
            server.close()
        if store:
            store.close()
        pipe.close()


def concurrent_reviewer(root, request, review, barrier, queue, crash=False):
    store = ReviewStore.open_public_fixture(Path(root))
    try:
        if barrier is not None:
            barrier.wait(5)
        def verify(_):
            if crash:
                os._exit(73)  # real process death AFTER FULL-synchronous intent
            queue.put(('verifier', os.getpid()))
            time.sleep(0.1)
            return canonical(review)
        try:
            result = store.review(request, verify)
            queue.put(('ok', result))
        except Failure as exc:
            queue.put(('refused', exc.record['code']))
    finally:
        store.close()


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-', dir='/private/tmp')
        self.root = Path(self.tmp.name)
        self.store = ReviewStore.open_public_fixture(self.root, create=True)
        self.plan, self.request, self.review = fixture_review()

    def tearDown(self):
        if self.store:
            self.store.close()
        self.tmp.cleanup()

    def test_original_result_idempotent_and_reopens(self):
        result = self.store.review(self.request, lambda r: canonical(self.review))
        def never(_):
            raise AssertionError('A repeated review must not execute verifier')
        self.assertEqual(self.store.review(self.request, never), result)
        self.store.close()
        self.store = ReviewStore.open_public_fixture(self.root)
        self.assertEqual(self.store.get(self.request['request_sha256']), result)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_events').fetchone(), (2,))

    def test_intent_only_never_remints(self):
        def cut(_):
            raise RuntimeError('source crash cut after durable intent')
        with self.assertRaises(RuntimeError):
            self.store.review(self.request, cut)
        self.store.close()
        self.store = ReviewStore.open_public_fixture(self.root)
        with self.assertRaises(Failure) as error:
            self.store.review(self.request, lambda r: canonical(self.review))
        self.assertEqual(error.exception.record['code'], 'RecoveryRequired')
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_events').fetchone(), (1,))

    def test_expired_result_repeated_bytes_unchanged(self):
        self.review.update(reviewed_ns=1, expires_ns=2)
        original = self.store.review(self.request, lambda r: canonical(self.review))
        self.assertEqual(self.store.review(self.request, lambda r: b'bad'), original)

    def test_failed_review_stored_without_remint(self):
        self.review.update(verdict='fail', blockers=['GateBlocked'])
        original = self.store.review(self.request, lambda r: canonical(self.review))
        self.assertEqual(self.store.review(self.request, lambda r: b'bad'), original)

    def test_request_changed_under_key_denied(self):
        self.store.review(self.request, lambda r: canonical(self.review))
        changed = dict(self.request, leaf_id='e' * 64)
        with self.assertRaises(Failure):
            self.store.review(changed, lambda r: canonical(self.review))

    def test_object_corruption_denied(self):
        result = self.store.review(self.request, lambda r: canonical(self.review))
        (self.store.objects / result['review_sha256']).write_bytes(b'corrupt')
        with self.assertRaises(Failure):
            self.store.get(self.request['request_sha256'])

    def test_extra_schema_and_rows_denied(self):
        self.store.db.execute('CREATE TABLE unwanted(x)')
        with self.assertRaises(Failure):
            self.store.get(self.request['request_sha256'])

    def test_sql_update_delete_guards(self):
        self.store.review(self.request, lambda r: canonical(self.review))
        for sql in ('DELETE FROM review_requests', 'DELETE FROM review_events',
                    "UPDATE review_requests SET review_hash='bad'", "UPDATE review_events SET prior='bad'"):
            with self.subTest(sql=sql), self.assertRaises(sqlite3.IntegrityError):
                self.store.db.execute(sql)

    def test_unreferenced_extra_row_denied_by_full_replay(self):
        self.store.db.execute('INSERT INTO review_requests VALUES(?,?,?,NULL,NULL)',
                              (self.request['request_sha256'], canonical(self.request), H))
        with self.assertRaises(Failure):
            self.store.get(self.request['request_sha256'])

    def test_real_process_crash_after_intent_is_not_resumed(self):
        ctx = multiprocessing.get_context('spawn')
        queue = ctx.Queue()
        process = ctx.Process(target=concurrent_reviewer,
                              args=(str(self.root), self.request, self.review, None, queue, True))
        process.start()
        process.join(5)
        if process.is_alive():
            process.terminate(); process.join(2)
        queue.close(); queue.join_thread()
        self.assertEqual(process.exitcode, 73)
        with self.assertRaises(Failure) as error:
            self.store.review(self.request, lambda r: canonical(self.review))
        self.assertEqual(error.exception.record['code'], 'RecoveryRequired')
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_events').fetchone(), (1,))

    def collect_review_outcomes(self, processes, queue, count):
        # Queue feeder threads can keep a child alive until the parent drains
        # its result. Joining first deadlocks once results fill the pipe. Keep
        # the same exit/time bounds and validate every outcome; do not hide a
        # failed or killed reviewer as successful review evidence.
        try:
            records = [queue.get(timeout=5) for _ in range(count)]
        finally:
            for process in processes:
                process.join(5)
                if process.is_alive():
                    process.terminate(); process.join(2)
            queue.close(); queue.join_thread()
        for process in processes:
            self.assertEqual(process.exitcode, 0)
        return records

    def test_concurrent_reviewers_never_mint_twice(self):
        ctx = multiprocessing.get_context('spawn')
        barrier, queue = ctx.Barrier(2), ctx.Queue()
        processes = [ctx.Process(target=concurrent_reviewer,
                     args=(str(self.root), self.request, self.review, barrier, queue)) for _ in range(2)]
        for process in processes:
            process.start()
        # Exactly two operation outcomes plus one actual verifier execution.
        records = self.collect_review_outcomes(processes, queue, 3)
        self.assertEqual(sum(r[0] == 'verifier' for r in records), 1)
        self.assertGreaterEqual(sum(r[0] == 'ok' for r in records), 1)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_requests').fetchone(), (1,))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_events').fetchone(), (2,))

    def test_large_cached_results_drain_before_join_without_new_verifier(self):
        # Two independently opened reviewers returning cached payloads exercise
        # backpressure without changing the one-verifier/one-result contract.
        self.review['evidence'] = sorted({H} | {digest(str(i).encode()) for i in range(8192)})
        original = self.store.review(self.request, lambda r: canonical(self.review))
        self.assertGreater(len(canonical(original)), 128*1024)
        ctx = multiprocessing.get_context('spawn')
        barrier, queue = ctx.Barrier(2), ctx.Queue()
        processes = [ctx.Process(target=concurrent_reviewer,
                     args=(str(self.root), self.request, self.review, barrier, queue)) for _ in range(2)]
        for process in processes:
            process.start()
        records = self.collect_review_outcomes(processes, queue, 2)
        self.assertEqual(records, [('ok', original), ('ok', original)])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_requests').fetchone(), (1,))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM review_events').fetchone(), (2,))

    def test_actual_reviewer_uid_required_before_protected_access(self):
        with self.assertRaises(Failure):
            ReviewStore.open_existing()

    def test_fixture_lexical_rejection_before_protected_access(self):
        with self.assertRaises(Failure):
            ReviewStore.open_public_fixture(Path('/Library/GRRR'))

    def test_context_wrong_nonce_and_owner_loss(self):
        owner = object()
        live = [owner]
        def current(campaign, leaf, supplied, raw, receipt):
            if live[0] is not supplied:
                raise Failure('RecoveryRequired', 'Live owner lost')
        context = ReviewContext(current)
        context.register(self.request['campaign_operation_id'], self.request['leaf_id'],
                         canonical(self.plan), canonical(self.plan['observation']), owner)
        request = dict(action='review-context', version=2, campaign_operation_id=self.request['campaign_operation_id'],
                       leaf_id=self.request['leaf_id'], actual_plan_bytes_sha256=digest(canonical(self.plan)),
                       nonce=self.plan['observation']['nonce'], service_epoch=self.plan['observation']['service_epoch'])
        self.assertEqual(context.handle(request)['anchor'], self.plan['observation']['anchor'])
        with self.assertRaises(Failure):
            context.handle(dict(request, nonce='e' * 64))
        live[0] = None
        with self.assertRaises(Failure):
            context.handle(request)
        context.close()
        with self.assertRaises(Failure):
            context.handle(request)

    def rpc_case(self, *, expired=False, changed_anchor=False, wrong_expected=False):
        if expired:
            self.review.update(reviewed_ns=1, expires_ns=2)
        owner = object()
        current_anchor = [copy.deepcopy(self.plan['observation']['anchor'])]
        def current(campaign, leaf, supplied, raw, receipt):
            if supplied is not owner or receipt['anchor'] != current_anchor[0]:
                raise Failure('StaleBinding', 'Current owner/anchor differs')
        context = ReviewContext(current)
        context.register(self.request['campaign_operation_id'], self.request['leaf_id'],
                         canonical(self.plan), canonical(self.plan['observation']), owner)
        server = ReviewServer.open_public_fixture(self.root, context, role='context')
        ctx = multiprocessing.get_context('spawn')
        parent, child = ctx.Pipe()
        process = ctx.Process(target=review_process, args=(str(self.root), self.request, self.review, child))
        process.start()
        child.close()
        try:
            self.assertTrue(parent.poll(5))
            self.assertEqual(parent.recv(), 'ready')
            if changed_anchor:
                current_anchor[0]['ledger_tip'] = 'f' * 64
            expected_value = expected(self.review)
            if wrong_expected:
                expected_value['verifier_inventory'] = 'f' * 64
            client = ReviewClient.open_public_fixture(self.root)
            if expired or changed_anchor or wrong_expected:
                with self.assertRaises(Failure):
                    client.review_and_get(self.request, expected_value)
            else:
                self.assertEqual(client.review_and_get(self.request, expected_value), canonical(self.review))
                self.assertEqual(client.identity, 'NONPRODUCTION')
                self.assertEqual(client.review_and_get(self.request, expected_value), canonical(self.review))
        finally:
            parent.send('stop')
            process.join(5)
            if process.is_alive():
                process.terminate()
                process.join(2)
            parent.close()
            server.close()
            context.close()
            self.assertEqual(process.exitcode, 0)

    def test_independent_process_review_context_roundtrip_no_deadlock(self):
        self.rpc_case()

    def test_expired_review_denies_client(self):
        self.rpc_case(expired=True)

    def test_intervening_anchor_change_denies_review(self):
        self.rpc_case(changed_anchor=True)

    def test_wrong_verifier_inventory_denies_client(self):
        self.rpc_case(wrong_expected=True)


if __name__ == '__main__':
    unittest.main()
