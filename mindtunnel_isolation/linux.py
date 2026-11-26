"""Launch only the bundled workers, using a fresh Linux network and mount namespace."""
import ctypes
import errno
import os
from contextlib import ExitStack, contextmanager
from pathlib import Path
import subprocess
import sys
import tempfile

from mindtunnel.core import MAX_FILE, MAX_JSON, parse, validate
from mindtunnel.files import read_regular, write_private

ROOT = Path(__file__).resolve().parents[1]
MOCK_LIMIT = 256 * 1024
RESULT_LIMIT = 16 * 1024 * 1024
RUNTIME = Path("/usr/bin/python3")
BWRAP = Path("/usr/bin/bwrap")


@contextmanager
def _memfile(raw=b""):
    with os.fdopen(os.memfd_create("mindtunnel", os.MFD_CLOEXEC), "w+b") as stream:
        stream.write(raw)
        stream.seek(0)
        yield stream


def _socket_filter(stream):
    """Export a native libseccomp filter. bwrap installs it before starting Python."""
    lib = ctypes.CDLL("libseccomp.so.2")
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]
    ctx = lib.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW
    if not ctx:
        raise ValueError("isolation_unavailable")
    try:
        for name in (b"socket", b"socketpair", b"io_uring_setup"):
            number = lib.seccomp_syscall_resolve_name(name)
            if number == -1 or lib.seccomp_rule_add(ctx, 0x00050000 | errno.EPERM, number, 0):
                raise ValueError("isolation_unavailable")
        if lib.seccomp_export_bpf(ctx, stream.fileno()):
            raise ValueError("isolation_unavailable")
        stream.seek(0)
    finally:
        lib.seccomp_release(ctx)


def _worker(entry, modules, inputs, stdin, limit):
    if sys.platform != "linux":
        raise ValueError("isolation_unavailable")
    try:
        with ExitStack() as stack:
            filt = stack.enter_context(_memfile())
            _socket_filter(filt)
            fds = [filt.fileno()]
            args = [str(BWRAP), "--unshare-all", "--unshare-user", "--disable-userns", "--new-session",
                    "--die-with-parent", "--cap-drop", "ALL", "--clearenv",
                    "--ro-bind", str(RUNTIME.resolve(strict=True)), "/usr/bin/python3"]
            for directory in ("/lib", "/lib64", "/usr/lib", "/usr/lib64"):
                if Path(directory).is_dir():
                    args.extend(["--ro-bind", directory, directory])
            args.extend(["--ro-bind", str(ROOT / "mindtunnel_isolation/runtime.py"), "/app/runtime.py"])
            for source, target in modules:
                args.extend(["--ro-bind", str(ROOT / source), target])
            for name, raw in inputs.items():
                stream = stack.enter_context(_memfile(raw))
                fds.append(stream.fileno())
                args.extend(["--ro-bind-data", str(stream.fileno()), "/input/" + name])
            args.extend(["--remount-ro", "/", "--seccomp", str(filt.fileno()),
                         "/usr/bin/python3", "-I", "-S", "-B", "/app/runtime.py", entry, str(limit)])
            output = stack.enter_context(tempfile.TemporaryFile())
            result = subprocess.run(args, input=stdin, stdout=output, stderr=subprocess.DEVNULL,
                                    env={}, pass_fds=fds, timeout=20, check=False)
            if result.returncode or output.tell() > limit:
                raise ValueError("isolated_worker_failed")
            output.seek(0)
            return output.read(limit + 1)
    except (OSError, AttributeError, subprocess.SubprocessError):
        raise ValueError("isolation_unavailable") from None


def run_mock(envelope):
    if type(envelope) is not bytes or len(envelope) > MOCK_LIMIT:
        raise ValueError("invalid_envelope")
    return _worker("/app/worker.py", [("mindtunnel_planner/worker.py", "/app/worker.py")],
                   {}, envelope, MOCK_LIMIT)


def run_private(contract, plan, mapping, data, out):
    def snapshot(path, limit):
        raw = read_regular(path, limit)
        if len(raw) > limit:
            raise ValueError("input_limit")
        return raw

    inputs = {"contract": snapshot(contract, MAX_JSON), "plan": snapshot(plan, MAX_JSON)}
    validate(parse(inputs["contract"]), parse(inputs["plan"]))
    inputs.update(mapping=snapshot(mapping, MAX_JSON), data=snapshot(data, MAX_FILE))
    files = ["mindtunnel/__init__.py", "mindtunnel/core.py", "mindtunnel/files.py",
             "mindtunnel_isolation/executor.py"]
    raw = _worker("/app/mindtunnel_isolation/executor.py", [(p, "/app/" + p) for p in files],
                  inputs, b"", RESULT_LIMIT)
    write_private(out, raw)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Run a private aggregate in a Linux sandbox")
    for name in ("contract", "plan", "mapping", "data", "out"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    try:
        run_private(**vars(args))
    except (OSError, ValueError):
        print("Rejected: isolated_execution_failed", file=sys.stderr)
        return 2
    print("Local result written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
