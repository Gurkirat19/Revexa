"""Offline repository-agent tests; no GitHub or AI network calls."""
from types import SimpleNamespace

from app.ai.repository_agent import _ask_with_fallback


class FailingProvider:
    def ask(self, **kwargs):
        raise RuntimeError("temporary provider outage")


class WorkingProvider:
    def ask(self, **kwargs):
        return SimpleNamespace(text="Evidence-backed answer", tool_call=None)


def test_provider_fallback_uses_alternate_provider(monkeypatch):
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    from app.ai import repository_agent as agent_module
    monkeypatch.setattr(agent_module, "get_provider", lambda model: WorkingProvider())
    response, model, provider = _ask_with_fallback(
        FailingProvider(), "gemini", question="How does auth work?", context="auth.py", tools=[]
    )
    assert response.text == "Evidence-backed answer"
    assert model == "groq"
    assert isinstance(provider, WorkingProvider)


def test_provider_failure_is_not_silently_swallowed_when_fallback_disabled(monkeypatch):
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "false")
    try:
        _ask_with_fallback(
            FailingProvider(), "gemini", question="Explain", context="", tools=[]
        )
    except RuntimeError as error:
        assert "Gemini provider failed" in str(error)
    else:
        raise AssertionError("Provider failure should be surfaced")
