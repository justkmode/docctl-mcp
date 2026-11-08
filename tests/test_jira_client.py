# test_jira_client.py — check get_or_create_issue with fake Jira answers (no network)
import sys
from pathlib import Path

import pytest

# jira_client lives in scripts/, which isn't a package, so add it to the import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import jira_client


class FakeResponse:
    """Stand-in for a requests.Response: returns fixed JSON and never fails."""

    def __init__(self, data):
        self._data = data

    def json(self):
        """Return the canned JSON body."""
        return self._data

    def raise_for_status(self):
        """Pretend the request succeeded (a 2xx answer)."""


@pytest.fixture
def fake_jira(monkeypatch):
    """Replace Jira with fakes and record every POST, so tests can see what was sent.

    Set fake_jira["search_issues"] to choose what the search returns.
    """
    # Dummy settings, so _load_settings() passes without a real .env
    monkeypatch.setenv("JIRA_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "dummy")

    state = {"search_issues": [], "posts": []}

    # GET = search: answer with whatever the test put in search_issues
    def fake_get(url, **kwargs):
        """Fake the search endpoint."""
        return FakeResponse({"issues": state["search_issues"], "isLast": True})

    # POST = create: remember the body and answer with a new key
    def fake_post(url, **kwargs):
        """Fake the create-issue endpoint."""
        state["posts"].append(kwargs["json"])
        return FakeResponse({"key": "DOC-99"})

    monkeypatch.setattr(jira_client.requests, "get", fake_get)
    monkeypatch.setattr(jira_client.requests, "post", fake_post)
    return state


def test_exact_match_is_reused(fake_jira):
    # Jira's fuzzy search returns a near-match and the exact one
    fake_jira["search_issues"] = [
        {"key": "DOC-1", "fields": {"summary": "Naming check failed: TEST-002.pdf"}},
        {"key": "DOC-2", "fields": {"summary": "Naming check failed: TEST-001.pdf"}},
    ]

    result = jira_client.get_or_create_issue("Naming check failed: TEST-001.pdf")

    assert result == ("DOC-2", False)
    assert fake_jira["posts"] == []  # nothing new was created


def test_near_matches_do_not_count(fake_jira):
    # Same words but different case / extra text: not the same issue
    fake_jira["search_issues"] = [
        {"key": "DOC-1", "fields": {"summary": "naming check failed: test-001.pdf"}},
        {"key": "DOC-2", "fields": {"summary": "Naming check failed: TEST-001.pdf (old)"}},
    ]

    result = jira_client.get_or_create_issue("Naming check failed: TEST-001.pdf")

    assert result == ("DOC-99", True)
    assert fake_jira["posts"][0]["fields"]["labels"] == ["docctl"]


def test_jql_escapes_quotes():
    jql = jira_client._build_jql('Bad "name".pdf', "DOC")

    # Inner quotes escaped once for the phrase, then the whole phrase escaped again
    assert jql == (
        'project = "DOC" AND labels = "docctl" AND statusCategory != Done'
        ' AND summary ~ "\\"Bad \\\\\\"name\\\\\\".pdf\\""'
    )
