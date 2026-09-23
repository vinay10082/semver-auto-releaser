"""Entry point for the semver auto-releaser CLI.

Usage:
    python main.py analyze              # show what the next version/bump would be
    python main.py release              # bump version, update changelog, tag, and (optionally) publish
    python main.py release --dry-run    # preview a release without writing anything
"""

from __future__ import annotations

import argparse
import sys

from releaser.commit_parser import BumpType
from releaser.config import load_config
from releaser.pipeline import ReleaseError, analyze, run_release
from releaser.version import VersionError


def _print_analysis(analysis) -> None:
    print(f"Current version : {analysis.current_version}")
    print(f"Last tag        : {analysis.last_tag or '(none)'}")
    print(f"Commits found   : {len(analysis.parsed_commits)}")
    print(f"Bump type       : {analysis.bump_type.name}")
    if analysis.bump_type is BumpType.NONE:
        print("Next version    : (no release needed)")
    else:
        print(f"Next version    : {analysis.next_version}")


def cmd_analyze(_: argparse.Namespace) -> int:
    config = load_config()
    result = analyze(config)
    _print_analysis(result)
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    config = load_config()
    if args.dry_run:
        config = _with_dry_run(config)

    result = analyze(config)
    _print_analysis(result)

    if result.bump_type is BumpType.NONE:
        print("\nNo releasable commits since the last tag. Nothing to do.")
        return 0

    tag_name = run_release(config, result)

    if config.dry_run:
        print(f"\n[dry-run] Would create tag '{tag_name}' and release {result.next_version}.")
    else:
        print(f"\nReleased {result.next_version} as tag '{tag_name}'.")
    return 0


def _with_dry_run(config):
    from dataclasses import replace

    return replace(config, dry_run=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Semantic version auto-releaser driven by Conventional Commits.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze", help="Show the next version bump without changing anything."
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    release_parser = subparsers.add_parser(
        "release", help="Bump the version, update the changelog, tag, and optionally publish."
    )
    release_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the release without writing files, committing, tagging, or pushing.",
    )
    release_parser.set_defaults(func=cmd_release)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ReleaseError, VersionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
