"""Campaign-v2 reducer: start is exact; every other action still refuses.

No stub accepts. An unimplemented action raises Unavailable, so a campaign
event can never be silently folded as if it had been checked.
"""
import base64
import copy
import unittest

from common import Failure, canonical, digest
from capstone_backend_index import _campaign, _domain, CAMPAIGN_ACTIONS
from capstone_backend_schema import TABLE_COLUMNS
from capstone_contract import operation_id
from unit_capstone_contract import bound_plan

H = 'a' * 64
CAMPAIGN = 'b' * 64
AUTH = 'c' * 64
RECEIPT = 'f' * 64


def empty_state():
    return {table: {} for table in TABLE_COLUMNS}


def seed(state, plan, raw):
    state['issuance'][(AUTH,)] = dict(
        auth_hash=AUTH, campaign_id=CAMPAIGN, issuance_id='d' * 64, spec_hash=H,
        registry_hash=H, auth_raw=b'auth', spec_raw=b'spec', intent_anchor=H,
        phase='issued', bundle_raw=b'bundle', issued_anchor=H)
    state['campaign'][(CAMPAIGN,)] = dict(
        campaign_id=CAMPAIGN, issuance_id='d' * 64, control_run='e' * 64,
        stop_epoch=0, stopped=0, stop_operation=None, stop_anchor=None)
    return canonical(plan)


def start_event(plan, raw, revision=0, **record_overrides):
    run = dict(
        campaign_id=CAMPAIGN,
        campaign_operation_id=operation_id(plan['grant']['grant_id'], plan['plan_sha256']),
        plan_hash=plan['plan_sha256'],
        plan_raw=base64.b64encode(raw).decode('ascii'),
        auth_hash=AUTH,
        owner_epoch='e' * 64,
        state='running',
        active_leaf=None,
        result_object=None,
        revision=0,
    )
    record = dict(campaign_id=CAMPAIGN, previous_revision=None, run=run,
                  binding=None, leaf_plan=None, evidence=[H, 'b' * 64])
    record.update(record_overrides)
    return dict(
        format='capstone-campaign-event-v2', version=2, action='campaign-start',
        idempotency_key=_domain('campaign-event-v2',
                                {'campaign_id': CAMPAIGN, 'action': 'campaign-start',
                                 'revision': revision}),
        record=record)


class CampaignReducerTests(unittest.TestCase):
    def setUp(self):
        self.plan, _, _ = bound_plan()
        self.state = empty_state()
        self.raw = seed(self.state, self.plan, None)
        self.grants = {self.plan['grant']['grant_id']: (self.plan['grant']['grant_id'],)}

    def test_start_accepts_exact_run_and_fills_receipt_fields(self):
        event = start_event(self.plan, self.raw)
        _campaign(self.state, event, {'digest': RECEIPT}, self.grants)
        row = self.state['campaign_run'][(CAMPAIGN,)]
        self.assertEqual(row['state'], 'running')
        self.assertEqual(row['revision'], 0)
        self.assertEqual(row['last_event'], RECEIPT)
        self.assertEqual(row['intent_anchor'], RECEIPT)
        self.assertEqual(row['plan_raw'], self.raw)

    def test_start_requires_unstopped_issued_campaign(self):
        event = start_event(self.plan, self.raw)
        self.state['campaign'][(CAMPAIGN,)]['stopped'] = 1
        with self.assertRaises(Failure) as blocked:
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)
        self.assertEqual(blocked.exception.record['code'], 'IntegrityFailure')

    def test_start_rejects_prior_active_run(self):
        event = start_event(self.plan, self.raw)
        self.state['campaign_run'][(CAMPAIGN,)] = dict(state='running')
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_start_rejects_non_null_previous_revision(self):
        event = start_event(self.plan, self.raw)
        event['record']['previous_revision'] = 0
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_start_rejects_binding_or_leaf_plan(self):
        for name in ('binding', 'leaf_plan'):
            event = start_event(self.plan, self.raw)
            event['record'][name] = {}
            with self.assertRaises(Failure):
                _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_start_rejects_unsorted_duplicate_or_short_evidence(self):
        for evidence in (['b' * 64, H], [H, H], [H], []):
            event = start_event(self.plan, self.raw, evidence=evidence)
            with self.assertRaises(Failure):
                _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_start_rejects_operation_id_mismatch(self):
        event = start_event(self.plan, self.raw)
        event['record']['run']['campaign_operation_id'] = '9' * 64
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_start_rejects_plan_hash_mismatch(self):
        event = start_event(self.plan, self.raw)
        event['record']['run']['plan_hash'] = '9' * 64
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_start_rejects_unknown_grant(self):
        event = start_event(self.plan, self.raw)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, {})

    def test_start_rejects_wrong_idempotency_key(self):
        event = start_event(self.plan, self.raw, revision=1)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)

    def test_unimplemented_actions_refuse_instead_of_accepting(self):
        for action in CAMPAIGN_ACTIONS:
            if action == 'campaign-start':
                continue
            event = start_event(self.plan, self.raw)
            event['action'] = action
            with self.assertRaises(Failure) as blocked:
                _campaign(self.state, event, {'digest': RECEIPT}, self.grants)
            self.assertEqual(blocked.exception.record['code'], 'Unavailable')
        self.assertNotIn((CAMPAIGN,), self.state['campaign_run'])

    def test_unknown_action_and_malformed_envelope_refuse(self):
        event = start_event(self.plan, self.raw)
        event['action'] = 'campaign-design'
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)
        event = start_event(self.plan, self.raw)
        event['record']['extra'] = 1
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)


if __name__ == '__main__':
    unittest.main()
