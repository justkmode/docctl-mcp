# jira_client.py — create ONE Jira issue through the REST API
import os  # read environment variables

import requests  # send HTTP requests
from dotenv import load_dotenv  # load secrets from the .env file

load_dotenv()  # reads .env, so the token never lives in the code

REQUIRED_VARS = ("JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")  # all must be set


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


def create_issue(summary, project_key="DOC"):
    """Create one Jira Task with the given title and return its key (e.g. "DOC-2").

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


# Runs only when started by hand, not when another file imports this one
if __name__ == "__main__":
    key = create_issue("Naming check failed: TEST-001.pdf")
    print(f"Created {key}")
