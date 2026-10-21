"""Separate real process probes an already-held launcher lock; no VM capability."""
import fcntl
import os
import sys

descriptor = os.open(sys.argv[1], os.O_RDONLY | os.O_NOFOLLOW)
try:
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('blocked')
        raise SystemExit(0)
    print('unexpectedly-acquired')
    raise SystemExit(2)
finally:
    os.close(descriptor)
