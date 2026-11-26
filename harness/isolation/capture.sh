#!/usr/bin/env bash
# Use only the synthetic project components and a fresh loopback-only namespace.
set -eu
cd "$(dirname "$0")/../.."
root=$(pwd -P)
args=(--unshare-all --unshare-user --uid 0 --gid 0 --cap-add CAP_NET_RAW --cap-add CAP_SETFCAP --die-with-parent --new-session
      --clearenv --setenv PATH /usr/bin --ro-bind /usr/bin/python3 /usr/bin/python3
      --ro-bind /usr/bin/bwrap /usr/bin/bwrap --proc /proc --dev /dev --tmpfs /tmp)
for dir in /lib /lib64 /usr/lib /usr/lib64; do
    if [[ -d $dir ]]; then args+=(--ro-bind "$dir" "$dir"); fi
done
for dir in mindtunnel mindtunnel_isolation mindtunnel_planner; do
    for module in "$dir"/*.py; do args+=(--ro-bind "$root/$module" "/project/$module"); done
done
for file in examples/{contract,plan,mapping,expected}.json examples/transactions.csv \
            harness/verify_isolation.py harness/isolation/{capture,probe}.py; do
    args+=(--ro-bind "$root/$file" "/project/$file")
done
exec /usr/bin/bwrap "${args[@]}" /usr/bin/python3 -I -B /project/harness/isolation/capture.py
