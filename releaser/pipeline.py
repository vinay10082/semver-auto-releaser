"""Orchestrates analyze/bump/changelog/release steps end to end."""

from __future__ import annotations

from dataclasses import dataclass

from releaser import git_utils
from releaser.changelog import prepend_changelog, render_release_notes
from releaser.commit_parser import BumpType, ParsedCommit, determine_bump, parse_commits
from releaser.config import Config
from releaser.github_release import create_release
from releaser.version import Version, read_version, write_version


class ReleaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class Analysis:
    current_version: Version
    next_version: Version
    bump_type: BumpType
    parsed_commits: list[ParsedCommit]
    last_tag: str | None


def analyze(config: Config) -> Analysis:
    if not git_utils.is_git_repo():
        raise ReleaseError("not inside a git repository")

    current_version = read_version(config.version_file)
    last_tag = git_utils.get_latest_tag(config.tag_prefix)
    commits = git_utils.get_commits_since(last_tag)
    parsed = parse_commits(commits)
    bump_type = determine_bump(parsed)
    next_version = current_version.bump(bump_type)

    return Analysis(
        current_version=current_version,
        next_version=next_version,
        bump_type=bump_type,
        parsed_commits=parsed,
        last_tag=last_tag,
    )


def run_release(config: Config, analysis: Analysis) -> str | None:
    """Applies the version bump, changelog, git tag, and optional publishing.

    Returns the new tag name, or None if there was nothing to release.
    """
    if analysis.bump_type is BumpType.NONE:
        return None

    tag_name = f"{config.tag_prefix}{analysis.next_version}"
    release_notes = render_release_notes(analysis.next_version, analysis.parsed_commits)

    if config.dry_run:
        return tag_name

    write_version(config.version_file, analysis.next_version)
    prepend_changelog(config.changelog_file, release_notes)

    git_utils.stage_files([config.version_file, config.changelog_file])
    git_utils.commit(f"chore(release): {analysis.next_version}")
    git_utils.create_tag(tag_name, f"Release {analysis.next_version}")

    if config.push_tags:
        git_utils.push(config.remote_name, config.default_branch)
        git_utils.push_tag(config.remote_name, tag_name)

    if config.create_github_release:
        if not config.github_repo_configured:
            raise ReleaseError(
                "CREATE_GITHUB_RELEASE is enabled but GITHUB_TOKEN/REPO_OWNER/REPO_NAME are not set"
            )
        create_release(
            token=config.github_token,
            owner=config.repo_owner,
            repo=config.repo_name,
            tag_name=tag_name,
            name=str(analysis.next_version),
            body=release_notes,
        )

    return tag_name
