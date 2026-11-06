"""Required public source regressions. WIP backend, no skipped/zero-test green."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'research'), str(ROOT / 'tests')]
MODULES = ('unit_capstone_contract', 'unit_capstone_peer', 'unit_capstone_journal',
           'unit_durable_evidence', 'unit_capstone_backend_contract',
           'unit_capstone_backend_launch', 'unit_capstone_backend_review',
           'unit_capstone_backend_composition', 'unit_capstone_backend_index',
           'unit_capstone_installation_record', 'unit_capstone_installation',
           'unit_capstone_installation_authority',
           'unit_capstone_installation_inventory',
           'unit_capstone_accounting_v5',
           'unit_capstone_campaign_reducer',
           'unit_capstone_campaign_append',
           'unit_capstone_driver')


def main():
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    for name in MODULES:
        part = loader.loadTestsFromName(name)
        if part.countTestCases() == 0:
            print('REQUIRED MODULE HAS ZERO TESTS: ' + name, file=sys.stderr)
            return 1
        suite.addTests(part)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print('SOURCE_ONLY BACKEND_WIP tests=%d failures=%d errors=%d skipped=%d; '
          'installed topology, live campaign execution and capstone NOT-QUALIFIED' %
          (result.testsRun, len(result.failures), len(result.errors), len(result.skipped)))
    return int(result.testsRun == 0 or bool(result.skipped) or not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
