#!/bin/bash
set -euo pipefail
DST=/Library/GRRR/bootstrap/recovery-v4
REVIEW=/private/tmp/grrr-review-r9.md
DRIVER=/private/tmp/grrr-install-verify-r9.py
EXPECTED_REVIEW=${1:?review SHA256 required}
[[ "$EXPECTED_REVIEW" =~ ^[0-9a-f]{64}$ ]]
test "$(/usr/bin/shasum -a 256 "$DRIVER" | /usr/bin/awk '{print $1}')" = fc5326471b92447cbc4eb70a0230ad9f6478cf74b55de3833a137e982a76dec1
test "$(/usr/bin/shasum -a 256 "$REVIEW" | /usr/bin/awk '{print $1}')" = "$EXPECTED_REVIEW"
test "$(/usr/bin/head -1 "$REVIEW")" = 'REVIEW_RESULT: APPROVED'
/usr/bin/install -o root -g wheel -m 444 "$DRIVER" "$DST/operator-r9.py"
/usr/bin/install -o root -g wheel -m 444 "$REVIEW" "$DST/review-verdict-r9.md"
test "$(/usr/bin/shasum -a 256 "$DST/operator-r9.py" | /usr/bin/awk '{print $1}')" = fc5326471b92447cbc4eb70a0230ad9f6478cf74b55de3833a137e982a76dec1
test "$(/usr/bin/shasum -a 256 "$DST/review-verdict-r9.md" | /usr/bin/awk '{print $1}')" = "$EXPECTED_REVIEW"
if /usr/bin/python3 -I -S "$DST/operator-r9.py" --verify > /private/tmp/grrr-r9-wrong-flags.log 2>&1; then
    echo 'ERROR: wrong flags were accepted' >&2
    exit 1
fi
/usr/bin/grep -F 'AssertionError: isolated flags required' /private/tmp/grrr-r9-wrong-flags.log
echo 'WRONG_FLAGS_REFUSED_BEFORE_PROTECTED_ACCESS'
if /opt/homebrew/bin/python3.14 -I -S -B "$DST/operator-r9.py" --verify > /private/tmp/grrr-r9-wrong-interpreter.log 2>&1; then
    echo 'ERROR: wrong interpreter was accepted' >&2
    exit 1
fi
/usr/bin/grep -F 'AssertionError: reviewed system Python 3.9 required' /private/tmp/grrr-r9-wrong-interpreter.log
echo 'WRONG_INTERPRETER_REFUSED_BEFORE_PROTECTED_ACCESS'
/usr/bin/python3 -I -S -B "$DST/operator-r9.py" --install
echo 'FRESH_PROCESS_VERIFY'
/usr/bin/python3 -I -S -B "$DST/operator-r9.py" --verify
