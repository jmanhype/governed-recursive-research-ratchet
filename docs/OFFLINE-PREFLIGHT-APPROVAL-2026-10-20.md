# Operator approval: offline build preflight, 2026-10-20

Recorded from the operator's explicit authorization in GRRR-90te nd notes and
dispatcher handoff. This supersedes the previous absence of build-profile approval,
not any license, isolation, identity, evidence, budget, or admission gate.

- Two independent fresh disposable VM invocations.
- vlt commit `129e0b3f15a3bd6af949ee47d76f6855c582ab73`.
- Go 1.26.10 linux-arm64 archive SHA-256
  `3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`.
- Each invocation: 512 MiB RAM, one vCPU, 300-second total hard ceiling.
- Cumulative build/test runtime before other probes/replays: maximum 600 seconds.
- Initial command timeout: 240 seconds, explicitly **unmeasured**. Record measured
  results without increasing the 300-second hard ceiling.
- No guest networking, host shares, clipboard, or forwarded agents.
- Evaluator-controlled read-only detached asset input only.
- No host build fallback, paid service, production access, automatic main merge,
  or promotion.
- Retain 30-second boot deadline, two-second stop acknowledgement target,
  five-second TERM grace and mandatory force kill, 1-MiB output cap, and 15-GB
  minimum host free space.
- Fail closed on unexplained build differences, missing dependencies, license
  ambiguity, isolation failure, non-clean baseline, or resource exhaustion.
  Exhaustion at 512 MiB is a measured blocker, not permission to increase RAM.

GPL/AGPL/BSL/noncommercial/source-available/unclear components still require
separate review. This is not a blanket license-clearance or redistribution grant.

## Emergency stop

The offline evaluator owns the kernel-authenticated control socket. Its stop action
fences the run and sends TERM immediately, acknowledging before the bounded drain.
The executor enforces five-second TERM grace followed by KILL. If the control
plane is unresponsive, the operator/root must identify the exact QEMU PID from
the preserved runtime receipt, verify its command/input-image binding, send TERM,
wait at most five seconds, then KILL that exact PID if still alive. Never use
`killall`, broad process-name matching, or an unverified stale PID. Preserve the
runtime/evidence and do not restart or reuse the candidate after forced stop.
