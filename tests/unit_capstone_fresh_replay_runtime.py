"""Real offline files/SQLite; guards are only for forbidden syscall assertions."""
import copy
import errno
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from common import Failure, canonical, digest
from fresh_replay_runtime import (BINDINGS, PREDECESSOR, RECOVERY, Proposal,
                                  fixture_preflight, prepare, validate_proposal)


class SpoofDigest(str):
    def __eq__(self, other):
        return True


class SubclassDict(dict):
    """Exact-type rejection probe for JSON object subclasses."""


class SubclassList(list):
    """Exact-type rejection probe for JSON array subclasses."""


class FreshRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grrr-734u-', dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.request = {'version': 1, 'namespace': 'a' * 32, 'target_state': 'absent',
                        'used_namespaces': ['b' * 32],
                        'predecessor': {'identity': 'c' * 64, 'target': PREDECESSOR,
                                        'replay_state': 'consumed', 'replay_count': 1},
                        'bindings': {}, 'identities': {'predecessor': 'c' * 64}}
        self.evidence = {}
        for name in BINDINGS:
            path = self.root / name
            if name == 'accounting':
                with sqlite3.connect(str(path)) as db:
                    db.execute('CREATE TABLE ledger (replay_state TEXT, replay_count INTEGER, unknown_cost TEXT, hold TEXT)')
                    db.execute("INSERT INTO ledger VALUES ('consumed', 1, NULL, 'retained')")
            else:
                path.write_bytes(canonical({'fixture': name, 'state': 'consumed'}))
            archive = digest(path.read_bytes())
            payload = {'archive_sha256': archive, 'fixture': name}
            if name == 'accounting':
                payload = {'archive_sha256': archive, 'version': 4, 'recovery_receipt': RECOVERY,
                           'unknowns': {'cost': None}, 'holds': ['retained']}
            identity = digest(name.encode())
            self.request['bindings'][name] = {'identity': identity, 'sha256': digest(canonical(payload)),
                                             'payload': payload}
            self.request['identities'][name] = identity
            self.evidence[name] = {'path': str(path), 'sha256': archive}
        self.before = self.snapshot()

    def snapshot(self):
        return {p.name: (p.read_bytes(), p.stat().st_ino) for p in self.root.iterdir() if p.is_file()}

    def request_hash(self):
        return digest(canonical(self.request))

    def run_fixture(self, **overrides):
        args = {'sandbox': str(self.root), 'target': str(self.root / ('replay-' + 'a' * 32)),
                'evidence': self.evidence}
        args.update(overrides)
        return fixture_preflight(self.request, self.request_hash(), **args)

    def test_consumed_predecessor_valid_absent_target_preserves_real_sqlite(self):
        proposal = self.run_fixture()
        result = proposal.record()
        self.assertEqual(result['status'], 'prepared_not_issued')
        self.assertTrue(all(v is False for v in result['authorizations'].values()))
        self.assertTrue(all(v == 'not-run' for v in result['live_gates'].values()))
        self.assertEqual(result['request'], self.request)
        self.assertNotEqual(result['proposed_target'], PREDECESSOR)
        self.assertEqual(self.before, self.snapshot())
        with sqlite3.connect('file:' + str(self.root / 'accounting') + '?mode=ro', uri=True) as db:
            self.assertEqual(db.execute('SELECT * FROM ledger').fetchall(), [('consumed', 1, None, 'retained')])
        self.assertEqual(self.before, self.snapshot())

    def test_canonical_immutable_hashes(self):
        proposal = prepare(self.request, self.request_hash())
        self.assertEqual(proposal.sha256, digest(proposal.canonical_bytes))
        validate_proposal(proposal, self.request, self.request_hash())
        detached = proposal.record()
        detached['request']['namespace'] = 'b' * 32
        self.assertEqual(proposal.record()['request'], self.request)
        with self.assertRaises(Failure):
            validate_proposal(Proposal(proposal.canonical_bytes, '0' * 64), self.request, self.request_hash())
        with self.assertRaises(Failure):
            prepare(self.request, '0' * 64)

    def test_pure_prepare_performs_no_filesystem_calls(self):
        with patch('os.open', side_effect=AssertionError('I/O')), \
             patch('builtins.open', side_effect=AssertionError('I/O')), \
             patch('os.stat', side_effect=AssertionError('I/O')), \
             patch('os.lstat', side_effect=AssertionError('I/O')):
            proposal = prepare(self.request, self.request_hash())
            self.assertEqual(proposal.record()['runtime_readiness'], 'not_asserted')

    def test_external_hash_and_evidence_reject_subclasses_before_io(self):
        changed = dict(self.evidence['source'], sha256=SpoofDigest('0' * 64))
        attacks = {
            'evidence mapping subclass': {'evidence': SubclassDict(copy.deepcopy(self.evidence))},
            'evidence entry subclass': {'evidence': {
                **copy.deepcopy(self.evidence), 'source': SubclassDict(changed)}},
            'evidence digest subclass': {'evidence': {**copy.deepcopy(self.evidence), 'source': changed}},
            'evidence list subclass': {'evidence': {
                **copy.deepcopy(self.evidence),
                'source': {'path': SubclassList([changed['path']]), 'sha256': changed['sha256']},
            }},
            'nonstring evidence key': {'evidence': {**copy.deepcopy(self.evidence), 1: changed}},
        }
        (self.root / 'source').write_bytes(b'changed real source fixture')
        for label, kwargs in attacks.items():
            with self.subTest(label=label):
                with patch('os.open', side_effect=AssertionError('I/O')), \
                     patch('builtins.open', side_effect=AssertionError('I/O')), \
                     patch('os.stat', side_effect=AssertionError('I/O')), \
                     patch('os.lstat', side_effect=AssertionError('I/O')):
                    with self.assertRaises(Failure) as caught:
                        self.run_fixture(**kwargs)
                self.assertEqual(caught.exception.record['code'], 'InvalidInput')
        self.assertEqual(self.before['accounting'], self.snapshot()['accounting'])

    def test_external_expected_hash_rejects_subclasses_before_io(self):
        for value in (SpoofDigest('0' * 64), SpoofDigest(self.request_hash())):
            with self.subTest(hash=str(value)), \
                 patch('os.open', side_effect=AssertionError('I/O')), \
                 patch('builtins.open', side_effect=AssertionError('I/O')), \
                 patch('os.stat', side_effect=AssertionError('I/O')), \
                 patch('os.lstat', side_effect=AssertionError('I/O')):
                with self.assertRaises(Failure) as caught:
                    prepare(self.request, value)
                self.assertEqual(caught.exception.record['code'], 'InvalidInput')

    def test_proposal_rejects_mutable_or_subclassed_bindings(self):
        proposal = prepare(self.request, self.request_hash())
        with self.assertRaises(Failure) as caught:
            Proposal(bytearray(proposal.canonical_bytes), proposal.sha256)
        self.assertEqual(caught.exception.record['code'], 'InvalidInput')
        with self.assertRaises(Failure) as caught:
            Proposal(proposal.canonical_bytes, SpoofDigest(proposal.sha256))
        self.assertEqual(caught.exception.record['code'], 'InvalidInput')

    def test_target_states_fail_closed(self):
        for state in ('consumed', 'reused', 'pending', 'stopped', 'unknown', None, True):
            with self.subTest(state=state):
                self.request['target_state'] = state
                with self.assertRaises(Failure):
                    self.run_fixture()
        self.assertEqual(self.before, self.snapshot())

    def test_reused_namespace(self):
        self.request['used_namespaces'].append('a' * 32)
        with self.assertRaises(Failure):
            self.run_fixture()

    def test_existing_target_and_dangling_target(self):
        target = self.root / ('replay-' + 'a' * 32)
        target.mkdir()
        with self.assertRaises(Failure):
            self.run_fixture()
        target.rmdir()
        target.symlink_to(self.root / 'absent')
        with self.assertRaises(Failure):
            self.run_fixture()
        target.unlink()
        self.assertEqual(self.before, self.snapshot())

    def test_stale_identity_manifest_and_missing_evidence(self):
        original = copy.deepcopy(self.request)
        for name in BINDINGS:
            for fault in ('identity', 'sha256', 'missing'):
                with self.subTest(name=name, fault=fault):
                    self.request = copy.deepcopy(original)
                    if fault == 'missing':
                        del self.request['bindings'][name]
                    else:
                        self.request['bindings'][name][fault] = '0' * 64
                    with self.assertRaises(Failure):
                        self.run_fixture()
        self.assertEqual(self.before, self.snapshot())

    def test_exact_schema_and_pinned_recovery(self):
        original = copy.deepcopy(self.request)
        for fault in ('extra', 'version', 'predecessor', 'recovery'):
            self.request = copy.deepcopy(original)
            if fault == 'extra':
                self.request['extra'] = False
            elif fault == 'version':
                self.request['version'] = True
            elif fault == 'predecessor':
                self.request['identities']['predecessor'] = '0' * 64
            else:
                entry = self.request['bindings']['accounting']
                entry['payload']['recovery_receipt'] = '0' * 64
                entry['sha256'] = digest(canonical(entry['payload']))
            with self.subTest(fault=fault), self.assertRaises(Failure):
                self.run_fixture()

    def test_every_path_lexical_before_any_metadata(self):
        attacks = ['/Library/GRRR', '//Library/GRRR/ledger', '/private/tmp/../Library/GRRR',
                   str(self.root) + '/../outside', str(self.root) + '//source',
                   str(self.root) + '/./source', '/private/tmp/other/source']
        for attack in attacks:
            for field in ('sandbox', 'target', 'evidence'):
                evidence = copy.deepcopy(self.evidence)
                evidence['accounting']['path'] = attack  # last entry must still validate first
                kwargs = {field: evidence if field == 'evidence' else attack}
                with self.subTest(attack=attack, field=field):
                    with patch('os.open', side_effect=AssertionError('metadata attempted')), \
                         patch('os.stat', side_effect=AssertionError('metadata attempted')), \
                         patch('os.lstat', side_effect=AssertionError('metadata attempted')):
                        with self.assertRaises(Failure):
                            self.run_fixture(**kwargs)

    def test_symlink_root_ancestor_final_and_dangling(self):
        link = self.root / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            self.run_fixture(sandbox=str(link), target=str(link / ('replay-' + 'a' * 32)),
                             evidence={n: dict(e, path=str(link / n)) for n, e in self.evidence.items()})
        for path in (link / 'source', self.root / 'dangling', self.root / 'final'):
            if path.name == 'dangling':
                path.symlink_to(self.root / 'missing')
            elif path.name == 'final':
                path.symlink_to(self.root / 'source')
            evidence = copy.deepcopy(self.evidence)
            evidence['source']['path'] = str(path)
            with self.assertRaises(OSError):
                self.run_fixture(evidence=evidence)
        ancestor_root = str(link / 'nested')
        with self.assertRaises(OSError):
            self.run_fixture(sandbox=ancestor_root, target=ancestor_root + '/replay-' + 'a' * 32,
                             evidence={n: dict(e, path=ancestor_root + '/' + n) for n, e in self.evidence.items()})

    def test_stale_real_bytes_and_unbound_fixture_hash(self):
        (self.root / 'source').write_bytes(b'changed')
        with self.assertRaises(Failure):
            self.run_fixture()
        self.evidence['source']['sha256'] = digest(b'changed')
        with self.assertRaises(Failure):
            self.run_fixture()
        self.assertEqual(self.before['accounting'], self.snapshot()['accounting'])

    def test_protected_symlink_destination_is_never_followed(self):
        link = self.root / 'protected-link'
        link.symlink_to('/Library/GRRR/no-probe')
        evidence = copy.deepcopy(self.evidence)
        evidence['source']['path'] = str(link)
        with self.assertRaises(OSError) as caught:
            self.run_fixture(evidence=evidence)
        self.assertEqual(caught.exception.errno, errno.ELOOP)
        link.unlink()
        self.assertEqual(self.before, self.snapshot())


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FreshRuntimeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(int(result.testsRun == 0 or bool(result.skipped) or not result.wasSuccessful()))
