"""Mandatory real UID-separated execution of every frozen corpus scenario."""
import json
import os
from pathlib import Path
import sys
import time
import uuid
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'research'))
from common import EVALUATOR, canonical, require
from corpus_evaluation import CorpusSession
from corpus_execution import validate_config
from ledger import verifySnapshot
from trusted_execution import root_record, validate_approval


class ValidatedCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require(len(sys.argv) == 2 and os.getuid() == EVALUATOR, 'Unauthorized',
                'AWAITING_PARENT_IDENTITY_RUN: approved corpus launcher and UID 320 required')
        cls.runtime = Path(sys.argv[1]); require(cls.runtime.parent == Path('/private/tmp')
            and cls.runtime.name.startswith('grrr-corpus-') and cls.runtime.stat().st_uid == 0,
            'Unauthorized', 'Untrusted corpus runtime')
        config = validate_config(root_record(cls.runtime/'runner/config.json'))
        validate_approval(root_record(cls.runtime/'runner/approval.json'), config,
                          root_record(cls.runtime/'runner/license.json'))
        cls.session = CorpusSession(cls.runtime/'evaluator'); cls.started = time.monotonic()

    @classmethod
    def tearDownClass(cls):
        if not hasattr(cls, 'session'): return
        summary = getattr(cls, 'summary', {'required': 32, 'executed': 0, 'skipped': 0,
                                            'failures': 1, 'errors': 0})
        snapshot = cls.session.ledger.snapshot({'kind':'validated-corpus-suite', 'summary': summary},
                                                uuid.uuid4().hex)
        (cls.session.root/'snapshot.json').write_bytes(canonical(snapshot))
        (cls.session.root/'summary.json').write_bytes(canonical(summary))
        cls.session.budget.db.close()

    def test_01_every_scenario_three_real_isolated_repetitions(self):
        manifest = json.loads((self.session.root/'corpus/manifest.json').read_bytes())
        observations = []
        challenges = sorted(manifest['challenge_ids'], key=lambda value: (not value.endswith('C001'), value))
        for challenge in challenges:
            with self.subTest(challenge=challenge):
                result, decision = self.session.execute(challenge); guest = result['guest']
                self.assertTrue(guest['supervisor_unchanged'])
                self.assertTrue(guest['kernel_lock_held_by_supervisor'])
                self.assertTrue(guest['candidate_exit_success'])
                self.assertEqual(decision['fixture_validation'], 'pass')
                self.assertEqual(len(guest['candidate_observation']['repetitions']), 3)
                self.assertTrue(decision['deterministic'])
                observations.append({'challenge': challenge, 'run': result['run'],
                                     'expected': decision['expected'], 'observed': decision['observed'],
                                     'repetitions': decision['repetitions'], 'seconds': result['seconds'],
                                     'raw_sha256': result['raw_sha256'], 'verified': False})
        self.assertEqual(len(observations), 32)
        (self.session.root/'observations.json').write_bytes(canonical(observations))
        self.__class__.summary = {'required': 32, 'executed': len(observations), 'skipped': 0,
                                  'failures': 0, 'errors': 0, 'repetitions': 96,
                                  'mandatory_isolated_fixture_gate': 'executed',
                                  'elapsed_seconds': time.monotonic()-self.started,
                                  'verified': False, 'admission': 'blocked'}

    def test_02_counts_and_clean_fault_partition(self):
        observations = json.loads((self.session.root/'observations.json').read_bytes())
        clean = [item for item in observations if item['expected'] == 'clean']
        defect = [item for item in observations if item['expected'] == 'defect']
        self.assertEqual(len(clean), 8); self.assertEqual(len(defect), 24)
        self.assertTrue(all(item['observed'] == item['expected'] for item in observations))

    def test_03_durable_ledger_snapshot_is_verifiable(self):
        snapshot = json.loads((self.session.root/'snapshot.json').read_bytes())
        verifySnapshot(snapshot, snapshot['receipt']['digest'])
        self.assertEqual(snapshot['events'][0]['event']['kind'], 'corpus-reserved')
        self.assertGreaterEqual(len(snapshot['events']), 96)

    def test_04_downstream_gates_remain_blocked(self):
        summary = json.loads((self.session.root/'summary.json').read_bytes())
        self.assertEqual(summary['mandatory_isolated_fixture_gate'], 'executed')
        self.assertFalse(summary['verified']); self.assertEqual(summary['admission'], 'blocked')


if __name__ == '__main__':
    unittest.main(verbosity=2, argv=[sys.argv[0]])
