"""Bounded regular-file I/O for owner-selected local paths on POSIX."""
import os
import secrets
import stat
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def parent_directory(path):
    """Pin a directory descriptor and reject symlinks in every path component."""
    path = Path(path)
    parts = path.parts
    if not parts or path.name in ("", ".", "..") or ".." in parts:
        raise ValueError("invalid_local_path")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open("/" if path.is_absolute() else ".", flags)
    try:
        for part in parts[:-1]:
            if part in ("/", "."):
                continue
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd, path.name
    finally:
        os.close(fd)


def read_regular(path, limit):
    with parent_directory(path) as (directory, name):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("regular_file_required")
            source = os.fdopen(fd, "rb")
        except BaseException:
            os.close(fd)
            raise
        with source:
            return source.read(limit + 1)


def write_private(path, raw):
    """Publish a complete 0600 file atomically, preserving any existing target."""
    with parent_directory(path) as (directory, name):
        temporary = ".mindtunnel-" + secrets.token_hex(16)
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(raw)
                output.flush()
                os.fsync(output.fileno())
            os.link(temporary, name, src_dir_fd=directory, dst_dir_fd=directory,
                    follow_symlinks=False)
        finally:
            os.unlink(temporary, dir_fd=directory)
