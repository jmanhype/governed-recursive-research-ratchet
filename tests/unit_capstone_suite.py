"""Required no-guest source suite: zero tests/skips/errors are failure."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'tests'))


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromNames(['unit_capstone_contract', 'unit_capstone_peer'])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print('SOURCE_ONLY tests=%d failures=%d errors=%d skipped=%d; full capstone NOT-RUN' %
          (result.testsRun, len(result.failures), len(result.errors), len(result.skipped)))
    return int(result.testsRun == 0 or bool(result.skipped) or not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
