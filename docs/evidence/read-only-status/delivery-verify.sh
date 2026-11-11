#!/bin/bash
set -euo pipefail
OUT=/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs
WT="$OUT/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-n49g"
cd "$WT"
E=docs/evidence/read-only-status
PROFILE='(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))'
shasum -a 256 research/status_view.py research/review_report.py scripts/grrr-review tests/unit_status_view.py tests/unit_review_report.py tests/unit_capstone_backend_suite.py docs/READ-ONLY-STATUS-VIEW.md > "$E/delivery-source.sha256"
shasum -a 256 -c "$E/authority-source.sha256" > "$E/delivery-authority-parity.log"
pvg verify research/status_view.py research/review_report.py scripts/grrr-review tests/unit_status_view.py tests/unit_review_report.py tests/unit_capstone_backend_suite.py --include-tests --format text > "$E/delivery-pvg-verify.log" 2>&1
cat "$E/delivery-pvg-verify.log"
for spec in '/opt/homebrew/bin/python3|314' '/opt/homebrew/bin/python3.12|312' '/usr/bin/python3|39'; do
  py=${spec%|*}
  label=${spec#*|}
  /usr/bin/sandbox-exec -p "$PROFILE" "$py" -B tests/unit_capstone_backend_suite.py > "$E/delivery-python$label.log" 2>&1
  tail -6 "$E/delivery-python$label.log"
done
/usr/bin/sandbox-exec -p "$PROFILE" /opt/homebrew/bin/python3 -B "$OUT/grrr-n49g-delivery-line-coverage.py" "$E/delivery-line-coverage.json" > "$E/delivery-line-coverage.log" 2>&1
tail -7 "$E/delivery-line-coverage.log"
shasum -a 256 -c "$E/delivery-source.sha256"
shasum -a 256 -c "$E/authority-source.sha256"
git diff --check
