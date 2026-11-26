"""Observe only the synthetic test network created by capture.sh."""
import socket
import subprocess
import sys

if socket.if_nameindex() != [(1, "lo")]:
    raise SystemExit("synthetic loopback-only namespace required")

with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3)) as monitor:
    monitor.bind(("lo", 0))
    monitor.settimeout(1)
    # Prove capture works before measuring the isolated workflow.
    marker = b"mindtunnel-loopback-capture-control"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(("127.0.0.1", 0))
        server.sendto(marker, server.getsockname())
        if server.recv(100) != marker or marker not in monitor.recv(65535):
            raise SystemExit("capture control failed")
    monitor.setblocking(False)
    while True:
        try:
            monitor.recv(65535)
        except BlockingIOError:
            break
    subprocess.run([sys.executable, "/project/harness/verify_isolation.py"], check=True)
    try:
        monitor.recv(65535)
    except BlockingIOError:
        print("Loopback capture control observed. 0 packets captured during isolated workflow.")
    else:
        raise SystemExit("unexpected synthetic network traffic")
