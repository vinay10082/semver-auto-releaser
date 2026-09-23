"""Thin wrappers around the git CLI used by the releaser."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


class GitError(RuntimeError):
    pass


def _run(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


@dataclass(frozen=True)
class Commit:
    hash: str
    subject: str
    body: str

    @property
    def full_message(self) -> str:
        return f"{self.subject}\n\n{self.body}".strip()


def is_git_repo() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_latest_tag(tag_prefix: str) -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "--match", f"{tag_prefix}*"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


_COMMIT_SEP = "\x1e"
_FIELD_SEP = "\x1f"


def get_commits_since(ref: str | None) -> list[Commit]:
    commit_range = f"{ref}..HEAD" if ref else "HEAD"
    log_format = f"%H{_FIELD_SEP}%s{_FIELD_SEP}%b{_COMMIT_SEP}"
    output = _run(["log", commit_range, f"--pretty=format:{log_format}"])
    if not output:
        return []

    commits: list[Commit] = []
    for raw in output.split(_COMMIT_SEP):
        raw = raw.strip("\n")
        if not raw:
            continue
        parts = raw.split(_FIELD_SEP)
        if len(parts) != 3:
            continue
        commit_hash, subject, body = parts
        commits.append(Commit(hash=commit_hash, subject=subject, body=body.strip()))
    return commits


def has_uncommitted_changes() -> bool:
    return bool(_run(["status", "--porcelain"]))


def stage_files(paths: list[str]) -> None:
    _run(["add", *paths])


def commit(message: str) -> None:
    _run(["commit", "-m", message])


def create_tag(tag_name: str, message: str) -> None:
    _run(["tag", "-a", tag_name, "-m", message])


def push(remote: str, branch: str) -> None:
    _run(["push", remote, branch])


def push_tag(remote: str, tag_name: str) -> None:
    _run(["push", remote, tag_name])
