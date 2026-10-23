"""Verify parent-supplied copies only; never open protected originals or execute code."""
import base64
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    databases = [ROOT / 'evaluator' / name for name in ('smoke-budget.sqlite', 'ledger.sqlite')]
    before = {path: sha(path.read_bytes()) for path in databases}
    connections = [sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True) for path in databases]
    try:
        budget, ledger = connections
        for db in connections:
            assert db.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
        assert budget.execute('SELECT * FROM state').fetchall() == [(1, 0)]
        reservations = budget.execute('SELECT id,run,maximum,actual,receipt FROM reservations').fetchall()
        assert len(reservations) == 1
        rid, run, maximum, actual, receipt = reservations[0]
        usage = json.loads(actual)
        assert usage == {'currency': 'USD', 'execution_us': 22823014, 'money_cents': 0, 'review_us': 0}
        assert json.loads(maximum)['execution_us'] == 480000000
        meters = budget.execute('SELECT id,reservation,body FROM metering').fetchall()
        assert len(meters) == 1 and meters[0][:2] == (receipt, rid)
        meter = json.loads(meters[0][2])
        assert meter['usage'] == usage
        objraw = (ROOT / 'evaluator/objects-444262c5').read_bytes()
        objhash = sha(objraw)
        assert objhash == meter['evidence'] == '444262c5a0457cd27c6b6ef29be3c474426707d62e2eeda458c74376c9e07a16'
        obj = json.loads(objraw)
        assert obj['run'] == run and obj['reservation'] == rid
        assert obj['ceased'] and obj['transport_complete'] and not obj['forced']
        assert obj['exit_code'] == 0 and obj['error'] is None
        raw = base64.b64decode(obj['raw_base64'], validate=True)
        assert len(raw) == obj['raw_bytes'] == 27673
        assert sha(raw) == obj['raw_sha256'] == 'adf82b14c9ac434e3883751e2648690b88e0324d1b55459631a4fe3fb4725bbd'
        guest = obj['guest']
        assert guest['supervisor_unchanged'] and guest['supervisor_sha256'] == obj['supervisor']
        creds = guest['candidate_credentials']
        assert creds['Uid'] == creds['Gid'] == '1000 1000 1000 1000'
        assert creds['Groups'] == '' and creds['NoNewPrivs'] == '1'
        assert all(creds[k] == '0' * 16 for k in ('CapAmb', 'CapBnd', 'CapEff', 'CapInh', 'CapPrm'))
        repetitions = guest['candidate_observation']['repetitions']
        assert len(repetitions) == 3 and all(r['exit'] == 0 for r in repetitions)
        assert len({r['output_sha256'] for r in repetitions}) == 1
        prior, kinds = '0' * 64, []
        for sequence, previous, hashed, body in ledger.execute('SELECT * FROM events ORDER BY seq'):
            assert previous == prior and sha(prior.encode() + body) == hashed
            event = json.loads(body)
            assert event['scope'] == 'C001-runtime-lifecycle-only'
            assert event['independent_replay_authorized'] is False
            assert event['contract_admission_authorized'] is False
            assert all(value == objhash for value in event.get('objects', []))
            kinds.append(event['kind'])
            prior = hashed
        assert kinds == ['runtime-smoke-reserved', 'runtime-smoke-transport', 'runtime-smoke-settled']
        lifecycle = json.loads((ROOT / 'private/lifecycle.json').read_bytes())
        assert lifecycle['children_ceased'] and lifecycle['evaluator_succeeded']
        assert lifecycle['exit_codes'] == [-15, 0] and lifecycle['elapsed_seconds'] == 24.019100959
        assert lifecycle['independent_replay_authorized'] is False
        assert lifecycle['contract_admission_authorized'] is False
        assert json.loads((ROOT / 'plan.json').read_bytes())['run'] == run
        recovery = json.loads((ROOT / 'failed-attempt/recovery.json').read_bytes())
        assert recovery['inventory_unchanged'] and recovery['base_namespace_inventory_verified']
        assert recovery['retry_authorized'] is False
    finally:
        for db in connections:
            db.close()
    assert all(sha(path.read_bytes()) == hashed for path, hashed in before.items())
    print('PASS: read-only SQLite integrity; settled budget; three-event hash chain; object/raw hashes;')
    print('guest identity/repetitions; lifecycle/run/recovery binding; DB bytes unchanged.')


if __name__ == '__main__':
    main()
