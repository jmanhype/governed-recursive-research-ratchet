"""Real-Ledger campaign append: start reaches replay; nothing unverified passes."""
import base64
import copy
import os
from pathlib import Path
import tempfile
import unittest

from common import GATES, Failure, canonical, digest
from capstone_backend_index import (_domain, apply_backend_stop, derive_manifest,
                                    open_public_fixture)
from capstone_contract import content_digest, operation_id, validate_record
from unit_capstone_backend_index import issuance_fixture
from unit_capstone_journal import fixture_connection

H = 'a' * 64


def raw(data):
    return base64.b64encode(data).decode('ascii')


def gate_set():
    return {name: dict(state='not-run', evidence=None, reason=None) for name in GATES}


class CampaignAppendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='capstone-journal-fixture-',
                                                dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = fixture_connection(self.root, create=True)
        self.addCleanup(self.ledger.close)
        self.index = open_public_fixture(self.ledger, self.root, create=True)
        self.row, self.spec, self.auth, self.grant = issuance_fixture()

    def issue(self):
        key = _domain('issue-intent-v1', {'authorization': self.row['auth_hash']})
        receipt = self.index.append_transition(
            'issuance-intent', [dict(table='backend_v2_issuance', rows=[self.row])], key)
        entries, leaves = [], []
        for leaf in self.spec['leaves']:
            grant = copy.deepcopy(self.grant)
            gid = _domain('issued-leaf-grant-v1', dict(
                issuance_id=H, authorization=self.row['auth_hash'],
                spec=self.row['spec_hash'], leaf_id=leaf['leaf_id']))
            grant.update(grant_id=gid, operator_uid=os.getuid(),
                         authorization_bytes_sha256=self.row['auth_hash'],
                         issuance_anchor=receipt['digest'], review_anchor=H,
                         bindings=leaf['request']['bindings'])
            grant['bounds'].update(scope=leaf['request']['scope'],
                                   maximum=leaf['maximum'],
                                   not_before_ns=0, expires_ns=1000)
            entries.append(dict(leaf_id=leaf['leaf_id'], grant_raw=raw(canonical(grant))))
            leaves.append(dict(campaign_id=self.row['campaign_id'],
                               leaf_index=leaf['index'], leaf_id=leaf['leaf_id'],
                               grant_id=gid, request_run=leaf['request']['run'],
                               request_hash=digest(canonical(leaf['request']))))
        bundle = dict(schema='capstone-grant-bundle-v1',
                      campaign_spec_sha256=self.row['spec_hash'], grants=entries)
        row = dict(self.row, phase='issued', intent_anchor=receipt['digest'],
                   bundle_raw=raw(canonical(bundle)))
        del row['issued_anchor']
        campaign = dict(campaign_id=self.row['campaign_id'], issuance_id=H,
                        control_run=_domain('campaign-control-v1',
                                            dict(issuance_id=H,
                                                 campaign_id=self.row['campaign_id'])),
                        stopped=0, stop_epoch=0, stop_operation=None, stop_anchor=None)
        commit_key = _domain('issue-commit-v1', {'authorization': self.row['auth_hash']})
        self.index.append_transition('issuance-commit', [
            dict(table='backend_v2_issuance', rows=[row]),
            dict(table='backend_v2_campaign', rows=[campaign]),
            dict(table='backend_v2_leaf', rows=leaves)], commit_key)
        return entries, leaves

    def plan_for(self, leaf, entry):
        grant = copy.deepcopy(self.grant)
        grant.update(grant_id=leaf['grant_id'], operator_uid=os.getuid(),
                     authorization_bytes_sha256=self.row['auth_hash'],
                     issuance_anchor=H, review_anchor=H,
                     bindings=self.spec['leaves'][leaf['leaf_index']]['request']['bindings'])
        grant['bounds'].update(scope=self.spec['leaves'][leaf['leaf_index']]['request']['scope'],
                               maximum=self.spec['leaves'][leaf['leaf_index']]['maximum'],
                               not_before_ns=0, expires_ns=1000)
        request = self.spec['leaves'][leaf['leaf_index']]['request']
        observation = dict(
            schema='capstone-observation-v1', nonce=H, operator_uid=os.getuid(),
            grant_id=leaf['grant_id'], grant_bytes_sha256=digest(canonical(grant)),
            authorization_bytes_sha256=self.row['auth_hash'],
            bindings=request['bindings'], observed_ns=1, service_epoch=H,
            anchor=dict(ledger_sequence=0, ledger_tip='0' * 64,
                        accounting_snapshot=H, grant_registry_snapshot=H,
                        installation=H),
            accounting=dict(version=1, stopped=False, history='unknown',
                            spendable=None, held=None),
            capability='observe-only', grant_state='available', blockers=[],
            receipt_sha256=H)
        observation['receipt_sha256'] = content_digest(observation, 'receipt_sha256')
        plan = dict(schema='capstone-plan-v1', request=request, grant=grant,
                    grant_bytes_sha256=digest(canonical(grant)),
                    authorization_bytes_sha256=self.row['auth_hash'],
                    observation=observation, gates=gate_set(), plan_sha256=H)
        plan['plan_sha256'] = content_digest(plan, 'plan_sha256')
        validate_record(plan, 'Plan')
        return plan

    def start_record(self, plan):
        op = operation_id(plan['grant']['grant_id'], plan['plan_sha256'])
        run = dict(campaign_id=self.row['campaign_id'], campaign_operation_id=op,
                   plan_hash=plan['plan_sha256'], plan_raw=raw(canonical(plan)),
                   auth_hash=self.row['auth_hash'], owner_epoch='e' * 64,
                   state='running', active_leaf=None, result_object=None, revision=0)
        return dict(campaign_id=self.row['campaign_id'], previous_revision=None,
                    run=run, binding=None, leaf_plan=None,
                    evidence=[H, 'b' * 64]), op

    def test_start_appends_through_real_ledger_and_replays(self):
        entries, leaves = self.issue()
        plan = self.plan_for(leaves[0], entries[0])
        record, op = self.start_record(plan)
        key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                            'action': 'campaign-start', 'revision': 0})
        receipt = self.index.append_campaign('campaign-start', record, key)
        self.assertEqual(receipt['sequence'], 3)
        state = self.index.validate()
        row = state['campaign_run'][(self.row['campaign_id'],)]
        self.assertEqual(row['state'], 'running')
        self.assertEqual(row['revision'], 0)
        self.assertEqual(row['campaign_operation_id'], op)
        self.assertEqual(row['last_event'], receipt['digest'])
        self.assertEqual(self.index.validate(), state)

    def test_unverified_action_refuses_without_writing(self):
        entries, leaves = self.issue()
        plan = self.plan_for(leaves[0], entries[0])
        record, _ = self.start_record(plan)
        start_key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                                  'action': 'campaign-start', 'revision': 0})
        self.index.append_campaign('campaign-start', record, start_key)
        tip = self.ledger.tip()
        select = dict(record, previous_revision=0)
        select['run'] = dict(record['run'], active_leaf=0, revision=1)
        event = dict(format='capstone-campaign-event-v2', version=2,
                     action='campaign-select', record=select,
                     idempotency_key=_domain('campaign-event-v2', {
                         'campaign_id': self.row['campaign_id'],
                         'action': 'campaign-select', 'revision': 1}))
        with self.assertRaises(Failure) as blocked:
            self.index.append_campaign('campaign-select', select,
                                       event['idempotency_key'])
        self.assertEqual(blocked.exception.record['code'], 'Unavailable')
        self.assertEqual(self.ledger.tip(), tip)

    def test_changed_cached_campaign_event_fails(self):
        entries, leaves = self.issue()
        plan = self.plan_for(leaves[0], entries[0])
        record, _ = self.start_record(plan)
        key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                            'action': 'campaign-start', 'revision': 0})
        self.index.append_campaign('campaign-start', record, key)
        changed = copy.deepcopy(record)
        changed['run']['owner_epoch'] = 'f' * 64
        with self.assertRaises(Failure):
            self.index.append_campaign('campaign-start', changed, key)


class CampaignSequenceTests(unittest.TestCase):
    setUp = CampaignAppendTests.setUp

    def issue(self):
        return CampaignAppendTests.issue(self)

    def plan_for(self, leaf, entry):
        return CampaignAppendTests.plan_for(self, leaf, entry)

    def start_record(self, plan):
        return CampaignAppendTests.start_record(self, plan)

    def run_row(self, **changes):
        state = self.index.validate()
        row = dict(state['campaign_run'][(self.row['campaign_id'],)])
        row.pop('last_event')
        row['plan_raw'] = raw(row['plan_raw'])
        row.update(changes)
        return row

    def append(self, action, record, revision, **verifiers):
        key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                            'action': action, 'revision': revision})
        return self.index.append_campaign(action, record, key, **verifiers)

    def inspect(self):
        return self.index.validate()['campaign_run'][(self.row['campaign_id'],)]

    def _run_two_leaf(self):
        entries, leaves = self.issue()
        plans = [self.plan_for(leaves[0], entries[0]), self.plan_for(leaves[1], entries[1])]
        start, _ = self.start_record(plans[0])
        self.append('campaign-start', start, 0)
        self.assertEqual(self.inspect()['state'], 'running')
        self.assertIsNone(self.inspect()['active_leaf'])

        calls = []

        def joins(campaign_id, completed, state):
            calls.append(('joins', list(completed)))

        def live(campaign_id, leaf_index, binding, plan_row, state):
            calls.append(('live', leaf_index))

        def proof(campaign_id, leaf_index, result, state):
            calls.append(('proof', leaf_index, result))

        for index, plan in enumerate(plans):
            revision = self.inspect()['revision']
            run = self.run_row(active_leaf=index, revision=revision + 1)
            evidence = [] if index == 0 else ['4' * 64]
            select = dict(campaign_id=self.row['campaign_id'], previous_revision=revision,
                          run=run, binding=None, leaf_plan=None, evidence=evidence)
            self.append('campaign-select', select, revision + 1, joins=joins)
            self.assertEqual(self.inspect()['active_leaf'], index)
            self.assertEqual(self.inspect()['revision'], revision + 1)

            grant = plan['grant']
            op = operation_id(grant['grant_id'], plan['plan_sha256'])
            start_rec = dict(action='start', version=1, plan=plan, operation_id=op)
            start_raw = canonical(start_rec)
            review_hash = '7' * 64
            binding = dict(operation_id=op, grant_id=grant['grant_id'],
                           plan_hash=plan['plan_sha256'],
                           start_hash=digest(start_raw),
                           start_raw=raw(start_raw))
            leaf_plan = dict(campaign_id=self.row['campaign_id'], leaf_index=index,
                             operation_id=op, plan_hash=plan['plan_sha256'],
                             plan_bytes_sha256=digest(canonical(plan)),
                             plan_raw=raw(canonical(plan)), review_hash=review_hash)
            revision = self.inspect()['revision']
            run = self.run_row(revision=revision + 1)
            bind = dict(campaign_id=self.row['campaign_id'], previous_revision=revision,
                        run=run, binding=binding, leaf_plan=leaf_plan,
                        evidence=[review_hash])
            self.append('campaign-leaf-bind', bind, revision + 1, live=live)
            self.assertEqual(self.inspect()['revision'], revision + 1)

            revision = self.inspect()['revision']
            run = self.run_row(active_leaf=None, revision=revision + 1)
            result = ('%d' % index) * 64
            advance = dict(campaign_id=self.row['campaign_id'],
                           previous_revision=revision, run=run, binding=None,
                           leaf_plan=None, evidence=[result])
            self.append('campaign-advance', advance, revision + 1, advance_proof=proof)
            self.assertIsNone(self.inspect()['active_leaf'])

        revision = self.inspect()['revision']

        def finish_provider(campaign_id, state, progress):
            return derive_manifest(state, campaign_id, progress, gate_set(), now_ns=1)

        # The run row must already carry the terminal hash, so derive it first.
        current = self.index.validate()
        manifest, terminal = derive_manifest(current, self.row['campaign_id'],
                                             {self.row['campaign_id']: {0, 1}},
                                             gate_set(), now_ns=1)
        run = self.run_row(state='completed', result_object=terminal, revision=revision + 1)
        finish = dict(campaign_id=self.row['campaign_id'], previous_revision=revision,
                      run=run, binding=None, leaf_plan=None, evidence=[terminal])
        self.append('campaign-finish', finish, revision + 1,
                    manifest_provider=finish_provider)
        final = self.inspect()
        self.assertEqual(final['state'], 'completed')
        self.assertEqual(final['result_object'], terminal)
        self.assertEqual(final['revision'], revision + 1)
        self.assertEqual(final['active_leaf'], None)
        self.assertEqual(self.index.validate(), self.index.validate())
        self.assertIn(('joins', []), calls)
        self.assertIn(('live', 1), calls)
        self.assertIn(('proof', 1, '1' * 64), calls)
        return terminal

    def test_two_leaf_campaign_runs_end_to_end(self):
        self._run_two_leaf()

    def test_finish_replay_rejects_missing_manifest_object(self):
        terminal = self._run_two_leaf()
        (self.root / 'objects' / terminal).unlink()
        with self.assertRaises(Failure):
            self.index.validate()

    def test_fence_after_start_moves_run_to_recovery(self):
        entries, leaves = self.issue()
        plan = self.plan_for(leaves[0], entries[0])
        record, _ = self.start_record(plan)
        start_key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                                  'action': 'campaign-start', 'revision': 0})
        self.index.append_campaign('campaign-start', record, start_key)
        state = self.index.validate()
        manifest, terminal = derive_manifest(state, self.row['campaign_id'], {},
                                             gate_set(), now_ns=1)
        failure = dict(schema='capstone-failure-v1')
        snapshot = dict(
            schema='capstone-campaign-fence-v2',
            campaign_operation_id=state['campaign_run'][(self.row['campaign_id'],)][
                'campaign_operation_id'],
            owner_epoch='e' * 64, observed_owner='absent', active_leaf=None,
            cut='owner-lost')
        evidence = sorted({digest(canonical(failure)), digest(canonical(snapshot)),
                           terminal})
        revision = state['campaign_run'][(self.row['campaign_id'],)]['revision']
        run = self.run_row(state='recovery-required', result_object=terminal,
                           revision=revision + 1)
        fence = dict(campaign_id=self.row['campaign_id'], previous_revision=revision,
                     run=run, binding=None, leaf_plan=None, evidence=evidence)

        def provider(campaign_id, state, evidence):
            return manifest, terminal, failure, snapshot

        self.append('campaign-fence', fence, revision + 1, fence_provider=provider)
        final = self.inspect()
        self.assertEqual(final['state'], 'recovery-required')
        self.assertEqual(final['result_object'], terminal)
        self.assertIsNone(final['active_leaf'])


class CampaignStopOutcomeLedgerTests(unittest.TestCase):
    setUp = CampaignAppendTests.setUp

    def issue(self):
        return CampaignAppendTests.issue(self)

    def plan_for(self, leaf, entry):
        return CampaignAppendTests.plan_for(self, leaf, entry)

    def start_record(self, plan):
        return CampaignAppendTests.start_record(self, plan)

    def stop_running_campaign(self):
        entries, leaves = self.issue()
        plan = self.plan_for(leaves[0], entries[0])
        record, _ = self.start_record(plan)
        start_key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                                  'action': 'campaign-start', 'revision': 0})
        self.index.append_campaign('campaign-start', record, start_key)
        state = self.index.validate()
        campaign = state['campaign'][(self.row['campaign_id'],)]
        run = state['campaign_run'][(self.row['campaign_id'],)]
        after = dict(run)
        after.pop('last_event')
        after['plan_raw'] = raw(after['plan_raw'])
        after.update(state='stop-pending', revision=run['revision'] + 1)
        stop = dict(schema='capstone-campaign-stop-v2',
                    campaign_id=campaign['campaign_id'],
                    control_run=campaign['control_run'], epoch=1,
                    primary_operation=H, affected_operations=[],
                    run_before_revision=run['revision'], run_after=after)
        event = dict(kind='safe-stop', run=campaign['control_run'], epoch=1,
                     operation=H, backend_stop=stop)
        self.ledger.append_atomic(320, event, self.ledger.tip(), 'campaign-stop',
                                  lambda db, receipt: apply_backend_stop(db, receipt, stop))
        return self.index.validate()

    def test_stop_outcome_verified_becomes_stopped(self):
        state = self.stop_running_campaign()
        run = state['campaign_run'][(self.row['campaign_id'],)]
        self.assertEqual(run['state'], 'stop-pending')
        manifest, terminal = derive_manifest(state, self.row['campaign_id'], {},
                                             gate_set(), now_ns=1)
        outcome = dict(schema='capstone-campaign-stop-v2')
        evidence = sorted({digest(canonical(outcome)), terminal})
        after = dict(run)
        after.pop('last_event')
        after['plan_raw'] = raw(after['plan_raw'])
        after.update(state='stopped', active_leaf=None, result_object=terminal,
                     revision=run['revision'] + 1)
        record = dict(campaign_id=self.row['campaign_id'],
                      previous_revision=run['revision'], run=after,
                      binding=None, leaf_plan=None, evidence=evidence)

        def provider(campaign_id, state, evidence):
            return manifest, terminal, outcome, True

        key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                             'action': 'campaign-stop-outcome',
                                             'revision': run['revision'] + 1})
        self.index.append_campaign('campaign-stop-outcome', record, key,
                                   stop_provider=provider)
        final = self.index.validate()['campaign_run'][(self.row['campaign_id'],)]
        self.assertEqual(final['state'], 'stopped')
        self.assertIsNone(final['active_leaf'])
        self.assertEqual(final['result_object'], terminal)

    def test_stop_outcome_unverified_requires_recovery(self):
        state = self.stop_running_campaign()
        run = state['campaign_run'][(self.row['campaign_id'],)]
        manifest, terminal = derive_manifest(state, self.row['campaign_id'], {},
                                             gate_set(), now_ns=1)
        outcome = dict(schema='capstone-campaign-stop-v2')
        evidence = sorted({digest(canonical(outcome)), terminal})
        after = dict(run)
        after.pop('last_event')
        after['plan_raw'] = raw(after['plan_raw'])
        after.update(state='recovery-required', result_object=terminal,
                     revision=run['revision'] + 1)
        record = dict(campaign_id=self.row['campaign_id'],
                      previous_revision=run['revision'], run=after,
                      binding=None, leaf_plan=None, evidence=evidence)

        def provider(campaign_id, state, evidence):
            return manifest, terminal, outcome, False

        key = _domain('campaign-event-v2', {'campaign_id': self.row['campaign_id'],
                                             'action': 'campaign-stop-outcome',
                                             'revision': run['revision'] + 1})
        self.index.append_campaign('campaign-stop-outcome', record, key,
                                   stop_provider=provider)
        final = self.index.validate()['campaign_run'][(self.row['campaign_id'],)]
        self.assertEqual(final['state'], 'recovery-required')
        self.assertEqual(final['result_object'], terminal)


if __name__ == '__main__':
    unittest.main()
