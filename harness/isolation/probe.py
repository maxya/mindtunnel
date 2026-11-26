import os
from pathlib import Path
import socket
import errno
assert not Path("/home").exists()
assert not Path("/input").exists()
assert not Path("/proc").exists()
assert 'MINDTUNNEL_TEST_CANARY' not in os.environ
for family in (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX):
    try:
        sock = socket.socket(family)
    except OSError as error:
        assert error.errno == errno.EPERM
    else:
        sock.close()
        raise AssertionError
print("isolated synthetic probe passed")
