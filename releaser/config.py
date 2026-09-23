"""Runtime configuration loaded from environment variables (.env)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    github_token: str | None
    repo_owner: str | None
    repo_name: str | None
    remote_name: str
    default_branch: str
    version_file: str
    changelog_file: str
    tag_prefix: str
    dry_run: bool
    push_tags: bool
    create_github_release: bool

    @property
    def github_repo_configured(self) -> bool:
        return bool(self.github_token and self.repo_owner and self.repo_name)


def load_config() -> Config:
    return Config(
        github_token=os.getenv("GITHUB_TOKEN"),
        repo_owner=os.getenv("REPO_OWNER"),
        repo_name=os.getenv("REPO_NAME"),
        remote_name=os.getenv("GIT_REMOTE", "origin"),
        default_branch=os.getenv("DEFAULT_BRANCH", "main"),
        version_file=os.getenv("VERSION_FILE", "pyproject.toml"),
        changelog_file=os.getenv("CHANGELOG_FILE", "CHANGELOG.md"),
        tag_prefix=os.getenv("TAG_PREFIX", "v"),
        dry_run=_bool_env("DRY_RUN", False),
        push_tags=_bool_env("PUSH_TAGS", False),
        create_github_release=_bool_env("CREATE_GITHUB_RELEASE", False),
    )
