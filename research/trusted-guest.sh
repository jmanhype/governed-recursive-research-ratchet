#!/bin/sh
# New profile only. Root-owned detached input; execution requires separate approval.
set -eu
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/work/home
export GOPATH=/work/gopath GOCACHE=/work/cache GOTMPDIR=/work/tmp
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local CGO_ENABLED=0 GOFLAGS=-mod=readonly
export GOMAXPROCS=1 GOGC=30 GOMEMLIMIT=128MiB
unset SSH_AUTH_SOCK SSH_AGENT_PID DISPLAY WAYLAND_DISPLAY
test "$(id -u)" = 0
test "$(ls /sys/class/net)" = lo
awk 'NF && !(NR == 1 && $1 == "Iface" && $2 == "Destination") {exit 1}' /proc/net/route
awk 'NF && $NF != "lo" {exit 1}' /proc/net/ipv6_route
test ! -e /dev/virtio-ports
! grep -E '9p|virtiofs|cifs|nfs|vboxsf|fuse' /proc/mounts
awk '$2 == "/inputs" && $3 == "iso9660" && $4 ~ /(^|,)ro(,|$)/ {found=1} END {exit !found}' /proc/mounts
for path in /Users /host /run/host /root/.ssh /root/.aws /work; do
    test ! -e "$path"
done
# Deny access to the original supervisor/source/image, not just its copied path.
chmod 700 /root
mkdir /root/inputs
mount -o move /inputs /root/inputs
rmdir /inputs
chmod 600 /dev/console /dev/ttyAMA0 /dev/vd*
mkdir /work
mount -t tmpfs -o size=512m,nosuid,nodev tmpfs /work
mkdir -p /work/control /work/bin /work/home /work/gopath /work/cache /work/tmp /work/source /work/candidate /work/vault
chmod 700 /work/control /work/source
chmod 755 /work /work/bin
chown 1000:1000 /work/candidate
chmod 700 /work/candidate
# Sticky root-owned vault prevents candidate replacement of the root lock inode.
chmod 1777 /work/vault
cd /root/inputs
sha256sum -c input.sum
tar -xzf go.tgz -C /work
chmod 700 /work/go
export GOROOT=/work/go PATH=/work/go/bin:/usr/sbin:/usr/bin:/sbin:/bin
tar -xf vlt.tar -C /work/source
cd /work/source
sha256sum -c /root/inputs/source.sum
go build -p=1 -trimpath -buildvcs=false -ldflags=-buildid= -o /work/bin/vlt ./cmd/vlt
cp /root/inputs/supervis /work/control/supervisor
cp /root/inputs/helper /work/bin/candidate-helper
chmod 700 /work/control/supervisor
chmod 755 /work/bin/vlt /work/bin/candidate-helper
printf 'SUPERVISOR-OWNED-CONTENT\n' > /work/control/expectation
chmod 600 /work/control/expectation
# Supervisor reads a bounded versioned metadata request from stdin. Candidate
# receives /dev/null instead and never inherits this trusted control transport.
exec /work/control/supervisor
