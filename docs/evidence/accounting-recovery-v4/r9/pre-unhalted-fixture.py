"""Fixture-only refusal test for a store planned while already active."""

import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from accounting_recovery_v4 import apply_install
from accounting_recovery_planner_v4 import build
from unit_capstone_recovery_v4 import RESEARCH, create_store


class PreUnhaltedFixtureTests(unittest.TestCase):
    def test_install_refuses_a_fresh_pre_unhalted_store(self):
        owner = os.getuid()
        with tempfile.TemporaryDirectory(prefix='grrr-pre-unhalted-') as temporary:
            base = Path(temporary)
            database = create_store(base)

            # The pre-halted state is part of the approved baseline itself.
            db = sqlite3.connect(database)
            try:
                db.execute('UPDATE state SET stopped=0 WHERE id=1')
                db.commit()
            finally:
                db.close()

            records = build(base, RESEARCH, owner=owner, active_uid=owner)
            with self.assertRaisesRegex(
                    RuntimeError, 'store is not stopped; recovery refuses'):
                apply_install(base, records['plan'], records['review'],
                              records['authorization'], privileged=False,
                              owner=owner, active_uid=owner)

            completion = base / 'recovery-v4' / 'complete.json'
            self.assertFalse(os.path.lexists(completion),
                             'refused install must not leave a completion marker')


if __name__ == '__main__':
    unittest.main()
