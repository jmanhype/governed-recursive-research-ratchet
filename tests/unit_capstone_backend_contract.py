"""Pure ReviewV2 data tests, not reviewer identity/approval or live proof."""
import copy
import hashlib
import json
import unittest

from common import Failure, canonical
from capstone_backend_contract import (MAX_RAW, SCHEMAS, campaign_operation_id,
    campaign_plan_digest, decode_raw, decode_record, domain_hash, encode_raw, validate_record)

H = 'a' * 64


def review():
    value = {k: H for k, spec in SCHEMAS['ReviewV2'].items() if spec == 'H'}
    value.update(schema='capstone-jit-review-v2', phase='actual-plan-prelaunch', verdict='pass',
        anchor=dict(ledger_sequence=0, ledger_tip='0'*64, accounting_snapshot=H,
                    grant_registry_snapshot=H, installation=H),
        reviewed_ns=1, expires_ns=2, evidence=[H], blockers=[])
    return value


class ContractTests(unittest.TestCase):
    def test_valid_review_and_canonical_roundtrip(self):
        value = review()
        self.assertIs(validate_record(value, 'ReviewV2'), value)
        self.assertEqual(decode_record(canonical(value), 'ReviewV2'), value)

    def test_expired_history_remains_data_not_execution_permission(self):
        self.assertEqual(decode_record(canonical(review()), 'ReviewV2')['expires_ns'], 2)

    def test_failed_review_is_recordable(self):
        value = review(); value.update(verdict='fail', blockers=['GateBlocked'], evidence=[])
        self.assertEqual(validate_record(value, 'ReviewV2'), value)

    def test_pass_with_blocker_rejected(self):
        value = review(); value['blockers'] = ['GateBlocked']
        with self.assertRaises(Failure): validate_record(value, 'ReviewV2')

    def test_missing_extra_or_unknown_kind_rejected(self):
        for value, kind in (({k:v for k,v in review().items() if k != 'phase'}, 'ReviewV2'),
                            (dict(review(), extra=1), 'ReviewV2'), (review(), 'CampaignPlanV2'),
                            (review(), True), (review(), 'InstallationV2')):
            with self.subTest(kind=kind), self.assertRaises(Failure): validate_record(value, kind)

    def test_type_first_enums(self):
        for field, value in (('verdict', True), ('phase', 1), ('schema', []), ('verdict', 'approved')):
            r = review(); r[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_noninteger_or_negative_times_rejected(self):
        for value in (True, -1, 1.0, '1', None):
            r = review(); r['reviewed_ns'] = value
            with self.subTest(value=value), self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_empty_or_reversed_window_rejected(self):
        for end in (0, 1):
            r = review(); r['expires_ns'] = end
            with self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_all_digest_fields_are_strict(self):
        for field, spec in SCHEMAS['ReviewV2'].items():
            if spec == 'H':
                for value in ('A'*64, 'a'*63, '', None, 1, True):
                    r = review(); r[field] = value
                    with self.subTest(field=field, value=value), self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_anchor_exact_keys_and_types(self):
        for value in (dict(review()['anchor'], extra=1), dict(review()['anchor'], ledger_sequence=True), {}, None):
            r = review(); r['anchor'] = value
            with self.subTest(value=value), self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_evidence_sorted_unique_strict_and_prerequisites(self):
        for value in ([H, H], ['b'*64,H], [1], H, []):
            r = review(); r['evidence'] = value
            with self.subTest(value=value), self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_unknown_or_wrong_type_blocker(self):
        for blockers in (['invented'], [True], 'GateBlocked'):
            r = review(); r.update(verdict='fail', blockers=blockers)
            with self.assertRaises(Failure): validate_record(r, 'ReviewV2')

    def test_duplicate_json_keys_rejected(self):
        raw = canonical(review())
        with self.assertRaises(Failure): decode_record(raw[:-1]+b',"verdict":"pass"}', 'ReviewV2')

    def test_float_nonfinite_malformed_and_deep_json_rejected(self):
        for raw in (b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1.0}', b'{', b'[]', b'\xff',
                    b'['*50+b'0'+b']'*50):
            with self.subTest(raw=raw), self.assertRaises(Failure): decode_record(raw, 'ReviewV2')

    def test_noncanonical_bytes_and_invalid_raw_type_rejected(self):
        for raw in (b' '+canonical(review()), json.dumps(review(), indent=1).encode(),
                    canonical(review()).decode(), b''):
            with self.assertRaises(Failure): decode_record(raw, 'ReviewV2')

    def test_raw_codec_golden_values(self):
        self.assertEqual(encode_raw(b'\x00\xff'), 'AP8=')
        self.assertEqual(decode_raw('AP8='), b'\x00\xff')
        self.assertEqual(decode_raw(encode_raw(b'')), b'')

    def test_raw_encoding_not_permissive(self):
        for value in ('Zg', 'Zh==', 'Zg===', 'Zg==\n', '☃', '!!!', b'Zg==', None):
            with self.subTest(value=value), self.assertRaises(Failure): decode_raw(value)

    def test_raw_bounds_and_bytes_type(self):
        for value in (bytearray(b'a'), 'a', b'x'*(MAX_RAW+1)):
            with self.assertRaises(Failure): encode_raw(value)
        with self.assertRaises(Failure): decode_raw('A'*(4*((MAX_RAW+2)//3)+1))

    def test_domain_hash_independent_golden_framing(self):
        expected = hashlib.sha256(b'tag\x00{"a":1}').hexdigest()
        self.assertEqual(domain_hash('tag', {'a':1}), expected)
        self.assertNotEqual(domain_hash('tag-x', {'a':1}), expected)
        self.assertNotEqual(domain_hash('tag', {'a':2}), expected)

    def test_domain_hash_rejects_ambiguous_or_unbounded_values(self):
        for tag, value in (('',{}), ('x\x00y',{}), ('☃',{}), ('x',[]), ('x',{'v':float('nan')}), ('x',{1:'v'})):
            with self.subTest(tag=tag), self.assertRaises(Failure): domain_hash(tag,value)
        cyclic = {}; cyclic['x'] = cyclic
        with self.assertRaises(Failure): domain_hash('x',cyclic)

    def test_campaign_hash_helpers_do_not_claim_schema_validation(self):
        p = dict(schema='capstone-campaign-plan-v2', campaign_plan_sha256=H, x=1)
        expected = hashlib.sha256(b'{"schema":"capstone-campaign-plan-v2","x":1}').hexdigest()
        self.assertEqual(campaign_plan_digest(p), expected)
        changed = dict(p, campaign_plan_sha256='b'*64)
        self.assertEqual(campaign_plan_digest(changed), expected)
        with self.assertRaises(Failure): validate_record(p, 'CampaignPlanV2')
        raw = b'campaign-operation-v2\x00' + json.dumps(dict(campaign_id='run-1',campaign_plan_sha256=H),
                    sort_keys=True,separators=(',',':')).encode()
        self.assertEqual(campaign_operation_id('run-1',H), hashlib.sha256(raw).hexdigest())
        with self.assertRaises(Failure): campaign_operation_id('../escape',H)

    def test_existing_v1_types_stay_unchanged_and_data_only(self):
        import capstone_contract as v1
        before = copy.deepcopy(v1.SCHEMAS)
        anchor = review()['anchor']
        self.assertEqual(decode_record(canonical(anchor),'Anchor'), anchor)
        self.assertEqual(v1.SCHEMAS,before)


if __name__ == '__main__':
    unittest.main()
