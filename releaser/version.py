"""Reading and writing the semantic version stored in pyproject.toml."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import tomlkit

from releaser.commit_parser import BumpType

_SEMVER_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


class VersionError(RuntimeError):
    pass


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(self, bump_type: BumpType) -> "Version":
        if bump_type is BumpType.MAJOR:
            return Version(self.major + 1, 0, 0)
        if bump_type is BumpType.MINOR:
            return Version(self.major, self.minor + 1, 0)
        if bump_type is BumpType.PATCH:
            return Version(self.major, self.minor, self.patch + 1)
        return self

    @classmethod
    def parse(cls, raw: str) -> "Version":
        match = _SEMVER_RE.match(raw.strip())
        if not match:
            raise VersionError(f"'{raw}' is not a valid MAJOR.MINOR.PATCH version")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
        )


def read_version(version_file: str) -> Version:
    path = Path(version_file)
    if not path.exists():
        raise VersionError(f"version file not found: {version_file}")

    doc = tomlkit.parse(path.read_text(encoding="utf-8"))
    raw = doc.get("project", {}).get("version") or doc.get("tool", {}).get(
        "poetry", {}
    ).get("version")
    if not raw:
        raise VersionError(
            f"could not find a version under [project] or [tool.poetry] in {version_file}"
        )
    return Version.parse(raw)


def write_version(version_file: str, new_version: Version) -> None:
    path = Path(version_file)
    doc = tomlkit.parse(path.read_text(encoding="utf-8"))

    if "project" in doc and "version" in doc["project"]:
        doc["project"]["version"] = str(new_version)
    elif "tool" in doc and "poetry" in doc["tool"] and "version" in doc["tool"]["poetry"]:
        doc["tool"]["poetry"]["version"] = str(new_version)
    else:
        raise VersionError(
            f"could not find a version under [project] or [tool.poetry] in {version_file}"
        )

    path.write_text(tomlkit.dumps(doc), encoding="utf-8")
