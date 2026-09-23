# Automatic Version Update

## Description
An automated release management pipeline enforcing semantic versioning via Conventional Commits.

## Architecture Overview
GitHub Actions workflow utilizing `commitizen` to parse commit history, mutate `pyproject.toml`, and generate changelogs dynamically.

## Prerequisites
* Git
* GitHub Actions
* `commitizen` or `python-semantic-release`

## Environment Variables
* `GITHUB_TOKEN` (provided by CI runner for repository mutation permissions)

## Quick Start & Usage
Install the pre-commit hook to enforce commit message structures locally prior to pushing code to the remote repository.

## Testing & CI
Validates commit regex patterns and simulates version bumping logic in an isolated git environment.
