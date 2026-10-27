"""Stage C adapter and sidecar-schema tests; no protected path is opened."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_stage_c import (  # noqa: E402
    APPROVED_LOCK_PROTOCOL, APPROVED_LOCK_PROTOCOL_SHA256,
    APPROVED_MUTATOR_COVERAGE_SHA256, AUTHORITY_FIELDS, DATABASE_SHA256,
    EXPECTED_DDL, LINEAGE_ARTIFACTS, OVERHEAD_CATEGORIES, RESERVATION_IDS,
    STAGE_A_BASELINE_SHA256, StageCError,
    stage_a_schema_gap, unresolved_stage_c_outcome, validate_completeness_record,
    validate_pending_disposition, validate_provenance_record,
    validate_quiescence_record, validate_schema_compatibility,
)


STAGE_A = ROOT / 'docs/evidence/spendability/stage-a/BASELINE.json'
DUMMY_HASH = hashlib.sha256(b'stage-c-test').hexdigest()


def authority_false():
    return {name: False for name in AUTHORITY_FIELDS}


def review_unresolved():
    return {'status': 'unresolved', 'review_sha256': None}


def raw_schema_fixture() -> dict:
    baseline = json.loads(STAGE_A.read_bytes())
    connection = sqlite3.connect(':memory:')
    for ddl in EXPECTED_DDL.values():
        connection.execute(ddl)

    def dict_rows(cursor):
        names = [description[0] for description in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    master = [{'type': row['type'], 'name': row['name'], 'table': row['tbl_name'], 'sql': row['sql']}
              for row in dict_rows(connection.execute(
                  "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"))]
    tables = tuple(sorted(EXPECTED_DDL))
    table_info = {table: dict_rows(connection.execute('PRAGMA table_info(' + table + ')'))
                  for table in tables}
    index_list = {table: dict_rows(connection.execute('PRAGMA index_list(' + table + ')'))
                  for table in tables}
    index_xinfo = {}
    for table in tables:
        index_xinfo[table] = {}
        for item in index_list[table]:
            index_xinfo[table][item['name']] = dict_rows(
                connection.execute('PRAGMA index_xinfo("' + item['name'] + '")'))
    foreign_keys = {table: dict_rows(connection.execute('PRAGMA foreign_key_list(' + table + ')'))
                    for table in tables}
    before = baseline['database']['before']
    database = {name: before[name] for name in (
        'sha256', 'device', 'inode', 'mode', 'uid', 'gid', 'nlink', 'size', 'acl')}
    return {
        'schema_version': 1,
        'database': database,
        'sqlite_master': master,
        'table_info': table_info,
        'index_list': index_list,
        'index_xinfo': index_xinfo,
        'foreign_keys': foreign_keys,
        'application_metadata': {
            'user_version': 0, 'application_id': 0,
            'journal_mode': 'delete', 'encoding': 'UTF-8',
        },
    }


def database_observation() -> dict:
    source = json.loads(STAGE_A.read_bytes())['database']['before']
    value = {name: source[name] for name in (
        'sha256', 'device', 'inode', 'mode', 'uid', 'gid', 'nlink', 'size', 'acl')}
    value['observed_at'] = '2026-10-26T00:00:30Z'
    return value


def lock_identity() -> dict:
    return {'device': 16777229, 'inode': 682589446, 'mode': 384,
            'uid': 320, 'gid': 320, 'nlink': 1, 'acl': 'no-acl'}


def quiescence_fixture() -> dict:
    identity = lock_identity()
    baseline = json.loads(STAGE_A.read_bytes())
    policy_hash = baseline['source_files']['policy_contract']['sha256']
    interpreter_hash = '5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26'
    observed = database_observation()
    locked = deepcopy(observed)
    locked['observed_at'] = '2026-10-26T00:00:40Z'
    after = deepcopy(observed)
    after['observed_at'] = '2026-10-26T00:00:50Z'
    return {
        'schema_version': 1,
        'record_type': 'writer-exclusion-v1',
        'baseline_sha256': STAGE_A_BASELINE_SHA256,
        'database_sha256': DATABASE_SHA256,
        'lock': {
            'path': '/Library/GRRR/accounting-poc2/launch.lock',
            'protocol_version': APPROVED_LOCK_PROTOCOL,
            'exclusive': True,
            'all_approved_mutators_covered': True,
            'identity_before': identity,
            'identity_opened': deepcopy(identity),
            'identity_released': deepcopy(identity),
            'acquired_at': '2026-10-26T00:00:00Z',
            'released_at': '2026-10-26T00:01:00Z',
            'acl': 'no-acl',
            'approved_protocol_sha256': APPROVED_LOCK_PROTOCOL_SHA256,
            'mutator_coverage_sha256': APPROVED_MUTATOR_COVERAGE_SHA256,
        },
        'observations': {
            'before': observed,
            'locked': locked,
            'after': after,
        },
        'sidecars': [],
        'process_inventory': {
            'uid_320_count': 0, 'uid_321_count': 0, 'qemu_count': 0,
            'inventory_sha256': DUMMY_HASH,
        },
        'toolchain': {
            'parent_code': {'observed_sha256': DUMMY_HASH, 'expected_sha256': DUMMY_HASH},
            'interpreter': {'observed_sha256': interpreter_hash, 'expected_sha256': interpreter_hash},
            'policy': {'observed_sha256': policy_hash, 'expected_sha256': policy_hash},
        },
        'review': review_unresolved(),
        'authority': authority_false(),
    }


def provenance_fixture(status='authenticated',
                       reservation_id='1bf9d516461040c0baef70648c074d61') -> dict:
    unresolved = status == 'unresolved'
    baseline = json.loads(STAGE_A.read_bytes())
    row = next(item for item in baseline['raw_tables']['reservations']['rows']
               if item['id']['value'] == reservation_id)
    request_blob = bytes.fromhex(row['binding']['blob_hex'])
    request_raw_hash = hashlib.sha256(request_blob).hexdigest()
    request_projection = hashlib.sha256(json.dumps(
        row['binding']['decoded'], sort_keys=True, separators=(',', ':'),
        ensure_ascii=True, allow_nan=False).encode('ascii')).hexdigest()
    settled = row['actual'].get('decoded') is not None
    meter_id = row['receipt']['value'] if settled else None
    usage_hash = (hashlib.sha256(json.dumps(
        row['actual']['decoded'], sort_keys=True, separators=(',', ':'),
        ensure_ascii=True, allow_nan=False).encode('ascii')).hexdigest()
        if settled else None)
    return {
        'schema_version': 1,
        'record_type': 'reservation-provenance-v1',
        'status': status,
        'reservation_id': reservation_id,
        'run': row['run']['value'],
        'stage': 'poc',
        'request': {
            'status': 'missing' if unresolved else 'present',
            'raw_sha256': None if unresolved else request_raw_hash,
            'canonical_sha256': None if unresolved else request_projection,
            'binding_authorized': False if unresolved else True,
        },
        'issuer': {
            'status': 'missing' if unresolved else 'authenticated',
            'principal_id': None if unresolved else 'issuer-320',
            'authenticated': False if unresolved else True,
            'code_sha256': None if unresolved else DUMMY_HASH,
            'toolchain_sha256': None if unresolved else DUMMY_HASH,
            'policy_sha256': None if unresolved else DUMMY_HASH,
            'runtime_profile_sha256': None if unresolved else DUMMY_HASH,
        },
        'measurement': {
            'status': 'missing' if unresolved else 'bounded',
            'started_at': None if unresolved else '2026-10-25T00:00:00Z',
            'ended_at': None if unresolved else '2026-10-25T00:01:00Z',
            'clock': None if unresolved else 'UTC-monotonic',
            'window_sha256': None if unresolved else DUMMY_HASH,
        },
        'source': {
            'status': 'missing' if unresolved else 'retained',
            'path': None if unresolved else 'protected://reservation/1',
            'raw_sha256': None if unresolved else request_raw_hash,
            'projection_sha256': None if unresolved else request_projection,
        },
        'meter': {
            'status': 'missing' if unresolved or not settled else 'bound',
            'meter_id': None if unresolved else meter_id,
            'usage_sha256': None if unresolved else usage_hash,
        },
        'review': review_unresolved(),
        'authority': authority_false(),
    }


def pending_fixture(status='unresolved') -> dict:
    resolved = status != 'unresolved'
    dispatched = False
    cessation_required = bool(resolved and dispatched)
    return {
        'schema_version': 1,
        'record_type': 'pending-disposition-v1',
        'status': status,
        'reservation_id': '69523b39a51c44739114313c9325028c',
        'maximum': {'currency': 'USD', 'money_cents': 0,
                    'execution_us': 300000000, 'review_us': 0},
        'request_id': 'request-1' if resolved else None,
        'idempotency_key': 'key-1' if resolved else None,
        'operation_id': 'operation-1' if resolved else None,
        'final_observation_sha256': DUMMY_HASH if resolved else None,
        'cessation': {
            'required': cessation_required,
            'observed': cessation_required,
            'method': 'process-group-absence' if cessation_required else 'not-required',
            'evidence_sha256': DUMMY_HASH,
        },
        'dispatch': {
            'status': 'unknown' if not resolved else 'not-dispatched',
            'evidence_sha256': None if not resolved else DUMMY_HASH,
        },
        'evaluator_state': {
            'state': 'active_or_unknown' if not resolved else 'stopped_or_halted',
            'evidence_sha256': None if not resolved else DUMMY_HASH,
        },
        'baseline_before_sha256': DATABASE_SHA256,
        'baseline_after_sha256': DATABASE_SHA256,
        'stale_handles_accounted': True if resolved else False,
        'missing_evidence': [] if resolved else ['final-observation', 'cessation'],
        'review': review_unresolved(),
        'authority': authority_false(),
    }


def completeness_fixture() -> dict:
    lineage = [{'artifact': artifact, 'status': 'unresolved', 'record_sha256': None,
                'unexplained': [artifact + '-record']} for artifact in sorted(LINEAGE_ARTIFACTS)]
    reservations = [{'reservation_id': reservation, 'status': 'unresolved',
                     'record_sha256': None,
                     'unexplained': [reservation + '-request']} for reservation in sorted(RESERVATION_IDS)]
    return {
        'schema_version': 1,
        'record_type': 'historical-completeness-v1',
        'status': 'unresolved',
        'lineage': lineage,
        'reservation_coverage': reservations,
        'operation_coverage': [
            {'status': 'unresolved', 'record_sha256': None, 'unexplained': ['operations']},
        ],
        'side_store_coverage': [
            {'status': 'unresolved', 'record_sha256': None, 'unexplained': ['side-stores']},
        ],
        'overhead': {
            category: {
                'status': 'unresolved', 'actor': 'unresolved',
                'boundary': '2026-campaign-boundary', 'source_sha256': DUMMY_HASH,
                'upper_bound_us': None,
            } for category in sorted(OVERHEAD_CATEGORIES)
        },
        'missing_history': ['overlap', 'paid-service', 'manual-adjustment'],
        'unbounded_unknown': True,
        'review': review_unresolved(),
        'authority': authority_false(),
    }


class SchemaCompatibilityAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = STAGE_A.read_bytes()
        cls.raw = raw_schema_fixture()

    def test_stage_a_shape_is_retained_but_extended_schema_remains_unresolved(self):
        gap = stage_a_schema_gap(self.baseline)
        self.assertEqual(gap['status'], 'unresolved')
        self.assertIn('index_xinfo', gap['missing_evidence'])
        self.assertEqual(gap['independent_review'], 'unresolved')
        self.assertFalse(any(gap['authority'].values()))

    def test_complete_raw_schema_maps_every_semantic_object(self):
        result = validate_schema_compatibility(self.raw)
        self.assertEqual(result['status'], 'mapped')
        self.assertEqual(set(result['semantic_objects']),
                         {'state', 'reservations', 'metering', 'overhead', 'store_identity',
                          'state_id_unique', 'reservation_id_unique', 'reservation_key_unique',
                          'metering_id_unique', 'metering_reservation_unique', 'overhead_key_unique'})
        self.assertNotEqual(result['raw_schema_sha256'], result['mapped_contract_schema_sha256'])
        self.assertEqual(result['independent_review'], 'unresolved')
        self.assertFalse(any(result['authority'].values()))

    def test_fixture_is_generated_from_real_sqlite_introspection(self):
        self.assertEqual(self.raw['index_list']['metering'], [
            {'seq': 0, 'name': 'sqlite_autoindex_metering_2', 'unique': 1, 'origin': 'u', 'partial': 0},
            {'seq': 1, 'name': 'sqlite_autoindex_metering_1', 'unique': 1, 'origin': 'pk', 'partial': 0},
        ])
        self.assertEqual(self.raw['index_list']['reservations'], [
            {'seq': 0, 'name': 'sqlite_autoindex_reservations_2', 'unique': 1, 'origin': 'u', 'partial': 0},
            {'seq': 1, 'name': 'sqlite_autoindex_reservations_1', 'unique': 1, 'origin': 'pk', 'partial': 0},
        ])
        metering_id = self.raw['index_xinfo']['metering']['sqlite_autoindex_metering_1']
        self.assertEqual(metering_id[0],
                         {'seqno': 0, 'cid': 0, 'name': 'id', 'desc': 0, 'coll': 'BINARY', 'key': 1})
        self.assertEqual(metering_id[1],
                         {'seqno': 1, 'cid': -1, 'name': None, 'desc': 0, 'coll': 'BINARY', 'key': 0})

    def test_changed_ddl_fails_before_mapping(self):
        value = deepcopy(self.raw)
        item = next(row for row in value['sqlite_master']
                    if row['type'] == 'table' and row['name'] == 'metering')
        item['sql'] += ' '
        with self.assertRaises(StageCError) as raised:
            validate_schema_compatibility(value)
        self.assertEqual(str(raised.exception), 'schema_fingerprint: metering DDL differs')

    def test_missing_index_inventory_fails_closed(self):
        value = deepcopy(self.raw)
        value['index_list']['metering'].pop(0)
        with self.assertRaises(StageCError) as raised:
            validate_schema_compatibility(value)
        self.assertEqual(str(raised.exception),
                         'schema_fingerprint: metering semantic index mapping differs')

    def test_unapproved_foreign_key_fails(self):
        value = deepcopy(self.raw)
        value['foreign_keys']['metering'] = [{'example': True}]
        with self.assertRaises(StageCError) as raised:
            validate_schema_compatibility(value)
        self.assertEqual(str(raised.exception),
                         'schema_fingerprint: unapproved foreign-key constraint exists')

    def test_extended_column_change_cannot_retain_schema(self):
        value = deepcopy(self.raw)
        value['table_info']['metering'][1]['notnull'] = 0
        with self.assertRaises(StageCError) as raised:
            validate_schema_compatibility(value)
        self.assertEqual(str(raised.exception), 'schema_fingerprint: metering column declaration differs')

    def test_per_index_xinfo_binding_is_required(self):
        value = deepcopy(self.raw)
        value['index_xinfo']['reservations']['sqlite_autoindex_reservations_1'][0]['name'] = 'key'
        with self.assertRaises(StageCError) as raised:
            validate_schema_compatibility(value)
        self.assertEqual(str(raised.exception),
                         'schema_fingerprint: sqlite_autoindex_reservations_1 key xinfo differs')

    def test_application_metadata_is_pinned(self):
        value = deepcopy(self.raw)
        value['application_metadata']['application_id'] = 1
        with self.assertRaises(StageCError) as raised:
            validate_schema_compatibility(value)
        self.assertEqual(str(raised.exception), 'schema_fingerprint: database application metadata differs')

    def test_forged_parsed_stage_a_baseline_is_rejected_by_byte_hash(self):
        parsed = json.loads(self.baseline)
        parsed['raw_tables']['reservations']['rows'][0]['run']['value'] = 'forged-run'
        forged = json.dumps(parsed, sort_keys=True, separators=(',', ':')).encode('ascii')
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(provenance_fixture(), forged)
        self.assertEqual(str(raised.exception),
                         'provenance: retained Stage A baseline SHA-256 differs')


class QuiescenceSidecar(unittest.TestCase):
    def test_valid_writer_exclusion_schema_remains_unreviewed_and_powerless(self):
        result = validate_quiescence_record(quiescence_fixture())
        self.assertTrue(result['schema_valid'])
        self.assertTrue(result['writer_exclusion_recorded'])
        self.assertFalse(result['writer_exclusion_observed'])
        self.assertFalse(result['writer_exclusion_proven'])
        self.assertEqual(result['review_status'], 'unresolved')
        self.assertFalse(result['valid'])
        self.assertIsNone(result['spendable'])
        self.assertFalse(result['execution_authorized'])

    def test_sensitive_process_rejects_quiescence(self):
        value = quiescence_fixture()
        value['process_inventory']['qemu_count'] = 1
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception), 'quiescence: sensitive process inventory is nonempty')

    def test_database_drift_rejects_quiescence(self):
        value = quiescence_fixture()
        value['observations']['after']['sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception),
                         'quiescence: database identity changed during the locked window')

    def test_authority_flag_rejects_quiescence(self):
        value = quiescence_fixture()
        value['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception), 'quiescence: sidecar authority must remain entirely false')

    def test_mutually_stable_unrelated_database_rejects_quiescence(self):
        value = quiescence_fixture()
        for name in ('before', 'locked', 'after'):
            value['observations'][name]['sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception),
                         'quiescence: observed database is not the pinned Stage A database')

    def test_unapproved_lock_protocol_rejects_quiescence(self):
        value = quiescence_fixture()
        value['lock']['protocol_version'] = 'unapproved-v2'
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception),
                         'quiescence: lock protocol is not the approved accounting-poc2 protocol')

    def test_nonchronological_lock_window_rejects_quiescence(self):
        value = quiescence_fixture()
        value['lock']['acquired_at'] = '2026-10-26T00:02:00Z'
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception), 'quiescence: lock window is not chronological')

    def test_unapproved_lock_path_rejects_quiescence(self):
        value = quiescence_fixture()
        value['lock']['path'] = '/tmp/unrelated.lock'
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception),
                         'quiescence: lock path differs from the accounting-poc2 launch lock')

    def test_extended_acl_representation_rejects_quiescence(self):
        value = quiescence_fixture()
        value['lock']['acl'] = 'user:evil allow write'
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception),
                         'quiescence: lock ACL differs from the approved no-ACL representation')

    def test_stage_c_cannot_claim_approved_quiescence_review(self):
        value = quiescence_fixture()
        value['review'] = {'status': 'approved', 'review_sha256': DUMMY_HASH}
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception),
                         'quiescence: Stage C cannot claim reviewed quiescence proof')

    def test_toolchain_observation_must_equal_expected_identity(self):
        value = quiescence_fixture()
        value['toolchain']['interpreter']['observed_sha256'] = DUMMY_HASH
        value['toolchain']['interpreter']['expected_sha256'] = STAGE_A_BASELINE_SHA256
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception), 'quiescence: toolchain interpreter identity differs')

    def test_observation_timestamps_must_be_ordered(self):
        value = quiescence_fixture()
        value['observations']['locked']['observed_at'] = '2026-10-26T00:00:20Z'
        with self.assertRaises(StageCError) as raised:
            validate_quiescence_record(value)
        self.assertEqual(str(raised.exception), 'quiescence: before-to-locked window is not chronological')


class ProvenanceAndPendingSidecars(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = STAGE_A.read_bytes()

    def test_authenticated_provenance_is_schema_valid_but_not_spendability(self):
        result = validate_provenance_record(provenance_fixture(), self.baseline)
        self.assertTrue(result['schema_valid'])
        self.assertEqual(result['status'], 'authenticated')
        self.assertFalse(result['valid'])
        self.assertIsNone(result['spendable'])

    def test_unresolved_provenance_may_not_assert_evidence(self):
        value = provenance_fixture('unresolved')
        result = validate_provenance_record(value, self.baseline)
        self.assertEqual(result['status'], 'unresolved')
        value['source']['raw_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: unresolved provenance cannot assert incomplete evidence')

    def test_unauthenticated_issuer_fails_authenticated_provenance(self):
        value = provenance_fixture()
        value['issuer']['authenticated'] = False
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: issuer authentication differs must be True')

    def test_retained_run_binding_is_required(self):
        value = provenance_fixture()
        value['run'] = 'unrelated-run'
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: provenance run or stage differs from retained evidence')

    def test_request_provenance_must_reproduce_retained_bytes(self):
        value = provenance_fixture()
        value['request']['raw_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: request provenance does not reproduce retained bytes')

    def test_pending_reservation_cannot_claim_bound_meter(self):
        value = provenance_fixture(reservation_id='69523b39a51c44739114313c9325028c')
        value['meter']['status'] = 'bound'
        value['meter']['meter_id'] = DUMMY_HASH
        value['meter']['usage_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: pending reservation cannot assert settled meter provenance')

    def test_missing_meter_group_cannot_assert_meter_evidence(self):
        value = provenance_fixture(reservation_id='69523b39a51c44739114313c9325028c')
        value['meter']['meter_id'] = DUMMY_HASH
        value['meter']['usage_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: missing meter link cannot assert meter evidence')

    def test_unresolved_group_status_cannot_assert_authenticated(self):
        value = provenance_fixture('unresolved')
        value['issuer']['status'] = 'authenticated'
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: unresolved provenance groups must all be missing')

    def test_measurement_window_must_be_chronological(self):
        value = provenance_fixture()
        value['measurement']['started_at'] = '2026-10-25T00:02:00Z'
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(value, self.baseline)
        self.assertEqual(str(raised.exception),
                         'provenance: measurement window is not chronological')

    def test_unresolved_pending_retains_full_maximum(self):
        result = validate_pending_disposition(pending_fixture())
        self.assertEqual(result['status'], 'unresolved')
        self.assertTrue(result['full_maximum_retained'])
        self.assertIsNone(result['spendable'])

    def test_pending_maximum_cannot_be_reduced(self):
        value = pending_fixture()
        value['maximum']['execution_us'] = 0
        with self.assertRaises(StageCError) as raised:
            validate_pending_disposition(value)
        self.assertEqual(str(raised.exception),
                         'pending_evidence: pending maximum differs from the retained full hold')

    def test_unresolved_pending_cannot_assert_final_observation(self):
        value = pending_fixture()
        value['final_observation_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_pending_disposition(value)
        self.assertEqual(str(raised.exception),
                         'pending_evidence: unresolved pending sidecar asserts a final observation')

    def test_resolved_pending_requires_stale_handles_accounted(self):
        value = pending_fixture('failed_not_dispatched')
        value['cessation']['required'] = False
        value['cessation']['observed'] = False
        value['cessation']['method'] = 'not-required'
        value['stale_handles_accounted'] = False
        with self.assertRaises(StageCError) as raised:
            validate_pending_disposition(value)
        self.assertEqual(str(raised.exception), 'pending_evidence: stale handles differs must be True')

    def test_pending_baseline_must_be_pinned_to_stage_a(self):
        value = pending_fixture()
        value['baseline_before_sha256'] = DUMMY_HASH
        value['baseline_after_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_pending_disposition(value)
        self.assertEqual(str(raised.exception),
                         'pending_evidence: pending disposition changed the protected baseline')

    def test_failed_not_dispatched_cannot_claim_dispatched_evidence(self):
        value = pending_fixture('failed_not_dispatched')
        value['dispatch']['status'] = 'dispatched'
        value['cessation']['required'] = True
        value['cessation']['observed'] = True
        value['cessation']['method'] = 'process-group-absence'
        with self.assertRaises(StageCError) as raised:
            validate_pending_disposition(value)
        self.assertEqual(str(raised.exception),
                         'pending_evidence: failed_not_dispatched contradicts dispatch evidence')

    def test_unresolved_pending_cannot_assert_dispatch_evidence(self):
        value = pending_fixture()
        value['dispatch']['status'] = 'not-dispatched'
        value['dispatch']['evidence_sha256'] = DUMMY_HASH
        with self.assertRaises(StageCError) as raised:
            validate_pending_disposition(value)
        self.assertEqual(str(raised.exception),
                         'pending_evidence: unresolved contradicts dispatch evidence')


class CompletenessSidecar(unittest.TestCase):
    def test_unresolved_completeness_preserves_unknowns(self):
        result = validate_completeness_record(completeness_fixture())
        self.assertTrue(result['schema_valid'])
        self.assertEqual(result['status'], 'unresolved')
        self.assertTrue(result['schema_valid'])
        self.assertIsNone(result['spendable'])
        self.assertEqual(result['allowed_mutations'], [])

    def test_unresolved_history_cannot_claim_bounded_unknown(self):
        value = completeness_fixture()
        value['unbounded_unknown'] = False
        with self.assertRaises(StageCError) as raised:
            validate_completeness_record(value)
        self.assertEqual(str(raised.exception), 'historical_completeness: unbounded unknown differs must be True')

    def test_unresolved_overhead_cannot_invent_zero_upper_bound(self):
        value = completeness_fixture()
        value['overhead']['other']['upper_bound_us'] = 0
        with self.assertRaises(StageCError) as raised:
            validate_completeness_record(value)
        self.assertEqual(str(raised.exception),
                         'historical_completeness: other unresolved upper bound must be null')

    def test_missing_reservation_coverage_fails(self):
        value = completeness_fixture()
        value['reservation_coverage'].pop()
        with self.assertRaises(StageCError) as raised:
            validate_completeness_record(value)
        self.assertEqual(str(raised.exception),
                         'historical_completeness: reservation coverage count differs')

    def test_complete_status_cannot_retain_unresolved_children(self):
        value = completeness_fixture()
        value['status'] = 'complete'
        value['missing_history'] = []
        value['unbounded_unknown'] = False
        with self.assertRaises(StageCError) as raised:
            validate_completeness_record(value)
        self.assertEqual(str(raised.exception),
                         'historical_completeness: operation_coverage is unresolved in a complete record')

    def test_empty_operation_coverage_is_not_affirmative_absence(self):
        value = completeness_fixture()
        value['operation_coverage'] = []
        with self.assertRaises(StageCError) as raised:
            validate_completeness_record(value)
        self.assertEqual(str(raised.exception), 'historical_completeness: operation_coverage differs')

    def test_missing_history_must_be_meaningful_strings(self):
        value = completeness_fixture()
        value['missing_history'] = [None]
        with self.assertRaises(StageCError) as raised:
            validate_completeness_record(value)
        self.assertEqual(str(raised.exception),
                         'historical_completeness: missing history entry contains unsafe or empty text')


class FailClosedOutcome(unittest.TestCase):
    def test_stage_c_outcome_never_becomes_spendability(self):
        outcome = unresolved_stage_c_outcome('schema_fingerprint')
        self.assertFalse(outcome['valid'])
        self.assertIsNone(outcome['spendable'])
        self.assertEqual(outcome['allowed_mutations'], [])
        self.assertFalse(outcome['execution_authorized'])
        self.assertFalse(any(outcome['authority'].values()))


if __name__ == '__main__':
    unittest.main()
