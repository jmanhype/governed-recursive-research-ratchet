#!/bin/bash
set -u
PKG=/Library/GRRR/replay-package
RT=/Library/GRRR/independent-replay
IPC=$RT/d011-independent-v2-normal/ipc
MODE=normal
PY=/usr/bin/python3
cd /tmp || exit 9
sudo -u _grrr_runner /bin/rm -f "$IPC/executor.sock" "$IPC/executor-control.sock"
sudo -u _grrr_runner /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C \
  $PY -u -c "import sys; sys.path.insert(0,'$PKG'); import replay; raise SystemExit(replay.runner('$MODE'))" \
  > /tmp/grrr-runner.log 2>&1 &
for i in $(seq 1 150); do
  [ -S "$IPC/executor.sock" ] && break
  sleep 0.2
done
if [ ! -S "$IPC/executor.sock" ]; then
  echo "RUNNER_SOCKET_MISSING"
  tail -25 /tmp/grrr-runner.log
  sudo -u _grrr_runner /usr/bin/pkill -f "replay.runner" 2>/dev/null
  exit 8
fi
echo "RUNNER_READY"
sudo -u _grrr_evaluator /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C \
  $PY -u -c "import sys; sys.path.insert(0,'$PKG'); import replay; raise SystemExit(replay.evaluator('$MODE'))" \
  > /tmp/grrr-evaluator.log 2>&1
CODE=$?
sudo -u _grrr_runner /usr/bin/pkill -f "replay.runner" 2>/dev/null
sleep 0.5
echo "EVALUATOR_EXIT=$CODE"
echo "--- evaluator tail ---"; tail -15 /tmp/grrr-evaluator.log
echo "--- runner tail ---"; tail -10 /tmp/grrr-runner.log
