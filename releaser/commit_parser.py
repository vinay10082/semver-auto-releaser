"""Conventional Commits parsing and bump-type classification."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum

from releaser.git_utils import Commit

_HEADER_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<description>.+)$"
)
_BREAKING_FOOTER_RE = re.compile(r"^BREAKING[ -]CHANGE:\s*(.+)$", re.MULTILINE)

_MINOR_TYPES = {"feat"}
_PATCH_TYPES = {"fix", "perf"}

_SECTION_TITLES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance Improvements",
    "revert": "Reverts",
}


class BumpType(IntEnum):
    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3


@dataclass(frozen=True)
class ParsedCommit:
    commit: Commit
    type: str | None
    scope: str | None
    description: str
    is_breaking: bool
    breaking_description: str | None

    @property
    def bump_type(self) -> BumpType:
        if self.is_breaking:
            return BumpType.MAJOR
        if self.type in _MINOR_TYPES:
            return BumpType.MINOR
        if self.type in _PATCH_TYPES:
            return BumpType.PATCH
        return BumpType.NONE

    @property
    def section_title(self) -> str | None:
        if self.is_breaking:
            return "BREAKING CHANGES"
        return _SECTION_TITLES.get(self.type or "")


def parse_commit(commit: Commit) -> ParsedCommit:
    match = _HEADER_RE.match(commit.subject.strip())
    breaking_footer = _BREAKING_FOOTER_RE.search(commit.body)

    if not match:
        return ParsedCommit(
            commit=commit,
            type=None,
            scope=None,
            description=commit.subject.strip(),
            is_breaking=bool(breaking_footer),
            breaking_description=breaking_footer.group(1).strip() if breaking_footer else None,
        )

    is_breaking = bool(match.group("breaking")) or bool(breaking_footer)
    return ParsedCommit(
        commit=commit,
        type=match.group("type").lower(),
        scope=match.group("scope"),
        description=match.group("description").strip(),
        is_breaking=is_breaking,
        breaking_description=breaking_footer.group(1).strip() if breaking_footer else None,
    )


def parse_commits(commits: list[Commit]) -> list[ParsedCommit]:
    return [parse_commit(c) for c in commits]


def determine_bump(parsed_commits: list[ParsedCommit]) -> BumpType:
    if not parsed_commits:
        return BumpType.NONE
    return max((pc.bump_type for pc in parsed_commits), default=BumpType.NONE)
