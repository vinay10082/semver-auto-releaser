"""Publishing a GitHub Release via the REST API."""

from __future__ import annotations

import requests

_API_ROOT = "https://api.github.com"


class GitHubReleaseError(RuntimeError):
    pass


def create_release(
    *,
    token: str,
    owner: str,
    repo: str,
    tag_name: str,
    name: str,
    body: str,
    draft: bool = False,
    prerelease: bool = False,
) -> dict:
    url = f"{_API_ROOT}/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "tag_name": tag_name,
        "name": name,
        "body": body,
        "draft": draft,
        "prerelease": prerelease,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code >= 300:
        raise GitHubReleaseError(
            f"GitHub release creation failed ({response.status_code}): {response.text}"
        )
    return response.json()
