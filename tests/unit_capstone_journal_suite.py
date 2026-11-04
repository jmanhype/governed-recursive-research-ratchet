"""Source-only journal suite; no skipped-green or zero-test success."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'tests'))


def failed(result: unittest.TestResult) -> bool:
    return result.testsRun == 0 or bool(result.skipped) or not result.wasSuccessful()


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromName('unit_capstone_journal')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print('SOURCE_ONLY JOURNAL tests=%d failures=%d errors=%d skipped=%d; full capstone NOT-RUN' %
          (result.testsRun, len(result.failures), len(result.errors), len(result.skipped)))
    return int(failed(result))


if __name__ == '__main__':
    raise SystemExit(main())
