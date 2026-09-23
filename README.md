# Semver Auto Releaser

## Description
A self-contained release management tool that enforces [Semantic Versioning](https://semver.org/) by parsing [Conventional Commits](https://www.conventionalcommits.org/) history. It determines the next version bump, mutates the version in `pyproject.toml`, generates a changelog, tags the release, and can optionally push the tag and publish a GitHub Release.

## Architecture Overview
* `releaser/commit_parser.py` — parses conventional commit headers/footers and classifies each commit as `major`, `minor`, `patch`, or no-op.
* `releaser/version.py` — reads/writes the semantic version stored in `pyproject.toml`.
* `releaser/changelog.py` — renders and prepends release notes to `CHANGELOG.md`.
* `releaser/git_utils.py` — wraps the `git` CLI (tags, commit history, commit/push).
* `releaser/github_release.py` — publishes a GitHub Release via the REST API.
* `releaser/pipeline.py` — orchestrates analyze → bump → changelog → tag → publish.
* `main.py` — CLI entry point.

## Prerequisites
* Git
* Python 3.9+
* A GitHub personal access token (only if publishing GitHub Releases)

## Installation
```bash
pip install -r requirements.txt
```

## Environment Variables
Configuration is loaded from a `.env` file (see `.env.example`):

| Variable | Description | Default |
| --- | --- | --- |
| `GITHUB_TOKEN` | Token used to create GitHub Releases | _(none)_ |
| `REPO_OWNER` | GitHub repository owner | _(none)_ |
| `REPO_NAME` | GitHub repository name | _(none)_ |
| `GIT_REMOTE` | Remote to push commits/tags to | `origin` |
| `DEFAULT_BRANCH` | Branch to push release commits to | `main` |
| `VERSION_FILE` | File containing the semantic version | `pyproject.toml` |
| `CHANGELOG_FILE` | File release notes are prepended to | `CHANGELOG.md` |
| `TAG_PREFIX` | Prefix used for git tags | `v` |
| `DRY_RUN` | Preview a release without writing anything | `false` |
| `PUSH_TAGS` | Push the release commit/tag after tagging | `false` |
| `CREATE_GITHUB_RELEASE` | Publish a GitHub Release after tagging | `false` |

## Quick Start & Usage
```bash
# Copy and edit the environment file
cp .env.example .env

# See what the next version would be, without changing anything
python main.py analyze

# Perform a release: bump version, update changelog, commit, and tag
python main.py release

# Preview a release without writing files, committing, tagging, or pushing
python main.py release --dry-run
```

Commit messages must follow the Conventional Commits format for the releaser to detect them:
* `fix: ...` → patch release
* `feat: ...` → minor release
* `feat!: ...` or a `BREAKING CHANGE:` footer → major release
* Any other type (`chore`, `docs`, `refactor`, `test`, `ci`, ...) does not trigger a release on its own.

## CI Usage
Run `python main.py release` in a GitHub Actions workflow with `GITHUB_TOKEN` and `PUSH_TAGS=true` (and `CREATE_GITHUB_RELEASE=true` if you want a GitHub Release published) to fully automate releases on merge to your default branch.
