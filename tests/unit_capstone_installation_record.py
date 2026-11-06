"""InstallationV2 canonical data tests; no installation or authority proof."""
import copy
import hashlib
import json
import unittest

from common import MAX_WIRE, canonical
from capstone_contract import Failure
from capstone_installation_record import (DIGEST_FIELDS, FIELDS, SCHEMA,
    decode_record, encode_record, validate_record)


def installation():
    value = {name: f'{index % 16:x}' * 64 for index, name in enumerate(sorted(DIGEST_FIELDS))}
    value.update(schema=SCHEMA, operator_uid=501)
    return value


class InstallationRecordTests(unittest.TestCase):
    def test_canonical_roundtrip_and_exact_hash(self):
        value = installation()
        raw, hashed = encode_record(value)
        expected = canonical(value)
        self.assertEqual(raw, expected)
        self.assertEqual(hashed, hashlib.sha256(expected).hexdigest())
        self.assertEqual(decode_record(raw), value)
        self.assertEqual(encode_record(decode_record(raw)), (raw, hashed))
        self.assertEqual(FIELDS, {'schema', 'operator_uid'} | DIGEST_FIELDS)

    def test_exact_fields_and_wrong_schema_rejected(self):
        for field in FIELDS:
            value = installation()
            del value[field]
            with self.subTest(field=field, mode='missing'), self.assertRaises(Failure):
                validate_record(value)
        for field in FIELDS:
            value = installation()
            value['extra'] = None
            with self.subTest(field=field, mode='extra'), self.assertRaises(Failure):
                validate_record(value)
        for schema in ('capstone-installation-v1', 'InstallationV2', '', None, 2, True):
            value = installation(); value['schema'] = schema
            with self.subTest(schema=schema), self.assertRaises(Failure):
                validate_record(value)

    def test_operator_uid_strict_and_distinct_from_service_uids(self):
        for uid in (True, False, -1, 0, 1.0, '501', None, 320, 321, 322,
                    4294967295, 4294967296):
            value = installation(); value['operator_uid'] = uid
            with self.subTest(uid=uid), self.assertRaises(Failure):
                validate_record(value)

    def test_every_digest_field_is_exact_lowercase_sha256_text(self):
        for field in DIGEST_FIELDS:
            for value in ('A' * 64, 'a' * 63, 'a' * 65, '', 'z' * 64, 1, True,
                          None, b'a' * 64):
                record = installation(); record[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(Failure):
                    validate_record(record)

    def test_duplicate_noncanonical_float_and_wrong_type_bytes_rejected(self):
        value = installation()
        raw = canonical(value)
        duplicate = raw[:-1] + b',"schema":"capstone-installation-v2"}'
        noncanonical = [
            b' ' + raw, json.dumps(value, indent=1).encode(), raw.decode(),
            raw + b' ', b'', b'[]', b'\xff', b'{"operator_uid":501.0}',
            b'{"operator_uid":NaN}', b'{"operator_uid":Infinity}',
        ]
        for bad in [duplicate, *noncanonical]:
            with self.subTest(bad=bad[:40]), self.assertRaises(Failure):
                decode_record(bad)

    def test_oversize_descriptor_rejected_before_decoding(self):
        for raw in (b'x' * (MAX_WIRE + 1), bytearray(canonical(installation())), None):
            with self.subTest(type=type(raw).__name__), self.assertRaises(Failure):
                decode_record(raw)

    def test_valid_data_is_not_authority(self):
        # Encode/decode intentionally returns only data bytes/hash and has no
        # authority-returning surface to assert against.
        value = installation()
        raw, hashed = encode_record(value)
        changed = copy.deepcopy(value)
        changed['corpus_sha256'] = 'f' * 64
        changed_raw, changed_hash = encode_record(changed)
        self.assertNotEqual((raw, hashed), (changed_raw, changed_hash))


if __name__ == '__main__':
    unittest.main()
