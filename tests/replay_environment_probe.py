"""Unprivileged child reporting only environment variable names and safe allowlist."""
import json
import os
import sys


def main() -> None:
    flags = bool(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode)
    if not flags or os.getuid() == 0:
        raise SystemExit('Unprivileged isolated probe required')
    names = sorted(os.environ)
    safe_values = {key: os.environ.get(key) for key in ('PATH', 'LC_ALL')}
    record = {'names': names, 'allowlist': safe_values, 'python': sys.executable,
              'uid': os.getuid(), 'isolated_flags': flags,
              'generated_cf_encoding': os.environ.get('__CF_USER_TEXT_ENCODING')}
    print(json.dumps(record, sort_keys=True))


if __name__ == '__main__':
    main()
