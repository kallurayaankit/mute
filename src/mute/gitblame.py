"""Git blame: who added this suppression, and when."""

import os
import subprocess
from datetime import datetime, timezone


def _run(args, cwd="."):
    """Run a git command. Returns stdout on success, None on any failure.

    Failures include: git not installed, not a repo, invalid cwd path,
    timeout, non-zero exit. All of these should be non-fatal.
    """
    # If cwd is given and doesn't exist, fail fast
    if cwd and cwd != ".":
        try:
            if not os.path.isdir(cwd):
                return None
        except (OSError, TypeError):
            return None

    try:
        r = subprocess.run(
            args, capture_output=True, text=True, cwd=cwd, timeout=30,
        )
        if r.returncode != 0:
            return None
        return r.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, NotADirectoryError,
            PermissionError, OSError):
        return None


def is_repo(cwd="."):
    return _run(["git", "rev-parse", "--git-dir"], cwd=cwd) is not None


def blame_line(file_path, line, cwd="."):
    """Return (sha, author, date_iso) for the given line, or (None, None, None)."""
    out = _run(
        ["git", "blame", "-L", str(line) + "," + str(line), "--porcelain", file_path],
        cwd=cwd,
    )
    if not out:
        return None, None, None

    sha = None
    author = None
    author_time = None

    for raw in out.splitlines():
        line_txt = raw.strip()
        if not line_txt:
            continue
        if sha is None and len(line_txt.split()) >= 1 and len(line_txt.split()[0]) == 40:
            sha = line_txt.split()[0]
            continue
        if line_txt.startswith("author "):
            author = line_txt[len("author "):].strip()
            continue
        if line_txt.startswith("author-time "):
            try:
                author_time = int(line_txt[len("author-time "):].strip())
            except ValueError:
                pass
            continue

    date_iso = ""
    if author_time:
        date_iso = datetime.fromtimestamp(author_time, tz=timezone.utc).strftime("%Y-%m-%d")

    return sha, author, date_iso


def age_days(date_iso):
    if not date_iso:
        return 0
    try:
        dt = datetime.fromisoformat(date_iso).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return max(0, (now - dt).days)
    except ValueError:
        return 0
