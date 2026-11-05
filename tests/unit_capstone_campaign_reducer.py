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


def started_state(plan, raw, leaves=1):
    state = empty_state()
    seed(state, plan, None)
    op = operation_id(plan['grant']['grant_id'], plan['plan_sha256'])
    state['campaign_run'][(CAMPAIGN,)] = dict(
        campaign_id=CAMPAIGN, campaign_operation_id=op, plan_hash=plan['plan_sha256'],
        plan_raw=raw, auth_hash=AUTH, owner_epoch='e' * 64, state='running',
        active_leaf=None, result_object=None, intent_anchor=RECEIPT, revision=0,
        last_event=RECEIPT)
    for index in range(leaves):
        state['leaf'][(CAMPAIGN, index)] = dict(
            campaign_id=CAMPAIGN, leaf_index=index, leaf_id=('1' + str(index)) * 32,
            grant_id=plan['grant']['grant_id'], request_run='run-%d' % index,
            request_hash=H)
    return state


def select_event(plan, raw, revision=0, **record_overrides):
    run = dict(
        campaign_id=CAMPAIGN,
        campaign_operation_id=operation_id(plan['grant']['grant_id'], plan['plan_sha256']),
        plan_hash=plan['plan_sha256'], plan_raw=base64.b64encode(raw).decode('ascii'),
        auth_hash=AUTH, owner_epoch='e' * 64, state='running', active_leaf=0,
        result_object=None, intent_anchor=RECEIPT, revision=revision + 1)
    record = dict(campaign_id=CAMPAIGN, previous_revision=revision, run=run,
                  binding=None, leaf_plan=None, evidence=[])
    record.update(record_overrides)
    return dict(
        format='capstone-campaign-event-v2', version=2, action='campaign-select',
        idempotency_key=_domain('campaign-event-v2',
                                {'campaign_id': CAMPAIGN, 'action': 'campaign-select',
                                 'revision': revision + 1}),
        record=record)


class CampaignSelectTests(unittest.TestCase):
    def setUp(self):
        self.plan, _, _ = bound_plan()
        self.raw = canonical(self.plan)
        self.state = started_state(self.plan, self.raw)
        self.grants = {self.plan['grant']['grant_id']: (self.plan['grant']['grant_id'],)}
        self.calls = []

    def joins(self, campaign_id, completed, state):
        self.calls.append((campaign_id, list(completed)))

    def test_select_accepts_first_unfinished_leaf(self):
        event = select_event(self.plan, self.raw)
        _campaign(self.state, event, {'digest': '9' * 64}, self.grants,
                  {}, self.joins)
        row = self.state['campaign_run'][(CAMPAIGN,)]
        self.assertEqual(row['active_leaf'], 0)
        self.assertEqual(row['revision'], 1)
        self.assertEqual(row['last_event'], '9' * 64)
        self.assertEqual(row['intent_anchor'], RECEIPT)
        self.assertEqual(self.calls, [(CAMPAIGN, [])])

    def test_select_requires_completion_joins(self):
        event = select_event(self.plan, self.raw)
        with self.assertRaises(Failure) as blocked:
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)
        self.assertEqual(blocked.exception.record['code'], 'Unavailable')
        self.assertEqual(self.state['campaign_run'][(CAMPAIGN,)]['active_leaf'], None)

    def test_select_rejects_stale_revision_and_active_leaf(self):
        event = select_event(self.plan, self.raw, revision=1)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, self.joins)
        self.state['campaign_run'][(CAMPAIGN,)]['active_leaf'] = 0
        event = select_event(self.plan, self.raw)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, self.joins)

    def test_select_rejects_plan_already_present_for_leaf(self):
        self.state['leaf_plan'][(CAMPAIGN, 0)] = dict(campaign_id=CAMPAIGN, leaf_index=0)
        event = select_event(self.plan, self.raw)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, self.joins)

    def test_select_rejects_evidence_before_first_completion(self):
        event = select_event(self.plan, self.raw, evidence=[H])
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, self.joins)

    def test_select_rejects_changed_immutable_field(self):
        event = select_event(self.plan, self.raw)
        event['record']['run']['plan_hash'] = '9' * 64
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, self.joins)

    def test_select_propagates_join_failure(self):
        def refusing(campaign_id, completed, state):
            raise Failure('GateBlocked', 'Predecessor settlement is not certified')
        event = select_event(self.plan, self.raw)
        with self.assertRaises(Failure) as blocked:
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, refusing)
        self.assertEqual(blocked.exception.record['code'], 'GateBlocked')

    def test_select_rejects_campaign_without_leaves(self):
        self.state['leaf'].clear()
        event = select_event(self.plan, self.raw)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, self.joins)


def selected_state(plan, raw):
    state = started_state(plan, raw)
    row = state['campaign_run'][(CAMPAIGN,)]
    row.update(active_leaf=0, revision=1, last_event=RECEIPT)
    return state


def bind_event(plan, raw, review_hash='7' * 64, revision=1, **record_overrides):
    op = operation_id(plan['grant']['grant_id'], plan['plan_sha256'])
    start = dict(action='start', version=1, plan=plan, operation_id=op)
    start_raw = canonical(start)
    binding = dict(operation_id=op, grant_id=plan['grant']['grant_id'],
                   plan_hash=plan['plan_sha256'], start_hash=digest(start_raw),
                   start_raw=base64.b64encode(start_raw).decode('ascii'))
    leaf_plan = dict(campaign_id=CAMPAIGN, leaf_index=0, operation_id=op,
                     plan_hash=plan['plan_sha256'],
                     plan_bytes_sha256=digest(raw),
                     plan_raw=base64.b64encode(raw).decode('ascii'),
                     review_hash=review_hash)
    run = dict(
        campaign_id=CAMPAIGN, campaign_operation_id=op, plan_hash=plan['plan_sha256'],
        plan_raw=base64.b64encode(raw).decode('ascii'), auth_hash=AUTH,
        owner_epoch='e' * 64, state='running', active_leaf=0, result_object=None,
        intent_anchor=RECEIPT, revision=revision + 1)
    record = dict(campaign_id=CAMPAIGN, previous_revision=revision, run=run,
                  binding=binding, leaf_plan=leaf_plan, evidence=[review_hash])
    record.update(record_overrides)
    return dict(
        format='capstone-campaign-event-v2', version=2, action='campaign-leaf-bind',
        idempotency_key=_domain('campaign-event-v2',
                                {'campaign_id': CAMPAIGN, 'action': 'campaign-leaf-bind',
                                 'revision': revision + 1}),
        record=record)


class CampaignLeafBindTests(unittest.TestCase):
    def setUp(self):
        self.plan, _, _ = bound_plan()
        self.raw = canonical(self.plan)
        self.state = selected_state(self.plan, self.raw)
        self.grants = {self.plan['grant']['grant_id']: (self.plan['grant']['grant_id'],)}
        self.calls = []

    def live(self, campaign_id, leaf_index, binding, plan_row, state):
        self.calls.append((campaign_id, leaf_index))

    def test_bind_inserts_binding_and_plan_atomically(self):
        event = bind_event(self.plan, self.raw)
        _campaign(self.state, event, {'digest': '9' * 64}, self.grants,
                  {}, None, self.live)
        op = event['record']['binding']['operation_id']
        self.assertIn((op,), self.state['binding'])
        self.assertEqual(self.state['binding'][(op,)]['bind_anchor'], '9' * 64)
        self.assertIn((CAMPAIGN, 0), self.state['leaf_plan'])
        self.assertEqual(self.state['campaign_run'][(CAMPAIGN,)]['revision'], 2)
        self.assertEqual(self.calls, [(CAMPAIGN, 0)])

    def test_bind_requires_live_verification(self):
        event = bind_event(self.plan, self.raw)
        with self.assertRaises(Failure) as blocked:
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants)
        self.assertEqual(blocked.exception.record['code'], 'Unavailable')
        self.assertFalse(self.state['binding'])

    def test_bind_rejects_leaf_mismatch(self):
        event = bind_event(self.plan, self.raw)
        event['record']['leaf_plan']['leaf_index'] = 1
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, None, self.live)

    def test_bind_rejects_plan_byte_digest_mismatch(self):
        event = bind_event(self.plan, self.raw)
        event['record']['leaf_plan']['plan_bytes_sha256'] = '9' * 64
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, None, self.live)

    def test_bind_rejects_start_plan_mismatch(self):
        event = bind_event(self.plan, self.raw)
        other = copy.deepcopy(self.plan)
        other['plan_sha256'] = '9' * 64
        start = dict(action='start', version=1, plan=other,
                     operation_id=self.plan['grant']['grant_id'])
        raw = canonical(start)
        event['record']['binding']['start_raw'] = base64.b64encode(raw).decode('ascii')
        event['record']['binding']['start_hash'] = digest(raw)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, None, self.live)

    def test_bind_rejects_wrong_evidence(self):
        event = bind_event(self.plan, self.raw, review_hash='7' * 64)
        event['record']['evidence'] = ['8' * 64]
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, None, self.live)

    def test_bind_rejects_duplicate_binding_or_plan(self):
        event = bind_event(self.plan, self.raw)
        self.state['binding'][(event['record']['binding']['operation_id'],)] = dict(
            operation_id=event['record']['binding']['operation_id'])
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, None, self.live)

    def test_bind_rejects_stale_revision(self):
        event = bind_event(self.plan, self.raw, revision=0)
        with self.assertRaises(Failure):
            _campaign(self.state, event, {'digest': RECEIPT}, self.grants, {}, None, self.live)


if __name__ == '__main__':
    unittest.main()
