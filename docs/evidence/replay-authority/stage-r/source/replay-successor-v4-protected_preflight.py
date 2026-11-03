"""Lexical-first containment validation for sandbox source paths."""

import os
from pathlib import Path
import stat


LIBRARY_ROOT = Path("/Library")
PROTECTED_ROOT = Path("/Library/GRRR")


def safe_sandbox_path(path: Path, sandbox_root: Path, *,
                      exists: bool, directory: bool) -> None:
    if not isinstance(path, Path) or not isinstance(sandbox_root, Path):
        raise ValueError("sandbox values must be paths")
    raw_path = str(path)
    raw_root = str(sandbox_root)
    if not path.is_absolute() or not sandbox_root.is_absolute():
        raise ValueError("sandbox paths must be absolute")
    if raw_path.startswith("//") or raw_root.startswith("//"):
        raise ValueError("sandbox paths must use one root separator")
    if ".." in path.parts or ".." in sandbox_root.parts:
        raise ValueError("sandbox paths cannot contain ..")
    normalized_root = Path(os.path.normpath(raw_root))
    normalized_path = Path(os.path.normpath(raw_path))
    if normalized_root.parent == normalized_root:
        raise ValueError("filesystem root cannot be the sandbox")
    if not normalized_path.is_relative_to(normalized_root):
        raise ValueError("sandbox path escapes explicit root")
    if normalized_path == normalized_root and not directory:
        raise ValueError("sandbox root cannot be a file target")
    if normalized_path == normalized_root and not exists:
        raise ValueError("sandbox root cannot be an absent target")
    for candidate in (normalized_root, normalized_path):
        if (candidate == LIBRARY_ROOT or LIBRARY_ROOT in candidate.parents
                or candidate == PROTECTED_ROOT
                or PROTECTED_ROOT in candidate.parents):
            raise ValueError("protected path is outside the sandbox")

    root_chain = []
    current = normalized_root
    while current.parent != current:
        root_chain.append(current)
        current = current.parent
    root_chain.append(current)
    for member in reversed(root_chain):
        info = member.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise ValueError("sandbox root ancestor is not a real directory")

    path_chain = []
    current = normalized_path
    while current != normalized_root:
        path_chain.append(current)
        current = current.parent
    for member in reversed(path_chain):
        try:
            info = member.lstat()
        except FileNotFoundError:
            if member == normalized_path and not exists:
                continue
            raise
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("sandbox symlink is forbidden")
        if member == normalized_path:
            if directory and not stat.S_ISDIR(info.st_mode):
                raise ValueError("sandbox directory differs")
            if not directory and not stat.S_ISREG(info.st_mode):
                raise ValueError("sandbox file differs")
        elif not stat.S_ISDIR(info.st_mode):
            raise ValueError("sandbox ancestor is not a real directory")
