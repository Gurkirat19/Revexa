"""Offline tests for the session profile payload used by the frontend avatar."""
import os

os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")

from app.auth import _public_user


def test_github_user_without_stored_avatar_gets_public_fallback():
    user = _public_user({
        "id": 1, "github_id": 123, "login": "octocat", "name": "Octocat",
        "email": "octo@example.com", "avatar_url": None, "provider": "github",
    })
    assert user["connected"] is True
    assert user["avatar_url"] == "https://github.com/octocat.png?size=64"


def test_stored_https_avatar_is_preserved():
    user = _public_user({
        "id": 1, "github_id": 123, "login": "octocat", "name": "Octocat",
        "email": "octo@example.com", "avatar_url": "https://avatars.githubusercontent.com/u/123?v=4",
        "provider": "github",
    })
    assert user["avatar_url"] == "https://avatars.githubusercontent.com/u/123?v=4"


def test_non_https_avatar_is_not_returned():
    user = _public_user({
        "id": 1, "github_id": 123, "login": "octocat", "name": "Octocat",
        "email": "octo@example.com", "avatar_url": "http://example.com/avatar.png", "provider": "github",
    })
    assert user["avatar_url"] is None


def test_email_only_user_does_not_get_github_avatar_fallback():
    user = _public_user({
        "id": 2, "github_id": -123, "login": "person@example.com", "name": "Person",
        "email": "person@example.com", "avatar_url": None, "provider": "email",
    })
    assert user["connected"] is False
    assert user["avatar_url"] is None
