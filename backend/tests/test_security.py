"""Offline security regression tests; no live OAuth or AI calls."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import require_authenticated_user, get_user_github_token
from app.github.client import github_authorization_header, set_request_github_token, reset_request_github_token

client = TestClient(app)

@pytest.mark.parametrize("path,payload", [
    ("/api/review", {"pr_url": "https://github.com/owner/repo/pull/1"}),
    ("/api/repository/chat", {"repo_url": "https://github.com/owner/repo", "question": "Explain"}),
])
def test_anonymous_requests_are_rejected(path, payload):
    response = client.post(path, json=payload)
    assert response.status_code == 401


def test_cross_site_mutation_is_rejected():
    response = client.post("/api/auth/logout", headers={"Origin": "https://attacker.example"})
    assert response.status_code == 403


def test_oversized_request_is_rejected():
    response = client.post("/api/review", headers={"Content-Length": "1048577"}, content=b"{}")
    assert response.status_code == 413


def test_authenticated_but_unlinked_user_cannot_review():
    app.dependency_overrides[require_authenticated_user] = lambda: {"id": 99, "github_id": -1}
    try:
        response = client.post("/api/review", json={"pr_url": "https://github.com/owner/repo/pull/1"})
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_github_token_is_request_scoped():
    with pytest.raises(ValueError):
        github_authorization_header()
    marker = set_request_github_token("fake-token")
    try:
        assert github_authorization_header() == "Bearer fake-token"
    finally:
        reset_request_github_token(marker)
    with pytest.raises(ValueError):
        github_authorization_header()
