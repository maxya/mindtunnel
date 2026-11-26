# Linux process isolation

Run the isolated executor using the same five paths as the ordinary run command.

```sh
mkdir -m 700 work
python3 -m mindtunnel_isolation.linux --contract examples/contract.json \
  --plan examples/plan.json --mapping examples/mapping.json \
  --data examples/transactions.csv --out work/isolated-result.json
```

Use physical paths and an owner-controlled output directory. The optional launcher requires Linux, a trusted /usr/bin/python3 (3.11+), /usr/bin/bwrap with user namespaces and libseccomp.so.2. Missing capabilities cause rejection. The ordinary CLI and manual transfer workflow work without these optional tools. They run with the owner's normal process privileges.

The trusted host launcher snapshots the four bounded inputs after checking the public plan and pins them as read-only files in the private worker. It receives the result via an anonymous local temporary file and publishes exclusively at the selected path. Choose local owner-controlled temporary storage. The separate mock worker receives only its approved public envelope on stdin. Both workers get a new mount, network and PID namespace, read-only system library directories and selected Python files, a cleared environment, no host home or /proc mount, and no inherited application descriptors. Bubblewrap drops capabilities and prevents nested user namespaces. A native seccomp filter rejects socket creation, socket pairs and io_uring setup. The trusted startup restricts CPU (10 seconds), address space (256 MiB), output size and core dumps. The parent imposes a 20-second timeout. The module selects the worker, never the plan.

Run these synthetic checks from the repository on a compatible Linux host.

```sh
python3 harness/verify_isolation.py
bash harness/isolation/capture.sh
```

The second command measures the *outer synthetic namespace's* loopback traffic during a nested isolated workflow. A control datagram checks that capture is working. Only the test supervisor receives namespace-local capture and nested UID mapping capabilities. This observation covers the recorded run and interface. Both workers use further private network namespaces. Socket-denial probes use the same launcher profile. This check requires a host that permits nested user namespaces.

Assume trusted system libraries, workers, launcher, host OS and local operator. Keep private data out of system runtime directories. Local backups, crash leftovers, malicious installed code and terminal capture are outside the guarantee. Read-only mounts do not encrypt local storage. The launcher has access to the selected inputs and output. macOS has no isolated adapter in this implementation. No actual provider is configured and no provider retention terms have been evaluated.
