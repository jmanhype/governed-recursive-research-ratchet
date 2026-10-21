"""Provisioning schema/identity refusal; no root operations or QEMU."""
import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('provision_review', str(ROOT / 'scripts/provision-trusted-host'))
spec = importlib.util.spec_from_loader(loader.name, loader)
provision = importlib.util.module_from_spec(spec)
loader.exec_module(provision)


class Provisioning(unittest.TestCase):
    def plan(self):
        return {'version': 1, 'decision': 'approved-provisioning-only',
                'installer_sha256': 'a'*64, 'python_sha256': 'b'*64,
                'host_code': provision.sha(provision.canonical({'research/common.py': 'c'*64})),
                'source_files': {'research/common.py': 'c'*64},
                'files': [{'source': '/untrusted/input', 'destination': 'snapshots/provisioned/research/common.py',
                           'sha256': 'c'*64, 'size': 1}],
                'qemu_manifest': 'qemu/installation.json',
                'migration': {'database_source': '/prior/db', 'receipt_source': '/prior/receipt',
                              'receipt_sha256': 'd'*64},
                'campaign': 'e'*64, 'store_id': 'f'*64, 'database_sha256': 'a'*64}

    def test_schema_only_is_not_authority(self):
        self.assertEqual(provision.validate_plan(self.plan())['decision'], 'approved-provisioning-only')

    def test_qemu_only_plan_cannot_carry_accounting(self):
        plan = self.plan()
        plan['decision'] = 'approved-qemu-provisioning-only'
        with self.assertRaises(RuntimeError):
            provision.validate_plan(plan)
        for field in ('migration', 'campaign', 'store_id', 'database_sha256'):
            del plan[field]
        self.assertEqual(provision.validate_plan(plan)['decision'], 'approved-qemu-provisioning-only')

    def test_traversal_missing_source_duplicate_and_unknown_rejected(self):
        for mutation in ('traversal', 'missing', 'duplicate', 'unknown', 'self'):
            plan = self.plan()
            if mutation == 'traversal':
                plan['files'][0]['destination'] = 'snapshots/../escape'
            elif mutation == 'missing':
                plan['source_files']['research/extra.py'] = 'c'*64
            elif mutation == 'duplicate':
                plan['files'].append(dict(plan['files'][0]))
            elif mutation == 'unknown':
                plan['paid_dispatch'] = True
            else:
                plan['files'][0]['destination'] = 'bootstrap/provision-trusted-host'
            with self.subTest(mutation=mutation), self.assertRaises(RuntimeError):
                provision.validate_plan(plan)

    def test_nonroot_installer_refuses_before_effects(self):
        result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                 str(ROOT / 'scripts/provision-trusted-host')],
                                capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('root isolated independently installed provisioner required', result.stderr)
