"""Private-temp authority data joins; no protected access or approval proof."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import capstone_installation_authority as authority
from capstone_installation import open_public_fixture
from capstone_installation_record import DIGEST_FIELDS, SCHEMA
from common import Failure, canonical, digest


H_A = 'a' * 64
H_B = 'b' * 64
H_C = 'c' * 64
MAXIMUM = dict(currency='USD', money_cents=1, execution_us=1, review_us=1)
FIXTURE_FILES = {
    'authority/installation.json': b'installation descriptor source fixture\n',
    'authority/registry.json': b'approval registry source fixture\n',
}


def fixture_records(files=FIXTURE_FILES):
    return [dict(relative_path=path, mode=0o444, sha256=digest(data))
            for path, data in sorted(files.items())]


def write_fixture(root, files=FIXTURE_FILES):
    for path, data in sorted(files.items()):
        leaf = Path(root) / path
        leaf.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | os.O_NOFOLLOW, 0o600)
        try:
            os.write(descriptor, data)
        finally:
            os.close(descriptor)
        leaf.chmod(0o444)
    return fixture_records(files)


def installation(*, source_manifest_sha256=H_A, authorization_registry_sha256=H_B,
                 operator_uid=501):
    value = {name: H_C for name in DIGEST_FIELDS}
    value.update(schema=SCHEMA, operator_uid=operator_uid,
                 source_manifest_sha256=source_manifest_sha256,
                 authorization_registry_sha256=authorization_registry_sha256)
    return value


def authorization(*, installation_sha256=H_A, operator_uid=501):
    return dict(schema='capstone-authorization-v1', action='capstone-execute',
                operator_uid=operator_uid, campaign_spec_sha256=H_A,
                baseline_endorsement_sha256=H_A,
                installation_sha256=installation_sha256,
                not_before_ns=10, expires_ns=20, maximum=MAXIMUM,
                leaf_ids=[H_A, H_B], review_anchor=H_C)


def approval(auth=None, *, campaign_id='private-campaign', import_review=H_B,
             issuance_id=H_A):
    auth = authorization() if auth is None else auth
    raw, hashed = authority.encode_authorization(auth)
    return dict(schema='capstone-approval-v1',
                authorization_sha256=hashed,
                authorization_raw=authority.encode_raw(raw),
                campaign_spec_sha256=auth['campaign_spec_sha256'],
                campaign_id=campaign_id, issuance_id=issuance_id,
                receipt_max_age_ns=5, floors=H_A, import_review=import_review)


def registry(*approvals):
    return dict(schema='capstone-approval-registry-v1', entries=list(approvals))


def pinned_records():
    descriptor = installation()
    auth = authorization(installation_sha256=digest(canonical(descriptor)))
    first_registry = registry(approval(auth))
    first_raw, _ = authority.encode_registry(first_registry)
    pinned = dict(descriptor,
                  authorization_registry_sha256=digest(first_raw))
    return canonical(pinned), first_registry


class AuthorityRecordTests(unittest.TestCase):
    def test_exact_authorization_approval_registry_roundtrip_and_hashes(self):
        auth = authorization()
        auth_raw, auth_hash = authority.encode_authorization(auth)
        self.assertEqual(auth_hash, hashlib.sha256(auth_raw).hexdigest())
        self.assertEqual(authority.decode_authorization(auth_raw), auth)

        entry = approval(auth)
        entry_raw, entry_hash = authority.encode_approval(entry)
        self.assertEqual(entry_hash, hashlib.sha256(entry_raw).hexdigest())
        self.assertEqual(authority.decode_approval(entry_raw), entry)
        self.assertIn('"authorization_raw":"' + authority.encode_raw(auth_raw) + '"',
                      entry_raw.decode('ascii'))

        value = registry(entry)
        raw, hashed = authority.encode_registry(value)
        self.assertEqual(hashed, hashlib.sha256(raw).hexdigest())
        self.assertEqual(authority.decode_registry(raw), value)

    def test_exact_fields_types_order_and_windows_rejected(self):
        auth = authorization()
        for field in authority.AUTHORIZATION_FIELDS:
            value = copy.deepcopy(auth)
            del value[field]
            with self.subTest(field=field), self.assertRaises(Failure):
                authority.validate_authorization(value)
        bad_values = []
        for field in ('schema', 'action', 'operator_uid', 'campaign_spec_sha256',
                      'not_before_ns', 'maximum', 'leaf_ids', 'review_anchor'):
            value = copy.deepcopy(auth)
            value[field] = {'invalid sentinel': True}
            bad_values.append((field, value))
        for field, value in list(bad_values) + [
                ('unsorted leaves', dict(auth, leaf_ids=[H_B, H_A])),
                ('duplicate leaves', dict(auth, leaf_ids=[H_A, H_A])),
                ('empty leaves', dict(auth, leaf_ids=[])),
                ('reversed window', dict(auth, not_before_ns=20, expires_ns=20))]:
            with self.subTest(case=field), self.assertRaises(Failure):
                authority.validate_authorization(value)

    def test_noncanonical_duplicate_float_and_bad_embedded_raw_rejected(self):
        auth_raw, _ = authority.encode_authorization(authorization())
        for raw in (b' ' + auth_raw, json.dumps(authorization()).encode(),
                    auth_raw + b' ', auth_raw.decode(),
                    auth_raw[:-1] + b',"schema":"capstone-authorization-v1"}',
                    b'{"not_before_ns":1.0}', b'{"not_before_ns":NaN}', b''):
            with self.subTest(raw=raw[:32]), self.assertRaises(Failure):
                authority.decode_authorization(raw)

        entry = approval()
        entry['authorization_raw'] = authority.encode_raw(b'not-json')
        with self.assertRaises(Failure):
            authority.validate_approval(entry)
        entry = approval()
        entry['authorization_sha256'] = H_A
        with self.assertRaises(Failure):
            authority.validate_approval(entry)

    def test_registry_order_and_unique_keys_rejected(self):
        first = approval(campaign_id='one')
        second = approval(authorization(installation_sha256=H_B),
                          campaign_id='two', issuance_id=H_B)
        ordered = sorted((first, second),
                         key=lambda entry: entry['authorization_sha256'])
        for value in (
            registry(*reversed(ordered)),
            registry(ordered[0], dict(ordered[0])),
            dict(registry(*ordered), schema='capstone-approval-registry-v2'),
            dict(registry(*ordered), entries=[]),
        ):
            with self.subTest(value=value), self.assertRaises(Failure):
                authority.validate_registry(value)
        value = registry(*ordered)
        self.assertIs(authority.validate_registry(value), value)

    def test_registry_pin_rejects_changed_bytes(self):
        descriptor, first_registry = pinned_records()
        installed, registry_value = authority.validate_registry_pin(
            descriptor, canonical(first_registry))
        self.assertEqual(installed['authorization_registry_sha256'],
                         digest(canonical(first_registry)))
        changed = copy.deepcopy(first_registry)
        changed['entries'][0]['receipt_max_age_ns'] = 6
        with self.assertRaises(Failure):
            authority.validate_registry_pin(descriptor, canonical(changed))


class AuthorityResolutionTests(unittest.TestCase):
    def test_full_byte_cycle_or_stale_installation_never_resolves(self):
        descriptor_raw, registry_value = pinned_records()
        with self.assertRaises(Failure) as caught:
            authority.validate_authority_binding(descriptor_raw,
                                                 canonical(registry_value))
        self.assertEqual(caught.exception.record['code'], 'StaleBinding')

        # A forged candidate that claims the final descriptor cannot also be
        # the bytes embedded in the registry pinned by that descriptor.
        descriptor = json.loads(descriptor_raw)
        auth = authorization(installation_sha256=digest(descriptor_raw))
        claim_registry = registry(approval(auth))
        changed = dict(descriptor,
                       authorization_registry_sha256=digest(canonical(claim_registry)))
        with self.assertRaises(Failure):
            authority.validate_authority_binding(canonical(changed),
                                                 canonical(claim_registry))

    def test_import_provenance_is_not_injectable_and_resolver_fails_closed(self):
        entry = approval()
        with self.assertRaisesRegex(Failure, 'provenance is not qualified'):
            authority.require_import_provenance(entry)

        descriptor_raw, registry_value = pinned_records()
        registered_hash = registry_value['entries'][0]['authorization_sha256']
        self.assertNotEqual(H_A, registered_hash)
        with self.assertRaises(Failure) as caught:
            authority.resolve_authorization(
                descriptor_raw, canonical(registry_value), H_A, 15)
        self.assertEqual(caught.exception.record['code'], 'Unavailable')

        # The fixture's registered authorization is bound to the pre-pinned
        # descriptor.  The pinned descriptor changes when it commits that
        # registry, so resolution stops at the installation binding check.
        with self.assertRaises(Failure) as caught:
            authority.resolve_authorization(
                descriptor_raw, canonical(registry_value), registered_hash, 15)
        self.assertEqual(caught.exception.record['code'], 'StaleBinding')

    def test_production_authority_refuses_before_any_filesystem_access(self):
        with patch('builtins.open', side_effect=AssertionError), \
                patch('os.open', side_effect=AssertionError), \
                patch('os.stat', side_effect=AssertionError), \
                patch('os.lstat', side_effect=AssertionError), \
                patch('os.listdir', side_effect=AssertionError):
            for role in (None, 'evaluator', 'reviewer', 'operator'):
                with self.subTest(role=role), self.assertRaises(Failure) as caught:
                    authority.open_installed_authority(role)
                self.assertEqual(caught.exception.record['code'], 'Unavailable')


class DetachedInventoryJoinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-',
                                                 dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.records = write_fixture(self.root)

    def test_private_fixture_inventory_joins_only_as_nonproduction_bytes(self):
        fixture = open_public_fixture(str(self.root), self.records)
        descriptor = installation(source_manifest_sha256=fixture['inventory_sha256'])
        descriptor_raw = canonical(descriptor)
        result = authority.validate_detached_source_inventory(descriptor_raw, fixture)
        self.assertEqual(result, {
            'schema': 'capstone-detached-source-inventory-join-v1',
            'environment': 'NONPRODUCTION',
            'source_manifest_sha256': fixture['inventory_sha256'],
            'trusted_provenance': False,
            'stable_installation': False,
            'inventory_sha256': fixture['inventory_sha256'],
        })

    def test_inventory_or_descriptor_tamper_and_false_provenance_rejected(self):
        fixture = dict(open_public_fixture(str(self.root), self.records))
        descriptor = installation(source_manifest_sha256=fixture['inventory_sha256'])
        for changed in (
            dict(fixture, inventory_raw=b'[]'),
            dict(fixture, inventory_sha256=H_A),
            dict(fixture, trusted_provenance=True),
            dict(fixture, stable_installation=True),
        ):
            with self.subTest(changed=sorted(k for k in changed if fixture.get(k) != changed[k])), \
                    self.assertRaises(Failure):
                authority.validate_detached_source_inventory(canonical(descriptor), changed)

        changed_contents = dict(fixture['contents'])
        changed_contents['authority/installation.json'] = b'changed fixture bytes'
        with self.assertRaises(Failure):
            authority.validate_detached_source_inventory(
                canonical(descriptor), dict(fixture, contents=changed_contents))
        with self.assertRaises(Failure):
            authority.validate_detached_source_inventory(canonical(installation()), fixture)


if __name__ == '__main__':
    unittest.main()
