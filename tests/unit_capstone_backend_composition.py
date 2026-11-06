"""Two JIT public journal/reviewer/rights/child sends, not a completed backend.

This deliberately does NOT fabricate campaign issuance, v5 accounting, complete
phase evidence, or a root Manifest. Fixture grants/reservations are explicit;
the test proves composition of implemented mechanics and unchanged v1 Journal.
"""
import copy
import multiprocessing
import os
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
import time
import unittest

from common import Failure, canonical, digest
from capstone_contract import bind_observation, content_digest, operation_id
from capstone_journal import open_public_fixture
from capstone_launch import Gate, LaunchBroker, send_ticket
from capstone_review import ReviewStore, _hash
from capstone_review_service import ReviewClient, ReviewContext, ReviewServer
from unit_capstone_backend_launch import ticket
from unit_capstone_backend_review import fixture_review, expected, raw64, review_process
from unit_capstone_journal import fixture_connection, install_public_grant


def composition_broker_worker(root, conn, pipe, operation):
    db = sqlite3.connect(str(Path(root) / 'owned.sqlite'), isolation_level=None)
    db.execute('PRAGMA synchronous=FULL')
    db.execute('CREATE TABLE owned(launch TEXT PRIMARY KEY, body BLOB NOT NULL)')
    gate, broker = Gate(Path(root) / 'gate'), None
    def resolve(leaf):
        if leaf != 'harmless':
            raise Failure('GateBlocked', 'Fixture catalog mismatch')
        return (sys.executable, '-c', "import time; print('owned-child',flush=True); time.sleep(10)")
    def validate(t, r):
        if t['operation_id'] != operation or t['intent_anchor'] != 'a' * 64 or t['epoch'] != 0:
            raise Failure('StaleBinding', 'Fixture intent identity differs')
    def commit(t, r, remaining):
        try:
            with gate.acquire(0.03):
                raise AssertionError('Gate released before durable owned commit')
        except Failure:
            pass
        db.execute('BEGIN IMMEDIATE')
        db.execute('INSERT INTO owned VALUES(?,?)', (r['launch_id'], canonical(r)))
        db.commit()
        return dict(state='COMMITTED', launch_id=r['launch_id'], session_id=r['session_id'],
                    intent_anchor=t['intent_anchor'], owned_sha256=digest(canonical(r)))
    try:
        broker = LaunchBroker.open_public_fixture(gate, resolve, validate, commit)
        prepared = broker.prepare(operation, '3' * 64, 0, 'harmless')
        pipe.send(prepared)
        result = broker.launch(conn, timeout=2)
        pipe.send(('launched', result, broker.read(prepared['launch_id'], timeout=2)))
        if pipe.recv() != 'cancel':
            raise ValueError('Expected cancellation')
        pipe.send(broker.cancel(prepared['launch_id']))
        pipe.send('done')
    finally:
        if broker:
            broker.close()
        db.close(); conn.close(); pipe.close()


class CompositionTests(unittest.TestCase):
    def test_two_fresh_plans_reviewed_then_two_one_use_permits_and_owned_children(self):
        ctx = multiprocessing.get_context('spawn')
        with tempfile.TemporaryDirectory(prefix='capstone-journal-fixture-', dir='/private/tmp') as td:
            directory = Path(td)
            ledger = fixture_connection(directory, True)
            journal = open_public_fixture(ledger, directory)
            source = []
            base_anchor = dict(ledger_sequence=0, ledger_tip=ledger.tip(), accounting_snapshot='a' * 64,
                               grant_registry_snapshot='b' * 64, installation='c' * 64)
            try:
                for i in range(2):
                    plan, request, review = fixture_review()
                    plan['grant']['grant_id'] = plan['observation']['grant_id'] = digest(str(i).encode())
                    plan['request']['run'] = 'source-jit-leaf-%d' % i
                    invocation = canonical({k: plan['request'][k] for k in ('run', 'scope', 'maximum')})
                    plan['request']['bindings']['invocation_bytes_sha256'] = digest(invocation)
                    plan['grant']['bindings'] = copy.deepcopy(plan['request']['bindings'])
                    plan['observation']['bindings'] = copy.deepcopy(plan['request']['bindings'])
                    grant_raw = canonical(plan['grant'])
                    plan['grant_bytes_sha256'] = plan['observation']['grant_bytes_sha256'] = digest(grant_raw)
                    plan['observation']['anchor'] = copy.deepcopy(base_anchor)
                    plan['observation']['receipt_sha256'] = content_digest(plan['observation'], 'receipt_sha256')
                    plan['plan_sha256'] = content_digest(plan, 'plan_sha256')
                    start = dict(action='start', version=1, plan=plan,
                                 operation_id=operation_id(plan['grant']['grant_id'], plan['plan_sha256']))
                    install_public_grant(ledger.db, start, grant_raw)
                    source.append((plan, request, review, grant_raw))
                actual_plans, actual_reviews, sends = [], [], 0
                for i, (static_plan, request, review, grant_raw) in enumerate(source):
                    anchor = dict(base_anchor, ledger_tip=ledger.tip(),
                                  ledger_sequence=ledger.db.execute('SELECT count(*) FROM events').fetchone()[0])
                    if i:
                        with self.assertRaises(Failure) as stale:
                            bind_observation(static_plan, nonce=static_plan['observation']['nonce'],
                                service_epoch=static_plan['observation']['service_epoch'], anchor=anchor,
                                now_ns=time.time_ns(), operator_uid=os.getuid())
                        self.assertEqual(stale.exception.record['code'], 'StaleBinding')
                    plan = copy.deepcopy(static_plan)
                    receipt = plan['observation']
                    receipt.update(anchor=anchor, observed_ns=time.time_ns(), nonce=digest(os.urandom(32)))
                    receipt['receipt_sha256'] = content_digest(receipt, 'receipt_sha256')
                    plan['plan_sha256'] = content_digest(plan, 'plan_sha256')
                    self.assertEqual(plan['request'], static_plan['request'])
                    self.assertEqual(plan['grant'], static_plan['grant'])
                    self.assertEqual(plan['grant_bytes_sha256'], digest(grant_raw))
                    request.update(leaf_id=digest(('leaf-%d' % i).encode()), actual_plan_raw=raw64(canonical(plan)))
                    request['request_sha256'] = _hash('jit-review-request-v2',
                        {k: v for k, v in request.items() if k != 'request_sha256'})
                    oid = operation_id(plan['grant']['grant_id'], plan['plan_sha256'])
                    review.update(leaf_id=request['leaf_id'], operation_id=oid, anchor=anchor,
                        actual_plan_sha256=plan['plan_sha256'], actual_plan_bytes_sha256=digest(canonical(plan)),
                        observation_sha256=digest(canonical(receipt)), grant_bytes_sha256=digest(grant_raw),
                        reviewed_ns=time.time_ns(), expires_ns=min(plan['grant']['bounds']['expires_ns'],
                            receipt['observed_ns'] + plan['grant']['bounds']['receipt_max_age_ns']))
                    with tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-', dir='/private/tmp') as bt:
                        root = Path(bt)
                        (root / 'gate').touch(mode=0o600)
                        gate = Gate(root / 'gate')
                        store = ReviewStore.open_public_fixture(root, create=True)
                        store.close()
                        owner = object()
                        def current(campaign, leaf, supplied, raw, observation):
                            if supplied is not owner or observation['anchor']['ledger_tip'] != ledger.tip():
                                raise Failure('StaleBinding', 'Source owner/current tip differs')
                        context = ReviewContext(current)
                        context.register(request['campaign_operation_id'], request['leaf_id'],
                                         canonical(plan), canonical(receipt), owner)
                        server = ReviewServer.open_public_fixture(root, context, role='context')
                        parent, child = ctx.Pipe()
                        reviewer = ctx.Process(target=review_process, args=(str(root), request, review, child))
                        reviewer.start()
                        child.close()
                        try:
                            self.assertTrue(parent.poll(5))
                            self.assertEqual(parent.recv(), 'ready')
                            reviewed = ReviewClient.open_public_fixture(root).review_and_get(request, expected(review))
                            self.assertEqual(reviewed, canonical(review))
                            actual_reviews.append(digest(reviewed))
                        finally:
                            parent.send('stop')
                            reviewer.join(5)
                            if reviewer.is_alive():
                                reviewer.terminate(); reviewer.join(2)
                            parent.close()
                            server.close()
                            context.close()
                            self.assertEqual(reviewer.exitcode, 0)
                        # Exact unchanged freshness helper after independent RPC.
                        bind_observation(plan, nonce=receipt['nonce'], service_epoch=receipt['service_epoch'],
                                         anchor=anchor, now_ns=time.time_ns(), operator_uid=os.getuid())
                        start = dict(action='start', version=1, plan=plan, operation_id=oid)
                        journal.claim(start, os.getuid())
                        # This is a fixture reservation identity, NOT v5 allowance.
                        journal.record_reserved(oid, digest(('fixture-hold-%d' % i).encode()))
                        _, permit = journal.mark_dispatch_pending(oid)
                        self.assertIsNotNone(permit)
                        left, right = socket.socketpair()
                        parent, child = ctx.Pipe()
                        broker = ctx.Process(target=composition_broker_worker, args=(str(root), right, child, oid))
                        broker.start(); right.close(); child.close()
                        try:
                            self.assertTrue(parent.poll(5))
                            prepared = parent.recv()
                            # Must receive the actual Journal operation identity.
                            self.assertEqual(prepared['operation_id'], oid)
                            sent = ticket(**{k: prepared[k] for k in ('launch_id', 'session_id',
                                'operation_id', 'control_run', 'epoch')})
                            permit.consume()
                            send_ticket(left, sent, gate.acquire(1), expected_uid=os.getuid(), timeout=2)
                            sends += 1
                            self.assertTrue(parent.poll(5))
                            response = parent.recv()
                            self.assertEqual(response[0], 'launched', response)
                            with self.assertRaises(Failure):
                                permit.consume()
                            self.assertIsNone(journal.mark_dispatch_pending(oid)[1])
                            parent.send('cancel')
                            self.assertTrue(parent.poll(5))
                            self.assertTrue(parent.recv()['reaped'])
                            self.assertTrue(parent.poll(5))
                            self.assertEqual(parent.recv(), 'done')
                        finally:
                            left.close(); parent.close()
                            broker.join(5)
                            if broker.is_alive():
                                broker.terminate(); broker.join(2)
                            self.assertEqual(broker.exitcode, 0)
                    actual_plans.append(plan['plan_sha256'])
                self.assertEqual(sends, 2)
                self.assertEqual(len(set(actual_plans)), 2)
                self.assertEqual(len(set(actual_reviews)), 2)
                self.assertEqual(ledger.db.execute('SELECT count(*) FROM capstone_operations').fetchone(), (2,))
                self.assertEqual(ledger.db.execute('SELECT count(*) FROM capstone_grants WHERE consumed_by IS NOT NULL').fetchone(), (2,))
            finally:
                ledger.close()


if __name__ == '__main__':
    unittest.main()
