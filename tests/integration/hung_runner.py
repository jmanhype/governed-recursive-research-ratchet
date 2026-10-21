#!/usr/bin/env python3
"""Deliberately TERM-resistant research-run fixture under UID 321."""
from pathlib import Path
import signal
import sys
import time


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: hung_runner.py RUN READY_PATH')
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    ready = Path(sys.argv[2])
    ready.write_text(sys.argv[1] + '\n', encoding='ascii')
    while True:
        time.sleep(1)
