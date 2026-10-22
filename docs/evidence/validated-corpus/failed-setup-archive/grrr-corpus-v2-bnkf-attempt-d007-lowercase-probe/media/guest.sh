#!/bin/sh
# New corpus profile only. Root owns input and variant selection; candidate sees one scenario.
set -eu
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/work/home
export GOPATH=/work/gopath GOCACHE=/work/cache GOTMPDIR=/work/tmp
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local CGO_ENABLED=0 GOFLAGS=-mod=readonly
unset SSH_AUTH_SOCK SSH_AGENT_PID DISPLAY WAYLAND_DISPLAY
test "$(id -u)" = 0
test "$(ls /sys/class/net)" = lo
awk 'NF && !(NR == 1 && $1 == "Iface" && $2 == "Destination") {exit 1}' /proc/net/route
awk 'NF && $NF != "lo" {exit 1}' /proc/net/ipv6_route
test ! -e /dev/virtio-ports
! grep -E '9p|virtiofs|cifs|nfs|vboxsf|fuse' /proc/mounts
awk '$2 == "/inputs" && $3 == "iso9660" && $4 ~ /(^|,)ro(,|$)/ {found=1} END {exit !found}' /proc/mounts
for path in /Users /host /run/host /root/.ssh /root/.aws /work; do test ! -e "$path"; done
chmod 700 /root
mkdir /root/inputs
mount -o move /inputs /root/inputs
rmdir /inputs
chmod 600 /dev/console /dev/ttyAMA0 /dev/vd*
mkdir /work
mount -t tmpfs -o size=512m,nosuid,nodev tmpfs /work
mkdir -p /work/control /work/bin /work/home /work/gopath /work/cache /work/tmp /root/source /work/vault
chmod 700 /work/control; chmod 755 /work /work/bin; chmod 1777 /work/vault
mkdir -p /work/candidate/source /work/candidate/cache /work/candidate/gopath /work/candidate/tmp
chown -R 1000:1000 /work/candidate /work/home; chmod 700 /work/candidate
cd /root/inputs
sha256sum -c input.sum
tar -xzf go.tgz -C /work
chmod -R a-w /work/go; chmod 755 /work/go /work/go/bin /work/go/pkg/tool
tar -xf vlt.tar -C /root/source
mkdir /root/probes
tar -xf probes.tar -C /root/probes
chmod 700 /root/probes
chmod 600 /root/probes/*
cd /root/source && sha256sum -c /root/inputs/source.sum
cp /root/inputs/corpus-supervis /work/control/supervisor
cp /root/inputs/corpus-helper /work/bin/corpus-helper
chmod 700 /work/control/supervisor; chmod 755 /work/bin/corpus-helper
printf 'EVALUATOR-OWNED-TRUTH\n' > /work/control/expectation
chmod 600 /work/control/expectation
exec /work/control/supervisor
