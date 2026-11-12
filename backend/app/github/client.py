import re
from urllib.parse import urlparse, quote

import requests

from contextvars import ContextVar

# A request-scoped token prevents users from sharing a server-wide GitHub credential.
_active_github_token: ContextVar[str | None] = ContextVar("active_github_token", default=None)

def set_request_github_token(token: str):
    return _active_github_token.set(token)

def reset_request_github_token(marker):
    _active_github_token.reset(marker)

def github_authorization_header() -> str:
    token = _active_github_token.get()
    if not token:
        raise ValueError("Authenticated GitHub access is required")
    return f"Bearer {token}"


GITHUB_API_URL = "https://api.github.com"


def parse_pr_url(pr_url: str):
    """
    Extract owner, repository name and pull request number
    from a GitHub pull request URL.
    """

    parsed_url = urlparse(pr_url.strip())

    if parsed_url.netloc not in ["github.com", "www.github.com"]:
        raise ValueError("URL must be a GitHub URL")

    match = re.match(
        r"^/([^/]+)/([^/]+)/pull/(\d+)",
        parsed_url.path
    )

    if not match:
        raise ValueError(
            "Invalid GitHub pull request URL. "
            "Expected: https://github.com/owner/repo/pull/123"
        )

    owner = match.group(1)
    repo = match.group(2)
    pr_number = int(match.group(3))

    return {
        "owner": owner,
        "repo": repo,
        "pr_number": pr_number
    }


def parse_repo_url(repo_url: str):
    """
    Extract owner and repository name
    from a GitHub repository URL.
    """

    parsed_url = urlparse(repo_url.strip())

    if parsed_url.netloc not in [
        "github.com",
        "www.github.com"
    ]:
        raise ValueError("URL must be a GitHub URL")

    match = re.match(
        r"^/([^/]+)/([^/]+)/?$",
        parsed_url.path
    )

    if not match:
        raise ValueError(
            "Invalid GitHub repository URL. "
            "Expected: https://github.com/owner/repository"
        )

    owner = match.group(1)
    repo = match.group(2)

    return {
        "owner": owner,
        "repo": repo
    }


def get_repository(owner: str, repo: str):
    """
    Fetch repository information from GitHub.
    """

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}"
    )

    headers = {
        "Authorization": github_authorization_header(),
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers, timeout=20
    )

    if response.status_code == 401:
        raise ValueError(
            "GitHub authentication failed. Check your token."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub denied the request. "
            "Check token permissions or rate limits."
        )

    if response.status_code == 404:
        raise ValueError(
            f"Repository {owner}/{repo} was not found. "
            "Check that it exists and your token has access."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API request failed: {response.status_code}"
        )

    return response.json()


def get_repository_tree(
    owner: str,
    repo: str,
    branch: str | None = None
):
    """
    Fetch the complete repository file tree.
    """

    if branch is None:
        repository = get_repository(
            owner,
            repo
        )

        branch = repository["default_branch"]

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/git/trees/{branch}"
    )

    params = {
        "recursive": "1"
    }

    headers = {
        "Authorization": github_authorization_header(),
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params, timeout=20
    )

    if response.status_code == 401:
        raise ValueError(
            "GitHub authentication failed. Check your token."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub denied the request. "
            "Check token permissions or rate limits."
        )

    if response.status_code == 404:
        raise ValueError(
            f"Repository tree for {owner}/{repo} "
            f"could not be found."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API request failed: {response.status_code}"
        )

    return response.json()


def read_file(
    owner: str,
    repo: str,
    path: str,
    branch: str | None = None
):
    """
    Read the contents of a file from a GitHub repository.
    """

    if branch is None:
        repository = get_repository(
            owner,
            repo
        )

        branch = repository["default_branch"]

    encoded_path = quote(
        path,
        safe="/"
    )

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/contents/{encoded_path}"
    )

    params = {
        "ref": branch
    }

    headers = {
        "Authorization": github_authorization_header(),
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params, timeout=20
    )

    if response.status_code == 401:
        raise ValueError(
            "GitHub authentication failed. Check your token."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub denied the request. "
            "Check token permissions or rate limits."
        )

    if response.status_code == 404:
        raise ValueError(
            f"File '{path}' was not found "
            f"in {owner}/{repo}."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API request failed: {response.status_code}"
        )

    data = response.json()

    if data.get("type") != "file":
        raise ValueError(
            f"'{path}' is not a file."
        )

    if data.get("encoding") != "base64":
        raise ValueError(
            f"GitHub returned an unsupported encoding "
            f"for '{path}'."
        )

    import base64

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    return {
        "path": data["path"],
        "size": data.get("size", 0),
        "content": content
    }


def search_code(
    owner: str,
    repo: str,
    query: str
):
    """
    Search for code inside a GitHub repository.
    """

    url = f"{GITHUB_API_URL}/search/code"

    search_query = f"{query} repo:{owner}/{repo}"

    params = {
        "q": search_query,
        "per_page": 20
    }

    headers = {
        "Authorization": github_authorization_header(),
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params, timeout=20
    )

    if response.status_code == 401:
        raise ValueError(
            "GitHub authentication failed. Check your token."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub denied the request. "
            "Check token permissions or search rate limits."
        )

    if response.status_code == 422:
        raise ValueError(
            "GitHub rejected the search query."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API request failed: {response.status_code}"
        )

    data = response.json()

    results = []

    for item in data.get("items", []):
        results.append({
            "name": item["name"],
            "path": item["path"],
            "sha": item["sha"],
            "url": item["html_url"]
        })

    return {
        "total_count": data.get("total_count", 0),
        "results": results
    }





def get_pr(owner: str, repo: str, pr_number: int):
    """
    Fetch basic pull request information from GitHub.
    """

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pr_number}"
    )

    headers = {
        "Authorization": github_authorization_header(),
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 401:
        raise ValueError(
            "GitHub authentication failed. Check your token."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub denied the request. "
            "Check token permissions or rate limits."
        )

    if response.status_code == 404:
        raise ValueError(
            f"GitHub could not find PR #{pr_number} "
            f"in {owner}/{repo}. "
            "Check that the repository and PR exist "
            "and that your token has access."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API request failed: {response.status_code}"
        )

    return response.json()


def get_pr_files(owner: str, repo: str, pr_number: int):
    """
    Fetch the files changed in a pull request.
    """

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pr_number}/files"
    )

    headers = {
        "Authorization": github_authorization_header(),
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 401:
        raise ValueError(
            "GitHub authentication failed. Check your token."
        )

    if response.status_code == 403:
        raise ValueError(
            "GitHub denied the request. "
            "Check token permissions or rate limits."
        )

    if response.status_code == 404:
        raise ValueError(
            f"GitHub could not find PR #{pr_number} "
            f"in {owner}/{repo}."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API request failed: {response.status_code}"
        )

    return response.json()