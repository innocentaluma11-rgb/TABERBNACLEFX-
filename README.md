# TABERBNACLEFX- + Composio

This repository now includes a minimal Python app that connects to the Composio GitHub toolkit and makes a real tool call against the GitHub integration.

## What is included

- `app.py` – initializes Composio and executes a GitHub tool call
- `requirements.txt` – adds the Composio Python SDK
- `.env.example` – sample environment variables
- `.gitignore` – ignores local secrets

## 1) Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then fill in your values in `.env`:

```env
COMPOSIO_API_KEY=your_api_key_here
COMPOSIO_USER_ID=user-123
GITHUB_OWNER=innocentaluma11-rgb
GITHUB_REPO=TABERBNACLEFX-
```

## 2) Connect the GitHub integration in Composio

1. Log in to the Composio Dashboard.
2. Add the GitHub integration.
3. Authorize the GitHub account you want this app to use.
4. Copy the API key to `COMPOSIO_API_KEY`.
5. Use the connected user identifier for `COMPOSIO_USER_ID`.

## 3) Run the app

```bash
python app.py
```

This should:

1. List GitHub tools available to the user
2. Execute a GitHub repo metadata call
3. Print the result from the first real tool call

## 4) Example output

```text
Listing GitHub tools for user ID: user-123
[...] 

Making a real GitHub tool call for innocentaluma11-rgb/TABERBNACLEFX-
{'name': 'TABERBNACLEFX-', ...}
```

## What to try next

- Replace the GitHub tool with Slack, Gmail, Notion, or Google Sheets
- Add a `toolkits=["slack"]` call and use `client.tools.execute(...)`
- Add a local `FastAPI` endpoint to trigger Composio actions from HTTP requests
- Add auth checks and a proper config loader for production
- Add logging and retries around tool execution

## Notes

The exact Composio tool slug names can vary a little by SDK version, so if you see a tool-name mismatch, print the `tools.get(...)` result and use the exact slug returned by the SDK.
