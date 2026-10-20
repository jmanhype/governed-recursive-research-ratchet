#!/bin/sh
# Evaluator-authored fixed bootstrap; source and toolchain are read-only media.
set -eu
export PATH=/inputs/go/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/work/home GOPATH=/work/gopath GOCACHE=/work/cache GOTMPDIR=/work/tmp
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local CGO_ENABLED=0 GOFLAGS=-mod=readonly
export GOMAXPROCS=1 GOGC=30 GOMEMLIMIT=128MiB
unset SSH_AUTH_SOCK SSH_AGENT_PID DISPLAY WAYLAND_DISPLAY
printf 'GRRR-ISOLATION-BEGIN\n'
cat /proc/net/route /proc/net/ipv6_route /proc/mounts /proc/partitions
ls -l /sys/class/net /sys/class/block /dev/virtio-ports 2>/dev/null || true
test "$(ls /sys/class/net)" = lo
test "$(wc -l < /proc/net/route)" -eq 1
test ! -e /dev/virtio-ports
test "$(cat /sys/class/block/vda/ro)" = 1
! grep -E '9p|virtiofs|cifs|nfs|vboxsf|fuse' /proc/mounts
for path in /Users /home/speed /root/.ssh /root/.aws /run/host /host /protected /production /evaluator; do
    test ! -e "$path"
done
test ! -e /tmp/grrr-reset
touch /tmp/grrr-reset
! touch /inputs/unauthorized-write 2>/dev/null
printf 'GRRR-ISOLATION-PASS\n'
mkdir /work
mount -t tmpfs -o size=350m tmpfs /work
mkdir -p /work/home /work/gopath /work/cache /work/tmp /work/source /work/vault
cp -R /inputs/source/. /work/source/
cd /work/source
sha256sum -c /inputs/source.sha256
printf 'GRRR-DEPENDENCIES-BEGIN\n'
go version
go list -deps -f '{{.ImportPath}} standard={{.Standard}} {{with .Module}}{{.Path}} {{.Version}}{{end}}' ./...
printf 'GRRR-DEPENDENCIES-END\n'
go build -p=1 -trimpath -buildvcs=false -ldflags=-buildid= -o /work/vlt ./cmd/vlt
printf 'GRRR-BUILD-SHA256 '
sha256sum /work/vlt
set +e
go test -json -count=1 -p=1 ./... > /work/tests.json
test_result=$?
set -e
cat /work/tests.json
test "$test_result" -eq 0
! grep -q '"Action":"skip"' /work/tests.json
printf 'GRRR-TESTS-PASS\n'
/work/vlt vault=/work/vault create name=Synthetic path=Synthetic.md content=GRRR-SYNTHETIC silent
/work/vlt vault=/work/vault read file=Synthetic > /work/synthetic.txt
grep -q GRRR-SYNTHETIC /work/synthetic.txt
printf 'GRRR-SYNTHETIC-IO-PASS\n'
sha256sum -c /inputs/source.sha256
test ! -e /inputs/unauthorized-write
printf 'GRRR-BASELINE-PASS\n'
