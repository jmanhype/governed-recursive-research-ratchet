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
    if sys.argv[1:] == ['--leaf']:
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
