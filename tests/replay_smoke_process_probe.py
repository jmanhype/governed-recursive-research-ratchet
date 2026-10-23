"""Harmless real process-group fixture. Never imports or starts a VM executor."""
import os
from pathlib import Path
import subprocess
import signal
import sys
import time


def main() -> None:
    if os.getuid() == 0:
        raise SystemExit('Non-root test fixture only')
    if sys.argv[1:] == ['--early-stop']:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
        from replay_smoke import DeferredStop, cease_groups, present_groups
        from common import Failure
        stop = DeferredStop()
        signal.signal(signal.SIGTERM, stop.handler)
        processes = []
        parent = os.getpid()
        def early_stop():
            os.kill(parent, signal.SIGTERM)
            time.sleep(0.1)  # Parent is still waiting for Popen's exec-error pipe.
        try:
            stop.spawn(processes, [sys.executable, '-I', '-S', '-B', str(Path(__file__)), '--leaf'],
                       start_new_session=True, preexec_fn=early_stop)
            raise AssertionError('Early stop was not observed')
        except Failure:
            assert stop.requested and len(processes) == 1
        finally:
            assert cease_groups(processes, time.monotonic() + 7)
        assert not present_groups({p.pid for p in processes}, time.monotonic() + 1)
        print('registered-before-stop; no-orphan', flush=True)
    elif sys.argv[1:] == ['--leaf']:
        time.sleep(30)
    elif sys.argv[1:] in (['--spawn'], ['--ignore-term']):
        if sys.argv[1:] == ['--ignore-term']:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
        child = subprocess.Popen([sys.executable, '-I', '-S', '-B', str(Path(__file__)), '--leaf'])
        print(child.pid, flush=True)
        child.wait(timeout=35)
    else:
        raise SystemExit('Unregistered fixture action')


if __name__ == '__main__':
    main()
