"""Stage M replay-authority state audit tests."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

import persistent_budget  # noqa: E402
import replay  # noqa: E402
from common import Failure  # noqa: E402
from replay_authority_audit import (  # noqa: E402
    REPLAY_PROFILE,
    STAGE_A_BASELINE_SHA256,
    build_authority_audit,
    preflight_classification,
    store_classification,
    validate_authority_audit,
)
from spendability_stage_c import StageCError  # noqa: E402


AUDIT = ROOT / 'docs/evidence/replay-authority/stage-m/AUDIT.json'
STAGE_A = ROOT / 'docs/evidence/spendability/stage-a/BASELINE.json'


class ReplayAuthorityAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = build_authority_audit(ROOT)

    def call_preflight(self, binding):
        with patch.object(replay, 'root_record', lambda path: binding):
            replay.preflight()

    def test_audit_uses_live_source_profile_contracts(self):
        contracts = self.record['source_contracts']
        self.assertEqual(contracts['legacy_profiles'], list(persistent_budget.PROFILES))
        self.assertEqual(contracts['registered_profiles'],
                         list(persistent_budget.REGISTERED_PROFILES))
        self.assertEqual(contracts['preflight_required_version'], 1)
        self.assertEqual(contracts['preflight_rejected_versions'], [2, 3])
        self.assertEqual(contracts['store_writable_version'], 1)
        self.assertEqual(contracts['store_writable_profile_contract'],
                         list(persistent_budget.PROFILES))
        self.assertEqual(contracts['store_read_only_versions'], [2, 3])

    def test_actual_preflight_accepts_only_hypothetical_v1_four_profiles(self):
        variants = {item['name']: item['binding'] for item in self.record['variants']}
        with self.assertRaises(Failure) as raised:
            self.call_preflight(variants['legal-legacy-v1-three-profiles'])
        self.assertEqual(raised.exception.record['code'], 'GateBlocked')
        self.call_preflight(variants['preflight-valid-hypothetical-v1-four-profiles'])
        for name in ('registered-frozen-v2-four-profiles',
                     'recovered-readonly-v3-four-profiles'):
            with self.subTest(name=name), self.assertRaises(Failure) as raised:
                self.call_preflight(variants[name])
            self.assertEqual(raised.exception.record['code'], 'GateBlocked')

    def test_audited_active_binding_is_committed_v3(self):
        raw = STAGE_A.read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), STAGE_A_BASELINE_SHA256)
        active = json.loads(raw)['active']
        self.assertEqual(active['version'], 3)
        self.assertIn(REPLAY_PROFILE, active['profiles'])
        self.assertEqual(self.record['basis']['stage_a_baseline_sha256'],
                         STAGE_A_BASELINE_SHA256)

    def test_no_variant_can_both_pass_preflight_and_open_writable_replay(self):
        for item in self.record['variants']:
            self.assertFalse(item['independent_replay_possible'])
        self.assertEqual(self.record['summary'], {
            'variants_audited': 5,
            'preflight_pass_variants': 1,
            'store_schema_pass_variants': 4,
            'writable_store_variants': 1,
            'replay_capable_variants': 0,
        })

    def test_the_two_partial_successes_fail_for_opposite_reasons(self):
        by_name = {item['name']: item for item in self.record['variants']}
        preflight_only = by_name['preflight-valid-hypothetical-v1-four-profiles']
        store_only = by_name['legal-legacy-v1-three-profiles']
        self.assertEqual(preflight_only['preflight']['result'], 'pass')
        self.assertEqual(preflight_only['persistent_store_schema']['result'], 'fail')
        self.assertEqual(store_only['preflight']['result'], 'fail')
        self.assertEqual(store_only['persistent_store_schema']['result'], 'pass')
        self.assertFalse(store_only['persistent_store_schema']['read_only'])

    def test_v2_and_v3_are_schema_valid_but_frozen(self):
        for name in ('audited-active-v3', 'registered-frozen-v2-four-profiles',
                     'recovered-readonly-v3-four-profiles'):
            item = next(item for item in self.record['variants'] if item['name'] == name)
            self.assertEqual(item['persistent_store_schema']['result'], 'pass')
            self.assertTrue(item['persistent_store_schema']['read_only'])
            self.assertEqual(item['persistent_store_schema']['mutations'], 'denied')
            self.assertEqual(item['preflight']['result'], 'fail')

    def test_finding_demands_new_contract_not_gate_relaxation(self):
        self.assertEqual(self.record['finding']['classification'],
                         'inconsistent-authority-state-machine')
        self.assertIn('Design and independently review a new binding authority contract',
                      self.record['finding']['required_next_step'])
        self.assertIn('do not relax preflight', self.record['finding']['required_next_step'])

    def test_record_remains_fail_closed_and_powerless(self):
        outcome = self.record['outcome']
        self.assertFalse(outcome['replay_possible'])
        self.assertIsNone(outcome['spendable'])
        self.assertFalse(outcome['execution_authorized'])
        self.assertEqual(outcome['allowed_mutations'], [])
        self.assertFalse(outcome['protected_access'])
        self.assertFalse(any(self.record['authority'].values()))

    def test_saved_audit_matches_exact_regeneration_and_hash(self):
        saved = AUDIT.read_bytes()
        self.assertEqual(json.loads(saved), self.record)
        self.assertEqual(sha256(saved).hexdigest(),
                         '39869d025fae2ad97c4368e5ceaeff073afe5f8ef32cbdb941f9d06f727a87aa')

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_authority_audit(self.record, ROOT)
        self.assertTrue(result['record_valid'])
        self.assertFalse(result['replay_possible'])
        self.assertIsNone(result['spendable'])
        self.assertFalse(result['execution_authorized'])

    def test_tampered_v1_profile_does_not_become_replay_capable(self):
        legacy = list(persistent_budget.PROFILES)
        registered = list(persistent_budget.REGISTERED_PROFILES)
        binding = {'version': 1, 'profiles': registered}
        self.assertEqual(preflight_classification(binding, registered)['result'], 'pass')
        store = store_classification(binding, legacy, registered)
        self.assertEqual(store['result'], 'fail')
        self.assertEqual(store['reason'],
                         'binding profiles differ from version contract')

    def test_classification_and_authority_injection_are_rejected(self):
        value = deepcopy(self.record)
        value['outcome']['replay_possible'] = True
        with self.assertRaises(StageCError) as raised:
            validate_authority_audit(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'replay_authority_audit: record differs from exact regeneration')
        value = deepcopy(self.record)
        value['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_authority_audit(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'replay_authority_audit: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
