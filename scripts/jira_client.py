# jira_client.py — create Jira issues through the REST API, without duplicates
import os  # read environment variables

import requests  # send HTTP requests
from dotenv import load_dotenv  # load secrets from the .env file

load_dotenv()  # reads .env, so the token never lives in the code

REQUIRED_VARS = ("JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")  # all must be set
DOCCTL_LABEL = "docctl"  # marks issues created by this tool


def _load_settings():
    """Read the Jira settings from the environment and stop if any are missing.

    Returns (url, email, token). Raises RuntimeError naming every missing
    variable at once, so you can fix the .env in one go.
    """
    # Collect all missing names first, instead of failing on the first one
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing in .env: {', '.join(missing)}")

    return (
        os.getenv("JIRA_URL"),        # your Jira site address
        os.getenv("JIRA_EMAIL"),      # your Atlassian login email
        os.getenv("JIRA_API_TOKEN"),  # the API token (secret!)
    )


def _escape_jql(text):
    """Make text safe to put inside a double-quoted JQL string.

    A backslash becomes \\\\ and a quote becomes \\", so a summary with
    quotes in it can't end the JQL string early.
    """
    # Backslashes first, otherwise we'd double the ones added for the quotes
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _build_jql(summary, project_key):
    """Build the JQL that finds open docctl issues whose title looks like `summary`.

    Jira's `~` text search is fuzzy, so this only narrows the list;
    find_open_issue() does the exact comparison afterwards.
    """
    # Wrapping the summary in escaped quotes makes `~` a phrase search,
    # so characters like - and : in filenames are treated as plain text
    phrase = _escape_jql(f'"{_escape_jql(summary)}"')
    return (
        f'project = "{_escape_jql(project_key)}"'
        f' AND labels = "{DOCCTL_LABEL}"'
        " AND statusCategory != Done"  # open = anything not finished
        f' AND summary ~ "{phrase}"'
    )


def find_open_issue(summary, project_key="DOC"):
    """Return the key of an open docctl issue with exactly this summary, or None.

    Raises RuntimeError if settings are missing, and requests.HTTPError if
    Jira rejects the search.
    """
    jira_url, email, token = _load_settings()

    # Ask Jira's current search endpoint for likely candidates
    response = requests.get(
        f"{jira_url}/rest/api/3/search/jql",  # replaces the old /rest/api/3/search
        params={
            "jql": _build_jql(summary, project_key),
            "fields": "summary",  # the new endpoint returns only IDs unless asked
            "maxResults": 50,     # one page is plenty after the phrase filter
        },
        auth=(email, token),
        timeout=10,
    )
    response.raise_for_status()

    # Jira's match is fuzzy, so only an exact, character-for-character title counts
    for issue in response.json().get("issues", []):
        if issue["fields"]["summary"] == summary:
            return issue["key"]
    return None


def create_issue(summary, project_key="DOC"):
    """Create one Jira Task with the given title and return its key (e.g. "DOC-2").

    The issue gets the "docctl" label so find_open_issue() can find it later.
    Raises RuntimeError if settings are missing, and requests.HTTPError if
    Jira rejects the request (bad token, unknown project, ...).
    """
    # Settings are read here, not at import time, so importing needs no .env
    jira_url, email, token = _load_settings()

    # The JSON body = the data we send
    payload = {
        "fields": {
            "project": {"key": project_key},  # which Jira space
            "summary": summary,               # issue title
            "issuetype": {"name": "Task"},    # must exist in the space
            "labels": [DOCCTL_LABEL],         # lets us find our own issues again
        }
    }

    # Send the request to Jira
    response = requests.post(
        f"{jira_url}/rest/api/3/issue",  # endpoint = 'create an issue'
        json=payload,                     # requests turns the dict into JSON
        auth=(email, token),              # basic auth = email + API token
        timeout=10,                       # don't wait forever
    )

    # Turn 4xx/5xx answers into a real error instead of silently continuing
    response.raise_for_status()

    return response.json()["key"]  # Jira's answer includes the new key


def get_or_create_issue(summary, project_key="DOC"):
    """Return (key, created): reuse an open docctl issue with this exact title, or make one.

    created is False when an existing issue was found, True when a new one
    was made. Running this twice with the same summary gives one issue, not two.
    """
    # Look first, so repeated audits don't pile up duplicate tickets
    existing = find_open_issue(summary, project_key)
    if existing:
        return existing, False

    return create_issue(summary, project_key), True


# Runs only when started by hand, not when another file imports this one
if __name__ == "__main__":
    key, created = get_or_create_issue("Naming check failed: TEST-001.pdf")
    print(f"Created {key}" if created else f"Already exists: {key}")
