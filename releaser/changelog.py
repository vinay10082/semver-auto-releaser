"""Markdown changelog generation from parsed conventional commits."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from releaser.commit_parser import ParsedCommit
from releaser.version import Version

_SECTION_ORDER = ["BREAKING CHANGES", "Features", "Bug Fixes", "Performance Improvements", "Reverts"]

_HEADER = "# Changelog\n\nAll notable changes to this project are documented in this file.\n"


def _format_entry(pc: ParsedCommit) -> str:
    scope = f"**{pc.scope}:** " if pc.scope else ""
    short_hash = pc.commit.hash[:7]
    if pc.is_breaking and pc.breaking_description:
        return f"- {scope}{pc.breaking_description} ({short_hash})"
    return f"- {scope}{pc.description} ({short_hash})"


def render_release_notes(
    version: Version, parsed_commits: list[ParsedCommit], release_date: date | None = None
) -> str:
    release_date = release_date or datetime.now().date()
    sections: dict[str, list[str]] = {}

    for pc in parsed_commits:
        title = pc.section_title
        if title is None:
            continue
        sections.setdefault(title, []).append(_format_entry(pc))

    lines = [f"## {version} ({release_date.isoformat()})", ""]
    wrote_any = False
    for title in _SECTION_ORDER:
        entries = sections.get(title)
        if not entries:
            continue
        wrote_any = True
        lines.append(f"### {title}")
        lines.append("")
        lines.extend(entries)
        lines.append("")

    if not wrote_any:
        lines.append("_No user-facing changes._")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def prepend_changelog(changelog_file: str, release_notes: str) -> None:
    path = Path(changelog_file)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing.startswith("# Changelog"):
            header, _, rest = existing.partition("\n\n")
            body = rest.strip("\n")
            new_content = f"{_HEADER}\n{release_notes}\n{body}\n" if body else f"{_HEADER}\n{release_notes}"
        else:
            new_content = f"{_HEADER}\n{release_notes}\n{existing}"
    else:
        new_content = f"{_HEADER}\n{release_notes}"

    path.write_text(new_content.rstrip() + "\n", encoding="utf-8")
