"""Stage I provenance-enrichment tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

import spendability_provenance as provenance_module  # noqa: E402
from spendability_provenance import (  # noqa: E402
    APPROVAL_SHA256,
    EXECUTION_COMPLETED_AT,
    EXECUTION_DURATION_MS,
    EXECUTION_STARTED_AT,
    EXPORT_COMMIT,
    LICENSE_REVIEW_SHA256,
    SESSION_EXTRACT_SHA256,
    SESSION_SOURCE_SHA256,
    SOURCE_COMMIT,
    STAGE_H_PACKAGE_SHA256,
    _validate_session_extract,
    build_provenance_record,
    validate_provenance_record,
)
from spendability_stage_c import StageCError  # noqa: E402


class _AbsentSourcePath:
    def __init__(self, original):
        self.original = original

    def __str__(self):
        return self.original

    def exists(self):
        return False


SESSION_EXTRACT = ROOT / 'docs/evidence/spendability/stage-i/SESSION-EXTRACT.json'
PROVENANCE = ROOT / 'docs/evidence/spendability/stage-i/PROVENANCE.json'


class SpendabilityProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session_raw = SESSION_EXTRACT.read_bytes()
        cls.record = build_provenance_record(ROOT)

    def test_binds_exact_stage_h_and_session_inputs(self):
        basis = self.record['basis']
        self.assertEqual(sha256(self.session_raw).hexdigest(),
                         basis['session_extract_sha256'])
        self.assertEqual(basis['session_extract_sha256'], SESSION_EXTRACT_SHA256)
        self.assertEqual(basis['session_source_sha256'], SESSION_SOURCE_SHA256)
        self.assertEqual(basis['stage_h_package_sha256'], STAGE_H_PACKAGE_SHA256)

    def test_session_extract_redacts_credentials_and_kept_custody(self):
        extract = _validate_session_extract(self.session_raw)
        self.assertEqual(extract['source']['sha256'], SESSION_SOURCE_SHA256)
        self.assertEqual({item['line_number'] for item in extract['redactions']},
                         {11465, 11489, 11647})
        text = self.session_raw.decode('utf-8').lower()
        self.assertNotIn('"chars"', text)
        self.assertNotIn('1234', text)
        self.assertNotIn('api_key', text)
        self.assertFalse(extract['security']['credential_values copied'])

    def test_extract_uses_retained_publication_when_source_is_absent(self):
        absent = _AbsentSourcePath(str(provenance_module.SESSION_SOURCE_PATH))
        with mock.patch.object(provenance_module, 'SESSION_SOURCE_PATH', absent):
            extract = _validate_session_extract(self.session_raw)
        source = extract['source']
        self.assertEqual(source['retrieval_method'],
                         'read-only exact JSONL line extraction')
        self.assertEqual(source['sha256'], SESSION_SOURCE_SHA256)
        # The pinned Stage I publication remains valid without inventing a
        # replacement for the mutable original source archive.
        self.assertEqual(len(extract['records']), 12)

    def test_git_custody_binds_source_and_export_commits(self):
        source = self.record['git_custody']['source_commit']
        export = self.record['git_custody']['export_commit']
        self.assertEqual(source['commit'], SOURCE_COMMIT)
        self.assertEqual(export['commit'], EXPORT_COMMIT)
        self.assertEqual(export['parents'], [SOURCE_COMMIT])
        self.assertEqual(source['subject'],
                         'harden(GRRR-gu87): require wheel-owned trusted bootstrap')
        self.assertEqual(export['subject'],
                         'evidence(GRRR-gu87): preserve v4 trusted observation run')

    def test_plan_binds_all_twenty_six_source_code_hashes(self):
        # Build validates every plan code hash against the pinned Git source commit.
        self.assertEqual(self.record['summary']['common_toolchain_profile_candidates'], 1)
        self.assertIn('runtime profile', self.record['items'][0]['common_evidence']
                      ['issuer_code_toolchain_profile']['evidence'])

    def test_authorization_references_are_candidates_not_protected_bytes(self):
        evidence = self.record['items'][0]['common_evidence']['authorization']
        self.assertEqual(evidence['status'], 'candidate-reference-found')
        self.assertIn(APPROVAL_SHA256, self.record['basis']['approval_sha256'])
        self.assertEqual(self.record['basis']['license_review_sha256'],
                         LICENSE_REVIEW_SHA256)
        self.assertIn('exact protected approval/review artifact bytes',
                      evidence['remaining'])

    def test_batch_execution_boundary_is_bound(self):
        boundary = self.record['execution_boundary']
        self.assertEqual(boundary['started_at'], EXECUTION_STARTED_AT)
        self.assertEqual(boundary['completed_at'], EXECUTION_COMPLETED_AT)
        self.assertEqual(boundary['duration_ms'], EXECUTION_DURATION_MS)
        self.assertEqual(boundary['private_runtime'],
                         '/private/tmp/grrr-trusted-rk5jwjmv')
        common = self.record['items'][0]['common_evidence']['measurement_boundary']
        self.assertEqual(common['status'], 'partial-common-candidate')
        self.assertIn('per-reservation UTC start/end', common['remaining'])

    def test_actual_process_identities_do_not_fabricate_request_bindings(self):
        common = self.record['items'][0]['common_evidence']['principal_and_issuer_identity']
        self.assertEqual(common['status'], 'partial-common-candidate')
        self.assertIn('_grrr_evaluator and _grrr_runner', common['evidence'])
        self.assertIn('numeric process UID mapping and per-request authenticated principal/issuer binding',
                      common['remaining'])

    def test_all_eight_candidates_remain_unclassified_and_unready(self):
        items = self.record['items']
        identifiers = [item['request_item_id'] for item in items]
        self.assertEqual(len(items), 8)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(item['classification'] is None for item in items))
        self.assertTrue(all(item['response_readiness']
                            == 'candidate-record-set-not-response-ready'
                            for item in items))
        self.assertTrue(all(item['reservation_specific_missing'] for item in items))
        self.assertEqual(self.record['summary'], {
            'candidate_record_sets': 8,
            'response_ready_record_sets': 0,
            'common_toolchain_profile_candidates': 1,
            'authorization_reference_candidates': 1,
            'batch_execution_boundary_candidates': 1,
            'custody_chain_candidates': 1,
            'final_classifications_made': 0,
        })

    def test_record_remains_fail_closed_and_powerless(self):
        self.assertFalse(self.record['outcome']['response_ready'])
        self.assertFalse(self.record['outcome']['classification_complete'])
        self.assertFalse(self.record['outcome']['valid'])
        self.assertIsNone(self.record['outcome']['spendable'])
        self.assertFalse(self.record['outcome']['execution_authorized'])
        self.assertEqual(self.record['outcome']['allowed_mutations'], [])
        self.assertFalse(any(self.record['authority'].values()))

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_provenance_record(self.record, ROOT)
        self.assertTrue(result['record_valid'])
        self.assertFalse(result['response_ready'])
        self.assertFalse(result['classification_complete'])
        self.assertIsNone(result['spendable'])

    def test_modified_session_extract_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            _validate_session_extract(b'changed')
        self.assertEqual(str(raised.exception),
                         'provenance: Stage I session extract bytes differ')

    def test_classification_and_authority_injection_are_rejected(self):
        classified = deepcopy(self.record)
        classified['items'][0]['classification'] = 'supplied'
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(classified, ROOT)
        self.assertEqual(str(raised.exception),
                         'provenance: record differs from exact regeneration')
        authorized = deepcopy(self.record)
        authorized['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_provenance_record(authorized, ROOT)
        self.assertEqual(str(raised.exception),
                         'provenance: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
