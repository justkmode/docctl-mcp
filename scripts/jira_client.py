# jira_client.py — create ONE Jira issue through the REST API
import os  # read environment variables

import requests  # send HTTP requests
from dotenv import load_dotenv  # load secrets from the .env file

load_dotenv()  # reads .env, so the token never lives in the code

JIRA_URL = os.getenv("JIRA_URL")        # your Jira site address
EMAIL = os.getenv("JIRA_EMAIL")         # your Atlassian login email
TOKEN = os.getenv("JIRA_API_TOKEN")     # the API token (secret!)

payload = {                              # the JSON body = the data we send
    "fields": {
        "project": {"key": "DOC"},       # which Jira space
        "summary": "Naming check failed: TEST-001.pdf",  # issue title
        "issuetype": {"name": "Task"},   # must exist in the space
    }
}

response = requests.post(
    f"{JIRA_URL}/rest/api/3/issue",     # endpoint = 'create an issue'
    json=payload,                        # requests turns the dict into JSON
    auth=(EMAIL, TOKEN),                 # basic auth = email + API token
    timeout=10,                          # don't wait forever
)

print(response.status_code)  # 201 = created
print(response.text)         # Jira's answer, incl. the new key (DOC-1)